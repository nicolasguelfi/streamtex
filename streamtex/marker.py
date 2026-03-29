"""Marker Navigation System — opt-in slide-like navigation for StreamTeX books."""

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import streamlit.components.v1 as components

from .constants import LINK_ACTIVE_COLOR_DARK, STX_CORAL, STX_HOME_URL
from .export import _render
from .toc import TOCRegistry

# ---------------------------------------------------------------------------
# Tiny logo for the floating nav bar (base64-encoded at import time)
# ---------------------------------------------------------------------------
_LOGO_TINY_PATH = Path(__file__).parent / "static" / "logo-stx-tiny.png"
_LOGO_B64: str = ""
if _LOGO_TINY_PATH.exists():
    _LOGO_B64 = base64.b64encode(_LOGO_TINY_PATH.read_bytes()).decode()


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

    draggable: bool = True
    """Allow the floating nav widget to be dragged anywhere on screen (mouse + touch)."""

    collapsible: bool = True
    """Show a ⋮ button to collapse/expand the nav widget.
    When collapsed, a drag grip handle replaces the hidden elements."""


class MarkerRegistry:
    """Registry that collects markers during a book render pass."""

    def __init__(self, config: MarkerConfig):
        self.config = config
        self._entries: list[dict] = []

    def reset(self) -> None:
        self._entries = []

    def register(self, label: str, anchor: str, hidden: bool = False) -> int:
        idx = len(self._entries)
        self._entries.append({"index": idx, "label": label, "anchor": anchor, "hidden": hidden})
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


def register_marker(label: str, anchor: str, hidden: bool = False) -> int:
    """Register a marker in the global registry. Requires prior init."""
    global _registry
    assert isinstance(_registry, MarkerRegistry), (
        "Marker registry is not initialized. Call reset_marker_registry first."
    )
    return _registry.register(label, anchor, hidden=hidden)


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

def st_marker(label: str = "", visible: bool = False, hidden: bool = False) -> None:
    """Place a navigation marker in the content.

    No-op if the marker registry has not been initialized (backward compat).

    Args:
        label: Marker label shown in the sidebar list and nav widget.
        visible: If True, render a visible dashed line in the content.
        hidden: If True, the marker works for PageUp/PageDown navigation
                but does not appear in the sidebar list or nav widget.
    """
    if _registry is None:
        return

    idx = _registry.count()

    if not label:
        label = f"Marker {idx + 1}"

    # Deterministic anchor so cache-build and live-render produce the same ID
    slug = TOCRegistry.get_key_anchor(label)
    anchor = f"stx-marker-{slug}-{idx}"

    _registry.register(label, anchor, hidden=hidden)

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

