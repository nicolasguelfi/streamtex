# Proposition : Import de donnees Google Sheets dans StreamTeX

**Date** : 2026-02-20
**Statut** : Proposition (non implemente)
**Priorite** : Moyenne
**Module cible** : `streamtex/gsheet.py` (nouveau)

---

## 1. Contexte et motivation

StreamTeX est une librairie de rendu de contenu style. Les donnees affichees dans les
blocs (tableaux, graphiques, metriques) sont actuellement generees en Python ou chargees
depuis des fichiers statiques (`static/various/*.json`, `static/texts/*.txt`).

Dans les contextes pedagogiques et professionnels, les donnees sources vivent souvent
dans Google Sheets : notes d'etudiants, resultats d'enquetes, planning, KPIs. Copier
manuellement ces donnees dans des fichiers JSON ou CSV cree une desynchronisation.

### Objectif

Permettre aux blocs StreamTeX de consommer des donnees Google Sheets directement,
avec deux modes :
- **Statique** : donnees chargees une fois au demarrage (cached), exportables en HTML
- **Dynamique** : donnees rafraichies periodiquement (live), non exportables

### Contraintes StreamTeX

| Contrainte | Impact |
|-----------|--------|
| Zero HTML brut dans le code utilisateur | L'import doit retourner des structures Python (DataFrame, dict), pas du HTML |
| `stx.*` pour le contenu, `st.*` pour l'interactivite | Les donnees alimentent `stx.st_dataframe()`, `stx.st_table()`, `stx.st_line_chart()` |
| Dual rendering (Streamlit + export) | Les donnees statiques doivent fonctionner avec le pipeline d'export |
| DI pattern (BlockHelperConfig) | La configuration des credentials doit suivre le pattern DI |
| Lazy-loading | Les feuilles ne doivent etre chargees que si le bloc qui les utilise est rendu |

---

## 2. Analyse des approches possibles

### 2.1. Approche A : URL CSV publique (sans authentification)

Google Sheets expose un endpoint CSV pour les feuilles publiques :
```
https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={TAB_NAME}
```

**Avantages** :
- Zero configuration d'authentification
- Un seul `requests.get()` + `csv.reader()` (ou `pandas.read_csv()`)
- Fonctionne immediatement pour les feuilles "Tous les utilisateurs avec le lien"

**Inconvenients** :
- Ne fonctionne PAS pour les feuilles privees
- Google peut rate-limiter les requetes
- Pas de granularite (plage A1:C10, onglet specifique)

### 2.2. Approche B : Google Sheets API v4 (service account)

Utilise `google-api-python-client` + un fichier `credentials.json` (service account).

**Avantages** :
- Acces aux feuilles privees (partagees avec le service account)
- Granularite totale (plage, onglet, formatage)
- API officielle, stable

**Inconvenients** :
- Dependance lourde (`google-api-python-client`, `google-auth`)
- Configuration complexe (GCP console, JSON secret)
- Le fichier `credentials.json` ne doit JAMAIS etre commite

### 2.3. Approche C : Hybride (recommandee)

Deux backends interchangeables, meme API utilisateur :

```
GSheetConfig
  ├── mode="public"  → Backend CSV (zero config)
  └── mode="private" → Backend API v4 (credentials requises)
```

L'utilisateur choisit au niveau du projet, pas du bloc.

---

## 3. Architecture proposee

### 3.1. Nouveau module : `streamtex/gsheet.py`

```
streamtex/
  gsheet.py          ← NOUVEAU : import Google Sheets
  __init__.py         ← ajouter exports gsheet
```

### 3.2. API publique

#### Configuration (DI pattern, comme BlockHelperConfig)

```python
# streamtex/gsheet.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import csv
import io
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GSheetConfig:
    """Configuration for Google Sheets data import.

    Follows the DI pattern established by BlockHelperConfig and ExportConfig.

    Attributes:
        mode: "public" (CSV endpoint, no auth) or "private" (API v4, requires credentials)
        credentials_path: Path to service account JSON (mode="private" only)
        cache_ttl: Cache duration in seconds (0 = no cache, None = cache forever)
        default_sheet_tab: Default tab name when not specified per-source
    """
    mode: str = "public"
    credentials_path: Optional[str] = None
    cache_ttl: Optional[int] = 300  # 5 minutes par defaut
    default_sheet_tab: str = "Sheet1"


# Global singleton (pattern identique a ExportConfig, TOCConfig)
_gsheet_config: Optional[GSheetConfig] = None


def set_gsheet_config(config: GSheetConfig) -> None:
    """Set global Google Sheets configuration. Call once at project startup."""
    global _gsheet_config
    _gsheet_config = config


def get_gsheet_config() -> Optional[GSheetConfig]:
    """Get current Google Sheets configuration."""
    return _gsheet_config
```

