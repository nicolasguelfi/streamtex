"""streamtex.i18n: T / TF, current_lang order, with_lang, st_book(lang=) (#85)."""

import pytest

from streamtex import i18n


@pytest.fixture
def langs():
    i18n.set_languages(("en", "fr"), "en")
    yield
    i18n.set_languages(("en", "fr"), "en")


def test_T_fallbacks_and_strict(langs, monkeypatch):
    monkeypatch.delenv("STX_LANG", raising=False)
    leaf = {"en": "Hello", "fr": "Bonjour", "de": ""}
    assert i18n.T(leaf, "fr") == "Bonjour"
    assert i18n.T({"en": "Hello"}, "fr") == "Hello"           # missing -> default language
    assert i18n.T({"fr": "Bonjour"}, "en") == "Bonjour"       # no default -> first value
    i18n.set_languages(("en", "fr", "de"))
    assert i18n.T(leaf, "de") == ""                            # empty is a value, not a hole
    assert i18n.T("raw") == "raw"
    with pytest.raises(TypeError):
        i18n.T("raw", strict=True)
    assert i18n.TF({"en": ("a ", ("S", "b"))}, "en") == ("a ", ("S", "b"))
    assert i18n.TF({"en": "one"}, "en") == ("one",)


def test_current_lang_order(langs, monkeypatch):
    monkeypatch.delenv("STX_LANG", raising=False)
    assert i18n.current_lang() == "en"
    assert i18n.current_lang(default="fr") == "fr"
    monkeypatch.setenv("STX_LANG", "fr")
    assert i18n.current_lang() == "fr"
    monkeypatch.setenv("STX_LANG", "xx")
    with pytest.raises(ValueError):
        i18n.current_lang()


def test_with_lang_and_set_languages(langs):
    assert i18n.with_lang("http://h/x", "fr") == "http://h/x?lang=fr"
    assert i18n.with_lang("http://h/x?a=1", "fr") == "http://h/x?a=1&lang=fr"
    # an existing lang= is replaced, not repeated; the #fragment stays last
    assert i18n.with_lang("http://h/x?lang=en&a=1", "fr") == "http://h/x?a=1&lang=fr"
    assert i18n.with_lang("http://h/x#sec", "fr") == "http://h/x?lang=fr#sec"
    with pytest.raises(ValueError):
        i18n.set_languages(("en",), "fr")


def test_i18n_names_stay_out_of_the_star_import():
    ns = {}
    exec("from streamtex import *", ns)  # noqa: S102
    for name in ("T", "TF", "current_lang", "with_lang", "set_languages"):
        assert name not in ns


def test_st_book_lang_reaches_every_block(tmp_path, monkeypatch):
    """lang="auto" resolves $STX_LANG and hands it to build(); block_kwargs wins."""
    import textwrap

    from streamtex.cli.build_check import run_book

    (tmp_path / "blocks").mkdir()
    (tmp_path / "blocks" / "__init__.py").write_text("")
    out = tmp_path / "seen.txt"
    (tmp_path / "blocks" / "bck_a.py").write_text(textwrap.dedent(f"""
        def build(lang="?", x=None, **_):
            open({str(out)!r}, "a").write(f"{{lang}}:{{x}}\\n")
    """))
    (tmp_path / "book.py").write_text(textwrap.dedent("""
        from streamtex import st_book
        import blocks.bck_a as a
        st_book([a], lang="auto", block_kwargs={"x": 1})
        st_book([a], lang="auto", block_kwargs={"lang": "en"})
    """))
    monkeypatch.setenv("STX_LANG", "fr")
    r = run_book(tmp_path / "book.py", timeout=60)
    assert r.book_error is None and not r.errors, (r.book_error, r.errors)
    assert out.read_text().splitlines() == ["fr:1", "en:None"]


def test_real_st_book_resolves_lang_before_anything_else(monkeypatch, langs):
    """The real st_book: lang= becomes block_kwargs["lang"] (warmup path observes it)."""
    import types

    import streamtex.book as book

    monkeypatch.delenv("STX_LANG", raising=False)
    seen = []
    monkeypatch.setattr(book, "_warmup_mode", True)
    monkeypatch.setattr(book, "_warmup_build_cache",
                        lambda *a, block_args=(), block_kwargs=None, **k: seen.append(block_kwargs))
    blk = types.ModuleType("b")
    book.st_book([blk], lang="fr", block_kwargs={"x": 1}, export=False, loading=False)
    book.st_book([blk], lang="auto", block_kwargs={"lang": "en"}, export=False, loading=False)
    book.st_book([blk], export=False, loading=False)
    assert seen == [{"lang": "fr", "x": 1}, {"lang": "en"}, {}]
