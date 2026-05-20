"""One-shot migration: convert v0.1 (absolute pt values) scale_curves.toml
to v0.2 (relative ratios + single base) format.

Run from the streamtex repo root:

    uv run python -m streamtex.scripts.migrate_curves_to_relative > /tmp/scale_curves_v2.toml

Then inspect the output, validate the round-trip, and replace the TOML.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# Tuning knobs for the v0.2 schema. base_idx = 7 is the natural anchor
# because palier 7 was 18pt in word_processor (the design intent of the
# original v0.1 curves).
BASE_PT_DESKTOP = 18
BASE_IDX = 7
TABLET_SCALE = 0.85
MOBILE_SCALE = 0.70
DEFAULT_CURVE = "word_processor"

CURVE_NAMES = ("word_processor", "geometric", "body_centric", "bell")


def _format_ratios(ratios: list[float]) -> str:
    """Pretty-print ratios on multiple lines for readability."""
    formatted = [f"{r:.3f}" for r in ratios]
    # Group by 7 per line (roughly aligned with paliers)
    lines = []
    for i in range(0, len(formatted), 7):
        lines.append("  " + ", ".join(formatted[i : i + 7]))
    return "[\n" + ",\n".join(lines) + ",\n]"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    old_path = repo_root / "streamtex" / "styles" / "scale_curves.toml"
    with open(old_path, "rb") as f:
        old = tomllib.load(f)

    out: list[str] = []
    out.append("# streamtex/styles/scale_curves.toml — v0.2 (relative architecture)")
    out.append("#")
    out.append("# Single source of truth for the indexed responsive font scale.")
    out.append("# ALL values derive from base_pt_desktop + ratios:")
    out.append("#   desktop[i] = round(base_pt_desktop * ratios[i])")
    out.append("#   tablet[i]  = round(desktop[i] * tablet_scale)")
    out.append("#   mobile[i]  = round(desktop[i] * mobile_scale)")
    out.append("#")
    out.append("# Each curve provides 29 adimensional ratios; position [base_idx]")
    out.append("# MUST equal 1.0 by construction (the BASE palier).")
    out.append("#")
    out.append("# After editing, regenerate the static CSS block:")
    out.append("#   uv run python -m streamtex.styles.scale > /tmp/scale_block.css")
    out.append("# Then paste the output into streamtex/static/default.css.")
    out.append("# Also regenerate the Python idx_N fallbacks:")
    out.append("#   uv run python -m streamtex.scripts.regenerate_idx_fallbacks")
    out.append("")
    out.append("[metadata]")
    out.append('schema_version = "0.2"')
    out.append(f"base_pt_desktop = {BASE_PT_DESKTOP}")
    out.append(f"base_idx = {BASE_IDX}")
    out.append(f"tablet_scale = {TABLET_SCALE}")
    out.append(f"mobile_scale = {MOBILE_SCALE}")
    out.append(f'default_curve = "{DEFAULT_CURVE}"')
    out.append("")

    for name in CURVE_NAMES:
        if name not in old:
            print(f"WARN: curve {name!r} missing in old TOML", file=sys.stderr)
            continue
        desktop_old = old[name]["desktop"]
        anchor = desktop_old[BASE_IDX]
        if anchor == 0:
            print(f"FATAL: curve {name!r} has 0 at base_idx={BASE_IDX}", file=sys.stderr)
            return 1
        # Compute ratios relative to the anchor (NOT to BASE_PT_DESKTOP).
        # The new base_pt_desktop becomes the new global scale; ratios
        # carry the curve's silhouette.
        ratios = [round(v / anchor, 3) for v in desktop_old]
        # Sanity check: ratios[BASE_IDX] must be 1.0 exactly
        ratios[BASE_IDX] = 1.000
        out.append(f"[{name}]")
        out.append(f'description = "{old[name].get("description", "")}"')
        out.append(f"ratios = {_format_ratios(ratios)}")
        out.append("")

        # Diagnostic to stderr: what the round-trip will produce vs original
        print(f"# {name} round-trip diagnostic (desktop):", file=sys.stderr)
        for i, r in enumerate(ratios):
            roundtrip = round(BASE_PT_DESKTOP * r)
            delta = roundtrip - desktop_old[i]
            mark = "" if abs(delta) <= 1 else "  <<< DELTA > 1pt"
            print(
                f"  idx_{i:2d}: was {desktop_old[i]:4d}pt, ratio {r:.3f} → {roundtrip:4d}pt (Δ={delta:+d}){mark}",
                file=sys.stderr,
            )

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
