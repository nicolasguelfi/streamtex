"""Enrich exported HTML with navigation: sidebar TOC, marker bar, search.

Called by ``stx export html`` CLI to transform raw export HTML into a
fully navigable static document.  All generated content is pure HTML/CSS/JS
with zero server-side dependencies.
"""

import base64
import json
import re
from pathlib import Path

from .export import _get_theme_color

# Path to the cross-context scroll-spy script.  Same file is used by the
# live runtime via :mod:`streamtex.marker_runtime`.  Loading at import
# time keeps the export fast — no I/O per export call.
_SCROLL_SPY_JS_PATH = Path(__file__).resolve().parent / "static" / "js" / "stx_scroll_spy.js"
try:
    _SCROLL_SPY_JS = _SCROLL_SPY_JS_PATH.read_text(encoding="utf-8")
except OSError:
    _SCROLL_SPY_JS = ""

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
/* --- Export sidebar navigation ---
 *
 * Colors are pulled from CSS custom properties on :root that ``enrich_export_html``
 * sets from the project's ``.streamlit/config.toml`` theme (with Streamlit 1.56
 * dark/light defaults as fallback).  This keeps the static export visually
 * aligned with the live app instead of switching to a hardcoded palette based
 * on the reader's OS ``prefers-color-scheme`` preference.
 */
/* Layout variable for the sidebar width.  The default 280px is also the
 * "reset" target for the double-click on the resize handle (see
 * _SIDEBAR_RESIZE_JS).  At runtime the JS reads any persisted width
 * from localStorage and updates this variable. */
:root { --stx-sidebar-width: 280px; }

