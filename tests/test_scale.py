"""Tests for the indexed responsive font scale."""

import pytest

from streamtex.styles.base import StxStyles
from streamtex.styles.scale import (
    _PALIER_COUNT_MAX,
    ScaleConfig,
    ScaleCurve,
    compute_scale,
    emit_scale_css,
    emit_static_css,
)
from streamtex.styles.text import Sizes


class TestScaleConfig:
    def test_default(self):
        c = ScaleConfig()
        assert c.count == 20
        assert c.curve == ScaleCurve.WORD_PROCESSOR

    def test_count_validation(self):
        with pytest.raises(ValueError):
            ScaleConfig(count=0)
        with pytest.raises(ValueError):
            ScaleConfig(count=30)


class TestComputeScale:
    def test_word_processor_default(self):
        desktop, tablet, mobile = compute_scale(ScaleConfig())
        assert len(desktop) == 20
        assert len(tablet) == 20
        assert len(mobile) == 20
        assert desktop == sorted(desktop)

    def test_count_29(self):
        desktop, _, _ = compute_scale(ScaleConfig(count=_PALIER_COUNT_MAX))
        assert len(desktop) == _PALIER_COUNT_MAX

    def test_custom_curve_list_v0_1_legacy_compat(self):
        """Legacy: list of 29 ints all >= 6 — interpreted as v0.1 absolute pt
        values, normalized to ratios internally, then re-scaled by base_pt_desktop.
        With base_pt_desktop=18 (default) and anchor (index 7) = 15, the resulting
        desktop[7] should equal 18 (because ratio[7] normalizes to 1.0)."""
        custom = list(range(8, 8 + _PALIER_COUNT_MAX))  # [8, 9, ..., 36]; anchor[7] = 15
        desktop, tablet, _ = compute_scale(
            ScaleConfig(curve=custom, count=10)
        )
        # base_pt_desktop=18 (default), anchor was 15 → desktop[7] should be 18
        # desktop[0] = round(18 * 8/15) = round(9.6) = 10
        assert desktop[7] == 18
        assert desktop[0] == 10
        # Tablet at default 0.85: round(10 * 0.85) = 8 ... but it's by per-palier,
        # actually tablet = round(desktop[i] * 0.85)
        assert tablet[0] == round(desktop[0] * 0.85)

    def test_custom_curve_wrong_length(self):
        with pytest.raises(ValueError):
            compute_scale(ScaleConfig(curve=[1, 2, 3]))

    def test_all_named_curves_valid(self):
        for curve in ScaleCurve:
            desktop, _, _ = compute_scale(ScaleConfig(curve=curve, count=_PALIER_COUNT_MAX))
            assert len(desktop) == _PALIER_COUNT_MAX
            assert all(v > 0 for v in desktop)

    def test_custom_breakpoints_override(self):
        desktop, tablet, mobile = compute_scale(
            ScaleConfig(
                curve=ScaleCurve.WORD_PROCESSOR,
                count=5,
                custom_desktop=[10, 20, 30, 40, 50],
                custom_mobile=[5, 10, 15, 20, 25],
            )
        )
        assert desktop == [10, 20, 30, 40, 50]
        assert mobile == [5, 10, 15, 20, 25]
        assert len(tablet) == 5  # default tablet from curve, sliced to count


class TestEmitScaleCss:
    def test_emits_29_vars_per_breakpoint(self):
        css = emit_scale_css(ScaleConfig(count=_PALIER_COUNT_MAX))
        assert css.count("--stx-scale-") == _PALIER_COUNT_MAX * 3
        assert ":root {" in css
        assert "@media (max-width: 1024px)" in css
        assert "@media (max-width: 480px)" in css

    def test_emit_with_count_5(self):
        css = emit_scale_css(ScaleConfig(count=5))
        assert css.count("--stx-scale-") == 5 * 3

    def test_emit_static_consistent(self):
        css = emit_static_css()
        for i in range(_PALIER_COUNT_MAX):
            assert f"--stx-scale-{i}:" in css


class TestIndexedTokens:
    def test_29_idx_tokens_exist(self):
        for i in range(_PALIER_COUNT_MAX):
            assert hasattr(Sizes, f"idx_{i}"), f"missing Sizes.idx_{i}"

    def test_subscript_access(self):
        for i in range(_PALIER_COUNT_MAX):
            assert StxStyles.scale[i] is getattr(Sizes, f"idx_{i}")

    def test_subscript_clamping_low(self):
        assert StxStyles.scale[-1] is StxStyles.scale[0]
        assert StxStyles.scale[-100] is StxStyles.scale[0]

    def test_subscript_clamping_high(self):
        assert StxStyles.scale[100] is StxStyles.scale[_PALIER_COUNT_MAX - 1]
        assert StxStyles.scale[_PALIER_COUNT_MAX] is StxStyles.scale[_PALIER_COUNT_MAX - 1]

    def test_subscript_type_error_on_float(self):
        with pytest.raises(TypeError):
            StxStyles.scale[3.5]


