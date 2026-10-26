"""What each session sees on the HTML face (#148): its level, the exports it needs, the server's file.

A level is ``None`` (closed: "not open yet"), ``"all"``, ``N`` (slides 1 to N, the block of slide N
whole) or a schedule ``((epoch seconds, level), …)``; ``passwords.DEFAULT`` is the site's level
(``stx release limit SITE N``, kept in the state as ``up_to_slide``), else all the slides.

On the target, ``static/sites/<site>/levels`` holds one line per label, read by the login service::

    S1027	releases/<release>-s120
    S1103	closed
    ADMIN	current
    S1110	1762761600=releases/<release>-s52;1762779600=current

The service answers the folder of the label's level at the current time (``X-Stx-View``); nginx serves
it, or the "not open yet" page. A scheduled level therefore changes by itself, with no program on the
server. A label missing from the file is closed; without the file, everyone sees ``current``.
"""

from __future__ import annotations

import time

from .passwords import DEFAULT

CLOSED = "closed"
CURRENT = "current"


def resolve(level, default: int | None):
    """The level of a label once the site's level is known (*default*: N, or None for all)."""
    if level == DEFAULT:
        return "all" if default is None else default
    return level


def cuts(levels: dict, default: int | None) -> set[int]:
    """The slide numbers some label needs an export for, now or later."""
    out: set[int] = set()
    for level in levels.values():
        level = resolve(level, default)
        steps = level if isinstance(level, tuple) else ((0, level),)
        out |= {v for _, v in steps if isinstance(v, int)}
    return out


def folder(value, names: dict[int, str]) -> str:
    """The folder of one level: ``closed``, ``current`` or ``releases/<release>-s<last>``."""
    if value is None:
        return CLOSED
    if value == "all":
        return CURRENT
    return f"releases/{names[value]}"


def text(levels: dict, default: int | None, names: dict[int, str]) -> str:
    """The ``levels`` file: one line per label (*names*: slide number → its release folder)."""
    lines = []
    for label, level in sorted(levels.items()):
        level = resolve(level, default)
        if isinstance(level, tuple):
            spec = ";".join(f"{ts}={folder(v, names)}" for ts, v in level)
        else:
            spec = folder(level, names)
        lines.append(f"{label}\t{spec}\n")
    return "".join(lines)


def now_of(level, default: int | None, now: float | None = None):
    """The level in force at *now* (a schedule before its first step: closed)."""
    level = resolve(level, default)
    if not isinstance(level, tuple):
        return level
    current = None
    for ts, v in level:
        if ts <= (now if now is not None else time.time()):
            current = v
    return current


def describe(level, default: int | None) -> str:
    """A level in words, for ``status`` and ``auth-status``."""
    level = resolve(level, default)
    if isinstance(level, tuple):
        steps = ", ".join(f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))}→{describe(v, None)}"
                          for ts, v in level)
        return f"schedule ({steps})"
    return {None: "not open yet", "all": "all"}.get(level, f"up to {level}")
