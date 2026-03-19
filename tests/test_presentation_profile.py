"""Tests for streamtex.presentation_profile (Phases 1–3)."""

from __future__ import annotations

import pytest

from streamtex.presentation_profile import (
    _ACTIVE_PROFILE_KEY,
    _MODE_LABELS,
    PageLayout,
    PresentationProfile,
    ProfileConfig,
    SlideBreakDisplayConfig,
    ViewMode,
    apply_profile,
    build_default_profile,
    is_profile_modified,
)
from streamtex.slide import SlideBreakMode

# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def session_state(monkeypatch):
    """Provide an isolated dict as st.session_state for profile functions."""
    state: dict = {}
    monkeypatch.setattr("streamlit.session_state", state)
    return state


# ── PageLayout ────────────────────────────────────────────────────────────


class TestPageLayout:
    def test_defaults(self):
        layout = PageLayout()
        assert layout.width == 90
        assert layout.zoom == 100

    def test_custom(self):
        layout = PageLayout(width=40, zoom=150)
        assert layout.width == 40
        assert layout.zoom == 150

    def test_extreme_values(self):
        """No range limits — any numeric value is accepted."""
        layout = PageLayout(width=500, zoom=10)
        assert layout.width == 500
        assert layout.zoom == 10

    def test_negative_values(self):
        layout = PageLayout(width=-20, zoom=-50)
        assert layout.width == -20
        assert layout.zoom == -50

    def test_zero_values(self):
        layout = PageLayout(width=0, zoom=0)
        assert layout.width == 0
        assert layout.zoom == 0


# ── SlideBreakDisplayConfig ───────────────────────────────────────────────


class TestSlideBreakDisplayConfig:
    def test_defaults(self):
        config = SlideBreakDisplayConfig()
        assert config.enabled is True
        assert config.mode == SlideBreakMode.FULL
        assert config.space == 5

    def test_no_range_limit_on_space(self):
        config = SlideBreakDisplayConfig(space=200)
        assert config.space == 200
        config2 = SlideBreakDisplayConfig(space=-10)
        assert config2.space == -10


# ── ViewMode ──────────────────────────────────────────────────────────────


class TestViewMode:
    def test_values(self):
        assert ViewMode.PAGINATED.value == "Paginated"
        assert ViewMode.CONTINUOUS.value == "Continuous"


# ── PresentationProfile ──────────────────────────────────────────────────


class TestPresentationProfile:
    def test_name_only(self):
        p = PresentationProfile(name="Test")
        assert p.mode == ViewMode.PAGINATED
        assert p.layout.width == 90
        assert p.layout.zoom == 100
        assert p.wrap is True
        assert p.breaks.enabled is True
        assert p.breaks.mode == SlideBreakMode.FULL
        assert p.breaks.space == 5

    def test_flat_construction(self):
        p = PresentationProfile(
            name="Presenter",
            mode=ViewMode.PAGINATED,
            layout=PageLayout(width=100, zoom=100),
            wrap=False,
            breaks=SlideBreakDisplayConfig(
                enabled=True,
                mode=SlideBreakMode.FULL,
                space=100,
            ),
        )
        assert p.mode == ViewMode.PAGINATED
        assert p.layout.width == 100
        assert p.wrap is False
        assert p.breaks.space == 100

    def test_mobile_profile(self):
        """Standard mobile profile: full width, reduced zoom."""
        p = PresentationProfile(
            name="Mobile",
            layout=PageLayout(width=100, zoom=60),
            breaks=SlideBreakDisplayConfig(enabled=False),
        )
        assert p.layout.width == 100
        assert p.layout.zoom == 60
        assert p.mode == ViewMode.PAGINATED  # default
        assert p.wrap is True
        assert p.breaks.enabled is False
        assert p.breaks.space == 5


# ── build_default_profile ────────────────────────────────────────────────


class TestBuildDefaultProfile:
    def test_from_book_params(self):
        p = build_default_profile(page_width=80, zoom=90, paginate=True)
        assert p.name == "Default"
        assert p.layout.width == 80
        assert p.layout.zoom == 90
        assert p.mode == ViewMode.PAGINATED

    def test_defaults(self):
        p = build_default_profile()
        assert p.layout.width == 90
        assert p.layout.zoom == 100
        assert p.mode == ViewMode.CONTINUOUS


# ── apply_profile / is_profile_modified ──────────────────────────────────


class TestApplyProfile:
    def test_writes_all_keys(self, session_state):
        p = PresentationProfile(
            name="Test",
            mode=ViewMode.PAGINATED,
            layout=PageLayout(width=50, zoom=80),
            wrap=False,
            breaks=SlideBreakDisplayConfig(
                enabled=False,
                mode=SlideBreakMode.RULE_ONLY,
                space=30,
            ),
        )
        apply_profile(p)
        assert session_state[_ACTIVE_PROFILE_KEY] == "Test"
        # 7 field keys + 1 active profile key = 8
        assert len(session_state) == 8

    def test_extreme_values_applied(self, session_state):
        p = PresentationProfile(
            name="Extreme",
            layout=PageLayout(width=500, zoom=-20),
            breaks=SlideBreakDisplayConfig(space=999),
        )
        apply_profile(p)
        assert session_state[_ACTIVE_PROFILE_KEY] == "Extreme"


