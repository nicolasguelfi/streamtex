from __future__ import annotations

import logging
import os
from typing import Optional

from .blocks import get_static_sources
from .export import _render
from .image_crop import CropConfig, build_crop_html, get_natural_size, normalize_crop
from .media_overlay import MediaOverlay, wrap_media_overlay
from .styles import StxStyles, Style
from .utils import (
    __get_base64_encoded_image,
    __get_mime_type,
    __is_absolute_path,
    __is_relative_path,
    __is_url,
    contain_link,
)

logger = logging.getLogger(__name__)

try:
    import streamlit as _st
except ImportError:
    _st = None

_static_image_base = "app/static/images"


def configure_image_path(base_path: str):
    """Configure the base path used to resolve static image URIs."""
    global _static_image_base
    _static_image_base = base_path

def st_image(
    style: Style = StxStyles.none,
    width="100%", height="auto",
    uri: str="", alt: str="",
    link: str="", hover: bool=True,
    light_bg: bool = False,
    *,
    # --- New: editing support ---
    editable: bool = False,
    name: str = "",
    prompt: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    ai_size: Optional[str] = None,
    quality: str = "standard",
    overlay: Optional[MediaOverlay] = None,
    crop: CropConfig | tuple | list | None = None,
    natural_size: Optional[tuple[float, float]] = None,
) -> Optional[str]:
    """
    Generates an HTML `img` tag based on the image URI, with optional styles, link wrapping, and hover effects.

    :param style: A `Style` object defining CSS styles to apply to the image. Defaults to `StxStyles.none`.
    :param width: The width of the image. Can be a string (e.g., "50%") or an integer (e.g., 100). Defaults to "100%".
    :param height: The height of the image. Can be a string (e.g., "300px") or an integer (e.g., 300). Defaults to "100%".
    :param uri: The image URI. Can be:
        - A URL (e.g., "https://example.com/image.png").
        - An absolute path (e.g., "C:User/images/image.png").
        - A relative path (e.g., "/images/image.png". This can start with '.', '..', '/' and backslash).
        - A static path (e.g., images/image.png).
    :param alt: The alternative text for the image, used for accessibility or when the image cannot be displayed.
    :param link: An optional hyperlink to wrap around the image. Defaults to an empty string (no link).
    :param hover: If True, enables hover functionality for the image link. Defaults to True.
    :param overlay: Optional `MediaOverlay` badge rendered inside the image's
        final display box (e.g. an AI-transparency mark). `None` (default)
        keeps the emitted HTML strictly identical to previous versions.
    :param crop: Optional edge crop — a `CropConfig` or a 4-value tuple of
        percentages in CSS inset order `(top, right, bottom, left)`, each
        the percentage of the natural dimension removed from that edge.
        `width` then designates the *visible* zone (the crop result), and
        `height` must stay `"auto"` (the crop fixes it via aspect-ratio).
        `None` (default) keeps the emitted HTML strictly identical to
        previous versions.
    :param natural_size: Optional `(W, H)` natural pixel dimensions of the
        source image, used with `crop` when the library cannot read them
        (mandatory for http(s) URIs in this version).  Refused without
        `crop`, and refused when the `CropConfig` already carries one.
    :return: A string containing the HTML `img` tag, optionally wrapped in a hyperlink.

    Notes:
    - URLs are used directly as the `src` attribute.
    - Local files are base64 encoded for compatibility with browsers that don't allow local file paths in HTML.
    - If the URI cannot be resolved or is unsupported, the `src` attribute is left empty.
    - The function wraps the image tag in a link if `link` is provided, using the `contain_link` function.
    """
    # 0. Crop parameters — validate before any work.
    if natural_size is not None and crop is None:
        raise ValueError(
            "natural_size= requires crop= — an orphan natural_size is "
            "almost always an editing mistake"
        )
    crop_cfg = normalize_crop(crop, natural_size) if crop is not None else None

    # 1. Convert integer sizes to pixel-based strings
    if isinstance(width, int):
        width = f"{width}px"
    if isinstance(height, int):
        height = f"{height}px"

    # 1b. If a name is given, prefer the managed version (AI-generated
    #     or replaced via the editor panel) over the original URI.
    #     This runs regardless of editable so deployed (non-editable) apps
    #     still find images saved in static/images/managed/.
    if name:
        try:
            from .ai.history import get_current
            managed = get_current(name)
            if managed:
                uri = managed
        except Exception:
            logger.debug("Failed to resolve managed image for '%s'", name, exc_info=True)

    # 1c. Apply display settings from metadata (zoom / manual size).
    #     Load persisted values from JSON on first access so the zoom
    #     takes effect even in non-editable (deployed) mode.
    if name:
        _prefix = f"stx_img_display_{name}"
        _already_init = _st.session_state.get(f"{_prefix}_initialized") if _st else False
        if _st and not _already_init:
            from .image_editor import _load_display_from_metadata
            _load_display_from_metadata(name, _prefix)
        _zoom = _st.session_state.get(f"{_prefix}_zoom") if _st else None
        _dw = _st.session_state.get(f"{_prefix}_width") if _st else None
        _dh = _st.session_state.get(f"{_prefix}_height") if _st else None
        # logger.warning("[DIAG:APPLY] '%s' already_init=%s, zoom=%s, dw=%s, dh=%s, original_width=%s", name, _already_init, _zoom, _dw, _dh, width)
        if _dw:
            width = _dw
        elif _zoom is not None and _zoom != 100:
            width = f"{_zoom}%"
        if _dh:
            height = _dh

    # 2. Get the source (URL or Base64)
    img_src = get_image_src(uri)

    # 2b. AI generation fallback — when prompt is provided but no image exists.
    #     Checks the AI cache first (no API call), then auto-generates if the
    #     global AIImageConfig.auto_generate flag is True.  When a name is
    #     provided the generated image is also saved into the managed/ history
    #     so that subsequent renders use it directly via step 1b above.
    if not img_src and prompt:
        try:
            from .ai.config import AIImageConfig, get_ai_image_config
            from .ai.generate import generate_image, is_cached

            cfg = get_ai_image_config() or AIImageConfig()
            _prov = provider or cfg.provider
            _sz = ai_size or cfg.default_size

            _should_generate = (
                is_cached(prompt, provider=_prov, size=_sz,
                          quality=quality, model=model, config=cfg)
                or cfg.auto_generate
            )
            if _should_generate:
                _ai_path = generate_image(
                    prompt, provider=_prov, size=_sz,
                    quality=quality, model=model, config=cfg,
                )
                _ai_src = get_image_src(_ai_path)
                if _ai_src:
                    uri = _ai_path
                    img_src = _ai_src
                    # Persist into managed/ history when a name is given
                    if name:
                        from .ai.history import save_version
                        save_version(
                            name, _ai_path, source_type="ai_generated",
                            prompt=prompt, provider=_prov, model=model,
                            size=_sz, quality=quality,
                        )
        except Exception as exc:
            logger.warning("AI auto-generate failed for %r: %s", name or prompt[:50], exc, exc_info=True)

    # 3. Show placeholder if image not found
    if not img_src:
        placeholder = (
            f'<div style="border:2px dashed #888;padding:16px;text-align:center;'
            f'color:#888;border-radius:4px;margin:8px 0;">'
            f'Image not found: {uri}</div>'
        )
        _render(placeholder)
        return None

    # 4. Construct the CSS style string
    css_style = f"{str(style)} width: {width}; height: {height};"

    # 4b. Crop pre-checks — the height conflict is tested after step 1c
    #     so an editor-panel display_height is refused too, and the
    #     natural size is read on the *resolved* uri (managed / AI
    #     versions included).
    if crop_cfg is not None:
        if height != "auto":
            raise ValueError(
                "crop= is incompatible with an explicit height= in this "
                "version — the crop fixes the height via aspect-ratio; "
                f"remove height (got {height!r})"
            )
        natural_w, natural_h = get_natural_size(uri, crop_cfg)

    # 5. Construct the HTML
    if overlay is None:
        if crop_cfg is None:
            # Legacy emission — MUST stay byte-identical to pre-overlay
            # versions (guarded by the non-regression test in
            # tests/test_image.py).
            html_content = f'<img src="{img_src}" alt="{alt}" style="{css_style}">'
        else:
            # The caller style lives on the crop container (the visible
            # zone), never on the inner <img>, never duplicated.
            html_content = build_crop_html(
                img_src, alt, crop_cfg, natural_w, natural_h,
                width=width, caller_css=str(style),
            )
    else:
        # Native overlay slot: the wrapper carries the resolved display
        # width (known at this point — zoom / display_width applied in
        # step 1c), the img fills it, and the badge anchors inside the
        # box.  In editor mode the wrapper encloses ONLY the <img> — the
        # "Edit Image" panel is rendered separately below.
        if crop_cfg is None:
            img_css = f"{str(style)} width: 100%; height: {height};"
            inner = f'<img src="{img_src}" alt="{alt}" style="{img_css}">'
        else:
            # The overlay wrapper encloses the crop container (the badge
            # anchors on the visible zone, never on the cropped-away
            # bands); the container fills the wrapper, which carries the
            # resolved width.
            inner = build_crop_html(
                img_src, alt, crop_cfg, natural_w, natural_h,
                width=width, caller_css=str(style), inside_overlay=True,
            )
        html_content = wrap_media_overlay(
            inner, overlay, width=width, caller_css=str(style),
        )

    # 6. Handle Link Wrapping
    html_content = contain_link(html_content, link, False, hover)

    # 7. Render (pass light_bg to force a white background inside the
    #    iframe — useful for SVG diagrams designed for light mode)
    _render(html_content, light_bg=light_bg)

    # --- Editable panel ---
    if editable and _st is not None:
        # Import editor panel lazily to avoid circular imports
        from .image_editor import _render_editor_panel
        _render_editor_panel(
            uri=uri,
            name=name,
            prompt=prompt,
            provider=provider,
            model=model,
            ai_size=ai_size,
            quality=quality,
            style=style,
            width=width,
            height=height,
            alt=alt,
            link=link,
            hover=hover,
            light_bg=light_bg,
        )

    return uri if img_src else None

