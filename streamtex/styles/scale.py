"""Indexed responsive font scale — Layer 1 (Python generator, v0.2 relative).

Loads scale_curves.toml at import time. The TOML now stores a single
``base_pt_desktop`` value plus 29 adimensional ratios per curve. All
pt values are *derived* — no absolute pt is stored except the base.

Exposes:

- ScaleCurve enum (named curves available in the TOML).
- ScaleConfig dataclass (per-document override).
- compute_scale(config) → (desktop, tablet, mobile) lists of pt ints.
- emit_scale_css(config) → CSS text for a <style> tag.
- emit_static_css() → CSS block matching default.css (count=29 default curve).

Run as ``python -m streamtex.styles.scale`` to print the static CSS block.

Changing ``base_pt_desktop`` in the TOML re-scales every palier, every
breakpoint, every curve proportionally. Per-document override via
``st_book(scale=ScaleConfig(base_pt_desktop=24))`` does the same at
runtime without editing the TOML.
"""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)

_CURVES_FILE = Path(__file__).parent / "scale_curves.toml"
_PALIER_COUNT_MAX = 29


def _load_curves() -> dict:
    """Load and validate scale_curves.toml (v0.2 schema).

    Validation:
    - schema_version is "0.2".
    - metadata has base_pt_desktop (positive int/float), base_idx
      (int in [0, 28]), tablet_scale + mobile_scale (positive floats).
    - Every curve has a ``ratios`` list of 29 positive floats.
    - ratios[base_idx] == 1.0 (the anchor).
    """
    with open(_CURVES_FILE, "rb") as f:
        data = tomllib.load(f)

    meta = data.get("metadata", {})
    if meta.get("schema_version") != "0.2":
        raise ValueError(
            f"scale_curves.toml: expected schema_version '0.2', "
            f"got {meta.get('schema_version')!r}. Run "
            f"`uv run python -m streamtex.scripts.migrate_curves_to_relative` "
            f"to migrate a v0.1 file."
        )
    base_pt = meta.get("base_pt_desktop")
    base_idx = meta.get("base_idx")
    tablet_scale = meta.get("tablet_scale")
    mobile_scale = meta.get("mobile_scale")
    if not (isinstance(base_pt, (int, float)) and base_pt > 0):
        raise ValueError(f"metadata.base_pt_desktop must be positive number, got {base_pt!r}.")
    if not (isinstance(base_idx, int) and 0 <= base_idx < _PALIER_COUNT_MAX):
        raise ValueError(
            f"metadata.base_idx must be int in [0, {_PALIER_COUNT_MAX - 1}], got {base_idx!r}."
        )
    if not (isinstance(tablet_scale, (int, float)) and tablet_scale > 0):
        raise ValueError(f"metadata.tablet_scale must be positive number, got {tablet_scale!r}.")
    if not (isinstance(mobile_scale, (int, float)) and mobile_scale > 0):
        raise ValueError(f"metadata.mobile_scale must be positive number, got {mobile_scale!r}.")

    for name, curve in data.items():
        if name == "metadata":
            continue
        ratios = curve.get("ratios")
        if not isinstance(ratios, list) or len(ratios) != _PALIER_COUNT_MAX:
            raise ValueError(
                f"scale_curves.toml[{name}].ratios: must be a list of "
                f"{_PALIER_COUNT_MAX} numbers (got {type(ratios).__name__} "
                f"len={len(ratios) if isinstance(ratios, list) else 'N/A'})."
            )
        if not all(isinstance(r, (int, float)) and r > 0 for r in ratios):
            raise ValueError(
                f"scale_curves.toml[{name}].ratios: all values must be positive numbers."
            )
        if abs(ratios[base_idx] - 1.0) > 1e-6:
            raise ValueError(
                f"scale_curves.toml[{name}].ratios[{base_idx}] must equal 1.0 "
                f"(the base anchor), got {ratios[base_idx]}."
            )
        if ratios != sorted(ratios):
            logger.warning(
                "scale_curves.toml[%s].ratios: not monotonically non-decreasing — "
                "visual inconsistency risk.",
                name,
            )
    return data


