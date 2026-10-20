/* StreamTeX video stage — st_video(theater=, fit=, fullscreen=) (#56).
 *
 * One script for the live app (mounted with the marker runtime) and the
 * HTML export (inlined once when the page has a staged video).
 *
 * A staged video has a marker <span class="stx-video-marker"
 * data-stx-video="slide|window|" data-stx-fit="contain|cover"
 * data-stx-fs="0|1" data-stx-loop="0|1">, and a close button.
 *   - export: the marker sits in its box <div class="stx-vbox">, in a slot;
 *   - live: the marker is rendered by st.markdown inside the st.container
 *     that also holds st.video; that container becomes the box.
 *
 * theater="slide": the box fills the screen height in the flow (CSS only).
 * theater="window": the box covers the window while its slide is on screen;
 *   the close button or Esc closes it; leaving the slide closes it and pauses
 *   the video; coming back opens it again.
 * fullscreen: the first Play (a click, the gesture browsers require) asks for
 *   fullscreen; at the end the video leaves it, unless it loops.
 */
(function () {
  var win = window;
  var doc = win.document;
  if (win.__stxVideo) { win.__stxVideo.scan(); return; }

  var CSS = [
    '.stx-vbox video, .stx-vbox iframe { object-fit: contain; }',
    '.stx-vbox.stx-fit-cover video { object-fit: cover; }',
    '.stx-vbox.stx-theater-slide { background: #000; }',
    '.stx-vbox.stx-theater-slide video, .stx-vbox.stx-theater-slide iframe {',
    '  display: block; width: 100% !important; max-width: 100% !important;',
    '  height: calc(100vh / var(--stx-z, 1)) !important; }',
    '.stx-vbox.stx-theater-window.stx-open { position: fixed !important; inset: 0 !important;',
    '  z-index: 999990 !important; background: #000; margin: 0 !important; padding: 0 !important;',
    '  width: calc(100vw / var(--stx-z, 1)) !important; max-width: none !important;',
    '  height: calc(100vh / var(--stx-z, 1)) !important;',
    '  display: flex !important; align-items: center; justify-content: center; }',
    '.stx-vbox.stx-theater-window.stx-open > * { width: 100% !important; max-width: none !important; }',
    '.stx-vbox.stx-theater-window.stx-open video, .stx-vbox.stx-theater-window.stx-open iframe {',
    '  display: block; width: calc(100vw / var(--stx-z, 1)) !important; max-width: none !important;',
    '  height: calc(100vh / var(--stx-z, 1)) !important; }',
    '.stx-video-open [data-testid="stSidebar"], .stx-video-open [data-testid="stHeader"],',
    '.stx-video-open .stx-export-sidebar, .stx-video-open .stx-sidebar-toggle { visibility: hidden !important; }',
    '.stx-vbox-close { display: none; }',
    '.stx-vbox.stx-open .stx-vbox-close { display: block; position: fixed; top: 12px; right: 16px;',
    '  z-index: 999991; width: 40px; height: 40px; border: 0; border-radius: 50%;',
    '  background: rgba(0,0,0,.55); color: #fff; font: 26px/40px sans-serif; cursor: pointer; }',
    '@media print { .stx-vbox.stx-theater-window.stx-open { position: static !important;',
    '  width: auto !important; height: auto !important; } .stx-vbox-close { display: none !important; } }'
  ].join('\n');

  function addStyle() {
    if (doc.getElementById('stx-video-css')) return;
    var s = doc.createElement('style');
    s.id = 'stx-video-css';
    s.textContent = CSS;
    (doc.head || doc.documentElement).appendChild(s);
  }

  var windows = [];

  // A zoomed page (the view zoom, the export's zoom) scales vw / vh inside
  // it: the box divides by the zoom it sits under to fill the screen.
  function fitZoom(box) {
    var z = box.parentElement && box.parentElement.currentCSSZoom;
    if (z && Math.abs(z - 1) > 0.001) box.style.setProperty('--stx-z', String(z));
    else box.style.removeProperty('--stx-z');
  }

  function boxOf(marker) {
    var box = marker.closest('.stx-vbox');
    if (box) return box;                                   // export
    box = marker.closest('[data-testid="stVerticalBlock"]');   // live: the st.container
    var cell = marker.closest('[data-testid="stElementContainer"]');
    if (cell) { cell.style.height = '0'; cell.style.minHeight = '0'; cell.style.overflow = 'visible'; }
    if (box) box.classList.add('stx-vbox');
    return box;
  }

  function wireFullscreen(box, loop) {
    var done = false;
    box.addEventListener('play', function (e) {
      var v = e.target;
      if (done || !v || v.tagName !== 'VIDEO' || doc.fullscreenElement || !v.requestFullscreen) return;
      var p = v.requestFullscreen();
      if (p && p.then) p.then(function () { done = true; }, function () { /* no gesture: next Play */ });
      else done = true;
    }, true);
    if (!loop) {
      box.addEventListener('ended', function (e) {
        if (doc.fullscreenElement === e.target && doc.exitFullscreen) doc.exitFullscreen();
      }, true);
    }
  }

  function wireWindow(box, marker) {
    var slot = box.parentElement;                // stays in the flow where the video was
    var state = { box: box, closed: false };
    windows.push(state);
    function open() {
      if (state.closed) return;
      fitZoom(box);
      box.classList.add('stx-open');
      doc.documentElement.classList.add('stx-video-open');   // sidebars stop covering it
      var v = box.querySelector('video');                     // an autoplay video starts again
      if (v && v.autoplay && v.paused) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
    }
    function close(pause) {
      box.classList.remove('stx-open');
      if (!doc.querySelector('.stx-vbox.stx-open')) doc.documentElement.classList.remove('stx-video-open');
      if (pause) { var v = box.querySelector('video'); if (v && !v.paused) v.pause(); }
    }
    state.close = function () { state.closed = true; close(false); };
    var btn = marker.parentElement && marker.parentElement.querySelector('.stx-vbox-close');
    if (btn) btn.addEventListener('click', function (e) { e.preventDefault(); state.close(); });
    if (!slot || !('IntersectionObserver' in win)) { open(); return; }
    new win.IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) open();
        else { state.closed = false; close(true); }   // left the slide
      });
    }).observe(slot);
  }

  function setup(marker) {
    if (marker.__stxDone) return;
    var box = boxOf(marker);
    if (!box) return;
    marker.__stxDone = true;
    var mode = marker.getAttribute('data-stx-video') || '';
    fitZoom(box);
    box.classList.add('stx-fit-' + (marker.getAttribute('data-stx-fit') || 'contain'));
    if (mode) box.classList.add('stx-theater-' + mode);
    if (marker.getAttribute('data-stx-fs') === '1') wireFullscreen(box, marker.getAttribute('data-stx-loop') === '1');
    if (mode === 'window') wireWindow(box, marker);
  }

  function scan() {
    addStyle();
    var list = doc.querySelectorAll('.stx-video-marker');
    for (var i = 0; i < list.length; i++) setup(list[i]);
    var boxes = doc.querySelectorAll('.stx-vbox');
    for (var j = 0; j < boxes.length; j++) fitZoom(boxes[j]);
    // a page change (paginated view) removed an open video without closing it
    if (!doc.querySelector('.stx-vbox.stx-open')) doc.documentElement.classList.remove('stx-video-open');
    windows = windows.filter(function (st) { return st.box.isConnected; });
  }

  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    windows.forEach(function (s) { if (s.box.classList.contains('stx-open')) s.close(); });
  });

  win.__stxVideo = { scan: scan };
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', scan);
  else scan();
  if ('MutationObserver' in win) {
    var pending = false;
    new win.MutationObserver(function () {
      if (pending) return;
      pending = true;
      win.requestAnimationFrame(function () { pending = false; scan(); });
    }).observe(doc.documentElement, { childList: true, subtree: true });
  }
})();
