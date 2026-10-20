/* StreamTeX countdown racks — st_countdown (#52).
 *
 * One script for the live app (mounted with the marker runtime) and the HTML
 * export (inlined once in a page that holds a rack). It brings every
 * rack of the page (.stx-cd with its data-stx-countdown JSON) to life:
 * state, one shared 250 ms tick, chain hand-over, buttons, alarms, bells,
 * double-click editing and digit fitting. A rack is found through the DOM
 * tree only (no ids, no key): the export holds every slide in one document.
 *
 * Chain mode: cards with an end (countdown, stopwatch or clock with a target)
 * are gates — one gate runs at a time, and its end starts the next unfinished
 * gate; cards with no end are free and run until paused. A stopwatch keeps
 * counting past its target (overtime stays readable); a clock target already
 * past hands over at once.
 */
(function () {
  var win = window, doc = win.document;
  if (win.__stxCountdown) { win.__stxCountdown.scan(); return; }

  var racks = [];
  // Card state lives here, not in the DOM: Streamlit replaces a rack's
  // element on every rerun, and the new one takes the old one's state over
  // (key: rack id + its rank among the racks of that id on the page).
  var STORE = {};
  function store(key, idx, init) {
    var r = STORE[key] = STORE[key] || {};
    return r[idx] = r[idx] || init;
  }
  var TRIM = {bell: 0.50, beep: 0.35, chime: 0.60, gong: 0.45};
  var PERIOD = {bell: 1.2, beep: 0.9, chime: 1.8, gong: 3.0};
  var BELL_ON = '🔔', BELL_OFF = '🔕';

  function pad(n) { return String(n).padStart(2, '0'); }
  function fmt(sec) { sec = Math.max(0, Math.floor(sec)); return pad(Math.floor(sec / 60)) + ':' + pad(sec % 60); }
  function hhmm(t) { var d = new Date(t); return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function parseMinutes(v) {           // "40" = 40 min, "40:30" = 40 min 30 s
    var m = String(v).trim().match(/^(\d{1,3})(?::([0-5]?\d))?$/);
    if (!m) return null;
    var s = parseInt(m[1], 10) * 60 + (m[2] ? parseInt(m[2], 10) : 0);
    return s > 0 ? s : null;
  }
  function parseHHMM(v) {
    var m = String(v).trim().match(/^([01]?\d|2[0-3]):([0-5]\d)$/);
    return m ? pad(parseInt(m[1], 10)) + ':' + m[2] : null;
  }

  // ── Audio: one AudioContext per page, unlocked by any click on a rack ──────
  function armAudio() {
    try {
      var C = win.AudioContext || win.webkitAudioContext;
      if (!C) return;
      var a = win.__stxCdAudio = win.__stxCdAudio || new C();
      if (a.state === 'suspended') a.resume();
      if (!a.__kicked) {                       // Safari / iOS: a muted buffer
        var src = a.createBufferSource();      // played inside the gesture
        src.buffer = a.createBuffer(1, 1, 22050);
        src.connect(a.destination); src.start(0);
        a.__kicked = true;
      }
    } catch (e) {}
  }
  function voice(a, out, type, freq, t0, atk, peak, decay) {
    var o = a.createOscillator(), g = a.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.linearRampToValueAtTime(peak, t0 + atk);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + atk + decay);
    o.connect(g); g.connect(out);
    o.start(t0); o.stop(t0 + atk + decay + 0.05);
  }
  function play(sp) {                          // a failure never stops a timer
    var a = win.__stxCdAudio;
    if (!sp || sp.vol <= 0 || !a) return;
    try {
      if (a.state === 'suspended') a.resume();
      if (a.state !== 'running') return;
      var t0 = a.currentTime + 0.02, master = a.createGain();
      master.gain.value = Math.pow(sp.vol, 1.6) * (TRIM[sp.sound] || 0.5);
      master.connect(a.destination);
      var per = PERIOD[sp.sound] || 1.2;
      var reps = sp.dur ? Math.min(60, Math.max(1, Math.ceil(sp.dur / per))) : 1;
      if (sp.dur) {
        master.gain.setValueAtTime(master.gain.value, t0 + sp.dur);
        master.gain.exponentialRampToValueAtTime(0.0001, t0 + sp.dur + 0.2);
      }
      for (var r = 0; r < reps; r++) {
        var tk = t0 + r * per, i;
        if (sp.sound === 'beep') {
          var lp = a.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 3000; lp.connect(master);
          for (i = 0; i < 3; i++) voice(a, lp, 'square', 1046.5, tk + i * 0.22, 0.01, 1.0, 0.12);
        } else if (sp.sound === 'chime') {
          var notes = [523.25, 659.25, 783.99];
          for (i = 0; i < notes.length; i++) {
            voice(a, master, 'triangle', notes[i], tk + i * 0.18, 0.01, 0.8, 1.2);
            voice(a, master, 'sine', notes[i] * 2, tk + i * 0.18, 0.01, 0.25, 0.9);
          }
        } else if (sp.sound === 'gong') {
          var lp2 = a.createBiquadFilter(); lp2.type = 'lowpass';
          lp2.frequency.setValueAtTime(1200, tk); lp2.frequency.exponentialRampToValueAtTime(300, tk + 2.5);
          lp2.connect(master);
          var gp = [1.0, 1.52, 2.01, 2.66, 3.22, 4.16];
          for (i = 0; i < gp.length; i++) voice(a, lp2, 'sine', 98 * gp[i], tk, 0.02, 0.9 / (1 + i * 0.4), 2.5);
        } else {
          var bp = [1.0, 2.0, 2.92, 4.07];
          for (i = 0; i < bp.length; i++) voice(a, master, 'sine', 660 * bp[i], tk, 0.005, 0.9 / (1 + i * 0.6), 0.9);
        }
      }
    } catch (e) {}
  }

  // ── Mute state per card, remembered in localStorage (best effort) ──────────
  function mutedKey(rack, i) { return 'stx-cd-muted-' + rack.id + '-' + i; }
  function isMuted(rack, i) {
    try { var v = win.localStorage.getItem(mutedKey(rack, i)); if (v !== null) return v === '1'; } catch (e) {}
    return rack.defaultMuted;
  }
  function setMuted(rack, i, m) { try { win.localStorage.setItem(mutedKey(rack, i), m ? '1' : '0'); } catch (e) {} }

  // ── Digits fill their card: measured, not estimated ────────────────────────
  function fit(card) {
    try {
      var root = card.el, d = card.digits;
      if (card.editing) return;
      var cs = win.getComputedStyle(root);
      var H = root.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      var W = root.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      if (!(H > 0) || !(W > 0)) return;
      var wlim = W * card.widthPct / 100 * 0.94;
      for (var it = 0; it < 3; it++) {
        var extra = 0;
        Array.prototype.forEach.call(root.children, function (ch) { if (ch !== d) extra += ch.offsetHeight; });
        var avail = Math.max(10, (H - extra) * 0.92);
        var cur = parseFloat(win.getComputedStyle(d).fontSize) || avail;
        var w = d.scrollWidth || 1;
        var next = Math.min(avail, cur * wlim / w);
        d.style.fontSize = next + 'px';
        if (Math.abs(next - cur) < 0.5) break;
      }
    } catch (e) {}
  }

  // ── Cards ───────────────────────────────────────────────────────────────────
  function makeCard(rack, idx, spec, el) {
    var card = {rack: rack, idx: idx, spec: spec, el: el, kind: spec.kind,
                digits: el.querySelector('.stx-cd-digits'), at: el.querySelector('.stx-cd-at'),
                alarm: spec.alarm, editing: false,
                widthPct: spec.width || rack.width};
    function cls(running, done) {
      el.classList.toggle('stx-cd-running', !!running);
      el.classList.toggle('stx-cd-done', !!done);
    }
    function ring() { if (card.alarm && !isMuted(rack, idx)) play(card.alarm); }
    function pauseOtherGates() {
      if (rack.mode !== 'chain' || card.isFree()) return;
      rack.cards.forEach(function (c) { if (c !== card && !c.isFree()) c.pause(); });
    }
    function ended() { ring(); rack.relay(idx); }

    if (card.kind === 'countdown') {
      var total = spec.total, S = store(rack.key, idx, {remaining: total, endAt: null});
      card.isFree = function () { return false; };
      card.isDone = function () { return S.remaining <= 0; };
      card.paint = function () {
        if (card.editing) return;
        if (card.isDone()) { card.digits.textContent = fmt(total); cls(false, true); card.at.textContent = ''; return; }
        card.digits.textContent = fmt(Math.ceil(S.remaining));
        cls(S.endAt !== null, false);
        card.at.textContent = S.endAt !== null ? rack.endsAt + ' ' + hhmm(S.endAt) : '';
      };
      card.tick = function () {
        if (S.endAt === null) return;
        S.remaining = (S.endAt - Date.now()) / 1000;
        if (S.remaining <= 0) { S.remaining = 0; S.endAt = null; card.paint(); ended(); return; }
        card.paint();
      };
      card.start = function () {
        if (card.isDone() || S.endAt !== null) return;
        pauseOtherGates();
        S.endAt = Date.now() + S.remaining * 1000;
        card.paint();
      };
      card.pause = function () {
        if (S.endAt === null) return;
        S.remaining = Math.max(0, (S.endAt - Date.now()) / 1000);
        S.endAt = null;
        if (card.isDone()) ring();                // paused inside the last tick
        card.paint();
      };
      card.reset = function () { S.remaining = total; S.endAt = null; card.paint(); };
      card.editValue = function () { return fmt(Math.ceil(S.remaining > 0 ? S.remaining : total)); };
      card.applyEdit = function (v, wasRunning) {
        var s = parseMinutes(v);
        if (s !== null) S.remaining = s;            // a finished card comes back to life
        card.paint();
        if (wasRunning && S.remaining > 0) card.start();
      };
      card.running = function () { return S.endAt !== null; };
    } else if (card.kind === 'stopwatch') {
      var W = store(rack.key, idx, {target: spec.total, elapsed: 0, startAt: null, fired: false});
      card.isFree = function () { return !(W.target > 0); };
      card.isDone = function () { return W.target > 0 ? W.fired : false; };
      card.paint = function () {
        if (card.editing) return;
        card.digits.textContent = fmt(W.elapsed);
        cls(W.startAt !== null && !(W.target > 0 && W.fired), W.target > 0 && W.fired);
        card.at.textContent = W.startAt !== null ? rack.since + ' ' + hhmm(W.startAt) : '';
      };
      card.tick = function () {
        if (W.startAt === null) return;
        W.elapsed = (Date.now() - W.startAt) / 1000;
        if (W.target > 0 && !W.fired && W.elapsed >= W.target) { W.fired = true; card.paint(); ended(); return; }
        card.paint();                             // overtime keeps counting
      };
      card.start = function () {
        if (W.startAt !== null) return;
        pauseOtherGates();
        W.startAt = Date.now() - W.elapsed * 1000;
        card.paint();
      };
      card.pause = function () {
        if (W.startAt === null) return;
        W.elapsed = Math.max(0, (Date.now() - W.startAt) / 1000);
        W.startAt = null; card.paint();
      };
      card.reset = function () {
        W.elapsed = 0; W.startAt = null; W.fired = false; W.target = spec.total; card.paint();
      };
      card.editValue = function () { return W.target > 0 ? fmt(W.target) : ''; };
      card.applyEdit = function (v) {               // the target, in minutes
        if (String(v).trim() === '') { W.target = 0; W.fired = false; }
        else {
          var s = parseMinutes(v);
          if (s !== null) { W.target = s; W.fired = W.startAt === null && W.elapsed >= W.target; }
        }
        card.paint();
      };
      card.running = function () { return W.startAt !== null; };
    } else {                                        // clock
      var K = store(rack.key, idx, {ttime: spec.ttime, armed: false, fired: false}), FMT = null;
      try {
        FMT = new Intl.DateTimeFormat('en-GB', {timeZone: spec.tz, hour12: false,
          hour: '2-digit', minute: '2-digit', second: '2-digit'});
      } catch (e) {}
      var now = function () {
        try { if (FMT) return FMT.format(new Date()); } catch (e) {}
        return new Date().toTimeString().slice(0, 8);
      };
      var footer = function () { card.at.textContent = spec.city + (K.ttime ? ' · → ' + K.ttime : ''); };
      card.isFree = function () { return !K.ttime; };
      card.isDone = function () { return K.ttime ? K.fired : false; };
      card.paint = function () {
        if (card.editing) return;
        card.digits.textContent = now();
        cls(false, !!K.ttime && K.fired);
      };
      card.tick = function () {
        card.paint();
        if (K.ttime && K.armed && !K.fired && now().slice(0, 5) >= K.ttime) { K.fired = true; card.paint(); ended(); }
      };
      card.start = function () { if (K.ttime && !K.armed) { K.armed = true; card.tick(); } };
      card.pause = function () {};
      card.reset = function () { K.armed = false; K.fired = false; K.ttime = spec.ttime; footer(); card.paint(); };
      card.editValue = function () { return K.ttime || ''; };
      card.applyEdit = function (v) {               // the target, HH:MM
        if (String(v).trim() === '') { K.ttime = null; K.fired = false; K.armed = false; }
        else { var t = parseHHMM(v); if (t) { K.ttime = t; K.fired = false; } }
        footer(); card.paint();
      };
      card.running = function () { return false; };
      footer();
    }

    // Double-click the digits: edit the value; Enter / blur applies, Escape cancels.
    card.digits.addEventListener('dblclick', function () {
      if (card.editing) return;
      var wasRunning = card.kind === 'countdown' && card.running();
      if (wasRunning) card.pause();
      card.editing = true;
      card.digits.textContent = '';
      var inp = doc.createElement('input');
      inp.className = 'stx-cd-edit';
      inp.value = card.editValue();
      inp.setAttribute('aria-label', card.kind === 'countdown' ? 'minutes or MM:SS' :
                       card.kind === 'stopwatch' ? 'target minutes' : 'target HH:MM');
      card.digits.appendChild(inp);
      inp.focus(); inp.select();
      function done(apply) {
        if (!card.editing) return;
        card.editing = false;
        var v = inp.value;
        if (apply) card.applyEdit(v, wasRunning);
        else { card.paint(); if (wasRunning) card.start(); }
        fit(card);
      }
      inp.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter') done(true);
        else if (ev.key === 'Escape') done(false);
        ev.stopPropagation();
      });
      inp.addEventListener('blur', function () { done(true); });
    });

    function on(sel, fn) { var b = el.querySelector(sel); if (b) b.addEventListener('click', fn); }
    on('.stx-cd-go', function () { card.start(); });
    on('.stx-cd-halt', function () { card.pause(); });
    on('.stx-cd-zero', function () { card.reset(); });
    var bell = el.querySelector('.stx-cd-bell');
    card.paintBell = function () {
      if (!bell) return;
      var m = isMuted(rack, idx);
      bell.textContent = m ? BELL_OFF : BELL_ON;
      bell.style.opacity = m ? '0.55' : '1';
    };
    if (bell) bell.addEventListener('click', function () {
      var m = !isMuted(rack, idx);
      setMuted(rack, idx, m);
      card.paintBell();
      rack.paintBell();
      if (!m) { armAudio(); setTimeout(function () { play({sound: card.alarm.sound, vol: Math.min(card.alarm.vol, 0.35)}); }, 60); }
    });
    card.paintBell();
    return card;
  }

  // ── Racks ───────────────────────────────────────────────────────────────────
  function hydrate(el) {
    var data;
    try { data = JSON.parse(el.getAttribute('data-stx-countdown')); } catch (e) { return; }
    var same = Array.prototype.filter.call(doc.querySelectorAll('.stx-cd[data-stx-countdown]'),
      function (e) { try { return JSON.parse(e.getAttribute('data-stx-countdown')).id === data.id; } catch (x) { return false; } });
    var rack = {el: el, id: data.id, key: data.id + '#' + same.indexOf(el), mode: data.mode, endsAt: data.endsAt || 'ends at',
                since: data.since || 'since', width: data.width || 80,
                defaultMuted: data.muted !== false, cards: []};
    var cardEls = el.querySelectorAll('[data-stx-cd-card]');
    data.cards.forEach(function (spec, i) { if (cardEls[i]) rack.cards.push(makeCard(rack, i, spec, cardEls[i])); });

    rack.relay = function (idx) {                  // chain: the next gate starts
      if (rack.mode !== 'chain') return;
      for (var k = idx + 1; k < rack.cards.length; k++) {
        var c = rack.cards[k];
        if (c.isFree()) { c.start(); continue; }
        if (!c.isDone()) { c.start(); break; }
      }
    };
    rack.startAll = function () {
      if (rack.mode === 'parallel') { rack.cards.forEach(function (c) { if (!c.isDone()) c.start(); }); return; }
      for (var k = 0; k < rack.cards.length; k++) {
        var c = rack.cards[k];
        if (c.isFree()) { c.start(); continue; }
        if (!c.isDone()) { c.start(); break; }
      }
    };
    var alarmed = rack.cards.filter(function (c) { return c.alarm; });
    var gbell = el.querySelector('.stx-cd-all-bell');
    function allArmed() { return alarmed.every(function (c) { return !isMuted(rack, c.idx); }); }
    rack.paintBell = function () {
      if (!gbell) return;
      var on = allArmed();
      gbell.textContent = on ? BELL_ON : BELL_OFF;
      gbell.style.opacity = on ? '1' : '0.55';
    };
    if (gbell) gbell.addEventListener('click', function () {
      var arm = !allArmed();
      alarmed.forEach(function (c) { setMuted(rack, c.idx, !arm); c.paintBell(); });
      rack.paintBell();
      if (arm && alarmed.length) {
        armAudio();
        var a0 = alarmed[0].alarm;
        setTimeout(function () { play({sound: a0.sound, vol: Math.min(a0.vol, 0.35)}); }, 60);
      }
    });
    rack.paintBell();
    var go = el.querySelector('.stx-cd-all-start'), zero = el.querySelector('.stx-cd-all-reset');
    if (go) go.addEventListener('click', rack.startAll);
    if (zero) zero.addEventListener('click', function () { rack.cards.forEach(function (c) { c.reset(); }); });
    if (alarmed.length) el.addEventListener('click', armAudio);   // the gesture unlocks audio

    rack.cards.forEach(function (c) { c.paint(); });
    rack.cards.forEach(function (c) { fit(c); });
    try {
      if (win.ResizeObserver) {
        var ro = new win.ResizeObserver(function (entries) {
          var seen = [];
          entries.forEach(function (en) {
            var cardEl = en.target.closest('[data-stx-cd-card]');
            rack.cards.forEach(function (c) { if (c.el === cardEl && seen.indexOf(c) < 0) seen.push(c); });
          });
          seen.forEach(fit);
        });
        rack.cards.forEach(function (c) {
          ro.observe(c.el);
          Array.prototype.forEach.call(c.el.children, function (ch) { if (ch !== c.digits) ro.observe(ch); });
        });
      }
    } catch (e) {}
    try { if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(function () { rack.cards.forEach(fit); }); } catch (e) {}
    [100, 400, 1000, 2000].forEach(function (d) { setTimeout(function () { rack.cards.forEach(fit); }, d); });

    var started = store(rack.key, 'auto', {done: false});
    if (data.autostart && !started.done) {         // a break screen: starts when first shown
      if ('IntersectionObserver' in win) {
        var io = new win.IntersectionObserver(function (entries) {
          if (entries.some(function (en) { return en.isIntersecting; })) {
            io.disconnect(); if (!started.done) { started.done = true; rack.startAll(); }
          }
        });
        io.observe(el);
      } else { started.done = true; rack.startAll(); }
    }
    racks.push(rack);
  }

  function scan() {
    var list = doc.querySelectorAll('.stx-cd[data-stx-countdown]');
    for (var i = 0; i < list.length; i++) {
      if (!list[i].__stxCd) { list[i].__stxCd = true; hydrate(list[i]); }
    }
  }

  setInterval(function () {                         // one tick for every rack
    racks = racks.filter(function (r) { return r.el.isConnected; });
    racks.forEach(function (r) { r.cards.forEach(function (c) { try { c.tick(); } catch (e) {} }); });
  }, 250);

  win.__stxCountdown = {scan: scan};
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', scan); else scan();
  if ('MutationObserver' in win) {
    var pending = false;
    new win.MutationObserver(function () {
      if (pending) return;
      pending = true;
      win.requestAnimationFrame(function () { pending = false; scan(); });
    }).observe(doc.documentElement, {childList: true, subtree: true});
  }
})();
