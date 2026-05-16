"""Parse ``manifest.toml``, ``.patterns-meta.json``, and pattern frontmatter.

Provides the foundational data model used by the rest of the
:mod:`streamtex.patterns` package: it has no internal dependencies aside
from the public exceptions exposed by :mod:`streamtex.patterns`.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import (
    SUPPORTED_SCHEMA_VERSIONS,
    ManifestError,
    MetaError,
    __version_schema__,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REQUIRED_FM_FIELDS = ("name", "type", "description", "extrapolable", "since")


@dataclass(frozen=True)
class Frontmatter:
    """A parsed pattern frontmatter block."""

    name: str
    type: str
    description: str
    extrapolable: bool
    since: str
    tags: tuple[str, ...] = ()


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split a markdown text into (yaml_block, body).

    Raises:
        ManifestError: if the document has no frontmatter.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ManifestError("missing frontmatter (expected leading '---' block)")
    return m.group(1), m.group(2)


def _parse_tags_value(raw: str) -> tuple[str, ...]:
    """Parse a YAML-ish list value: ``[a, b, "c"]`` or ``[]``."""
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        raise ManifestError(f"tags must be a YAML list, got: {raw!r}")
    inner = raw[1:-1].strip()
    if not inner:
        return ()
    items = []
    for item in inner.split(","):
        v = item.strip().strip("\"'")
        if v:
            items.append(v)
    return tuple(items)


def _coerce_bool(raw: str, *, field_name: str) -> bool:
    s = raw.strip().lower()
    if s in ("true", "yes"):
        return True
    if s in ("false", "no"):
        return False
    raise ManifestError(f"invalid bool for '{field_name}': {raw!r}")


def parse_frontmatter(text: str) -> Frontmatter:
    """Parse a YAML-ish frontmatter block (mini-parser, no PyYAML dependency).

    Recognises scalars (string, bool) and a ``tags`` array.
    """
    fields: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ManifestError(f"malformed frontmatter line: {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Strip simple wrapping quotes.
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        fields[key] = value

    missing = [k for k in _REQUIRED_FM_FIELDS if k not in fields]
    if missing:
        raise ManifestError(f"missing frontmatter fields: {', '.join(missing)}")

    if fields["type"] != "pattern":
        raise ManifestError(
            f"frontmatter type must be 'pattern', got {fields['type']!r}"
        )

    since = str(fields["since"])
    if not _DATE_RE.match(since):
        raise ManifestError(f"invalid 'since' date format: {since!r}")

    extrapolable = _coerce_bool(str(fields["extrapolable"]), field_name="extrapolable")

    tags_raw = fields.get("tags", "[]")
    tags = _parse_tags_value(str(tags_raw)) if tags_raw else ()

    return Frontmatter(
        name=str(fields["name"]),
        type=str(fields["type"]),
        description=str(fields["description"]),
        extrapolable=extrapolable,
        since=since,
        tags=tags,
    )


# ---------------------------------------------------------------------------
# Repo manifest
# ---------------------------------------------------------------------------

_DEFAULT_REQUIRED_SECTIONS = (
    "Visual",
    "Structure",
    "Styling rules",
    "Code skeleton",
    "When to use",
    "When NOT to use",
)


@dataclass(frozen=True)
class RepoManifest:
    """The parsed top-level ``manifest.toml`` of a patterns source repo."""

    name: str
    version: str
    description: str
    spec_version: str
    since: str
    scopes: dict[str, str] = field(default_factory=dict)
    presets: dict[str, str] = field(default_factory=dict)
    required_sections: tuple[str, ...] = _DEFAULT_REQUIRED_SECTIONS
    validate_on_pr: bool = False


def load_repo_manifest(source_dir: Path) -> RepoManifest:
    """Load and validate ``<source_dir>/manifest.toml``.

    Raises:
        ManifestError: if the file is missing or malformed.
    """
    path = source_dir / "manifest.toml"
    if not path.is_file():
        raise ManifestError(f"manifest.toml not found in {source_dir}")
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - rare
        raise ManifestError(f"{path}: {exc}") from exc

    repo = data.get("repo", {})
    for k in ("name", "version", "description", "spec_version", "since"):
        if k not in repo:
            raise ManifestError(f"{path}: missing [repo].{k}")

    ci = data.get("ci", {})
    required_sections = tuple(ci.get("required_sections", _DEFAULT_REQUIRED_SECTIONS))

    return RepoManifest(
        name=str(repo["name"]),
        version=str(repo["version"]),
        description=str(repo["description"]),
        spec_version=str(repo["spec_version"]),
        since=str(repo["since"]),
        scopes=dict(data.get("scopes", {})),
        presets=dict(data.get("presets", {})),
        required_sections=required_sections,
        validate_on_pr=bool(ci.get("validate_on_pr", False)),
    )


# ---------------------------------------------------------------------------
# .patterns-meta.json
# ---------------------------------------------------------------------------

META_FILENAME = ".patterns-meta.json"


@dataclass
class PatternRecord:
    """A single pattern entry in ``.patterns-meta.json``."""

    name: str
    from_: str
    sha: str
    installed_sha: str

    def to_dict(self) -> dict[str, str]:
        """Serialize for JSON, mapping ``from_`` to ``from``."""
        return {
            "name": self.name,
            "from": self.from_,
            "sha": self.sha,
            "installed_sha": self.installed_sha,
        }


EFFECTIVE_MODES = ("empty", "preset", "individual", "all", "composite")
"""Possible return values of :attr:`PatternSelection.effective_mode`.

