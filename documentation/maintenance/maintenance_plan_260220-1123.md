# Plan de Maintenance StreamTeX — 2026-02-20 11:23

> **Ce document est self-contained.** Il contient tous les chemins, numéros de ligne,
> extraits de code et instructions nécessaires pour exécuter chaque tâche sans contexte
> supplémentaire. Il a été produit après une inspection approfondie complète du projet.

---

## ÉTAT D'AVANCEMENT — Dernière mise à jour : 2026-02-20

> **Exécution arrêtée après E1** (sur instruction utilisateur).
> Phases A, B, C, D, E1 terminées. Phases E2→E7 et F1→F4 restent à faire.

| Phase | Statut | Tests avant | Tests après |
|-------|--------|-------------|-------------|
| **A** (A1-A7) | ✅ TERMINÉE | 203 | 203 |
| **B** (B1-B8) | ✅ TERMINÉE | 203 | 206 |
| **C** (C1-C6) | ✅ TERMINÉE | 206 | 206 |
| **D** (D1-D8) | ✅ TERMINÉE | 206 | 466 |
| **E1** | ✅ TERMINÉE | 466 | 466 |
| **E2-E7** | ⬜ À FAIRE | — | — |
| **F1-F4** | ⬜ À FAIRE | — | — |

### Notes importantes post-exécution

1. **B4 (ancres TOC)** — L'implémentation initiale proposée dans le plan (`re.sub(r'[^\w\s-]', '', ...)`)
   supprimait les `.` au lieu de les remplacer par `-`, ce qui cassait le test existant
   `test_key_anchor_format` (attendait `"1-2-my-title"`, obtenait `"12-my-title"`).
   **Correction appliquée** : les `.` et caractères de ponctuation courants sont remplacés
   par `-` (pas supprimés), puis les `-` multiples sont collapsés. Le regex final est :
   ```python
   slug = re.sub(r'[.\'"!?@#$%^&*()+=\[\]{}|\\/<>,;:~`]', '-', title.lower())
   slug = re.sub(r'[-\s]+', '-', slug).strip('-')
   ```

2. **B6 (MIME étendu)** — Le test `test_unsupported` existant utilisait `"file.bmp"` comme
   cas non-supporté. Avec `mimetypes.guess_type()`, BMP est maintenant supporté.
   **Correction appliquée** : test mis à jour pour utiliser `"file.xyz"` comme cas non-supporté,
   et 3 nouveaux tests ajoutés (`test_bmp`, `test_svg`, `test_webp`).

3. **C2 (gap parameter)** — Le paramètre `gap` explicite est injecté dans le CSS généré.
   Si `grid_style` contient aussi un `gap` en CSS, le `gap` du CSS de `grid_style` sera
   écrasé par le `gap` explicite car ce dernier est dans le sélecteur plus spécifique
   du grid container. **Documenter ce comportement** dans coding_standards.md si nécessaire.

4. **C3 (st_br count)** — L'ancien `st_br()` appelait `st_space("v", 0)` qui générait
   `padding-top: 0` (invisible). Le nouveau génère de vrais `<br>` tags. C'est un
   **changement de comportement** mais strictement bénéfique (l'ancien ne faisait rien).

5. **D (tests)** — 260 nouveaux tests ajoutés (206→466). Les tests D1-D8 utilisent
   `unittest.mock.patch` pour mocker Streamlit et le module export. Certains tests
   documentent des comportements actuels qui pourraient changer :
   - `test_list.py` documente le `ZeroDivisionError` quand `ListStyle.symbols=[]`
     (sera corrigé par E3)
   - `test_book_integration.py` documente que `st_include(None)` lève `AttributeError`
     (accès à `None.__path__`)

6. **E1 (constants.py)** — L'import dans `zoom.py` est fait à l'intérieur de la fonction
   `inject_zoom_logic()` (pas au top-level) car les constantes étaient des variables
   locales. L'import dans `export.py` est au top-level car il sert de default dans
   la dataclass `ExportConfig`. Les constantes ne sont **pas exportées** dans
   `__init__.py` — elles sont internes à la librairie.

### Prochaine étape recommandée

Reprendre à **E2** (normaliser `add_css()`). C'est la tâche la plus délicate des phases
restantes car elle affecte **toute la composition de styles**. Recommandation :
- Lancer les 3 projets tests visuellement AVANT E2 pour avoir une référence
- Appliquer E2
- Relancer les 466 tests + vérification visuelle des 3 projets

---

## Contexte du projet

- **Version** : 0.2.0 | Python >=3.10 | Streamlit >=1.54.0
- **Tests** : 466 tests unitaires (tous passent au 2026-02-20, après exécution A1→E1)
- **Structure** : librairie `streamtex/` + 3 projets tests + 2 templates + shared-blocks
- **Environnement** : uv uniquement (`uv run pytest`, `uv run streamlit run ...`)
- **Racine projet** : `/Volumes/Mac_Data/.../github/streamtex/`

## Philosophie du plan

Le plan est ordonné du **moins risqué au plus risqué** :

1. **Phase A** — Documentation & fichiers projet (zéro risque de casser le code)
2. **Phase B** — Corrections isolées (un fichier, un fix, facilement réversible)
3. **Phase C** — Features additives (ajout de code, pas de modification de l'existant)
4. **Phase D** — Tests unitaires (ajout pur, renforce la confiance)
5. **Phase E** — Refactoring interne (modifications structurelles, risque modéré)
6. **Phase F** — Refactoring d'API publique (risque le plus élevé, nécessite migration)

**Règle impérative** : après chaque tâche, lancer `uv run pytest tests/ -v` et vérifier
que les 466+ tests passent. Si un test échoue, corriger avant de passer à la suite.

---

## Phase A — Documentation & fichiers projet

> **Risque : ZÉRO.** Aucun code Python de la librairie n'est modifié.

### A1. ✅ Corriger CLAUDE.md — supprimer la référence au dossier supprimé

**Fichier** : `CLAUDE.md`
**Ligne ~68** : contient `├── test_project/            # Original comprehensive test (legacy)`

