"""Export-aware widget wrappers — call the native st.* widget AND inject
a static HTML fallback into the export buffer.

Each helper follows the same pattern:
1. Call the native Streamlit widget (visible in the live app).
2. If export is active, generate a static HTML representation and append it.

No ``st.html()`` calls here — satisfies ``test_export_guard.py``.
"""

import base64
import io
import json
import os
import re

import pandas as pd
import streamlit as st

from .export import export_append, is_export_active

# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------

def _to_dataframe(data) -> pd.DataFrame:
    """Coerce *data* (dict, list, or DataFrame) to a ``pd.DataFrame``."""
    if isinstance(data, pd.DataFrame):
        return data
    return pd.DataFrame(data)


def _dataframe_to_html(df: pd.DataFrame) -> str:
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


def st_graphviz(dot_source, **kw):
    """Display a Graphviz graph with ``st.graphviz_chart()`` and export SVG."""
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

    *data* can be a file path (str), a URL (str), or raw bytes.
    """
    if isinstance(data, (bytes, bytearray)):
        mime = format_hint or "application/octet-stream"
        b64 = base64.b64encode(data).decode()
        return f"data:{mime};base64,{b64}", mime

    if isinstance(data, str):
        if data.startswith(("http://", "https://", "www.")):
            mime = format_hint or "application/octet-stream"
            return data, mime
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


def st_audio(data, **kw):
    """Display audio with ``st.audio()`` and export an ``<audio>`` tag."""
    st.audio(data, **kw)
    if is_export_active():
        fmt = kw.get("format")
        src, mime = _media_src(data, _AUDIO_MIME, fmt)
        export_append(
            f'<audio controls class="stx-media">'
            f'<source src="{src}" type="{mime}">'
            f'Your browser does not support the audio element.</audio>'
        )


def st_video(data, **kw):
    """Display video with ``st.video()`` and export a ``<video>`` or YouTube embed."""
    st.video(data, **kw)
    if is_export_active():
        fmt = kw.get("format")
        # YouTube URL → iframe embed
        if isinstance(data, str):
            yt = _YOUTUBE_RE.search(data)
            if yt:
                vid = yt.group(1)
                export_append(
                    f'<div class="stx-media"><iframe width="560" height="315" '
                    f'src="https://www.youtube.com/embed/{vid}" '
                    f'frameborder="0" allowfullscreen></iframe></div>'
                )
                return

        src, mime = _media_src(data, _VIDEO_MIME, fmt)
        export_append(
            f'<video controls class="stx-media" style="max-width:100%">'
            f'<source src="{src}" type="{mime}">'
            f'Your browser does not support the video element.</video>'
        )
