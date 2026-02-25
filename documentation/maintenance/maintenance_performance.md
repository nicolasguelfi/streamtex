# Plan de Maintenance : Performance de la Librairie StreamTeX

> **Date** : 2026-02-25
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 3.0
> **Statut** : Sprints 1-3 terminés — reste uniquement la recherche future (section 9)

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Périmètre et méthode de validation](#2-périmètre-et-méthode-de-validation)
3. [Métriques actuelles](#3-métriques-actuelles)
4. [Catégorie A — Import initial (démarrage à froid)](#4-catégorie-a--import-initial-démarrage-à-froid)
5. [Catégorie B — Rendu par re-run (chemin chaud)](#5-catégorie-b--rendu-par-re-run-chemin-chaud)
6. [Catégorie C — E/S fichiers et réseau](#6-catégorie-c--es-fichiers-et-réseau)
7. [Tableau récapitulatif](#7-tableau-récapitulatif)
8. [Plan d'action — Bilan d'exécution](#8-plan-daction--bilan-dexécution)
9. [Recherche future — Réduction des appels DOM](#9-recherche-future--réduction-des-appels-dom)
10. [Bonnes pratiques déjà en place](#10-bonnes-pratiques-déjà-en-place)

---

## 1. Résumé exécutif

### Le problème initial

Le chargement d'une page avec ~10 blocs était perçu comme lent. L'analyse en profondeur de la librairie `streamtex/` a révélé **3 familles d'optimisations sans risque fonctionnel** :

| Catégorie | Impact estimé | Nb d'optimisations | Statut |
|-----------|--------------|--------------------|----|
| **A. Import initial** (cold start) | 300-600ms gaspillés | 3 optimisations | **FAIT** |
| **B. Rendu par re-run** (chemin chaud) | Accumulation sur chaque interaction | 4 optimisations | **FAIT** |
| **C. E/S fichiers et réseau** | I/O disque/réseau à chaque re-render | 2 optimisations | **FAIT** |

Une 4e famille (**D. Réduction des appels DOM**) offre un potentiel de gain important mais nécessite un travail de recherche préalable car les corrections impactent l'architecture CSS/JS fondamentale de la librairie. Elle est documentée en [section 9](#9-recherche-future--réduction-des-appels-dom).

### Architecture Streamlit : le contexte fondamental

Streamlit **ré-exécute l'intégralité du script Python** à chaque interaction utilisateur (clic, changement de widget, navigation). Ce n'est pas un bug — c'est l'architecture de Streamlit. Cela signifie que **tout ce qui n'est pas mis en cache est recalculé à chaque interaction**.

```
┌──────────────────────────────────────────────────────────┐
│ Utilisateur clique un widget                             │
│         ↓                                                │
│ Streamlit ré-exécute book.py depuis le début             │
│         ↓                                                │
│ import streamtex (si premier run)  ← Catégorie A ✅     │
│         ↓                                                │
│ st_book() s'exécute :                                    │
│   ├─ load_css()          ← caché @cache_resource ✅     │
│   ├─ setup_bibliography  ← caché @cache_data ✅         │
│   ├─ Pour chaque bloc :                                  │
│   │   ├─ block.build()                                   │
│   │   │   ├─ st_write()   ← st.html()                   │
│   │   │   ├─ st_grid()    ← N×st.html()                 │
│   │   │   ├─ st_image()   ← caché @cache_data ✅        │
│   │   │   ├─ st_code()    ← caché @cache_data ✅        │
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

La librairie dispose de **766 tests unitaires** (`uv run pytest tests/ -v`). Les composants ciblés ont une couverture complète :

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
| `export.py` | `test_export_guard.py` | ~30 | Guard, buffer, config |
| `utils.py` | `test_utils.py` | ~20 | Clés uniques, strip_html |

### Validation après chaque sprint

```bash
# 1. Tests unitaires (obligatoire)
uv run pytest tests/ -v

# 2. Lint (obligatoire)
uv run ruff check streamtex/

# 3. Tests visuels (recommandé) — vérifier le rendu sur les 3 projets de test
./run-test-projects.sh --intro --advanced --collection
```

### Mesure de baseline

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
| Setup st_book | 3 | 0 | 0 | ~~1 (CSS)~~ 0 (caché) |
| 20x st_write | 20 | 0 | 0 | 0 |
| 2x st_grid (4 cells) | 20 | 0 | 10 | 0 |
| 1x st_list (5 items) | 24 | 0 | 12 | 0 |
| 3x st_image (local) | 3 | 0 | 0 | ~~3 (+ base64)~~ 0 (caché) |
| 1x st_block | 2 | 0 | 1 | 0 |
| Navigation markers | 0 | 1 (~300 lignes JS) | 0 | 0 |
| **TOTAL** | **~72** | **1** | **~23** | **0** (tout caché) |

> Chaque `st.html()` crée un élément Shadow DOM. 72 éléments Shadow DOM par page est significatif. La réduction de ce nombre est traitée en [section 9 (recherche future)](#9-recherche-future--réduction-des-appels-dom).

### Mode paginé vs continu

| Métrique | Mode continu | Mode paginé |
|----------|-------------|-------------|
| Blocs rendus par re-run | Tous (N) | 1 seul |
| `st.html()` par re-run | ~72 x (N/10) | ~72 |
| Coût première visite | Normal | Double (cache warmup) |
| Boutons cachés | 0 | N (1 par page) |
| JS injecté | ~300 lignes | ~570 lignes |

---

## 4. Catégorie A — Import initial (démarrage à froid)

Ces problèmes affectaient le **premier chargement** de l'application (cold start). Après le premier import, Python cache les modules.

### A1. ~~CRITIQUE~~ FAIT — `pandas` importé au niveau module

**Fichier** : `streamtex/export_widgets.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | +200-400ms au démarrage |
| **Statut** | **FAIT** |

**Implémentation** : `pandas` est importé uniquement dans les fonctions qui l'utilisent (`_to_dataframe`, `_dataframe_to_html`, `_chart_to_svg`). Les annotations de type utilisent `TYPE_CHECKING` pour que ruff et les IDE voient le type sans import runtime.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

def _to_dataframe(data) -> "pd.DataFrame":
    import pandas as pd  # lazy — uniquement quand appelé
    ...
```

---

### A2. ~~HAUTE~~ FAIT — `requests` + `beautifulsoup4` importés via chaîne transitive

**Fichier** : `streamtex/link_preview.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | +70-140ms au démarrage |
| **Statut** | **FAIT** |

**Implémentation** : Les 3 imports (`requests`, `bs4`, `requests.exceptions`) sont déplacés à l'intérieur de `_get_page_preview()` — la seule fonction qui les utilise. Le module ne fait plus aucun import lourd au chargement.

```python
def _get_page_preview(url: str):
    import requests
    from bs4 import BeautifulSoup as bs
    # requests.exceptions accédé via requests.exceptions.ConnectionError
    ...
```

---

### A3. ~~MOYENNE~~ FAIT — `requests` importé dans `gsheet.py`

**Fichier** : `streamtex/gsheet.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | +50-100ms si A2 corrigé |
| **Statut** | **FAIT** |

**Implémentation** : `requests` est importé uniquement dans `_fetch_public_csv_cached()`, la fonction interne cachée qui effectue le fetch HTTP. Aucun import `requests` au niveau module.

```python
@st.cache_data(ttl=_DEFAULT_CACHE_TTL, show_spinner=False)
def _fetch_public_csv_cached(url: str, headers: bool) -> List[Dict[str, Any]]:
    import requests  # lazy — uniquement quand appelé
    ...
```

---

## 5. Catégorie B — Rendu par re-run (chemin chaud)

Ces problèmes affectaient **chaque interaction utilisateur** (chaque re-run Streamlit).

### B1. ~~CRITIQUE~~ FAIT — Images base64 ré-encodées à chaque re-render

**Fichiers** : `streamtex/image_utils.py`, `streamtex/image.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | Lecture disque + encodage base64 par image, par re-render |
| **Statut** | **FAIT** |

**Implémentation** : `@st.cache_data(show_spinner=False)` sur `_get_base64_encoded_image()` avec paramètre `_mtime` pour invalidation automatique. Le site d'appel dans `image.py` passe `os.path.getmtime(file_path)`.

```python
# image_utils.py
@st.cache_data(show_spinner=False)
def _get_base64_encoded_image(file_path: str, _mtime: float = 0):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# image.py — site d'appel
mtime = os.path.getmtime(file_path)
encoded_image = __get_base64_encoded_image(file_path, _mtime=mtime)
```

> Cette correction bénéficie aussi automatiquement aux images de couverture des collections (`collection.py:_render_project_card`).

---

### B2. ~~HAUTE~~ FAIT — Bibliographie re-parsée à chaque re-render

**Fichier** : `streamtex/bib.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | I/O fichier + parsing regex par re-render |
| **Statut** | **FAIT** |

**Implémentation** : `@_cache_bib` (alias de `@st.cache_data(show_spinner=False)`) sur `_load_bib_cached()` avec paramètre `_mtime`. La fonction `load_bib()` calcule le mtime et délègue au cache.

```python
@_cache_bib
def _load_bib_cached(path: str, ext: str, _mtime: float = 0) -> List[BibEntry]:
    ...

def load_bib(path: str) -> List[BibEntry]:
    mtime = os.path.getmtime(path)
    return _load_bib_cached(path, ext, _mtime=mtime)
```

---

### B3. ~~HAUTE~~ FAIT — Coloration syntaxique Pygments non cachée

**Fichier** : `streamtex/code.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | CPU par bloc de code, par re-render |
| **Statut** | **FAIT** |

**Implémentation** : `@_cache_code` (alias de `@st.cache_data(show_spinner=False)`) sur `_highlight_code()`. Le highlighting Pygments est exécuté une seule fois par combinaison (code, language, line_numbers, font_size).

```python
@_cache_code
def _highlight_code(code: str, language: str, line_numbers: bool,
                    font_size: str) -> str:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import TextLexer, get_lexer_by_name
    ...
```

---

### B4. ~~MOYENNE~~ FAIT — Google Sheets rechargé sans cache

**Fichier** : `streamtex/gsheet.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | Requête HTTP par re-render (latence réseau 100-500ms) |
| **Statut** | **FAIT** |

**Implémentation** : `@st.cache_data(ttl=_DEFAULT_CACHE_TTL, show_spinner=False)` sur `_fetch_public_csv_cached()`. Le TTL par défaut est 300 secondes, défini dans la constante `_DEFAULT_CACHE_TTL`.

```python
_DEFAULT_CACHE_TTL = 300

@st.cache_data(ttl=_DEFAULT_CACHE_TTL, show_spinner=False)
def _fetch_public_csv_cached(url: str, headers: bool) -> List[Dict[str, Any]]:
    import requests
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return _parse_csv_text(resp.text, headers)
```

---

## 6. Catégorie C — E/S fichiers et réseau

### C1. ~~BASSE~~ FAIT — `default.css` relu à chaque re-render

**Fichier** : `streamtex/book.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | Faible (cache Python implicite) |
| **Statut** | **FAIT** |

**Implémentation** : `@st.cache_resource` sur `_read_css()`. Le contenu CSS est lu une seule fois et gardé en mémoire.

```python
@st.cache_resource
def _read_css(file_name: str) -> str:
    with resources.open_text('streamtex.static', file_name) as f:
        return f.read()

def load_css(file_name: str):
    st.html(f'<style>{_read_css(file_name)}</style>')
```

---

### C2. INFO — Résolution des chemins statiques avec I/O

**Fichier** : `streamtex/image.py`

| Aspect | Détail |
|--------|--------|
| **Impact** | `2 x len(static_sources)` appels `stat()` par image, par re-render |
| **Statut** | **Résolu indirectement par B1** |

**Explication** : Une fois `_get_base64_encoded_image` cachée, la résolution de chemin complète (y compris les appels `os.path.isfile()`) n'est exécutée qu'une seule fois par image grâce au cache.

---

### C3. INFO — Inspector fait du parsing AST + walk disque

**Fichier** : `streamtex/inspector.py` (fonction `discover_sources`)

| Aspect | Détail |
|--------|--------|
| **Impact** | Significatif mais **partiellement atténué** |
| **Atténuation existante** | `_get_cached_project_files()` cache déjà les résultats dans `st.session_state` par racine de projet |

Le module inspector parse l'AST Python et parcourt le disque, mais :
1. C'est **opt-in** — seulement quand l'inspector est ouvert en mode développement
2. Le scan de fichiers projet est **déjà caché** dans `st.session_state`
3. Seule la découverte de sources au niveau bloc est non cachée

**Correction** : Pas de correction immédiate nécessaire. Le cache `session_state` existant couvre le cas d'usage principal.

---

## 7. Tableau récapitulatif

### Par priorité d'impact (optimisations librairie uniquement)

| # | Sévérité initiale | Catégorie | Problème | Statut | Implémentation |
|---|----------|-----------|----------|--------|----------------|
| **A1** | CRITIQUE | Import | `pandas` eager import | **FAIT** | `TYPE_CHECKING` + lazy import dans fonctions |
| **B1** | CRITIQUE | Rendu | Images base64 non cachées | **FAIT** | `@st.cache_data` + `_mtime` |
| **A2** | HAUTE | Import | `requests`+`bs4` chaîne transitive | **FAIT** | Imports déplacés dans `_get_page_preview()` |
| **B2** | HAUTE | Rendu | Bibliographie re-parsée | **FAIT** | `@_cache_bib` + `_mtime` dans `_load_bib_cached()` |
| **B3** | HAUTE | Rendu | Pygments non caché | **FAIT** | `@_cache_code` sur `_highlight_code()` |
| **B4** | MOYENNE | Rendu | Google Sheets sans cache | **FAIT** | `@st.cache_data(ttl=300)` sur `_fetch_public_csv_cached()` |
| **A3** | MOYENNE | Import | `requests` dans gsheet.py | **FAIT** | Lazy import dans `_fetch_public_csv_cached()` |
| **C1** | BASSE | I/O | CSS relu du disque | **FAIT** | `@st.cache_resource` sur `_read_css()` |

### Éléments classés en recherche future (section 9)

| # | Catégorie | Problème | Gain potentiel | Pourquoi "recherche" |
|---|-----------|----------|----------------|---------------------|
| **D1** | DOM | 2 `st.html()` par conteneur | -50% appels `st.html()` sur conteneurs | Correction proposée architecturalement incorrecte — nécessite prototypage |
| **D2** | DOM | ~300 lignes JS marker ré-injectées | -1 iframe lourd par re-render | Risque fonctionnel sur navigation clavier |
| **D3** | DOM | Nav paginée (JS + N boutons) | -N boutons serveur | Risque fonctionnel sur navigation |
| **D4** | DOM | UUID cryptographique pour CSS | ~23 appels système/page | Gain négligeable, risque de collision CSS |
| **A4** | Import | Lazy modules via `__getattr__` | -50-100ms cold start | Complexité élevée, risque de régressions |

---

## 8. Plan d'action — Bilan d'exécution

### Sprint 1 — Lazy imports, zéro risque — TERMINÉ

**Objectif** : Réduire le temps de cold start de 300-600ms.

| # | Action | Fichier | Statut |
|---|--------|---------|--------|
| A1 | Lazy import `pandas` | `export_widgets.py` | **FAIT** |
| A2 | Lazy import `requests`+`bs4` | `link_preview.py` | **FAIT** |
| A3 | Lazy import `requests` | `gsheet.py` | **FAIT** |

---

### Sprint 2 — Cache re-render, zéro risque — TERMINÉ

**Objectif** : Éliminer les recalculs redondants à chaque interaction utilisateur.

| # | Action | Fichier(s) | Statut |
|---|--------|-----------|--------|
| B1 | `@st.cache_data` sur base64 images | `image_utils.py`, `image.py` | **FAIT** |
| B2 | Cache parsing bibliographie | `bib.py` | **FAIT** |
| B3 | `@st.cache_data` Pygments | `code.py` | **FAIT** |

---

### Sprint 3 — Cache I/O et réseau — TERMINÉ

**Objectif** : Éliminer les requêtes réseau et lectures fichier redondantes.

| # | Action | Fichier(s) | Statut |
|---|--------|-----------|--------|
| B4 | Implémenter cache TTL GSheet | `gsheet.py` | **FAIT** |
| C1 | `@st.cache_resource` sur CSS | `book.py` | **FAIT** |

---

### Validation finale

```bash
# 766 tests passent (2026-02-25)
uv run pytest tests/ -v

# Lint propre (2026-02-25)
uv run ruff check streamtex/
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
- Grille 3x3 = 2 (grille) + 9 x 2 (cellules) = **20 `st.html()`**
- Liste 5 items = 4 (liste) + 5 x 4 (items) = **24 `st.html()`**
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

1. **Déplacer le `<style>` à l'intérieur du container** — Tester si un `<style>` injecté via `st.html()` à l'intérieur d'un `st.container()` peut styler le container parent. Cela dépend du comportement du Shadow DOM de Streamlit (version >=1.54). Si ça fonctionne, on peut fusionner CSS et marker en 1 seul `st.html()` à l'intérieur.

2. **Batch CSS injection** — Collecter tous les `<style>` d'une page et les injecter en un seul `st.html()` au début, puis n'émettre que les markers (1 `st.html()` par conteneur au lieu de 2). Cela nécessite un mécanisme de collecte en deux passes.

3. **CSS global avec classes prédéfinies** — Au lieu de générer des sélecteurs `:has()` uniques par conteneur, utiliser des classes CSS prédéfinies et les appliquer directement au markup Streamlit. Cela nécessite de comprendre comment Streamlit gère les attributs de classes sur les containers natifs.

**Prochaine étape** : Créer un prototype minimal testant la piste 1 sur Streamlit 1.54+ et mesurer si le Shadow DOM permet la remontée CSS.

---

### D2. Navigation marker : ~300 lignes de JS ré-injectées

**Fichier** : `streamtex/marker.py:183-499`

La navigation par marqueurs injecte ~300 lignes de JavaScript via `components.html()` (iframe) à chaque re-render. 9 remplacements `.replace()` de chaînes sont effectués pour injecter les données dynamiques dans le JS statique.

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | Éliminer la ré-injection du JS scaffold à chaque re-render |
| **Risque fonctionnel** | **Élevé** — la navigation clavier PageUp/PageDown est fondamentale |
| **Complexité** | Élevée — séparer JS statique vs données dynamiques |

**Piste** : Séparer le JS en 2 parties : un scaffold statique (injecté une seule fois via `st.session_state`) et les données dynamiques (markers, config) injectées à chaque render. Le scaffold écouterait un événement custom pour recevoir les nouvelles données.

---

### D3. Navigation paginée : ~268 lignes JS + N boutons cachés

**Fichier** : `streamtex/book.py`

En mode paginé, chaque re-render crée **N boutons Streamlit cachés** (1 par page) et injecte ~268 lignes de JS via `components.html()`.

| Aspect | Détail |
|--------|--------|
| **Gain potentiel** | Réduire N boutons à une fenêtre de +-5 pages |
| **Risque fonctionnel** | **Moyen** — la navigation par numéro de page pourrait être impactée |
| **Complexité** | Moyenne |

**Piste** : Limiter les boutons cachés à une fenêtre autour de la page courante (ex: pages [current-5, current+5]) et recréer la fenêtre dynamiquement à chaque changement de page.

---

### D4. UUID cryptographique pour noms CSS

**Fichier** : `streamtex/utils.py`

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

**Décision** : Reporter. Si le cold start reste problématique après A1/A2/A3 (maintenant implémentés), envisager cette optimisation avec un prototype isolé.

---

## 10. Bonnes pratiques déjà en place

L'analyse a aussi révélé des choix de conception **bien faits** qu'il faut préserver :

| Composant | Bonne pratique |
|-----------|---------------|
| **Pygments** | Import lazy dans `_highlight_code()` + `@_cache_code` |
| **Mermaid** | `mermaid-py` importé lazy seulement pendant l'export |
| **Google API libs** | `google-auth`, `googleapiclient` importés lazy dans les fonctions backend |
| **matplotlib** | Import lazy dans `_chart_to_svg()` |
| **pandas** | Import lazy dans les fonctions + `TYPE_CHECKING` pour annotations |
| **requests** | Import lazy dans `_get_page_preview()` et `_fetch_public_csv_cached()` |
| **beautifulsoup4** | Import lazy dans `_get_page_preview()` |
| **Inspector** | Import lazy dans `st_book()` seulement quand activé |
| **Inspector files** | Cache `session_state` sur le scan de fichiers projet |
| **PlantUML SVG** | `@st.cache_data(show_spinner=False)` sur le fetch HTTP |
| **TikZ compilation** | `@st.cache_data(show_spinner=False)` sur le subprocess LaTeX |
| **Images base64** | `@st.cache_data(show_spinner=False)` + `_mtime` pour invalidation |
| **Bibliographie** | `@_cache_bib` + `_mtime` sur `_load_bib_cached()` |
| **Google Sheets** | `@st.cache_data(ttl=300)` sur `_fetch_public_csv_cached()` |
| **CSS** | `@st.cache_resource` sur `_read_css()` |
| **Block registries** | Cache dict manuel qui persiste entre re-runs |
| **Mode paginé** | Ne rend qu'un seul bloc par re-render (après cache warmup) |
| **Styles de base** | Attributs de classe = singletons créés une seule fois |
| **String building** | `"".join(parts)` dans write.py (pas de concaténation répétée) |
| **Couleurs dark mode** | CSS custom properties centralisées (`--stx-link-color`, `--stx-link-active-color`) + constantes Python dans `constants.py` |
