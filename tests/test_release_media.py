"""#142 — media per site: the live face serves only the files its site shows."""
import os
import subprocess
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from streamtex.cli.release_cmd import media_report_cmd
from streamtex.release import ReleaseError, build, ops
from streamtex.release import media as md
from streamtex.release.config import load_config

STX_TOML = """
    [release]
    project = "demo"
    media = "assets"
    {extra}
    [[release.sites]]
    site = "deck"
    book = "docs/deck/book.py"
    {site_extra}
"""


def _project(tmp_path, monkeypatch, extra="", site_extra=""):
    """A project whose document's static folder is the shared media folder, as in all-trainings."""
    (tmp_path / "stx.toml").write_text(textwrap.dedent(STX_TOML.format(extra=extra, site_extra=site_extra)))
    assets = tmp_path / "assets"
    for rel, data in {"media/a.mp4": b"A" * 40, "media/b.mp4": b"B" * 30, "media/c.png": b"C" * 40,
                      "downloads/x.pdf": b"X", "downloads/deck/y.pdf": b"Y"}.items():
        (assets / rel).parent.mkdir(parents=True, exist_ok=True)
        (assets / rel).write_bytes(data)
    monkeypatch.chdir(tmp_path)
    return load_config(tmp_path)


def _snapshot(tmp_path, book='st_video("app/static/media/b.mp4")\n'):
    """The code snapshot as export leaves it: the document's static links to the media folder, the
    media folder itself not there (publish links it to the server's)."""
    code = tmp_path / "work" / "code"
    (code / "docs" / "deck").mkdir(parents=True)
    (code / "docs" / "deck" / "book.py").write_text(book)
    (code / "docs" / "deck" / "static").symlink_to("../../assets")
    return code


def _export(tmp_path, files):
    html = tmp_path / "work" / "html"
    for rel, data in files.items():
        (html / rel).parent.mkdir(parents=True, exist_ok=True)
        (html / rel).write_bytes(data)
    return html


# -- configuration ---------------------------------------------------------------------------------