#### Source de donnees

```python
@dataclass
class GSheetSource:
    """Represents a single Google Sheets data source.

    Attributes:
        sheet_id: The Google Sheets document ID (from the URL)
        tab: Tab (worksheet) name within the spreadsheet
        range: Cell range in A1 notation (e.g. "A1:D20"). None = entire tab.
        headers: If True, first row is treated as column headers
    """
    sheet_id: str
    tab: str = ""        # "" = use config.default_sheet_tab
    range: Optional[str] = None
    headers: bool = True

    @staticmethod
    def from_url(url: str, tab: str = "", range: Optional[str] = None) -> "GSheetSource":
        """Create a GSheetSource from a full Google Sheets URL.

        Example:
            src = GSheetSource.from_url(
                "https://docs.google.com/spreadsheets/d/1BxiM.../edit",
                tab="Notes",
                range="A1:E30"
            )
        """
        import re
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError(f"Cannot extract sheet_id from URL: {url}")
        return GSheetSource(sheet_id=match.group(1), tab=tab, range=range)
```

#### Fonctions de chargement

```python
def load_gsheet(source: GSheetSource, *, config: Optional[GSheetConfig] = None) -> List[Dict[str, Any]]:
    """Load data from a Google Sheet. Returns a list of row dictionaries.

    This is the PRIMARY function for block authors. It loads data once and
    caches it according to config.cache_ttl.

    The return type is a list of dicts (JSON-like), compatible with:
    - stx.st_dataframe(pd.DataFrame(data))
    - stx.st_table(pd.DataFrame(data))
    - stx.st_line_chart(pd.DataFrame(data))
    - Direct iteration in block build() functions

    Args:
        source: GSheetSource defining which sheet/tab/range to load
        config: Optional config override. If None, uses global config.

    Returns:
        List of dicts, one per row. Keys are column headers (if headers=True)
        or "col_0", "col_1", etc. (if headers=False).

    Raises:
        GSheetError: On network/auth/parsing failures
        ValueError: If no config is set and mode="private"

    Example:
        from streamtex import load_gsheet, GSheetSource

        grades = GSheetSource(sheet_id="1BxiM...", tab="S1-2026", range="A1:E30")
        data = load_gsheet(grades)

        # Use in block
        stx.st_dataframe(pd.DataFrame(data))
    """
    cfg = config or _gsheet_config or GSheetConfig()
    resolved_tab = source.tab or cfg.default_sheet_tab

    if cfg.mode == "public":
        return _load_public_csv(source.sheet_id, resolved_tab, source.range, source.headers)
    elif cfg.mode == "private":
        if not cfg.credentials_path:
            raise ValueError("GSheetConfig.credentials_path required for mode='private'")
        return _load_private_api(source.sheet_id, resolved_tab, source.range,
                                  source.headers, cfg.credentials_path)
    else:
        raise ValueError(f"Unknown GSheetConfig mode: {cfg.mode!r}. Use 'public' or 'private'.")


def load_gsheet_df(source: GSheetSource, *, config: Optional[GSheetConfig] = None):
    """Convenience: load_gsheet() but returns a pandas DataFrame directly.

    Requires pandas to be installed. Falls back to load_gsheet() if pandas
    is not available.

    Example:
        df = load_gsheet_df(grades_source)
        stx.st_line_chart(df, x="Student", y="Grade")
    """
    data = load_gsheet(source, config=config)
    try:
        import pandas as pd
        return pd.DataFrame(data)
    except ImportError:
        logger.warning("pandas not installed — returning list of dicts instead of DataFrame")
        return data
```

#### Backends

