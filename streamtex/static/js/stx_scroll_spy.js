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
      // `anchor === null` (no match) must NOT light up entries whose
      // own anchorOf also returns null (e.g. entries that don't yet
      // have an inner <a>).  Strict null guard:
      var entryAnchor = anchorOf(entries[i]);
      var isActive = (anchor !== null) && (entryAnchor === anchor);
      var cur = entries[i].classList.contains(ACTIVE_CLS);
      if (isActive && !cur) entries[i].classList.add(ACTIVE_CLS);
      else if (!isActive && cur) entries[i].classList.remove(ACTIVE_CLS);
    }
  }

  function findClosestAnchor() {
    // Best = the anchor with the largest rect.top that is still <= TOP_OFFSET
    // (the most recently scrolled-past heading).
    //
    // Skip `stx-goto-*` anchors: those target the hidden Streamlit
    // navigation buttons used by paginated mode, not real content
    // headings.  They live at a degenerate position in the document
    // (absolute, left:-9999px, top:auto) so their bounding rect would
    // otherwise pollute the closest-anchor heuristic with arbitrary
    // values that don't match the user's scroll position.
    var entries = getEntries();
    var bestBelow = null;
    var bestBelowTop = Infinity;
    var bestAbove = null;
    var bestAboveTop = -Infinity;
    var seen = {};
    for (var i = 0; i < entries.length; i++) {
      var a = anchorOf(entries[i]);
      if (!a || seen[a]) continue;
      if (a.indexOf('stx-goto-') === 0) continue;
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

  // Single fire path for recomputing the active entry.
  //
  // setActive() is the SOLE writer of `.stx-nav-active` (add + remove).
  // On every recompute we call it with the result of
  // findClosestAnchor() — `null` means "no anchor visible" and clears
  // every existing active class.  We never gate on
  // "anchor === currentActiveAnchor" because the same value can map to
  // a DIFFERENT DOM node after Streamlit's reconciliation (a node's
  // inner <a href> can flip between content-anchor and `stx-goto-N`
  // depending on which page is current).
  function fireRecompute() {
    if (Date.now() < suppressUntil) return;
    setActive(findClosestAnchor());
  }

  // Throttle: fire at most once per 100 ms, but ALWAYS fire within
  // 100 ms of any pending signal.  This is critical for the rapid-
  // navigation case (double PageDown, floating-arrow burst): a pure
  // debounce would keep getting postponed by trailing mutations and
  // the highlight could end up stuck on a stale node forever.
  // Throttling gives us a guaranteed cadence.
  var THROTTLE_MS = 100;
  var lastFireMs = 0;
  var pendingTimer = null;
  function scheduleRecompute() {
    var now = Date.now();
    var sinceLast = now - lastFireMs;
    if (sinceLast >= THROTTLE_MS) {
      lastFireMs = now;
      fireRecompute();
      return;
    }
    if (pendingTimer) return;  // already scheduled
    pendingTimer = setTimeout(function () {
      pendingTimer = null;
      lastFireMs = Date.now();
      fireRecompute();
    }, THROTTLE_MS - sinceLast);
  }

  // Scroll → throttled recompute.
  hostWin.addEventListener('scroll', scheduleRecompute, { passive: true });

  // Hashchange: some Streamlit navigation paths update the URL hash,
  // others don't.  Listening here costs nothing and helps the few
  // paths that do (sidebar TOC click on a `#stx-goto-N` link).
  hostWin.addEventListener('hashchange', scheduleRecompute);

  // Initial pass — fire once after the DOM settles.
  if (hostDoc.readyState === 'complete' || hostDoc.readyState === 'interactive') {
    setTimeout(fireRecompute, 80);
  } else {
    hostWin.addEventListener('load', function () { setTimeout(fireRecompute, 80); });
  }

  // MutationObserver: any childList mutation in the body subtree
  // (which is what Streamlit reconciliation produces on every rerun)
  // schedules a recompute.  Combined with the 100 ms throttle, this
  // gives us a guaranteed recompute cadence during DOM churn — so
  // even if Streamlit emits trailing mutations for several seconds
  // (async images, lazy-loaded components, etc.) the active entry
  // converges on the correct one within ~100 ms of the DOM stabilising.
  //
  // We ALSO observe `class` attribute mutations and route them through
  // the same throttled recompute.  In practice Streamlit reconciles by
  // node replacement (childList), but if anything strips
  // `.stx-nav-active` via a pure attribute mutation with no surrounding
  // DOM change, the childList-only path would miss it.  Routing through
  // setActive() — the single writer — means the safety net cannot cause
  // class flapping: setActive() reads the current state before writing.
  var Observer = hostWin.MutationObserver || window.MutationObserver;
  if (Observer) {
    var obs = new Observer(function (mutations) {
      for (var j = 0; j < mutations.length; j++) {
        var m = mutations[j];
        if (m.type === 'childList' &&
            (m.addedNodes.length > 0 || m.removedNodes.length > 0)) {
          scheduleRecompute();
          return;
        }
        if (m.type === 'attributes' && m.attributeName === 'class') {
          scheduleRecompute();
          return;
        }
      }
    });
    obs.observe(hostDoc.body, {
      childList: true, subtree: true,
      attributes: true, attributeFilter: ['class'],
    });
    hostWin.__stxScrollSpyObs = obs;
  }
})();
