"""``.stx-release.json``: the targets and what each one serves — versioned, never a secret.

::

    {"default_target": "prod",
     "targets": {"prod": {"type": "ssh", "host": "root@1.2.3.4", "ssh_key": "~/.ssh/id_ed25519",
                          "root": "/data/stx/trainings", "domain": "example.org",
                          "coolify_env": ".stx-deploy.env", "coolify_project": "trainings",
                          "coolify_server": "localhost", "static_app": "trainings-static",
                          "live_app": "trainings-live", "static_uuid": "…", "live_uuid": "…"},
                 "local": {"type": "local", "root": "~/.stx-host-sim", "domain": "example.org",
                           "static": "stx-static", "live": "stx-live",
                           "static_url": "http://127.0.0.1:8091", "live_url": "http://127.0.0.1:8092"}},
     "sites": {"prod": {"chat1d-slides": {"port": 9001, "release": "5c26474e49dc", "previous": "…",
                                          "date": "…", "asleep": false, "html_open": false,
                                          "up_to_slide": 12, "html_release": "5c26474e49dc-s14",
                                          "html_previous": "…", "last": "limit"}}}}

The same shape as the prototype's ``state.json``; ``stx release import`` copies it (#136, rel2 passage=a).
"""

from __future__ import annotations

import json
from pathlib import Path

from . import ReleaseError

STATE_FILE = ".stx-release.json"
#: What a site entry keeps (the prototype's training/kind are replaced by the site list of stx.toml).
SITE_KEYS = ("port", "release", "previous", "date", "asleep", "html_open", "skew",
             # the HTML face's own release under a slide limit (#146, as the prototype's bascule2/n1)
             "html_release", "html_previous", "up_to_slide", "up_to_slide_previous", "last", "html_date",
             # each slide number's cut of the release, now and before (#148)
             "cuts", "cuts_previous")


def state_path(root: Path) -> Path:
    return root / STATE_FILE


def load_state(root: Path) -> dict:
    path = state_path(root)
    if not path.is_file():
        return {"default_target": None, "targets": {}, "sites": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ReleaseError(f"{path}: {e}") from None
    state.setdefault("targets", {})
    state.setdefault("sites", {})
    return state


def save_state(root: Path, state: dict) -> None:
    state_path(root).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sites_of(state: dict, target: str) -> dict:
    return state["sites"].setdefault(target, {})


def import_prototype(root: Path, source: Path, known_sites: set[str], force: bool = False) -> dict:
    """The prototype's state.json → .stx-release.json, nothing sent to the server (rel2 passage=a).

    Targets are copied as they are; each site entry keeps what stx release reads. Sites the project
    no longer lists are reported, and kept, so that status still shows them.
    """
    if state_path(root).exists() and not force:
        raise ReleaseError(f"{STATE_FILE} already exists — pass --force to replace it")
    try:
        old = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ReleaseError(f"{source}: {e}") from None
    sites = old.get("sites", {})
    flat = {k: v for k, v in sites.items() if isinstance(v, dict) and "target" in v}
    if flat:                                   # the prototype's oldest, flat form
        grouped: dict = {}
        for site, v in flat.items():
            grouped.setdefault(v["target"], {})[site] = v
        sites = grouped
    new = {"default_target": old.get("default_target"), "targets": old.get("targets", {}), "sites": {}}
    unknown: list[str] = []
    for target, entries in sites.items():
        for site, v in entries.items():
            new["sites"].setdefault(target, {})[site] = {k: v[k] for k in SITE_KEYS if k in v}
            if site not in known_sites:
                unknown.append(f"{target}/{site}")
    save_state(root, new)
    new["_unknown"] = unknown
    return new