**Action** : Supprimer cette ligne. Le dossier `tests/test_project/` a été supprimé
(commit `7dee28a`).

**Vérification** : `grep -n "test_project/" CLAUDE.md` ne doit plus rien retourner
(sauf `test_project_intro` et `test_project_advanced`).

---

### A2. ✅ Corriger le Dockerfile — mettre à jour le FOLDER par défaut

**Fichier** : `Dockerfile`
**Ligne 28** : `ARG FOLDER="tests/test_project"`

**Action** : Remplacer par :
```dockerfile
ARG FOLDER="tests/test_project_intro"
```

**Vérification** : `grep "ARG FOLDER" Dockerfile` retourne la nouvelle valeur.

---

### A3. ✅ Corriger template_project/book.py — auto_marker_on_toc

**Fichier** : `documentation/template_project/book.py`
**Ligne 27** : `auto_marker_on_toc=1,`

**Action** : Remplacer `1` par `True` :
```python
auto_marker_on_toc=True,
```

**Raison** : Le paramètre attend un booléen. `1` fonctionne en Python mais est
trompeur pour les débutants et incohérent avec les projets tests.

---

### A4. ✅ Implémenter les 3 blocs placeholder dans test_project_advanced

**Fichiers concernés** (tous dans `tests/test_project_advanced/blocks/`) :
- `bck_lazy_block_registry_demo.py` (26 lignes, contient "Content coming soon!")
- `bck_shared_blocks_usage.py` (26 lignes, contient "Content coming soon!")
- `bck_static_resolution_demo.py` (26 lignes, contient "Content coming soon!")

**Action** : Remplacer le contenu de chaque bloc par une documentation pédagogique
complète de la fonctionnalité correspondante, en suivant le pattern standard
(BlockStyles + build() + show_code/show_explanation/show_details).

**bck_lazy_block_registry_demo.py** doit montrer :
- Création d'un `LazyBlockRegistry([path1, path2])`
- Accès aux blocs via `registry.bck_name`
- Priorité des sources (premier chemin gagne)
- Comparaison avec `ProjectBlockRegistry`

**bck_shared_blocks_usage.py** doit montrer :
- Import de blocs partagés depuis `shared-blocks/`
- Utilisation dans `st_book([shared.bck_header, local.bck_content, shared.bck_footer])`
- Pattern d'organisation multi-projet

**bck_static_resolution_demo.py** doit montrer :
- `sx.set_static_sources([local_path, shared_path])`
- `sx.resolve_static("image.png")` — résolution par priorité
- Pattern de fallback entre sources statiques

**Import pattern attendu** :
```python
from streamtex import st_write, st_block, st_space, Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
```

---

### A5. ✅ Mettre à jour coding_standards.md

**Fichier** : `documentation/coding_standards.md` (204 lignes actuellement)

**Action** : Ajouter trois nouvelles sections à la fin :

