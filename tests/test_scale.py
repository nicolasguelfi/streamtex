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

    def test_custom_curve_list(self):
        custom = list(range(8, 8 + _PALIER_COUNT_MAX))
        desktop, tablet, _ = compute_scale(
            ScaleConfig(curve=custom, count=10)
        )
        assert desktop == custom[:10]
        assert tablet[0] == max(1, int(custom[0] * 0.75))

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
        assert StxStyles.text_xs is Sizes.idx_2
        assert StxStyles.text_base is Sizes.idx_4
        assert StxStyles.text_9xl is Sizes.idx_19


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