class TestIsProfileModified:
    def test_not_modified_after_apply(self, session_state):
        p = PresentationProfile("Test", layout=PageLayout(width=50, zoom=80))
        apply_profile(p)
        assert not is_profile_modified(p)

    def test_width_change_detected(self, session_state):
        from streamtex.zoom import _PAGE_WIDTH_KEY

        p = PresentationProfile("Test", layout=PageLayout(width=50, zoom=80))
        apply_profile(p)
        session_state[_PAGE_WIDTH_KEY] = 55
        assert is_profile_modified(p)

    def test_zoom_change_detected(self, session_state):
        from streamtex.zoom import _ZOOM_KEY

        p = PresentationProfile("Test", layout=PageLayout(width=50, zoom=80))
        apply_profile(p)
        session_state[_ZOOM_KEY] = 90
        assert is_profile_modified(p)

    def test_mode_change_detected(self, session_state):
        from streamtex.book import _STX_VIEW_MODE_KEY

        p = PresentationProfile("Test", mode=ViewMode.CONTINUOUS)
        apply_profile(p)
        session_state[_STX_VIEW_MODE_KEY] = "Paginated"
        assert is_profile_modified(p)

    def test_wrap_change_detected(self, session_state):
        from streamtex.code import _WRAP_ALL_KEY

        p = PresentationProfile("Test", wrap=True)
        apply_profile(p)
        session_state[_WRAP_ALL_KEY] = False
        assert is_profile_modified(p)

    def test_breaks_change_detected(self, session_state):
        from streamtex.slide import _BREAK_ENABLED_KEY

        p = PresentationProfile(
            "Test", breaks=SlideBreakDisplayConfig(enabled=True),
        )
        apply_profile(p)
        session_state[_BREAK_ENABLED_KEY] = False
        assert is_profile_modified(p)

    def test_restore_clears_modified(self, session_state):
        from streamtex.zoom import _PAGE_WIDTH_KEY

        p = PresentationProfile("Test", layout=PageLayout(width=50, zoom=80))
        apply_profile(p)
        session_state[_PAGE_WIDTH_KEY] = 55
        assert is_profile_modified(p)
        session_state[_PAGE_WIDTH_KEY] = 50
        assert not is_profile_modified(p)


# ── Profile list construction ─────────────────────────────────────────────


class TestProfileListConstruction:
    def test_default_always_first(self):
        user = [PresentationProfile("Mobile", layout=PageLayout(width=100, zoom=60))]
        default = build_default_profile(page_width=90, zoom=100)
        all_profiles = [default] + user
        assert all_profiles[0].name == "Default"
        assert all_profiles[1].name == "Mobile"

    def test_user_default_replaces_auto(self):
        user = [
            PresentationProfile("Default", layout=PageLayout(width=80, zoom=90)),
            PresentationProfile("Mobile", layout=PageLayout(width=100, zoom=60)),
        ]
        assert user[0].name == "Default"
        assert user[0].layout.width == 80

    def test_empty_user_profiles(self):
        default = build_default_profile()
        all_profiles = [default] + []
        assert len(all_profiles) == 1
        assert all_profiles[0].name == "Default"

    def test_duplicate_names_detected(self):
        profiles = [
            PresentationProfile("Mobile"),
            PresentationProfile("Mobile"),
        ]
        names = [p.name for p in profiles]
        assert len(set(names)) != len(names)


# ── Factory presets (Phase 2) ─────────────────────────────────────────────


class TestFactoryPresets:
    def test_responsive_preset(self):
        profiles = PresentationProfile.responsive_preset()
        assert len(profiles) == 3
        names = [p.name for p in profiles]
        assert names == ["Desktop", "Tablet", "Mobile"]
        mobile = profiles[2]
        assert mobile.layout.width == 100
        assert mobile.layout.zoom == 60
        assert mobile.breaks.enabled is False

    def test_presentation_preset(self):
        profiles = PresentationProfile.presentation_preset()
        assert len(profiles) == 3
        names = [p.name for p in profiles]
        assert names == ["Presenter", "Audience", "Handout"]
        presenter = profiles[0]
        assert presenter.mode == ViewMode.PAGINATED
        assert presenter.layout.width == 100
        assert presenter.breaks.space == 5
        handout = profiles[2]
        assert handout.breaks.enabled is False

    def test_desktop_mobile_preset(self):
        profiles = PresentationProfile.desktop_mobile_preset()
        assert len(profiles) == 2
        assert profiles[0].name == "Desktop"
        assert profiles[1].name == "Mobile"
        assert profiles[1].layout.zoom == 60
        assert profiles[1].breaks.enabled is False


# ── MODE_LABELS ───────────────────────────────────────────────────────────


