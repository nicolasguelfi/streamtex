"""st_countdown — a grid of countdown, stopwatch and clock cards on a slide (#52).

``st_countdown(steps, mode)`` draws one *rack*: global buttons above a grid
of cards. In ``"chain"`` mode one card runs at a time and hands over to the
next; in ``"parallel"`` mode every card runs on its own. Everything happens in
the browser, the same way in the live app and in the HTML export.

Python validates the steps, then writes the rack as HTML: the idle state
(labels, full durations) is drawn here, so a PDF or a page without scripts
shows it. ``static/js/stx_countdown.js`` brings every rack of the page to
life: it is mounted with the marker runtime in the app and inlined once in an
export page that holds a rack. The rack carries its settings in one
``data-stx-countdown`` attribute (JSON); nothing textual reaches the script
any other way.

Spec: ticket #52 (consolidated v3.1). Reference behaviour: the userland
``st_countdown_rack`` of the POSTAIR decks (v8).
"""

from __future__ import annotations

import dataclasses
import hashlib
import html as _html
import json
import logging
import math
import os
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

#: Synthesised alarm timbres (WebAudio, no media file: offline rooms ring too).
ALARM_SOUNDS = ("bell", "beep", "chime", "gong")
#: Card types (``{"type": …}`` in a step's options).
CARD_TYPES = ("countdown", "stopwatch", "clock")
MODES = ("chain", "parallel")

_STEP_KEYS = {"type", "tz", "city", "alarm", "volume", "duration", "label_scale", "width"}
_HHMM_RE = re.compile(r"([01]?\d|2[0-3]):([0-5]\d)")


@dataclass
class CountdownConfig:
    """Appearance and behaviour of a rack (the ``MarkerConfig`` idiom).

    Colours default to a projection-friendly palette (``None``); labels are
    plain strings, so the caller translates them.

    :param autostart: Start the rack the first time it is on screen (a break
        screen) instead of waiting for a click.
    :param show_global_buttons: Draw ▶ Start / ↺ Reset (and the global bell)
        above the grid.
    :param alarm: The end-of-step timbre of every card with an end:
        ``"bell" | "beep" | "chime" | "gong"``, ``"off"`` or ``None`` (silent).
    :param alarm_volume: 0-1, perceptual.
    :param alarm_duration: Seconds, in ]0, 60]: the timbre's motif repeats
        until it is covered; ``None`` plays it once.
    :param alarm_muted: An alarmed rack starts muted; the bells arm it.
    """

    color_running: str | None = None
    color_pending: str | None = None
    color_finished: str | None = None
    card_css: str = ""
    start_all_label: str = "▶ Start"
    reset_all_label: str = "↺ Reset"
    ends_at_label: str = "ends at"
    since_label: str = "since"
    autostart: bool = False
    show_global_buttons: bool = True
    alarm: str | None = None
    alarm_volume: float = 0.6
    alarm_duration: float | None = None
    alarm_muted: bool = True

    @classmethod
    def resolve(cls, local: dict | None = None, json_path: str | None = None) -> CountdownConfig:
        """Defaults ← *local* ← the JSON file at *json_path*; the file wins.

        The defaults are the schema: an unknown key or a value of the wrong
        type is dropped (``bool`` is not an ``int``; a JSON list stands for a
        tuple), an unreadable layer is dropped, a missing file is silent. A
        setting never breaks the slide: the problems are logged, and shown on
        the page when ``STX_EDITABLE`` is on. *json_path* resolves through
        the registered static sources and is read again on every build.
        """
        values: dict = {}
        problems: list[str] = []
        layers: list[tuple[str, dict]] = []
        if local is not None:
            if isinstance(local, dict):
                layers.append(("local settings", local))
            else:
                problems.append(f"local settings ignored: a dict is expected, not {type(local).__name__}")
        if json_path:
            from .blocks import resolve_static
            path = resolve_static(json_path)
            if os.path.isfile(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        layers.append((json_path, data))
                    else:
                        problems.append(f"{json_path} ignored: a JSON object is expected")
                except (OSError, ValueError) as exc:
                    problems.append(f"{json_path} ignored: {exc}")
        defaults = {f.name: f.default for f in dataclasses.fields(cls)}
        for name, layer in layers:
            for key, value in layer.items():
                if key not in defaults:
                    problems.append(f"{name}: unknown key {key!r} ignored")
                    continue
                if not _fits(value, defaults[key], key):
                    problems.append(f"{name}: {key}={value!r} has the wrong type, ignored")
                    continue
                values[key] = value
        for p in problems:
            logger.warning("CountdownConfig.resolve: %s", p)
        if problems:
            _show_problems(problems)
        return cls(**values)


def _fits(value, default, key: str) -> bool:
    """Is *value* of the type of the default of *key*? (``None`` defaults: str/number)."""
    if key in ("color_running", "color_pending", "color_finished", "alarm"):
        return value is None or isinstance(value, str)
    if key == "alarm_duration":
        return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))
    if isinstance(default, bool):
        return isinstance(value, bool)
    if isinstance(default, float):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if isinstance(default, tuple):
        return isinstance(value, (list, tuple))
    return isinstance(value, type(default))


