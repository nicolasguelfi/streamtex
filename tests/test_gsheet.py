"""Tests for streamtex.gsheet — Google Sheets data import."""

from unittest.mock import MagicMock, patch

import pytest

from streamtex.gsheet import (
    AuthMode,
    GSheetConfig,
    GSheetError,
    GSheetSource,
    _load_public_csv,
    _parse_csv_text,
    _rows_to_dicts,
    get_gsheet_config,
    load_gsheet,
    set_gsheet_config,
)

# ===================================================================
# GSheetSource
# ===================================================================

class TestGSheetSource:
    def test_from_url_extracts_id(self):
        src = GSheetSource.from_url(
            "https://docs.google.com/spreadsheets/d/1BxiMkT123/edit#gid=0"
        )
        assert src.sheet_id == "1BxiMkT123"

    def test_from_url_with_tab_and_range(self):
        src = GSheetSource.from_url(
            "https://docs.google.com/spreadsheets/d/ABC_def-123/edit",
            tab="Notes", range="A1:E30"
        )
        assert src.sheet_id == "ABC_def-123"
        assert src.tab == "Notes"
        assert src.range == "A1:E30"

    def test_from_url_invalid_raises(self):
        with pytest.raises(ValueError, match="Cannot extract sheet_id"):
            GSheetSource.from_url("https://example.com/not-a-sheet")

    def test_defaults(self):
        src = GSheetSource(sheet_id="123")
        assert src.tab == ""
        assert src.range is None
        assert src.headers is True

    def test_headers_false(self):
        src = GSheetSource(sheet_id="123", headers=False)
        assert src.headers is False

    def test_from_url_with_headers(self):
        src = GSheetSource.from_url("https://docs.google.com/spreadsheets/d/X/edit",
                                    headers=False)
        assert src.headers is False


# ===================================================================
# GSheetConfig
# ===================================================================

class TestGSheetConfig:
    def test_defaults(self):
        cfg = GSheetConfig()
        assert cfg.auth_mode == AuthMode.SERVICE_ACCOUNT
        assert cfg.credentials_path is None
        assert cfg.cache_ttl == 300
        assert cfg.default_tab == "Sheet1"

    def test_public_mode(self):
        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC)
        assert cfg.auth_mode == "public"

    def test_resolve_credentials_explicit(self):
        cfg = GSheetConfig(credentials_path="/tmp/creds.json")
        assert cfg.resolve_credentials_path() == "/tmp/creds.json"

    def test_resolve_credentials_env_var(self):
        cfg = GSheetConfig()
        with patch.dict("os.environ", {"GSHEET_CREDENTIALS": "/tmp/env_creds.json"}):
            with patch("os.path.isfile", return_value=True):
                assert cfg.resolve_credentials_path() == "/tmp/env_creds.json"

    def test_resolve_credentials_gcloud_env(self):
        cfg = GSheetConfig()
        with patch.dict("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "/tmp/gcloud.json"},
                        clear=False):
            with patch("os.path.isfile", return_value=True):
                result = cfg.resolve_credentials_path()
                assert result is not None

    def test_resolve_credentials_none(self):
        cfg = GSheetConfig()
        with patch.dict("os.environ", {}, clear=True):
            assert cfg.resolve_credentials_path() is None

    def test_set_and_get_config(self):
        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC, cache_ttl=600)
        set_gsheet_config(cfg)
        assert get_gsheet_config() is cfg
        set_gsheet_config(None)


# ===================================================================
# CSV parsing
# ===================================================================

