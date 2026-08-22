"""Percentage-based edge cropping for :func:`streamtex.image.st_image`.

``CropConfig`` describes how much of each edge of the source image is cut
away, as percentages of the image's *natural* dimensions, in CSS inset
order: ``(top, right, bottom, left)`` — the same convention as
``clip-path: inset(...)``, ``margin`` and ``padding``.

The crop is pure CSS (no JavaScript): an ``overflow:hidden`` container
whose ``aspect-ratio`` matches the visible zone, containing the ``<img>``
enlarged to ``100% / (1 - left - right)`` and shifted with
``transform: translate(-left%, -top%)``.  Percentage translations refer
to the img's own box, so the cropped edges align exactly — only the
container's aspect-ratio needs the natural dimensions (W, H).

Natural dimensions are resolved in priority order:

1. ``CropConfig.natural_size`` (or the ``natural_size=`` parameter of
   ``st_image``) — used as-is, no file or network access.
2. Local files — bitmap sizes read via Pillow, SVG sizes parsed from the
   ``width``/``height`` attributes or the ``viewBox``.  Cached by
   ``(path, mtime)`` like the base64 encoding.
3. Served URIs (the ``configure_image_path`` "served, never inlined"
   pattern) — the bytes are located on disk via the explicit ``fs_root``
   or Streamlit's ``app/static`` serving convention, then read like any
   local file.  The URL-vs-base64 decision of ``get_image_src`` is
   untouched.
4. http(s) URIs — **not auto-detected in this version**: pass
   ``natural_size=(W, H)`` explicitly (a clear error says so).

Used by :func:`streamtex.image.st_image` via its ``crop=`` parameter.
"""

from __future__ import annotations

import dataclasses
import logging
import os
import re
from dataclasses import dataclass
from typing import Optional, Sequence

import streamlit as st

from .blocks import get_static_sources
from .image_utils import _is_absolute_path, _is_relative_path, _is_url

try:
    # Same import path as book.py — guarded against Streamlit version drift.
    from streamlit.runtime.scriptrunner_utils.script_run_context import (
        get_script_run_ctx,
    )
except ImportError:  # pragma: no cover — future Streamlit relocation
    get_script_run_ctx = None

logger = logging.getLogger(__name__)

_NATURAL_SIZE_HINT = (
    "pass natural_size=(W, H) with the image's natural pixel dimensions"
)