.stx-export-sidebar {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: var(--stx-sidebar-width, 280px);
  overflow-y: auto; overflow-x: hidden;
  background: var(--stx-export-sidebar-bg, #f8f9fa);
  color: var(--stx-export-sidebar-fg, #333);
  border-right: 1px solid var(--stx-export-sidebar-border, #e0e0e0);
  padding: 16px 12px; z-index: 1000;
  font-family: Arial, Helvetica, sans-serif; font-size: 14px;
  scrollbar-width: thin;
}

/* Drag-resize handle (P1 + P4: drag + double-click to reset). */
.stx-sidebar-resize-handle {
  position: absolute; top: 0; right: 0; bottom: 0;
  width: 6px; cursor: ew-resize;
  background: transparent;
  transition: background 0.15s;
  /* Make it click-through-safe when the user is not actively grabbing it. */
  touch-action: none;
}
.stx-sidebar-resize-handle:hover,
.stx-sidebar-resize-handle:focus-visible,
body.stx-sidebar-resizing .stx-sidebar-resize-handle {
  background: var(--stx-export-link, #1155cc);
  opacity: 0.5;
}
.stx-sidebar-resize-handle:focus { outline: none; }

/* While dragging, prevent text selection and freeze the margin/width
 * transition so the resize tracks the pointer with no lag. */
body.stx-sidebar-resizing { user-select: none; cursor: ew-resize; }
body.stx-sidebar-resizing .stx-export-sidebar,
body.stx-sidebar-resizing .streamtex-page { transition: none !important; }
.stx-sidebar-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 1px solid var(--stx-export-sidebar-border, #e0e0e0);
}
.stx-sidebar-header .stx-sidebar-collapse {
  background: none; border: none; cursor: pointer;
  font-size: 18px; line-height: 1; padding: 2px 6px;
  color: var(--stx-export-sidebar-muted, #888); border-radius: 4px; flex-shrink: 0;
}
.stx-sidebar-header .stx-sidebar-collapse:hover {
  background: var(--stx-export-sidebar-hover, #e8e8e8);
}
.stx-sidebar-logo {
  display: flex; align-items: center; gap: 6px;
  text-decoration: none; color: inherit; flex: 1;
  min-width: 0;
}
.stx-sidebar-logo svg { flex-shrink: 0; }
.stx-sidebar-logo span {
  font-size: 14px; font-weight: 700;
  color: var(--stx-export-sidebar-fg, #555);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.stx-export-sidebar .stx-search-box {
  width: 100%; padding: 6px 10px;
  border: 1px solid var(--stx-export-sidebar-input-border, #ccc);
  border-radius: 6px; font-size: 13px; box-sizing: border-box;
  outline: none; margin-bottom: 10px;
  background: var(--stx-export-sidebar-input-bg, #fff);
  color: var(--stx-export-sidebar-fg, #333);
}
/* Text-truncation lives on the inner <a>, not on the entry, so the active
 * indicator's ``::before`` (positioned at left:-8px) is not clipped by the
 * entry's own overflow box.  Keeping ``overflow: hidden`` on the entry
 * (the historical placement) clipped the bar entirely in static exports —
 * fixed in 0.6.33 by moving overflow/ellipsis down to the link. */
.stx-toc-entry {
  padding: 2px 0; line-height: 1.4;
  position: relative;
}
/* TOC entries are rendered as hyperlinks — same look as the live Streamlit
 * sidebar (linkColor + underlined), driven by the project's theme via the
 * --stx-export-link variable.  No bold weight on any TOC item (per user
 * request): the active entry is marked by a subtle left-border indicator
 * via the cross-context ``.stx-nav-active`` class (driven by
 * ``streamtex/static/js/stx_scroll_spy.js``), not a font-weight change. */
.stx-toc-entry a {
  display: block;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--stx-export-link, #1155cc);
  text-decoration: underline;
  font-weight: normal;
}
.stx-toc-entry a:hover { text-decoration: underline; }
.stx-toc-entry.stx-nav-active::before {
  content: '';
  position: absolute;
  left: -8px; top: 4px; bottom: 4px;
  width: 3px;
  background: var(--stx-export-link, #1155cc);
  border-radius: 2px;
}
/* Brighter text for the active entry — mirrors the live Streamlit
 * sidebar's per-page colouring (``--stx-link-active-color``).  The
 * project's theme only sets ``linkColor``; the active variant is
 * derived at render time via ``color-mix(white 35%)`` so dark themes
 * shift visibly lighter without the project having to declare a
 * separate active colour.  Falls through to ``--stx-export-link`` on
 * browsers without ``color-mix()`` (Safari < 16.2 / Chrome < 111). */
.stx-toc-entry.stx-nav-active a {
  color: color-mix(in srgb, var(--stx-export-link, #1155cc) 65%, white);
}
.stx-toc-l2 { padding-left: 16px; }
.stx-toc-l3 { padding-left: 32px; font-size: 13px; }
.stx-toc-l4 { padding-left: 48px; font-size: 12px; }

/* Main content offset — transitions with sidebar.  The margin tracks
 * the same --stx-sidebar-width variable that the sidebar's own width
 * uses, so resizing or toggling stays in lockstep with a single CSS
 * write. */
.streamtex-page {
  margin-left: var(--stx-sidebar-width, 280px);
  transition: margin-left 0.25s;
}

/* External toggle — only visible when sidebar is hidden */
.stx-sidebar-toggle {
  display: none; position: fixed; top: 12px; left: 12px;
  z-index: 1001;
  background: var(--stx-export-sidebar-bg, #f8f9fa);
  border: 1px solid var(--stx-export-sidebar-input-border, #ddd);
  color: var(--stx-export-sidebar-fg, inherit);
  border-radius: 6px; padding: 6px 10px; cursor: pointer;
  font-size: 18px; line-height: 1;
}
.stx-sidebar-hidden .stx-sidebar-toggle { display: block; }

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
    # Drag-resize handle on the right edge.  Double-click resets to 280px.
    # tabindex=0 + role="separator" makes it keyboard-focusable; the JS
    # listens for ArrowLeft/ArrowRight (Shift = bigger step) when focused.
    parts.append(
        '<div class="stx-sidebar-resize-handle" '
        'role="separator" aria-orientation="vertical" '
        'aria-label="Resize sidebar (double-click to reset)" '
        'tabindex="0"></div>'
    )
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
    // The TOC sidebar active indicator is owned by the cross-context
    // scroll-spy (stx_scroll_spy.js) — it tracks ALL TOC entry anchors
    // (not just markers), so the indicator can land on any level and
    // not just L1.  Nothing to do here.
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

  // Deep-link hook (see _DEEPLINK_JS): select the bar entry for a GLOBAL
  // marker index without scrolling (the caller already scrolled).
  window.__stxMarkerNavigateTo = function(globalIdx) {
    for (var i = 0; i < visible.length; i++) {
      if (visible[i].index === globalIdx) { currentIdx = i; updateUI(); return; }
    }
  };
})();
"""


# ---------------------------------------------------------------------------
# Deep link -- ?marker= / ?page= / #<key> / #stx-goto-<n> (see deeplink.py)
# ---------------------------------------------------------------------------

_DEEPLINK_JS = r"""
(function() {
  var markers = __MARKERS__;
  var toc = __TOC__;
  if (!markers.length && !toc.length) return;
  var stxMarkerRe = /^stx-marker-(.+)-\d+$/;

  // Mirror of TOCRegistry.get_key_anchor (toc.py)
  function slugOf(text) {
    var s = String(text || '').toLowerCase()
      .replace(/[.'"!?@#$%^&*()+=\[\]{}|\\\/<>,;:~`]/g, '-')
      .replace(/[-\s]+/g, '-').replace(/^-+|-+$/g, '');
    return s || 'section';
  }
  function markerSlug(m) {
    var mm = stxMarkerRe.exec(m.anchor || '');
    return mm ? mm[1] : slugOf(m.label);
  }
  function findMarker(ref) {
    if (!ref) return null;
    var i;
    for (i = 0; i < markers.length; i++) if (markers[i].key && markers[i].key === ref) return markers[i];
    for (i = 0; i < markers.length; i++) if (markers[i].anchor === ref) return markers[i];
    var slug = slugOf(ref);
    for (i = 0; i < markers.length; i++) {
      if (markerSlug(markers[i]) === slug || slugOf(markers[i].label) === slug) return markers[i];
    }
    return null;
  }
  /* First anchor of page n: a marker, else a TOC heading (pages without
     markers -- a footer, a references appendix -- stay reachable).      */
  function firstOfPage(n) {
    var i;
    for (i = 0; i < markers.length; i++) {
      if ((markers[i].page_idx || 0) === n) return markers[i];
    }
    for (i = 0; i < toc.length; i++) {
      if ((toc[i].page_idx || 0) === n && toc[i].key_anchor) {
        return { anchor: toc[i].key_anchor, index: -1 };
      }
    }
    return null;
  }
  function pageNumber(raw) {                              /* whole value must be digits */
    raw = (raw || '').trim();
    return /^\d+$/.test(raw) ? parseInt(raw, 10) : NaN;
  }
  function fromQuery() {
    var q = new URLSearchParams(window.location.search);
    var ref = (q.get('marker') || '').trim();
    var m = ref ? findMarker(ref) : null;
    if (!m) {
      var p = pageNumber(q.get('page'));                  /* 1-based */
      if (!isNaN(p) && p >= 1) m = firstOfPage(p - 1);
    }
    return m;
  }
  function fromHash() {
    var h = (window.location.hash || '').replace(/^#/, '');
    try { h = decodeURIComponent(h); } catch (e) { /* malformed %-encoding: use as is */ }
    h = h.trim();
    if (!h) return null;
    var g = /^stx-goto-(\d+)$/.exec(h);                    /* 0-based, sidebar convention */
    return g ? firstOfPage(parseInt(g[1], 10)) : findMarker(h);
  }
  function goTo(m) {
    if (!m) return;
    var el = document.getElementById(m.anchor);
    if (!el) return;
    el.scrollIntoView({ behavior: 'instant', block: 'start' });
    var nav = window.__stxMarkerNavigateTo;
    if (typeof nav === 'function' && m.index >= 0) nav(m.index);
  }
  /* Initial load: the query wins, then the hash. Later hash changes (a
     click on a sidebar #anchor link) resolve the hash ONLY -- the query
     is a landing instruction, not a permanent override.                */
  function initial() { goTo(fromQuery() || fromHash()); }
  initial();
  window.addEventListener('load', initial);
  window.addEventListener('hashchange', function() { goTo(fromHash()); });
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

_SIDEBAR_RESIZE_JS = """
(function() {
  var sidebar = document.getElementById('stx-sidebar');
  if (!sidebar) return;
  var handle = sidebar.querySelector('.stx-sidebar-resize-handle');
  if (!handle) return;
  var root = document.documentElement;
  var body = document.body;
  var MIN = 180;
  var MAX_FRAC = 0.5;
  var DEFAULT = 280;
  var STORAGE_KEY = 'stx-sidebar-width';

  function maxAllowed() {
    return Math.max(MIN, Math.floor(window.innerWidth * MAX_FRAC));
  }
  function clamp(px) {
    return Math.max(MIN, Math.min(px, maxAllowed()));
  }
  function setWidth(px, persist) {
    root.style.setProperty('--stx-sidebar-width', px + 'px');
    if (persist) {
      try { localStorage.setItem(STORAGE_KEY, String(px)); } catch (e) {}
    }
  }
  function currentWidth() {
    var v = parseInt(getComputedStyle(root).getPropertyValue('--stx-sidebar-width'), 10);
    return isNaN(v) ? DEFAULT : v;
  }

  // Restore persisted width on load (desktop only).
  try {
    var saved = parseInt(localStorage.getItem(STORAGE_KEY), 10);
    if (saved && window.innerWidth > 768) setWidth(clamp(saved), false);
  } catch (e) {}

  // --- Drag-to-resize ---------------------------------------------------
  var dragging = false;
  handle.addEventListener('pointerdown', function(e) {
    if (window.innerWidth <= 768) return;  // disabled on mobile
    dragging = true;
    body.classList.add('stx-sidebar-resizing');
    try { handle.setPointerCapture(e.pointerId); } catch (err) {}
    e.preventDefault();
  });
  handle.addEventListener('pointermove', function(e) {
    if (!dragging) return;
    setWidth(clamp(e.clientX), false);
  });
  function endDrag(e) {
    if (!dragging) return;
    dragging = false;
    body.classList.remove('stx-sidebar-resizing');
    try { handle.releasePointerCapture(e.pointerId); } catch (err) {}
    // Persist the final width once, not on every pointermove.
    try { localStorage.setItem(STORAGE_KEY, String(currentWidth())); } catch (err) {}
  }
  handle.addEventListener('pointerup', endDrag);
  handle.addEventListener('pointercancel', endDrag);

  // --- Double-click resets to the default (P4) -------------------------
  handle.addEventListener('dblclick', function() {
    setWidth(DEFAULT, true);
  });

  // --- Keyboard accessibility ------------------------------------------
  handle.addEventListener('keydown', function(e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var step = e.shiftKey ? 50 : 10;
    var delta = e.key === 'ArrowRight' ? step : -step;
    setWidth(clamp(currentWidth() + delta), true);
    e.preventDefault();
  });
})();
"""


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

def _build_theme_vars_css() -> str:
    """Emit a ``:root`` block of theme-derived CSS custom properties.

    Reads the project's theme via :func:`streamtex.export._get_theme_color`
    (which consults ``.streamlit/config.toml`` and falls back to Streamlit
    1.56's resolved dark defaults when ``base = "dark"`` is set without
    per-key overrides — including the values ``#1C1E1F`` for the sidebar
    background and ``#43A9FB`` for links that Streamlit's frontend
    computes at runtime).

    The variables emitted here are consumed by ``_SIDEBAR_CSS`` and feed
    every theme-sensitive value in the static sidebar.  Without this
    block the var() lookups resolve to the light-mode literal fallbacks.
    """
    sidebar_bg = _get_theme_color("theme.secondaryBackgroundColor", "#f8f9fa")
    sidebar_fg = _get_theme_color("theme.textColor", "#333333")
    link_color = _get_theme_color("theme.linkColor", "#1155cc")
    return (
        ":root {\n"
        f"  --stx-export-sidebar-bg: {sidebar_bg};\n"
        f"  --stx-export-sidebar-fg: {sidebar_fg};\n"
        f"  --stx-export-link: {link_color};\n"
        "}\n"
    )


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
        # Emit the :root theme variables BEFORE the sidebar CSS so the
        # var() lookups resolve to the project's theme (read from
        # .streamlit/config.toml with Streamlit 1.56 dark/light defaults
        # as fallback).  Without this block, the sidebar falls back to
        # the light-mode literal values baked into _SIDEBAR_CSS — still
        # readable, but not theme-aligned.
        extra_css += _build_theme_vars_css()
        extra_css += _SIDEBAR_CSS
        extra_js_parts.append(_SIDEBAR_TOGGLE_JS)
        # Resize handle JS — runs only when the sidebar is present.
        extra_js_parts.append(_SIDEBAR_RESIZE_JS)
        # Cross-context scroll-spy (same script the live runtime uses
        # via marker_runtime).  Drives `.stx-nav-active` on the entry
        # closest to the viewport top or the one the user just clicked.
        if _SCROLL_SPY_JS:
            extra_js_parts.append(_SCROLL_SPY_JS)

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
    if has_markers or has_toc:
        _toc_pages = [
            {"key_anchor": e.get("key_anchor"), "page_idx": e.get("page_idx", 0)}
            for e in (toc or []) if e.get("key_anchor")
        ]
        extra_js_parts.append(_DEEPLINK_JS
            .replace("__MARKERS__", json.dumps(markers or [], ensure_ascii=False))
            .replace("__TOC__", json.dumps(_toc_pages, ensure_ascii=False)))

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