class TestParseCsvText:
    def test_with_headers(self):
        text = "Name,Grade\nAlice,15\nBob,18\n"
        result = _parse_csv_text(text, headers=True)
        assert len(result) == 2
        assert result[0] == {"Name": "Alice", "Grade": "15"}
        assert result[1] == {"Name": "Bob", "Grade": "18"}

    def test_without_headers(self):
        text = "Alice,15\nBob,18\n"
        result = _parse_csv_text(text, headers=False)
        assert result[0] == {"col_0": "Alice", "col_1": "15"}

    def test_empty(self):
        assert _parse_csv_text("", headers=True) == []

    def test_headers_only(self):
        text = "Name,Grade\n"
        result = _parse_csv_text(text, headers=True)
        assert result == []

    def test_ragged_rows_padded(self):
        text = "A,B,C\n1,2\n"
        result = _parse_csv_text(text, headers=True)
        assert result[0] == {"A": "1", "B": "2", "C": ""}

    def test_extra_columns(self):
        text = "A\n1,2\n"
        result = _parse_csv_text(text, headers=True)
        assert result[0]["A"] == "1"
        assert result[0]["col_1"] == "2"


class TestRowsToDicts:
    def test_empty_rows(self):
        assert _rows_to_dicts([], True) == []
        assert _rows_to_dicts([], False) == []

    def test_headers(self):
        rows = [["X", "Y"], ["1", "2"]]
        result = _rows_to_dicts(rows, True)
        assert result == [{"X": "1", "Y": "2"}]

    def test_no_headers(self):
        rows = [["a", "b"]]
        result = _rows_to_dicts(rows, False)
        assert result == [{"col_0": "a", "col_1": "b"}]


# ===================================================================
# load_gsheet
# ===================================================================

class TestLoadGSheet:
    def test_unknown_mode_raises(self):
        cfg = GSheetConfig(auth_mode="magic")
        src = GSheetSource(sheet_id="123")
        with pytest.raises(ValueError, match="Unknown auth_mode"):
            load_gsheet(src, config=cfg)

    def test_service_account_without_credentials_raises(self):
        cfg = GSheetConfig(auth_mode=AuthMode.SERVICE_ACCOUNT)
        src = GSheetSource(sheet_id="123")
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="credentials not found"):
                load_gsheet(src, config=cfg)

    def test_oauth2_without_credentials_raises(self):
        cfg = GSheetConfig(auth_mode=AuthMode.OAUTH2)
        src = GSheetSource(sheet_id="123")
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="credentials not found"):
                load_gsheet(src, config=cfg)

    @patch("requests.get")
    def test_public_mode_calls_csv(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "Name,Score\nAlice,90\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC)
        src = GSheetSource(sheet_id="ABC")
        result = load_gsheet(src, config=cfg)

        assert len(result) == 1
        assert result[0]["Name"] == "Alice"
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_public_with_tab_and_range(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "A\n1\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC)
        src = GSheetSource(sheet_id="ID", tab="Sheet2", range="A1:A5")
        load_gsheet(src, config=cfg)

        url = mock_get.call_args[0][0]
        assert "sheet=Sheet2" in url
        assert "range=A1%3AA5" in url


# ===================================================================
# load_public_csv error handling
# ===================================================================

class TestLoadPublicCSV:
    @patch("requests.get")
    def test_network_error_raises_gsheet_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("timeout")

        with pytest.raises(GSheetError, match="Failed to fetch"):
            _load_public_csv("123", "Sheet1", None, True)

    @patch("requests.get")
    def test_http_error_raises_gsheet_error(self, mock_get):
        import requests
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_resp

        with pytest.raises(GSheetError, match="Failed to fetch"):
            _load_public_csv("123", "Sheet1", None, True)


# ===================================================================
# load_gsheet_df
# ===================================================================

class TestLoadGSheetDf:
    @patch("requests.get")
    def test_returns_dataframe_if_pandas(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "X,Y\n1,2\n3,4\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from streamtex.gsheet import load_gsheet_df
        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC)
        src = GSheetSource(sheet_id="ID")

        result = load_gsheet_df(src, config=cfg)

        # Should be a DataFrame if pandas is installed
        try:
            import pandas as pd
            assert isinstance(result, pd.DataFrame)
            assert list(result.columns) == ["X", "Y"]
        except ImportError:
            assert isinstance(result, list)
