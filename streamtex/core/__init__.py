"""StreamTeX reuse architecture — core contracts, validation, discovery.

This package is the foundation of the reuse architecture (cf.
documentation/maintenance/reuse-architecture/PLAN.md §5). It exposes:

* `contracts` — Protocols and TypedDicts that define design systems, components,
  kits, and packs.
* `validation` — pure functions that return ValidationIssue lists for a given
  component module / design system module / kit TOML / pack directory.
* `discovery` — runtime helpers to enumerate packs/components from an installed
  Python environment and from `stx.toml`.

The top-level `streamtex` package re-exports the three symbols pack authors use
most (`DesignSystemProtocol`, `ComponentMeta`, `ReuseArchitectureError`); the
remaining infrastructure stays under `streamtex.core.*` per the convention in
§5.0 of the plan.
"""

from streamtex.core import contracts, validation, discovery

__all__ = ["contracts", "validation", "discovery"]