This is a *derived* classification of a selection, not an input mode.
Persistence is always done in the v3 composite shape; ``effective_mode``
is a convenience for callers that just want to label "what kind of
selection is this" (e.g. for log messages or analytics).
"""

# Legacy v2 mode strings — still accepted on read for back-compat.
_LEGACY_V2_MODES = ("preset", "individual", "all")


@dataclass
class PatternSelection:
    """User-expressed install intent persisted across syncs (schema v3).

    A selection is the *intent* — a composable recipe — as opposed to
    ``PatternsMeta.patterns`` which is the *resolved snapshot* of what's
    actually on disk. ``stx patterns sync`` re-resolves the intent on a
    fresh clone or after the source repo evolves.

    Composition rules:
        1. If ``all_flag`` is True → every pattern in the source.
        2. Otherwise: union of patterns(p) for p in ``presets``,
           plus ``individuals``, minus ``excludes``.

    All fields default to empty so the "no intent" case is representable
    (and recognisable via :meth:`is_empty`).
    """

    presets: tuple[str, ...] = ()
    """Preset names taken in full (subject to ``excludes``)."""

    individuals: tuple[str, ...] = ()
    """Pattern names picked explicitly, on top of any preset contents."""

    excludes: tuple[str, ...] = ()
    """Pattern names to subtract from the resolved set (presets + individuals)."""

    all_flag: bool = False
    """When True, take every pattern in the source (still subject to ``excludes``)."""

    def __post_init__(self) -> None:
        # Coerce to tuples in case callers pass lists.
        object.__setattr__(self, "presets", tuple(self.presets))
        object.__setattr__(self, "individuals", tuple(self.individuals))
        object.__setattr__(self, "excludes", tuple(self.excludes))
        if self.all_flag and (self.presets or self.individuals):
            raise MetaError(
                "selection.all=true is exclusive with presets/individuals "
                "(use excludes to subtract instead)"
            )

    # ---- Derived helpers ---------------------------------------------------

    @property
    def effective_mode(self) -> str:
        """Classify this selection — see :data:`EFFECTIVE_MODES`."""
        if self.is_empty():
            return "empty"
        if self.all_flag:
            return "all"
        if self.presets and not self.individuals and len(self.presets) == 1:
            return "preset"
        if self.individuals and not self.presets:
            return "individual"
        return "composite"

    def is_empty(self) -> bool:
        """True iff this selection would resolve to no patterns."""
        return not (self.all_flag or self.presets or self.individuals)

    # ---- Serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Emit the v3 canonical JSON/TOML shape."""
        return {
            "presets": list(self.presets),
            "individuals": list(self.individuals),
            "excludes": list(self.excludes),
            "all": self.all_flag,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternSelection:
        """Build from either v3 canonical or v2 (``mode``+``items``) shape."""
        # v3 shape (preferred): presence of any of the new fields decides.
        v3_keys = {"presets", "individuals", "excludes", "all"}
        if v3_keys & data.keys():
            return cls(
                presets=_coerce_str_tuple(data.get("presets", []), "presets"),
                individuals=_coerce_str_tuple(data.get("individuals", []), "individuals"),
                excludes=_coerce_str_tuple(data.get("excludes", []), "excludes"),
                all_flag=bool(data.get("all", False)),
            )
        # v2 legacy shape: {"mode": "...", "items": [...]}.
        if "mode" in data:
            return cls.from_legacy(
                mode=str(data.get("mode", "")),
                items=_coerce_str_tuple(data.get("items", []), "items"),
            )
        # Empty / unknown → empty selection (no intent recorded).
        return cls()

    @classmethod
    def from_legacy(cls, mode: str, items: tuple[str, ...]) -> PatternSelection:
        """Build a v3 selection from the v2 (mode, items) pair.

        Used for both meta-file migration (v2 → v3) and for the legacy
        positional API (still useful in tests).
        """
        if mode not in _LEGACY_V2_MODES:
            raise MetaError(
                f"invalid legacy mode {mode!r} (expected one of {_LEGACY_V2_MODES})"
            )
        if mode == "preset":
            if len(items) != 1:
                raise MetaError(
                    "legacy mode='preset' requires exactly one item"
                )
            return cls(presets=items)
        if mode == "individual":
            return cls(individuals=items)
        # mode == "all"
        if items:
            raise MetaError("legacy mode='all' must have an empty items list")
        return cls(all_flag=True)


def _coerce_str_tuple(value: object, field_name: str) -> tuple[str, ...]:
    """Best-effort: turn a JSON/TOML list value into a tuple of str."""
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise MetaError(
            f"selection.{field_name} must be a list, got {type(value).__name__}"
        )
    return tuple(str(x) for x in value)


@dataclass
class PatternsMeta:
    """The complete ``.patterns-meta.json`` document."""

    schema_version: int
    source: str
    source_commit: str | None
    preset: str | None
    mode: str
    installed_at: str
    patterns: list[PatternRecord]
    selection: PatternSelection | None = None
    """User intent (schema v2+). ``None`` for v1 files migrated in-memory."""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema_version": self.schema_version,
            "source": self.source,
            "source_commit": self.source_commit,
            "preset": self.preset,
            "mode": self.mode,
            "installed_at": self.installed_at,
            "patterns": [p.to_dict() for p in self.patterns],
        }
        if self.schema_version >= 2:
            out["selection"] = self.selection.to_dict() if self.selection else None
        return out


