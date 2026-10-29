"""Stage mode: the document in a fixed virtual screen scaled to the window (#105).

A document lays itself out against the browser window (``vw``, ``vh``, slide
breaks). An author who projects on 1920×1080 but works on a laptop never sees
the projector's layout. The stage renders the document inside an ``<iframe>``
of the chosen size — the one construct that gives a page a viewport of its
own — scaled to fit the window, centred, with black bands, like the device
mode of Chrome DevTools.

The stage opens from the URL: ``?stage=1920x1080`` (``?stage=1`` takes the
document's size). The tab then shows only the stage; its frame loads the same
URL without ``stage``, so ``?marker=`` and ``#anchor`` deep links pass through.
The same script serves the live app (sidebar link under the zoom controls) and
the HTML export (sidebar link, same password cookie on a published site).

    st_book([...], stage=(1920, 1080))     # default; stage=False: no link
"""

import json
from urllib.parse import urlencode

DEFAULT_STAGE = (1920, 1080)
STAGE_KEY = "_stx_stage"
_MIN, _MAX = 100, 10000


def parse_stage(value) -> tuple[int, int] | None:
    """The stage size of ``st_book(stage=...)``: ``(w, h)``, ``[w, h]`` or ``"WxH"``.

    ``True`` gives 1920×1080; ``False`` or ``None`` turns the stage off.
    Raises ``ValueError`` on anything else, or a side outside 100–10000 px.
    """
    if value is None or value is False:
        return None
    if value is True:
        return DEFAULT_STAGE
    if isinstance(value, str):
        parts = value.lower().replace("×", "x").split("x")
    else:
        parts = list(value) if isinstance(value, (tuple, list)) else []
    try:
        w, h = (int(p) for p in parts)
    except (TypeError, ValueError):
        raise ValueError(f"stage: expected (width, height) or \"WxH\", not {value!r}") from None
    if not (_MIN <= w <= _MAX and _MIN <= h <= _MAX):
        raise ValueError(f"stage: {w}x{h} is outside {_MIN}-{_MAX} px")
    return w, h


def requested_stage(params: dict, default: tuple[int, int] | None) -> tuple[int, int] | None:
    """The size asked by ``?stage=`` (``WxH``, or any other value for *default*); None without it.

    The stage stays off when the document turned it off (*default* None).
    """
    raw = params.get("stage")
    if isinstance(raw, list):
        raw = raw[-1] if raw else None
    if raw is None or default is None:
        return None
    try:
        return parse_stage(raw)
    except ValueError:
        return default


def stage_href(params: dict, size: tuple[int, int]) -> str:
    """The relative link that opens the current URL (*params*) on the stage."""
    return "?" + urlencode({**{k: v for k, v in params.items() if k != "stage"},
                            "stage": f"{size[0]}x{size[1]}"}, doseq=True)


