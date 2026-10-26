"""stx release access (#147): one [admin] password added to every site, the labels that see all the
content, one record per password so that one login opens every site holding it."""
import textwrap
import tomllib

import pytest

from streamtex.deploy.stx_auth import check_password, parse_records
from streamtex.release import ReleaseError
from streamtex.release import passwords as pw
from streamtex.release.config import load_config

STX_TOML = """
    [release]
    project = "demo"
    [[release.sites]]
    site = "deck-a"
    book = "docs/a/book.py"
    group = "GAI"
    [[release.sites]]
    site = "deck-b"
    book = "docs/b/book.py"
    group = "GAI"
    [[release.sites]]
    site = "manual"
    book = "docs/m/book.py"
    faces = ["html"]
"""

PASSWORDS = """
    [admin]
    live = "ADMIN:root"
    html = "ADMIN:root"

    [GAI]
    html = "PROMO-A:pa,PROMO-B:pb:2026-12-31"
    full = ["PROMO-A"]

    [GAI.sites.deck-b]
    full = []

    [manual]
    [manual.sites.manual]
    open = true
"""


@pytest.fixture
def cfg(tmp_path):
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML))
    return load_config(tmp_path)


def _data(text=PASSWORDS):
    return tomllib.loads(textwrap.dedent(text))


def _labels(entries):
    return [e.label for e in entries]


def test_admin_is_added_to_every_face(cfg):
    a = pw.for_site(_data(), cfg.site("deck-a"))
    assert _labels(a["html"]) == ["PROMO-A", "PROMO-B", "ADMIN"]
    assert _labels(a["live"]) == ["ADMIN"]               # no participant on the live face: the admin's alone


def test_an_open_face_stays_open(cfg):
    assert pw.for_site(_data(), cfg.site("manual")) == {"html": None}


def test_the_full_labels(cfg):
    assert pw.full_labels(_data(), cfg.site("deck-a")) == {"PROMO-A", "ADMIN"}
    assert pw.full_labels(_data(), cfg.site("deck-b")) == {"ADMIN"}        # the site level replaces the group's


def test_no_rule_on_what_a_password_contains(cfg):
    data = _data('[admin]\nhtml = "ADMIN:a"\nlive = "ADMIN:a"\n[GAI]\nhtml = "P:1"\n')
    assert [e.password for e in pw.for_site(data, cfg.site("deck-a"))["html"]] == ["1", "a"]


@pytest.mark.parametrize("text,match", [
    ('[admin]\nhtml = "ADMIN:root"\nlive = "ADMIN:root"\n[GAI]\nhtml = "P:root"\n', "share a password"),
    ('[admin]\nhtml = "ADMIN:root"\nlive = "ADMIN:root"\n[GAI]\nhtml = "ADMIN:other"\n', "appears twice"),
    ('[admin]\nhtml = "ADMIN:root"\nopen = true\n', r"\[admin\]: live and/or html"),
    ('[admin]\nhtml = "ADMIN:ro ot"\nlive = "ADMIN:root"\n', "whitespace"),
    ('[GAI]\nhtml = "P:p"\nlive = "P:q"\nfull = "P"\n', "a list of password labels"),
])
def test_what_the_login_screen_could_never_match_is_refused(cfg, text, match):
    with pytest.raises(ReleaseError, match=match):
        pw.for_site(_data(text), cfg.site("deck-a")), pw.full_labels(_data(text), cfg.site("deck-a"))


def test_without_admin_nothing_changes(cfg):
    data = _data('[GAI]\nhtml = "P:p"\n')
    with pytest.raises(ReleaseError, match="an omission never opens"):
        pw.for_site(data, cfg.site("deck-a"))                           # the live face has no password


def test_one_record_per_password_across_sites(cfg):
    pool = pw.RecordPool()
    a = pool.text(pw.for_site(_data(), cfg.site("deck-a"))["html"])
    b = pool.text(pw.for_site(_data(), cfg.site("deck-b"))["html"])
    live = pool.text(pw.for_site(_data(), cfg.site("deck-a"))["live"])
    admin = {parse_records(x).entry("ADMIN").record for x in (a, b, live)}
    assert len(admin) == 1 and check_password(admin.pop(), "root")


def test_a_record_already_on_the_server_is_kept(cfg):
    first = pw.RecordPool().text(pw.for_site(_data(), cfg.site("deck-a"))["html"])
    again = pw.RecordPool(first).text(pw.for_site(_data(), cfg.site("deck-a"))["html"])
    assert again == first                                             # no session closed by writing again
    changed = _data(PASSWORDS.replace("PROMO-B:pb", "PROMO-B:new"))
    after = parse_records(pw.RecordPool(first).text(pw.for_site(changed, cfg.site("deck-a"))["html"]))
    before = parse_records(first)
    assert after.entry("PROMO-A") == before.entry("PROMO-A")
    assert after.entry("PROMO-B") != before.entry("PROMO-B")         # only this label's sessions end


def test_the_levels_of_admin_and_full(cfg):
    levels = pw.levels_for(_data(), cfg.site("deck-a"))
    assert levels == {"PROMO-A": "all", "PROMO-B": pw.DEFAULT, "ADMIN": "all"}
