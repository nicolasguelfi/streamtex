"""Paginated HTML export: one file per page of the page map (#106)."""

import json
import re
import shutil
import subprocess
import sys
import textwrap

import pytest
from click.testing import CliRunner

from streamtex.export import strip_page_sentinels
from streamtex.export_enrich import _build_sidebar_html
from streamtex.export_paginate import (
    build_entry_html,
    build_page_documents,
    page_file_names,
    split_pages,
    strip_head_break,
    to_subfolder,
)

node = pytest.mark.skipif(not shutil.which("node"), reason="node not available")

RULE = '<div class="stx-el" style="align-self:stretch"><hr class="stx-slide-break-rule" style="x"></div>'
SPACER = '<div class="stx-el" style="align-self:stretch"><div class="stx-slide-break-spacer" style="height: 2vh;"></div></div>'
SPACE = '<div class="stx-el" style="align-self:stretch"><div style="height: 2em;"></div></div>'
MARK = '<div class="stx-el" style="align-self:stretch"><div id="m{n}" class="streamtex-marker"></div></div>'


class TestNames:
    def test_unique_blocks_keep_their_name(self):
        pages = [{"block": "content.bck_intro"}, {"block": "content.bck_rag"}]
        assert page_file_names(pages, []) == ["bck_intro.html", "bck_rag.html"]

    def test_copies_take_their_section_then_what_precedes(self):
        pages = [{"block": "bck_intro"}, {"block": "bck_bravo"}, {"block": "bck_x"},
                 {"block": "bck_bravo"}, {"block": "bck_bravo"}]
        toc = [{"level": 1, "page_idx": 0, "_reg_label": "Séance 1 — Prompts"},
               {"level": 1, "page_idx": 3, "_reg_label": "RAG"}]
        assert page_file_names(pages, toc) == [
            "bck_intro.html", "seance-1-prompts--bck_bravo.html", "bck_x.html",
            "rag--bck_bravo.html", "rag--bck_bravo--bck_bravo.html"]

    def test_tree_pages_use_their_list_block(self):
        pages = [{"block": "a", "start": [0], "parent": "lists.L1"},
                 {"block": "a", "start": [1], "parent": "lists.L2"}]
        assert page_file_names(pages, []) == ["L1--a.html", "L2--a.html"]

    def test_no_positional_number_and_stable_under_reordering(self):
        pages = [{"block": "bck_a"}, {"block": "bck_b"}, {"block": "bck_c"}]
        names = page_file_names(pages, [])
        assert names == page_file_names(list(reversed(pages)), [])[::-1]
        assert not any(re.search(r"\d", n) for n in names)

    def test_always_unique(self):
        pages = [{"block": "x"}] * 6
        names = page_file_names(pages, [])
        assert len(set(names)) == 6


class TestCut:
    def _doc(self):
        page = '<div class="streamtex-page">\n'
        from streamtex.export import _LIST_INSIDE_JS
        body = ("<!--stx-page:0-->\n" + MARK.format(n=0) + "\n<p>A</p>\n" + SPACE + "\n" + RULE + "\n" + SPACER
                + "\n<!--stx-page:1-->\n" + MARK.format(n=1) + "\n<p>B</p>")
        return "<html><head></head><body>\n" + page + body + "\n</div>\n" + _LIST_INSIDE_JS + "\n</body></html>"

    def test_split(self):
        head, segs, tail = split_pages(self._doc())
        assert [n for n, _ in segs] == [0, 1] and head.endswith('<div class="streamtex-page">\n')
        assert "<p>A</p>" in segs[0][1] and "<p>B</p>" in segs[1][1]

    def test_strip_head_break(self):
        body = SPACE + "\n" + RULE + "\n" + SPACER + "\n" + MARK.format(n=3) + "\n<p>x</p>"
        assert strip_head_break(body).startswith(MARK.format(n=3))
        plain = SPACE + "\n" + MARK.format(n=3)
        assert strip_head_break(plain) == plain           # block.top without a break is kept

    def test_documents(self):
        pages = [{"block": "bck_a"}, {"block": "bck_b"}]
        files, docs = build_page_documents(self._doc(), pages, [])
        assert files == ["bck_a.html", "bck_b.html"]
        assert [d[0] for d in docs] == files and docs[1][2] == [1]
        assert "<p>A</p>" in docs[0][1] and "<p>B</p>" not in docs[0][1]

    def test_a_page_that_could_not_be_cut_stays_with_the_previous(self):
        doc = self._doc().replace("<!--stx-page:1-->\n", "")
        files, docs = build_page_documents(doc, [{"block": "bck_a"}, {"block": "bck_b"}], [])
        assert files == ["bck_a.html", "bck_a.html"] and len(docs) == 1

    def test_continuous_has_no_sentinel(self):
        assert "stx-page" not in strip_page_sentinels(self._doc())

    def test_assets_one_folder_down(self):
        html = '<img src="data/images/a.png"><div style="background:url(\'data/x.png\')">'
        assert to_subfolder(html) == '<img src="../data/images/a.png"><div style="background:url(\'../data/x.png\')">'


