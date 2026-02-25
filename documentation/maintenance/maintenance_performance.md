# Plan de Maintenance : Performance de la Librairie StreamTeX

> **Date** : 2026-02-25
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 2.0
> **Statut** : Audité et corrigé — prêt pour exécution

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Périmètre et méthode de validation](#2-périmètre-et-méthode-de-validation)
3. [Métriques actuelles](#3-métriques-actuelles)
4. [Catégorie A — Import initial (démarrage à froid)](#4-catégorie-a--import-initial-démarrage-à-froid)
5. [Catégorie B — Rendu par re-run (chemin chaud)](#5-catégorie-b--rendu-par-re-run-chemin-chaud)
6. [Catégorie C — E/S fichiers et réseau](#6-catégorie-c--es-fichiers-et-réseau)
7. [Tableau récapitulatif](#7-tableau-récapitulatif)
8. [Plan d'action recommandé](#8-plan-daction-recommandé)
9. [Recherche future — Réduction des appels DOM](#9-recherche-future--réduction-des-appels-dom)
10. [Bonnes pratiques déjà en place](#10-bonnes-pratiques-déjà-en-place)

---

## 1. Résumé exécutif

### Le problème

Le chargement d'une page avec ~10 blocs est perçu comme lent. L'analyse en profondeur de la librairie `streamtex/` révèle **3 familles d'optimisations sans risque fonctionnel** :

| Catégorie | Impact estimé | Nb d'optimisations | Risque fonctionnel |
|-----------|--------------|--------------------|--------------------|
| **A. Import initial** (cold start) | 300-600ms gaspillés | 3 optimisations | Nul |
| **B. Rendu par re-run** (chemin chaud) | Accumulation sur chaque interaction | 3 optimisations | Nul |
| **C. E/S fichiers et réseau** | I/O disque/réseau à chaque re-render | 2 optimisations | Nul |

Une 4e famille (**D. Réduction des appels DOM**) offre un potentiel de gain important mais nécessite un travail de recherche préalable car les corrections impactent l'architecture CSS/JS fondamentale de la librairie. Elle est documentée en [section 9](#9-recherche-future--réduction-des-appels-dom).

### Architecture Streamlit : le contexte fondamental

Streamlit **ré-exécute l'intégralité du script Python** à chaque interaction utilisateur (clic, changement de widget, navigation). Ce n'est pas un bug — c'est l'architecture de Streamlit. Cela signifie que **tout ce qui n'est pas mis en cache est recalculé à chaque interaction**.

```
┌──────────────────────────────────────────────────────────┐
│ Utilisateur clique un widget                             │
│         ↓                                                │
│ Streamlit ré-exécute book.py depuis le début             │
│         ↓                                                │
│ import streamtex (si premier run)  ← Catégorie A        │
│         ↓                                                │
│ st_book() s'exécute :                                    │
│   ├─ load_css()          ← E/S fichier (Cat. C)         │
│   ├─ setup_bibliography  ← Parsing fichier (Cat. B)     │
│   ├─ Pour chaque bloc :                                  │
│   │   ├─ block.build()                                   │
│   │   │   ├─ st_write()   ← st.html()                   │
│   │   │   ├─ st_grid()    ← N×st.html()                 │
│   │   │   ├─ st_image()   ← base64 re-encode (Cat. B)   │
│   │   │   ├─ st_code()    ← Pygments re-run (Cat. B)    │
│   │   │   └─ st_list()    ← N×st.html()                 │
│   │   └─ st_space()       ← st.html()                   │
│   └─ marker navigation    ← ~300 lignes JS              │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Périmètre et méthode de validation

### Périmètre

Ce document couvre **uniquement les optimisations du code de la librairie `streamtex/`**. Sont hors périmètre :
- Les bonnes pratiques d'utilisation dans les projets utilisateurs (blocs `build()`, choix de styles)
- Les manuels et projets de démonstration (`documentation/manuals/`, `projects/`)
- Les optimisations qui modifient l'API publique de la librairie

### Principe directeur

**Chaque optimisation doit avoir un risque fonctionnel nul.** Si une optimisation présente un risque, elle est classée en "recherche future" (section 9) et ne sera exécutée qu'après prototypage et validation.

### Couverture de tests existante

La librairie dispose de **203 tests unitaires** (`uv run pytest tests/ -v`). Les composants ciblés ont une couverture complète :

| Composant | Fichier de test | Nb tests | Couverture |
|-----------|----------------|----------|------------|
| `container.py` | `test_container.py` | ~95 | CSS, markers, export, imbrication |
| `grid.py` | `test_grid.py` | ~60 | Styles, compteur, templates CSS |
| `list.py` | `test_list.py` | ~50 | Niveaux, bullets, context vars |
| `image.py` | `test_image.py` | ~40 | Chemins, base64, MIME, URIs |
| `bib.py` | `test_bib.py` | ~100 | Parsing, formatage, citations |
| `code.py` | `test_code.py` | ~25 | Pygments, numéros de ligne, CSS |
| `gsheet.py` | `test_gsheet.py` | ~40 | URLs, CSV, modes auth |
| `export_widgets.py` | `test_export_widgets.py` | ~50 | Buffer, HTML, DataFrames |
| `utils.py` | `test_utils.py` | ~20 | Clés uniques, strip_html |

### Validation après chaque sprint

```bash
# 1. Tests unitaires (obligatoire)
uv run pytest tests/ -v

# 2. Tests visuels (recommandé) — vérifier le rendu sur les 3 projets de test
./run-test-projects.sh --intro --advanced --collection
```

### Mesure de baseline

Avant de commencer les optimisations, mesurer les temps de référence :

```bash
# Cold start — temps d'import de la librairie
uv run python -c "import time; t=time.perf_counter(); import streamtex; print(f'Import: {(time.perf_counter()-t)*1000:.0f}ms')"

# Warm start — temps de ré-import (déjà en cache Python)
uv run python -c "
import time
import streamtex  # warm up
import importlib
importlib.invalidate_caches()
t=time.perf_counter()
importlib.reload(streamtex)
print(f'Reload: {(time.perf_counter()-t)*1000:.0f}ms')
"
```

---

## 3. Métriques actuelles

### Coût estimé d'une page typique (10 blocs, mode continu)

Pour une page contenant 20 `st_write`, 2 grilles (4 cellules chacune), 1 liste (5 items), 3 images locales et 1 bloc conteneur :

| Composant | Appels `st.html()` | Appels `components.html()` | Générations UUID | Lectures fichier |
|-----------|--------------------|-----------------------------|------------------|-----------------|
| Setup st_book | 3 | 0 | 0 | 1 (CSS) |
| 20× st_write | 20 | 0 | 0 | 0 |
| 2× st_grid (4 cells) | 20 | 0 | 10 | 0 |
| 1× st_list (5 items) | 24 | 0 | 12 | 0 |
| 3× st_image (local) | 3 | 0 | 0 | 3 (+ base64) |
| 1× st_block | 2 | 0 | 1 | 0 |
| Navigation markers | 0 | 1 (~300 lignes JS) | 0 | 0 |
| **TOTAL** | **~72** | **1** | **~23** | **4** |

> Chaque `st.html()` crée un élément Shadow DOM. 72 éléments Shadow DOM par page est significatif. La réduction de ce nombre est traitée en [section 9 (recherche future)](#9-recherche-future--réduction-des-appels-dom).

### Mode paginé vs continu

| Métrique | Mode continu | Mode paginé |
|----------|-------------|-------------|
| Blocs rendus par re-run | Tous (N) | 1 seul |
| `st.html()` par re-run | ~72 × (N/10) | ~72 |
| Coût première visite | Normal | Double (cache warmup) |
| Boutons cachés | 0 | N (1 par page) |
| JS injecté | ~300 lignes | ~570 lignes |

---

## 4. Catégorie A — Import initial (démarrage à froid)

Ces problèmes affectent le **premier chargement** de l'application (cold start). Après le premier import, Python cache les modules.

### A1. CRITIQUE — `pandas` importé au niveau module

**Fichier** : `streamtex/export_widgets.py:17`

```python
import pandas as pd  # ← Chargé pour TOUT le monde, même sans utiliser de DataFrame
```

| Aspect | Détail |
|--------|--------|
| **Impact** | +200-400ms au démarrage |
| **Qui est affecté** | 100% des projets (via `from streamtex import *`) |
| **Quand** | Premier import uniquement |
| **Risque fonctionnel** | **Nul** — correction transparente |
| **Tests impactés** | `test_export_widgets.py` — les tests ne vérifient pas le moment de l'import |

**Détail** : `pandas` est importé au niveau module mais n'est utilisé que dans les fonctions d'export (`_to_dataframe`, `_dataframe_to_html`, `_chart_to_svg`) — et uniquement quand `is_export_active()` est vrai. La majorité des utilisateurs ne déclenchent jamais l'export.

**Correction** : Déplacer l'import à l'intérieur des 4 fonctions qui l'utilisent.

```python
# AVANT (module level)
import pandas as pd

# APRÈS (lazy, dans chaque fonction qui utilise pd)
def _to_dataframe(data):
    import pandas as pd
    ...

def _dataframe_to_html(df):
    import pandas as pd
    ...

def _chart_to_svg(chart_func, data, ...):
    import pandas as pd
    ...
```

**Validation** : `uv run pytest tests/test_export_widgets.py -v`

---

### A2. HAUTE — `requests` + `beautifulsoup4` importés via chaîne transitive

**Fichier** : `streamtex/link_preview.py:5-8`

```python
import requests                         # +50-100ms
from bs4 import BeautifulSoup as bs     # +20-40ms
from requests.exceptions import ConnectionError, Timeout
```

**Chaîne d'import** : `__init__.py` → `utils.py` → `link_preview.py` → `requests` + `bs4`

| Aspect | Détail |
|--------|--------|
| **Impact** | +70-140ms au démarrage |
| **Qui est affecté** | 100% des projets |
| **Risque fonctionnel** | **Nul** — `_get_page_preview()` n'est jamais appelée par la librairie |
| **Tests impactés** | Aucun — la fonction n'est pas testée car jamais utilisée en interne |

**Détail** : `_get_page_preview()` est la seule fonction qui utilise `requests` et `bs4` dans ce module. Elle est ré-exportée via `utils.py` mais **n'est appelée nulle part dans la librairie**. Les autres fonctions exportées (`contain_link`, `inject_link_preview_scaffold`) ne manipulent que des chaînes de caractères et du HTML — elles n'ont pas besoin de `requests` ni de `bs4`.

**Correction** : Déplacer les 3 imports dans `_get_page_preview()` uniquement.

```python
# AVANT (module level)
import requests
from bs4 import BeautifulSoup as bs
from requests.exceptions import ConnectionError, Timeout

# APRÈS (lazy, uniquement dans la fonction qui les utilise)
def _get_page_preview(url: str) -> dict:
    import requests
    from bs4 import BeautifulSoup as bs
    from requests.exceptions import ConnectionError, Timeout
    ...
```

**Validation** : `uv run pytest tests/ -v` (aucun test spécifique à link_preview)

---

### A3. MOYENNE — `requests` importé dans `gsheet.py`

**Fichier** : `streamtex/gsheet.py:28`

```python
import requests  # Utilisé uniquement dans _load_public_csv()
```

| Aspect | Détail |
|--------|--------|
| **Impact** | Nul actuellement (déjà chargé par A2), mais **+50-100ms si A2 est corrigé** |
| **Risque fonctionnel** | **Nul** — correction transparente |
| **Tests impactés** | `test_gsheet.py` — les tests mockent `requests.get`, le mock fonctionne identiquement en lazy |

**Détail** : `requests` n'est utilisé que dans `_load_public_csv()` (mode `AuthMode.PUBLIC`). Les backends `SERVICE_ACCOUNT` et `OAUTH2` importent déjà leurs dépendances Google de manière lazy (bonne pratique). Seul le mode PUBLIC n'a pas été aligné.

**Correction** : Déplacer l'import dans `_load_public_csv()`.

```python
# AVANT (module level)
import requests

# APRÈS (lazy, dans la seule fonction qui l'utilise)
def _load_public_csv(url: str, ...):
    import requests
    ...
```

**Validation** : `uv run pytest tests/test_gsheet.py -v`

---

## 5. Catégorie B — Rendu par re-run (chemin chaud)

Ces problèmes affectent **chaque interaction utilisateur** (chaque re-run Streamlit).

### B1. CRITIQUE — Images base64 ré-encodées à chaque re-render

**Fichier** : `streamtex/image_utils.py:42-49` (appelé par `streamtex/image.py:98-99`)

```python
# image_utils.py — exécuté à CHAQUE re-render pour CHAQUE image
def _get_base64_encoded_image(file_path: str):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
```

| Aspect | Détail |
|--------|--------|
| **Impact** | Lecture disque + encodage base64 par image, par re-render |
| **Exemple** | 10 images de 500KB = 5MB lus + 6.6MB base64 générés à chaque clic |
| **Risque fonctionnel** | **Nul** — `@st.cache_data` est transparent, l'invalidation par mtime garantit la fraîcheur |
| **Tests impactés** | `test_image.py` — les tests mockent `open()`, le cache n'interfère pas avec les mocks |

**Correction** : Ajouter `@st.cache_data` basé sur le chemin et le mtime du fichier.

```python
import os
import streamlit as st

@st.cache_data(show_spinner=False)
def _get_base64_encoded_image(file_path: str, _mtime: float = None):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
```

Le site d'appel dans `image.py` doit passer le mtime :

```python
# Dans get_image_src() — après résolution du chemin
mtime = os.path.getmtime(full_path)
encoded = _get_base64_encoded_image(full_path, _mtime=mtime)
```

> **Note technique** : Le paramètre `_mtime` avec underscore est une convention Streamlit — les paramètres préfixés par `_` ne sont pas hashés pour la clé de cache mais sont utilisés pour l'invalidation. Si le fichier est modifié sur disque, le mtime change et le cache est invalidé automatiquement.

**Validation** : `uv run pytest tests/test_image.py -v` + test visuel avec un projet contenant des images

**Note** : Cette correction bénéficie aussi automatiquement aux images de couverture des collections (`collection.py:_render_project_card`) puisqu'elles passent par la même fonction `get_image_src()` → `_get_base64_encoded_image()`.

---

### B2. HAUTE — Bibliographie re-parsée à chaque re-render

**Fichier** : `streamtex/book.py:44-62` (fonction `_setup_bibliography`)

```python
# Exécuté à CHAQUE re-render dans st_book()
def _setup_bibliography(bib_sources, bib_config):
    reset_bib_registry()          # Efface tout
    for src in bib_sources:
        load_bib(src)             # Re-parse le fichier .bib depuis le disque
```

| Aspect | Détail |
|--------|--------|
| **Impact** | I/O fichier + parsing regex par re-render |
| **Exemple** | Un fichier .bib de 200 entrées re-parsé à chaque clic |
| **Risque fonctionnel** | **Nul** — le cache est transparent, l'invalidation par mtime garantit la fraîcheur |
| **Tests impactés** | `test_bib.py` — les tests appellent `parse_bibtex_string()` directement, pas `load_bib()` |

**Correction** : Cacher le parsing avec `@st.cache_data`, clé = (chemin, mtime).

```python
# Dans bib.py
@st.cache_data(show_spinner=False)
def _parse_bib_file(file_path: str, _mtime: float) -> list:
    """Parse un fichier .bib et retourne la liste des BibEntry."""
    with open(file_path, 'r') as f:
        content = f.read()
    return parse_bibtex_string(content)

def load_bib(file_path: str) -> list:
    mtime = os.path.getmtime(file_path)
    return _parse_bib_file(file_path, _mtime=mtime)
```

**Validation** : `uv run pytest tests/test_bib.py -v`

---

### B3. HAUTE — Coloration syntaxique Pygments non cachée

**Fichier** : `streamtex/code.py`

`st_code()` re-highlight le même code à chaque re-render. L'import de Pygments est déjà lazy (bonne pratique), mais le **résultat du highlighting** n'est pas mis en cache.

```python
# Exécuté à CHAQUE re-render pour CHAQUE bloc de code
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

lexer = get_lexer_by_name(language, stripall=True)    # Chaque render
formatter = HtmlFormatter(**fmt_options)               # Chaque render
highlighted = highlight(code, lexer, formatter)        # Chaque render
```

| Aspect | Détail |
|--------|--------|
| **Impact** | CPU par bloc de code, par re-render |
| **Exemple** | 5 blocs de code × highlighting Pygments = 5× le même travail |
| **Risque fonctionnel** | **Nul** — le résultat de Pygments est déterministe pour les mêmes entrées |
| **Tests impactés** | `test_code.py` — les tests valident le HTML produit, identique avec ou sans cache |

**Correction** : Extraire le highlighting dans une fonction cachée.

```python
@st.cache_data(show_spinner=False)
def _highlight_code(code: str, language: str, line_numbers: bool,
                    font_size: str, line_number_color: str) -> str:
    """Retourne le HTML Pygments pour un bloc de code donné."""
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import TextLexer, get_lexer_by_name
    # ... highlighting logic ...
    return highlighted_html
```

**Validation** : `uv run pytest tests/test_code.py -v`

---

### B4. MOYENNE — Google Sheets rechargé sans cache

**Fichier** : `streamtex/gsheet.py`

Le champ `GSheetConfig.cache_ttl: Optional[int] = 300` existe dans la config mais **n'est jamais implémenté**. Chaque re-render refait la requête HTTP.

```python
@dataclass
class GSheetConfig:
    auth_mode: str = AuthMode.SERVICE_ACCOUNT
    cache_ttl: Optional[int] = 300    # ← Existe mais IGNORÉ dans load_gsheet()
```

| Aspect | Détail |
|--------|--------|
| **Impact** | Requête HTTP par re-render (latence réseau 100-500ms) |
| **Risque fonctionnel** | **Nul** — le cache avec TTL est transparent, les données sont rafraîchies automatiquement |
| **Tests impactés** | `test_gsheet.py` — les tests mockent `requests.get()`, le cache n'interfère pas |

**Correction** : Implémenter le cache sur `_load_public_csv` et les fonctions backend.

> **Attention technique** : `@st.cache_data(ttl=...)` ne supporte pas un TTL dynamique provenant d'un argument de fonction. La solution est d'utiliser une fonction wrapper avec un TTL fixe par défaut, ou d'utiliser le pattern `st.cache_data` avec un hash personnalisé.

```python
# Approche recommandée : TTL fixe par défaut (300s), configurable via constante
_DEFAULT_CACHE_TTL = 300

@st.cache_data(ttl=_DEFAULT_CACHE_TTL, show_spinner=False)
def _load_public_csv_cached(url: str, has_header: bool) -> list:
    import requests
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return _parse_csv_text(resp.text, has_header=has_header)

def _load_public_csv(source, config):
    # Si cache_ttl est personnalisé et différent du défaut, on bypass le cache
    if config.cache_ttl and config.cache_ttl != _DEFAULT_CACHE_TTL:
        # Appel direct sans cache pour TTL personnalisé
        import requests
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return _parse_csv_text(resp.text, has_header=source.has_header)
    return _load_public_csv_cached(url, source.has_header)
```

**Validation** : `uv run pytest tests/test_gsheet.py -v`

---

## 6. Catégorie C — E/S fichiers et réseau

### C1. BASSE — `default.css` relu à chaque re-render

**Fichier** : `streamtex/book.py:255-267`

```python
def load_css(file_name: str):
    with resources.open_text('streamtex.static', file_name) as f:
        st.html(f'<style>{f.read()}</style>')
```

| Aspect | Détail |
|--------|--------|
| **Impact** | **Faible en pratique** — le chemin principal utilise `importlib.resources.open_text()` qui bénéficie du cache du système d'import Python. Seul le chemin de fallback (`except`) fait une vraie lecture disque. |
| **Risque fonctionnel** | **Nul** |
| **Tests impactés** | `test_book_integration.py` — ne teste pas `load_css()` directement |

**Correction** : Cacher le contenu CSS en mémoire avec `@st.cache_resource`.

```python
@st.cache_resource
def _read_css(file_name: str) -> str:
    with resources.open_text('streamtex.static', file_name) as f:
        return f.read()

def load_css(file_name: str):
    st.html(f'<style>{_read_css(file_name)}</style>')
```

> **Note** : Le gain réel est faible car `resources.open_text()` bénéficie déjà d'un cache implicite Python. Cette optimisation est un "nice to have" mais pas prioritaire.

**Validation** : `uv run pytest tests/test_book_integration.py -v` + test visuel (vérifier que les styles CSS sont bien appliqués)

---

### C2. INFO — Résolution des chemins statiques avec I/O

**Fichier** : `streamtex/image.py:108-124`

Pour chaque image non-URL, la fonction itère `static_sources` et teste 2 sous-dossiers par source via `os.path.isfile()`.

| Aspect | Détail |
|--------|--------|
| **Impact** | `2 × len(static_sources)` appels `stat()` par image, par re-render |
| **Risque fonctionnel** | **Nul** |

**Correction** : Résolu automatiquement par B1 — une fois `_get_base64_encoded_image` cachée, la résolution de chemin complète (y compris les appels `os.path.isfile()`) n'est exécutée qu'une seule fois par image grâce au cache. Pas de correction supplémentaire nécessaire si B1 est implémenté.

---

### C3. INFO — Inspector fait du parsing AST + walk disque

**Fichier** : `streamtex/inspector.py` (fonction `discover_sources`)

| Aspect | Détail |
|--------|--------|
| **Impact** | Significatif mais **partiellement atténué** |
| **Risque fonctionnel** | **Nul** |
| **Atténuation existante** | `_get_cached_project_files()` cache déjà les résultats dans `st.session_state` par racine de projet |

Le module inspector parse l'AST Python et parcourt le disque, mais :
1. C'est **opt-in** — seulement quand l'inspector est ouvert en mode développement
2. Le scan de fichiers projet est **déjà caché** dans `st.session_state`
3. Seule la découverte de sources au niveau bloc est non cachée

**Correction** : Pas de correction immédiate nécessaire. Le cache `session_state` existant couvre le cas d'usage principal.

---

## 7. Tableau récapitulatif

### Par priorité d'impact (optimisations librairie uniquement)

| # | Sévérité | Catégorie | Problème | Impact estimé | Complexité | Risque fonctionnel |
|---|----------|-----------|----------|---------------|------------|-------------------|
| **A1** | CRITIQUE | Import | `pandas` eager import | +200-400ms cold start | Faible | **Nul** |
| **B1** | CRITIQUE | Rendu | Images base64 non cachées | I/O × N images × re-render | Faible | **Nul** |
| **A2** | HAUTE | Import | `requests`+`bs4` chaîne transitive | +70-140ms cold start | Faible | **Nul** |
| **B2** | HAUTE | Rendu | Bibliographie re-parsée | I/O fichier × re-render | Faible | **Nul** |
| **B3** | HAUTE | Rendu | Pygments non caché | CPU × blocs code × re-render | Faible | **Nul** |
| **B4** | MOYENNE | Rendu | Google Sheets sans cache | Requête HTTP × re-render | Faible | **Nul** |
| **A3** | MOYENNE | Import | `requests` dans gsheet.py | +50-100ms si A2 corrigé | Faible | **Nul** |
| **C1** | BASSE | I/O | CSS relu du disque | Faible (cache Python implicite) | Faible | **Nul** |

### Éléments classés en recherche future (section 9)

| # | Catégorie | Problème | Gain potentiel | Pourquoi "recherche" |
|---|-----------|----------|----------------|---------------------|
| **D1** | DOM | 2 `st.html()` par conteneur | -50% appels `st.html()` sur conteneurs | Correction proposée architecturalement incorrecte — nécessite prototypage |
| **D2** | DOM | ~300 lignes JS marker ré-injectées | -1 iframe lourd par re-render | Risque fonctionnel sur navigation clavier |
| **D3** | DOM | Nav paginée (JS + N boutons) | -N boutons serveur | Risque fonctionnel sur navigation |
| **D4** | DOM | UUID cryptographique pour CSS | ~23 appels système/page | Gain négligeable, risque de collision CSS |
| **A4** | Import | Lazy modules via `__getattr__` | -50-100ms cold start | Complexité élevée, risque de régressions |

---

## 8. Plan d'action recommandé

### Sprint 1 — Lazy imports, zéro risque

**Objectif** : Réduire le temps de cold start de 300-600ms.

**Principe** : Déplacer les `import` lourds du niveau module vers l'intérieur des fonctions qui les utilisent. C'est un pattern Python standard, sans effet de bord.

| # | Action | Fichier | Gain estimé |
|---|--------|---------|-------------|
| A1 | Lazy import `pandas` | `export_widgets.py` | -200-400ms cold start |
| A2 | Lazy import `requests`+`bs4` | `link_preview.py` | -70-140ms cold start |
| A3 | Lazy import `requests` | `gsheet.py` | -50-100ms cold start |

**Validation Sprint 1** :

```bash
# 1. Tests unitaires
uv run pytest tests/test_export_widgets.py tests/test_gsheet.py -v

# 2. Mesure du gain cold start (comparer avec la baseline)
uv run python -c "import time; t=time.perf_counter(); import streamtex; print(f'Import: {(time.perf_counter()-t)*1000:.0f}ms')"

# 3. Test fonctionnel rapide — vérifier que l'export et gsheet fonctionnent
uv run pytest tests/ -v
```

---

### Sprint 2 — Cache re-render, zéro risque

**Objectif** : Éliminer les recalculs redondants à chaque interaction utilisateur.

**Principe** : Ajouter `@st.cache_data` sur les fonctions pures dont le résultat est déterministe pour les mêmes entrées. Le décorateur Streamlit gère automatiquement le cycle de vie du cache.

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| B1 | `@st.cache_data` sur base64 images | `image_utils.py`, `image.py` | -I/O majeur par re-render |
| B2 | Cache parsing bibliographie | `bib.py` | -I/O fichier par re-render |
| B3 | `@st.cache_data` Pygments | `code.py` | -CPU par bloc code |

**Validation Sprint 2** :

```bash
# 1. Tests unitaires des composants modifiés
uv run pytest tests/test_image.py tests/test_bib.py tests/test_code.py -v

# 2. Tests complets
uv run pytest tests/ -v

# 3. Test visuel — vérifier le rendu des images, biblio, et blocs de code
./run-test-projects.sh --intro --advanced
```

---

### Sprint 3 — Cache I/O et réseau

**Objectif** : Éliminer les requêtes réseau et lectures fichier redondantes.

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| B4 | Implémenter cache TTL GSheet | `gsheet.py` | -requête HTTP par re-render |
| C1 | `@st.cache_resource` sur CSS | `book.py` | -1 lecture fichier/re-render (gain faible) |

**Validation Sprint 3** :

```bash
# 1. Tests unitaires
uv run pytest tests/test_gsheet.py tests/test_book_integration.py -v

# 2. Tests complets
uv run pytest tests/ -v

# 3. Test visuel — vérifier que les styles CSS sont appliqués
./run-test-projects.sh --intro --advanced --collection
```

---

## 9. Recherche future — Réduction des appels DOM

Cette section documente les optimisations qui offrent un **potentiel de gain significatif** mais nécessitent un travail de recherche et de prototypage avant implémentation, car elles touchent à l'architecture CSS/JS fondamentale de la librairie.

### D1. Réduire les appels `st.html()` par conteneur

#### Le problème

Chaque appel à `st_block()`, `st_span()`, et leurs utilisateurs (`st_grid`, `st_list`) émet **2 appels `st.html()`** :

1. **Appel 1** — Injection du `<style>` avec les règles CSS (en dehors du `st.container()`)
2. **Appel 2** — Insertion du `<span>` marker invisible (à l'intérieur du `st.container()`)

Le sélecteur CSS `:has()` fait le lien entre les deux :

```css
/* Le <style> cible le div parent qui CONTIENT le <span> marker */
div:has(> .element-container > .stHtml > span.block-xxxx) {
    /* styles appliqués */
}
```

#### Pourquoi c'est le contributeur dominant

Pour une page typique (10 blocs) :

| Composant | `st.html()` propres | `st.html()` via st_block | Total |
|-----------|--------------------|-----------------------|-------|
| `st_block()` | 2 | — | 2 |
| `st_span()` | 2 | — | 2 |
| `st_grid()` (conteneur) | 2 | — | 2 |
| Cellule `st_grid()` | — | 2 (via st_block) | 2 |
| `st_list()` (conteneur) | 2 | 2 (via st_block) | 4 |
| Item `st_list()` | 2 | 2 (via st_block) | 4 |

**Exemples concrets** :
- Grille 3×3 = 2 (grille) + 9 × 2 (cellules) = **20 `st.html()`**
- Liste 5 items = 4 (liste) + 5 × 4 (items) = **24 `st.html()`**
- **Total page typique** : ~72 `st.html()`, dont **~46 viennent des conteneurs** (64%)

**Gain potentiel** : Si chaque conteneur passait de 2 à 1 `st.html()`, on économiserait ~23 appels Shadow DOM par page, soit une réduction d'environ **32%** du nombre total d'éléments Shadow DOM.

#### Pourquoi la correction initialement proposée est incorrecte

Le document v1.0 proposait de simplement concaténer le CSS et le marker :

```python
# PROPOSÉ (v1.0) — NE FONCTIONNE PAS
st.html(f'{css}<span class="{block_id}">')
```

**Cette correction est architecturalement impossible** car elle viole la contrainte de placement :

```
Structure DOM requise par le sélecteur :has() :

┌─ div (parent Streamlit)  ← CSS APPLIQUÉ ICI via :has()
│  ├─ .stHtml
│  │  └─ <style>...         ← DOIT être ici (en dehors du container)
│  │
│  └─ st.container()
│     └─ .stHtml
│        └─ <span marker>   ← DOIT être ici (à l'intérieur du container)
```

Si on fusionne les deux dans un seul `st.html()`, le `<style>` et le `<span>` se retrouvent **au même endroit** dans le DOM. Le sélecteur `:has()` ne trouvera plus le marker **à l'intérieur** du container, et les styles ne s'appliqueront plus.

De plus, chaque `st.html()` crée un élément Shadow DOM isolé. Un `<style>` dans un Shadow DOM ne peut styler que les éléments à l'intérieur de ce même Shadow DOM — pas les éléments du DOM principal (Light DOM) ou d'autres Shadow DOM.

#### Impact sur les tests existants

Les tests de `container.py` (**~95 tests**), `grid.py` (**~60 tests**) et `list.py` (**~50 tests**) valident explicitement :
- Le nombre d'appels `st.html()` et leur contenu
- La structure CSS générée (sélecteurs `:has()`)
- L'insertion du marker span

Toute modification de l'architecture CSS/marker nécessiterait une mise à jour massive des tests.

#### Pistes de recherche

1. **Déplacer le `<style>` à l'intérieur du container** — Tester si un `<style>` injecté via `st.html()` à l'intérieur d'un `st.container()` peut styler le container parent. Cela dépend du comportement du Shadow DOM de Streamlit (version ≥1.54). Si ça fonctionne, on peut fusionner CSS et marker en 1 seul `st.html()` à l'intérieur.

2. **Batch CSS injection** — Collecter tous les `<style>` d'une page et les injecter en un seul `st.html()` au début, puis n'émettre que les markers (1 `st.html()` par conteneur au lieu de 2). Cela nécessite un mécanisme de collecte en deux passes.

3. **CSS global avec classes prédéfinies** — Au lieu de générer des sélecteurs `:has()` uniques par conteneur, utiliser des classes CSS prédéfinies et les appliquer directement au markup Streamlit. Cela nécessite de comprendre comment Streamlit gère les attributs de classes sur les containers natifs.

**Prochaine étape** : Créer un prototype minimal testant la piste 1 sur Streamlit 1.54+ et mesurer si le Shadow DOM permet la remontée CSS.

---

### D2. Navigation marker : ~300 lignes de JS ré-injectées

**Fichier** : `streamtex/marker.py:183-483`

La navigation par marqueurs injecte ~300 lignes de JavaScript via `components.html()` (iframe) à chaque re-render. 8 remplacements `.replace()` de chaînes sont effectués pour injecter les données dynamiques dans le JS statique.

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | Éliminer la ré-injection du JS scaffold à chaque re-render |
| **Risque fonctionnel** | **Élevé** — la navigation clavier PageUp/PageDown est fondamentale |
| **Complexité** | Élevée — séparer JS statique vs données dynamiques |

**Piste** : Séparer le JS en 2 parties : un scaffold statique (injecté une seule fois via `st.session_state`) et les données dynamiques (markers, config) injectées à chaque render. Le scaffold écouterait un événement custom pour recevoir les nouvelles données.

---

### D3. Navigation paginée : ~268 lignes JS + N boutons cachés

**Fichier** : `streamtex/book.py:581-849, 996-999`

En mode paginé, chaque re-render crée **N boutons Streamlit cachés** (1 par page) et injecte ~268 lignes de JS via `components.html()`.

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | Réduire N boutons à une fenêtre de ±5 pages |
| **Risque fonctionnel** | **Moyen** — la navigation par numéro de page pourrait être impactée |
| **Complexité** | Moyenne |

**Piste** : Limiter les boutons cachés à une fenêtre autour de la page courante (ex: pages [current-5, current+5]) et recréer la fenêtre dynamiquement à chaque changement de page.

---

### D4. UUID cryptographique pour noms CSS

**Fichier** : `streamtex/utils.py:31-33`

```python
def generate_key(prefix: str = "block"):
    return f"{prefix}-{uuid.uuid4().hex}"
```

`uuid.uuid4()` utilise `/dev/urandom` (appel système cryptographique).

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | ~23 appels système par page (négligeable) |
| **Risque fonctionnel** | **Moyen** — un compteur simple produit les mêmes IDs entre re-runs (`block-1`, `block-2`...). Si Streamlit ne nettoie pas parfaitement le Shadow DOM entre re-runs, les anciens sélecteurs CSS pourraient interférer avec les nouveaux. |
| **Complexité** | Faible |

**Décision** : Gain trop faible pour justifier le risque. **Non recommandé** sauf si mesuré comme un bottleneck réel.

---

### A4. Lazy module loading via `__getattr__`

**Fichier** : `streamtex/__init__.py`

Le fichier `__init__.py` importe tous les modules au chargement : mermaid, plantuml, tikz, bib, gsheet, inspector, collection...

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | +50-100ms cold start |
| **Risque fonctionnel** | **Élevé** — le pattern `__getattr__` pour lazy loading peut casser `from streamtex import *`, l'auto-complétion IDE, et les introspections de module |
| **Complexité** | Élevée |

**Décision** : Reporter après que les Sprints 1-3 auront été implémentés et mesurés. Si le cold start reste problématique après A1/A2/A3, envisager cette optimisation avec un prototype isolé.

---

## 10. Bonnes pratiques déjà en place

L'analyse a aussi révélé des choix de conception **bien faits** qu'il faut préserver :

| Composant | Bonne pratique |
|-----------|---------------|
| **Pygments** | Import lazy dans `st_code()` (try/except, pas module-level) |
| **Mermaid** | `mermaid-py` importé lazy seulement pendant l'export |
| **Google API libs** | `google-auth`, `googleapiclient` importés lazy dans les fonctions backend |
| **matplotlib** | Import lazy dans `_chart_to_svg()` |
| **Inspector** | Import lazy dans `st_book()` seulement quand activé |
| **Inspector files** | Cache `session_state` sur le scan de fichiers projet |
| **PlantUML SVG** | `@st.cache_data(show_spinner=False)` sur le fetch HTTP |
| **TikZ compilation** | `@st.cache_data(show_spinner=False)` sur le subprocess LaTeX |
| **Block registries** | Cache dict manuel qui persiste entre re-runs |
| **Mode paginé** | Ne rend qu'un seul bloc par re-render (après cache warmup) |
| **Styles de base** | Attributs de classe = singletons créés une seule fois |
| **String building** | `"".join(parts)` dans write.py (pas de concaténation répétée) |
