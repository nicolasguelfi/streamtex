"""Marker Navigation System — opt-in slide-like navigation for StreamTeX books."""

import json
import streamlit as st
import streamlit.components.v1 as components
from dataclasses import dataclass, field
from typing import Optional
from .export import _render
from .toc import TOCRegistry


@dataclass
class MarkerConfig:
    """Configuration for the marker navigation system.

    Pass an instance to ``st_book(marker_config=...)`` to enable
    marker-based navigation with a floating widget and keyboard shortcuts.
    """

    show_nav_ui: bool = True
    """Show the floating navigation widget (counter, prev/next buttons, popup list)."""

    auto_marker_on_toc: int | bool = False
    """Bridge TOC headings to markers automatically.
    True = all levels, int N = up to level N, False = disabled."""

    nav_position: str = "bottom-right"
    """Widget position: ``"bottom-right"`` or ``"bottom-center"``."""

    nav_label_chars: int = 40
    """Max characters for the current marker label in the widget. 0 = hidden."""

    popup_open: bool = False
    """Initial state of the marker popup list (open or closed)."""

    next_keys: list[str] = field(default_factory=lambda: ["PageDown"])
    """Keys to navigate to the next marker (JS KeyboardEvent.key values).
    Supports modifier syntax: ``"Ctrl+ArrowRight"``."""

    prev_keys: list[str] = field(default_factory=lambda: ["PageUp"])
    """Keys to navigate to the previous marker.
    Supports modifier syntax: ``"Ctrl+ArrowLeft"``."""


