"""Export-aware widget wrappers — call the native st.* widget AND inject
a static HTML fallback into the export buffer.

Each helper follows the same pattern:
1. Call the native Streamlit widget (visible in the live app).
2. If export is active, generate a static HTML representation and append it.

No ``st.html()`` calls here — satisfies ``test_export_guard.py``.
"""

from __future__ import annotations

import base64
import functools
import io
import json
import os
import re
import struct
from typing import TYPE_CHECKING
from urllib.parse import quote, urlsplit

if TYPE_CHECKING:
    import pandas as pd

import streamlit as st

from .export import export_append, is_export_active

# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------

def _to_dataframe(data) -> "pd.DataFrame":
    """Coerce *data* (dict, list, or DataFrame) to a ``pd.DataFrame``."""
    import pandas as pd
    if isinstance(data, pd.DataFrame):
        return data
    return pd.DataFrame(data)


def _dataframe_to_html(df: "pd.DataFrame") -> str:
    """Render a DataFrame as an HTML table with StreamTeX CSS classes."""
    return df.to_html(index=False, classes="stx-table", border=0)


def _chart_to_svg(data, chart_type: str, *, x=None, y=None, size=(6, 3)) -> str:
    """Render chart *data* to an inline SVG string via matplotlib.

    Falls back to an HTML table if matplotlib is not installed.
    """
    df = _to_dataframe(data)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        # Graceful fallback: render data as a table instead of SVG
        return (
            f'<div class="stx-chart"><p><em>[{chart_type} chart — '
            f'install matplotlib for SVG export]</em></p>'
            f'{_dataframe_to_html(df)}</div>'
        )

    fig, ax = plt.subplots(figsize=size)

    plot_x = x
    plot_y = y if y is not None else [c for c in df.columns if c != x]

    if chart_type == "line":
        df.plot(x=plot_x, y=plot_y, kind="line", ax=ax)
    elif chart_type == "bar":
        df.plot(x=plot_x, y=plot_y, kind="bar", ax=ax)
    elif chart_type == "area":
        df.plot(x=plot_x, y=plot_y, kind="area", ax=ax, alpha=0.4)
    elif chart_type == "scatter":
        if plot_y and isinstance(plot_y, list):
            y_col = plot_y[0]
        else:
            y_col = plot_y
        x_col = plot_x if plot_x else df.columns[0]
        if y_col is None and len(df.columns) > 1:
            y_col = df.columns[1]
        ax.scatter(df[x_col], df[y_col])
        ax.set_xlabel(str(x_col))
        ax.set_ylabel(str(y_col))

    ax.legend(fontsize="small")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    buf.seek(0)
    svg = buf.read().decode("utf-8")
    return f'<div class="stx-chart">{svg}</div>'


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def st_dataframe(data, **kw):
    """Display a dataframe with ``st.dataframe()`` and export an HTML table."""
    st.dataframe(data, **kw)
    if is_export_active():
        df = _to_dataframe(data)
        export_append(_dataframe_to_html(df))


def st_table(data, **kw):
    """Display a static table with ``st.table()`` and export an HTML table."""
    st.table(data, **kw)
    if is_export_active():
        df = _to_dataframe(data)
        export_append(_dataframe_to_html(df))


def st_metric(label, value, delta=None, **kw):
    """Display a metric with ``st.metric()`` and export styled HTML."""
    st.metric(label, value, delta=delta, **kw)
    if is_export_active():
        delta_html = ""
        if delta is not None:
            try:
                delta_num = float(delta)
                color = "#09ab3b" if delta_num >= 0 else "#ff2b2b"
                arrow = "&#9650;" if delta_num >= 0 else "&#9660;"
            except (ValueError, TypeError):
                color = "#09ab3b"
                arrow = ""
            delta_html = (
                f'<div class="stx-metric-delta" style="color:{color}">'
                f'{arrow} {delta}</div>'
            )
        html = (
            f'<div class="stx-metric">'
            f'<div class="stx-metric-label">{label}</div>'
            f'<div class="stx-metric-value">{value}</div>'
            f'{delta_html}'
            f'</div>'
        )
        export_append(html)


