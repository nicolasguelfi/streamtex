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
    // Active = the anchor whose target is CLOSEST to the reading line
    // (TOP_OFFSET), above or below.
    //
    // The previous rule ("largest rect.top still <= TOP_OFFSET", i.e. the
    // most recently scrolled-past heading) lagged one entry behind after a
    // programmatic scroll: the floating widget parks the MARKER at its
    // scroll offset, but the sidebar tracks HEADING anchors that sit just
    // BELOW their marker — landing just past TOP_OFFSET — so "largest top
    // <= TOP_OFFSET" selected the PREVIOUS heading (companion §6.3/§6.9,
    // the user-reported −1 lag in continuous + export). Picking the nearest
    // anchor instead tracks the displayed section without that off-by-one.
    // (Trade-off: while free-scrolling a tall section it may switch to the
    // next heading slightly early — accepted.)
    var entries = getEntries();
    var best = null;
    var bestDist = Infinity;
    var seen = {};
    for (var i = 0; i < entries.length; i++) {
      var a = anchorOf(entries[i]);
      if (!a || seen[a]) continue;
      seen[a] = true;
      var target = hostDoc.getElementById(a);
      if (!target) continue;
      var dist = Math.abs(target.getBoundingClientRect().top - TOP_OFFSET);
      if (dist < bestDist) {
        bestDist = dist;
        best = a;
      }
    }
    return best;
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
  // Listen in the CAPTURE phase so we hear scroll from ANY container, not
  // just window. In live Streamlit the scroll happens inside `.stMain`
  // (a scrollable <section>), whose scroll events do not reach a plain
  // window listener — leaving the sidebar highlight frozen (companion
  // §6.15). Capture-phase listeners receive scroll from descendant
  // scrollers, covering window (export) and .stMain (live) uniformly.
  hostWin.addEventListener('scroll', onScroll, { capture: true, passive: true });

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
