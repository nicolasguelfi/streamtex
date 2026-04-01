"""Enrich exported HTML with navigation: sidebar TOC, marker bar, search.

Called by ``stx export html`` CLI to transform raw export HTML into a
fully navigable static document.  All generated content is pure HTML/CSS/JS
with zero server-side dependencies.
"""

import base64
import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Prop E — Auto-detect title from TOC
# ---------------------------------------------------------------------------

def _auto_title(toc: list[dict]) -> str | None:
    """Return the label of the first level-1 TOC entry, or None."""
    for entry in toc:
        if entry.get("level") == 1:
            return entry.get("_reg_label") or entry.get("title", "").lstrip("0123456789. ")
    return None


# ---------------------------------------------------------------------------
# Prop D — Strip Streamlit-only CSS rules from default.css
# ---------------------------------------------------------------------------

# Selectors that only make sense inside Streamlit's DOM
_STREAMLIT_SELECTORS = (
    "header[data-testid=",
    ".stApp",
    ".stMainBlockContainer",
    ".stElementContainer",
    'div[data-testid="stBidiComponentRegular"]',
    ".stHtml",
    ".stVerticalBlock",
)


def _strip_streamlit_css(css: str) -> str:
    """Remove CSS rule blocks whose selectors target Streamlit-only elements."""
    result = []
    i = 0
    while i < len(css):
        # Find next rule block opening brace
        brace = css.find("{", i)
        if brace == -1:
            result.append(css[i:])
            break
        selector = css[i:brace].strip()
        # Find matching closing brace (handles one level of nesting for @media)
        if selector.startswith("@"):
            # Keep @media rules — they contain CSS variables we need
            depth = 0
            j = brace
            while j < len(css):
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                    if depth == 0:
                        result.append(css[i:j + 1])
                        i = j + 1
                        break
                j += 1
            else:
                result.append(css[i:])
                break
            continue
        # Simple rule block
        close = css.find("}", brace)
        if close == -1:
            result.append(css[i:])
            break
        # Check if selector targets Streamlit
        skip = any(sel in selector for sel in _STREAMLIT_SELECTORS)
        if not skip:
            result.append(css[i:close + 1])
        i = close + 1
    return "".join(result)


# ---------------------------------------------------------------------------
# Prop A — Sidebar TOC HTML + CSS
# ---------------------------------------------------------------------------

_SIDEBAR_CSS = """
/* --- Export sidebar navigation --- */
.stx-export-sidebar {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: 280px; overflow-y: auto; overflow-x: hidden;
  background: #f8f9fa; border-right: 1px solid #e0e0e0;
  padding: 16px 12px; z-index: 1000;
  font-family: Arial, Helvetica, sans-serif; font-size: 14px;
  scrollbar-width: thin;
}
@media (prefers-color-scheme: dark) {
  .stx-export-sidebar {
    background: #1a1a2e; border-right-color: #333;
    color: #e0e0e0;
  }
}
.stx-sidebar-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}
@media (prefers-color-scheme: dark) {
  .stx-sidebar-header { border-bottom-color: #444; }
}
.stx-sidebar-header .stx-sidebar-collapse {
  background: none; border: none; cursor: pointer;
  font-size: 18px; line-height: 1; padding: 2px 6px;
  color: #888; border-radius: 4px; flex-shrink: 0;
}
.stx-sidebar-header .stx-sidebar-collapse:hover { background: #e8e8e8; }
@media (prefers-color-scheme: dark) {
  .stx-sidebar-header .stx-sidebar-collapse { color: #aaa; }
  .stx-sidebar-header .stx-sidebar-collapse:hover { background: #333; }
}
.stx-sidebar-logo {
  display: flex; align-items: center; gap: 6px;
  text-decoration: none; color: inherit; flex: 1;
  min-width: 0;
}
.stx-sidebar-logo svg { flex-shrink: 0; }
.stx-sidebar-logo span {
  font-size: 14px; font-weight: 700; color: #555;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
@media (prefers-color-scheme: dark) {
  .stx-sidebar-logo span { color: #ccc; }
}
.stx-export-sidebar .stx-search-box {
  width: 100%; padding: 6px 10px; border: 1px solid #ccc;
  border-radius: 6px; font-size: 13px; box-sizing: border-box;
  outline: none; margin-bottom: 10px; background: #fff; color: #333;
}
@media (prefers-color-scheme: dark) {
  .stx-export-sidebar .stx-search-box {
    background: #2a2a3e; border-color: #555; color: #e0e0e0;
  }
}
.stx-toc-entry {
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  padding: 2px 0; line-height: 1.4;
}
.stx-toc-entry a { text-decoration: none; color: inherit; }
.stx-toc-entry a:hover { text-decoration: underline; }
.stx-toc-entry.stx-toc-active a { font-weight: 700; color: #1155cc; }
@media (prefers-color-scheme: dark) {
  .stx-toc-entry.stx-toc-active a { color: #42D0F3; }
}
.stx-toc-l1 { font-weight: 600; }
.stx-toc-l2 { padding-left: 16px; }
.stx-toc-l3 { padding-left: 32px; font-size: 13px; }
.stx-toc-l4 { padding-left: 48px; font-size: 12px; }

/* Main content offset — transitions with sidebar */
.streamtex-page { margin-left: 280px; transition: margin-left 0.25s; }

/* External toggle — only visible when sidebar is hidden */
.stx-sidebar-toggle {
  display: none; position: fixed; top: 12px; left: 12px;
  z-index: 1001; background: #f8f9fa; border: 1px solid #ddd;
  border-radius: 6px; padding: 6px 10px; cursor: pointer;
  font-size: 18px; line-height: 1;
}
.stx-sidebar-hidden .stx-sidebar-toggle { display: block; }
@media (prefers-color-scheme: dark) {
  .stx-sidebar-toggle { background: #1a1a2e; border-color: #555; color: #e0e0e0; }
}

/* Sidebar transition */
.stx-export-sidebar { transition: transform 0.25s; }

/* Hidden state (desktop + mobile) */
.stx-sidebar-hidden .stx-export-sidebar { transform: translateX(-100%); }
.stx-sidebar-hidden .streamtex-page { margin-left: 0; }
.stx-sidebar-hidden .stx-sidebar-toggle { left: 12px; }

/* Mobile: start hidden, toggle opens */
@media (max-width: 768px) {
  .stx-export-sidebar { transform: translateX(-100%); }
  .stx-export-sidebar.stx-sidebar-open { transform: translateX(0); }
  .streamtex-page { margin-left: 0; }
}
"""