def _show_problems(problems: list[str]) -> None:
    try:
        from .runtime_flags import is_editable
        if is_editable():
            import streamlit as st
            st.warning("CountdownConfig: " + "; ".join(problems))
    except Exception:  # noqa: BLE001 — a warning must never break the slide
        pass


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_sound(value, where: str, allow_none: bool = True):
    if value in ("off",) or (allow_none and value is None):
        return None
    if value not in ALARM_SOUNDS:
        raise ValueError(f"st_countdown: {where} unknown alarm {value!r} — "
                         f"{', '.join(ALARM_SOUNDS)}, 'off' or None")
    return value


def _check_volume(value, where: str) -> float:
    if not _number(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"st_countdown: {where} volume {value!r} outside [0, 1]")
    return float(value)


def _check_duration(value, where: str):
    if value is None:
        return None
    if not _number(value) or not 0 < value <= 60:
        raise ValueError(f"st_countdown: {where} alarm duration {value!r} outside ]0, 60] "
                         f"seconds (None plays the motif once)")
    return float(value)


def _grid(n: int, grid) -> tuple[int, int]:
    if grid is None:
        cols = math.ceil(math.sqrt(n))
        return math.ceil(n / cols), cols
    if (not isinstance(grid, (tuple, list)) or len(grid) != 2
            or not all(isinstance(v, int) and not isinstance(v, bool) for v in grid)):
        raise ValueError(f"st_countdown: grid must be (rows, cols), not {grid!r}")
    rows, cols = grid
    if rows < 1 or cols < 1 or rows * cols < n:
        raise ValueError(f"st_countdown: a {rows}×{cols} grid is too small for {n} card(s)")
    return rows, cols