**Section "10. Block Registry Patterns"** :
- Quand utiliser `ProjectBlockRegistry` (un seul projet, blocs locaux)
- Quand utiliser `LazyBlockRegistry` (multi-source, blocs partagés)
- Exemple complet de `blocks/__init__.py` avec `ProjectBlockRegistry`
- Exemple de `book.py` avec `LazyBlockRegistry` pour shared-blocks

**Section "11. Hybrid Helper Patterns"** :
- Mode 1 : Fonctions standalone (`from streamtex import show_code`)
- Mode 2 : Config Injection (`BlockHelperConfig` + `set_block_helper_config()`)
- Mode 3 : OOP Inheritance (`class ProjectBlockHelper(BlockHelper)`)
- Quand utiliser chaque mode (débutant → intermédiaire → avancé)

**Section "12. Multi-Source Block Resolution"** :
- `LazyBlockRegistry([path1, path2])` — priorité du premier chemin
- `set_static_sources([path1, path2])` — résolution statique
- Règles de priorité et résolution de conflits

---

### A6. ✅ Mettre à jour template_project/helpers.py

**Fichier** : `documentation/template_project/blocks/helpers.py` (8 lignes actuellement)

**Action** : Étendre pour montrer le pattern `BlockHelperConfig` :
```python
"""Block helpers — project-specific configuration."""
from pathlib import Path
from streamtex import (
    BlockHelperConfig, set_block_helper_config,
    show_code, show_explanation, show_details, show_code_inline,
)
from custom.styles import Styles as s


class ProjectBlockHelperConfig(BlockHelperConfig):
    """Override default styles with project-specific ones."""

    def get_code_style(self):
        # Return your project's code box style, or None for default
        return None

    def get_explanation_style(self):
        return None

    def get_details_style(self):
        return None


# Activate at import time — all blocks will use these styles
set_block_helper_config(ProjectBlockHelperConfig())
```

---

### A7. ✅ Compléter template_collection

**Dossier** : `documentation/template_collection/`

**Problème actuel** : pas de dossier `blocks/`, pas de README, `custom/styles.py`
utilise un pattern différent des autres projets.

**Actions** :
1. Créer `documentation/template_collection/blocks/__init__.py` avec le pattern
   `ProjectBlockRegistry` standard
2. Créer `documentation/template_collection/blocks/bck_home.py` — bloc d'exemple
   minimal pour la page d'accueil
3. Créer `documentation/template_collection/blocks/helpers.py` — helpers minimal
4. Aligner `custom/styles.py` sur le même pattern que `template_project`

---

## Phase B — Corrections isolées (un fichier, un fix)

> **Risque : FAIBLE.** Chaque correction touche un seul fichier, une seule ligne ou
> un seul pattern. Facilement réversible avec `git checkout -- <file>`.

### B1. ✅ Fix StyleGrid mutable default argument

**Fichier** : `streamtex/styles/core.py`
**Ligne 179** :
```python
# AVANT
def __init__(self, css_grid: List[List[Style]] = []):
    self.css_grid = css_grid
```

**Action** :
```python
# APRÈS
def __init__(self, css_grid: Optional[List[List[Style]]] = None):
    self.css_grid = css_grid if css_grid is not None else []
```

**Tests** : Vérifier que `test_styles.py::TestStyleGrid` passe toujours.

---

### B2. ✅ Fix isinstance au lieu de type() dans space.py

**Fichier** : `streamtex/space.py`
**Ligne 17** :
```python
# AVANT
if type(size) is int:
# APRÈS
if isinstance(size, int):
```

---

### B3. ✅ Supprimer le code mort `if False` dans container.py

**Fichier** : `streamtex/container.py`
**Lignes 18-24** : Bloc CSS conditionné par `if False` — ne s'exécute jamais.

**Action** : Supprimer le bloc conditionnel entier. Garder le reste du CSS intact.

---

### B4. ✅ Améliorer la génération d'ancres dans toc.py (voir notes post-exécution #1)

**Fichier** : `streamtex/toc.py`
**Lignes 94-96** :
```python
# AVANT
@staticmethod
def get_key_anchor(title: str):
    return title.replace('.', '-').replace(' ', '-').lower()
```

**Action** :
```python
# APRÈS
@staticmethod
def get_key_anchor(title: str):
    import re
    # Remove non-alphanumeric characters (keep letters, digits, hyphens)
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Collapse whitespace and hyphens into single hyphens
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug or 'section'
```