class MarkerRegistry:
    """Registry that collects markers during a book render pass."""

    def __init__(self, config: MarkerConfig):
        self.config = config
        self._entries: list[dict] = []

    def reset(self) -> None:
        self._entries = []

    def register(self, label: str, anchor: str) -> int:
        idx = len(self._entries)
        self._entries.append({"index": idx, "label": label, "anchor": anchor})
        return idx

    def get_entries(self) -> list[dict]:
        return list(self._entries)

    def count(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Global singleton (same pattern as toc.py)
# ---------------------------------------------------------------------------

_registry: Optional[MarkerRegistry] = None


def reset_marker_registry(config: MarkerConfig = None) -> None:
    """Initialise or reset the global marker registry."""
    global _registry
    if _registry is not None:
        _registry.reset()
        if config is not None:
            _registry.config = config
    elif config is not None:
        _registry = MarkerRegistry(config)


def register_marker(label: str, anchor: str) -> int:
    """Register a marker in the global registry. Requires prior init."""
    global _registry
    assert isinstance(_registry, MarkerRegistry), (
        "Marker registry is not initialized. Call reset_marker_registry first."
    )
    return _registry.register(label, anchor)


def marker_entries() -> list[dict]:
    """Return registered markers, or [] if the registry is not initialized."""
    global _registry
    if _registry is None:
        return []
    return _registry.get_entries()


def marker_count() -> int:
    """Return marker count, or 0 if the registry is not initialized."""
    global _registry
    if _registry is None:
        return 0
    return _registry.count()


def get_marker_config() -> Optional[MarkerConfig]:
    """Return the current config, or None if markers are not active."""
    global _registry
    if _registry is None:
        return None
    return _registry.config


# ---------------------------------------------------------------------------
# Public API — st_marker()
# ---------------------------------------------------------------------------

def st_marker(label: str = "", visible: bool = False) -> None:
    """Place a navigation marker in the content.

    No-op if the marker registry has not been initialized (backward compat).
    """
    if _registry is None:
        return

    idx = _registry.count()

    if not label:
        label = f"Marker {idx + 1}"

    # Deterministic anchor so cache-build and live-render produce the same ID
    slug = TOCRegistry.get_key_anchor(label)
    anchor = f"stx-marker-{slug}-{idx}"

    _registry.register(label, anchor)

    if visible:
        style = (
            "border-top: 1px dashed rgba(128,128,128,0.4); "
            "font-size: 10px; color: rgba(128,128,128,0.6); "
            "padding: 2px 6px; scroll-margin-top: 80px;"
        )
        html = f'<div id="{anchor}" class="streamtex-marker" data-marker-index="{idx}" style="{style}">{label}</div>'
    else:
        style = "height: 0; overflow: hidden; scroll-margin-top: 80px;"
        html = f'<div id="{anchor}" class="streamtex-marker" data-marker-index="{idx}" style="{style}"></div>'

    _render(html)


# ---------------------------------------------------------------------------
# JS / CSS injection — called once after all blocks are rendered
# ---------------------------------------------------------------------------

def inject_marker_navigation() -> None:
    """Inject the floating nav widget and keyboard/scroll JS.

    Uses components.html() to create a real iframe where scripts execute
    (st.html() strips <script> tags in Streamlit 1.54+).
    From the iframe we access parent.document (same pattern as zoom.py).
    """
    entries = marker_entries()
    if not entries:
        return

    config = get_marker_config()
    if config is None:
        return

    pos_css = {
        "bottom-right": "bottom: 24px; right: 24px;",
        "bottom-center": "bottom: 24px; left: 50%; transform: translateX(-50%);",
    }.get(config.nav_position, "bottom: 24px; right: 24px;")

    show_ui = "block" if config.show_nav_ui else "none"
    scroll_offset = 80

    js_body = """
(function() {
    var hostDoc = parent.document;
    var hostWin = hostDoc.defaultView || parent;

    var markers = __MARKERS__;
    var nextKeys = __NEXT_KEYS__;
    var prevKeys = __PREV_KEYS__;
    var OFFSET = __OFFSET__;
    var currentIdx = 0;
    var popupOpen = __POPUP_OPEN__;

    if (!markers.length) return;

    /* --- Cleanup previous run --- */
    if (hostWin._stxMarkerCleanup) {
        try { hostWin._stxMarkerCleanup(); } catch(e) {}
    }

    /* --- Key matching --- */
    function matchesKey(e, keyDefs) {
        for (var i = 0; i < keyDefs.length; i++) {
            var parts = keyDefs[i].split('+');
            if (parts.length === 2) {
                var mod = parts[0].toLowerCase();
                var key = parts[1];
                var modOk = (mod === 'ctrl'  && e.ctrlKey)  ||
                            (mod === 'shift' && e.shiftKey) ||
                            (mod === 'alt'   && e.altKey)   ||
                            (mod === 'meta'  && e.metaKey);
                if (modOk && e.key === key) return true;
            } else {
                if (e.key === keyDefs[i]) return true;
            }
        }
        return false;
    }

    /* --- Find marker element --- */
    function findMarkerElement(anchor) {
        var el = hostDoc.getElementById(anchor);
        if (el) return el;
        var iframes = hostDoc.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) {
            try {
                var idoc = iframes[i].contentDocument;
                if (idoc && idoc.getElementById(anchor)) return iframes[i];
            } catch(e) {}
        }
        return null;
    }

    /* --- Scroll --- */
    function scrollToTarget(target) {
        var sc = hostDoc.querySelector('.stMain');
        if (sc && sc.scrollHeight > sc.clientHeight) {
            var cRect = sc.getBoundingClientRect();
            var tRect = target.getBoundingClientRect();
            sc.scrollTo({ top: sc.scrollTop + tRect.top - cRect.top - OFFSET,
                          behavior: 'smooth' });
        } else {
            var rect = target.getBoundingClientRect();
            hostWin.scrollTo({
                top: (hostWin.pageYOffset || hostDoc.documentElement.scrollTop)
                     + rect.top - OFFSET,
                behavior: 'smooth' });
        }
    }

    function scrollToMarker(anchor) {
        var target = findMarkerElement(anchor);
        if (target) scrollToTarget(target);
    }

    function navigateTo(idx) {
        if (idx < 0) {
            if (hostWin._stxMarkerBoundary) { hostWin._stxMarkerBoundary('prev'); return; }
            idx = 0;
        }
        if (idx >= markers.length) {
            if (hostWin._stxMarkerBoundary) { hostWin._stxMarkerBoundary('next'); return; }
            idx = markers.length - 1;
        }
        currentIdx = idx;
        var m = markers[idx];
        var target = findMarkerElement(m.anchor);
        if (target) {
            scrollToTarget(target);
        } else if (m.page !== undefined && hostWin._stxMarkerGoToPage) {
            hostWin._stxMarkerStartIdx = idx;
            hostWin._stxMarkerGoToPage(m.page);
        }
        updateUI();
    }

    /* ================================================================
       NAV WIDGET — fixed-width counter + popup marker list
       ================================================================ */
    var nav = hostDoc.getElementById('streamtex-marker-nav');
    if (nav) nav.remove();

    nav = hostDoc.createElement('div');
    nav.id = 'streamtex-marker-nav';
    nav.style.cssText = 'position:fixed;__POS_CSS__display:__SHOW_UI__;z-index:999998;font-family:sans-serif;user-select:none;';
    hostDoc.body.appendChild(nav);

    /* --- Controls bar --- */
    var bar = hostDoc.createElement('div');
    bar.style.cssText = 'display:flex;align-items:center;gap:8px;background:rgba(40,40,40,.85);color:#eee;border-radius:24px;padding:6px 14px;font-size:13px;backdrop-filter:blur(6px);box-shadow:0 2px 10px rgba(0,0,0,.3);';
    nav.appendChild(bar);

    var btnStyle = 'background:none;border:none;color:inherit;font-size:16px;cursor:pointer;padding:2px 6px;border-radius:4px;line-height:1;';
    var btnHover = 'rgba(128,128,128,.25)';

    var btnPrev = hostDoc.createElement('button');
    btnPrev.textContent = '\\u25C0';
    btnPrev.style.cssText = btnStyle;
    btnPrev.onmouseenter = function() { this.style.background = btnHover; };
    btnPrev.onmouseleave = function() { this.style.background = 'none'; };
    btnPrev.onclick = function() { navigateTo(currentIdx - 1); };

    /* Fixed-width counter */
    var totalDigits = String(markers.length).length;
    var counterWidth = (totalDigits * 2 + 3) + 'ch';
    var counter = hostDoc.createElement('span');
    counter.style.cssText = 'min-width:' + counterWidth + ';text-align:center;display:inline-block;font-variant-numeric:tabular-nums;';

    var btnNext = hostDoc.createElement('button');
    btnNext.textContent = '\\u25B6';
    btnNext.style.cssText = btnStyle;
    btnNext.onmouseenter = function() { this.style.background = btnHover; };
    btnNext.onmouseleave = function() { this.style.background = 'none'; };
    btnNext.onclick = function() { navigateTo(currentIdx + 1); };

    var btnList = hostDoc.createElement('button');
    btnList.textContent = '\\u2630';
    btnList.style.cssText = btnStyle + 'font-size:14px;';
    btnList.onmouseenter = function() { this.style.background = btnHover; };
    btnList.onmouseleave = function() { this.style.background = 'none'; };
    btnList.onclick = function(e) { e.stopPropagation(); togglePopup(); };

    var labelChars = __LABEL_CHARS__;
    var label = hostDoc.createElement('span');
    label.style.cssText = 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;opacity:.8;' +
        (labelChars > 0 ? 'width:' + labelChars + 'ch;display:inline-block;' : 'display:none;');

    bar.appendChild(btnPrev);
    bar.appendChild(counter);
    bar.appendChild(btnNext);
    bar.appendChild(btnList);
    bar.appendChild(label);

    /* --- Popup marker list --- */
    var popup = hostDoc.createElement('div');
    popup.style.cssText = 'display:none;position:absolute;bottom:calc(100% + 8px);right:0;background:rgba(30,30,30,.95);color:#eee;border-radius:12px;padding:6px 0;min-width:240px;max-width:350px;max-height:400px;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.5);backdrop-filter:blur(8px);font-size:12px;';

    for (var mi = 0; mi < markers.length; mi++) {
        var row = hostDoc.createElement('div');
        row.className = 'stx-popup-item';
        row.dataset.idx = mi;
        row.style.cssText = 'padding:7px 16px;cursor:pointer;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-left:3px solid transparent;transition:background .1s;';
        row.textContent = (mi + 1) + '. ' + markers[mi].label;
        row.onmouseenter = function() { this.style.background = 'rgba(128,128,128,.25)'; };
        row.onmouseleave = function() {
            if (parseInt(this.dataset.idx) !== currentIdx) this.style.background = 'transparent';
            else this.style.background = 'rgba(128,128,128,.2)';
        };
        (function(idx) {
            row.onclick = function() { navigateTo(idx); togglePopup(false); };
        })(mi);
        popup.appendChild(row);
    }
    nav.appendChild(popup);

    function togglePopup(show) {
        popupOpen = typeof show === 'boolean' ? show : !popupOpen;
        popup.style.display = popupOpen ? 'block' : 'none';
        hostWin._stxMarkerPopupState = popupOpen;
        if (popupOpen) highlightPopup();
    }

    function highlightPopup() {
        var items = popup.querySelectorAll('.stx-popup-item');
        for (var j = 0; j < items.length; j++) {
            var isActive = j === currentIdx;
            items[j].style.background = isActive ? 'rgba(128,128,128,.2)' : 'transparent';
            items[j].style.borderLeftColor = isActive ? '#4a9eff' : 'transparent';
            items[j].style.fontWeight = isActive ? '600' : 'normal';
        }
        if (items[currentIdx]) items[currentIdx].scrollIntoView({ block: 'nearest' });
    }

    /* Close popup on outside click */
    function outsideClick(e) {
        if (popupOpen && !nav.contains(e.target)) togglePopup(false);
    }
    hostDoc.addEventListener('click', outsideClick);

    /* --- Update UI --- */
    function updateUI() {
        var m = markers[currentIdx];
        var padded = String(currentIdx + 1).padStart(totalDigits, '\\u2007');
        counter.textContent = padded + ' / ' + markers.length;
        label.textContent = m ? m.label : '';
        if (popupOpen) highlightPopup();
    }

    /* --- Keyboard handler --- */
    function keyHandler(e) {
        var tag = (e.target.tagName || '').toUpperCase();
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT'
            || e.target.isContentEditable) return;
        if (e.key === 'Escape' && popupOpen) {
            e.preventDefault(); togglePopup(false); return false;
        }
        if (matchesKey(e, nextKeys)) {
            e.preventDefault(); e.stopPropagation();
            navigateTo(currentIdx + 1); return false;
        } else if (matchesKey(e, prevKeys)) {
            e.preventDefault(); e.stopPropagation();
            navigateTo(currentIdx - 1); return false;
        }
    }

    hostDoc.addEventListener('keydown', keyHandler, true);

    /* --- Propagate into iframes --- */
    var attachedFrames = new WeakSet();
    function attachToIframe(iframe) {
        if (attachedFrames.has(iframe)) return;
        attachedFrames.add(iframe);
        function tryAttach() {
            try {
                var doc = iframe.contentDocument;
                if (doc) doc.addEventListener('keydown', keyHandler, true);
            } catch(e) {}
        }
        tryAttach();
        iframe.addEventListener('load', tryAttach);
    }
    function scanIframes() {
        var iframes = hostDoc.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) attachToIframe(iframes[i]);
    }
    scanIframes();
    var obs = new MutationObserver(scanIframes);
    obs.observe(hostDoc.body, { childList: true, subtree: true });
    var scanInterval = setInterval(scanIframes, 2000);

    /* --- Scroll tracker --- */
    var scrollTimer = null;
    function scrollHandler() {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(function() {
            var best = -1, bestDist = Infinity;
            for (var i = 0; i < markers.length; i++) {
                var t = findMarkerElement(markers[i].anchor);
                if (!t) continue;
                var d = Math.abs(t.getBoundingClientRect().top - OFFSET);
                if (d < bestDist) { bestDist = d; best = i; }
            }
            /* Only update if at least one marker was found in the DOM.
               When no markers are found (iframes still loading after a
               page navigation), keep the current index unchanged to
               avoid resetting to a wrong default.                     */
            if (best >= 0 && best !== currentIdx) {
                currentIdx = best; updateUI();
            }
        }, 150);
    }
    var scrollTarget = hostDoc.querySelector('.stMain') || hostWin;
    scrollTarget.addEventListener('scroll', scrollHandler);

    /* --- Cleanup --- */
    hostWin._stxMarkerCleanup = function() {
        hostDoc.removeEventListener('keydown', keyHandler, true);
        hostDoc.removeEventListener('click', outsideClick);
        obs.disconnect();
        clearInterval(scanInterval);
        clearTimeout(scrollTimer);
        clearTimeout(initTimer);
        scrollTarget.removeEventListener('scroll', scrollHandler);
        var el = hostDoc.getElementById('streamtex-marker-nav');
        if (el) el.remove();
    };

    /* --- Init --- */
    var initTimer = setTimeout(function() {
        var startIdx = hostWin._stxMarkerStartIdx || 0;
        if (startIdx < 0) startIdx = markers.length + startIdx;
        startIdx = Math.max(0, Math.min(startIdx, markers.length - 1));
        currentIdx = startIdx;
        hostWin._stxMarkerStartIdx = 0;
        /* Restore popup state from previous run if available */
        if (hostWin._stxMarkerPopupState !== undefined) {
            popupOpen = hostWin._stxMarkerPopupState;
        }
        updateUI(); scanIframes();
        if (popupOpen) { popup.style.display = 'block'; highlightPopup(); }
    }, 500);
})();
"""

    # Replace placeholders
    js_body = (js_body
        .replace('__MARKERS__', json.dumps(entries))
        .replace('__NEXT_KEYS__', json.dumps(config.next_keys))
        .replace('__PREV_KEYS__', json.dumps(config.prev_keys))
        .replace('__OFFSET__', str(scroll_offset))
        .replace('__LABEL_CHARS__', str(config.nav_label_chars))
        .replace('__POPUP_OPEN__', 'true' if config.popup_open else 'false')
        .replace('__POS_CSS__', pos_css)
        .replace('__SHOW_UI__', show_ui))

    # components.html() creates a real iframe where scripts execute
    # (st.html() strips <script> tags in Streamlit 1.54+)
    components.html(f"<script>{js_body}</script>", height=0)
