"""File-level helpers shared by the Claude profile commands.

- CLAUDE.md ownership (#67): the root ``CLAUDE.md`` is written only when stx
  owns it; a user-authored file is never touched and the profile text goes
  to ``.claude/CLAUDE.md`` instead (Claude Code loads both).
- ``settings.json`` merge (#68): profile settings are merged into an
  existing file, never replacing it.
- Machine settings (#72): ``~/.config/streamtex/config.toml``.
"""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from pathlib import Path

# The profile text, when the root CLAUDE.md belongs to the user.
PROFILE_CLAUDE_MD = os.path.join(".claude", "CLAUDE.md")
SETTINGS_PATH = os.path.join(".claude", "settings.json")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path: str, content: str) -> None:
    if os.path.isfile(path):
        st = os.stat(path)
        if not st.st_mode & 0o200:
            os.chmod(path, st.st_mode | 0o200)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def root_claude_md_is_owned(
    target: str,
    *,
    candidates: tuple[str | None, ...] = (),
    locked_sha: str | None = None,
) -> bool:
    """True when stx may write the root CLAUDE.md of *target*.

    stx owns the file when it is absent, when its content equals one of the
    *candidates* (renders stx produced — the previous template, the new one,
    or the profile's raw CLAUDE.md), or when its hash is the one recorded in
    the lock file.
    """
    current = _read(os.path.join(target, "CLAUDE.md"))
    if current is None:
        return True
    if any(c is not None and current == c for c in candidates):
        return True
    return locked_sha is not None and sha256_text(current) == locked_sha


def write_profile_claude_md(
    target: str,
    content: str,
    *,
    candidates: tuple[str | None, ...] = (),
    locked_sha: str | None = None,
) -> tuple[str, bool]:
    """Write the profile's CLAUDE.md text where it belongs.

    Returns ``(relative_destination, changed)``. The destination is
    ``CLAUDE.md`` when stx owns the root file, ``.claude/CLAUDE.md``
    otherwise (the root file is then left byte-identical).
    """
    owned = root_claude_md_is_owned(
        target, candidates=(*candidates, content), locked_sha=locked_sha,
    )
    rel = "CLAUDE.md" if owned else PROFILE_CLAUDE_MD
    dst = os.path.join(target, rel)
    if _read(dst) == content:
        return rel, False
    _write(dst, content)
    return rel, True


# ---------------------------------------------------------------------------
# settings.json
# ---------------------------------------------------------------------------

def _merge(local, source):
    """Return *local* completed with what *source* adds; nothing removed."""
    if isinstance(local, dict) and isinstance(source, dict):
        out = dict(local)
        for k, v in source.items():
            out[k] = _merge(local[k], v) if k in local else v
        return out
    if isinstance(local, list) and isinstance(source, list):
        return local + [x for x in source if x not in local]
    return local  # scalar conflict: the user's value wins


def _covers(local, source) -> bool:
    if isinstance(local, dict) and isinstance(source, dict):
        return all(k in local and _covers(local[k], v) for k, v in source.items())
    if isinstance(local, list) and isinstance(source, list):
        return all(x in local for x in source)
    return True  # scalar: the user's value is authoritative


def _load_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def settings_cover(local_path: str, source_path: str) -> bool:
    """True when the local settings already contain everything the source sets."""
    local, source = _load_json(local_path), _load_json(source_path)
    if local is None or source is None:
        return False
    return _covers(local, source)


def merge_settings(source_path: str, dst_path: str) -> bool:
    """Merge *source_path* into *dst_path* (created if absent). Returns changed."""
    source = _load_json(source_path)
    if source is None:
        return False
    if not os.path.isfile(dst_path):
        _write(dst_path, json.dumps(source, indent=2, ensure_ascii=False) + "\n")
        return True
    local = _load_json(dst_path)
    if local is None:  # unreadable user file: never clobber it
        return False
    merged = _merge(local, source)
    if merged == local:
        return False
    _write(dst_path, json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    return True


# ---------------------------------------------------------------------------
# Machine settings
# ---------------------------------------------------------------------------

def machine_config_path() -> Path:
    return Path.home() / ".config" / "streamtex" / "config.toml"


def load_machine_config() -> dict:
    p = machine_config_path()
    if not p.is_file():
        return {}
    try:
        with open(p, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def global_commands_enabled(override: bool | None = None) -> bool:
    """Whether shared commands are copied to ``~/.claude/commands`` (#72).

    *override* wins, then ``$STX_GLOBAL_COMMANDS`` (set by the
    ``--[no-]global-commands`` flags), then ``[claude] global_commands`` of
    the machine config; default True (0.7.34 behaviour).
    """
    if override is not None:
        return override
    env = os.environ.get("STX_GLOBAL_COMMANDS")
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no", "off")
    value = load_machine_config().get("claude", {}).get("global_commands", True)
    return bool(value)