def test_off_by_default(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    assert cfg.media_per_site is False and cfg.media_keep == () and cfg.site("deck").media_keep == ()


def test_keys_read(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, 'media_per_site = true\nmedia_keep = ["downloads/*"]',
                   'media_keep = ["media/b.mp4"]')
    assert cfg.media_per_site is True and cfg.media_keep == ("downloads/*",)
    assert cfg.site("deck").media_keep == ("media/b.mp4",)


@pytest.mark.parametrize("extra, site_extra, said", [
    ('media_per_site = "yes"', "", "true or false"),
    ('media_keep = "downloads/*"', "", "a list of globs"),
    ('media_keep = ["/media/*"]', "", "a list of globs"),
    ("", "media_keep = [1]", "a list of globs"),
])
def test_bad_values_refused(tmp_path, monkeypatch, extra, site_extra, said):
    with pytest.raises(ReleaseError, match=said):
        _project(tmp_path, monkeypatch, extra, site_extra)


# -- the plan --------------------------------------------------------------------------------------

def test_plan_keeps_the_export_media_and_the_patterns(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, 'media_keep = ["downloads/*.pdf"]', 'media_keep = ["nothing/*"]')
    code = _snapshot(tmp_path)
    html = _export(tmp_path, {"en/deck/data/video/a_1a2b3c.mp4": b"A" * 40,     # media/a.mp4, renamed
                              "fr/deck/data/video/a_1a2b3c.mp4": b"A" * 40,
                              "en/deck/data/image/c_9f.png": b"D" * 40,         # same size as c.png, not it
                              "en/deck/data/image/inline.svg": b"<svg/>",
                              "en/deck/deck.html": b"A" * 40})                  # not under data/
    mp = md.plan(cfg, cfg.site("deck"), code, html)
    assert mp.kept == {"media/a.mp4": "export", "downloads/x.pdf": "downloads/*.pdf",
                       "downloads/deck/y.pdf": "downloads/*.pdf"}
    assert mp.dropped == ["media/b.mp4", "media/c.png"]
    assert mp.unmatched == 2
    assert mp.named == ["media/b.mp4"]                 # named by book.py, not kept: said
    assert not (code / "assets").exists()              # the media link is taken away again


def test_plan_of_a_document_without_static(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    code = tmp_path / "work" / "code"
    (code / "docs" / "deck").mkdir(parents=True)
    assert md.plan(cfg, cfg.site("deck"), code, _export(tmp_path, {})).static is None


def test_served_links_reach_the_same_files(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    code = _snapshot(tmp_path)
    (code / "assets").symlink_to(tmp_path / "assets")        # as on the server: the media linked
    served = md.build_served(code, cfg.site("deck"), ["media/a.mp4", "downloads/deck/y.pdf"])
    assert (served / "media" / "a.mp4").read_bytes() == b"A" * 40
    assert (served / "downloads" / "deck" / "y.pdf").read_bytes() == b"Y"
    assert not os.path.isabs(os.readlink(served / "media" / "a.mp4"))
    assert sorted(p.relative_to(served).as_posix() for p in served.rglob("*") if p.is_file()) == [
        "downloads/deck/y.pdf", "media/a.mp4"]


def test_nothing_kept_serves_nothing(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    served = md.build_served(_snapshot(tmp_path), cfg.site("deck"), [])
    assert served.is_dir() and not any(served.iterdir())


# -- the router's link follows the release ---------------------------------------------------------

class LocalTarget:
    name = "prod"

    def __init__(self, root):
        self.root = root

    def path(self, *parts):
        return str(self.root.joinpath(*parts))

    def sh(self, cmd, check=True):
        return subprocess.run(["sh", "-c", cmd], text=True, capture_output=True, check=check)

    def switch_cmd(self, base, release, link="current"):
        return f"cd {base} && rm -f {link} && ln -s releases/{release} {link}"


def test_the_static_link_follows_the_release(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    site = cfg.site("deck")
    t = LocalTarget(tmp_path / "srv")
    base = tmp_path / "srv" / "live" / "sites" / "deck"
    (base / "releases" / "r1").mkdir(parents=True)                    # before media_per_site
    (base / "releases" / "r2" / md.SERVED).mkdir(parents=True)        # with it
    (tmp_path / "srv" / "static" / "sites" / "deck").mkdir(parents=True)
    ops.switch(t, site, "r2")
    assert os.readlink(base / "static") == f"/srv/live/sites/deck/current/{md.SERVED}"
    ops.switch(t, site, "r1")                                         # a rollback: the whole folder again
    assert os.readlink(base / "static") == "/srv/live/sites/deck/current/docs/deck/static"


# -- publish ---------------------------------------------------------------------------------------

class _Copied(Exception):
    pass


def _publish(tmp_path, monkeypatch, cfg, faces=("live", "html")):
    """Publish up to the copy of the code; returns the files of its .stx-served and what was said."""
    code = _snapshot(tmp_path)
    html = _export(tmp_path, {"en/deck/data/video/a.mp4": b"A" * 40})
    monkeypatch.setattr(build, "snapshot", lambda c, s, w: code)
    monkeypatch.setattr(build, "export", lambda c, s, code_, w, r, env: (html, r))
    seen = {}

    class Target:
        name = "prod"

        def path(self, *parts):
            return "/".join(parts)

        def sh(self, cmd, check=True):
            return subprocess.CompletedProcess(cmd, 0, "", "")

        def rsync(self, src, dest, *opts):
            if src == f"{code}/":
                served = code / md.SERVED
                seen["served"] = sorted(p.relative_to(served).as_posix() for p in served.rglob("*")
                                        if p.is_symlink()) if served.exists() else None
                raise _Copied

    said = []
    site = cfg.site("deck")
    object.__setattr__(site, "faces", faces)
    with pytest.raises(_Copied):
        ops.publish_site(Target(), cfg, {"sites": {}}, site, "r2", {"live": None, "html": None}, said.append)
    return seen["served"], said


def test_publish_with_media_per_site(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, 'media_per_site = true\nmedia_keep = ["downloads/x.pdf"]')
    served, said = _publish(tmp_path, monkeypatch, cfg)
    assert served == ["downloads/x.pdf", "media/a.mp4"]
    assert any("media per site: 2 of 5 file(s) served" in s for s in said)
    assert any("named in the site's files, not served: media/b.mp4" in s for s in said)


def test_publish_without_media_per_site_changes_nothing(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch)
    served, said = _publish(tmp_path, monkeypatch, cfg)
    assert served is None and not any("media per site" in s for s in said)


def test_a_live_only_site_keeps_its_whole_folder(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, "media_per_site = true")
    served, said = _publish(tmp_path, monkeypatch, cfg, faces=("live",))
    assert served is None and any("has no HTML face" in s for s in said)


# -- the report ------------------------------------------------------------------------------------

def test_media_report(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, 'media_keep = ["downloads/*"]')
    code = _snapshot(tmp_path)
    html = _export(tmp_path, {"en/deck/data/video/a.mp4": b"A" * 40})
    monkeypatch.setattr(build, "snapshot", lambda c, s, w: code)
    monkeypatch.setattr(build, "export", lambda c, s, code_, w, r, env: (html, r))
    r = CliRunner().invoke(media_report_cmd, ["deck", "--list", "dropped"])
    assert r.exit_code == 0, r.output
    assert "kept: 3 file(s)" in r.output and "1 shown by the HTML export, 2 named by media_keep" in r.output
    assert "no longer served: 2 file(s)" in r.output
    assert "media/b.mp4" in r.output and "media/c.png" in r.output
    assert "media_per_site = false: nothing changes" in r.output
    assert Path(cfg.root / "assets" / "media" / "a.mp4").exists()     # the project untouched
