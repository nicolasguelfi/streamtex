"""Run-time switches of a deployed document: editable? exportable? (#93).

Both large projects carried their own copy (sumvadis ``postair_env.py``,
formerly seven ``config.py``; ai4se6d three ``custom/config.py`` with 167
uses and a documentation announcing the opposite default). One reading:

- ``STX_EDITABLE`` — the image-editing panels (AI images) are shown;
- ``STX_EXPORTABLE`` — the export panel (HTML / PDF) is shown.

Each is read from the environment, then from an optional ``.env`` file
(``KEY=value`` lines) next to the book; the legacy names ``IS_EDITABLE`` /
``IS_EXPORTABLE`` are accepted. Truthy: ``1 true yes on`` (any case).
Default: ``False`` for both — a deployed document is read-only unless asked.
Nothing in the library reads them implicitly: a book passes them where it
wants, e.g. ``AIImageConfig(editable=stx.is_editable())``.
"""

from __future__ import annotations

import os
from pathlib import Path

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().removeprefix("export ").strip()] = value.strip().strip("\'\"")
    return values


def env_flag(name: str, default: bool = False, *, legacy: str | None = None,
             env_file: str | os.PathLike | None = None) -> bool:
    """A boolean switch: environment, then *env_file*, then *default*."""
    candidates = [name] + ([legacy] if legacy else [])
    file_values = _read_env_file(Path(env_file)) if env_file else {}
    for source in (os.environ, file_values):
        for key in candidates:
            raw = source.get(key)
            if raw is None:
                continue
            value = raw.strip().lower()
            if value in _TRUE:
                return True
            if value in _FALSE:
                return False
            raise ValueError(f"{key}={raw!r}: expected one of 1/0, true/false, yes/no, on/off")
    return default


def is_editable(env_file: str | os.PathLike | None = None) -> bool:
    """``STX_EDITABLE`` (legacy ``IS_EDITABLE``) — default False."""
    return env_flag("STX_EDITABLE", legacy="IS_EDITABLE", env_file=env_file)


def is_exportable(env_file: str | os.PathLike | None = None) -> bool:
    """``STX_EXPORTABLE`` (legacy ``IS_EXPORTABLE``) — default False."""
    return env_flag("STX_EXPORTABLE", legacy="IS_EXPORTABLE", env_file=env_file)