_LOGO_TINY_PATH = Path(__file__).parent / "static" / "logo-stx-tiny.png"
_LOGO_B64: str = ""
if _LOGO_TINY_PATH.exists():
    _LOGO_B64 = base64.b64encode(_LOGO_TINY_PATH.read_bytes()).decode()


def _build_sidebar_html(toc: list[dict], has_search: bool = False,
                        doc_version: str = "", lib_version: str = "") -> str:
    """Build the sidebar TOC HTML from cache data."""
    parts = ['<nav id="stx-sidebar" class="stx-export-sidebar">']
    # Header: collapse button + "Powered with StreamTeX" logo
    _logo_img = ""
    if _LOGO_B64:
        _logo_img = (
            f'<img src="data:image/png;base64,{_LOGO_B64}" '
            f'width="20" height="20" alt="StreamTeX" '
            f'style="border-radius:4px;" />'
        )
    parts.append(
        '<div class="stx-sidebar-header">'
        '<button class="stx-sidebar-collapse" id="stx-sidebar-collapse" '
        'aria-label="Hide sidebar" title="Hide sidebar">&#9776;</button>'
        f'<a class="stx-sidebar-logo" href="https://streamtex.org" '
        f'target="_blank" rel="noopener" title="streamtex.org">'
        f'{_logo_img}<span>Powered with StreamTeX</span></a>'
        '</div>'
    )
    if has_search:
        parts.append(
            '<input id="stx-search" class="stx-search-box" '
            'type="text" placeholder="Search..." autocomplete="off" />'
        )
    for entry in toc:
        level = entry.get("level", 1)
        anchor = entry.get("key_anchor", "")
        title = entry.get("title", "")
        lvl_class = f"stx-toc-l{min(level, 4)}"
        block_idx = entry.get("block_idx", entry.get("page_idx", 0))
        parts.append(
            f'<div class="stx-toc-entry {lvl_class}" data-stx-block="{block_idx}">'
            f'<a href="#{anchor}">{title}</a></div>'
        )
    # Version footer
    if doc_version:
        _ver_text = f"docs {doc_version}"
        if lib_version:
            _ver_text += f" &middot; lib {lib_version}"
        parts.append(
            f'<div style="margin-top:16px;padding-top:8px;'
            f'border-top:1px solid #e0e0e0;font-size:11px;color:#999;">'
            f'{_ver_text}</div>'
        )
    parts.append('<div style="height:40px;"></div>')  # bottom spacer
    parts.append('</nav>')
    # Hamburger toggle for mobile
    parts.append(
        '<button class="stx-sidebar-toggle" id="stx-sidebar-toggle" '
        'aria-label="Toggle navigation">&#9776;</button>'
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Prop B — Floating marker navigation bar (JS)
# ---------------------------------------------------------------------------

_MARKER_NAV_CSS = """
/* --- Floating marker navigation bar --- */
#stx-marker-nav {
  position: fixed; bottom: 24px; right: 24px; z-index: 999998;
  display: flex; align-items: center; gap: 8px;
  background: rgba(50,50,50,0.92); color: #fff;
  padding: 8px 14px; border-radius: 10px;
  font-family: Arial, Helvetica, sans-serif; font-size: 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  user-select: none; backdrop-filter: blur(8px);
}
#stx-marker-nav button {
  background: none; border: none; color: #fff; cursor: pointer;
  font-size: 16px; padding: 2px 6px; border-radius: 4px;
  line-height: 1;
}
#stx-marker-nav button:hover { background: rgba(255,255,255,0.15); }
#stx-marker-nav .stx-mn-counter {
  min-width: 48px; text-align: center; cursor: pointer;
  font-variant-numeric: tabular-nums;
}
#stx-marker-nav .stx-mn-label {
  max-width: 30ch; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; font-size: 13px; opacity: 0.8;
}
#stx-marker-nav .stx-mn-popup {
  display: none; position: absolute; bottom: 100%; right: 0;
  margin-bottom: 8px; background: rgba(40,40,40,0.95);
  border-radius: 8px; padding: 8px 0; max-height: 60vh;
  overflow-y: auto; min-width: 200px; max-width: 320px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
#stx-marker-nav .stx-mn-popup-item {
  padding: 6px 14px; cursor: pointer; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; font-size: 13px;
}
#stx-marker-nav .stx-mn-popup-item:hover { background: rgba(255,255,255,0.1); }
#stx-marker-nav .stx-mn-popup-item.stx-mn-active {
  border-left: 3px solid #42D0F3; padding-left: 11px;
}
@media (max-width: 600px) {
  #stx-marker-nav { bottom: 12px; right: 12px; padding: 6px 10px; gap: 4px; }
  #stx-marker-nav .stx-mn-label { display: none; }
}
"""

_MARKER_NAV_JS = """
(function() {
  var markers = __MARKERS__;
  var visible = markers.filter(function(m) { return !m.hidden; });
  if (!visible.length) return;
  var currentIdx = 0;

  // --- Scroll to marker ---
  function scrollTo(anchor) {
    var el = document.getElementById(anchor);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function navigateTo(idx) {
    if (idx < 0) idx = 0;
    if (idx >= visible.length) idx = visible.length - 1;
    currentIdx = idx;
    scrollTo(visible[idx].anchor);
    updateUI();
  }

  // --- Build widget ---
  var nav = document.createElement('div');
  nav.id = 'stx-marker-nav';

  var prevBtn = document.createElement('button');
  prevBtn.textContent = '\\u25C0';
  prevBtn.title = 'Previous (PageUp)';
  prevBtn.onclick = function() { navigateTo(currentIdx - 1); };

  var counter = document.createElement('span');
  counter.className = 'stx-mn-counter';
  counter.title = 'Click for marker list';

  var nextBtn = document.createElement('button');
  nextBtn.textContent = '\\u25B6';
  nextBtn.title = 'Next (PageDown)';
  nextBtn.onclick = function() { navigateTo(currentIdx + 1); };

  var label = document.createElement('span');
  label.className = 'stx-mn-label';

  // --- Popup list ---
  var popup = document.createElement('div');
  popup.className = 'stx-mn-popup';
  for (var i = 0; i < visible.length; i++) {
    (function(idx) {
      var row = document.createElement('div');
      row.className = 'stx-mn-popup-item';
      row.textContent = (idx + 1) + '. ' + visible[idx].label;
      row.onclick = function() { navigateTo(idx); popup.style.display = 'none'; };
      popup.appendChild(row);
    })(i);
  }

  counter.onclick = function(e) {
    e.stopPropagation();
    popup.style.display = popup.style.display === 'none' ? 'block' : 'none';
    highlightPopup();
  };

  nav.appendChild(prevBtn);
  nav.appendChild(counter);
  nav.appendChild(nextBtn);
  nav.appendChild(label);
  nav.appendChild(popup);
  document.body.appendChild(nav);

  // Close popup on outside click
  document.addEventListener('click', function(e) {
    if (!nav.contains(e.target)) popup.style.display = 'none';
  });

  // --- UI update ---
  function updateUI() {
    counter.textContent = (currentIdx + 1) + ' / ' + visible.length;
    label.textContent = visible[currentIdx].label;
    highlightPopup();
    // Highlight active TOC entry
    document.querySelectorAll('.stx-toc-entry').forEach(function(el) { el.classList.remove('stx-toc-active'); });
    var activeAnchor = visible[currentIdx].anchor;
    var tocLink = document.querySelector('.stx-toc-entry a[href="#' + activeAnchor + '"]');
    if (!tocLink) {
      // Try matching by marker label to TOC title
      var m = visible[currentIdx];
      document.querySelectorAll('.stx-toc-entry a').forEach(function(a) {
        if (a.textContent.indexOf(m.label) !== -1) {
          a.parentElement.classList.add('stx-toc-active');
        }
      });
    } else {
      tocLink.parentElement.classList.add('stx-toc-active');
    }
  }

  function highlightPopup() {
    var items = popup.querySelectorAll('.stx-mn-popup-item');
    for (var j = 0; j < items.length; j++) {
      items[j].classList.toggle('stx-mn-active', j === currentIdx);
    }
    // Scroll active item into view in popup
    if (items[currentIdx]) items[currentIdx].scrollIntoView({ block: 'nearest' });
  }

  // --- Keyboard navigation ---
  document.addEventListener('keydown', function(e) {
    var tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;
    if (e.key === 'PageDown' || e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault(); navigateTo(currentIdx + 1);
    } else if (e.key === 'PageUp' || e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault(); navigateTo(currentIdx - 1);
    } else if (e.key === 'Escape') {
      popup.style.display = 'none';
    }
  });

  // --- Scroll tracking ---
  var scrollTimer;
  var navigating = false;
  var origNavigateTo = navigateTo;
  navigateTo = function(idx) {
    navigating = true;
    origNavigateTo(idx);
    setTimeout(function() { navigating = false; }, 400);
  };

  window.addEventListener('scroll', function() {
    if (navigating) return;
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function() {
      var best = -1, bestDist = Infinity;
      for (var i = 0; i < visible.length; i++) {
        var el = document.getElementById(visible[i].anchor);
        if (!el) continue;
        var d = Math.abs(el.getBoundingClientRect().top - 100);
        if (d < bestDist) { bestDist = d; best = i; }
      }
      if (best >= 0 && best !== currentIdx) {
        currentIdx = best;
        updateUI();
      }
    }, 150);
  });

  // --- Init ---
  updateUI();
})();
"""


# ---------------------------------------------------------------------------
# Prop C — Search JS
# ---------------------------------------------------------------------------

_SEARCH_JS = """
(function() {
  var index = __SEARCH_INDEX__;
  var input = document.getElementById('stx-search');
  if (!input) return;

  input.addEventListener('input', function() {
    var query = input.value.toLowerCase().trim();
    var tokens = query ? query.split(/\\s+/) : [];
    var entries = document.querySelectorAll('.stx-toc-entry');

    entries.forEach(function(el) {
      if (!tokens.length) { el.style.display = ''; return; }
      var blockIdx = el.getAttribute('data-stx-block');
      var text = index[blockIdx] || '';
      var match = tokens.every(function(t) { return text.indexOf(t) !== -1; });
      el.style.display = match ? '' : 'none';
    });
  });
})();
"""


# ---------------------------------------------------------------------------
# Sidebar toggle JS
# ---------------------------------------------------------------------------

_SIDEBAR_TOGGLE_JS = """
(function() {
  var extBtn = document.getElementById('stx-sidebar-toggle');
  var colBtn = document.getElementById('stx-sidebar-collapse');
  var sidebar = document.getElementById('stx-sidebar');
  if (!sidebar) return;
  var body = document.body;

  function hideSidebar() {
    if (window.innerWidth <= 768) {
      sidebar.classList.remove('stx-sidebar-open');
    } else {
      body.classList.add('stx-sidebar-hidden');
      try { localStorage.setItem('stx-sidebar', 'hidden'); } catch(e) {}
    }
  }
  function showSidebar() {
    if (window.innerWidth <= 768) {
      sidebar.classList.add('stx-sidebar-open');
    } else {
      body.classList.remove('stx-sidebar-hidden');
      try { localStorage.setItem('stx-sidebar', 'visible'); } catch(e) {}
    }
  }

  // Collapse button inside sidebar -> hide
  if (colBtn) colBtn.addEventListener('click', hideSidebar);
  // External toggle button -> show
  if (extBtn) extBtn.addEventListener('click', showSidebar);

  // Close sidebar when clicking a TOC link (mobile)
  sidebar.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && window.innerWidth <= 768) {
      sidebar.classList.remove('stx-sidebar-open');
    }
  });
  // Restore desktop preference
  try {
    if (localStorage.getItem('stx-sidebar') === 'hidden' && window.innerWidth > 768) {
      body.classList.add('stx-sidebar-hidden');
    }
  } catch(e) {}
})();
"""


# ---------------------------------------------------------------------------
# Smooth scroll CSS
# ---------------------------------------------------------------------------

_SMOOTH_SCROLL_CSS = "html { scroll-behavior: smooth; }\n"


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

def enrich_export_html(
    raw_html: str,
    toc: list[dict] | None = None,
    markers: list[dict] | None = None,
    search_index: dict | None = None,
    doc_version: str = "",
    lib_version: str = "",
) -> str:
    """Transform raw export HTML into a fully navigable static document.

    Injects:
    - Sidebar TOC with anchor links (Prop A)
    - Floating marker navigation bar with keyboard support (Prop B)
    - Client-side search filtering (Prop C)
    - Cleaned CSS without Streamlit-only rules (Prop D)
    - Auto-detected document title (Prop E)

    Parameters
    ----------
    raw_html : str
        Complete HTML document from ``generate_export_html()``.
    toc : list[dict] | None
        TOC entries from page cache (``cache["toc"]``).
    markers : list[dict] | None
        Marker entries from page cache (``cache["markers"]``).
    search_index : dict | None
        Search index mapping block indices to plain text.
    """
    if not raw_html:
        return raw_html

    has_toc = bool(toc)
    has_markers = bool(markers)
    has_search = bool(search_index) and has_toc

    # --- Prop E: Auto-detect title ---
    if toc:
        auto_title = _auto_title(toc)
        if auto_title:
            raw_html = re.sub(
                r"<title>[^<]*</title>",
                f"<title>{auto_title}</title>",
                raw_html,
                count=1,
            )

    # --- Prop D: Strip Streamlit-only CSS ---
    raw_html = _strip_streamlit_css_in_html(raw_html)

    # --- Collect CSS and JS to inject ---
    extra_css = _SMOOTH_SCROLL_CSS
    extra_js_parts = []

    if has_toc:
        extra_css += _SIDEBAR_CSS
        extra_js_parts.append(_SIDEBAR_TOGGLE_JS)

    if has_markers:
        extra_css += _MARKER_NAV_CSS

    # --- Inject extra CSS before </style> ---
    raw_html = raw_html.replace(
        "</style>",
        extra_css + "</style>",
        1,
    )

    # --- Build and inject sidebar HTML after <body> ---
    if has_toc:
        sidebar_html = _build_sidebar_html(toc, has_search=has_search,
                                           doc_version=doc_version, lib_version=lib_version)
        raw_html = raw_html.replace("<body>", "<body>\n" + sidebar_html, 1)

    # --- Build JS block ---
    if has_markers:
        marker_js = _MARKER_NAV_JS.replace(
            "__MARKERS__", json.dumps(markers, ensure_ascii=False)
        )
        extra_js_parts.append(marker_js)

    if has_search:
        # Convert search index keys to strings for JS object
        str_index = {str(k): v for k, v in search_index.items()} if search_index else {}
        search_js = _SEARCH_JS.replace(
            "__SEARCH_INDEX__", json.dumps(str_index, ensure_ascii=False)
        )
        extra_js_parts.append(search_js)

    # --- Inject JS before </body> ---
    if extra_js_parts:
        js_block = "<script>\n" + "\n".join(extra_js_parts) + "\n</script>"
        raw_html = raw_html.replace("</body>", js_block + "\n</body>", 1)

    return raw_html


def _strip_streamlit_css_in_html(html: str) -> str:
    """Find the <style> block in the HTML and strip Streamlit-only rules."""
    style_start = html.find("<style>")
    style_end = html.find("</style>")
    if style_start == -1 or style_end == -1:
        return html
    # Extract content between <style> and </style>
    css_start = style_start + len("<style>")
    css_content = html[css_start:style_end]
    cleaned = _strip_streamlit_css(css_content)
    return html[:css_start] + cleaned + html[style_end:]
