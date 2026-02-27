"""Full-text search for StreamTeX TOC — collects block text during render."""

from __future__ import annotations

import json
from typing import Optional

from .utils import strip_html


class TextCollector:
    """Accumulates plain-text fragments per block during rendering."""

    def __init__(self):
        self._current_block: int | None = None
        self._blocks: dict[int, list[str]] = {}
        self._active: bool = True

    def set_block(self, idx: int) -> None:
        self._current_block = idx

    def record(self, html: str) -> None:
        if not self._active or self._current_block is None:
            return
        text = strip_html(html).strip()
        if text:
            self._blocks.setdefault(self._current_block, []).append(text)

    def get_index(self) -> dict[int, str]:
        return {k: " ".join(v).lower() for k, v in self._blocks.items()}


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_collector: Optional[TextCollector] = None


def start_collector() -> TextCollector:
    global _collector
    _collector = TextCollector()
    return _collector


def stop_collector() -> dict[int, str]:
    global _collector
    if _collector is None:
        return {}
    index = _collector.get_index()
    _collector = None
    return index


def record_if_active(html: str) -> None:
    if _collector is not None:
        _collector.record(html)


# ---------------------------------------------------------------------------
# Client-side search — HTML input (st.markdown) + JS (components.html)
# ---------------------------------------------------------------------------

def generate_search_input_html(placeholder: str = "Search...") -> str:
    """Return HTML for the search input — rendered via st.markdown."""
    return (
        f'<div style="margin-bottom:8px;">'
        f'<input data-stx-search="1" type="text" placeholder="{placeholder}"'
        f' style="width:100%;padding:6px 10px;border:1px solid #ccc;'
        f'border-radius:6px;font-size:14px;box-sizing:border-box;outline:none;" />'
        f'</div>'
    )


def generate_search_script(block_index: dict[int, str]) -> str:
    """Return <script> HTML for components.html() — runs in iframe, targets parent DOM.

    Uses setInterval retry loop (up to 60s) for reliable DOM-ready detection.
    Streamlit's rehype-raw plugin is lazily loaded, so data-stx-* attributes
    may not appear in the DOM for several seconds on slow/cold deployments.
    """
    index_json = json.dumps(block_index, ensure_ascii=False)
    return f"""<script>
(function() {{
    var hostDoc = parent.document;
    var _stxBlockTexts = {index_json};
    var _t0 = Date.now();

    function setup() {{
        var input = hostDoc.querySelector('[data-stx-search]');
        if (!input) return false;
        /* Replace previous handler so updated index data takes effect.
           The DOM element may survive across Streamlit reruns, so we
           cannot rely on a simple bound-once flag. */
        if (input._stxSearchHandler) {{
            input.removeEventListener('input', input._stxSearchHandler);
        }}
        var elems = hostDoc.querySelectorAll('[data-stx-block]');
        console.info('[STX Search] setup OK after ' + (Date.now() - _t0) + 'ms, '
                     + elems.length + ' TOC entries');
        var handler = function() {{
            var query = input.value.toLowerCase().trim();
            var tokens = query ? query.split(/\\s+/) : [];
            var elems = hostDoc.querySelectorAll('[data-stx-block]');
            for (var i = 0; i < elems.length; i++) {{
                var blockIdx = elems[i].getAttribute('data-stx-block');
                if (!tokens.length) {{
                    elems[i].style.display = '';
                    continue;
                }}
                var text = _stxBlockTexts[blockIdx] || '';
                var match = true;
                for (var t = 0; t < tokens.length; t++) {{
                    if (text.indexOf(tokens[t]) === -1) {{ match = false; break; }}
                }}
                elems[i].style.display = match ? '' : 'none';
            }}
        }};
        input.addEventListener('input', handler);
        input._stxSearchHandler = handler;
        return true;
    }}

    /* Try immediately, then retry every 500ms for up to 60s.
       Covers rehype-raw lazy loading on slow/cold Render deployments. */
    if (!setup()) {{
        var _warned = false;
        var _iv = setInterval(function() {{
            var elapsed = Date.now() - _t0;
            if (setup()) {{
                clearInterval(_iv);
                return;
            }}
            if (!_warned && elapsed > 5000) {{
                console.warn('[STX Search] still waiting for data-stx-search ('
                             + elapsed + 'ms)');
                _warned = true;
            }}
            if (elapsed > 60000) {{
                clearInterval(_iv);
                console.error('[STX Search] setup failed after 60s '
                              + '— data-stx-search never appeared');
            }}
        }}, 500);
    }}
}})();
</script>"""