# The stage: called with the window to turn into a stage. It does nothing in
# a framed document (the stage's own frame) or a second time.
_STAGE_JS = r"""
function stxStage(win, w, h) {
  var doc = win.document;
  if (win.self !== win.top || doc.getElementById('stx-stage')) return;
  var url = new win.URL(win.location.href);
  url.searchParams.delete('stage');
  var css = doc.createElement('style');
  css.textContent =
    'html.stx-staged, html.stx-staged body { overflow: hidden !important; }' +
    '#stx-stage { position: fixed; inset: 0; z-index: 2147483647; background: #000; overflow: hidden; }' +
    '#stx-stage .stx-stage-box { position: absolute; left: 0; top: 0; transform-origin: 0 0; }' +
    '#stx-stage iframe { display: block; width: 100%; height: 100%; border: 0; background: #fff; }' +
    '#stx-stage .stx-stage-bar { position: absolute; top: 6px; right: 8px;' +
    ' display: flex; gap: 8px; align-items: center;' +
    ' font: 12px/1.2 system-ui, sans-serif; color: #ddd; background: rgba(40,40,40,.85); padding: 4px 8px;' +
    ' border-radius: 6px; opacity: .35; transition: opacity .15s; }' +
    '#stx-stage .stx-stage-bar:hover, #stx-stage .stx-stage-bar:focus-within { opacity: 1; }' +
    '#stx-stage .stx-stage-bar button { font: inherit; color: inherit; background: none; border: 1px solid #777;' +
    ' border-radius: 4px; padding: 1px 6px; cursor: pointer; }';
  doc.head.appendChild(css);
  var root = doc.createElement('div');
  root.id = 'stx-stage';
  var box = doc.createElement('div');
  box.className = 'stx-stage-box';
  box.style.width = w + 'px';
  box.style.height = h + 'px';
  var frame = doc.createElement('iframe');
  frame.title = 'Stage ' + w + '×' + h;
  frame.src = url.href;
  box.appendChild(frame);
  var bar = doc.createElement('div');
  bar.className = 'stx-stage-bar';
  var readout = doc.createElement('span');
  var full = doc.createElement('button');
  full.type = 'button';
  full.textContent = 'Full screen';
  bar.appendChild(readout);
  bar.appendChild(full);
  root.appendChild(box);
  root.appendChild(bar);
  doc.body.appendChild(root);
  doc.documentElement.classList.add('stx-staged');
  doc.title = '▣ ' + doc.title;
  function fit() {
    var iw = win.innerWidth, ih = win.innerHeight;
    var s = Math.min(iw / w, ih / h);
    box.style.transform = 'translate(' + (iw - w * s) / 2 + 'px,' + (ih - h * s) / 2 + 'px) scale(' + s + ')';
    readout.textContent = w + '×' + h + ' · ' + Math.round(s * 100) + ' %';
    root.dataset.scale = s;
  }
  function focusFrame() { try { frame.focus(); frame.contentWindow.focus(); } catch (e) {} }
  win.addEventListener('resize', fit);
  doc.addEventListener('fullscreenchange', function () {
    full.textContent = doc.fullscreenElement ? 'Exit full screen' : 'Full screen';
    fit();
    focusFrame();
  });
  full.addEventListener('click', function () {
    if (doc.fullscreenElement) doc.exitFullscreen();
    else if (root.requestFullscreen) root.requestFullscreen().catch(function () {});
  });
  frame.addEventListener('load', focusFrame);
  root.addEventListener('click', function (e) { if (e.target === root) focusFrame(); });
  fit();
}
"""


def stage_script() -> str:
    """The JavaScript of the stage: defines ``stxStage(win, w, h)``."""
    return _STAGE_JS


def export_stage_js(size: tuple[int, int]) -> str:
    """Script for an HTML export: the sidebar link keeps the current URL; ``?stage=`` opens the stage."""
    w, h = size
    return _STAGE_JS + (
        "(function () {\n"
        f"  var W = {w}, H = {h};\n"
        "  var link = document.getElementById('stx-stage-link');\n"
        "  if (link) link.addEventListener('click', function () {\n"
        "    var u = new URL(location.href); u.searchParams.set('stage', W + 'x' + H); link.href = u.href;\n"
        "  });\n"
        "  var raw = new URLSearchParams(location.search).get('stage');\n"
        "  if (raw === null) return;\n"
        "  var m = /^(\\d{3,5})[x\\u00d7](\\d{3,5})$/i.exec(raw);\n"
        "  if (m) { W = +m[1]; H = +m[2]; }\n"
        "  var go = function () { stxStage(window, W, H); };\n"
        "  if (document.body) go(); else document.addEventListener('DOMContentLoaded', go);\n"
        "})();\n")


def render_stage(size: tuple[int, int]) -> None:
    """Turn the live app's tab into the stage (the tab shows nothing else)."""
    import streamlit as st

    w, h = size
    js = _STAGE_JS + f"stxStage(window.parent, {json.dumps(w)}, {json.dumps(h)});"
    st.iframe(f"<script>{js}</script>", height=1)


def stage_link(params: dict, size: tuple[int, int], container=None) -> None:
    """The sidebar link that opens the current page on the stage, in a new tab."""
    import streamlit as st

    ctx = container if container is not None else st.sidebar
    ctx.link_button(f"Stage {size[0]}×{size[1]}", stage_href(params, size),
                    help="Open this document in a virtual screen of this size, "
                         "scaled to the window (as on the projector)",
                    width="stretch")