def _card(i: int, step, rack_sound, rack_vol, rack_dur) -> dict:
    """One step → the card the runtime reads (plain data)."""
    where = f"step #{i}"
    if not isinstance(step, (tuple, list)) or len(step) not in (2, 3):
        raise ValueError(f"st_countdown: {where} must be (label, target) or (label, target, options)")
    label, target = step[0], step[1]
    opts = step[2] if len(step) == 3 else None
    if not isinstance(label, str):
        raise ValueError(f"st_countdown: {where} label must be a string (translate it first)")
    alarm_opts: dict = {}
    if isinstance(opts, str):
        alarm_opts = {"alarm": opts}
        opts = {}
    elif opts is None:
        opts = {}
    elif isinstance(opts, dict):
        unknown = set(opts) - _STEP_KEYS
        if unknown:
            raise ValueError(f"st_countdown: {where} unknown option(s) {sorted(unknown)} — "
                             f"{', '.join(sorted(_STEP_KEYS))}")
        alarm_opts = {k: opts[k] for k in ("alarm", "volume", "duration") if k in opts}
    else:
        raise ValueError(f"st_countdown: {where} 3rd item must be a timbre (str) or an options dict, "
                         f"not {type(opts).__name__}")
    kind = opts.get("type", "countdown")
    if kind not in CARD_TYPES:
        raise ValueError(f"st_countdown: {where} unknown type {kind!r} — {', '.join(CARD_TYPES)}")
    if ("tz" in opts or "city" in opts) and kind != "clock":
        raise ValueError(f"st_countdown: {where} 'tz' and 'city' only apply to type='clock'")
    for key in ("label_scale", "width"):
        v = opts.get(key)
        if v is not None and (not _number(v) or not 0 < v <= 100):
            raise ValueError(f"st_countdown: {where} {key} {v!r} outside ]0, 100]")

    card = {"label": label, "kind": kind, "total": 0, "ttime": None}
    if kind == "countdown":
        if not _number(target) or target <= 0:
            raise ValueError(f"st_countdown: {where} a countdown needs minutes > 0, not {target!r}")
        card["total"] = max(1, round(target * 60))
    elif kind == "stopwatch":
        if target is not None and (not _number(target) or target <= 0):
            raise ValueError(f"st_countdown: {where} a stopwatch target is minutes > 0 or None, "
                             f"not {target!r}")
        card["total"] = max(1, round(target * 60)) if target is not None else 0
    else:
        tz = opts.get("tz")
        if not tz or not isinstance(tz, str):
            raise ValueError(f"st_countdown: {where} a clock needs 'tz', an IANA time zone "
                             f"such as 'Europe/Luxembourg'")
        import zoneinfo
        try:
            zoneinfo.ZoneInfo(tz)
        except Exception:  # noqa: BLE001 — every failure means: not a zone
            raise ValueError(f"st_countdown: {where} unknown time zone {tz!r}") from None
        if target is not None:
            m = _HHMM_RE.fullmatch(str(target))
            if not m:
                raise ValueError(f"st_countdown: {where} clock target {target!r} — 'HH:MM' (24 h) or None")
            card["ttime"] = f"{int(m.group(1)):02d}:{m.group(2)}"
        city = opts.get("city")
        card["tz"] = tz
        card["city"] = city if isinstance(city, str) else tz.split("/")[-1].replace("_", " ")

    has_end = (kind == "countdown" or card["total"] > 0 or card["ttime"] is not None)
    if alarm_opts and not has_end:
        raise ValueError(f"st_countdown: {where} an alarm on a {kind} with no target would never ring")
    sound, vol, dur = rack_sound, rack_vol, rack_dur
    if "alarm" in alarm_opts:
        sound = _check_sound(alarm_opts["alarm"], f"{where}")
    if "volume" in alarm_opts:
        vol = _check_volume(alarm_opts["volume"], f"{where}")
    if "duration" in alarm_opts:
        dur = _check_duration(alarm_opts["duration"], f"{where}")
    card["alarm"] = ({"sound": sound, "vol": vol, **({"dur": dur} if dur else {})}
                     if has_end and sound and vol > 0 else None)
    card["label_scale"] = opts.get("label_scale")
    card["width"] = opts.get("width")
    return card


# ---------------------------------------------------------------------------
# Markup
# ---------------------------------------------------------------------------

_CSS = """
.stx-cd{--cd-run:#f39c12;--cd-pend:#8a8f98;--cd-done:#e74c3c;--cd-gap:1.2vw;
  display:flex;flex-direction:column;gap:1.2vh;width:100%;font-family:inherit;}
.stx-cd-bar{display:flex;gap:1.2vw;justify-content:center;align-items:center;}
.stx-cd-btn{background:transparent;cursor:pointer;font-weight:700;line-height:1.15;color:var(--cd-pend);
  border:0.14em solid currentColor;border-radius:0.5em;padding:0.15em 0.9em;font-family:inherit;}
.stx-cd-bar .stx-cd-btn{font-size:calc(1.9vw * var(--cd-scale,1));}
.stx-cd-btn.stx-cd-go{color:var(--cd-run);}
.stx-cd-grid{display:grid;gap:var(--cd-gap);width:100%;}
.stx-cd-card{container-type:size;display:flex;flex-direction:column;align-items:center;
  justify-content:space-evenly;min-width:0;min-height:0;height:100%;box-sizing:border-box;
  overflow:hidden;padding:0.6vh 0.4vw;border-radius:0.8vw;background:rgba(127,127,127,0.10);}
.stx-cd-card>*{flex-shrink:0;}
.stx-cd-label{font-weight:700;line-height:1.1;text-align:center;max-width:96%;overflow:hidden;
  text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;}
.stx-cd-digits{font-weight:900;letter-spacing:0.04em;line-height:1;white-space:nowrap;
  font-variant-numeric:tabular-nums;color:var(--cd-pend);cursor:pointer;}
.stx-cd-card.stx-cd-running .stx-cd-digits{color:var(--cd-run);}
.stx-cd-card.stx-cd-done .stx-cd-digits{color:var(--cd-done);opacity:0.45;}
.stx-cd-card.stx-cd-clock .stx-cd-digits{color:var(--cd-run);}
.stx-cd-card.stx-cd-clock.stx-cd-done .stx-cd-digits{color:var(--cd-done);}
.stx-cd-at{color:var(--cd-pend);white-space:nowrap;}
.stx-cd-at:empty{display:none;}
.stx-cd-row{display:flex;align-items:center;gap:min(2cqw,4cqh);}
.stx-cd-row .stx-cd-btn{border-width:min(0.6cqw,1.2cqh);padding:0.05em 0.8em;line-height:1;}
.stx-cd-row .stx-cd-halt{color:var(--cd-pend);}
.stx-cd-bell{opacity:0.55;}
.stx-cd-edit{font-size:0.5em;width:7ch;max-width:96%;box-sizing:border-box;text-align:center;
  background:transparent;color:inherit;border:none;border-bottom:0.06em solid currentColor;
  outline:none;padding:0;font-weight:inherit;font-family:inherit;letter-spacing:normal;}
"""