def load_meta(target_dir: Path) -> PatternsMeta:
    """Load ``<target_dir>/.patterns-meta.json``.

    Raises:
        MetaError: if the file is missing or malformed.
    """
    path = target_dir / META_FILENAME
    if not path.is_file():
        raise MetaError(f"{META_FILENAME} not found in {target_dir}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetaError(f"{path}: invalid JSON: {exc}") from exc

    schema = data.get("schema_version")
    if schema not in SUPPORTED_SCHEMA_VERSIONS:
        raise MetaError(
            f"{path}: unsupported schema_version {schema!r} "
            f"(supported: {SUPPORTED_SCHEMA_VERSIONS})"
        )

    raw_patterns = data.get("patterns", [])
    patterns: list[PatternRecord] = []
    for item in raw_patterns:
        try:
            patterns.append(
                PatternRecord(
                    name=item["name"],
                    from_=item["from"],
                    sha=item["sha"],
                    installed_sha=item["installed_sha"],
                )
            )
        except KeyError as exc:
            raise MetaError(f"{path}: pattern entry missing field {exc}") from exc

    selection: PatternSelection | None = None
    if int(schema) >= 2:
        raw_sel = data.get("selection")
        if isinstance(raw_sel, dict):
            try:
                # from_dict accepts both v2 (mode/items) and v3 shapes.
                selection = PatternSelection.from_dict(raw_sel)
            except MetaError as exc:
                raise MetaError(f"{path}: {exc}") from exc
    else:
        # v1 → v3 in-memory migration: infer selection from `preset` when
        # possible so sync stays functional. Otherwise leave None and let
        # the next install/sync record the user's explicit intent.
        if data.get("preset"):
            selection = PatternSelection.from_legacy(
                mode="preset", items=(str(data["preset"]),),
            )

    return PatternsMeta(
        schema_version=__version_schema__,
        source=str(data.get("source", "")),
        source_commit=data.get("source_commit"),
        preset=data.get("preset"),
        mode=str(data.get("mode", "copy")),
        installed_at=str(data.get("installed_at", "")),
        patterns=patterns,
        selection=selection,
    )


def save_meta(target_dir: Path, meta: PatternsMeta) -> Path:
    """Write the meta document to ``<target_dir>/.patterns-meta.json``."""
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / META_FILENAME
    payload = json.dumps(meta.to_dict(), indent=2, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# SHA helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Return the 64-char hex SHA-256 of *path*'s bytes."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the 64-char hex SHA-256 of *data*."""
    return hashlib.sha256(data).hexdigest()


# Avoid unused-import warning from dataclasses.asdict
_ = asdict
