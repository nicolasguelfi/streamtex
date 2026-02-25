# Plan de Maintenance : Performance de la Librairie StreamTeX

> **Date** : 2026-02-25
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 1.0
> **Statut** : Analyse complète, prêt pour priorisation

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Métriques actuelles](#2-métriques-actuelles)
3. [Catégorie A — Import initial (démarrage à froid)](#3-catégorie-a--import-initial-démarrage-à-froid)
4. [Catégorie B — Rendu par re-run (chemin chaud)](#4-catégorie-b--rendu-par-re-run-chemin-chaud)
5. [Catégorie C — E/S fichiers et réseau](#5-catégorie-c--es-fichiers-et-réseau)
6. [Catégorie D — Injection CSS/JS (overhead DOM)](#6-catégorie-d--injection-cssjs-overhead-dom)
7. [Tableau récapitulatif](#7-tableau-récapitulatif)
8. [Plan d'action recommandé](#8-plan-daction-recommandé)
9. [Bonnes pratiques déjà en place](#9-bonnes-pratiques-déjà-en-place)

---

## 1. Résumé exécutif

### Le problème

Le chargement d'une page avec ~10 blocs est perçu comme lent. L'analyse en profondeur révèle **4 familles de causes** qui se cumulent :

| Catégorie | Impact estimé | Nb de problèmes |
|-----------|--------------|-----------------|
| **A. Import initial** (cold start) | 300-700ms gaspillés | 4 problèmes |
| **B. Rendu par re-run** (chemin chaud) | Accumulation sur chaque interaction | 5 problèmes |
| **C. E/S fichiers et réseau** | I/O disque/réseau à chaque re-render | 5 problèmes |
| **D. Injection CSS/JS** (overhead DOM) | ~72 `st.html()` par page typique | 3 problèmes |

### Architecture Streamlit : le contexte fondamental

Streamlit **ré-exécute l'intégralité du script Python** à chaque interaction utilisateur (clic, changement de widget, navigation). Ce n'est pas un bug — c'est l'architecture de Streamlit. Cela signifie que **tout ce qui n'est pas caché est recalculé à chaque interaction**.

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
│   ├─ setup_bibliography  ← E/S fichier (Cat. C)         │
│   ├─ inject scaffolds    ← Injection JS (Cat. D)        │
│   ├─ Pour chaque bloc :                                  │
│   │   ├─ block.build()                                   │
│   │   │   ├─ st_write()   ← st.html() (Cat. D)         │
│   │   │   ├─ st_grid()    ← N×st.html() (Cat. D)       │
│   │   │   ├─ st_image()   ← base64 re-encode (Cat. C)  │
│   │   │   └─ st_list()    ← N×st.html() (Cat. D)       │
│   │   └─ st_space()       ← st.html() (Cat. D)         │
│   └─ marker navigation    ← 480 lignes JS (Cat. D)      │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Métriques actuelles

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
| Navigation markers | 0 | 1 (480 lignes JS) | 0 | 0 |
| **TOTAL** | **~72** | **1** | **~23** | **4** |

> Chaque `st.html()` crée un Shadow DOM element. 72 Shadow DOM elements par page est significatif.

### Mode paginé vs continu

| Métrique | Mode continu | Mode paginé |
|----------|-------------|-------------|
| Blocs rendus par re-run | Tous (N) | 1 seul |
| `st.html()` par re-run | ~72 × (N/10) | ~72 |
| Coût première visite | Normal | Double (cache warmup) |
| Boutons cachés | 0 | N (1 par page) |
| JS injecté | ~480 lignes | ~755 lignes |

---

## 3. Catégorie A — Import initial (démarrage à froid)

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
| **Fonctionnalités touchées** | Aucune — correction transparente |

**Correction** : Déplacer l'import à l'intérieur des fonctions qui l'utilisent (`st_dataframe`, `st_table`, `_to_dataframe`, `_chart_to_svg`).

```python
# AVANT (module level)
import pandas as pd

# APRÈS (lazy, dans chaque fonction)
def st_dataframe(style, data, ...):
    import pandas as pd
    ...
```

---

### A2. HAUTE — `requests` + `beautifulsoup4` importés via chaîne transitive

**Fichier** : `streamtex/link_preview.py:5-7`

```python
import requests                         # +50-100ms
from bs4 import BeautifulSoup as bs     # +20-40ms
```

**Chaîne d'import** : `__init__.py` → `utils.py` → `link_preview.py` → `requests` + `bs4`

| Aspect | Détail |
|--------|--------|
| **Impact** | +70-140ms au démarrage |
| **Qui est affecté** | 100% des projets |
| **Fonctionnalités touchées** | Aucune — `_get_page_preview()` n'est jamais appelé par la librairie |

**Correction** : Déplacer les imports dans `_get_page_preview()` uniquement.

---

### A3. MOYENNE — `requests` importé dans `gsheet.py`

**Fichier** : `streamtex/gsheet.py:29`

```python
import requests  # Redondant avec A2, mais problématique si A2 est corrigé
```

| Aspect | Détail |
|--------|--------|
| **Impact** | Nul actuellement (déjà chargé par A2), mais +50-100ms si A2 est corrigé |
| **Fonctionnalités touchées** | Aucune si corrigé en lazy |

**Correction** : Déplacer dans les fonctions `_load_public_csv()` et `load_gsheet()`.

---

### A4. BASSE — Tous les modules importés eagerly par `__init__.py`

**Fichier** : `streamtex/__init__.py`

Le fichier `__init__.py` importe **tous les modules** au chargement : mermaid, plantuml, tikz, bib, gsheet, inspector, collection... même si un projet n'en utilise aucun.

| Aspect | Détail |
|--------|--------|
| **Impact** | +50-100ms (modules légers, mais cumulatif) |
| **Complexité de correction** | Élevée (pattern `__getattr__` pour lazy module loading) |
| **Fonctionnalités touchées** | Aucune si bien implémenté |

**Correction (future)** : Implémenter le pattern `__getattr__` dans `__init__.py` pour un chargement paresseux des modules non-core. C'est une optimisation avancée à faire en Phase 2.

```python
# Pattern __getattr__ pour lazy loading
_LAZY_MODULES = {
    'st_mermaid': '.mermaid',
    'st_plantuml': '.plantuml',
    'st_tikz': '.tikz',
    'st_bibliography': '.bib',
    'load_gsheet': '.gsheet',
    # ...
}

def __getattr__(name):
    if name in _LAZY_MODULES:
        import importlib
        module = importlib.import_module(_LAZY_MODULES[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module 'streamtex' has no attribute {name}")
```

---

## 4. Catégorie B — Rendu par re-run (chemin chaud)

Ces problèmes affectent **chaque interaction utilisateur** (chaque re-run Streamlit).

### B1. CRITIQUE — Images base64 ré-encodées à chaque re-render

**Fichier** : `streamtex/image.py:98-99` → `streamtex/image_utils.py:42-49`

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
| **Fonctionnalités touchées** | Aucune — le cache est transparent |

**Correction** : Ajouter `@st.cache_data` basé sur le chemin et le mtime du fichier.

```python
@st.cache_data(show_spinner=False)
def _get_base64_encoded_image(file_path: str, _mtime: float = None):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Appel avec mtime pour invalidation automatique
mtime = os.path.getmtime(file_path)
encoded = _get_base64_encoded_image(file_path, _mtime=mtime)
```

---

### B2. HAUTE — Bibliographie re-parsée à chaque re-render

**Fichier** : `streamtex/book.py` (fonction `_setup_bibliography`)

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
| **Fonctionnalités touchées** | Aucune — le cache est transparent |

**Correction** : Cacher le parsing avec `@st.cache_data` clé = (chemin, mtime).

---

### B3. HAUTE — Coloration syntaxique Pygments non cachée

**Fichier** : `streamtex/code.py`

`st_code()` re-highlight le même code à chaque re-render. Aucun `@st.cache_data`.

| Aspect | Détail |
|--------|--------|
| **Impact** | CPU par bloc de code, par re-render |
| **Exemple** | 5 blocs de code × highlighting Pygments = 5× le même travail |
| **Fonctionnalités touchées** | Aucune |

**Correction** : `@st.cache_data` sur la fonction de highlighting, clé = (code, language, line_numbers).

---

### B4. MOYENNE — Composition de styles dans `build()`

**Fichier** : `streamtex/styles/core.py:62-71`

```python
# Si écrit dans build() — recréé à CHAQUE re-render
my_style = s.bold + s.red + s.large  # Crée 2 objets Style intermédiaires
```

| Aspect | Détail |
|--------|--------|
| **Impact** | Création d'objets Python (faible unitairement, cumulatif) |
| **Fonctionnalités touchées** | Aucune |

**Correction** : Documenter la bonne pratique — définir les styles composés dans `BlockStyles` (au niveau classe), pas dans `build()`. Les styles au niveau classe sont créés une seule fois.

```python
# BON — créé une seule fois au chargement du module
class BlockStyles:
    my_style = s.bold + s.red + s.large

# MAUVAIS — recréé à chaque re-render
def build():
    my_style = s.bold + s.red + s.large  # ← à éviter
```

---

### B5. MOYENNE — Google Sheets rechargé sans cache

**Fichier** : `streamtex/gsheet.py`

Le champ `GSheetConfig.cache_ttl: Optional[int] = 300` existe dans la config mais **n'est jamais implémenté**. Chaque re-render refait la requête HTTP.

| Aspect | Détail |
|--------|--------|
| **Impact** | Requête HTTP par re-render (latence réseau) |
| **Fonctionnalités touchées** | Aucune — le cache est transparent |

**Correction** : Implémenter `@st.cache_data(ttl=config.cache_ttl)` sur `_load_public_csv` et les fonctions API.

---

## 5. Catégorie C — E/S fichiers et réseau

### C1. MOYENNE — `default.css` relu du disque à chaque re-render

**Fichier** : `streamtex/book.py:255-267`

```python
def load_css(file_name: str):
    with resources.open_text('streamtex.static', file_name) as f:
        st.html(f'<style>{f.read()}</style>')
```

| Aspect | Détail |
|--------|--------|
| **Impact** | 1 lecture fichier par re-render |
| **Fonctionnalités touchées** | Aucune |

**Correction** : `@st.cache_resource` ou variable module-level.

```python
@st.cache_resource
def _read_css(file_name: str) -> str:
    with resources.open_text('streamtex.static', file_name) as f:
        return f.read()

def load_css(file_name: str):
    st.html(f'<style>{_read_css(file_name)}</style>')
```

---

### C2. BASSE — Images de couverture collection ré-encodées

**Fichier** : `streamtex/collection.py` (fonction `_render_project_card`)

Les images de couverture des projets dans le hub collection sont base64-encodées à chaque re-render.

| Aspect | Détail |
|--------|--------|
| **Impact** | Proportionnel au nombre de projets avec couverture |
| **Fonctionnalités touchées** | Aucune |

**Correction** : Même solution que B1 — `@st.cache_data` sur l'encodage base64.

---

### C3. BASSE — Fichier TOML collection re-parsé

**Fichier** : `streamtex/collection.py` (fonction `CollectionConfig.from_toml`)

Le fichier `collection.toml` (~1KB) est re-parsé à chaque re-render.

| Aspect | Détail |
|--------|--------|
| **Impact** | Négligeable (fichier très petit) |
| **Fonctionnalités touchées** | Aucune |

**Correction** : `@st.cache_resource` (optionnel, gain minimal).

---

### C4. BASSE — Résolution des chemins statiques avec I/O

**Fichier** : `streamtex/image.py:108-124`

Pour chaque image non-URL, la fonction itère `static_sources` et teste 2 sous-dossiers par source via `os.path.isfile()`.

| Aspect | Détail |
|--------|--------|
| **Impact** | `2 × len(static_sources)` appels stat() par image, par re-render |
| **Fonctionnalités touchées** | Aucune |

**Correction** : Cacher la résolution de chemin (même solution que B1).

---

### C5. INFO — Inspector fait du parsing AST + walk disque

**Fichier** : `streamtex/inspector.py` (fonction `discover_sources`)

Le module inspector parse l'AST Python et parcourt le disque à chaque render. Mais c'est opt-in (seulement quand l'inspector est ouvert).

| Aspect | Détail |
|--------|--------|
| **Impact** | Significatif mais seulement en mode développement |
| **Fonctionnalités touchées** | Aucune |

**Correction** : Cacher dans `st.session_state` clé = nom du module.

---

## 6. Catégorie D — Injection CSS/JS (overhead DOM)

### D1. HAUTE — Chaque conteneur émet 2 `st.html()`

**Fichiers** : `streamtex/container.py`, `streamtex/grid.py`, `streamtex/list.py`

Chaque appel à `st_block()`, `st_span()`, chaque cellule de grille et chaque item de liste émet :
1. Un `st.html(css)` pour le `<style>` avec un UUID unique
2. Un `st.html(marker)` pour le `<span>` de marquage

| Composant | `st.html()` par instance |
|-----------|-------------------------|
| `st_block()` | 2 |
| `st_span()` | 2 |
| Cellule `st_grid()` | 2 (via `st_block`) |
| `st_grid()` elle-même | 2 |
| Item `st_list()` | 4 (2 propres + 2 via `st_block`) |
| `st_list()` elle-même | 4 (2 propres + 2 via `st_block`) |

**Exemple** : une grille 3×3 = 2 (grille) + 9×2 (cellules) = **20 `st.html()`**

| Aspect | Détail |
|--------|--------|
| **Impact** | Dominant — représente la majorité des appels `st.html()` |
| **Complexité de correction** | Moyenne — fusionner CSS + marker en un seul `st.html()` |
| **Fonctionnalités touchées** | Aucune — optimisation interne |

**Correction** : Fusionner le `<style>` et le `<span>` marker en un seul appel `st.html()`.

```python
# AVANT (2 appels)
st.html(css)
# ... st.container() ...
st.html(f'<span class="{block_id}">')

# APRÈS (1 appel)
st.html(f'{css}<span class="{block_id}">')
```

**Gain estimé** : Réduction de ~50% des appels `st.html()` pour les conteneurs.

---

### D2. HAUTE — Navigation marker : 480 lignes de JS ré-injectées

**Fichier** : `streamtex/marker.py:160-499`

La navigation par marqueurs injecte ~480 lignes de JavaScript via `components.html()` (iframe lourd) à chaque re-render. 8 remplacements `.replace()` de chaînes sont effectués sur ce JS.

| Aspect | Détail |
|--------|--------|
| **Impact** | 1 iframe lourd par re-render |
| **Complexité de correction** | Élevée (architecture JS fondamentale) |
| **Fonctionnalités touchées** | Navigation clavier PageUp/PageDown |

**Correction possible** : Séparer le JS statique (scaffold) du JS dynamique (données). Cacher le scaffold, ne réinjecter que les données via `st.session_state`.

---

### D3. MOYENNE — Navigation paginée : ~275 lignes JS + N boutons cachés

**Fichier** : `streamtex/book.py:571-857, 996-999`

En mode paginé, chaque re-render :
- Crée N boutons Streamlit cachés (1 par page)
- Injecte ~275 lignes de JS via `components.html()`
- Plus le JS des markers (D2)
- Total : **~755 lignes de JS** dans des iframes

| Aspect | Détail |
|--------|--------|
| **Impact** | Proportionnel au nombre de pages |
| **Fonctionnalités touchées** | Navigation paginée |

**Correction** : Limiter les boutons cachés à une fenêtre (ex: ±5 pages autour de la page courante).

---

### D4. BASSE — UUID cryptographique pour noms CSS

**Fichier** : `streamtex/utils.py:31-33`

```python
def generate_key(prefix: str = "block"):
    return f"{prefix}-{uuid.uuid4().hex}"
```

`uuid.uuid4()` utilise `/dev/urandom` (appel système). Pour des noms de classes CSS, un compteur simple suffirait.

| Aspect | Détail |
|--------|--------|
| **Impact** | ~23 appels système par page typique (faible) |
| **Fonctionnalités touchées** | Aucune |

**Correction** : Remplacer par un compteur atomique.

```python
_counter = 0
def generate_key(prefix: str = "block"):
    global _counter
    _counter += 1
    return f"{prefix}-{_counter}"
```

---

## 7. Tableau récapitulatif

### Par priorité d'impact

| # | Sévérité | Catégorie | Problème | Impact estimé | Complexité fix | Risque fonctionnel |
|---|----------|-----------|----------|---------------|---------------|-------------------|
| **A1** | CRITIQUE | Import | `pandas` eager import | +200-400ms cold start | Faible | Aucun |
| **B1** | CRITIQUE | Rendu | Images base64 non cachées | I/O × N images × re-render | Faible | Aucun |
| **A2** | HAUTE | Import | `requests`+`bs4` via chaîne transitive | +70-140ms cold start | Faible | Aucun |
| **B2** | HAUTE | Rendu | Bibliographie re-parsée | I/O fichier × re-render | Faible | Aucun |
| **B3** | HAUTE | Rendu | Pygments non caché | CPU × blocs code × re-render | Faible | Aucun |
| **D1** | HAUTE | DOM | 2 `st.html()` par conteneur | ~50% des appels st.html | Moyenne | Aucun |
| **D2** | HAUTE | DOM | 480 lignes JS marker re-injectées | 1 iframe lourd × re-render | Élevée | Navigation |
| **B5** | MOYENNE | Rendu | Google Sheets sans cache | Requête HTTP × re-render | Faible | Aucun |
| **C1** | MOYENNE | I/O | CSS relu du disque | 1 lecture fichier × re-render | Faible | Aucun |
| **A3** | MOYENNE | Import | `requests` dans gsheet.py | +50-100ms si A2 corrigé | Faible | Aucun |
| **B4** | MOYENNE | Rendu | Styles composés dans build() | Objets Python × re-render | Aucune (doc) | Aucun |
| **D3** | MOYENNE | DOM | Nav paginée (JS + N boutons) | Proportionnel aux pages | Moyenne | Navigation |
| **A4** | BASSE | Import | Tous modules eager dans __init__ | +50-100ms cold start | Élevée | Risque régressions |
| **C2** | BASSE | I/O | Cover images collection | I/O × projets × re-render | Faible | Aucun |
| **D4** | BASSE | DOM | UUID cryptographique | ~23 appels système/page | Faible | Aucun |

### Par fonctionnalité impactée en cas de correction

| Fonctionnalité | Corrections sans risque | Corrections avec risque |
|---------------|------------------------|------------------------|
| **Rendu de base** (st_write, st_block) | D1, D4 | — |
| **Images** | B1, C2, C4 | — |
| **Grilles** | D1 | — |
| **Listes** | D1 | — |
| **Navigation** | — | D2, D3 |
| **Bibliographie** | B2 | — |
| **Code** | B3 | — |
| **Google Sheets** | B5 | — |
| **Import/démarrage** | A1, A2, A3 | A4 |
| **Documentation/bonnes pratiques** | B4 | — |

---

## 8. Plan d'action recommandé

### Sprint 1 — Gains rapides, zéro risque (estimé : 1-2 sessions)

Ces corrections sont **transparentes** — aucun changement d'API, aucun risque fonctionnel.

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| A1 | Lazy import `pandas` | `export_widgets.py` | -200-400ms cold start |
| A2 | Lazy import `requests`+`bs4` | `link_preview.py` | -70-140ms cold start |
| A3 | Lazy import `requests` | `gsheet.py` | -50-100ms cold start |
| B1 | `@st.cache_data` sur base64 images | `image.py`, `image_utils.py` | -I/O majeur par re-render |
| C1 | `@st.cache_resource` sur CSS | `book.py` | -1 lecture fichier/re-render |

**Gain Sprint 1** : ~300-600ms sur le cold start + élimination des I/O images redondants.

### Sprint 2 — Gains significatifs, faible risque (estimé : 1-2 sessions)

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| B2 | Cache parsing bibliographie | `bib.py`, `book.py` | -I/O fichier par re-render |
| B3 | `@st.cache_data` Pygments | `code.py` | -CPU par bloc code |
| B5 | Implémenter `cache_ttl` GSheet | `gsheet.py` | -requête HTTP/re-render |
| D1 | Fusionner CSS+marker en 1 `st.html()` | `container.py` | -50% appels st.html conteneurs |
| D4 | Compteur simple au lieu de UUID | `utils.py` | -appels système |

**Gain Sprint 2** : Réduction significative du coût par re-render.

### Sprint 3 — Optimisations structurelles (estimé : 2-3 sessions)

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| D1+ | Fusionner CSS+marker dans grid/list | `grid.py`, `list.py` | -50% appels st.html grilles/listes |
| D2 | Séparer JS statique/dynamique markers | `marker.py` | -overhead iframe |
| D3 | Limiter boutons cachés (fenêtre) | `book.py` | -N boutons serveur |
| B4 | Documenter bonnes pratiques styles | `coding_standards.md` | Prévention |

### Sprint 4 — Optimisation avancée (future, après multi-repo)

| # | Action | Fichier(s) | Gain estimé |
|---|--------|-----------|-------------|
| A4 | Lazy module loading via `__getattr__` | `__init__.py` | -50-100ms cold start |

---

## 9. Bonnes pratiques déjà en place

L'analyse a aussi révélé des choix de conception **bien faits** qu'il faut préserver :

| Composant | Bonne pratique |
|-----------|---------------|
| **Pygments** | Import lazy dans `st_code()` (try/except, pas module-level) |
| **Mermaid** | `mermaid-py` importé lazy seulement pendant l'export |
| **Google API libs** | `google-auth`, `googleapiclient` importés lazy dans les fonctions backend |
| **matplotlib** | Import lazy dans `_chart_to_svg()` |
| **Inspector** | Import lazy dans `st_book()` seulement quand activé |
| **PlantUML SVG** | `@st.cache_data(show_spinner=False)` sur le fetch HTTP |
| **TikZ compilation** | `@st.cache_data(show_spinner=False)` sur le subprocess LaTeX |
| **Block registries** | Cache dict manuel qui persiste entre re-runs |
| **Mode paginé** | Ne rend qu'un seul bloc par re-render (après cache warmup) |
| **Styles de base** | Attributs de classe = singletons créés une seule fois |
| **String building** | `"".join(parts)` dans write.py (pas de concaténation répétée) |
