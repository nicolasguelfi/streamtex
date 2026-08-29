"""Tests for streamtex.cli.export_cmd — option resolution (no full export)."""

from streamtex.cli.export_cmd import LANG_ENV_VAR, resolve_export_lang


class TestResolveExportLang:
    def test_default_is_en(self, monkeypatch):
        monkeypatch.delenv(LANG_ENV_VAR, raising=False)
        assert resolve_export_lang(None) == "en"

    def test_env_var(self, monkeypatch):
        monkeypatch.setenv(LANG_ENV_VAR, "fr")
        assert resolve_export_lang(None) == "fr"

    def test_option_wins_over_env(self, monkeypatch):
        monkeypatch.setenv(LANG_ENV_VAR, "fr")
        assert resolve_export_lang("de") == "de"

    def test_blank_env_is_ignored(self, monkeypatch):
        monkeypatch.setenv(LANG_ENV_VAR, "  ")
        assert resolve_export_lang(None) == "en"

    def test_env_var_name_is_stx_lang(self):
        assert LANG_ENV_VAR == "STX_LANG"


class TestExportHtmlOptions:
    def test_lang_and_suffix_options_exist(self):
        from streamtex.cli.export_cmd import export_html
        names = {p.name for p in export_html.params}
        assert {"lang", "suffix"} <= names
