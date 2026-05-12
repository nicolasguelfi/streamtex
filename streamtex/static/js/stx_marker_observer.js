/* StreamTeX marker observer — replaces per-instance :has() selectors.
 *
 * This script is injected via `streamlit.components.v1.html(..., height=0)`,
 * which means it runs inside a 0-pixel iframe.  All DOM operations must
 * therefore target the *parent* document (the actual Streamlit app page) via
 * `window.parent.document` — the iframe's own document is empty.
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
  var KIND_TO_CLASS = {
    'block':       'stx-block',
    'span':        'stx-span',
    'grid':        'stx-grid',
    'list':        'stx-list',
    'list-item':   'stx-list-item',
    'zoom':        'stx-zoom',
    'md-big':      'stx-md-big'
  };

  function applyMarker(markerSpan) {
    var kind = markerSpan.getAttribute('data-stx-kind');
    var cls = KIND_TO_CLASS[kind];
    if (!cls) return;

    var parent = markerSpan.closest(PARENT_SEL);
    if (!parent) return;
    if (parent.classList.contains(cls)) {
      // Already processed for this kind — still hide the marker cell.
      var ecPrev = markerSpan.closest('.element-container');
      if (ecPrev) ecPrev.classList.add('stx-marker-cell');
      return;
    }

    parent.classList.add(cls);

    // Forward data-stx-* attributes (except `kind`) as CSS custom properties.
    // Naming: `data-stx-foo-bar="x"` → `--stx-foo-bar: x;`
    var attrs = markerSpan.attributes;
    for (var i = 0; i < attrs.length; i++) {
      var a = attrs[i];
      if (a.name === 'data-stx-kind') continue;
      if (a.name.indexOf('data-stx-') !== 0) continue;
      var cssVar = '--' + a.name.slice('data-'.length);
      parent.style.setProperty(cssVar, a.value);
    }

    // Tag for the inspector / export tooling + per-instance CSS targeting.
    // Use a *kind-prefixed* attribute on the parent so multiple marker kinds
    // (e.g. a list-item that wraps a st_block) can coexist without one's uid
    // overwriting another's.
    var uid = markerSpan.getAttribute('data-stx-uid');
    if (uid) {
      parent.setAttribute('data-stx-' + kind + '-uid', uid);
    }

    // Boolean modifiers (presence-only attributes like data-stx-ordered).
    if (markerSpan.hasAttribute('data-stx-ordered')) {
      parent.classList.add('stx-list-item--ordered');
    }

    // Hide the marker's own element-container so it doesn't take a grid/flex slot.
    var ec = markerSpan.closest('.element-container');
    if (ec) ec.classList.add('stx-marker-cell');
  }

  function scan(root) {
    var scope = (root && root.querySelectorAll) ? root : hostDoc;
    var markers = scope.querySelectorAll('span.stx-marker:not([data-stx-processed])');
    for (var i = 0; i < markers.length; i++) {
      applyMarker(markers[i]);
      markers[i].setAttribute('data-stx-processed', '1');
    }
  }

  // Initial pass (covers everything already in the parent DOM at script start).
  scan(hostDoc);

  // MutationObserver lives in the iframe scope but observes the parent doc.
  // Same-origin Streamlit allows this; the observer instance survives as
  // long as window.parent.__stxMarkerObsHandle holds a reference.
  var ObserverCtor = hostWin.MutationObserver || window.MutationObserver;
  var obs = new ObserverCtor(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      var m = muts[i];
      for (var j = 0; j < m.addedNodes.length; j++) {
        var node = m.addedNodes[j];
        if (node.nodeType !== 1) continue;
        if (node.matches && node.matches('span.stx-marker:not([data-stx-processed])')) {
          applyMarker(node);
          node.setAttribute('data-stx-processed', '1');
        }
        if (node.querySelectorAll) scan(node);
      }
    }
  });
  obs.observe(hostDoc.body, { childList: true, subtree: true });

  // Keep a reference on the parent window so we can introspect from devtools.
  hostWin.__stxMarkerObsHandle = obs;
})();
