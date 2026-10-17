"""Export-aware widget wrappers — call the native st.* widget AND inject
a static HTML fallback into the export buffer.

Each helper follows the same pattern:
1. Call the native Streamlit widget (visible in the live app).
2. If export is active, generate a static HTML representation and append it.

No ``st.html()`` calls here — satisfies ``test_export_guard.py``.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

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


def _media_src(data, mime_map: dict, format_hint: str | None) -> tuple[str, str]:
    """Return ``(src_attr, mime)`` for an ``<audio>`` or ``<video>`` tag.

    *data* can be a file path (str), a URL (str), or raw bytes.  For a URL,
    the type comes from the extension of its path; an unknown one gives
    ``""``, and the ``<source>`` is then written without ``type`` (#114).
    """
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


def _media_box(width, align: str):
    """The st_block that sizes and places a media player (#126), or None.

    *width* is None (the full width, no box), pixels (``int``) or a CSS length
    (``"50%"``, ``"60vw"``, ``"800px"``); *align* places the narrower box. The
    player stretches inside it, live and in the export (the block's wrapper).
    """
    if align not in _ALIGN_MARGINS:
        raise ValueError(f"align must be 'center', 'left' or 'right', not {align!r}")
    if width is None:
        return None
    if isinstance(width, bool) or not isinstance(width, (int, str)):
        raise ValueError(f"width must be pixels (int) or a CSS length such as '50%', not {width!r}")
    length = f"{width}px" if isinstance(width, int) else width.strip()
    if not _CSS_LENGTH_RE.match(length):
        raise ValueError(f"width must be pixels (int) or a CSS length such as '50%', '60vw', '800px', not {width!r}")
    from .container import st_block
    from .styles import Style
    return st_block(Style(f"width:{length};max-width:100%;{_ALIGN_MARGINS[align]}", "stx_media_box"))


def st_audio(data, *, width: int | str | None = None, align: str = "center", **kw) -> None:
    """Display audio with ``st.audio()`` and export an ``<audio>`` tag.

    *width* / *align*: as for :func:`st_video` (#126).
    """
    box = _media_box(width, align)
    if box is None:
        _audio(data, **kw)
        return
    with box:
        _audio(data, _boxed=True, **kw)


def _audio(data, _boxed: bool = False, **kw):
    st.audio(data, **kw)
    if is_export_active():
        fmt = kw.get("format")
        src, mime = _media_src(data, _AUDIO_MIME, fmt)
        style = ' style="width:100%"' if _boxed else ""   # fills its sized box (#126)
        export_append(
            f'<audio controls class="stx-media"{style}>'
            f'{_source_tag(src, mime)}'
            f'Your browser does not support the audio element.</audio>'
        )


def st_video(data, *, width: int | str | None = None, align: str = "center", **kw) -> None:
    """Display video with ``st.video()`` and export a ``<video>`` or YouTube embed.

    *width* (#126): None (the full width of the container, as before), pixels
    (``int``) or a CSS length (``"50%"`` of the parent, ``"60vw"``, ``"800px"``);
    the video keeps its aspect ratio. *align* (``"center"``, ``"left"``,
    ``"right"``) places a video narrower than its container. The same box is
    drawn live and in the HTML export. ``st_zoom`` does not shrink a video,
    which fills its container: give it a width.

    ``autoplay=True`` without ``muted`` cannot start: browsers only play a
    muted video on their own. The video is then muted (one warning in the
    log); the reader can turn the sound on with the controls (#35).
    """
    global _warned_autoplay
    if kw.get("autoplay") and not kw.get("muted"):
        kw["muted"] = True
        if not _warned_autoplay:
            _warned_autoplay = True
            import logging
            logging.getLogger(__name__).warning(
                "st_video(autoplay=True) needs muted=True: browsers block a video that plays "
                "sound on its own. The video starts muted; the reader can turn the sound on.")
    box = _media_box(width, align)
    if box is None:
        _video(data, **kw)
        return
    with box:
        _video(data, _boxed=True, **kw)


def _video(data, _boxed: bool = False, **kw):
    st.video(data, **kw)
    if is_export_active():
        fmt = kw.get("format")
        # YouTube URL → iframe embed
        if isinstance(data, str):
            yt = _YOUTUBE_RE.search(data)
            if yt:
                vid = yt.group(1)
                # in a sized box (#126) the frame fills it at 16:9
                size = ('style="width:100%;height:auto;aspect-ratio:16/9" ' if _boxed
                        else 'width="560" height="315" ')
                export_append(
                    f'<div class="stx-media"><iframe {size}'
                    f'src="https://www.youtube.com/embed/{vid}" '
                    f'frameborder="0" allowfullscreen></iframe></div>'
                )
                return

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
        export_append(
            f'<video {" ".join(attrs)} class="stx-media" style="width:100%;max-width:100%">'
            f'{_source_tag(src, mime)}'
            f'Your browser does not support the video element.</video>'
        )