def st_json(data, **kw):
    """Display JSON with ``st.json()`` and export a formatted ``<pre>`` block."""
    st.json(data, **kw)
    if is_export_active():
        if isinstance(data, str):
            formatted = data
        else:
            formatted = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        from html import escape
        export_append(f'<pre class="stx-json">{escape(formatted)}</pre>')


def st_graphviz(dot_source="", *, file: str | None = None, encoding: str = "utf-8", **kw):
    """Display a Graphviz graph with ``st.graphviz_chart()`` and export SVG."""
    from .utils import resolve_content

    dot_source = resolve_content(dot_source, file=file, encoding=encoding)
    kw.setdefault("use_container_width", True)
    st.graphviz_chart(dot_source, **kw)
    if is_export_active():
        try:
            import graphviz as gv
            src = gv.Source(dot_source)
            svg = src.pipe(format="svg").decode("utf-8")
            export_append(f'<div class="stx-graphviz">{svg}</div>')
        except Exception:
            from html import escape
            export_append(f'<pre class="stx-graphviz">{escape(dot_source)}</pre>')


def st_line_chart(data, *, x=None, y=None, **kw):
    """Display a line chart with ``st.line_chart()`` and export SVG."""
    st.line_chart(data, x=x, y=y, **kw)
    if is_export_active():
        export_append(_chart_to_svg(data, "line", x=x, y=y))


def st_bar_chart(data, *, x=None, y=None, **kw):
    """Display a bar chart with ``st.bar_chart()`` and export SVG."""
    st.bar_chart(data, x=x, y=y, **kw)
    if is_export_active():
        export_append(_chart_to_svg(data, "bar", x=x, y=y))


def st_area_chart(data, *, x=None, y=None, **kw):
    """Display an area chart with ``st.area_chart()`` and export SVG."""
    st.area_chart(data, x=x, y=y, **kw)
    if is_export_active():
        export_append(_chart_to_svg(data, "area", x=x, y=y))


def st_scatter_chart(data, *, x=None, y=None, **kw):
    """Display a scatter chart with ``st.scatter_chart()`` and export SVG."""
    st.scatter_chart(data, x=x, y=y, **kw)
    if is_export_active():
        export_append(_chart_to_svg(data, "scatter", x=x, y=y))


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------

_YOUTUBE_RE = re.compile(
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([\w-]+)'
)

_AUDIO_MIME = {
    ".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac",
}

_VIDEO_MIME = {
    ".mp4": "video/mp4", ".webm": "video/webm", ".ogg": "video/ogg",
}


# Streamlit's own limit for a file of the app's ``static`` folder.
_SERVED_MAX_BYTES = 200 * 1024 * 1024


def _static_rel(data) -> str | None:
    """The path of a local *data* file inside the app's ``static`` folder, or None (#140).

    Streamlit serves that folder at ``/app/static/``. A video or a sound
    found there is played from that URL, instead of being read whole into
    memory at every run, and the HTML export takes it as a served file. Not
    for a file reached through a link that leaves the folder, nor one over
    200 MB: Streamlit refuses to serve both.
    """
    if isinstance(data, os.PathLike):
        data = os.fspath(data)
    if (not isinstance(data, str) or data.startswith(("http://", "https://", "www.", "data:"))
            or not os.path.isfile(data)):
        return None
    from .image_crop import _app_static_dir
    root = _app_static_dir()
    root_real = os.path.realpath(root)
    for path, base in ((os.path.abspath(data), os.path.abspath(root)),
                       (os.path.realpath(data), root_real)):
        try:
            rel = os.path.relpath(path, base)
        except ValueError:      # another drive
            continue
        if rel != os.pardir and not rel.startswith(os.pardir + os.sep):
            break
    else:
        return None
    if not os.path.realpath(os.path.join(root_real, rel)).startswith(root_real + os.sep):
        return None
    if os.path.getsize(data) > _SERVED_MAX_BYTES:
        return None
    return rel.replace(os.sep, "/")


