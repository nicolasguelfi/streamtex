"""ScaleConfig.amphi(): the lecture-hall scale preset (#84)."""

import streamtex as stx


def test_scale_amphi_preset_and_override():
    a = stx.ScaleConfig.amphi()
    assert (a.base_pt_desktop, a.tablet_scale, a.mobile_scale) == (30, 0.70, 0.55)
    b = stx.ScaleConfig.amphi(base_pt_desktop=28)
    assert b.base_pt_desktop == 28 and b.mobile_scale == 0.55
    assert stx.ScaleConfig.amphi() == stx.ScaleConfig(base_pt_desktop=30, tablet_scale=0.7, mobile_scale=0.55)