**Tests** : Vérifier que `test_toc.py::TestTOCRegistry::test_key_anchor_format` passe.
Ajouter un test pour les caractères spéciaux :
```python
def test_key_anchor_special_chars(self):
    anchor = TOCRegistry.get_key_anchor("L'introduction à la théorie")
    assert " " not in anchor
    assert "'" not in anchor
```

---

### B5. ✅ Remplacer print() par logging dans book.py

**Fichier** : `streamtex/book.py`
**Lignes concernées** : 54, 137, 673, 824-825

**Action** :
1. Ajouter en haut du fichier (après les imports) :
```python
import logging
logger = logging.getLogger(__name__)
```
2. Remplacer chaque `print(...)` par `logger.debug(...)`.

**Raison** : Les utilisateurs ne verront plus de messages de timing dans la console
sauf s'ils activent le logging explicitement.

---

### B6. ✅ Étendre la détection MIME dans image_utils.py (voir notes post-exécution #2)

**Fichier** : `streamtex/image_utils.py`
**Lignes 22-32** :
```python
# AVANT (switch if/elif manuel)
```

**Action** :
```python
# APRÈS
def _get_mime_type(file_path: str):
    """Determine the MIME type based on the file extension."""
    import mimetypes
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith('image/'):
        return mime
    # Fallback for common types not in mimetypes DB
    ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
    fallback = {
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        'bmp': 'image/bmp',
        'ico': 'image/x-icon',
    }
    return fallback.get(ext)
```

**Impact** : Ajoute le support SVG, WEBP, BMP, ICO sans casser l'existant.
**Tests** : Ajouter dans `test_utils.py` :
```python
def test_svg(self): assert _get_mime_type("icon.svg") == "image/svg+xml"
def test_webp(self): assert _get_mime_type("photo.webp") == "image/webp"
```

---

### B7. ✅ Ajouter validation TOML dans collection.py

**Fichier** : `streamtex/collection.py`
**Lignes 77-78** : `data = tomllib.load(f)` sans try/except.

**Action** : Entourer d'un try/except :
```python
try:
    data = tomllib.load(f)
except Exception as e:
    raise ValueError(
        f"Failed to parse collection TOML at {path}: {e}\n"
        f"Check TOML syntax at https://toml.io"
    ) from e
```

---

### B8. ✅ Remplacer print() par logging dans image_utils.py

**Fichier** : `streamtex/image_utils.py`
**Ligne 41** : `print(f"Error reading file {file_path}: {e}")`

**Action** :
```python
import logging
logger = logging.getLogger(__name__)
# ...
logger.warning(f"Error reading file {file_path}: {e}")
```

---

## Phase C — Features additives (ajout de code, pas de modification)

> **Risque : FAIBLE À MODÉRÉ.** Ajout de fonctionnalités nouvelles. L'existant n'est
> pas modifié. Risque uniquement si les exports `__init__.py` changent.

### C1. ✅ Ajouter `list_blocks()` à LazyBlockRegistry

**Fichier** : `streamtex/blocks.py`
**Après la méthode `__repr__` de LazyBlockRegistry (ligne ~97)** :

**Action** : Ajouter :
```python
def list_blocks(self) -> list:
    """List all discoverable block names across all sources."""
    blocks = set()
    for source_dir in self.sources:
        if os.path.isdir(source_dir):
            for f in os.listdir(source_dir):
                if f.startswith("bck_") and f.endswith(".py"):
                    blocks.add(f[:-3])  # Remove .py
    return sorted(blocks)

def get(self, block_name: str):
    """Get a block by name. Same as attribute access but explicit."""
    return getattr(self, block_name)
```

**Raison** : Aligner l'API avec `ProjectBlockRegistry` qui a déjà `list_blocks()`.

---

### C2. ✅ Ajouter paramètre `gap` à st_grid() (voir notes post-exécution #3)

**Fichier** : `streamtex/grid.py`
**Signature actuelle** (~ligne 120) : `def st_grid(cols=1, grid_style=None, cell_styles=None):`

**Action** : Ajouter un paramètre `gap` optionnel :
```python
def st_grid(cols=1, grid_style=None, cell_styles=None, gap=None):
```

Et dans le CSS (~ligne 138), remplacer `gap: 0;` par :
```python
gap_value = gap if gap else "0"
# ...
f"gap: {gap_value};"
```

**Important** : Si `grid_style` contient aussi un `gap`, le paramètre explicite
a priorité. Documenter ce comportement.

**Tests** : Ajouter un test dans un nouveau `test_grid.py`.

---

