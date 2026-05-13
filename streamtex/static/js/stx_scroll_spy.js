/* StreamTeX cross-context scroll-spy.
 *
 * Adds the ``stx-nav-active`` class to the TOC / Markers entry that
 * matches what the reader is currently focused on, across three
 * contexts that share the same ``data-stx-block`` markup:
 *
 *   * Live, TOC sidebar panel  (``populate_toc``)
 *   * Live, Markers sidebar panel  (``populate_markers_sidebar``)
 *   * Static HTML export sidebar  (``_build_sidebar_html``)
 *
 * Behaviour:
 *   1. Click on any ``[data-stx-block] a[href^="#"]`` -> the entry
 *      becomes active immediately.  A 400 ms suppression window stops
 *      the scroll handler from clobbering the click while smooth scroll
 *      is still in flight.
 *   2. Scroll -> the entry whose anchor target is closest to (but at or
 *      above) ~120 px from the viewport top becomes active.  If no
 *      anchor is yet above that line (top of document), the first
 *      anchor below it wins.
 *
 * Robustness:
 *   * ``__stxScrollSpy`` guard prevents double-installation when the
 *      v2 component re-mounts.
 *   * A MutationObserver watches the ``class`` attribute on
 *     ``[data-stx-block]`` and re-applies ``stx-nav-active`` to the
 *     tracked entry if Streamlit's reconciliation strips it on rerun
 *     (same pattern as the marker observer's auditMarkerCells).
 */
(function () {
  'use strict';

  var hostWin = window.parent || window;
  if (!hostWin) return;
  var hostDoc = hostWin.document;
  if (!hostDoc || !hostDoc.body) return;

  if (hostWin.__stxScrollSpy) return;
  hostWin.__stxScrollSpy = true;

  var ENTRY_SEL = '[data-stx-block]';
  var ACTIVE_CLS = 'stx-nav-active';
  // Pixel offset from the viewport top that defines "current reading"
  // position — sticky title / floating bar height typically lives in
  // this zone.
  var TOP_OFFSET = 120;
  // After a click, ignore scroll-spy recalculations for this long so
  // the smooth-scroll animation doesn't bounce the active state away
  // from the just-clicked entry.
  var CLICK_SUPPRESS_MS = 400;

  var currentActiveAnchor = null;
  var suppressUntil = 0;

  function getEntries() {
    return hostDoc.querySelectorAll(ENTRY_SEL);
  }

  function anchorOf(entry) {
    var a = entry.querySelector('a[href^="#"]');
    if (!a) return null;
    return decodeURIComponent(a.getAttribute('href').slice(1));
  }

  function setActive(anchor) {
    currentActiveAnchor = anchor;
    var entries = getEntries();
    for (var i = 0; i < entries.length; i++) {
      var isActive = anchorOf(entries[i]) === anchor;
      var cur = entries[i].classList.contains(ACTIVE_CLS);
      if (isActive && !cur) entries[i].classList.add(ACTIVE_CLS);
      else if (!isActive && cur) entries[i].classList.remove(ACTIVE_CLS);
    }
  }

  function findClosestAnchor() {
    // Best = the anchor with the largest rect.top that is still <= TOP_OFFSET
    // (the most recently scrolled-past heading).
    var entries = getEntries();
    var bestBelow = null;
    var bestBelowTop = Infinity;
    var bestAbove = null;
    var bestAboveTop = -Infinity;
    var seen = {};
    for (var i = 0; i < entries.length; i++) {
      var a = anchorOf(entries[i]);
      if (!a || seen[a]) continue;
      seen[a] = true;
      var target = hostDoc.getElementById(a);
      if (!target) continue;
      var top = target.getBoundingClientRect().top;
      if (top <= TOP_OFFSET) {
        if (top > bestAboveTop) {
          bestAboveTop = top;
          bestAbove = a;
        }
      } else {
        if (top < bestBelowTop) {
          bestBelowTop = top;
          bestBelow = a;
        }
      }
    }
    return bestAbove || bestBelow;
  }

  // Click handler — instantaneous active update, plus a short
  // suppression window so the subsequent smooth-scroll doesn't undo it.
  hostDoc.body.addEventListener('click', function (e) {
    if (!e.target || !e.target.closest) return;
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var entry = a.closest(ENTRY_SEL);
    if (!entry) return;
    var anchor = decodeURIComponent(a.getAttribute('href').slice(1));
    if (!anchor) return;
    setActive(anchor);
    suppressUntil = Date.now() + CLICK_SUPPRESS_MS;
  }, true);

  // Scroll handler — debounced.
  var scrollTimer = null;
  function onScroll() {
    if (Date.now() < suppressUntil) return;
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function () {
      var anchor = findClosestAnchor();
      if (anchor && anchor !== currentActiveAnchor) setActive(anchor);
    }, 80);
  }
  hostWin.addEventListener('scroll', onScroll, { passive: true });

  // Initial pass — fire once after the DOM settles.
  if (hostDoc.readyState === 'complete' || hostDoc.readyState === 'interactive') {
    setTimeout(onScroll, 50);
  } else {
    hostWin.addEventListener('load', function () { setTimeout(onScroll, 50); });
  }

  // MutationObserver — re-apply the active class if Streamlit's
  // reconciliation strips it on a rerun (live context).  Scoped to
  // class-attribute mutations so the cost is bounded.
  var Observer = hostWin.MutationObserver || window.MutationObserver;
  if (Observer) {
    var obs = new Observer(function () {
      if (!currentActiveAnchor) return;
      var entries = getEntries();
      for (var i = 0; i < entries.length; i++) {
        if (anchorOf(entries[i]) === currentActiveAnchor &&
            !entries[i].classList.contains(ACTIVE_CLS)) {
          entries[i].classList.add(ACTIVE_CLS);
        }
      }
    });
    obs.observe(hostDoc.body, {
      childList: true, subtree: true,
      attributes: true, attributeFilter: ['class']
    });
    hostWin.__stxScrollSpyObs = obs;
  }
})();