def inject_marker_navigation(
    *,
    profile_names: list[str] | None = None,
    active_profile: str | None = None,
    profile_modified: bool = False,
) -> None:
    """Inject the floating nav widget and keyboard/scroll JS.

    Uses components.html() to create a real iframe where scripts execute
    (st.html() strips <script> tags in Streamlit 1.54+).
    From the iframe we access parent.document (same pattern as zoom.py).

    :param profile_names: List of profile names for the profile popup.
    :param active_profile: Currently active profile name.
    :param profile_modified: Whether the active profile has been modified.
    """
    entries = marker_entries()
    if not entries:
        return

    config = get_marker_config()
    if config is None:
        return

    pos_css = {
        "bottom-right": "bottom: calc(24px + env(safe-area-inset-bottom, 0px)); right: 24px;",
        "bottom-center": "bottom: calc(24px + env(safe-area-inset-bottom, 0px)); left: 50%; transform: translateX(-50%);",
    }.get(config.nav_position, "bottom: calc(24px + env(safe-area-inset-bottom, 0px)); right: 24px;")

    show_ui = "block" if config.show_nav_ui else "none"
    scroll_offset = 80
    logo_b64 = _LOGO_B64

    js_body = """
(function() {
    var hostDoc = parent.document;
    var hostWin = hostDoc.defaultView || parent;

    var markers = __MARKERS__;
    var visibleMarkers = markers.filter(function(m) { return !m.hidden; });
    var nextKeys = __NEXT_KEYS__;
    var prevKeys = __PREV_KEYS__;
    var OFFSET = __OFFSET__;
    var currentIdx = 0;
    var _navigating = false;
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
        _navigating = true;
        var m = markers[idx];
        var target = findMarkerElement(m.anchor);
        if (target) {
            scrollToTarget(target);
            setTimeout(function() { _navigating = false; }, 300);
        } else if (m.page !== undefined && hostWin._stxMarkerGoToPage) {
            hostWin._stxMarkerStartIdx = idx;
            hostWin._stxMarkerGoToPage(m.page);
            _navigating = false;
        } else {
            _navigating = false;
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
    nav.style.cssText = 'position:fixed;__POS_CSS__display:__SHOW_UI__;z-index:999998;font-family:sans-serif;user-select:none;max-width:calc(100vw - 16px);';
    hostDoc.body.appendChild(nav);

    /* --- Responsive style for narrow viewports --- */
    var mobileStyle = hostDoc.getElementById('stx-marker-responsive');
    if (mobileStyle) mobileStyle.remove();
    mobileStyle = hostDoc.createElement('style');
    mobileStyle.id = 'stx-marker-responsive';
    mobileStyle.textContent =
    /* Tablet breakpoint */
    '@media (max-width: 800px) { ' +
        '#streamtex-marker-nav .stx-marker-bar { border-radius: 16px; } ' +
        '#streamtex-marker-nav .stx-marker-label { max-width: 20ch !important; flex-shrink: 1; } ' +
    '} ' +
    /* Mobile breakpoint — force 2-line layout */
    '@media (max-width: 600px) { ' +
        '#streamtex-marker-nav .stx-marker-break { display:block !important; width:100% !important; height:0 !important; } ' +
        '#streamtex-marker-nav .stx-marker-bar { gap: 4px; padding: 6px 10px; justify-content: center; } ' +
        '#streamtex-marker-nav .stx-marker-label { max-width: 14ch !important; flex-shrink: 1; } ' +
    '} ' +
    /* Hide number input spinners */
    '#streamtex-marker-nav input[type=number]::-webkit-outer-spin-button, ' +
    '#streamtex-marker-nav input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; } ';
    hostDoc.head.appendChild(mobileStyle);

    /* --- Controls bar --- */
    var bar = hostDoc.createElement('div');
    bar.className = 'stx-marker-bar';
    bar.style.cssText = 'display:flex;align-items:center;gap:8px;background:rgba(40,40,40,.85);color:#eee;border-radius:24px;padding:6px 14px;font-size:13px;backdrop-filter:blur(6px);box-shadow:0 2px 10px rgba(0,0,0,.3);flex-wrap:wrap;max-width:100%;box-sizing:border-box;';
    nav.appendChild(bar);

    var btnStyle = 'background:none;border:none;color:inherit;font-size:16px;cursor:pointer;padding:2px 6px;border-radius:4px;line-height:1;';
    var btnHover = 'rgba(128,128,128,.25)';

    var btnPrev = hostDoc.createElement('button');
    btnPrev.textContent = '\\u25C0';
    btnPrev.style.cssText = btnStyle;
    btnPrev.onmouseenter = function() { this.style.background = btnHover; };
    btnPrev.onmouseleave = function() { this.style.background = 'none'; };
    btnPrev.onclick = function() { navigateTo(currentIdx - 1); };

    /* Fixed-width counter (global marker index) — click to jump */
    var totalDigits = String(markers.length).length;
    var counterWidth = (totalDigits * 2 + 3) + 'ch';
    var counter = hostDoc.createElement('span');
    counter.style.cssText = 'min-width:' + counterWidth + ';text-align:center;display:inline-block;font-variant-numeric:tabular-nums;cursor:pointer;';
    counter.title = 'Click to jump to a marker number';

    var counterInput = hostDoc.createElement('input');
    counterInput.type = 'number';
    counterInput.min = '1';
    counterInput.max = String(markers.length);
    counterInput.style.cssText = 'width:' + counterWidth + ';text-align:center;background:rgba(255,255,255,.15);color:#eee;border:1px solid rgba(255,255,255,.3);border-radius:4px;font-size:13px;font-variant-numeric:tabular-nums;outline:none;display:none;-moz-appearance:textfield;';
    var counterEditing = false;

    function showCounterInput() {
        counterEditing = true;
        counterInput.value = String(currentIdx + 1);
        counter.style.display = 'none';
        counterInput.style.display = 'inline-block';
        counterInput.focus();
        counterInput.select();
    }
    function hideCounterInput() {
        counterEditing = false;
        counterInput.style.display = 'none';
        counter.style.display = 'inline-block';
    }
    function commitCounterInput() {
        var n = parseInt(counterInput.value, 10);
        if (n >= 1 && n <= markers.length) {
            navigateTo(n - 1);
        }
        hideCounterInput();
    }
    counter.onclick = function(e) { e.stopPropagation(); showCounterInput(); };
    counterInput.onkeydown = function(e) {
        e.stopPropagation();
        if (e.key === 'Enter') { e.preventDefault(); commitCounterInput(); }
        if (e.key === 'Escape') { e.preventDefault(); hideCounterInput(); }
    };
    counterInput.onblur = function() { hideCounterInput(); };

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
    label.className = 'stx-marker-label';
    label.style.cssText = 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;opacity:.8;' +
        (labelChars > 0 ? 'width:' + labelChars + 'ch;display:inline-block;' : 'display:none;');

    /* --- Profile data + phone icon popup --- */
    var profileNames = __PROFILE_NAMES__;
    var activeProfileName = __ACTIVE_PROFILE__;
    var profileModified = __PROFILE_MODIFIED__;

    var profileBtn = hostDoc.createElement('button');
    profileBtn.className = 'stx-nav-btn stx-profile-menu-btn';
    profileBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" ' +
        'fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round">' +
        '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>' +
        '<line x1="12" y1="18" x2="12.01" y2="18"/></svg>';
    profileBtn.title = 'Display profiles';
    profileBtn.style.cssText = btnStyle + 'display:flex;align-items:center;font-size:14px;';
    profileBtn.onmouseenter = function() { this.style.background = btnHover; };
    profileBtn.onmouseleave = function() { this.style.background = 'none'; };

    var profilePopup = hostDoc.createElement('div');
    profilePopup.className = 'stx-profile-popup';
    profilePopup.style.cssText = 'display:none;position:absolute;bottom:calc(100% + 8px);left:0;background:rgba(30,30,30,.95);backdrop-filter:blur(6px);border-radius:8px;padding:6px 0;min-width:150px;box-shadow:0 4px 20px rgba(0,0,0,.4);z-index:999999;';

    profileNames.forEach(function(name) {
        var isActive = (name === activeProfileName);
        var dispLabel = (isActive && profileModified) ? name + ' *' : name;
        var item = hostDoc.createElement('div');
        item.textContent = dispLabel;
        item.style.cssText = 'padding:7px 16px;cursor:pointer;font-size:13px;color:#e0e0e0;transition:background .15s;white-space:nowrap;' +
            (isActive
                ? 'border-left:3px solid #4fc3f7;background:rgba(79,195,247,.15);font-weight:600;'
                : 'border-left:3px solid transparent;');
        item.onmouseenter = function() {
            if (!isActive) this.style.background = 'rgba(255,255,255,.08)';
        };
        item.onmouseleave = function() {
            this.style.background = isActive ? 'rgba(79,195,247,.15)' : 'transparent';
        };
        (function(pName) {
            item.onclick = function() {
                profilePopup.style.display = 'none';
                profilePopupOpen = false;
                /* Find and click the hidden stx_prof_ button in sidebar.
                   The button's on_click sets _stx_profile_pending, triggering
                   a Streamlit-native rerun. */
                var allBtns = hostDoc.querySelectorAll(
                    '[data-testid="stBaseButton-secondary"]'
                );
                for (var bi = 0; bi < allBtns.length; bi++) {
                    var txt = (allBtns[bi].textContent || '').trim();
                    if (txt === 'stx_prof_' + pName) {
                        allBtns[bi].click();
                        return;
                    }
                }
            };
        })(name);
        profilePopup.appendChild(item);
    });

    var profilePopupOpen = false;
    profileBtn.onclick = function(e) {
        e.stopPropagation();
        profilePopupOpen = !profilePopupOpen;
        profilePopup.style.display = profilePopupOpen ? 'block' : 'none';
    };
    hostDoc.addEventListener('click', function(e) {
        if (profilePopupOpen && !profileBtn.contains(e.target) && !profilePopup.contains(e.target)) {
            profilePopupOpen = false;
            profilePopup.style.display = 'none';
        }
    });

    bar.appendChild(profileBtn);
    nav.appendChild(profilePopup);

    bar.appendChild(btnPrev);
    bar.appendChild(counter);
    bar.appendChild(counterInput);
    bar.appendChild(btnNext);
    bar.appendChild(btnList);

    /* Flex line-break element — hidden on desktop, forces 2nd row on mobile */
    var flexBreak = hostDoc.createElement('span');
    flexBreak.className = 'stx-marker-break';
    flexBreak.style.cssText = 'display:none;width:0;height:0;';
    bar.appendChild(flexBreak);

    bar.appendChild(label);

    /* --- Collapsible ⋮ button --- */
    var collapsible = __COLLAPSIBLE__;
    var collapsed = false;
    var btnCollapse = null;
    var barChildren = [];  /* elements to hide/show on collapse */
    var gripHandle = null;

    if (collapsible) {
        /* Restore collapsed state from localStorage */
        try { collapsed = localStorage.getItem('stx-marker-collapsed') === '1'; } catch(e) {}

        btnCollapse = hostDoc.createElement('button');
        btnCollapse.textContent = '\\u22EE';  /* ⋮ */
        btnCollapse.title = 'Collapse / expand navigation bar';
        btnCollapse.style.cssText = btnStyle + 'font-size:16px;font-weight:bold;letter-spacing:0;';
        btnCollapse.onmouseenter = function() { this.style.background = btnHover; };
        btnCollapse.onmouseleave = function() { this.style.background = 'none'; };

        /* Collect all bar children BEFORE adding collapse button */
        for (var ci = 0; ci < bar.childNodes.length; ci++) {
            barChildren.push(bar.childNodes[ci]);
        }

        bar.appendChild(btnCollapse);

        function applyCollapsed() {
            var disp = collapsed ? 'none' : '';
            for (var ci = 0; ci < barChildren.length; ci++) {
                barChildren[ci].style.display = disp;
                /* restore inline-block for counter when expanding */
                if (!collapsed && barChildren[ci] === counter) barChildren[ci].style.display = 'inline-block';
                if (!collapsed && barChildren[ci] === counterInput) barChildren[ci].style.display = 'none';
            }
            /* Grip handle: visible only when collapsed */
            if (gripHandle) gripHandle.style.display = collapsed ? 'inline-block' : 'none';
            bar.style.padding = collapsed ? '6px 8px' : '6px 14px';
            bar.style.borderRadius = collapsed ? '12px' : '24px';
            if (collapsed && popupOpen) togglePopup(false);
            try { localStorage.setItem('stx-marker-collapsed', collapsed ? '1' : '0'); } catch(e) {}
        }

        btnCollapse.onclick = function(e) {
            e.stopPropagation();
            collapsed = !collapsed;
            applyCollapsed();
            /* Re-clamp after size change (clampNav defined in Draggable block) */
            if (typeof clampNav === 'function') clampNav();
        };

        applyCollapsed();
    }

    /* --- Draggable (mouse + touch) --- */
    var draggable = __DRAGGABLE__;
    if (draggable) {
        nav.style.cursor = 'grab';
        nav.style.touchAction = 'none';  /* prevent browser scroll/zoom during drag */
        var _dragStartX, _dragStartY, _dragNavX, _dragNavY, _dragging = false;
        var _stxPopup = null;  /* set later when popup is created */

        /* Filter: only drag from non-interactive elements, never from popup */
        function isDragTarget(el) {
            var tag = el.tagName;
            if (tag === 'BUTTON' || tag === 'A' || tag === 'INPUT' || tag === 'IMG') return false;
            var node = el;
            while (node && node !== nav) {
                if (node === _stxPopup) return false;
                node = node.parentNode;
            }
            return true;
        }

        /* Clamp nav position to visible viewport */
        function clampNav() {
            var rect = nav.getBoundingClientRect();
            var vw = hostWin.innerWidth || hostDoc.documentElement.clientWidth;
            var vh = hostWin.innerHeight || hostDoc.documentElement.clientHeight;
            var cx = Math.max(0, Math.min(rect.left, vw - rect.width));
            var cy = Math.max(0, Math.min(rect.top, vh - rect.height));
            if (cx !== rect.left || cy !== rect.top) {
                nav.style.left = cx + 'px';
                nav.style.top = cy + 'px';
                nav.style.right = 'auto';
                nav.style.bottom = 'auto';
                nav.style.transform = 'none';
            }
            return {x: cx, y: cy};
        }

        function startDrag(x, y) {
            _dragging = true;
            _dragStartX = x;
            _dragStartY = y;
            var rect = nav.getBoundingClientRect();
            _dragNavX = rect.left;
            _dragNavY = rect.top;
            nav.style.cursor = 'grabbing';
        }

        function moveDrag(x, y) {
            if (!_dragging) return;
            nav.style.left = (_dragNavX + x - _dragStartX) + 'px';
            nav.style.top = (_dragNavY + y - _dragStartY) + 'px';
            nav.style.right = 'auto';
            nav.style.bottom = 'auto';
            nav.style.transform = 'none';
            clampNav();
        }

        function endDrag() {
            if (!_dragging) return;
            _dragging = false;
            nav.style.cursor = 'grab';
            try {
                var pos = clampNav();
                localStorage.setItem('stx-marker-pos', JSON.stringify(pos));
            } catch(e) {}
        }

        /* Restore saved position, then clamp to current viewport */
        try {
            var savedPos = JSON.parse(localStorage.getItem('stx-marker-pos'));
            if (savedPos && savedPos.x !== undefined) {
                nav.style.left = savedPos.x + 'px';
                nav.style.top = savedPos.y + 'px';
                nav.style.right = 'auto';
                nav.style.bottom = 'auto';
                nav.style.transform = 'none';
                var clamped = clampNav();
                if (clamped.x !== savedPos.x || clamped.y !== savedPos.y) {
                    localStorage.setItem('stx-marker-pos',
                        JSON.stringify(clamped));
                }
            }
        } catch(e) {}

        /* Mouse drag handlers */
        nav.addEventListener('mousedown', function(e) {
            if (!isDragTarget(e.target)) return;
            startDrag(e.clientX, e.clientY);
            e.preventDefault();
        });
        hostDoc.addEventListener('mousemove', function(e) { moveDrag(e.clientX, e.clientY); });
        hostDoc.addEventListener('mouseup', endDrag);

        /* Touch drag handlers (mobile/tablet) */
        nav.addEventListener('touchstart', function(e) {
            if (!isDragTarget(e.target)) return;
            var t = e.touches[0];
            startDrag(t.clientX, t.clientY);
        }, {passive: true});
        hostDoc.addEventListener('touchmove', function(e) {
            if (!_dragging) return;
            e.preventDefault();  /* prevent page scroll during drag */
            var t = e.touches[0];
            moveDrag(t.clientX, t.clientY);
        }, {passive: false});
        hostDoc.addEventListener('touchend', endDrag);

        /* Re-clamp on viewport resize (window resize, sidebar toggle, etc.) */
        hostWin.addEventListener('resize', function() {
            var pos = clampNav();
            try {
                localStorage.setItem('stx-marker-pos', JSON.stringify(pos));
            } catch(e) {}
        });
    }

    /* --- Logo + heart branding --- */
    var logoB64 = '__LOGO_B64__';
    var homeUrl = '__HOME_URL__';
    if (logoB64) {
        var sep = hostDoc.createElement('span');
        sep.style.cssText = 'width:1px;height:14px;background:rgba(255,255,255,.2);margin:0 4px;display:inline-block;';
        bar.appendChild(sep);

        var brand = hostDoc.createElement('a');
        brand.href = homeUrl;
        brand.target = '_blank';
        brand.rel = 'noopener';
        brand.title = 'StreamTeX';
        brand.style.cssText = 'display:inline-flex;align-items:center;gap:3px;text-decoration:none;cursor:pointer;opacity:.85;transition:opacity .15s;';
        brand.onmouseenter = function() { this.style.opacity = '1'; };
        brand.onmouseleave = function() { this.style.opacity = '.85'; };

        var logoImg = hostDoc.createElement('img');
        logoImg.src = 'data:image/png;base64,' + logoB64;
        logoImg.style.cssText = 'height:16px;width:auto;vertical-align:middle;';
        logoImg.alt = 'STx';
        brand.appendChild(logoImg);

        var heart = hostDoc.createElement('span');
        heart.textContent = '\\u2665';
        heart.style.cssText = 'color:__STX_CORAL__;font-size:10px;line-height:1;';
        brand.appendChild(heart);

        bar.appendChild(brand);
    }

    /* --- Drag grip handle (visible only when collapsed) --- */
    if (collapsible) {
        /* Include brand elements in collapsible group so they hide when collapsed */
        if (typeof sep !== 'undefined' && sep) barChildren.push(sep);
        if (typeof brand !== 'undefined' && brand) barChildren.push(brand);

        gripHandle = hostDoc.createElement('span');
        gripHandle.className = 'stx-drag-grip';
        gripHandle.textContent = '\\u2847\\u2847\\u2847';  /* ⡇⡇⡇ braille grip dots */
        gripHandle.title = 'Drag to move';
        gripHandle.style.cssText = 'display:none;cursor:grab;padding:2px 6px;font-size:14px;letter-spacing:2px;color:rgba(255,255,255,.5);touch-action:none;user-select:none;';
        bar.appendChild(gripHandle);

        /* Re-apply collapsed state now that all elements (brand, grip) exist */
        applyCollapsed();
    }

    /* --- Popup marker list --- */
    var popup = hostDoc.createElement('div');
    popup.style.cssText = 'display:none;position:absolute;bottom:calc(100% + 8px);right:0;background:rgba(30,30,30,.95);color:#eee;border-radius:12px;padding:6px 0;min-width:240px;max-width:350px;max-height:400px;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.5);backdrop-filter:blur(8px);font-size:12px;touch-action:auto;-webkit-overflow-scrolling:touch;';
    if (typeof _stxPopup !== 'undefined') _stxPopup = popup;  /* link to drag filter */

    for (var vi = 0; vi < visibleMarkers.length; vi++) {
        var globalIdx = visibleMarkers[vi].index;
        var row = hostDoc.createElement('div');
        row.className = 'stx-popup-item';
        row.dataset.idx = String(globalIdx);
        row.dataset.visIdx = String(vi);
        row.style.cssText = 'padding:7px 16px;cursor:pointer;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-left:3px solid transparent;transition:background .1s;';
        row.textContent = (globalIdx + 1) + '. ' + visibleMarkers[vi].label;
        row.onmouseenter = function() { this.style.background = 'rgba(128,128,128,.25)'; };
        row.onmouseleave = function() {
            if (parseInt(this.dataset.idx) !== currentIdx) this.style.background = 'transparent';
            else this.style.background = 'rgba(128,128,128,.2)';
        };
        (function(idx) {
            row.onclick = function() { navigateTo(idx); togglePopup(false); };
        })(globalIdx);
        popup.appendChild(row);
    }
    nav.appendChild(popup);

    function togglePopup(show) {
        popupOpen = typeof show === 'boolean' ? show : !popupOpen;
        popup.style.display = popupOpen ? 'block' : 'none';
        /* Allow native touch scroll inside popup; restore drag lock when closed */
        if (draggable) nav.style.touchAction = popupOpen ? 'auto' : 'none';
        hostWin._stxMarkerPopupState = popupOpen;
        if (popupOpen) highlightPopup();
    }

    function highlightPopup() {
        var items = popup.querySelectorAll('.stx-popup-item');
        var activeItem = null;
        for (var j = 0; j < items.length; j++) {
            var itemGlobalIdx = parseInt(items[j].dataset.idx);
            var isActive = itemGlobalIdx === currentIdx;
            items[j].style.background = isActive ? 'rgba(128,128,128,.2)' : 'transparent';
            items[j].style.borderLeftColor = isActive ? '__LINK_ACTIVE_COLOR__' : 'transparent';
            items[j].style.fontWeight = isActive ? '600' : 'normal';
            if (isActive) activeItem = items[j];
        }
        if (activeItem) activeItem.scrollIntoView({ block: 'nearest' });
    }

    /* Close popup on outside click */
    function outsideClick(e) {
        if (popupOpen && !nav.contains(e.target)) togglePopup(false);
    }
    hostDoc.addEventListener('click', outsideClick);

    /* --- Update UI (counter/label based on global marker index) --- */
    function nearestVisibleLabel() {
        for (var i = 0; i < visibleMarkers.length; i++) {
            if (visibleMarkers[i].index >= currentIdx) return visibleMarkers[i].label;
        }
        return visibleMarkers.length ? visibleMarkers[visibleMarkers.length - 1].label : '';
    }
    function updateUI() {
        if (counterEditing) return;
        var m = markers[currentIdx];
        var padded = String(currentIdx + 1).padStart(totalDigits, '\\u2007');
        counter.textContent = padded + ' / ' + markers.length;
        label.textContent = m ? (m.label || nearestVisibleLabel()) : '';
        if (popupOpen) highlightPopup();
        /* Sync presentation footer when counter_mode="slide" */
        var fc = hostDoc.querySelector('.stx-pf-counter[data-stx-counter="slide"]');
        if (fc) fc.textContent = 'Slide ' + (currentIdx + 1) + ' / ' + markers.length;
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
            /* Only update if at least one marker was found in the DOM
               and we are not in the middle of a programmatic scroll
               (navigateTo sets _navigating=true for 300ms).           */
            if (best >= 0 && best !== currentIdx && !_navigating) {
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
        var ms = hostDoc.getElementById('stx-marker-responsive');
        if (ms) ms.remove();
        /* Note: localStorage positions and collapsed state persist intentionally */
    };

    /* --- Init --- */
    var initTimer = setTimeout(function() {
        var startIdx = hostWin._stxMarkerStartIdx || 0;
        if (startIdx < 0) startIdx = markers.length + startIdx;
        startIdx = Math.max(0, Math.min(startIdx, markers.length - 1));
        hostWin._stxMarkerStartIdx = 0;

        /* Scroll to the target marker if it is in the DOM (same page).
           Without this, doScrollReset() in book.py forces the viewport
           to the top while currentIdx points to a different marker,
           causing LEFT/RIGHT to skip sections on cross-page navigation. */
        var m = markers[startIdx];
        var target = m ? findMarkerElement(m.anchor) : null;
        if (target) {
            currentIdx = startIdx;
            _navigating = true;
            scrollToTarget(target);
            setTimeout(function() { _navigating = false; }, 600);
        } else {
            /* Target marker not in DOM (cross-page or iframes not loaded).
               Detect nearest visible marker to sync with actual viewport. */
            var best = -1, bestDist = Infinity;
            for (var i = 0; i < markers.length; i++) {
                var t = findMarkerElement(markers[i].anchor);
                if (!t) continue;
                var d = Math.abs(t.getBoundingClientRect().top - OFFSET);
                if (d < bestDist) { bestDist = d; best = i; }
            }
            currentIdx = (best >= 0) ? best : startIdx;
        }

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
        .replace('__SHOW_UI__', show_ui)
        .replace('__LINK_ACTIVE_COLOR__', LINK_ACTIVE_COLOR_DARK)
        .replace('__LOGO_B64__', logo_b64)
        .replace('__HOME_URL__', STX_HOME_URL)
        .replace('__STX_CORAL__', STX_CORAL)
        .replace('__DRAGGABLE__', 'true' if config.draggable else 'false')
        .replace('__COLLAPSIBLE__', 'true' if config.collapsible else 'false')
        .replace('__PROFILE_NAMES__', json.dumps(profile_names or ["Default"]))
        .replace('__ACTIVE_PROFILE__', json.dumps(active_profile or "Default"))
        .replace('__PROFILE_MODIFIED__', 'true' if profile_modified else 'false'))

    # components.html() creates a real iframe where scripts execute
    # (st.html() strips <script> tags in Streamlit 1.54+)
    components.html(f"<script>{js_body}</script>", height=0)