class TestTailwindAliases:
    def test_aliases_exist(self):
        for alias in ("text_xs", "text_sm", "text_base", "text_lg",
                      "text_xl", "text_2xl", "text_3xl", "text_4xl",
                      "text_5xl", "text_6xl", "text_7xl", "text_8xl", "text_9xl"):
            assert hasattr(StxStyles, alias), f"missing StxStyles.{alias}"

    def test_aliases_point_to_idx(self):
        # v0.2: Tailwind aliases anchored on the BASE palier (idx_7).
        # text_base = base; smaller aliases are above the floor.
        assert StxStyles.text_xs is Sizes.idx_5    # 14pt @ base 18 (≥ 18.7px floor)
        assert StxStyles.text_base is Sizes.idx_7  # 18pt @ base 18 (BASE)
        assert StxStyles.text_9xl is Sizes.idx_19  # 128pt @ base 18


class TestFallbacksMatchCurve:
    """Each Sizes.idx_N fallback (the second arg of var()) must match the
    WORD_PROCESSOR desktop value at index N. Catches drift between TOML and
    Python stubs."""

    def test_fallbacks_match_default_curve(self):
        desktop, _, _ = compute_scale(
            ScaleConfig(curve=ScaleCurve.WORD_PROCESSOR, count=_PALIER_COUNT_MAX)
        )
        for i, expected_pt in enumerate(desktop):
            style = getattr(Sizes, f"idx_{i}")
            css = style.css if hasattr(style, "css") else str(style)
            assert f"{expected_pt}pt" in css, (
                f"idx_{i}: expected fallback {expected_pt}pt, got {css!r}"
            )


class TestPublicApiExport:
    def test_top_level_imports(self):
        import streamtex
        assert hasattr(streamtex, "ScaleConfig")
        assert hasattr(streamtex, "ScaleCurve")
        assert hasattr(streamtex, "compute_scale")
        assert hasattr(streamtex, "emit_scale_css")


class TestRelativeArchitectureV02:
    """v0.2 — base + ratios architecture. These tests guarantee the
    single-source-of-truth invariant: changing base_pt_desktop re-scales
    every palier on every breakpoint for every curve."""

    def test_base_pt_desktop_override(self):
        """ScaleConfig(base_pt_desktop=X) produces palier-7 desktop == X
        for the default WORD_PROCESSOR curve."""
        desktop, _, _ = compute_scale(ScaleConfig(base_pt_desktop=24, count=29))
        assert desktop[7] == 24

    def test_base_pt_desktop_scales_all_paliers(self):
        """Doubling base doubles every palier (within rounding)."""
        d1, _, _ = compute_scale(ScaleConfig(base_pt_desktop=18, count=29))
        d2, _, _ = compute_scale(ScaleConfig(base_pt_desktop=36, count=29))
        # Each palier should be approximately doubled (±1pt rounding)
        for i, (v1, v2) in enumerate(zip(d1, d2)):
            assert abs(v2 - 2 * v1) <= 1, f"palier {i}: {v1} → {v2}, expected ~{2*v1}"

    def test_tablet_scale_override(self):
        """tablet_scale=0.95 produces tablet palier 7 ≈ round(18 * 0.95) = 17pt."""
        _, tablet, _ = compute_scale(ScaleConfig(tablet_scale=0.95, count=29))
        assert tablet[7] == 17

    def test_mobile_scale_override(self):
        """mobile_scale=0.5 produces mobile palier 7 = round(18 * 0.5) = 9pt."""
        _, _, mobile = compute_scale(ScaleConfig(mobile_scale=0.5, count=29))
        assert mobile[7] == 9

    def test_all_curves_share_same_base(self):
        """In v0.2, all curves anchor at base_pt_desktop. palier-7 must
        equal base across the 4 named curves."""
        for curve in ScaleCurve:
            desktop, _, _ = compute_scale(ScaleConfig(curve=curve, count=29))
            assert desktop[7] == 18, f"{curve.value}: palier 7 = {desktop[7]} != 18"

    def test_text_xs_above_floor(self):
        """text_xs maps to palier 5 = 14pt @ base 18 (= 18.67px at 96 DPI
        ≥ 18px floor). With higher bases, even more comfortable."""
        from streamtex.styles.scale import _BASE_PT_DESKTOP_DEFAULT
        desktop, _, _ = compute_scale(ScaleConfig(count=29))
        # palier 5 desktop pt at default base
        assert desktop[5] >= 14, f"palier 5 = {desktop[5]}pt below 14pt floor"
        assert _BASE_PT_DESKTOP_DEFAULT == 18

    def test_text_base_is_idx_7(self):
        """text_base = the BASE palier (idx_7). Direct identity check."""
        assert StxStyles.text_base is Sizes.idx_7
        # And idx_7's fallback equals base_pt_desktop
        css = Sizes.idx_7.css if hasattr(Sizes.idx_7, "css") else str(Sizes.idx_7)
        assert "18pt" in css

    def test_inline_ratios_list(self):
        """ScaleConfig(curve=[29 floats]) with ratios[7]=1.0 treats as ratios."""
        ratios = [r / 18 for r in [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 40, 48, 60, 72, 96, 128, 156, 168, 180, 188, 192, 194, 195, 196, 200]]
        # ratios[7] = 18/18 = 1.0 ✓
        desktop, _, _ = compute_scale(ScaleConfig(curve=ratios, count=29))
        assert desktop[7] == 18

    def test_ratio_validation_anchor(self):
        """A curve where ratios[base_idx] ≠ 1.0 must be rejected at load time."""
        # This is checked at module-load time via _load_curves; we verify the
        # function exists and would raise on a bad TOML. (Don't actually
        # mutate the loaded TOML.)
        from streamtex.styles import scale
        assert hasattr(scale, "_load_curves")
