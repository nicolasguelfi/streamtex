"""st_countdown: validation, grid, CountdownConfig.resolve and the exported markup (#52)."""
import html
import json
import re

import pytest

import streamtex.export as export_mod
from streamtex import CountdownConfig, st_countdown
from streamtex.countdown import _grid
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer


@pytest.fixture(autouse=True)
def _export_buffer():
    reset_export_buffer(ExportConfig(enabled=True))
    yield
    export_mod._buffer = None


def _racks(page: str) -> list[dict]:
    return [json.loads(html.unescape(m)) for m in re.findall(r'data-stx-countdown="([^"]*)"', page)]


def _export(*calls, raw: bool = False) -> str:
    """The exported page; without its <style> and <script> blocks unless *raw*."""
    for steps, kw in calls:
        st_countdown(steps, **kw)
    page = generate_export_html()
    return page if raw else re.sub(r"<(style|script)>.*?</\1>", "", page, flags=re.S)


# -- grid ----------------------------------------------------------------------------

@pytest.mark.parametrize("n,expected", [(1, (1, 1)), (3, (2, 2)), (4, (2, 2)), (5, (2, 3)), (7, (3, 3))])
def test_default_grid_is_compact(n, expected):
    assert _grid(n, None) == expected


def test_grid_too_small_or_malformed():
    with pytest.raises(ValueError, match="too small"):
        st_countdown([("a", 1), ("b", 1), ("c", 1)], grid=(1, 2))
    for bad in ((2,), (1, 2, 3), ("1", 2), (1.0, 2), (0, 3)):
        with pytest.raises(ValueError):
            st_countdown([("a", 1)], grid=bad)


def test_explicit_grid_and_rack_height_in_the_markup():
    page = _export(([("a", 1), ("b", 1)], {"grid": (1, 3), "rack_vh": 40}))
    assert "grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(1,minmax(0,1fr));" \
           "height:40vh" in page


# -- validation ------------------------------------------------------------------------

@pytest.mark.parametrize("steps,kw,match", [
    ([], {}, "empty"),
    ([("a", 1)], {"mode": "relay"}, "mode"),
    ([("a", 0)], {}, "minutes > 0"),
    ([("a", -1)], {}, "minutes > 0"),
    ([("a", "5")], {}, "minutes > 0"),
    ([("a",)], {}, "label, target"),
    ([(3, 1)], {}, "label must be a string"),
    ([("a", 1, {"type": "timer"})], {}, "unknown type"),
    ([("a", 1, {"colour": "red"})], {}, "unknown option"),
    ([("a", 1, {"tz": "Europe/Paris"})], {}, "only apply to type='clock'"),
    ([("a", None, {"type": "clock"})], {}, "needs 'tz'"),
    ([("a", None, {"type": "clock", "tz": "Mars/Olympus"})], {}, "unknown time zone"),
    ([("a", "25:00", {"type": "clock", "tz": "UTC"})], {}, "HH:MM"),
    ([("a", "9h30", {"type": "clock", "tz": "UTC"})], {}, "HH:MM"),
    ([("a", -2, {"type": "stopwatch"})], {}, "stopwatch target"),
    ([("a", None, {"type": "stopwatch", "alarm": "bell"})], {}, "never ring"),
    ([("a", None, {"type": "clock", "tz": "UTC", "alarm": "gong"})], {}, "never ring"),
    ([("a", 1, "siren")], {}, "unknown alarm"),
    ([("a", 1, {"volume": 1.5})], {}, r"outside \[0, 1\]"),
    ([("a", 1, {"duration": 61})], {}, r"outside \]0, 60\]"),
    ([("a", 1, {"label_scale": 0})], {}, r"outside \]0, 100\]"),
    ([("a", 1, 3)], {}, "3rd item"),
    ([("a", 1)], {"config": CountdownConfig(alarm="siren")}, "unknown alarm"),
    ([("a", 1)], {"config": CountdownConfig(alarm_volume=-0.1)}, r"outside \[0, 1\]"),
    ([("a", 1)], {"config": CountdownConfig(alarm_duration=0)}, r"outside \]0, 60\]"),
    ([("a", 1)], {"rack_vh": 0}, "positive"),
    ([("a", 1)], {"digits_width": 120}, r"outside \]0, 100\]"),
])
def test_bad_input_fails_loudly(steps, kw, match):
    with pytest.raises(ValueError, match=match):
        st_countdown(steps, **kw)


def test_cards_carry_their_type_target_and_alarm():
    page = _export(([
        ("Talk", 0.5),
        ("Overtime", 2, {"type": "stopwatch"}),
        ("Free", None, {"type": "stopwatch"}),
        ("Now", None, {"type": "clock", "tz": "America/New_York"}),
        ("Resume", "9:05", {"type": "clock", "tz": "Asia/Tokyo", "city": "東京"}),
        ("Quiet", 1, "off"),
        ("Loud", 1, {"alarm": "gong", "volume": 1, "duration": 6}),
    ], {"config": CountdownConfig(alarm="bell", alarm_volume=0.5)}))
    cards = _racks(page)[0]["cards"]
    assert [c["kind"] for c in cards] == ["countdown", "stopwatch", "stopwatch", "clock", "clock",
                                          "countdown", "countdown"]
    assert [c["total"] for c in cards] == [30, 120, 0, 0, 0, 60, 60]
    assert cards[3]["city"] == "New York" and cards[3]["ttime"] is None
    assert cards[4]["city"] == "東京" and cards[4]["ttime"] == "09:05"
    assert cards[0]["alarm"] == {"sound": "bell", "vol": 0.5}           # the rack's alarm
    assert cards[1]["alarm"] == cards[4]["alarm"] == cards[0]["alarm"]  # targets are ends
    assert cards[2]["alarm"] is None and cards[3]["alarm"] is None      # no end: no alarm
    assert cards[5]["alarm"] is None                                    # "off"
    assert cards[6]["alarm"] == {"sound": "gong", "vol": 1.0, "dur": 6.0}
    assert page.count('class="stx-cd-btn stx-cd-bell"') == 4 and "stx-cd-all-bell" in page


