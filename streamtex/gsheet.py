"""Google Sheets data import for StreamTeX.

Provides two authentication backends:
1. Service Account JSON (recommended for server-side apps)
2. OAuth2 Client (fallback, requires interactive browser auth)

Environment variable support for deployed versions:
- GSHEET_CREDENTIALS: path to service account JSON
- GOOGLE_APPLICATION_CREDENTIALS: standard GCP env var (also supported)

Usage:
    from streamtex.gsheet import GSheetSource, load_gsheet, load_gsheet_df

    src = GSheetSource.from_url("https://docs.google.com/spreadsheets/d/ID/edit")
    data = load_gsheet(src)           # List[Dict]
    df   = load_gsheet_df(src)        # pandas DataFrame
"""

import csv
import io
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GSheetError(Exception):
    """Raised when Google Sheets data cannot be loaded."""
    pass


# ---------------------------------------------------------------------------
# Configuration (DI pattern — matches BlockHelperConfig / ExportConfig)
# ---------------------------------------------------------------------------

class AuthMode:
    """Authentication mode constants."""
    PUBLIC = "public"
    SERVICE_ACCOUNT = "service_account"
    OAUTH2 = "oauth2"


@dataclass
class GSheetConfig:
    """Configuration for Google Sheets data import.

    Attributes:
        auth_mode: "public" | "service_account" | "oauth2"
        credentials_path: Path to credentials JSON. If None, resolved from env vars.
        cache_ttl: Cache duration in seconds (0 = no cache, None = forever)
        default_tab: Default tab name when not specified per-source
    """
    auth_mode: str = AuthMode.SERVICE_ACCOUNT
    credentials_path: Optional[str] = None
    cache_ttl: Optional[int] = 300
    default_tab: str = "Sheet1"

    def resolve_credentials_path(self) -> Optional[str]:
        """Resolve credentials path: explicit > GSHEET_CREDENTIALS > GOOGLE_APPLICATION_CREDENTIALS."""
        if self.credentials_path:
            return self.credentials_path
        for env_var in ("GSHEET_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS"):
            path = os.environ.get(env_var)
            if path and os.path.isfile(path):
                return path
        return None


# Global singleton
_gsheet_config: Optional[GSheetConfig] = None


def set_gsheet_config(config: GSheetConfig) -> None:
    """Set global Google Sheets configuration. Call once at project startup."""
    global _gsheet_config
    _gsheet_config = config


def get_gsheet_config() -> Optional[GSheetConfig]:
    """Get current Google Sheets configuration."""
    return _gsheet_config


# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------

@dataclass
class GSheetSource:
    """Represents a single Google Sheets data source.

    Attributes:
        sheet_id: The Google Sheets document ID (from the URL)
        tab: Tab (worksheet) name. Empty string = use config default_tab.
        range: Cell range in A1 notation (e.g. "A1:D20"). None = entire tab.
        headers: If True, first row is treated as column headers.
    """
    sheet_id: str
    tab: str = ""
    range: Optional[str] = None
    headers: bool = True

    @staticmethod
    def from_url(url: str, tab: str = "", range: Optional[str] = None,
                 headers: bool = True) -> "GSheetSource":
        """Create a GSheetSource from a full Google Sheets URL.

        Example:
            src = GSheetSource.from_url(
                "https://docs.google.com/spreadsheets/d/1BxiM.../edit",
                tab="Notes", range="A1:E30"
            )
        """
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError(f"Cannot extract sheet_id from URL: {url}")
        return GSheetSource(sheet_id=match.group(1), tab=tab, range=range, headers=headers)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_gsheet(source: GSheetSource, *,
                config: Optional[GSheetConfig] = None) -> List[Dict[str, Any]]:
    """Load data from a Google Sheet. Returns a list of row dictionaries.

    Style resolution: explicit config > global config > default (public).

    Args:
        source: GSheetSource defining which sheet/tab/range to load
        config: Optional config override. If None, uses global config.

    Returns:
        List of dicts. Keys = column headers (if headers=True) or "col_0", etc.

    Raises:
        GSheetError: On network/auth/parsing failures
        ValueError: If credentials required but not found
    """
    cfg = config or _gsheet_config or GSheetConfig(auth_mode=AuthMode.PUBLIC)
    resolved_tab = source.tab or cfg.default_tab

    if cfg.auth_mode == AuthMode.PUBLIC:
        return _load_public_csv(source.sheet_id, resolved_tab, source.range, source.headers)
    elif cfg.auth_mode == AuthMode.SERVICE_ACCOUNT:
        creds_path = cfg.resolve_credentials_path()
        if not creds_path:
            raise ValueError(
                "Service account credentials not found. Set one of:\n"
                "  - GSheetConfig(credentials_path='path/to/creds.json')\n"
                "  - GSHEET_CREDENTIALS environment variable\n"
                "  - GOOGLE_APPLICATION_CREDENTIALS environment variable"
            )
        return _load_service_account(source.sheet_id, resolved_tab, source.range,
                                     source.headers, creds_path)
    elif cfg.auth_mode == AuthMode.OAUTH2:
        creds_path = cfg.resolve_credentials_path()
        if not creds_path:
            raise ValueError(
                "OAuth2 client credentials not found. Set credentials_path to your "
                "client_secret.json file."
            )
        return _load_oauth2(source.sheet_id, resolved_tab, source.range,
                            source.headers, creds_path)
    else:
        raise ValueError(
            f"Unknown auth_mode: {cfg.auth_mode!r}. "
            f"Use '{AuthMode.PUBLIC}', '{AuthMode.SERVICE_ACCOUNT}', or '{AuthMode.OAUTH2}'."
        )