### C3. ✅ Ajouter paramètre `count` à st_br() (voir notes post-exécution #4)

**Fichier** : `streamtex/space.py`
**Lignes 30-32** :
```python
# AVANT
def st_br():
    return st_space("v", 0)
```

**Action** :
```python
# APRÈS
def st_br(count: int = 1):
    """Add vertical line breaks. count=1 adds one <br>, count=2 adds two, etc."""
    html = "<br>" * max(1, count)
    _render(html)
```

**Raison** : `st_br()` actuel génère `padding-top: 0` qui ne fait rien visuellement.
La nouvelle version génère de vrais `<br>` tags.

---

### C4. ✅ Ajouter placeholder pour images non trouvées

**Fichier** : `streamtex/image.py`
**Lignes 88-90** : Actuellement `img_src = ""` si image non trouvée.

**Action** : Au lieu de générer `<img src="">`, générer un placeholder visible :
```python
if not img_src:
    placeholder = (
        f'<div style="border:2px dashed #888;padding:16px;text-align:center;'
        f'color:#888;border-radius:4px;margin:8px 0;">'
        f'Image not found: {uri}</div>'
    )
    _render(placeholder)
    return
```

---

### C5. ✅ Ajouter validation du paramètre `cols` dans st_grid()

**Fichier** : `streamtex/grid.py`
**Après la conversion int → str (~ligne 126)** :

**Action** : Ajouter une validation basique :
```python
if isinstance(cols, str):
    # Basic validation: must contain at least one CSS grid track
    if not cols.strip():
        raise ValueError("st_grid cols parameter cannot be empty string")
```

---

### C6. ✅ Ajouter tri stable dans collection.py

**Fichier** : `streamtex/collection.py`
**Lignes 101-106** :
```python
# AVANT
config.projects = dict(
    sorted(
        config.projects.items(),
        key=lambda item: item[1].order,
    )
)
```

**Action** :
```python
# APRÈS — tri stable avec clé comme tiebreaker
config.projects = dict(
    sorted(
        config.projects.items(),
        key=lambda item: (item[1].order, item[0]),
    )
)
```

---

## Phase D — Tests unitaires (ajout pur)

> **Risque : ZÉRO.** Ajout de fichiers de tests sans modification du code source.
> Peut révéler des bugs existants, ce qui est une bonne chose.

### D1. ✅ Créer test_grid.py (45 tests)

**Fichier à créer** : `tests/test_grid.py`

**Cas à tester** :
- `st_grid(cols=3)` génère `grid-template-columns: 1fr 1fr 1fr`
- `st_grid(cols="200px 1fr")` utilise le string tel quel
- `st_grid(cols="")` lève `ValueError` (après C5)
- `st_grid(cols=3, gap="24px")` génère `gap: 24px` (après C2)
- `StyleGrid` avec per-cell styling
- Interaction avec le buffer d'export

---

### D2. ✅ Créer test_container.py (42 tests)

**Fichier à créer** : `tests/test_container.py`

**Cas à tester** :
- `st_block(style)` génère un div avec le style CSS
- `st_span(style)` génère un div avec `display:flex`
- Nesting : `st_block` dans `st_block`
- Export wrapper : `<div>` pour block, `<div style="display:flex">` pour span

---

### D3. ✅ Créer test_list.py (31 tests)

**Fichier à créer** : `tests/test_list.py`

**Cas à tester** :
- `st_list(items, list_type="ul")` génère les items
- `st_list(items, list_type="ol")` utilise un counter CSS
- Nested items avec tuples
- `ListStyle(symbols=["→", "•"])` cycle correctement
- `ListStyle` avec liste vide de symboles (après R5 fix)

---

### D4. ✅ Créer test_space.py (40 tests)

**Fichier à créer** : `tests/test_space.py`

**Cas à tester** :
- `st_space("v", 2)` génère `padding-top: 2em`
- `st_space("h", 3)` génère `padding-left: 3em`
- `st_space("v", "20px")` utilise la valeur string telle quelle
- `st_br()` génère un `<br>` (après C3)
- `st_br(3)` génère trois `<br>` (après C3)

---

### D5. ✅ Créer test_image.py (44 tests)

**Fichier à créer** : `tests/test_image.py`

**Cas à tester** :
- Image existante (PNG) → génère `<img src="data:image/png;base64,..."`
- Image inexistante → génère placeholder (après C4)
- URL → utilise l'URL directement
- `configure_image_path("custom/path")` change le chemin de base

---