def test_idle_state_is_drawn_without_script():
    page = _export(([("Intro <b>", 1.5), ("Clock", None, {"type": "clock", "tz": "Europe/Luxembourg"})], {}))
    assert ">Intro &lt;b&gt;</div>" in page                 # labels are escaped
    assert '<div class="stx-cd-digits" style="font-size:' in page and ">01:30</div>" in page
    assert ">Luxembourg</div>" in page                       # a clock's city
    assert page.count('class="stx-cd-btn stx-cd-go"') == 1  # the countdown's ▶; none on a clock
    assert "stx-cd-all-start" in page


# -- markup contracts ---------------------------------------------------------------------

def test_runtime_injected_once_even_without_toc():
    page = _export(([("a", 1)], {}), ([("b", 2), ("c", 3)], {"mode": "parallel"}), raw=True)
    assert page.count("win.__stxCountdown = {scan: scan};") == 1
    assert len(_racks(page)) == 2
    assert "__stxCountdown" not in _plain_page()              # no rack, no runtime


def _plain_page() -> str:
    reset_export_buffer(ExportConfig(enabled=True))
    from streamtex import st_write
    st_write("no rack here")
    return generate_export_html()


def test_a_plain_rack_has_no_opt_in_output():
    page = _export(([("a", 1), ("b", 2)], {}))
    rack = _racks(page)[0]
    assert all(c["alarm"] is None for c in rack["cards"]) and "stx-cd-bell" not in page
    assert rack["autostart"] is False and rack["mode"] == "chain"
    assert "--cd-run:" not in page.split('class="stx-cd"')[1].split(">")[0]   # no colour override
    assert "stx-marker" not in page                         # one block = one marker: none added


def test_rack_id_is_stable_and_content_based():
    a = _racks(_export(([("a", 1), ("b", 2)], {})))[0]["id"]
    reset_export_buffer(ExportConfig(enabled=True))
    b = _racks(_export(([("a", 1), ("b", 2)], {})))[0]["id"]
    reset_export_buffer(ExportConfig(enabled=True))
    c = _racks(_export(([("a", 1), ("b", 3)], {})))[0]["id"]
    assert a == b != c


def test_config_labels_colours_and_switches():
    cfg = CountdownConfig(color_running="#0f0", start_all_label="▶ Los", reset_all_label="↺ Neu",
                          ends_at_label="endet um", since_label="seit", autostart=True,
                          show_global_buttons=False, card_css="background:#123;")
    page = _export(([("a", 1)], {"config": cfg}))
    rack = _racks(page)[0]
    assert rack["autostart"] is True and rack["endsAt"] == "endet um" and rack["since"] == "seit"
    assert "--cd-run:#0f0;" in page and "stx-cd-all-start" not in page and "background:#123;" in page


def test_live_runtime_mounts_the_countdown_script():
    from streamtex import marker_runtime
    assert marker_runtime._COUNTDOWN_JS_PATH.is_file()
    assert "__stxCountdown" in marker_runtime._read_asset(marker_runtime._COUNTDOWN_JS_PATH)


# -- CountdownConfig.resolve --------------------------------------------------------------

def test_resolve_layers_json_wins(tmp_path):
    path = tmp_path / "timers.json"
    path.write_text(json.dumps({"alarm": "gong", "alarm_volume": 1}))
    cfg = CountdownConfig.resolve({"alarm": "bell", "autostart": True}, str(path))
    assert (cfg.alarm, cfg.alarm_volume, cfg.autostart) == ("gong", 1, True)


def test_resolve_drops_what_does_not_fit(tmp_path, caplog):
    path = tmp_path / "timers.json"
    path.write_text(json.dumps({"autostart": 1, "nope": 2, "alarm_duration": "6"}))
    cfg = CountdownConfig.resolve({"alarm_muted": False, "alarm_volume": True}, str(path))
    assert cfg.alarm_muted is False                # kept
    assert cfg.autostart is False                  # 1 is not a bool
    assert cfg.alarm_volume == 0.6                 # True is not a number
    assert cfg.alarm_duration is None
    assert "unknown key 'nope'" in caplog.text


def test_resolve_survives_a_missing_or_broken_file(tmp_path, caplog):
    assert CountdownConfig.resolve(None, str(tmp_path / "absent.json")) == CountdownConfig()
    assert caplog.text == ""                       # a missing file is silent
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert CountdownConfig.resolve({"autostart": True}, str(bad)).autostart is True
    assert "bad.json ignored" in caplog.text