_CURVES = _load_curves()
_META = _CURVES["metadata"]
_BASE_PT_DESKTOP_DEFAULT = float(_META["base_pt_desktop"])
_BASE_IDX_DEFAULT = int(_META["base_idx"])
_TABLET_SCALE_DEFAULT = float(_META["tablet_scale"])
_MOBILE_SCALE_DEFAULT = float(_META["mobile_scale"])


class ScaleCurve(str, Enum):
    """Named curves available in scale_curves.toml. Values match TOML section names."""

    WORD_PROCESSOR = "word_processor"
    GEOMETRIC = "geometric"
    BODY_CENTRIC = "body_centric"
    BELL = "bell"


_DEFAULT_CURVE = ScaleCurve(_META.get("default_curve", "word_processor"))


@dataclass(frozen=True)
class ScaleConfig:
    """Per-document scale configuration.

    All four override fields default to ``None`` → use the TOML metadata.
    Set any field to a positive number to override at this document.

    Args:
        curve: A named ScaleCurve or a list of 29 numbers. If a list,
            interpreted as RATIOS (v0.2 schema). Legacy v0.1 callers
            who passed a list of 29 ints (typically values >= 6) get
            a deprecation warning + auto-conversion: the list is
            normalized by dividing each value by element at base_idx.
        count: Number of paliers used (1 to 29). Default 20.
        base_pt_desktop: Override the metadata base. Default None.
        base_idx: Override the metadata base index. Default None.
        tablet_scale: Override the metadata tablet shrink factor. Default None.
        mobile_scale: Override the metadata mobile shrink factor. Default None.
        custom_desktop / custom_tablet / custom_mobile: last-resort
            raw pt overrides (lists of N ints) — kept for backward
            compat. Used AFTER base+ratios computation.
    """

    curve: Union[ScaleCurve, list] = _DEFAULT_CURVE
    count: int = 20
    base_pt_desktop: Optional[float] = None
    base_idx: Optional[int] = None
    tablet_scale: Optional[float] = None
    mobile_scale: Optional[float] = None
    custom_desktop: Optional[list] = None
    custom_tablet: Optional[list] = None
    custom_mobile: Optional[list] = None

    def __post_init__(self):
        if not (1 <= self.count <= _PALIER_COUNT_MAX):
            raise ValueError(
                f"ScaleConfig.count must be between 1 and {_PALIER_COUNT_MAX}, got {self.count}."
            )
        if self.base_pt_desktop is not None and self.base_pt_desktop <= 0:
            raise ValueError(f"ScaleConfig.base_pt_desktop must be positive, got {self.base_pt_desktop}.")
        if self.base_idx is not None and not (0 <= self.base_idx < _PALIER_COUNT_MAX):
            raise ValueError(
                f"ScaleConfig.base_idx must be in [0, {_PALIER_COUNT_MAX - 1}], got {self.base_idx}."
            )
        if self.tablet_scale is not None and self.tablet_scale <= 0:
            raise ValueError(f"ScaleConfig.tablet_scale must be positive, got {self.tablet_scale}.")
        if self.mobile_scale is not None and self.mobile_scale <= 0:
            raise ValueError(f"ScaleConfig.mobile_scale must be positive, got {self.mobile_scale}.")