```python
class GSheetError(Exception):
    """Raised when Google Sheets data cannot be loaded."""
    pass


def _load_public_csv(sheet_id: str, tab: str, cell_range: Optional[str],
                     headers: bool) -> List[Dict[str, Any]]:
    """Backend A: Load via public CSV export endpoint."""
    import requests
    from urllib.parse import quote

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    if tab:
        url += f"&sheet={quote(tab)}"
    if cell_range:
        url += f"&range={quote(cell_range)}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise GSheetError(
            f"Failed to fetch public sheet {sheet_id}: {e}\n"
            f"Verify the sheet is shared as 'Anyone with the link'."
        ) from e

    reader = csv.reader(io.StringIO(resp.text))
    rows = [*reader]

    if not rows:
        return []

    if headers:
        col_names = rows[0]
        return [{col_names[i]: cell for i, cell in enumerate(row)}
                for row in rows[1:]]
    else:
        return [{f"col_{i}": cell for i, cell in enumerate(row)} for row in rows]


def _load_private_api(sheet_id: str, tab: str, cell_range: Optional[str],
                      headers: bool, credentials_path: str) -> List[Dict[str, Any]]:
    """Backend B: Load via Google Sheets API v4 with service account."""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise GSheetError(
            "Google Sheets API v4 requires:\n"
            "  uv add google-api-python-client google-auth\n"
            "Install these dependencies to use mode='private'."
        )

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    range_notation = f"'{tab}'"
    if cell_range:
        range_notation += f"!{cell_range}"

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_notation,
        ).execute()
    except Exception as e:
        raise GSheetError(f"Google Sheets API error for {sheet_id}: {e}") from e

    rows = result.get("values", [])

    if not rows:
        return []

    if headers:
        col_names = rows[0]
        return [{col_names[i] if i < len(col_names) else f"col_{i}": cell
                 for i, cell in enumerate(row)} for row in rows[1:]]
    else:
        return [{f"col_{i}": cell for i, cell in enumerate(row)} for row in rows]
```

#### Cache Streamlit

```python
def _get_cached_loader():
    """Returns a Streamlit-cached version of load_gsheet.

    Uses @st.cache_data with TTL from GSheetConfig.
    This function is called internally; users call load_gsheet() directly.
    """
    import streamlit as st

    cfg = _gsheet_config or GSheetConfig()
    ttl = cfg.cache_ttl if cfg.cache_ttl and cfg.cache_ttl > 0 else None

    @st.cache_data(ttl=ttl, show_spinner="Loading Google Sheet...")
    def _cached_load(sheet_id: str, tab: str, cell_range: str,
                     headers: bool, mode: str, creds_path: str):
        source = GSheetSource(sheet_id=sheet_id, tab=tab,
                              range=cell_range if cell_range else None,
                              headers=headers)
        cfg_override = GSheetConfig(mode=mode, credentials_path=creds_path or None)
        return load_gsheet(source, config=cfg_override)

    return _cached_load
```

### 3.3. Integration dans `__init__.py`

```python
# streamtex/__init__.py — ajouts

# Google Sheets import
from .gsheet import (
    GSheetConfig, GSheetSource, GSheetError,
    set_gsheet_config, get_gsheet_config,
    load_gsheet, load_gsheet_df,
)
```

### 3.4. Integration dans le block helper (DI)

Extension optionnelle de `BlockHelperConfig` pour les projets data-driven :

```python
# streamtex/block_helpers.py — extension

class BlockHelperConfig:
    # ... methodes existantes ...

    def get_gsheet_config(self) -> Optional["GSheetConfig"]:
        """Default GSheet config for data-loading helpers. Override in subclass."""
        return None
```

Le projet peut alors injecter la config une seule fois :

```python
# blocks/helpers.py (dans le projet utilisateur)

from streamtex import BlockHelperConfig, set_block_helper_config, GSheetConfig

class ProjectBlockHelperConfig(BlockHelperConfig):
    def get_code_style(self):
        return s.project.containers.code_box

    def get_gsheet_config(self):
        return GSheetConfig(
            mode="public",
            cache_ttl=600,  # 10 minutes
        )

set_block_helper_config(ProjectBlockHelperConfig())
```

---

## 4. Utilisation dans les blocs

### 4.1. Mode statique (recommande — compatible export)

```python
# blocks/_atomic/bck_grades_table.py

import streamlit as st
import streamtex as stx
from streamtex import *
from streamtex.gsheet import GSheetSource, load_gsheet_df
from custom.styles import Styles as s

class BlockStyles:
    pass

# Source definie au niveau du module (chargee une fois, cached)
_grades = GSheetSource.from_url(
    "https://docs.google.com/spreadsheets/d/1BxiMkT.../edit",
    tab="S1-2026",
    range="A1:E30"
)

def build():
    st_write(s.project.titles.section_title, "Notes S1-2026", toc_lvl="1")
    st_space("v", 2)

    df = load_gsheet_df(_grades)

    # Rendu via wrappers export-aware
    stx.st_dataframe(df)

    st_space("v", 2)
    st_write(s.big, "Moyenne generale : ", (s.bold, f"{df['Note'].mean():.1f}/20"))
```

