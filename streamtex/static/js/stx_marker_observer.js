/* StreamTeX marker observer — single-source-of-truth per-kind specs.
 *
 * Injected as a Streamlit components.v2 component with
 * isolate_styles=False, so the script runs INLINE in the host page (no
 * iframe).  In that mode `window.parent === window`, but we keep the
 * `hostWin/hostDoc` indirection for compatibility with the legacy
 * components.v1.html deployment (which ran the script inside a
 * 0-pixel iframe and reached the host page via `window.parent`).
 *
 * When a sentinel <span class="stx-marker" data-stx-kind="..."
 *   data-stx-uid="..." data-stx-*="..." style="display:none"></span>
 * appears anywhere in the parent Streamlit page, this observer applies
 * the spec for that kind to the nearest [data-testid="stVerticalBlock"]
 * ancestor.  Each spec declares:
 *
 *     cls               : the class to add (always present)
 *     inlineStyles(span): map of inline CSS props to set with !important
 *     booleanModifiers  : { dataAttrName: modifierClass } — class added
 *                         when the marker has the attribute
 *
 * applyMarker WRITES from the spec.  clearMarker READS the SAME spec to
 * undo every write when the marker is detached.  Adding a new kind, or
 * a new inline property on an existing kind, only requires editing
 * KIND_SPECS — both code paths consume it identically, so drift between
 * them is impossible by construction.  This invariant is what guarantees
 * the 0.6.27 paginated bleed-through fix can't silently regress.
 *
 * This entire system is the marker-runtime replacement for the legacy
 * `div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{uid})`
 * pattern.  See documentation/maintenance/freeze-has/fix-plan.md for context.
 */
