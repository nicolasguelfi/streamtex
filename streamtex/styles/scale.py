"""Indexed responsive font scale — Layer 1 (Python generator).

Loads scale_curves.toml at import time and exposes:

- ScaleCurve enum (named curves available in the TOML)
- ScaleConfig dataclass (per-document override)
- compute_scale(config) → (desktop, tablet, mobile) lists of pt ints
- emit_scale_css(config) → CSS text for a <style> tag
- emit_static_css() → CSS block matching default.css (count=29 default curve)

Run as ``python -m streamtex.styles.scale`` to print the static CSS block
that lives in default.css.
"""

from __future__ import annotations

import logging
import math
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)

_CURVES_FILE = Path(__file__).parent / "scale_curves.toml"
_PALIER_COUNT_MAX = 29


def _load_curves() -> dict:
    """Load and validate scale_curves.toml.

    Validation rules:
    - Every curve entry has exactly 29 ints per breakpoint.
    - All values are positive integers.
    - Monotonic non-decreasing emits a warning (not an error).
    """
    with open(_CURVES_FILE, "rb") as f:
        data = tomllib.load(f)
    for name, curve in data.items():
        if name == "metadata":
            continue
        for bp in ("desktop", "tablet", "mobile"):
            values = curve.get(bp)
            if not isinstance(values, list) or len(values) != _PALIER_COUNT_MAX:
                raise ValueError(
                    f"scale_curves.toml[{name}].{bp}: must be a list of "
                    f"{_PALIER_COUNT_MAX} integers (got {type(values).__name__} "
                    f"len={len(values) if isinstance(values, list) else 'N/A'})."
                )
            if not all(isinstance(v, int) and v > 0 for v in values):
                raise ValueError(
                    f"scale_curves.toml[{name}].{bp}: all values must be positive ints."
                )
            if values != sorted(values):
                logger.warning(
                    "scale_curves.toml[%s].%s: values are not monotonically "
                    "non-decreasing — visual inconsistency risk.",
                    name, bp,
                )
    return data


_CURVES = _load_curves()


class ScaleCurve(str, Enum):
    """Named curves available in scale_curves.toml. Values match TOML section names."""

    WORD_PROCESSOR = "word_processor"
    GEOMETRIC = "geometric"
    BODY_CENTRIC = "body_centric"
    BELL = "bell"


_DEFAULT_CURVE = ScaleCurve(_CURVES.get("metadata", {}).get("default_curve", "word_processor"))


@dataclass(frozen=True)
class ScaleConfig:
    """Per-document scale configuration.

    Args:
        curve: A named ScaleCurve or a custom list of 29 ints (desktop only —
            tablet/mobile derived at 75% / 60%).
        count: Number of paliers used (1 to 29). Default 20.
        custom_desktop / custom_tablet / custom_mobile: Optional lists of N ints
            overriding the curve. Must have ``count`` elements when used.
    """

    curve: Union[ScaleCurve, list] = _DEFAULT_CURVE
    count: int = 20
    custom_desktop: Optional[list] = None
    custom_tablet: Optional[list] = None
    custom_mobile: Optional[list] = None

    def __post_init__(self):
        if not (1 <= self.count <= _PALIER_COUNT_MAX):
            raise ValueError(
                f"ScaleConfig.count must be between 1 and {_PALIER_COUNT_MAX}, "
                f"got {self.count}."
            )


def compute_scale(config: ScaleConfig) -> tuple[list, list, list]:
    """Compute (desktop, tablet, mobile) lists of ``config.count`` pt values."""
    if isinstance(config.curve, ScaleCurve):
        curve_data = _CURVES[config.curve.value]
        desktop = list(curve_data["desktop"])
        tablet = list(curve_data["tablet"])
        mobile = list(curve_data["mobile"])
    elif isinstance(config.curve, list):
        if len(config.curve) != _PALIER_COUNT_MAX:
            raise ValueError(
                f"Custom curve must have exactly {_PALIER_COUNT_MAX} values, "
                f"got {len(config.curve)}."
            )
        desktop = list(config.curve)
        tablet = [max(1, math.floor(v * 0.75)) for v in desktop]
        mobile = [max(1, math.floor(v * 0.60)) for v in desktop]
    else:
        raise TypeError(
            f"ScaleConfig.curve must be ScaleCurve or list[int], "
            f"got {type(config.curve).__name__}."
        )

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