def get_image_src(uri: str) -> str:
    """
    Resolves the image source from a URL, absolute path, relative path, or static file.
    """
    if not uri:
        return ""
    img_src = ""
    if __is_url(uri):
        # If it's a URL, use it directly
        img_src = uri
    elif __is_absolute_path(uri) or __is_relative_path(uri):
        # If it's an absolute or relative path, try converting the file to base64
        file_path = uri if __is_absolute_path(uri) else os.path.join(os.getcwd(), uri)

        # Check if file exists before trying to read it
        if os.path.exists(file_path):
            mime_type = __get_mime_type(file_path)
            mtime = os.path.getmtime(file_path)
            encoded_image = __get_base64_encoded_image(file_path, mtime=mtime)
            if mime_type and encoded_image:
                # Use base64 encoding for local files with correct MIME type
                img_src = f"data:{mime_type};base64,{encoded_image}"
            else:
                img_src = ""  # Unsupported format or encoding failed
        else:
            img_src = "" # File not found
    else:
        # If no specific relative or absolute indicator, try configured static sources first
        static_sources = get_static_sources()

        for base in static_sources:
            # Try multiple common subdirectories in static sources
            for subdir in ["images", ""]:
                if subdir:
                    full_path = os.path.join(base, subdir, uri)
                else:
                    full_path = os.path.join(base, uri)

                if os.path.isfile(full_path):
                    mime_type = __get_mime_type(full_path)
                    mtime = os.path.getmtime(full_path)
                    encoded_image = __get_base64_encoded_image(full_path, mtime=mtime)
                    if mime_type and encoded_image:
                        img_src = f"data:{mime_type};base64,{encoded_image}"
                        return img_src

        # Fallback: use legacy static path (for Streamlit's built-in static serving)
        img_src = f"{_static_image_base}/{uri}"

    return img_src