# SVG root tag, then width/height/viewBox attributes.  Absolute lengths
# only (unitless or px) — relative units (%/em) fall back to the viewBox.
_SVG_TAG_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE | re.DOTALL)
_SVG_LENGTH_RE = r"""["']\s*([0-9.]+)\s*(?:px)?\s*["']"""
_SVG_WIDTH_RE = re.compile(r"\bwidth\s*=\s*" + _SVG_LENGTH_RE, re.IGNORECASE)
_SVG_HEIGHT_RE = re.compile(r"\bheight\s*=\s*" + _SVG_LENGTH_RE, re.IGNORECASE)
_SVG_VIEWBOX_RE = re.compile(
    r"""viewBox\s*=\s*["']\s*[0-9.eE+-]+[\s,]+[0-9.eE+-]+[\s,]+"""
    r"""([0-9.eE+]+)[\s,]+([0-9.eE+]+)\s*["']""",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CropConfig:
    """Edge crop for an image, in percent of its natural dimensions.

    :param top: Percentage of the natural height removed from the top
        edge.  Each value must be in ``[0, 100)``.
    :param right: Percentage of the natural width removed from the right
        edge.
    :param bottom: Percentage of the natural height removed from the
        bottom edge.  ``top + bottom`` must stay below 100.
    :param left: Percentage of the natural width removed from the left
        edge.  ``left + right`` must stay below 100.
    :param natural_size: Optional ``(W, H)`` natural pixel dimensions of
        the source image.  When given, no file read or network access is
        performed.  Mandatory for http(s) URIs in this version.
    """

    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0
    natural_size: Optional[tuple[float, float]] = None

    def __post_init__(self):
        for edge in ("top", "right", "bottom", "left"):
            value = getattr(self, edge)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(
                    f"CropConfig.{edge} must be a number in [0, 100) "
                    f"(got {value!r})"
                )
            if not (0 <= value < 100):
                raise ValueError(
                    f"CropConfig.{edge} must be in [0, 100) (got {value})"
                )
        if self.top + self.bottom >= 100:
            raise ValueError(
                f"CropConfig: top + bottom must stay below 100 "
                f"(got {self.top} + {self.bottom} = {self.top + self.bottom})"
            )
        if self.left + self.right >= 100:
            raise ValueError(
                f"CropConfig: left + right must stay below 100 "
                f"(got {self.left} + {self.right} = {self.left + self.right})"
            )
        if self.natural_size is not None:
            ns = self.natural_size
            if (
                not isinstance(ns, Sequence)
                or isinstance(ns, str)
                or len(ns) != 2
                or not all(
                    isinstance(v, (int, float)) and not isinstance(v, bool)
                    and v > 0
                    for v in ns
                )
            ):
                raise ValueError(
                    f"CropConfig.natural_size must be a (W, H) pair of "
                    f"positive numbers (got {self.natural_size!r})"
                )
            object.__setattr__(self, "natural_size", (float(ns[0]), float(ns[1])))


def normalize_crop(crop, natural_size=None) -> CropConfig:
    """Normalize the ``crop=`` value of ``st_image`` into a ``CropConfig``.

    Accepts a ``CropConfig`` or a sequence of 4 numbers in CSS inset
    order ``(top, right, bottom, left)``.  The standalone
    ``natural_size=`` parameter is merged in; giving it both there and
    inside the ``CropConfig`` is refused (redundant parameters are
    almost always editing mistakes).
    """
    if isinstance(crop, CropConfig):
        if natural_size is not None:
            if crop.natural_size is not None:
                raise ValueError(
                    "natural_size given twice: in the CropConfig and as the "
                    "natural_size= parameter — keep only one"
                )
            return dataclasses.replace(crop, natural_size=tuple(natural_size))
        return crop
    if (
        isinstance(crop, Sequence)
        and not isinstance(crop, str)
        and len(crop) == 4
    ):
        return CropConfig(
            *crop,
            natural_size=tuple(natural_size) if natural_size is not None else None,
        )
    raise ValueError(
        "crop must be a CropConfig or a 4-value sequence in CSS inset "
        f"order (top, right, bottom, left) — got {crop!r}"
    )


def _find_local_file(uri: str) -> str:
    """Locate the local file behind *uri*, or return ``""``.

    Mirrors the path resolution of ``streamtex.image.get_image_src``
    (absolute path, relative path, then configured static sources with
    the same ``images/`` sub-directory convention) without touching that
    function, whose legacy emission is guarded byte-for-byte.
    """
    if _is_absolute_path(uri):
        return uri if os.path.isfile(uri) else ""
    if _is_relative_path(uri):
        path = os.path.join(os.getcwd(), uri)
        return path if os.path.isfile(path) else ""
    for base in get_static_sources():
        for subdir in ["images", ""]:
            path = os.path.join(base, subdir, uri) if subdir else os.path.join(base, uri)
            if os.path.isfile(path):
                return path
    return ""


def _app_static_dir() -> str:
    """Best-effort filesystem path of Streamlit's ``app/static`` directory.

    Streamlit serves ``<main script dir>/static`` under the ``app/static``
    URL prefix.  The main script path comes from the ScriptRunContext when
    a runtime is active; without one (headless CLI export, which chdirs to
    the project dir before exec'ing book.py) the cwd is the anchor.  Every
    caller guards the result with a file-existence check, so a wrong
    anchor can only fall through to the explicit error, never mis-measure.
    """
    main_script_path = None
    if get_script_run_ctx is not None:
        try:
            ctx = get_script_run_ctx(suppress_warning=True)
            main_script_path = getattr(ctx, "main_script_path", None)
        except Exception:  # pragma: no cover — Streamlit version drift
            main_script_path = None
    if main_script_path:
        try:
            from streamlit import file_util
            return file_util.get_app_static_dir(main_script_path)
        except Exception:  # pragma: no cover — Streamlit version drift
            return os.path.join(os.path.dirname(main_script_path), "static")
    return os.path.join(os.getcwd(), "static")


def _find_served_file(uri: str) -> str:
    """Locate the bytes behind a ``configure_image_path``-served *uri*.

    These URIs are deliberately NOT found by the static sources (that is
    what makes ``get_image_src`` emit a served URL instead of inlining
    base64), but the bytes live on the server's disk.  Resolution:

    1. the explicit ``fs_root`` given to ``configure_image_path``;
    2. Streamlit's ``app/static`` serving convention — a base path
       ``app/static[/rest]`` maps to ``<app static dir>/rest``.

    Returns ``""`` when neither yields an existing file — the caller
    then raises the same explicit error as before.
    """
    from .image import _static_image_base, _static_image_fs_root

    if _static_image_fs_root:
        path = os.path.join(_static_image_fs_root, uri)
        if os.path.isfile(path):
            return path
    prefix = _static_image_base
    if prefix == "app/static" or prefix.startswith("app/static/"):
        rest = prefix[len("app/static"):].lstrip("/")
        base = _app_static_dir()
        path = os.path.join(base, rest, uri) if rest else os.path.join(base, uri)
        if os.path.isfile(path):
            return path
    return ""


def _parse_svg_size(svg_text: str) -> Optional[tuple[float, float]]:
    """Extract (W, H) from an SVG document, or ``None``.

    Priority: absolute ``width``/``height`` attributes on the root
    ``<svg>`` tag, then the ``viewBox``.
    """
    tag_match = _SVG_TAG_RE.search(svg_text)
    if not tag_match:
        return None
    tag = tag_match.group(0)
    w_match = _SVG_WIDTH_RE.search(tag)
    h_match = _SVG_HEIGHT_RE.search(tag)
    if w_match and h_match:
        w, h = float(w_match.group(1)), float(h_match.group(1))
        if w > 0 and h > 0:
            return (w, h)
    vb_match = _SVG_VIEWBOX_RE.search(tag)
    if vb_match:
        w, h = float(vb_match.group(1)), float(vb_match.group(2))
        if w > 0 and h > 0:
            return (w, h)
    return None


@st.cache_data(show_spinner=False)
def _read_local_image_size(file_path: str, mtime: float = 0):
    """Read the natural (W, H) of a local image file.

    Cached by Streamlit on ``(file_path, mtime)`` so a changed file is
    re-read, exactly like the base64 encoding cache.  Returns ``None``
    on failure (the caller raises the explicit error — a ``None`` cache
    entry also prevents re-reading a broken file on every rerun).
    """
    try:
        if file_path.lower().endswith(".svg"):
            with open(file_path, encoding="utf-8", errors="replace") as f:
                return _parse_svg_size(f.read())
        from PIL import Image
        with Image.open(file_path) as img:
            return (float(img.size[0]), float(img.size[1]))
    except Exception as e:
        logger.warning("Could not read image size of %s: %s", file_path, e)
        return None


def get_natural_size(uri: str, config: CropConfig) -> tuple[float, float]:
    """Resolve the natural (W, H) of the image behind *uri*.

    Priority: ``config.natural_size``, then local file bytes (Pillow for
    bitmaps, ``viewBox`` parsing for SVG).  http(s) URIs and any read
    failure raise an explicit ``ValueError`` proposing ``natural_size=``
    — never a silently empty or distorted rendering.
    """
    if config.natural_size is not None:
        return config.natural_size
    if _is_url(uri):
        raise ValueError(
            f"crop on a remote URI requires explicit dimensions: "
            f"{_NATURAL_SIZE_HINT} (uri: {uri!r})"
        )
    file_path = _find_local_file(uri) or _find_served_file(uri)
    if not file_path:
        raise ValueError(
            f"crop: cannot locate local image {uri!r} to read its "
            f"dimensions — {_NATURAL_SIZE_HINT}"
        )
    size = _read_local_image_size(file_path, mtime=os.path.getmtime(file_path))
    if size is None:
        raise ValueError(
            f"crop: cannot read the dimensions of {file_path!r} "
            f"(unsupported format, or SVG without width/height/viewBox) — "
            f"{_NATURAL_SIZE_HINT}"
        )
    return size


def _fmt(value: float) -> str:
    """Format a CSS number: at most 4 decimals, no trailing zeros."""
    return f"{value:.4f}".rstrip("0").rstrip(".")


def build_crop_html(
    img_src: str,
    alt: str,
    config: CropConfig,
    natural_w: float,
    natural_h: float,
    *,
    width: str,
    caller_css: str = "",
    inside_overlay: bool = False,
) -> str:
    """Emit the crop container ``<div>`` with its shifted ``<img>``.

    The container carries the caller CSS and the display *width* (the
    visible zone), plus the crop-critical declarations *after* it so
    they win in cascade order.  With ``inside_overlay=True`` the
    container fills the media-overlay wrapper (which then carries the
    width) instead of carrying the width itself.
    """
    t = config.top / 100
    b = config.bottom / 100
    l = config.left / 100  # noqa: E741 — l/r/t/b mirror the CSS inset naming
    r = config.right / 100
    visible_w = 1 - l - r
    visible_h = 1 - t - b
    container_width = "100%" if inside_overlay else width
    caller = f"{caller_css} " if caller_css else ""
    container_css = (
        f"{caller}overflow:hidden; width:{container_width}; "
        f"aspect-ratio:{_fmt(natural_w * visible_w)} / {_fmt(natural_h * visible_h)};"
    )
    img_css = (
        f"display:block; width:{_fmt(100 / visible_w)}%; height:auto; "
        f"transform:translate(-{_fmt(config.left)}%, -{_fmt(config.top)}%);"
    )
    return (
        f'<div class="stx-crop-box" style="{container_css}">'
        f'<img src="{img_src}" alt="{alt}" style="{img_css}"></div>'
    )
