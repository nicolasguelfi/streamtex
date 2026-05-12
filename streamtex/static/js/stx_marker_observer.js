/* StreamTeX marker observer — replaces per-instance :has() selectors.
 *
 * This script is injected via `streamlit.components.v1.html(..., height=0)`,
 * which means it runs inside a 0-pixel iframe.  All DOM operations must
 * therefore target the *parent* document (the actual Streamlit app page)
 * via `window.parent.document` — the iframe's own document is empty.
 *
 * Why components.v1.html instead of st.iframe (deprecated → removed
 * 2026-06-01):  st.iframe is a regular Streamlit element that Streamlit's
 * reconciliation can remove/recreate across reruns, destroying the
 * MutationObserver.  components.v1.html is treated as a custom component
 * whose iframe persists across reruns.  See
 * documentation/maintenance/components.v1_issue/ for the investigation
 * (0.6.19/0.6.20 failed attempts at switching this specific call site).
 *
 * When a sentinel <span class="stx-marker" data-stx-kind="..."
 *   data-stx-uid="..." data-stx-*="..." style="display:none"></span>
 * appears anywhere in the parent Streamlit page, this observer:
 *   1. Walks up to the nearest [data-testid="stVerticalBlock"] ancestor.
 *   2. Adds a class (e.g. `stx-block`, `stx-grid`, `stx-list-item`) on that
 *      ancestor based on `data-stx-kind`.
 *   3. Copies every other `data-stx-*` attribute onto the ancestor as a CSS
 *      custom property (`--stx-foo-bar`), so the global stylesheet can read
 *      parameter values without per-instance CSS injection.
 *   4. Tags the marker's .element-container with class `stx-marker-cell`
 *      so the global stylesheet can hide it.
 *   5. Sets a kind-prefixed UID attribute (`data-stx-{kind}-uid`) on the
 *      ancestor so per-instance stylesheets (`[data-stx-block-uid="…"]`,
 *      `[data-stx-list-item-uid="…"]`, …) can target it.
 *
 * This entire system is the marker-runtime replacement for the legacy
 * `div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{uid})`
 * pattern.  See documentation/maintenance/freeze-has/fix-plan.md for context.
 */
