"""Reuse-architecture contracts: Protocols and TypedDicts.

These types are the public contract surface that packs implement and that the
StreamTeX lib validates. Everything here is type-only / declarative — no
runtime side effects beyond `@runtime_checkable` registration.

Cross-references: PLAN.md §5.1 (DesignSystemProtocol), §5.2 (ComponentMeta),
§5.3 (KitManifest), §5.4 (PackManifest + StxTomlPackEntry).
"""

from __future__ import annotations

from typing import ClassVar, Literal, NotRequired, Protocol, TypedDict, runtime_checkable

from streamtex.styles import ListStyle, Style

# ---------------------------------------------------------------------------
# Style bundles (§5.1 — Q1 resolved option b: typed with concrete Style)
# ---------------------------------------------------------------------------


@runtime_checkable
class ColorsBundle(Protocol):
    primary: ClassVar[Style]
    accent: ClassVar[Style]
    bg: ClassVar[Style]
    surface: ClassVar[Style]
    text: ClassVar[Style]
    muted: ClassVar[Style]


@runtime_checkable
class TitlesBundle(Protocol):
    slide: ClassVar[Style]
    section: ClassVar[Style]
    subtitle: ClassVar[Style]
    body: ClassVar[Style]
    caption: ClassVar[Style]


@runtime_checkable
class CalloutsBundle(Protocol):
    info: ClassVar[Style]
    warn: ClassVar[Style]
    error: ClassVar[Style]
    success: ClassVar[Style]
    icon: ClassVar[Style]
    title: ClassVar[Style]
    body: ClassVar[Style]


@runtime_checkable
class StatHeroBundle(Protocol):
    value: ClassVar[Style]
    body: ClassVar[Style]


@runtime_checkable
class CardGridBundle(Protocol):
    card: ClassVar[Style]
    card_title: ClassVar[Style]
    card_body: ClassVar[Style]


@runtime_checkable
class ComparisonTableBundle(Protocol):
    header: ClassVar[Style]
    row: ClassVar[Style]
    accent_row: ClassVar[Style]


@runtime_checkable
class TakeawaysBundle(Protocol):
    item: ClassVar[Style]
    lead: ClassVar[Style]


@runtime_checkable
class BodyBundle(Protocol):
    paragraph: ClassVar[Style]
    emphasis: ClassVar[Style]
    code: ClassVar[Style]


@runtime_checkable
class FontsBundle(Protocol):
    """Font family declarations exposed by a design system.

    OPTIONAL bundle (not in REQUIRED_BUNDLES). A design system MAY provide
    fonts to let downstream documents pin typography via composable Style
    objects instead of hardcoding font-family strings in their own
    custom/styles.py. The three slots are intentionally kept distinct so a
    document can diverge heading vs body vs code typography without touching
    the pack.
    """

    body_family: ClassVar[Style]
    heading_family: ClassVar[Style]
    code_family: ClassVar[Style]


@runtime_checkable
class CitationBundle(Protocol):
    source: ClassVar[Style]
    author: ClassVar[Style]


@runtime_checkable
class InlineEmphasisBundle(Protocol):
    strong: ClassVar[Style]
    soft: ClassVar[Style]


@runtime_checkable
class ListsBundle(Protocol):
    bullet: ClassVar[ListStyle]
    ordered: ClassVar[ListStyle]


REQUIRED_BUNDLES: tuple[str, ...] = (
    "colors",
    "titles",
    "callouts",
    "body",
)
"""Bundles that every conforming design system MUST provide.

Optional bundles (stat_hero, card_grid, comparison_table, takeaways, citation,
inline_emphasis, lists, fonts) can be added by design systems but are not
mandatory. Components requesting an optional bundle they don't find raise
BV001 at install-time (cf. validation.validate_bundles_required).
"""


# ---------------------------------------------------------------------------
# Design system contract (§5.1)
# ---------------------------------------------------------------------------


@runtime_checkable
class DesignSystemProtocol(Protocol):
    name: ClassVar[str]
    colors: ClassVar[type[ColorsBundle]]
    titles: ClassVar[type[TitlesBundle]]
    callouts: ClassVar[type[CalloutsBundle]]
    body: ClassVar[type[BodyBundle]]


# ---------------------------------------------------------------------------
# Component metadata (§5.2)
# ---------------------------------------------------------------------------

Granularity = Literal["primitive", "composition", "block"]