def _live_source(data):
    """What ``st.video`` / ``st.audio`` receives: a served URL for a file of ``static`` (#140).

    Streamlit plays a ``/app/static/`` URL as it is, without its media file
    manager. Without static serving (``server.enableStaticServing``), or for
    any other source, *data* is passed on unchanged.
    """
    rel = _static_rel(data)
    if rel is None:
        return data
    try:
        serving = st.get_option("server.enableStaticServing")
    except Exception:  # pragma: no cover — Streamlit version drift
        serving = False
    return "/app/static/" + quote(rel) if serving else data


def _media_src(data, mime_map: dict, format_hint: str | None) -> tuple[str, str]:
    """Return ``(src_attr, mime)`` for an ``<audio>`` or ``<video>`` tag.

    *data* can be a file path (str), a URL (str), or raw bytes.  For a URL,
    the type comes from the extension of its path; an unknown one gives
    ``""``, and the ``<source>`` is then written without ``type`` (#114).
    A file of the app's ``static`` folder becomes ``app/static/…``, which
    the export copies into its ``data/`` folder (#140); another local file
    is inlined.
    """
    if isinstance(data, os.PathLike):
        data = os.fspath(data)
    if isinstance(data, (bytes, bytearray)):
        mime = format_hint or "application/octet-stream"
        b64 = base64.b64encode(data).decode()
        return f"data:{mime};base64,{b64}", mime

    if isinstance(data, str):
        if data.startswith(("http://", "https://", "www.")):
            ext = os.path.splitext(urlsplit(data).path)[1].lower()
            return data, format_hint or mime_map.get(ext, "")
        # Local file path
        ext = os.path.splitext(data)[1].lower()
        mime = format_hint or mime_map.get(ext, "application/octet-stream")
        rel = _static_rel(data)
        if rel is not None:
            return f"app/static/{rel}", mime
        try:
            with open(data, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{b64}", mime
        except OSError:
            return data, mime

    # io.BytesIO or other file-like
    if hasattr(data, "read"):
        raw = data.read()
        mime = format_hint or "application/octet-stream"
        b64 = base64.b64encode(raw).decode()
        return f"data:{mime};base64,{b64}", mime

    return str(data), format_hint or "application/octet-stream"


def _source_tag(src: str, mime: str) -> str:
    """``<source>`` with its ``type``, or without one when it is unknown.

    The browser skips a source whose ``type`` it cannot play, such as
    ``application/octet-stream``; without ``type`` it reads the file to decide.
    """
    type_attr = f' type="{mime}"' if mime else ""
    return f'<source src="{src}"{type_attr}>'


_ALIGN_MARGINS = {"center": "margin-left:auto;margin-right:auto;",
                  "left": "margin-right:auto;", "right": "margin-left:auto;"}
_CSS_LENGTH_RE = re.compile(r"^\d+(\.\d+)?(px|%|vw|vh|em|rem)$")
_warned_autoplay = False


def _media_box(width, align: str, max_vw=None, max_vh=None, ratio: float | None = None):
    """The st_block that sizes and places a media player (#126), or None.

    *width* is None (the full width, no box), pixels (``int``) or a CSS length
    (``"50%"``, ``"60vw"``, ``"800px"``); *align* places the narrower box. The
    player stretches inside it, live and in the export (the block's wrapper).
    *max_vw* / *max_vh* bound the box (#141): its width becomes
    ``min(width, max_vw vw, max_vh vh × ratio)``; without a *ratio* the
    height bound cannot be turned into a width and is left out.
    """
    if align not in _ALIGN_MARGINS:
        raise ValueError(f"align must be 'center', 'left' or 'right', not {align!r}")
    if width is None and max_vw is None and max_vh is None:
        return None
    if width is None:
        length = "100%"
    else:
        if isinstance(width, bool) or not isinstance(width, (int, str)):
            raise ValueError(f"width must be pixels (int) or a CSS length such as '50%', not {width!r}")
        length = f"{width}px" if isinstance(width, int) else width.strip()
        if not _CSS_LENGTH_RE.match(length):
            raise ValueError(
                f"width must be pixels (int) or a CSS length such as '50%', '60vw', '800px', not {width!r}")
    parts = [length]
    if max_vw is not None:
        parts.append(f"{_num(max_vw)}vw")
    if max_vh is not None and ratio is not None:
        parts.append(f"calc({_num(max_vh)}vh * {ratio:.6f})")
    if len(parts) > 1:
        length = f"min({', '.join(parts)})"
    from .container import st_block
    from .styles import Style
    return st_block(Style(f"width:{length};max-width:100%;{_ALIGN_MARGINS[align]}", "stx_media_box"))


def _num(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


# -- the picture size of a video (#141) --------------------------------------

_MP4_HEAD = 1 << 20          # the header of a "faststart" MP4 lies in its first MiB
_warned_ratio: set = set()


def _mp4_boxes(buf: bytes, start: int, end: int):
    """``(type, payload start, payload end, complete)`` of the boxes in ``buf[start:end]``."""
    i = start
    while i + 8 <= end:
        size, kind = struct.unpack(">I4s", buf[i:i + 8])
        head = 8
        if size == 1:
            if i + 16 > end:
                return
            size, head = struct.unpack(">Q", buf[i + 8:i + 16])[0], 16
        elif size == 0:
            size = end - i
        if size < head:
            return
        yield kind, i + head, min(i + size, end), i + size <= end
        i += size


def _tkhd_size(buf: bytes, start: int, end: int) -> tuple[float, float] | None:
    """The displayed size in the first ``tkhd`` with a picture (audio tracks have 0 × 0)."""
    for kind, a, b, complete in _mp4_boxes(buf, start, end):
        if kind in (b"moov", b"trak"):
            size = _tkhd_size(buf, a, b)
            if size:
                return size
        elif kind == b"tkhd" and complete and b - a >= 84:
            matrix = struct.unpack(">9i", buf[b - 44:b - 8])
            w, h = (v / 65536 for v in struct.unpack(">II", buf[b - 8:b]))
            if w > 0 and h > 0:
                # a quarter turn (a phone held upright) swaps the sides on screen
                return (h, w) if matrix[0] == 0 and matrix[4] == 0 else (w, h)
    return None


@functools.lru_cache(maxsize=256)
def _mp4_size(path: str, mtime: float) -> tuple[float, float] | None:
    """Width and height of an MP4 / MOV picture, read in its first MiB, or None."""
    try:
        with open(path, "rb") as f:
            head = f.read(_MP4_HEAD)
    except OSError:
        return None
    return _tkhd_size(head, 0, len(head))


def _video_ratio(data, natural_size) -> float | None:
    """Width / height of the picture: *natural_size*, else read from a local MP4.

    Warns once per source when it cannot be read: the height bound is then
    left out.
    """
    if natural_size is not None:
        return natural_size[0] / natural_size[1]
    if isinstance(data, os.PathLike):
        data = os.fspath(data)
    size = None
    if isinstance(data, str) and os.path.isfile(data):
        size = _mp4_size(os.path.abspath(data), os.path.getmtime(data))
    if size:
        return size[0] / size[1]
    key = data if isinstance(data, str) else type(data).__name__
    if key not in _warned_ratio:
        _warned_ratio.add(key)
        import logging
        logging.getLogger(__name__).warning(
            "st_video(max_vh=): the picture size of %s cannot be read, so the height bound is "
            "left out. An MP4 needs its header first (ffmpeg -movflags +faststart); otherwise "
            "give natural_size=(width, height).", key)
    return None


def _check_bounds(max_vw, max_vh, natural_size) -> None:
    for name, bound in (("max_vw", max_vw), ("max_vh", max_vh)):
        if bound is not None and (isinstance(bound, bool) or not isinstance(bound, (int, float))
                                  or bound <= 0):
            raise ValueError(f"{name} must be a positive number of {name[-2:]} units, not {bound!r}")
    if natural_size is not None:
        if max_vw is None and max_vh is None:
            raise ValueError("natural_size= goes with max_vw= / max_vh=")
        if (not isinstance(natural_size, (tuple, list)) or len(natural_size) != 2
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0
                       for v in natural_size)):
            raise ValueError(f"natural_size must be (width, height), two positive numbers, not {natural_size!r}")


def st_audio(data, *, width: int | str | None = None, align: str = "center", **kw) -> None:
    """Display audio with ``st.audio()`` and export an ``<audio>`` tag.

    *width* / *align*, and a file under ``static/``: as for :func:`st_video`
    (#126, #140).
    """
    box = _media_box(width, align)
    if box is None:
        _audio(data, **kw)
        return
    with box:
        _audio(data, _boxed=True, **kw)


def _audio(data, _boxed: bool = False, **kw):
    st.audio(_live_source(data), **kw)
    if is_export_active():
        fmt = kw.get("format")
        src, mime = _media_src(data, _AUDIO_MIME, fmt)
        style = ' style="width:100%"' if _boxed else ""   # fills its sized box (#126)
        export_append(
            f'<audio controls class="stx-media"{style}>'
            f'{_source_tag(src, mime)}'
            f'Your browser does not support the audio element.</audio>'
        )


def st_video(data, *, width: int | str | None = None, align: str = "center",
             max_vw: float | None = None, max_vh: float | None = None,
             natural_size: tuple[float, float] | None = None,
             theater: bool | str = False, fit: str = "contain", fullscreen: bool = False,
             **kw) -> None:
    """Display video with ``st.video()`` and export a ``<video>`` or YouTube embed.

    *width* (#126): None (the full width of the container, as before), pixels
    (``int``) or a CSS length (``"50%"`` of the parent, ``"60vw"``, ``"800px"``);
    the video keeps its aspect ratio. *align* (``"center"``, ``"left"``,
    ``"right"``) places a video narrower than its container. The same box is
    drawn live and in the HTML export. Inside ``st_zoom``, a video without a
    width still fills its container, while an explicit width (px, vw, vh) is
    multiplied by the zoom factor, like any other length: ``width="50vh"``
    in ``st_zoom(130)`` gives a 65 vh wide player.

    ``autoplay=True`` without ``muted`` cannot start: browsers only play a
    muted video on their own. The video is then muted (one warning in the
    log); the reader can turn the sound on with the controls (#35). An
    explicit ``muted=False`` is kept: a browser that allows sound on its own
    (a projection profile) plays it with sound, others wait for a click.

    *max_vw* / *max_vh* (#141), as in :func:`st_image`: the largest
    width in % of the window width, and the largest height in % of the
    window height. The player takes the largest size within *width* (the
    container by default) and both bounds, without distortion:
    ``st_video(clip, max_vw=100, max_vh=50)`` gives a 960 × 540 player for
    a 16:9 clip in a 1920 × 1080 window, and fills a narrow window's
    width. The picture's shape is read from a local MP4 (its header must
    come first: ``ffmpeg -movflags +faststart``); for a URL or another
    file, give *natural_size* ``(width, height)``. When it cannot be read,
    one warning is logged and only *max_vw* applies. Inside ``st_zoom``,
    the bounds are multiplied by the zoom like any length. Not with
    *theater*.

    A local file under the app's ``static/`` folder (static serving on) is
    played from its ``/app/static/…`` URL, not read into memory at every
    run, and the HTML export copies it into ``data/`` (#140). Put large
    videos there.

    A video that dominates the screen (#56), live and in the HTML export:

    - *theater*: ``"slide"`` (or ``True``) fills the screen height in the
      flow of the document, on black, and scrolls with its slide;
      ``"window"`` covers the whole window while its slide is on screen —
      the × button or Esc closes it, leaving the slide closes it and pauses
      the video, coming back opens it again. *width* / *align* do not apply.
    - *fit*: ``"contain"`` (default) shows the whole picture, with black
      bars when the screen has another shape; ``"cover"`` fills the screen
      and crops the edges.
    - *fullscreen*: ``True`` asks the browser for fullscreen on the first
      Play (browsers allow fullscreen only after a click, so never at page
      load) and leaves it when the video ends, unless it loops. The
      player's own fullscreen button is always there. Not possible for a
      YouTube video (a frame of another site): its own button remains.
    """
    global _warned_autoplay
    if kw.get("autoplay") and "muted" not in kw:
        kw["muted"] = True
        if not _warned_autoplay:
            _warned_autoplay = True
            import logging
            logging.getLogger(__name__).warning(
                "st_video(autoplay=True) needs muted=True: browsers block a video that plays "
                "sound on its own. The video starts muted; the reader can turn the sound on.")
    mode = _theater_mode(theater)
    if fit not in _FITS:
        raise ValueError(f"fit must be 'contain' or 'cover', not {fit!r}")
    if not isinstance(fullscreen, bool):
        raise ValueError(f"fullscreen must be True or False, not {fullscreen!r}")
    bounded = max_vw is not None or max_vh is not None
    _check_bounds(max_vw, max_vh, natural_size)
    if mode and bounded:
        raise ValueError("max_vw / max_vh do not apply with theater=: the theater sizes the video")
    if mode:
        _staged_video(data, mode, fit, fullscreen, kw)
        return
    ratio = _video_ratio(data, natural_size) if max_vh is not None else None
    box = _media_box(width, align, max_vw, max_vh, ratio)
    if fullscreen:
        if box is None:
            _staged_video(data, mode, fit, fullscreen, kw)
            return
        with box:
            _staged_video(data, mode, fit, fullscreen, kw)
        return
    if box is None:
        _video(data, **kw)
        return
    with box:
        _video(data, _boxed=True, **kw)


_FITS = ("contain", "cover")


def _theater_mode(theater) -> str:
    """``False`` → ``""``; ``True`` / ``"slide"`` → ``"slide"``; ``"window"``."""
    if theater is False or theater is None:
        return ""
    if theater is True:
        return "slide"
    if theater in ("slide", "window"):
        return theater
    raise ValueError(f"theater must be True, False, 'slide' or 'window', not {theater!r}")


def _staged_video(data, mode: str, fit: str, fullscreen: bool, kw: dict) -> None:
    """A video under the stage script (#56): a marker the script finds, then the player.

    Live, the marker and ``st.video`` share one ``st.container``, which the
    script turns into the box; in the export, the box is written here.
    """
    marker = (f'<span class="stx-video-marker" data-stx-video="{mode}" data-stx-fit="{fit}" '
              f'data-stx-fs="{int(fullscreen)}" data-stx-loop="{int(bool(kw.get("loop")))}" '
              f'style="display:none"></span>')
    close = ('<button type="button" class="stx-vbox-close" aria-label="Close" title="Close (Esc)">'
             '&times;</button>' if mode == "window" else "")
    with st.container():
        st.markdown(marker + close, unsafe_allow_html=True)
        st.video(_live_source(data), **kw)
    if is_export_active():
        classes = "stx-vbox" + (f" stx-theater-{mode}" if mode else "") + f" stx-fit-{fit}"
        export_append(f'<div class="stx-vbox-slot"><div class="{classes}">{marker}{close}'
                      f'{_video_export_html(data, True, kw)}</div></div>')


def _video(data, _boxed: bool = False, **kw):
    st.video(_live_source(data), **kw)
    if is_export_active():
        export_append(_video_export_html(data, _boxed, kw))


def _video_export_html(data, boxed: bool, kw: dict) -> str:
    """The exported player: a ``<video>``, or a YouTube frame."""
    fmt = kw.get("format")
    # YouTube URL → iframe embed
    if isinstance(data, str):
        yt = _YOUTUBE_RE.search(data)
        if yt:
            vid = yt.group(1)
            # in a sized box (#126) the frame fills it at 16:9
            size = ('style="width:100%;height:auto;aspect-ratio:16/9" ' if boxed
                    else 'width="560" height="315" ')
            return (f'<div class="stx-media"><iframe {size}'
                    f'src="https://www.youtube.com/embed/{vid}" '
                    f'frameborder="0" allowfullscreen></iframe></div>')

    src, mime = _media_src(data, _VIDEO_MIME, fmt)
    # The export plays the video the way the live page does: the same
    # ``autoplay`` / ``loop`` / ``muted`` given to ``st.video()``, and the
    # full width of its container (``st.video`` stretches by default).
    # Browsers only autoplay a muted video, inline on phones.
    attrs = ["controls"]
    if kw.get("autoplay"):
        attrs += ["autoplay", "playsinline"]
    if kw.get("loop"):
        attrs.append("loop")
    if kw.get("muted"):
        attrs.append("muted")
    return (f'<video {" ".join(attrs)} class="stx-media" style="width:100%;max-width:100%">'
            f'{_source_tag(src, mime)}'
            f'Your browser does not support the video element.</video>')