### 4.2. Mode dynamique (avec rafraichissement)

```python
# blocks/_atomic/bck_live_survey.py

import streamlit as st
import streamtex as stx
from streamtex import *
from streamtex.gsheet import GSheetSource, load_gsheet_df
from custom.styles import Styles as s

class BlockStyles:
    pass

_survey = GSheetSource(sheet_id="1BxiMkT...", tab="Responses")

def build():
    st_write(s.project.titles.section_title, "Resultats du sondage (live)")
    st_space("v", 2)

    # Bouton de rafraichissement (st.* pour l'interactivite)
    if st.button("Rafraichir les donnees", key="bck_survey_refresh"):
        st.cache_data.clear()

    df = load_gsheet_df(_survey)
    stx.st_bar_chart(df, x="Question", y="Score")
```

### 4.3. Donnees dans un graphique avec style

```python
# blocks/_atomic/bck_kpi_dashboard.py

import streamtex as stx
from streamtex import *
from streamtex.gsheet import GSheetSource, load_gsheet

_kpis = GSheetSource(sheet_id="...", tab="KPIs", range="A1:C5")

def build():
    data = load_gsheet(_kpis)

    gap = Style("gap:24px;", "kpi_gap")
    with st_grid(cols=len(data), grid_style=gap) as g:
        for row in data:
            with g.cell():
                stx.st_metric(
                    label=row["Indicator"],
                    value=row["Value"],
                    delta=row.get("Delta", ""),
                )
```

---

## 5. Gestion des dependances

### 5.1. Dependances obligatoires

`requests` est deja une dependance de StreamTeX (utilise dans `link_preview.py`).
`csv` et `io` sont dans la stdlib. **Aucune nouvelle dependance obligatoire.**

### 5.2. Dependances optionnelles

| Package | Usage | Installation |
|---------|-------|--------------|
| `pandas` | `load_gsheet_df()` retourne DataFrame | `uv add pandas` |
| `google-api-python-client` | mode="private" (API v4) | `uv add google-api-python-client` |
| `google-auth` | Auth service account | `uv add google-auth` |

Les imports optionnels utilisent le pattern `try/except ImportError` deja present
dans StreamTeX (cf. `export_widgets.py` pour matplotlib).

### 5.3. Groupes dans pyproject.toml

```toml
[project.optional-dependencies]
gsheet = ["google-api-python-client>=2.0", "google-auth>=2.0"]
data = ["pandas>=2.0"]
```

Installation : `uv add streamtex[gsheet,data]` ou `uv sync --extra gsheet`.

---

## 6. Securite

### 6.1. Credentials

- Le fichier `credentials.json` ne doit JAMAIS etre commite
- Ajouter `credentials*.json` au `.gitignore` du template_project
- Documenter l'utilisation de variables d'environnement comme alternative :

```python
# Alternative : credentials depuis variable d'environnement
import os

GSheetConfig(
    mode="private",
    credentials_path=os.environ.get("GSHEET_CREDENTIALS", "credentials.json"),
)
```

### 6.2. Rate limiting

- Le backend CSV public peut etre rate-limite par Google
- Le cache Streamlit (`@st.cache_data`) mitigue ce risque
- En cas de 429, lever `GSheetError` avec message explicatif

### 6.3. Validation des donnees

- Les donnees proviennent d'une source externe non controlee
- Ne JAMAIS injecter directement dans du HTML (XSS)
- `stx.st_dataframe()` et `stx.st_table()` echappent deja le contenu
- Pour `st_write()`, les donnees textuelles doivent etre echappees :

```python
from html import escape

st_write(s.medium, escape(data[0]["Name"]))
```

---

## 7. Compatibilite avec le pipeline d'export

### 7.1. Mode statique : compatible

`load_gsheet()` retourne des structures Python. Ces donnees alimentent `stx.st_dataframe()`,
`stx.st_table()`, `stx.st_line_chart()` etc., qui sont deja export-aware.

Le cycle est :
```
Google Sheets → load_gsheet() → Python data → stx.st_dataframe() → Streamlit + Export HTML
```

### 7.2. Mode dynamique : partiellement compatible

Les donnees chargees au moment du rendu seront incluses dans l'export HTML.
Mais le bouton "Rafraichir" (`st.button`) ne sera pas present dans l'export
(comportement standard des widgets interactifs).

