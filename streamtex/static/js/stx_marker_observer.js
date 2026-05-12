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

  function hideMarkerCell(markerSpan) {
    // Hide the marker's own cell — bulletproof: class for CSS introspection,
    // inline !important for guaranteed effect regardless of cascade.
    var ec = markerSpan.closest(EC_SEL);
    if (!ec) return;
    ec.classList.add('stx-marker-cell');
    ec.style.setProperty('display', 'none', 'important');
  }

  function applyMarker(markerSpan) {
    var kind = markerSpan.getAttribute('data-stx-kind');
    var cls = KIND_TO_CLASS[kind];
    if (!cls) return;

    var parent = markerSpan.closest(PARENT_SEL);
    if (!parent) return;

    // Idempotent fast-path: if the current parent already carries the kind
    // class, the heavy lifting was done on a previous pass.  Just make sure
    // the marker cell stays hidden (Streamlit reconciliation can re-render
    // the .stElementContainer subtree on rerun while keeping the marker).
    if (parent.classList.contains(cls)) {
      hideMarkerCell(markerSpan);
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

    // Kind-specific INLINE style overrides — set directly on the element with
    // !important so they beat Streamlit's own inline `display: flex` (which is
    // applied on every stVerticalBlock since 1.56+ and beats our external
    // !important rule on some Streamlit builds).  This makes the layout
    // independent of the CSS cascade.
    if (kind === 'grid') {
      var tpl = markerSpan.getAttribute('data-stx-grid-template') || '1fr';
      var g   = markerSpan.getAttribute('data-stx-grid-gap') || '0';
      parent.style.setProperty('display', 'grid', 'important');
      parent.style.setProperty('grid-template-columns', tpl, 'important');
      parent.style.setProperty('gap', g, 'important');
      parent.style.setProperty('align-items', 'stretch', 'important');
    } else if (kind === 'span') {
      parent.style.setProperty('display', 'flex', 'important');
      parent.style.setProperty('flex-direction', 'row', 'important');
      parent.style.setProperty('white-space', 'pre', 'important');
    } else if (kind === 'list-item') {
      parent.style.setProperty('display', 'flex', 'important');
      parent.style.setProperty('flex-direction', 'row', 'important');
      parent.style.setProperty('align-items', 'baseline', 'important');
      parent.style.setProperty('gap', '0.5rem', 'important');
    } else if (kind === 'zoom') {
      var z = markerSpan.getAttribute('data-stx-zoom-factor') || '1';
      parent.style.setProperty('zoom', z, 'important');
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
    hideMarkerCell(markerSpan);
  }

  function scan(root) {
    // Walk every marker on every pass — applyMarker is idempotent and uses
    // a fast-path when the parent already has the kind class.  We cannot
    // skip "previously processed" markers via a one-shot attribute because
    // Streamlit reconciliation may replace the parent stVerticalBlock on
    // rerun (settings change, paginated navigation) while reusing the
    // marker, which would otherwise leave the new parent un-classed.
    var scope = (root && root.querySelectorAll) ? root : hostDoc;
    var markers = scope.querySelectorAll('span.stx-marker');
    for (var i = 0; i < markers.length; i++) {
      applyMarker(markers[i]);
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
        if (node.matches && node.matches('span.stx-marker')) {
          applyMarker(node);
        }
        if (node.querySelectorAll) scan(node);
      }
    }
  });
  obs.observe(hostDoc.body, { childList: true, subtree: true });

  // Keep a reference on the parent window so we can introspect from devtools.
  hostWin.__stxMarkerObsHandle = obs;
})();