def test_sidebar_is_global_and_links_to_other_files():
    toc = [{"level": 1, "key_anchor": "intro", "title": "Intro", "page_idx": 0},
           {"level": 1, "key_anchor": "rag", "title": "RAG", "page_idx": 1}]
    html = _build_sidebar_html(toc, page_nav={"files": ["a.html", "b.html"], "here": [1], "prefix": ""})
    assert 'href="a.html#intro"' in html and 'href="#rag"' in html
    assert 'stx-on-page" data-stx-block="1"' in html


@node
@pytest.mark.parametrize("query,expected", [("", "pages/a.html"), ("?slide=2", "pages/b.html#m1"),
                                            ("?page=2", "pages/b.html"), ("?marker=k1", "pages/b.html#m1"),
                                            ("#intro", "pages/a.html#intro")])
def test_entry_file_sends_links_to_their_page(query, expected):
    markers = [{"anchor": "m0", "label": "A", "page_idx": 0}, {"anchor": "m1", "key": "k1", "label": "B", "page_idx": 1}]
    toc = [{"key_anchor": "intro", "page_idx": 0}]
    html = build_entry_html(["a.html", "b.html"], "pages/", markers, toc, "T")
    js = re.search(r"<script>(.*)</script>", html, re.S).group(1)
    search, _, hash_ = query.partition("#")
    prog = textwrap.dedent(f"""
        var location = {{ search: {json.dumps(search)}, hash: {json.dumps('#' + hash_ if hash_ else '')},
                          replace: function(u) {{ console.log(u); }} }};
        function URLSearchParams(q) {{ this.q = q; }}
        URLSearchParams.prototype.get = function(k) {{
          var m = new RegExp('[?&]' + k + '=([^&]*)').exec(this.q); return m ? m[1] : null; }};
    """) + js
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == expected


# ---------------------------------------------------------------------------
# stx export html --html-mode (CLI, end to end)
# ---------------------------------------------------------------------------