def load_gsheet_df(source: GSheetSource, *,
                   config: Optional[GSheetConfig] = None):
    """Load a Google Sheet as a pandas DataFrame.

    Falls back to list of dicts if pandas is not installed.
    """
    data = load_gsheet(source, config=config)
    try:
        import pandas as pd
        return pd.DataFrame(data)
    except ImportError:
        logger.warning("pandas not installed — returning list of dicts")
        return data


# ---------------------------------------------------------------------------
# Backend: Public CSV (no auth)
# ---------------------------------------------------------------------------

def _load_public_csv(sheet_id: str, tab: str, cell_range: Optional[str],
                     headers: bool) -> List[Dict[str, Any]]:
    """Load via public CSV export endpoint (no authentication)."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    if tab:
        url += f"&sheet={quote(tab)}"
    if cell_range:
        url += f"&range={quote(cell_range)}"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise GSheetError(
            f"Failed to fetch public sheet {sheet_id}: {e}\n"
            f"Verify the sheet is shared as 'Anyone with the link'."
        ) from e

    return _parse_csv_text(resp.text, headers)


# ---------------------------------------------------------------------------
# Backend: Service Account (Google Sheets API v4)
# ---------------------------------------------------------------------------

def _load_service_account(sheet_id: str, tab: str, cell_range: Optional[str],
                          headers: bool, credentials_path: str) -> List[Dict[str, Any]]:
    """Load via Google Sheets API v4 with a service account."""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise GSheetError(
            "Google Sheets API v4 requires:\n"
            "  uv add google-api-python-client google-auth\n"
            "Install these to use auth_mode='service_account'."
        )

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    range_notation = f"'{tab}'"
    if cell_range:
        range_notation += f"!{cell_range}"

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_notation
        ).execute()
    except Exception as e:
        raise GSheetError(f"Google Sheets API error for {sheet_id}: {e}") from e

    rows = result.get("values", [])
    return _rows_to_dicts(rows, headers)


# ---------------------------------------------------------------------------
# Backend: OAuth2 (interactive)
# ---------------------------------------------------------------------------

def _load_oauth2(sheet_id: str, tab: str, cell_range: Optional[str],
                 headers: bool, client_secret_path: str) -> List[Dict[str, Any]]:
    """Load via Google Sheets API v4 with OAuth2 (interactive browser auth)."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise GSheetError(
            "OAuth2 requires:\n"
            "  uv add google-api-python-client google-auth-oauthlib\n"
            "Install these to use auth_mode='oauth2'."
        )

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    token_path = os.path.splitext(client_secret_path)[0] + "_token.json"

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    range_notation = f"'{tab}'"
    if cell_range:
        range_notation += f"!{cell_range}"

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_notation
        ).execute()
    except Exception as e:
        raise GSheetError(f"Google Sheets API error for {sheet_id}: {e}") from e

    rows = result.get("values", [])
    return _rows_to_dicts(rows, headers)


# ---------------------------------------------------------------------------
# Shared parsing helpers
# ---------------------------------------------------------------------------

def _parse_csv_text(text: str, headers: bool) -> List[Dict[str, Any]]:
    """Parse CSV text into a list of dicts."""
    rows = [*csv.reader(io.StringIO(text))]
    return _rows_to_dicts(rows, headers)


def _rows_to_dicts(rows: List[List[str]], headers: bool) -> List[Dict[str, Any]]:
    """Convert a list of row lists into a list of dicts."""
    if not rows:
        return []

    if headers:
        col_names = rows[0]
        result = []
        for row in rows[1:]:
            d = {}
            for i, cell in enumerate(row):
                key = col_names[i] if i < len(col_names) else f"col_{i}"
                d[key] = cell
            # Pad missing columns with empty string
            for i in range(len(row), len(col_names)):
                d[col_names[i]] = ""
            result.append(d)
        return result
    else:
        return [{f"col_{i}": cell for i, cell in enumerate(row)} for row in rows]
