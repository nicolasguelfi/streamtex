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

    Uses MutationObserver for reliable DOM-ready detection (React may batch
    the st.markdown render after the iframe script executes).
    """
    index_json = json.dumps(block_index, ensure_ascii=False)
    return f"""<script>
(function() {{
    var hostDoc = parent.document;
    var _stxBlockTexts = {index_json};

    function setup() {{
        var input = hostDoc.querySelector('[data-stx-search]');
        if (!input) return false;
        if (input._stxSearchBound) return true;
        input._stxSearchBound = true;
        input.addEventListener('input', function() {{
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
        }});
        return true;
    }}

    /* Try immediately, then use MutationObserver for reliable DOM-ready */
    if (!setup()) {{
        var obs = new MutationObserver(function() {{
            if (setup()) obs.disconnect();
        }});
        obs.observe(hostDoc.body || hostDoc.documentElement,
                    {{ childList: true, subtree: true }});
        /* Safety: disconnect after 10s to avoid leaks */
        setTimeout(function() {{ obs.disconnect(); }}, 10000);
    }}
}})();
</script>"""
