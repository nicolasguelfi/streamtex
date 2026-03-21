"""Loading overlay with progress indicator for StreamTeX apps.

Displays a full-screen semi-transparent overlay during initial loading,
with an optional progress percentage based on module rendering count.

The overlay is injected into the parent Streamlit document via JS
(same pattern as paginated navigation and marker widgets).
"""

from __future__ import annotations

import logging

import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTML/CSS/JS templates
# ---------------------------------------------------------------------------

_OVERLAY_CSS = """\
#stx-loading-overlay {
  position: fixed; inset: 0; z-index: 99999;
  background: rgba(120, 80, 160, 0.85);
  display: flex; align-items: center; justify-content: center;
  transition: opacity 0.3s ease;
}
#stx-loading-card {
  background: rgba(255,255,255,0.1); backdrop-filter: blur(8px);
  border-radius: 16px; padding: 48px 64px; text-align: center;
  color: white; min-width: 280px;
}
#stx-loading-brand {
  font-size: 1.6rem; font-weight: 700; letter-spacing: 1px;
  margin-bottom: 12px; opacity: 0.9;
}
#stx-loading-status {
  font-size: 1.1rem; font-weight: 500; margin-bottom: 8px;
}
#stx-loading-percent {
  font-size: 3rem; font-weight: 700; letter-spacing: 2px;
  margin-bottom: 12px; display: none;
}
#stx-loading-bar {
  width: 260px; height: 4px; border-radius: 2px;
  background: rgba(255,255,255,0.2); margin: 0 auto 12px;
}
#stx-loading-bar-fill {
  height: 100%; border-radius: 2px; background: white;
  width: 0%; transition: width 1.5s ease;
}
#stx-loading-counter {
  font-size: 0.85rem; opacity: 0.6; display: none;
}
#stx-loading-module {
  font-size: 0.75rem; opacity: 0.45; margin-top: 4px;
  font-family: monospace; display: none;
}
#stx-loading-heartbeat {
  display: none; margin-top: 14px;
}
#stx-loading-heartbeat span {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.7); margin: 0 3px;
  animation: stx-bounce 1.4s ease-in-out infinite;
}
#stx-loading-heartbeat span:nth-child(2) { animation-delay: 0.16s; }
#stx-loading-heartbeat span:nth-child(3) { animation-delay: 0.32s; }
@keyframes stx-pulse {
  0%, 100% { opacity: 0.4; }
  50%      { opacity: 1; }
}
@keyframes stx-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1.2); opacity: 1; }
}
.stx-pulse { animation: stx-pulse 1.5s ease-in-out infinite; }
"""

_INJECT_JS = """\
<script>
(function() {
  var doc = parent.document;
  if (doc.getElementById('stx-loading-overlay')) return;
  var style = doc.createElement('style');
  style.textContent = `__CSS__`;
  doc.head.appendChild(style);
  var overlay = doc.createElement('div');
  overlay.id = 'stx-loading-overlay';
  overlay.innerHTML = `
    <div id="stx-loading-card">
      <div id="stx-loading-brand">StreamTeX</div>
      <div id="stx-loading-status" class="stx-pulse">Initializing\\u2026</div>
      <div id="stx-loading-percent"></div>
      <div id="stx-loading-bar"><div id="stx-loading-bar-fill"></div></div>
      <div id="stx-loading-counter"></div>
      <div id="stx-loading-module"></div>
      <div id="stx-loading-heartbeat"><span></span><span></span><span></span></div>
    </div>
  `;
  doc.body.appendChild(overlay);
})();
</script>
"""

_UPDATE_JS = """\
<script>
(function() {
  var doc = parent.document;
  var pct = __PCT__;
  var current = __CURRENT__;
  var total = __TOTAL__;
  var modName = '__MODULE__';
  var el;
  el = doc.getElementById('stx-loading-status');
  if (el) { el.textContent = 'Loading\\u2026'; el.classList.remove('stx-pulse'); }
  el = doc.getElementById('stx-loading-percent');
  if (el) { el.style.display = 'block'; el.textContent = pct + '%'; }
  el = doc.getElementById('stx-loading-bar-fill');
  if (el) { el.style.width = pct + '%'; }
  el = doc.getElementById('stx-loading-counter');
  if (el) { el.style.display = 'block'; el.textContent = 'module ' + current + ' / ' + total; }
  el = doc.getElementById('stx-loading-module');
  if (el && modName) { el.style.display = 'block'; el.textContent = modName; }
  el = doc.getElementById('stx-loading-heartbeat');
  if (el) { el.style.display = 'block'; }
})();
</script>
"""

_REMOVE_JS = """\
<script>
(function() {
  var doc = parent.document;
  var overlay = doc.getElementById('stx-loading-overlay');
  if (!overlay) return;
  overlay.style.opacity = '0';
  setTimeout(function() { overlay.remove(); }, 350);
})();
</script>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def inject_loading_overlay() -> None:
    """Create the full-screen loading overlay on the parent document."""
    js = _INJECT_JS.replace("__CSS__", _OVERLAY_CSS.replace("`", "\\`"))
    components.html(js, height=0)


def update_loading_progress(current: int, total: int, module_name: str = "") -> None:
    """Update the overlay to show progress *current* / *total*.

    Parameters
    ----------
    current:
        Number of modules rendered so far (1-based after each render).
    total:
        Total number of modules.
    module_name:
        Short display name of the module being rendered (e.g. ``bck_intro``).
    """
    pct = int(100 * current / total) if total > 0 else 0
    # Sanitise module name for JS string literal
    safe_name = module_name.replace("\\", "\\\\").replace("'", "\\'")
    js = (_UPDATE_JS
          .replace("__PCT__", str(pct))
          .replace("__CURRENT__", str(current))
          .replace("__TOTAL__", str(total))
          .replace("__MODULE__", safe_name))
    components.html(js, height=0)


def remove_loading_overlay() -> None:
    """Fade out and remove the loading overlay."""
    components.html(_REMOVE_JS, height=0)