---

## 8. Tests unitaires

### 8.1. Fichier : `tests/test_gsheet.py`

```python
# tests/test_gsheet.py

import pytest
from unittest.mock import patch, MagicMock
from streamtex.gsheet import (
    GSheetConfig, GSheetSource, GSheetError,
    load_gsheet, set_gsheet_config,
    _load_public_csv,
)


class TestGSheetSource:
    def test_from_url_extracts_id(self):
        src = GSheetSource.from_url(
            "https://docs.google.com/spreadsheets/d/1BxiMkT123/edit#gid=0"
        )
        assert src.sheet_id == "1BxiMkT123"

    def test_from_url_with_tab_and_range(self):
        src = GSheetSource.from_url(
            "https://docs.google.com/spreadsheets/d/ABC/edit",
            tab="Notes", range="A1:E30"
        )
        assert src.sheet_id == "ABC"
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


class TestGSheetConfig:
    def test_defaults(self):
        cfg = GSheetConfig()
        assert cfg.mode == "public"
        assert cfg.credentials_path is None
        assert cfg.cache_ttl == 300

    def test_set_and_get_config(self):
        cfg = GSheetConfig(mode="private", credentials_path="/tmp/creds.json")
        set_gsheet_config(cfg)
        from streamtex.gsheet import get_gsheet_config
        assert get_gsheet_config() is cfg
        # Cleanup
        set_gsheet_config(None)


class TestLoadPublicCSV:
    @patch("streamtex.gsheet.requests.get")
    def test_parses_csv_with_headers(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "Name,Grade\nAlice,15\nBob,18\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _load_public_csv("123", "Sheet1", None, headers=True)

        assert len(result) == 2
        assert result[0] == {"Name": "Alice", "Grade": "15"}
        assert result[1] == {"Name": "Bob", "Grade": "18"}

    @patch("streamtex.gsheet.requests.get")
    def test_parses_csv_without_headers(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "Alice,15\nBob,18\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _load_public_csv("123", "Sheet1", None, headers=False)

        assert result[0] == {"col_0": "Alice", "col_1": "15"}

    @patch("streamtex.gsheet.requests.get")
    def test_empty_sheet_returns_empty(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = ""
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _load_public_csv("123", "Sheet1", None, headers=True)
        assert result == []

    @patch("streamtex.gsheet.requests.get")
    def test_network_error_raises_gsheet_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("timeout")

        with pytest.raises(GSheetError, match="Failed to fetch"):
            _load_public_csv("123", "Sheet1", None, headers=True)


class TestLoadGSheet:
    def test_unknown_mode_raises(self):
        cfg = GSheetConfig(mode="magic")
        src = GSheetSource(sheet_id="123")
        with pytest.raises(ValueError, match="Unknown GSheetConfig mode"):
            load_gsheet(src, config=cfg)

    def test_private_without_credentials_raises(self):
        cfg = GSheetConfig(mode="private")
        src = GSheetSource(sheet_id="123")
        with pytest.raises(ValueError, match="credentials_path required"):
            load_gsheet(src, config=cfg)
```

Estimation : **~30 tests** couvrant les deux backends, la configuration, le parsing,
les erreurs, et l'integration cache.

---

## 9. Arbre de fichiers impactes

| Fichier | Action | Risque |
|---------|--------|--------|
| `streamtex/gsheet.py` | CREER | Nul (nouveau module) |
| `streamtex/__init__.py` | MODIFIER (6 imports) | Faible |
| `streamtex/block_helpers.py` | MODIFIER (1 methode optionnelle) | Faible |
| `pyproject.toml` | MODIFIER (optional-dependencies) | Nul |
| `tests/test_gsheet.py` | CREER | Nul |
| `documentation/coding_standards.md` | MODIFIER (section GSheet) | Nul |
| `CLAUDE.md` | MODIFIER (mentionner gsheet.py) | Nul |

**Aucun fichier existant de la librairie core n'est structurellement modifie.**

---

## 10. Plan d'implementation par phases

### Phase 1 : Backend public CSV (2-3h)

1. Creer `streamtex/gsheet.py` avec `GSheetConfig`, `GSheetSource`, `load_gsheet()`
2. Implementer `_load_public_csv()` avec `requests` + `csv`
3. Ajouter exports dans `__init__.py`
4. Creer `tests/test_gsheet.py` (~15 tests)
5. Verifier : `uv run pytest tests/ -v`