def _project(tmp_path):
    p = tmp_path / "deck"
    (p / "blocks").mkdir(parents=True)
    (p / "blocks" / "__init__.py").write_text("")
    for name in ("bck_intro", "bck_rag", "bck_end"):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            def build(**k):
                stx.st_marker("{name}")
                stx.st_write("text-{name}", toc_lvl="1")
                stx.st_slide_break()
                stx.st_write("more-{name}")
        """))
    (p / "book.py").write_text(textwrap.dedent("""
        import streamtex as stx
        from blocks import bck_intro, bck_rag, bck_end
        stx.st_book([bck_intro, bck_rag, bck_end], toc_config=stx.TOCConfig(),
                    marker_config=stx.MarkerConfig(), paginate=True, html_export_mode="both")
    """))
    return p


@pytest.fixture
def cli_project(tmp_path):
    p = _project(tmp_path)
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


SENTINEL = re.compile(r"<!--stx-page:\d+-->")


def _body(html):
    """The page content: from the page wrapper to the first script."""
    start = html.find('<div class="streamtex-page">')
    return html[start:html.find("<script>", start)]


def _page_nav(html):
    m = re.search(r"var PAGE_NAV = (null|\{.*?\});\n", html)
    return json.loads(m.group(1))


def _ids(html):
    body = html[html.find('<div class="streamtex-page">'):]
    return re.findall(r'<div id="([^"]+)" class="streamtex-marker"', body)


def test_cli_both(cli_project, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(cli_project), "-o", str(out)])
    assert r.exit_code == 0, r.output
    folder = out / "deck"
    cont = (folder / "deck.html").read_text()
    files = sorted(f.name for f in (folder / "pages").iterdir())
    assert files == ["bck_end.html", "bck_intro.html", "bck_rag.html"]
    assert not SENTINEL.search(cont) and _page_nav(cont)["other"] == "pages/"
    order = ["bck_intro.html", "bck_rag.html", "bck_end.html"]
    paged = sum((_ids((folder / "pages" / f).read_text()) for f in order), [])
    assert paged == _ids(cont) and len(paged) == 6
    rag = (folder / "pages" / "bck_rag.html").read_text()
    assert "text-bck_rag" in _body(rag) and "text-bck_intro" not in _body(rag)
    assert 'href="bck_intro.html#' in rag and _page_nav(rag)["other"] == "../deck.html"
    assert '<hr class="stx-slide-break-rule"' not in _body(rag).split("text-bck_rag")[0]   # no rule at its head


def test_cli_continuous_override(cli_project, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(cli_project), "-o", str(out), "--html-mode", "continuous"])
    assert r.exit_code == 0, r.output
    cont = (out / "deck" / "deck.html").read_text()
    assert not (out / "deck" / "pages").exists()
    assert not SENTINEL.search(cont) and _page_nav(cont) is None


def test_cli_paginated_entry_file(cli_project, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(cli_project), "-o", str(out), "--html-mode", "paginated"])
    assert r.exit_code == 0, r.output
    entry = (out / "deck" / "deck.html").read_text()
    assert "location.replace" in entry and '"pages/"' in entry
    rag = (out / "deck" / "pages" / "bck_rag.html").read_text()
    assert _page_nav(rag)["other"] is None              # no other mode to switch to


def test_st_book_refuses_a_wrong_mode():
    import streamtex.book as bm
    with pytest.raises(ValueError, match="html_export_mode"):
        bm._st_book_impl([], html_export_mode="pages")
    assert "html_export_mode" in bm.BOOK_DEFAULT_KEYS


# ---------------------------------------------------------------------------
# Images load as the reader nears them (#115)
# ---------------------------------------------------------------------------

_PNG = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


@pytest.fixture
def image_project(tmp_path):
    import base64
    p = _project(tmp_path)
    (p / "pic.png").write_bytes(base64.b64decode(_PNG))
    for name in ("bck_intro", "bck_rag", "bck_end"):
        (p / "blocks" / f"{name}.py").write_text(textwrap.dedent(f"""
            import streamtex as stx
            def build(**k):
                stx.st_marker("{name}")
                stx.st_write("text-{name}", toc_lvl="1")
                stx.st_image(uri=r"{p / 'pic.png'}", width="10px")
                stx.st_slide_break()
                stx.st_image(uri=r"{p / 'pic.png'}", width="10px")
        """))
    yield p
    for n in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[n]


def _imgs(html):
    return re.findall(r"<img\b[^>]*>", _body(html))


def test_cli_images_after_the_first_slide_are_lazy(image_project, tmp_path):
    from streamtex.cli.export_cmd import export_html
    out = tmp_path / "out"
    r = CliRunner().invoke(export_html, [str(image_project), "-o", str(out), "--asset-mode", "embedded"])
    assert r.exit_code == 0, r.output
    for f in ("bck_intro.html", "bck_rag.html", "bck_end.html"):     # each page: its first slide eager
        first, second = _imgs((out / "deck-pages" / f).read_text())
        assert "loading=" not in first
        assert 'loading="lazy" decoding="async"' in second
    cont = _imgs((out / "deck.html").read_text())
    assert len(cont) == 6 and "loading=" not in cont[0]
    assert all('loading="lazy"' in i for i in cont[1:])