### D6. ✅ Créer test_code.py (14 tests)

**Fichier à créer** : `tests/test_code.py`

**Cas à tester** :
- `st_code(style, code="print('hello')")` génère du HTML avec Pygments
- Fallback sans Pygments → génère `<pre>` simple
- `language="python"` utilise le bon lexer
- `line_numbers=True` génère des numéros de ligne

---

### D7. ✅ Créer test_overlay.py (18 tests)

**Fichier à créer** : `tests/test_overlay.py`

**Cas à tester** :
- `st_overlay()` crée un conteneur `position: relative`
- `o.layer(top=20, left=30)` génère `position: absolute; top: 20px; left: 30px`
- `o.layer(top="50%")` utilise la valeur string telle quelle
- Export wrapper génère le HTML correct

---

### D8. ✅ Créer test_book_integration.py (22 tests, voir notes post-exécution #5)

**Fichier à créer** : `tests/test_book_integration.py`

**Cas à tester** :
- `st_include(module)` appelle `module.build()`
- `st_include(module)` gère les erreurs gracieusement
- `load_css()` charge le CSS par défaut
- Cache hash est stable pour les mêmes entrées
- Cache hash est différent pour des ordres différents (bug actuel !)

---

## Phase E — Refactoring interne (modifications structurelles)

> **Risque : MODÉRÉ.** Ces changements touchent l'architecture interne. Chaque
> modification doit être suivie d'un run complet de tests.

### E1. ✅ Centraliser les constantes dupliquées (voir notes post-exécution #6)

**Problème** : `PAGE_WIDTH="1224pt"` et `PAGE_PADDING="36pt"` sont définies dans :
- `streamtex/zoom.py` lignes 54-56
- `streamtex/export.py` ligne 26 (dans `ExportConfig` dataclass defaults)

**Action** :
1. Créer `streamtex/constants.py` :
```python
"""Centralized constants for StreamTeX."""
PAGE_WIDTH = "1224pt"
PAGE_PADDING = "36pt"
```
2. Importer depuis `zoom.py` et `export.py` :
```python
from .constants import PAGE_WIDTH, PAGE_PADDING
```
3. Ajouter `from .constants import PAGE_WIDTH, PAGE_PADDING` dans `__init__.py`
   si pertinent.

---

### E2. Normaliser add_css() dans styles/core.py

**Fichier** : `streamtex/styles/core.py`
**Lignes ~15-22** :

**Problème actuel** :
- `"color:red" + "font-size:12pt"` → `"color:red; font-size:12pt"` (pas de `;` final)
- `"color:red;" + ";font-size"` → `"color:red;; ;font-size"` (double `;`)

**Action** :
```python
def add_css(str1: str, str2: str) -> str:
    """Merge two CSS strings, normalizing semicolons."""
    parts = []
    for s in [str1, str2]:
        if s and s.strip():
            parts.append(s.rstrip('; ').strip())
    return "; ".join(parts) + (";" if parts else "")
```

**Tests** : Ajouter dans `test_styles.py` :
```python
def test_add_css_normalizes_semicolons(self):
    assert add_css("color:red;", ";font-size:12pt") == "color:red; font-size:12pt;"
    assert add_css("color:red", "font-size:12pt") == "color:red; font-size:12pt;"
    assert add_css("", "color:red") == "color:red;"
    assert add_css("color:red", "") == "color:red;"
```

**ATTENTION** : Cette modification affecte toute la composition de styles.
Tester **tous** les tests existants + lancer les projets visuellement.

---

### E3. Protéger ListStyle.lvl() contre liste vide

**Fichier** : `streamtex/styles/core.py`
**Méthode `lvl()`** (~ligne 170) :

```python
# AVANT
index = (lvl - 1) % len(self.symbols)

# APRÈS
if not self.symbols:
    return ""
index = (lvl - 1) % len(self.symbols)
```

---

### E4. Remplacer le state global par logging module dans book.py

**Fichier** : `streamtex/book.py`

**Action complémentaire à B5** : Après avoir remplacé print() par logging, vérifier
que le module n'utilise pas d'autres effets de bord globaux non nécessaires.

Les clés `st.session_state` suivantes doivent être préfixées de manière unique :
- `_stx_page_cache` → `_streamtex_page_cache`
- `_stx_current_page` → `_streamtex_current_page`
- `_stx_view_mode` → `_streamtex_view_mode`

Ce renommage est rétro-compatible car ces clés sont internes à la librairie.

---