class TestModeLabels:
    def test_all_modes_covered(self):
        assert SlideBreakMode.FULL in _MODE_LABELS
        assert SlideBreakMode.RULE_ONLY in _MODE_LABELS
        assert SlideBreakMode.SPACER_ONLY in _MODE_LABELS

    def test_reverse_lookup(self):
        reverse = {v: k for k, v in _MODE_LABELS.items()}
        assert reverse["Full"] == SlideBreakMode.FULL
        assert reverse["Rule only"] == SlideBreakMode.RULE_ONLY


# ── ProfileConfig — JSON serialization (Phase 3) ─────────────────────────


class TestProfileConfig:
    def test_round_trip(self):
        profiles = [
            PresentationProfile(
                name="Desktop",
                layout=PageLayout(width=90, zoom=100),
            ),
            PresentationProfile(
                name="Mobile",
                layout=PageLayout(width=100, zoom=60),
                breaks=SlideBreakDisplayConfig(enabled=False),
            ),
        ]
        config = ProfileConfig(name="test", profiles=profiles)
        json_str = config.to_json()
        restored = ProfileConfig.from_json(json_str)

        assert restored.name == "test"
        assert len(restored.profiles) == 2
        assert restored.profiles[0].name == "Desktop"
        assert restored.profiles[0].layout.width == 90
        assert restored.profiles[1].name == "Mobile"
        assert restored.profiles[1].layout.zoom == 60
        assert restored.profiles[1].breaks.enabled is False

    def test_save_load(self, tmp_path):
        config = ProfileConfig(
            name="file_test",
            profiles=[PresentationProfile("Test", layout=PageLayout(width=50))],
        )
        path = tmp_path / "config.json"
        config.save(path)
        restored = ProfileConfig.load(path)
        assert restored.name == "file_test"
        assert restored.profiles[0].layout.width == 50

    def test_extreme_values_serialized(self):
        config = ProfileConfig(
            name="extreme",
            profiles=[
                PresentationProfile(
                    "Big",
                    layout=PageLayout(width=500, zoom=-20),
                    breaks=SlideBreakDisplayConfig(space=999),
                ),
            ],
        )
        restored = ProfileConfig.from_json(config.to_json())
        assert restored.profiles[0].layout.width == 500
        assert restored.profiles[0].layout.zoom == -20
        assert restored.profiles[0].breaks.space == 999

    def test_version_field(self):
        config = ProfileConfig(name="v", profiles=[])
        data = config.to_dict()
        assert data["version"] == 1

    def test_mode_serialization(self):
        config = ProfileConfig(
            name="modes",
            profiles=[
                PresentationProfile("P", mode=ViewMode.PAGINATED),
                PresentationProfile("C", mode=ViewMode.CONTINUOUS),
            ],
        )
        restored = ProfileConfig.from_json(config.to_json())
        assert restored.profiles[0].mode == ViewMode.PAGINATED
        assert restored.profiles[1].mode == ViewMode.CONTINUOUS

    def test_break_mode_serialization(self):
        config = ProfileConfig(
            name="breaks",
            profiles=[
                PresentationProfile(
                    "A",
                    breaks=SlideBreakDisplayConfig(mode=SlideBreakMode.RULE_ONLY),
                ),
            ],
        )
        restored = ProfileConfig.from_json(config.to_json())
        assert restored.profiles[0].breaks.mode == SlideBreakMode.RULE_ONLY

    def test_wrap_serialization(self):
        config = ProfileConfig(
            name="wrap",
            profiles=[PresentationProfile("A", wrap=False)],
        )
        restored = ProfileConfig.from_json(config.to_json())
        assert restored.profiles[0].wrap is False

    def test_empty_profiles(self):
        config = ProfileConfig(name="empty", profiles=[])
        restored = ProfileConfig.from_json(config.to_json())
        assert restored.name == "empty"
        assert len(restored.profiles) == 0

    def test_to_dict_structure(self):
        config = ProfileConfig(
            name="test",
            profiles=[PresentationProfile("A", layout=PageLayout(width=50, zoom=75))],
        )
        d = config.to_dict()
        assert d["name"] == "test"
        assert d["version"] == 1
        assert len(d["profiles"]) == 1
        p = d["profiles"][0]
        assert p["name"] == "A"
        assert p["mode"] == "Paginated"
        assert p["layout"]["width"] == 50
        assert p["layout"]["zoom"] == 75
        assert p["wrap"] is True
        assert p["breaks"]["enabled"] is True
        assert p["breaks"]["mode"] == "Full"
        assert p["breaks"]["space"] == 5

    def test_from_dict_defaults(self):
        """Missing fields in JSON should use sensible defaults."""
        data = {
            "name": "minimal",
            "version": 1,
            "profiles": [{"name": "Simple"}],
        }
        config = ProfileConfig._from_dict(data)
        p = config.profiles[0]
        assert p.layout.width == 90
        assert p.layout.zoom == 100
        assert p.mode == ViewMode.PAGINATED
        assert p.wrap is True
        assert p.breaks.enabled is True