### Phase 2 : Backend API v4 (1-2h)

1. Implementer `_load_private_api()` avec `google-api-python-client`
2. Ajouter `[project.optional-dependencies]` dans `pyproject.toml`
3. Ajouter tests mockes pour le backend API
4. Documenter la configuration service account

### Phase 3 : Cache Streamlit et `load_gsheet_df()` (1h)

1. Implementer `_get_cached_loader()` avec `@st.cache_data`
2. Implementer `load_gsheet_df()` (wrapper pandas)
3. Tests avec mock pandas

### Phase 4 : Integration DI et documentation (1h)

1. Etendre `BlockHelperConfig` avec `get_gsheet_config()`
2. Ajouter section dans `coding_standards.md`
3. Mettre a jour `CLAUDE.md`
4. Creer un bloc de demonstration dans les manuels

### Phase 5 : Bloc de demonstration (optionnel, 1h)

1. Creer `stx_manual_advanced/blocks/_atomic/bck_gsheet_import.py`
2. Utiliser une feuille Google publique de demonstration
3. Montrer les 3 patterns : table, chart, metrics

---

## 11. Alternatives evaluees et rejetees

### Alternative 1 : Composant Streamlit custom (st.experimental_data_editor)

Streamlit offre `st.experimental_connection` pour les sources de donnees.
Rejete car : pas de controle sur le rendu (incompatible avec le pipeline d'export
StreamTeX), dependance a une API experimentale instable.

### Alternative 2 : Fichier CSV/JSON synchronise manuellement

Le workflow "exporter CSV → placer dans static/ → charger dans bloc" existe deja.
Rejete comme solution primaire car : desynchronisation, friction manuelle.
Reste valide comme fallback hors-ligne.

### Alternative 3 : Module independant (pip install streamtex-gsheet)

Un package separe eviterait de grossir le core. Rejete pour la Phase 1 car :
la fonctionnalite est petite (~200 lignes), n'ajoute aucune dependance obligatoire,
et beneficie du DI pattern existant. A reconsiderer si d'autres sources de donnees
sont ajoutees (Notion, Airtable, etc.) — dans ce cas, factoriser en
`streamtex/datasources/` avec un backend par fichier.

---

## 12. Diagramme d'architecture

```
┌──────────────────────────────────────────────────────┐
│  Bloc utilisateur (bck_grades.py)                    │
│                                                      │
│  grades = GSheetSource.from_url("https://...")       │
│  df = load_gsheet_df(grades)                         │
│  stx.st_dataframe(df)                                │
└──────────┬───────────────────────────┬───────────────┘
           │                           │
           ▼                           ▼
┌──────────────────┐       ┌───────────────────────┐
│  gsheet.py       │       │  export_widgets.py     │
│                  │       │                        │
│  _load_public_csv│       │  st_dataframe()        │
│  _load_private_  │       │  → st.dataframe() [ST] │
│  api             │       │  → export_append() [EX]│
└──────────┬───────┘       └───────────────────────┘
           │
           ▼
┌──────────────────┐
│  @st.cache_data  │
│  (TTL configurable)
└──────────┬───────┘
           │
           ▼
┌──────────────────┐       ┌───────────────────────┐
│  Backend CSV     │  OR   │  Backend API v4       │
│  (requests.get)  │       │  (google-api-client)  │
└──────────────────┘       └───────────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────────┐
│              Google Sheets                            │
└──────────────────────────────────────────────────────┘
```

---

## 13. Questions ouvertes

1. **Faut-il supporter d'autres sources de donnees (Notion, Airtable) dans la meme API ?**
   Si oui, generaliser avec une interface `DataSource` abstraite des la Phase 1.

2. **Le cache doit-il etre invalidable depuis l'UI ?**
   Un `st.button("Refresh")` + `st.cache_data.clear()` est fonctionnel mais brutal
   (invalide TOUT le cache). Envisager un cache par cle de source.

3. **Faut-il un `st_gsheet()` (composant de rendu) en plus de `load_gsheet()` (chargement) ?**
   Position actuelle : NON. `load_gsheet()` retourne des donnees, l'utilisateur choisit
   le composant de rendu (`st_dataframe`, `st_table`, `st_line_chart`). C'est plus
   flexible et conforme a la philosophie StreamTeX (separation donnees / rendu).

---

*Proposition generee le 2026-02-20 apres analyse approfondie du projet StreamTeX v0.2.0.*
*Aucun fichier modifie. Ce document est un plan d'implementation a valider.*