### E5. Harmoniser les erreurs LazyBlockRegistry / ProjectBlockRegistry

**Fichier** : `streamtex/blocks.py`

**Problème** : `LazyBlockRegistry.__getattr__` lève `AttributeError` (ligne 94).
`ProjectBlockRegistry.get` lève `BlockNotFoundError` (ligne 173).

**Action** :
1. Dans `LazyBlockRegistry.__getattr__`, remplacer les deux `raise AttributeError`
   par `raise BlockNotFoundError` (pour les blocs non trouvés) et
   `raise BlockImportError` (pour les erreurs d'import).
2. Garder un `except (BlockNotFoundError, BlockImportError) as e:` qui
   re-raise en `AttributeError(str(e))` pour compatibilité `getattr()`.

```python
def __getattr__(self, block_name: str):
    if block_name.startswith('_'):
        raise AttributeError(f"LazyBlockRegistry has no attribute '{block_name}'")
    # ... chargement ...
    try:
        return self._load(block_name)
    except BlockNotFoundError as e:
        raise AttributeError(str(e)) from e
```

---

### E6. Corriger le module name collision dans LazyBlockRegistry

**Fichier** : `streamtex/blocks.py`
**Ligne 80** : `f"lazy_blocks.{block_name}"`

**Action** :
```python
# APRÈS — inclure l'id du registre pour unicité
spec = importlib.util.spec_from_file_location(
    f"lazy_blocks_{id(self)}_{block_name}",
    block_path
)
```

---

### E7. Ajouter cleanup des timers/observers dans marker.py

**Fichier** : `streamtex/marker.py`

**Problème** : Si le marker est injecté plusieurs fois, les MutationObserver et
setInterval s'accumulent (memory leak).

**Action** : Au début du script JS injecté (avant la création du MutationObserver),
ajouter :
```javascript
// Cleanup previous instance if exists
if (hostWin._stxMarkerCleanup) {
    try { hostWin._stxMarkerCleanup(); } catch(e) {}
}
```

Ceci est déjà partiellement fait dans la cleanup function (lignes 433-443),
mais le cleanup n'est pas appelé AVANT la réinjection.

---

## Phase F — Refactoring d'API publique (risque élevé)

> **Risque : ÉLEVÉ.** Ces changements affectent l'interface publique de la librairie.
> Ils nécessitent une migration dans tous les projets tests et templates.
> **NE PAS commencer cette phase sans avoir terminé les phases A-E.**

### F1. Ajouter `__all__` dans tous les `__init__.py`

**Fichiers concernés** :
- `streamtex/__init__.py`
- `streamtex/styles/__init__.py`

**Action** : Ajouter un `__all__` explicite listant uniquement les symboles publics.

**Exemple pour `streamtex/__init__.py`** :
```python
__all__ = [
    # Core rendering
    "st_write", "st_image", "st_code", "st_block", "st_span",
    "st_space", "st_br", "st_grid", "st_list", "st_overlay",
    # Book & navigation
    "st_book", "st_include", "st_toc", "load_css",
    "TOCConfig", "MarkerConfig", "st_marker",
    # Styles
    "Style", "ListStyle", "StyleGrid", "StreamTeX_Styles",
    # Enums
    "Tags",
    # Export
    "ExportConfig", "st_export",
    "st_dataframe", "st_table", "st_metric", "st_json",
    # Registry
    "LazyBlockRegistry", "ProjectBlockRegistry",
    "BlockNotFoundError", "BlockImportError",
    "set_static_sources", "get_static_sources", "resolve_static",
    # Helpers
    "BlockHelperConfig", "BlockHelper",
    "show_code", "show_code_inline", "show_explanation", "show_details",
    "set_block_helper_config", "get_block_helper_config",
    # Collection
    "st_collection", "CollectionConfig", "ProjectMeta",
    # Zoom
    "add_zoom_options", "inject_zoom_logic",
]
```

**Raison** : Contrôle explicite de `from streamtex import *`. Actuellement, cet
import expose des détails d'implémentation.

---

### F2. Ajouter type hints systématiques

**Fichiers concernés** : Tous les modules publics de `streamtex/`.

**Priorité** (par fréquence d'utilisation) :
1. `write.py` — `st_write(style: Style, *args, tag: Tag = ..., ...) -> None`
2. `container.py` — `st_block(style: Style = ...) -> ContextManager`
3. `grid.py` — `st_grid(cols: Union[int, str] = ..., ...) -> ContextManager`
4. `space.py` — `st_space(direction: str, size: Union[int, str]) -> None`
5. `image.py` — `st_image(style: Style, uri: str, ...) -> None`
6. `list.py` — `st_list(items: list, ...) -> ContextManager`
7. `code.py` — `st_code(style: Style, code: str, ...) -> None`
8. `overlay.py` — `st_overlay(style: Style = ...) -> ContextManager`

**Action** :
- Ajouter les annotations de type sur les fonctions publiques
- Créer `streamtex/py.typed` (fichier vide, PEP 561 marker)
- Ne PAS modifier le comportement, uniquement les annotations

**ATTENTION** : Certaines fonctions acceptent `Style` ou `str` pour le paramètre
`style` (via l'opérateur `+`). Les type hints doivent refléter ça :
`Union[Style, str, None]`.

---

### F3. Migrer les enums vers enum.Enum (OPTIONNEL)

**Fichier** : `streamtex/enums.py`

**État actuel** : Classes custom `Tag` et `ListType` avec `__repr__`.

**Action** :
```python
from enum import Enum

class Tags(str, Enum):
    div = "div"
    span = "span"
    h1 = "h1"
    # ...

class ListTypes(str, Enum):
    ordered = "ol"
    unordered = "ul"
```

**ATTENTION** : Changement BREAKING. `Tags.div` retournait `"div"` via `__repr__()`.
Avec `str, Enum`, `str(Tags.div)` retourne `"Tags.div"` et `Tags.div.value` retourne
`"div"`. Il faut vérifier TOUS les usages de `Tags.*` dans la codebase.

**Migration nécessaire** : Partout où `str(tag)` ou `repr(tag)` est utilisé pour
obtenir le nom HTML, il faudra utiliser `tag.value`.

**Fichiers impactés** : `write.py`, `list.py`, `container.py`, tous les blocs.

> **Recommandation** : Différer cette tâche à une version 0.3.0 avec une migration
> guide explicite. L'impact est trop large pour un patch maintenance.

---

### F4. Validate_project() — outil de diagnostic pour débutants (OPTIONNEL)

**Fichier à créer** : `streamtex/doctor.py`

**Concept** : Un helper qui vérifie la structure d'un projet StreamTeX et signale
les problèmes courants.

```python
def validate_project(project_path: str) -> list:
    """Validate a StreamTeX project structure. Returns list of issues."""
    issues = []
    # Check blocks/ directory exists
    # Check build() function in each block
    # Check custom/styles.py exists
    # Check setup.py exists
    # Check book.py exists and imports st_book
    return issues
```

**Usage prévu** :
```bash
uv run python -c "from streamtex.doctor import validate_project; print(validate_project('.'))"
```

> **Recommandation** : Feature utile mais non urgente. À planifier pour 0.3.0.

---

## Résumé du plan d'exécution

| Phase | Tâches | Risque | Statut |
|-------|--------|--------|--------|
| **A** | A1-A7 | ZÉRO | ✅ TERMINÉE |
| **B** | B1-B8 | FAIBLE | ✅ TERMINÉE |
| **C** | C1-C6 | FAIBLE-MODÉRÉ | ✅ TERMINÉE |
| **D** | D1-D8 | ZÉRO | ✅ TERMINÉE (260 tests ajoutés) |
| **E** | E1 | MODÉRÉ | ✅ E1 TERMINÉE |
| **E** | E2-E7 | MODÉRÉ | ⬜ À FAIRE |
| **F** | F1-F4 | ÉLEVÉ | ⬜ À FAIRE |

### Ordre d'exécution recommandé (restant)

```
→ E2 → E3 → E4 → E5 → E6 → E7
→ F1 → F2 → F3 (optionnel) → F4 (optionnel)
```

### Checkpoint obligatoire après chaque tâche

```bash
uv run pytest tests/ -v
# Attendu : 466+ tests passent
```

### Points de non-retour

- **Après Phase E2** (normalisation add_css) : tester VISUELLEMENT chaque projet
  test pour vérifier que les styles n'ont pas changé d'apparence.
- **Avant Phase F3** (enum migration) : créer une branche dédiée. Ne pas merger
  sur main sans validation complète.

---

*Plan généré le 2026-02-20 à 11:23 par inspection approfondie du projet StreamTeX v0.2.0.*
*Phases A→E1 exécutées le 2026-02-20. 466 tests passent (203 initiaux + 3 MIME + 260 Phase D).*
*Fichiers créés : 8 tests + constants.py + 3 template_collection. Fichiers modifiés : 12 librairie + 4 documentation.*