(function () {
  'use strict';

  // We live inside a Streamlit components iframe.  Reach back to the parent
  // window/document for all real DOM operations.  Same pattern as
  // streamtex/marker.py and streamtex/bib_preview.py.
  var hostWin = window.parent;
  if (!hostWin) return;
  var hostDoc = hostWin.document;
  if (!hostDoc || !hostDoc.body) return;

  if (hostWin.__stxMarkerObs) return;       // idempotent across reruns
  hostWin.__stxMarkerObs = true;

  var PARENT_SEL = '[data-testid="stVerticalBlock"]';
  // Streamlit ≤ 1.55 used class `.element-container`; ≥ 1.56 renamed it to
  // `stElementContainer` and exposes it via `data-testid="stElementContainer"`.
  // Match both so we can find the marker's own cell across versions.
  var EC_SEL = '[data-testid="stElementContainer"], .element-container';
  var KIND_TO_CLASS = {
    'block':       'stx-block',
    'span':        'stx-span',
    'grid':        'stx-grid',
    'list':        'stx-list',
    'list-item':   'stx-list-item',
    'zoom':        'stx-zoom',
    'md-big':      'stx-md-big'
  };

  // Idempotent inline-style setter: only writes if the existing
  // (value, priority) tuple does not already match — this avoids triggering
  // MutationObserver fires for no-op writes, which is what stops the
  // attribute-watching observer below from looping on itself.
  function setInlineImportant(el, prop, value) {
    if (el.style.getPropertyValue(prop) === value &&
        el.style.getPropertyPriority(prop) === 'important') return;
    el.style.setProperty(prop, value, 'important');
  }

  function hideMarkerCell(markerSpan) {
    // Hide the marker's own cell — bulletproof: class for CSS introspection,
    // inline !important for guaranteed effect regardless of cascade.
    var ec = markerSpan.closest(EC_SEL);
    if (!ec) return;
    if (!ec.classList.contains('stx-marker-cell')) {
      ec.classList.add('stx-marker-cell');
    }
    setInlineImportant(ec, 'display', 'none');
  }

  function applyMarker(markerSpan) {
    // Fully idempotent: every write is guarded by a read so re-running
    // applyMarker on an already-applied marker fires no mutations.  This is
    // essential because the MutationObserver watches attribute changes
    // (Streamlit's reconciliation strips our class/uid/style on rerun),
    // and a non-idempotent applyMarker would loop on itself indefinitely.
    var kind = markerSpan.getAttribute('data-stx-kind');
    var cls = KIND_TO_CLASS[kind];
    if (!cls) return;

    var parent = markerSpan.closest(PARENT_SEL);
    if (!parent) return;

    // 1. Kind class.
    if (!parent.classList.contains(cls)) {
      parent.classList.add(cls);
    }

    // 2. Forward data-stx-* attributes (except `kind`) as CSS custom
    //    properties.  Naming: `data-stx-foo-bar="x"` → `--stx-foo-bar: x;`.
    var attrs = markerSpan.attributes;
    for (var i = 0; i < attrs.length; i++) {
      var a = attrs[i];
      if (a.name === 'data-stx-kind') continue;
      if (a.name.indexOf('data-stx-') !== 0) continue;
      var cssVar = '--' + a.name.slice('data-'.length);
      if (parent.style.getPropertyValue(cssVar) !== a.value) {
        parent.style.setProperty(cssVar, a.value);
      }
    }

    // 3. Kind-specific INLINE style overrides — set directly on the element
    //    with !important so they beat Streamlit's own inline `display: flex`
    //    (applied on every stVerticalBlock since 1.56).  This makes the
    //    layout independent of the CSS cascade.
    if (kind === 'grid') {
      var tpl = markerSpan.getAttribute('data-stx-grid-template') || '1fr';
      var g   = markerSpan.getAttribute('data-stx-grid-gap') || '0';
      setInlineImportant(parent, 'display', 'grid');
      setInlineImportant(parent, 'grid-template-columns', tpl);
      setInlineImportant(parent, 'gap', g);
      setInlineImportant(parent, 'align-items', 'stretch');
    } else if (kind === 'span') {
      setInlineImportant(parent, 'display', 'flex');
      setInlineImportant(parent, 'flex-direction', 'row');
      setInlineImportant(parent, 'white-space', 'pre');
    } else if (kind === 'list-item') {
      setInlineImportant(parent, 'display', 'flex');
      setInlineImportant(parent, 'flex-direction', 'row');
      setInlineImportant(parent, 'align-items', 'baseline');
      setInlineImportant(parent, 'gap', '0.5rem');
    } else if (kind === 'zoom') {
      var z = markerSpan.getAttribute('data-stx-zoom-factor') || '1';
      setInlineImportant(parent, 'zoom', z);
    }

    // 4. Per-instance kind-prefixed uid attribute (the per-instance
    //    stylesheet selectors target `[data-stx-{kind}-uid="…"]`).
    var uid = markerSpan.getAttribute('data-stx-uid');
    if (uid) {
      var uidAttr = 'data-stx-' + kind + '-uid';
      if (parent.getAttribute(uidAttr) !== uid) {
        parent.setAttribute(uidAttr, uid);
      }
    }

    // 5. Boolean modifiers (presence-only attributes like data-stx-ordered).
    if (markerSpan.hasAttribute('data-stx-ordered')) {
      if (!parent.classList.contains('stx-list-item--ordered')) {
        parent.classList.add('stx-list-item--ordered');
      }
    }

    // 6. Hide the marker's own element-container so it doesn't take a
    //    grid/flex slot.
    hideMarkerCell(markerSpan);
  }

  function scanAll(root) {
    // Full-document marker walk.  Used only for the initial bootstrap
    // pass (covers everything already in the DOM at script start) — the
    // per-mutation hot path uses surgical processing instead, see
    // handleBatch() below.
    var scope = (root && root.querySelectorAll) ? root : hostDoc;
    var markers = scope.querySelectorAll('span.stx-marker');
    for (var i = 0; i < markers.length; i++) {
      applyMarker(markers[i]);
    }
  }

  // Initial pass (covers everything already in the parent DOM at script start).
  scanAll(hostDoc);

  // Surgical mutation handling — each batch of MutationRecords is
  // processed by acting only on what changed:
  //
  //   - childList.addedNodes: extract any span.stx-marker (the node itself
  //     or descendants of an added subtree) and apply it.
  //   - attributes on a stVerticalBlock parent: Streamlit reconciliation
  //     may have stripped our class/uid/style.  Find the marker inside
  //     that parent and re-apply.
  //
  // We dedupe targets via Sets so a single batch with many mutations on
  // the same parent triggers at most one applyMarker per parent.  This
  // is what bounds the per-batch cost to O(unique_targets) instead of
  // the previous O(all_markers × batches) full-document scans.
  //
  // applyMarker is fully idempotent (no-op when state already matches),
  // so re-running it on a parent that is already in the correct state
  // does not trigger a feedback loop through the observer.
  var pendingBatch = [];
  var pendingScheduled = false;

  function handleBatch(batch) {
    var addedMarkers = (typeof Set === 'function') ? new Set() : null;
    var dirtyParents = (typeof Set === 'function') ? new Set() : null;
    // Fallback for engines without Set: dedupe via Array.indexOf.
    var addedArr = addedMarkers ? null : [];
    var dirtyArr = dirtyParents ? null : [];

    function pushMarker(m) {
      if (addedMarkers) { addedMarkers.add(m); return; }
      if (addedArr.indexOf(m) === -1) addedArr.push(m);
    }
    function pushParent(p) {
      if (dirtyParents) { dirtyParents.add(p); return; }
      if (dirtyArr.indexOf(p) === -1) dirtyArr.push(p);
    }

    for (var i = 0; i < batch.length; i++) {
      var rec = batch[i];
      if (rec.type === 'childList') {
        var added = rec.addedNodes;
        for (var j = 0; j < added.length; j++) {
          var n = added[j];
          if (n.nodeType !== 1) continue;
          if (n.matches && n.matches('span.stx-marker')) {
            pushMarker(n);
          }
          if (n.querySelectorAll) {
            var sub = n.querySelectorAll('span.stx-marker');
            for (var k = 0; k < sub.length; k++) pushMarker(sub[k]);
          }
        }
      } else if (rec.type === 'attributes') {
        var t = rec.target;
        if (t && t.nodeType === 1 && t.matches && t.matches(PARENT_SEL)) {
          pushParent(t);
        }
      }
    }

    function processMarker(marker) {
      applyMarker(marker);
    }
    function processParent(parent) {
      // The marker for this parent lives inside one of its
      // element-container children.  ``:scope`` keeps the lookup tight
      // and short-circuits as soon as we find it.
      var marker = parent.querySelector(':scope span.stx-marker');
      if (marker) applyMarker(marker);
    }

    if (addedMarkers) {
      addedMarkers.forEach(processMarker);
      dirtyParents.forEach(processParent);
    } else {
      for (var i = 0; i < addedArr.length; i++) processMarker(addedArr[i]);
      for (var i = 0; i < dirtyArr.length; i++) processParent(dirtyArr[i]);
    }
  }

  function scheduleHandle() {
    if (pendingScheduled || pendingBatch.length === 0) return;
    pendingScheduled = true;
    var raf = hostWin.requestAnimationFrame || window.requestAnimationFrame ||
              function (cb) { return setTimeout(cb, 16); };
    raf(function () {
      var batch = pendingBatch;
      pendingBatch = [];
      pendingScheduled = false;
      handleBatch(batch);
    });
  }

  // MutationObserver lives in the iframe scope but observes the parent doc.
  // Same-origin Streamlit allows this; the observer instance survives as
  // long as window.parent.__stxMarkerObsHandle holds a reference.
  //
  // We watch THREE kinds of changes:
  //   - childList   : new markers, new stVerticalBlocks added on rerun.
  //   - attributes  : Streamlit reconciliation can strip our class / uid /
  //                   inline style from existing parents WITHOUT touching
  //                   their child list — this is what made the "settings
  //                   slider wipes backgrounds" bug invisible to a
  //                   childList-only observer.  We filter to only the
  //                   attributes that, if changed, would invalidate our
  //                   layout: `class`, `style`, and each `data-stx-*-uid`.
  var ObserverCtor = hostWin.MutationObserver || window.MutationObserver;
  var obs = new ObserverCtor(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      pendingBatch.push(mutations[i]);
    }
    scheduleHandle();
  });
  obs.observe(hostDoc.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: [
      'class', 'style',
      'data-stx-block-uid', 'data-stx-grid-uid', 'data-stx-list-uid',
      'data-stx-list-item-uid', 'data-stx-zoom-uid', 'data-stx-span-uid',
      'data-stx-md-big-uid'
    ]
  });

  // Keep a reference on the parent window so we can introspect from devtools.
  hostWin.__stxMarkerObsHandle = obs;
})();