class ComponentMeta(TypedDict):
    """Schema for the `__component_meta__` dict at module level of a component.

    See PLAN.md §4.1.2 for the canonical example. Field semantics:

    * `name` — snake_case slug; MUST match the module file name (sans .py).
    * `description` — single-line human description.
    * `tags` — free-form snake_case tags for filtering / discovery.
    * `extrapolable` — when True, INVARIANTS/PARAMS/INTERDITS sections MUST
      be present in the docstring (each with ≥ 2 items).
    * `since` — ISO date the component was introduced.
    * `bundles_required` — list of `"<bundle>.<attr>"` strings the public
      function reads from the active design system.
    * `granularity` — primitive | composition | block.
    * `related` — free cross-references (mention only).
    * `uses_components` — names of other components called inside this one
      (Q5 option A; advisory, not auto-resolved).
    """

    name: str
    description: str
    tags: list[str]
    extrapolable: bool
    since: str
    bundles_required: list[str]
    granularity: Granularity
    related: NotRequired[list[str]]
    uses_components: NotRequired[list[str]]


# ---------------------------------------------------------------------------
# Kit manifest (§5.3)
# ---------------------------------------------------------------------------


class KitDesignSystemRef(TypedDict):
    ref: str  # "<name>" or "<pack>:<name>"


class KitComponentsSpec(TypedDict):
    include: list[str]


class KitSpec(TypedDict):
    name: str
    description: str
    since: str
    design_system: KitDesignSystemRef
    cli_template: NotRequired[KitDesignSystemRef]
    project_blueprint: NotRequired[KitDesignSystemRef]
    components: KitComponentsSpec
    samples: NotRequired[dict]


# Alias for clarity at call sites that mean "a kit manifest"
KitManifest = KitSpec


# ---------------------------------------------------------------------------
# Pack manifest (§5.4)
# ---------------------------------------------------------------------------


class ManifestFormat(TypedDict):
    """Q16 resolved — format = "0.x" mouvant pendant track streamtex 0.7.x.

    validate_pack accepts any "0.x.y"; bumping to "1.0" requires one of:
    (i) ≥ 2 external packs beyond streamtex-design, OR
    (ii) 3-6 months of feedback, OR
    (iii) concrete frictions resolved (cf. §24.2).
    """

    format: str


class PackEntrypoint(TypedDict):
    module: str


class PackInfo(TypedDict):
    name: str
    version: str
    author: str
    license: str
    streamtex_compat: str


class PackDataSection(TypedDict, total=False):
    """Optional `[pack.data]` table (manifest 0.2+).

    Each key lists the artifact names of a given category that the pack ships.
    The list is the source-of-truth for discovery: an unlisted file on disk is
    not enumerated. Categories absent from this dict mean the pack does not
    provide that artifact kind.

    Cross-references: `streamtex.core.artifacts.spec.ArtifactKind`.
    """

    palettes: list[str]
    ai_prompts: list[str]
    archetypes: list[str]
    guidelines: list[str]
    skills: list[str]
    agents: list[str]
    assets: list[str]
    integrations: list[str]


class PackManifest(TypedDict):
    manifest: ManifestFormat
    pack: PackInfo
    entrypoint: PackEntrypoint
    scopes: NotRequired[dict]
    data: NotRequired[PackDataSection]  # manifest 0.2+, optional


# ---------------------------------------------------------------------------
# stx.toml [[packs]] entry (§5.4 — Q7 option α + Q17)
# ---------------------------------------------------------------------------

PackType = Literal["git", "local", "pypi"]


class StxTomlPackEntry(TypedDict):
    """Schema for `[[packs]]` entries in a project `stx.toml`.

    Distinct from PackManifest (which is the manifest a pack itself ships).
    Per-type field rules:

    * git: `ref` required, `rev` optional (tag/branch/SHA).
    * local: `name` + `path` required, `primary` optional (exactly one local
      pack may have primary=true per project — validated by Check 33).
      `editable` allowed only with type="local" (Check 33c).
    * pypi: `name` + `constraint` required.
    """

    type: PackType
    name: NotRequired[str]
    ref: NotRequired[str]
    rev: NotRequired[str]
    path: NotRequired[str]
    primary: NotRequired[bool]
    editable: NotRequired[bool]
    constraint: NotRequired[str]


__all__ = [
    "ColorsBundle",
    "TitlesBundle",
    "CalloutsBundle",
    "StatHeroBundle",
    "CardGridBundle",
    "ComparisonTableBundle",
    "TakeawaysBundle",
    "BodyBundle",
    "FontsBundle",
    "CitationBundle",
    "InlineEmphasisBundle",
    "ListsBundle",
    "REQUIRED_BUNDLES",
    "DesignSystemProtocol",
    "Granularity",
    "ComponentMeta",
    "KitDesignSystemRef",
    "KitComponentsSpec",
    "KitSpec",
    "KitManifest",
    "ManifestFormat",
    "PackDataSection",
    "PackEntrypoint",
    "PackInfo",
    "PackManifest",
    "PackType",
    "StxTomlPackEntry",
]