def _fmt(sec: int) -> str:
    return f"{sec // 60:02d}:{sec % 60:02d}"


def _rack_id(cards: list[dict], mode: str) -> str:
    """Stable across reloads: the bells remember their state per card."""
    data = json.dumps([[c["label"], c["kind"], c["total"], c["ttime"]] for c in cards] + [mode],
                      ensure_ascii=False)
    return hashlib.sha1(data.encode("utf-8")).hexdigest()[:12]


def _card_html(i: int, card: dict, *, scale: float, label_scale: float, ends_scale: float,
               card_css: str) -> str:
    lsc = (card["label_scale"] or label_scale) * scale
    kind = card["kind"]
    if kind == "countdown":
        digits = _fmt(card["total"])
    elif kind == "stopwatch":
        digits = "00:00"
    else:
        digits = "--:--:--"
    at = ""
    if kind == "clock":
        at = card["city"] + (f" · → {card['ttime']}" if card["ttime"] else "")
    btn = f"font-size:min({6.5 * scale:.2f}cqw,{12 * scale:.2f}cqh)"
    buttons = ""
    if kind != "clock":
        buttons = (f'<button type="button" class="stx-cd-btn stx-cd-go" style="{btn}">▶</button>'
                   f'<button type="button" class="stx-cd-btn stx-cd-halt" style="{btn}">⏸</button>'
                   f'<button type="button" class="stx-cd-btn stx-cd-zero" style="{btn}">↺</button>')
    if card["alarm"]:
        buttons += f'<button type="button" class="stx-cd-btn stx-cd-bell" style="{btn}">\U0001F515</button>'
    row = f'<div class="stx-cd-row">{buttons}</div>' if buttons else ""
    digit_vh = max(20.0, 92 - 10 * (card["label_scale"] or label_scale) - 8 * ends_scale - 14)
    return (
        f'<div class="stx-cd-card stx-cd-{kind}" data-stx-cd-card="{i}" style="{_html.escape(card_css)}">'
        f'<div class="stx-cd-label" style="font-size:min({8 * lsc:.2f}cqw,{10 * lsc:.2f}cqh)">'
        f'{_html.escape(card["label"])}</div>'
        f'<div class="stx-cd-digits" style="font-size:{digit_vh * scale:.2f}cqh">{digits}</div>'
        f'<div class="stx-cd-at" style="font-size:min({4.5 * ends_scale * scale:.2f}cqw,'
        f'{8 * ends_scale * scale:.2f}cqh)">{_html.escape(at)}</div>'
        f'{row}</div>'
    )


