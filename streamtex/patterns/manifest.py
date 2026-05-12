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

from . import ManifestError, MetaError, __version_schema__

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source": self.source,
            "source_commit": self.source_commit,
            "preset": self.preset,
            "mode": self.mode,
            "installed_at": self.installed_at,
            "patterns": [p.to_dict() for p in self.patterns],
        }


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
    if schema != __version_schema__:
        raise MetaError(
            f"{path}: unsupported schema_version {schema!r} "
            f"(expected {__version_schema__})"
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

    return PatternsMeta(
        schema_version=int(schema),
        source=str(data.get("source", "")),
        source_commit=data.get("source_commit"),
        preset=data.get("preset"),
        mode=str(data.get("mode", "copy")),
        installed_at=str(data.get("installed_at", "")),
        patterns=patterns,
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
