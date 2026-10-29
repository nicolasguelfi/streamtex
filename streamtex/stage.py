"""Stage mode: the document in a fixed virtual screen scaled to the window (#105).

A document lays itself out against the browser window (``vw``, ``vh``, slide
breaks). An author who projects on 1920×1080 but works on a laptop never sees
the projector's layout. The stage renders the document inside an ``<iframe>``
of the chosen size — the one construct that gives a page a viewport of its
own — scaled to fit the window, centred, with black bands, like the device
mode of Chrome DevTools.

The stage is for the live app only (a link under the zoom controls); the HTML
export carries neither the link nor the script (0.7.81). It opens from the URL:
``?stage=1920x1080`` (``?stage=1`` takes the document's size). The tab then
shows only the stage; its frame loads the same URL without ``stage`` (plus
``stage_frame=1``, which hides the link inside), so ``?marker=`` and
``#anchor`` deep links pass through. "Exit stage" brings the tab back to the
page without the stage.

    st_book([...], stage=(1920, 1080))     # default; stage=False: no link
"""

import json
from urllib.parse import urlencode

DEFAULT_STAGE = (1920, 1080)
#: In the URL of the stage's own frame: the page inside shows no stage link.
FRAME_PARAM = "stage_frame"
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
    return "?" + urlencode({**{k: v for k, v in params.items() if k not in ("stage", FRAME_PARAM)},
                            "stage": f"{size[0]}x{size[1]}"}, doseq=True)


# The stage: called with the window to turn into a stage. It does nothing in
# a framed document (the stage's own frame) or a second time.
_STAGE_JS = r"""
function stxStage(win, w, h) {
  var doc = win.document;
  if (win.self !== win.top || doc.getElementById('stx-stage')) return;
  var url = new win.URL(win.location.href);
  url.searchParams.delete('stage');
  var inside = new win.URL(url.href);
  inside.searchParams.set('stage_frame', '1');
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
    '#stx-stage .stx-stage-bar button, #stx-stage .stx-stage-bar a { font: inherit; color: inherit; background: none;' +
    ' border: 1px solid #777; text-decoration: none;' +
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
  frame.src = inside.href;
  box.appendChild(frame);
  var bar = doc.createElement('div');
  bar.className = 'stx-stage-bar';
  var readout = doc.createElement('span');
  var full = doc.createElement('button');
  full.type = 'button';
  full.textContent = 'Full screen';
  // A link of the page itself: in the live app this script runs in a sandboxed
  // component frame, which may not navigate the tab (location.replace is refused).
  var exit = doc.createElement('a');
  exit.href = url.href;
  exit.setAttribute('role', 'button');
  exit.textContent = 'Exit stage';
  exit.title = 'Back to the page without the stage';
  bar.appendChild(readout);
  bar.appendChild(full);
  bar.appendChild(exit);
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