(function () {
  'use strict';

  // Host DOM access.  Under components.v2 + isolate_styles=False the script
  // is inline so `window.parent === window`; under the legacy v1 iframe
  // `window.parent` is the host page.  Both forms resolve to the same
  // hostWin/hostDoc here.
  var hostWin = window.parent || window;
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

  // -------------------------------------------------------------------------
  // KIND_SPECS — single source of truth for per-kind marker behavior.
  //
  // Both applyMarker (DOM additions) and clearMarker (DOM removals) consume
  // entries from this table.  Because the additive and retractive code paths
  // share the same declarations, an inline property written by applyMarker
  // cannot silently slip past clearMarker — the cause of the paginated
  // bleed-through bug fixed in 0.6.27.
  //
  // Schema:
  //   cls               (string, required)
  //       Class added to the marker's stVerticalBlock ancestor.
  //   inlineStyles      (function(span) -> { prop: value }, optional)
  //       CSS properties applyMarker sets on the ancestor with !important.
  //       clearMarker calls the same function on the detached span and
  //       uses only the returned KEYS to strip — the values may be
  //       degenerate when attributes are no longer readable, but the keys
  //       are always the same set.
  //   booleanModifiers  ({ attrName: modifierClass }, optional)
  //       For every attrName present on the marker span, applyMarker adds
  //       modifierClass to the ancestor.  clearMarker removes every listed
  //       modifierClass unconditionally (applyMarker only adds, so an
  //       unconditional symmetric removal is correct).
  //
  // Adding a new kind: append one entry below.  No other change required.
  var KIND_SPECS = {
    'block':     { cls: 'stx-block' },
    'span':      {
      cls: 'stx-span',
      inlineStyles: function () {
        return {
          'display': 'flex',
          'flex-direction': 'row',
          'white-space': 'pre'
        };
      }
    },
    'grid':      {
      cls: 'stx-grid',
      inlineStyles: function (span) {
        return {
          'display': 'grid',
          'grid-template-columns': span.getAttribute('data-stx-grid-template') || '1fr',
          'gap': span.getAttribute('data-stx-grid-gap') || '0',
          'align-items': 'stretch'
        };
      }
    },
    'list':      { cls: 'stx-list' },
    'list-item': {
      cls: 'stx-list-item',
      inlineStyles: function () {
        return {
          'display': 'flex',
          'flex-direction': 'row',
          'align-items': 'baseline',
          'gap': '0.5rem'
        };
      },
      booleanModifiers: { 'data-stx-ordered': 'stx-list-item--ordered' }
    },
    'zoom':      {
      cls: 'stx-zoom',
      inlineStyles: function (span) {
        return { 'zoom': span.getAttribute('data-stx-zoom-factor') || '1' };
      }
    },
    'md-big':    { cls: 'stx-md-big' }
  };

  function cssEscapeUid(uid) {
    if (hostWin.CSS && hostWin.CSS.escape) return hostWin.CSS.escape(uid);
    // Defensive fallback — streamtex generate_key() produces safe ids
    // (kind-digits) so the regex covers everything we ever pass.
    return String(uid).replace(/[^A-Za-z0-9_-]/g, '\\$&');
  }

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

  function forwardCustomProps(markerSpan, parent) {
    // Forward every data-stx-* attribute (except `kind`) onto the parent
    // as a CSS custom property: `data-stx-foo-bar="x"` -> `--stx-foo-bar: x;`.
    // Per-instance stylesheets can then read the values without per-instance
    // CSS injection.
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
  }

  function applyMarker(markerSpan) {
    // Fully idempotent: every write is guarded by a read so re-running
    // applyMarker on an already-applied marker fires no mutations.  This is
    // essential because the MutationObserver watches attribute changes
    // (Streamlit's reconciliation strips our class/uid/style on rerun),
    // and a non-idempotent applyMarker would loop on itself indefinitely.
    var kind = markerSpan.getAttribute('data-stx-kind');
    var spec = KIND_SPECS[kind];
    if (!spec) return;

    var parent = markerSpan.closest(PARENT_SEL);
    if (!parent) return;

    // 1. Kind class.
    if (!parent.classList.contains(spec.cls)) {
      parent.classList.add(spec.cls);
    }

    // 2. Forward data-stx-* attrs as CSS custom properties on the parent.
    forwardCustomProps(markerSpan, parent);

    // 3. Kind-specific inline styles — declared once in KIND_SPECS so the
    //    write site here and the strip site in clearMarker stay in lockstep.
    if (spec.inlineStyles) {
      var styles = spec.inlineStyles(markerSpan);
      for (var p in styles) {
        if (Object.prototype.hasOwnProperty.call(styles, p)) {
          setInlineImportant(parent, p, styles[p]);
        }
      }
    }

    // 4. Per-instance kind-prefixed uid attribute (per-instance stylesheet
    //    selectors target `[data-stx-{kind}-uid="…"]`).
    var uid = markerSpan.getAttribute('data-stx-uid');
    if (uid) {
      var uidAttr = 'data-stx-' + kind + '-uid';
      if (parent.getAttribute(uidAttr) !== uid) {
        parent.setAttribute(uidAttr, uid);
      }
    }

    // 5. Boolean modifiers (presence-only data attribute -> modifier class),
    //    also declared in KIND_SPECS so clearMarker can find them.
    if (spec.booleanModifiers) {
      for (var attrName in spec.booleanModifiers) {
        if (!Object.prototype.hasOwnProperty.call(spec.booleanModifiers, attrName)) continue;
        var modCls = spec.booleanModifiers[attrName];
        if (markerSpan.hasAttribute(attrName)) {
          if (!parent.classList.contains(modCls)) {
            parent.classList.add(modCls);
          }
        }
      }
    }

    // 6. Hide the marker's own element-container so it doesn't take a
    //    grid/flex slot.
    hideMarkerCell(markerSpan);
  }

  // When a marker span is detached from the DOM (e.g. Streamlit unmounts
  // the slide it belonged to during paginated navigation), the parent
  // stVerticalBlock — if React preserved it for some other reason — keeps
  // the class, the kind-prefixed uid attribute, the CSS custom properties
  // and the inline layout styles applyMarker wrote on it.  When a new
  // slide is then rendered that REUSES the same DOM node for a different
  // construct, those stale styles bleed through.
  //
  // clearMarker reverses applyMarker by reading the SAME KIND_SPECS entry
  // applyMarker consumed — so the two stay in lockstep by construction.
  // A "marker with same uid still attached?" guard makes the operation
  // safe under React move-style reconciliation (a detach + re-attach in
  // the same batch leaves the parent state untouched).
  function clearMarker(removedSpan) {
    if (!removedSpan || !removedSpan.getAttribute) return;
    var kind = removedSpan.getAttribute('data-stx-kind');
    var uid  = removedSpan.getAttribute('data-stx-uid');
    if (!kind || !uid) return;
    var spec = KIND_SPECS[kind];
    if (!spec) return;
    var uidAttr = 'data-stx-' + kind + '-uid';
    var sel = '[' + uidAttr + '="' + cssEscapeUid(uid) + '"]';
    var parent = hostDoc.querySelector(sel);
    if (!parent) return;
    // If a marker with the same uid is still attached anywhere inside the
    // parent, the "removal" was actually a re-render — leave the parent
    // state untouched and let the freshly-added marker re-apply.
    var still = parent.querySelector(
      'span.stx-marker[data-stx-uid="' + cssEscapeUid(uid) + '"]'
    );
    if (still) return;

    // 1. Strip the kind class.
    if (parent.classList.contains(spec.cls)) {
      parent.classList.remove(spec.cls);
    }

    // 2. Strip every boolean-modifier class declared for this kind.
    //    applyMarker only adds modifiers (never removes), so unconditional
    //    removal here is the symmetric undo.
    if (spec.booleanModifiers) {
      for (var modAttr in spec.booleanModifiers) {
        if (!Object.prototype.hasOwnProperty.call(spec.booleanModifiers, modAttr)) continue;
        var modCls = spec.booleanModifiers[modAttr];
        if (parent.classList.contains(modCls)) {
          parent.classList.remove(modCls);
        }
      }
    }

    // 3. Strip the kind-prefixed uid attribute.
    if (parent.hasAttribute(uidAttr)) parent.removeAttribute(uidAttr);

    // 4. Strip every CSS custom property we forwarded from data-stx-* attrs.
    var attrs = removedSpan.attributes;
    if (attrs) {
      for (var i = 0; i < attrs.length; i++) {
        var a = attrs[i];
        if (a.name === 'data-stx-kind' || a.name === 'data-stx-uid') continue;
        if (a.name.indexOf('data-stx-') !== 0) continue;
        var cssVar = '--' + a.name.slice('data-'.length);
        parent.style.removeProperty(cssVar);
      }
    }

    // 5. Strip the inline layout properties.  We discover the property
    //    KEYS by calling the SAME spec.inlineStyles applyMarker called;
    //    the returned values are unused here — only the keys matter.
    //    Driving both code paths from the one function is what makes
    //    drift impossible.
    if (spec.inlineStyles) {
      var styles = spec.inlineStyles(removedSpan);
      for (var p in styles) {
        if (Object.prototype.hasOwnProperty.call(styles, p)) {
          parent.style.removeProperty(p);
        }
      }
    }
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
  //   - childList.addedNodes:   any span.stx-marker (the node itself or a
  //                             descendant of an added subtree) is applied.
  //   - childList.removedNodes: any detached span.stx-marker is run through
  //                             clearMarker (AFTER additions so a re-added
  //                             marker's "still attached?" guard sees the
  //                             new instance).
  //   - attributes on a stVerticalBlock parent: Streamlit reconciliation
  //                             may have stripped our class/uid/style.
  //                             Find the marker inside that parent and
  //                             re-apply.
  //
  // We dedupe targets via Sets so a single batch with many mutations on
  // the same parent triggers at most one applyMarker per parent.  This
  // bounds the per-batch cost to O(unique_targets) instead of the
  // previous O(all_markers × batches) full-document scans.
  //
  // applyMarker is fully idempotent (no-op when state already matches),
  // so re-running it on a parent that is already in the correct state
  // does not trigger a feedback loop through the observer.
  var pendingBatch = [];
  var pendingScheduled = false;

  function handleBatch(batch) {
    var addedMarkers = (typeof Set === 'function') ? new Set() : null;
    var dirtyParents = (typeof Set === 'function') ? new Set() : null;
    // removedMarkers must be an *Array* (preserve insertion order) so a
    // moved marker that is removed then re-added in the same batch keeps
    // the natural ordering for the "still attached?" check.
    var removedMarkers = [];
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
        var removed = rec.removedNodes;
        for (var rj = 0; rj < removed.length; rj++) {
          var rn = removed[rj];
          if (!rn || rn.nodeType !== 1) continue;
          // Caveat: ``rn.matches`` exists even on detached subtrees but
          // ``rn.querySelectorAll`` only finds elements that were part
          // of the removed subtree at the time of detachment.  Both
          // suffice for clearMarker because it reads the data attributes
          // directly on the removed span.
          if (rn.matches && rn.matches('span.stx-marker')) {
            removedMarkers.push(rn);
          }
          if (rn.querySelectorAll) {
            var rsub = rn.querySelectorAll('span.stx-marker');
            for (var rk = 0; rk < rsub.length; rk++) {
              removedMarkers.push(rsub[rk]);
            }
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
      for (var ai = 0; ai < addedArr.length; ai++) processMarker(addedArr[ai]);
      for (var pi = 0; pi < dirtyArr.length; pi++) processParent(dirtyArr[pi]);
    }
    // Process removals AFTER additions so a "moved" marker (removed
    // then re-added in the same batch) has its new instance in the DOM
    // when clearMarker's ``still attached?`` guard runs.
    for (var r = 0; r < removedMarkers.length; r++) {
      clearMarker(removedMarkers[r]);
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

  // Keep references on the parent window for devtools introspection.
  hostWin.__stxMarkerObsHandle = obs;
  hostWin.__stxMarkerSpecs = KIND_SPECS;
})();