def _resolve_ratios(config: ScaleConfig, base_idx: int) -> list:
    """Resolve the ratios list for the given curve.

    Handles the legacy compat shim: if curve is a list of 29 ints all
    >= 6, treat it as v0.1 absolute pt values and normalize by anchor.
    """
    if isinstance(config.curve, ScaleCurve):
        return list(_CURVES[config.curve.value]["ratios"])
    if isinstance(config.curve, list):
        if len(config.curve) != _PALIER_COUNT_MAX:
            raise ValueError(
                f"Custom curve must have exactly {_PALIER_COUNT_MAX} values, "
                f"got {len(config.curve)}."
            )
        # Legacy shim: if all ints AND all >= 6, treat as v0.1 absolute pt values
        all_ints = all(isinstance(v, int) for v in config.curve)
        all_large = all(v >= 6 for v in config.curve)
        if all_ints and all_large:
            logger.warning(
                "ScaleConfig.curve passed as list of ints >= 6 — interpreting as "
                "legacy v0.1 absolute-pt list and normalizing to ratios. Migrate "
                "to ScaleConfig(curve=ScaleCurve.X, base_pt_desktop=Y) for clarity."
            )
            anchor = config.curve[base_idx]
            if anchor == 0:
                raise ValueError(f"Legacy curve has 0 at base_idx={base_idx}.")
            return [v / anchor for v in config.curve]
        # Otherwise: treat as ratios (v0.2)
        if abs(config.curve[base_idx] - 1.0) > 1e-6:
            logger.warning(
                "Inline ratios list: ratios[%d] = %s ≠ 1.0 — base palier may not "
                "match base_pt_desktop. Normalizing.",
                base_idx, config.curve[base_idx],
            )
            anchor = config.curve[base_idx]
            return [r / anchor for r in config.curve]
        return list(config.curve)
    raise TypeError(
        f"ScaleConfig.curve must be ScaleCurve or list, got {type(config.curve).__name__}."
    )


def compute_scale(config: ScaleConfig) -> tuple[list, list, list]:
    """Compute (desktop, tablet, mobile) lists of ``config.count`` pt values.

    Algorithm:
      desktop[i] = round(base_pt_desktop * ratios[i])
      tablet[i]  = round(desktop[i]    * tablet_scale)
      mobile[i]  = round(desktop[i]    * mobile_scale)

    custom_{desktop,tablet,mobile} are applied AFTER the computation
    (last-resort override).
    """
    base_pt = config.base_pt_desktop if config.base_pt_desktop is not None else _BASE_PT_DESKTOP_DEFAULT
    base_idx = config.base_idx if config.base_idx is not None else _BASE_IDX_DEFAULT
    tablet_k = config.tablet_scale if config.tablet_scale is not None else _TABLET_SCALE_DEFAULT
    mobile_k = config.mobile_scale if config.mobile_scale is not None else _MOBILE_SCALE_DEFAULT

    ratios = _resolve_ratios(config, base_idx)

    desktop = [max(1, round(base_pt * r)) for r in ratios]
    tablet = [max(1, round(v * tablet_k)) for v in desktop]
    mobile = [max(1, round(v * mobile_k)) for v in desktop]

    if config.custom_desktop:
        desktop = list(config.custom_desktop)
    if config.custom_tablet:
        tablet = list(config.custom_tablet)
    if config.custom_mobile:
        mobile = list(config.custom_mobile)

    return desktop[: config.count], tablet[: config.count], mobile[: config.count]


def emit_scale_css(config: Optional[ScaleConfig] = None) -> str:
    """Generate the :root + @media query CSS block for a given config.

    If ``config`` is None, uses the default curve at count=29 (matches default.css).
    """
    config = config or ScaleConfig(count=_PALIER_COUNT_MAX)
    desktop, tablet, mobile = compute_scale(config)

    lines = [":root {"]
    for i, v in enumerate(desktop):
        lines.append(f"    --stx-scale-{i}: {v}pt;")
    lines.append("}")

    lines.append("@media (max-width: 1024px) { :root {")
    for i, v in enumerate(tablet):
        lines.append(f"    --stx-scale-{i}: {v}pt;")
    lines.append("} }")

    lines.append("@media (max-width: 480px) { :root {")
    for i, v in enumerate(mobile):
        lines.append(f"    --stx-scale-{i}: {v}pt;")
    lines.append("} }")

    return "\n".join(lines)


def emit_static_css() -> str:
    """CSS block embedded in default.css (default curve, count=29)."""
    return emit_scale_css(ScaleConfig(count=_PALIER_COUNT_MAX))


if __name__ == "__main__":
    print(emit_static_css())