def st_countdown(
    steps: list,
    mode: str = "chain",
    *,
    grid: tuple[int, int] | None = None,
    rack_vh: float = 62,
    scale: float = 1.0,
    label_scale: float = 2.0,
    ends_scale: float = 2.0,
    digits_width: float = 80,
    config: CountdownConfig | None = None,
) -> None:
    """A grid of countdown, stopwatch and clock cards (#52).

    :param steps: ``[(label, target), …]`` or ``(label, target, options)``.
        The label is a plain string (translate it first). The target is
        minutes for a countdown (fractions allowed: ``0.5`` = 30 s) or a
        stopwatch (``None`` = no target), ``"HH:MM"`` for a clock (``None`` =
        no target). The 3rd item is a timbre (``"bell"`` … or ``"off"``) or a
        dict: ``type`` (``"countdown"`` default, ``"stopwatch"``,
        ``"clock"``), ``tz`` (IANA, required for a clock) and ``city``,
        ``alarm``, ``volume``, ``duration``, ``label_scale``, ``width``.
    :param mode: ``"chain"``: one card with an end runs at a time and hands
        over to the next when it ends; cards with no end run freely.
        ``"parallel"``: every card runs on its own.
    :param grid: ``(rows, cols)``; ``None`` = the compact grid with the
        biggest cells (``cols = ceil(sqrt(k))``). Cards fill left to right,
        top to bottom; leftover cells stay empty.
    :param rack_vh: Height of the grid, in % of the window height.
    :param scale: Fine zoom of the card content.
    :param label_scale: Card name size (a step may set its own).
    :param ends_scale: Size of the "ends at / since / city" line.
    :param digits_width: % of the card width the digits may use (a step may
        set its own ``width``).
    :param config: Colours, labels, ``autostart``, global buttons, alarms.

    Double-click the digits to change a value: a countdown's time left
    (``40`` = 40 min, ``40:30``), a stopwatch's target in minutes, a clock's
    target ``HH:MM`` (an empty value removes the target). Enter or a click
    elsewhere applies it, Escape cancels; ↺ restores the original.
    """
    cfg = config or CountdownConfig()
    if mode not in MODES:
        raise ValueError(f"st_countdown: mode must be 'chain' or 'parallel', not {mode!r}")
    if not steps:
        raise ValueError("st_countdown: steps is empty")
    for name, value in (("rack_vh", rack_vh), ("scale", scale), ("label_scale", label_scale),
                        ("ends_scale", ends_scale), ("digits_width", digits_width)):
        if not _number(value) or value <= 0:
            raise ValueError(f"st_countdown: {name} must be a positive number, not {value!r}")
    if digits_width > 100:
        raise ValueError(f"st_countdown: digits_width {digits_width!r} outside ]0, 100]")
    rack_sound = _check_sound(cfg.alarm, "config")
    rack_vol = _check_volume(cfg.alarm_volume, "config")
    rack_dur = _check_duration(cfg.alarm_duration, "config")
    cards = [_card(i, s, rack_sound, rack_vol, rack_dur) for i, s in enumerate(steps)]
    rows, cols = _grid(len(cards), grid)
    rack_id = _rack_id(cards, mode)

    data = {
        "v": 1, "id": rack_id, "mode": mode, "autostart": bool(cfg.autostart),
        "muted": bool(cfg.alarm_muted), "endsAt": cfg.ends_at_label, "since": cfg.since_label,
        "width": float(digits_width),
        "cards": [{"kind": c["kind"], "total": c["total"], "ttime": c["ttime"],
                   "tz": c.get("tz"), "city": c.get("city"), "alarm": c["alarm"],
                   "width": c["width"]} for c in cards],
    }
    colors = "".join(f"{var}:{val};" for var, val in (
        ("--cd-run", cfg.color_running), ("--cd-pend", cfg.color_pending),
        ("--cd-done", cfg.color_finished)) if val)
    bar = ""
    if cfg.show_global_buttons:
        bell = ('<button type="button" class="stx-cd-btn stx-cd-bell stx-cd-all-bell">\U0001F515</button>'
                if any(c["alarm"] for c in cards) else "")
        bar = (f'<div class="stx-cd-bar">'
               f'<button type="button" class="stx-cd-btn stx-cd-go stx-cd-all-start">'
               f'{_html.escape(cfg.start_all_label)}</button>'
               f'<button type="button" class="stx-cd-btn stx-cd-all-reset">'
               f'{_html.escape(cfg.reset_all_label)}</button>{bell}</div>')
    body = "".join(_card_html(i, c, scale=scale, label_scale=label_scale, ends_scale=ends_scale,
                              card_css=cfg.card_css) for i, c in enumerate(cards))
    markup = (
        f"<style>{_CSS}</style>"
        f'<div class="stx-cd" data-stx-countdown="{_html.escape(json.dumps(data, ensure_ascii=False))}" '
        f'style="--cd-scale:{scale};{colors}">{bar}'
        f'<div class="stx-cd-grid" style="grid-template-columns:repeat({cols},minmax(0,1fr));'
        f'grid-template-rows:repeat({rows},minmax(0,1fr));height:{rack_vh}vh">{body}</div></div>'
    )
    from .export import st_html
    st_html(markup)
