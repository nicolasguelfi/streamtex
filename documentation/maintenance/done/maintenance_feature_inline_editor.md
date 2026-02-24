# Proposition : Block Inspector — Editeur de sources inline pour StreamTeX

**Date** : 2026-02-21
**Statut** : Proposition v2 (non implemente)
**Priorite** : Haute
**Modules cibles** : `streamtex/inspector.py` (nouveau), modifications dans `streamtex/book.py`

---

## 1. Contexte et besoin

> "Lorsque je visualise un element a l'ecran, je voudrais pouvoir acceder aux
> differents fichiers qui ont ete utilises pour rendre ce que je vois — le fichier
> Python du bloc, mais aussi les fichiers annexes : textes, diagrammes Mermaid,
> donnees JSON, images, styles... Pouvoir modifier rapidement le contenu, les
> valeurs, les parametres, les couleurs, le style, et voir le resultat sans IDE."

---

## 2. Decisions de conception (clarifiees)

| Point | Decision |
|---|---|
| **Conteneur** | Panneau droit extensible (pas un dialog modal) |
| **Bouton** | `✎` discret, coin superieur droit de chaque bloc |
| **Blocs concernes** | Tous : atomiques ET composites |
| **Categories de fichiers** | Registre extensible (pas de dico hardcode) |
| **Editeur** | `streamlit-ace` (avec fallback `st.text_area`) |
| **Sauvegarde** | Un bouton Save par fichier + bouton Cancel par fichier |
| **Securite** | Pas de restriction de repertoire ; mot de passe optionnel |
| **Deploiement Docker** | Les edits sur version deployee seront ecrases ; accepte |
| **Git push** | Non prevu pour l'instant |

---

## 3. Faisabilite du panneau droit dans Streamlit

### 3.1 Technique utilisee : `:has()` + `position: fixed`

StreamTeX utilise deja exactement cette technique dans 3 composants :

| Composant | Technique | Fichier |
|---|---|---|
| `st_block()` | `:has()` + marker span → repositionnement CSS | `container.py:19` |
| Marker navigation | `position: fixed; z-index: 999998` | `marker.py:285` |
| Zoom layout | CSS modifiant `.stMain .block-container` | `zoom.py:58-80` |

Le principe pour le panneau droit serait identique :

```
┌─ .stApp ─────────────────────────────────────────────────────────┐
│ ┌─ stSidebar ─┐  ┌─ .stMain ──────────────────────────────────┐ │
│ │             │  │ ┌─ .block-container ──────┐ ┌─ Inspector ┐ │ │
│ │  Table des  │  │ │                         │ │             │ │ │
│ │  matieres   │  │ │  Contenu des blocs      │ │  Fichiers   │ │ │
│ │             │  │ │  (compresse quand        │ │  du bloc    │ │ │
│ │  Markers    │  │ │   l'inspecteur est       │ │  selectionne│ │ │
│ │             │  │ │   ouvert)                │ │             │ │ │
│ │  Zoom       │  │ │                         │ │  [Save]     │ │ │
│ │             │  │ └─────────────────────────┘ │  [Cancel]   │ │ │
│ └─────────────┘  │                             └─────────────┘ │ │
│                  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation CSS

```css
/* Marqueur invisible dans le container de l'inspecteur */
div:has(> .element-container > .stHtml > span.stx-inspector-panel) {
    position: fixed !important;
    right: 0 !important;
    top: 0 !important;
    width: var(--stx-inspector-width, 35%) !important;
    height: 100vh !important;
    overflow-y: auto !important;
    z-index: 100 !important;  /* au-dessus du contenu, sous les tooltips */
    background: var(--background-color) !important;
    box-shadow: -2px 0 8px rgba(0,0,0,0.15) !important;
    padding: 1rem !important;
    border-left: 1px solid rgba(128,128,128,0.2) !important;
}

/* Compresser le contenu principal quand l'inspecteur est ouvert */
.stMain .block-container {
    padding-right: calc(var(--stx-inspector-width, 35%) + 20px) !important;
}
```

### 3.3 Pourquoi ca fonctionne

1. **Widgets Streamlit reels** : Le container repositionne contient de vrais widgets
   (`st_ace`, `st.button`, `st.tabs`). Le CSS ne deplace que visuellement ; l'arbre
   React de Streamlit reste intact. Les interactions (clic, saisie) fonctionnent normalement.

2. **Pattern deja prouve** : `st_block()` utilise exactement le meme mecanisme
   (`:has()` + marker span) depuis le debut du projet (`container.py:19-39`).

3. **Scroll independant** : `overflow-y: auto` sur le panneau fixe donne un scroll
   independant du contenu principal. L'utilisateur peut scroller le code dans
   l'inspecteur sans bouger le contenu visible.

4. **Redimensionnement** : Via une variable CSS `--stx-inspector-width` modifiable
   par un selecteur dans le panneau (Narrow 25% / Medium 35% / Wide 50%).

### 3.4 Points d'attention

| Risque | Mitigation |
|---|---|
| Ecrans etroits (<1024px) | Passer en mode overlay au lieu de cote-a-cote |
| Rerun Streamlit | Le panneau est re-rendu a chaque rerun (session_state conserve l'etat) |
| Conflit z-index | z-index 100 (sous marker 999998, sous tooltips 999999) |
| Export HTML | Cacher l'inspecteur pendant l'export (`is_export_active()`) |

---

## 4. Registre de categories de fichiers (extensible)

### 4.1 Probleme avec un dico hardcode

Un dictionnaire `_EXT_TO_CATEGORY = {".mmd": "Diagrams", ...}` est :
- Rigide : ajouter une categorie necessite de modifier le code source
- Non-extensible par les projets utilisateurs
- Incapable de gerer les nouveaux types decouverts dynamiquement

### 4.2 Solution : `FileCategoryRegistry` (pattern d'enregistrement)

```python
@dataclass
class FileCategory:
    """Definition d'une categorie de fichiers."""
    name: str                    # Nom affiche (onglet)
    extensions: set[str]         # {".mmd", ".tex"}
    ace_language: str            # Mode pour streamlit-ace
    validator: Callable | None   # Fonction de validation (ou None)
    icon: str = ""               # Icone optionnelle


class FileCategoryRegistry:
    """Registre extensible de categories de fichiers."""

    def __init__(self):
        self._categories: list[FileCategory] = []
        self._ext_index: dict[str, FileCategory] = {}

    def register(self, category: FileCategory):
        """Ajouter une categorie. Dernier enregistre gagne en cas de conflit."""
        self._categories.append(category)
        for ext in category.extensions:
            self._ext_index[ext] = category

    def get_category(self, file_path: str) -> FileCategory:
        """Trouver la categorie pour un fichier. Auto-decouverte si inconnu."""
        ext = Path(file_path).suffix.lower()
        if ext in self._ext_index:
            return self._ext_index[ext]
        # Auto-decouverte : creer une categorie "Other" pour les extensions inconnues
        return FileCategory(name="Other", extensions={ext},
                           ace_language="text", validator=None)

    def categories_used(self, files: list) -> list[FileCategory]:
        """Retourner uniquement les categories qui ont des fichiers."""
        ...
```

### 4.3 Categories integrées

```python
# Enregistrement des categories de base
_registry = FileCategoryRegistry()

_registry.register(FileCategory(
    name="Python", extensions={".py"},
    ace_language="python",
    validator=_validate_python,
))

_registry.register(FileCategory(
    name="Diagrams", extensions={".mmd", ".tex", ".puml", ".dot"},
    ace_language="text",
    validator=None,
))

_registry.register(FileCategory(
    name="Data", extensions={".json", ".csv", ".toml", ".yaml", ".yml"},
    ace_language="json",  # json par defaut, adapte per-file
    validator=_validate_json_if_json,
))

_registry.register(FileCategory(
    name="Texts", extensions={".txt", ".md", ".bib", ".ris", ".rst"},
    ace_language="markdown",
    validator=None,
))
```

### 4.4 Extension cote projet

```python
# Dans book.py ou setup.py du projet utilisateur
from streamtex.inspector import FileCategory, get_category_registry

get_category_registry().register(FileCategory(
    name="SQL",
    extensions={".sql"},
    ace_language="sql",
    validator=None,
))
```

### 4.5 Decouverte dynamique

Quand un fichier avec une extension inconnue est decouvert, le registre
renvoie automatiquement une categorie "Other" avec un editeur texte.
L'utilisateur voit le fichier et peut l'editer. Aucune configuration necessaire.

---

## 5. Le bouton `✎` : blocs atomiques ET composites

### 5.1 Qui recoit un bouton ?

Chaque module dans la `module_list` de `st_book()` recoit un bouton `✎`.
Cela inclut les blocs atomiques ET les composites.

### 5.2 Comportement selon le type de bloc

| Type de bloc | Fichiers affiches dans l'inspecteur |
|---|---|
| **Atomique** (ex: `bck_title.py`) | `bck_title.py` + fichiers statiques references + `custom/styles.py` |
| **Composite** (ex: `bck_ui_components.py`) | `bck_ui_components.py` + TOUS les atomiques (`_atomic/bck_tabs.py`, `_atomic/bck_dynamic.py`, ...) + fichiers statiques + styles |

### 5.3 Pas de confusion : un seul bouton par section visible

Le bouton `✎` apparait uniquement au niveau `st_book` (un par element de `module_list`).
Il n'y a **pas** de bouton supplementaire sur les sous-blocs atomiques rendus
a l'interieur d'un composite. L'inspecteur du composite montre deja tous ses
fichiers internes.

```
┌──────────────────────────────────────────────────────────┐
│ ✎  bck_ui_components  (composite)                       │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ bck_tabs_expanders_popover  (atomique, pas de ✎)    │ │
│ │ contenu rendu...                                     │ │
│ └──────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ bck_dynamic_content  (atomique, pas de ✎)           │ │
│ │ contenu rendu...                                     │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

Au clic sur `✎`, l'inspecteur montre :
- Tab **Python** : `bck_ui_components.py`, `_atomic/bck_tabs_expanders_popover.py`, `_atomic/bck_dynamic_content.py`
- Tab **Diagrams** : tout fichier `.mmd` ou `.tex` reference
- Tab **Data** : tout fichier `.json`, `.csv` reference
- Tab **Styles** : `custom/styles.py`

### 5.4 Cas special : bloc atomique utilise seul dans st_book

Si `module_list` contient directement un bloc atomique (pas enveloppe dans
un composite), il recoit son propre `✎` et l'inspecteur montre ses fichiers.
Aucune ambiguite.

---

## 6. Placement du bouton `✎` (coin superieur droit)

### 6.1 Technique CSS

Le bouton est un vrai `st.button` Streamlit, repositionne en coin superieur droit
via CSS (meme pattern que `st_block` dans `container.py`).

```python
# Dans st_include, quand l'inspecteur est actif :
btn_id = generate_key("insp_btn")

# 1. Marker invisible pour le CSS
st.html(f'<span class="{btn_id}" style="display:none;"></span>')

# 2. Vrai bouton Streamlit (cliquable)
clicked = st.button("✎", key=f"_stx_inspect_{block_name}",
                     help=f"Inspect: {block_name}")

# 3. CSS pour positionner le bouton dans le coin superieur droit du bloc
st.html(f"""<style>
/* Le bouton est dans un container frere du bloc */
div:has(> .element-container > .stHtml > span.{btn_id}) + div [data-testid="stButton"] {{
    position: absolute;
    top: 4px;
    right: 4px;
    z-index: 50;
    opacity: 0.15;
    transition: opacity 0.2s;
}}
div:has(> .element-container > .stHtml > span.{btn_id}) + div [data-testid="stButton"]:hover {{
    opacity: 0.8;
}}
</style>""")
```

### 6.2 Comportement visuel

- **Par defaut** : bouton quasi-invisible (opacity 0.15)
- **Au hover** : bouton visible (opacity 0.8)
- **Taille** : petit, un seul caractere `✎`
- **Position** : fixe dans le coin superieur droit du bloc

### 6.3 Mode pagine vs continu

- **Mode continu** : un bouton `✎` par bloc visible dans la page (potentiellement beaucoup)
- **Mode pagine** : un seul bloc visible = un seul bouton `✎`

Dans les deux cas, le bouton est discret grace a l'opacity faible.

---

## 7. Save par fichier individuel + Cancel

### 7.1 UX dans le panneau inspecteur

```
┌─── Inspector: bck_ui_components ─────────────────┐
│                                                    │
│ Width: [▪ Narrow ▪ Medium ▪ Wide]    [✕ Close]   │
│                                                    │
│ ┌──────────────────────────────────────────────┐  │
│ │ Python │ Diagrams │ Data │ Styles │ Texts    │  │
│ ├──────────────────────────────────────────────┤  │
│ │                                              │  │
│ │ ▸ bck_ui_components.py                       │  │
│ │ ▸ _atomic/bck_tabs.py           ← selected   │  │
│ │ ▸ _atomic/bck_dynamic.py                     │  │
│ │                                              │  │
│ │ ┌──────────────────────────────────────────┐ │  │
│ │ │  1 │ import streamtex as stx             │ │  │
│ │ │  2 │ from streamtex import *             │ │  │
│ │ │  3 │                                     │ │  │
│ │ │  4 │ class BlockStyles:                  │ │  │
│ │ │  5 │     title = s.bold + s.Large        │ │  │
│ │ │ ...│                                     │ │  │
│ │ └──────────────────────────────────────────┘ │  │
│ │                                              │  │
│ │ ✓ Syntax OK                                  │  │
│ │ [💾 Save this file]   [↩ Cancel changes]     │  │
│ │                                              │  │
│ └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### 7.2 Workflow de sauvegarde

1. L'utilisateur edite un fichier dans l'inspecteur
2. La validation syntaxique s'affiche en temps reel (Python: `ast.parse`, JSON: `json.loads`)
3. **Save this file** : ecrit uniquement CE fichier sur disque + `.bak` backup
4. **Cancel changes** : recharge le contenu original depuis le disque (reset du text_area/ace)
5. Apres Save : Streamlit detecte le changement `.py` et relance le script
6. L'inspecteur reste ouvert sur le meme fichier (grace a `session_state`)

### 7.3 Indicateur de modifications non sauvegardees

```
│ ▸ bck_ui_components.py                          │
│ ▸ _atomic/bck_tabs.py  ● modified               │  ← point rouge si modifie
│ ▸ _atomic/bck_dynamic.py                         │
```

L'indicateur est base sur la comparaison entre le contenu actuel de l'editeur
et le contenu lu depuis le disque.

---

## 8. Securite : mot de passe optionnel

### 8.1 Pas de restriction de repertoire

L'inspecteur peut ouvrir n'importe quel fichier decouvert, meme hors du projet.
Cela couvre le cas des blocs partages (`LazyBlockRegistry` avec sources distantes).

### 8.2 Protection par mot de passe (optionnel)

```python
@dataclass
class InspectorConfig:
    enabled: bool = False
    password: str | None = None     # Si defini, demande le mot de passe
    ...

# Dans l'inspecteur, avant d'afficher le contenu :
if config.password:
    if "_stx_inspector_auth" not in st.session_state:
        st.session_state["_stx_inspector_auth"] = False
    if not st.session_state["_stx_inspector_auth"]:
        pwd = st.text_input("Password", type="password", key="_stx_insp_pwd")
        if pwd == config.password:
            st.session_state["_stx_inspector_auth"] = True
            st.rerun()
        elif pwd:
            st.error("Incorrect password")
        return  # Ne pas afficher l'inspecteur
```

### 8.3 Activation par variable d'environnement

```python
# Alternative a la config Python :
import os
InspectorConfig(
    enabled=os.getenv("STREAMTEX_INSPECTOR", "0") == "1",
    password=os.getenv("STREAMTEX_INSPECTOR_PASSWORD"),
)
```

---

## 9. Architecture technique : flux d'interaction

### 9.1 Session state

```python
_STX_INSPECTOR_OPEN    = "_stx_inspector_open"     # bool
_STX_INSPECTOR_BLOCK   = "_stx_inspector_block"    # nom du module inspecte
_STX_INSPECTOR_FILE    = "_stx_inspector_file"     # chemin du fichier selectionne
_STX_INSPECTOR_CAT     = "_stx_inspector_category" # onglet categorie actif
_STX_INSPECTOR_WIDTH   = "_stx_inspector_width"    # "Narrow" | "Medium" | "Wide"
_STX_INSPECTOR_AUTH    = "_stx_inspector_auth"      # bool (password ok?)
```

### 9.2 Flux complet

```
1. st_book() itere sur module_list
2.   pour chaque module :
3.     st_include() rend le bloc
4.     si inspector.enabled :
5.       rendre le bouton ✎ (discret, coin sup droit)
6.       si ✎ clique :
7.         session_state[OPEN] = True
8.         session_state[BLOCK] = module_name
9.         st.rerun()
10.
11. apres la boucle de rendu :
12.   si session_state[OPEN] == True :
13.     decouvrir les sources du bloc selectionne
14.     rendre le panneau droit (container + CSS fixed)
15.     l'utilisateur edite, save, ou close
16.     save → ecrire fichier → Streamlit rerun automatique
17.     close → session_state[OPEN] = False → st.rerun()
```

### 9.3 Structure du module `streamtex/inspector.py`

```
streamtex/inspector.py
├── InspectorConfig          # Configuration
├── FileCategory             # Definition d'une categorie
├── FileCategoryRegistry     # Registre extensible
├── SourceFile               # Un fichier decouvert
├── discover_sources()       # Decouverte (statique Phase 1, tracage Phase 2)
├── validate_file()          # Validation par type
├── render_inspector_panel() # Le panneau droit complet
├── inject_inspector_button()# Le bouton ✎
└── inject_inspector_css()   # CSS pour le panneau fixe
```

---

## 10. Decouverte des fichiers (Phase 1 : analyse statique)

### 10.1 Sources toujours decouvertes

| Source | Methode |
|---|---|
| Fichier Python principal | `module.__file__` |
| Blocs atomiques | Regex `load_atomic_block\("(\w+)"` dans le source |
| `custom/styles.py` | Convention : remonter jusqu'a `book.py`, resoudre `custom/styles.py` |

### 10.2 Sources decouvertes par regex

Scanner le code Python (principal + atomiques) pour extraire les chaines
de caracteres contenant des extensions de fichiers connues :

```python
# Pattern : chaine contenant un chemin avec extension connue
KNOWN_EXTENSIONS = {".mmd", ".tex", ".json", ".csv", ".txt", ".md",
                    ".bib", ".ris", ".toml", ".yaml", ".yml", ".sql",
                    ".puml", ".dot"}

pattern = r'["\']([^"\']*\.(?:' + '|'.join(ext[1:] for ext in KNOWN_EXTENSIONS) + r'))["\']'

# Pour chaque match, tenter de resoudre le chemin :
# 1. Chemin absolu ? → utiliser directement
# 2. resolve_static() → chercher dans les static_sources
# 3. Relatif au bloc → chercher par rapport au fichier .py
# 4. Relatif au projet → chercher par rapport a book.py
```

### 10.3 Declaration explicite (fallback)

```python
# Dans un bloc, optionnel :
__sources__ = [
    "static/data/custom_format.xyz",  # Fichier avec extension non standard
]
```

### 10.4 Phase 2 (futur) : tracage runtime

Instrumenter `resolve_static()` et `st_image()` pour enregistrer les acces
fichiers pendant `build()`. Combine avec l'analyse statique pour 100% de couverture.

---

## 11. Plan d'implementation

### Phase 1 : MVP

- [ ] `streamtex/inspector.py` : `InspectorConfig`, `FileCategoryRegistry`, `SourceFile`
- [ ] Decouverte statique : Python files + atomiques + regex + styles
- [ ] Panneau droit : CSS fixed + marker span (pattern `container.py`)
- [ ] Editeur : `streamlit-ace` (fallback `st.text_area`)
- [ ] Bouton `✎` : discret, coin superieur droit, opacity fade
- [ ] Save/Cancel par fichier individuel avec backup `.bak`
- [ ] Validation : Python (`ast.parse`), JSON (`json.loads`)
- [ ] Integration `st_book` + `st_include` (parametre `inspector`)
- [ ] Mot de passe optionnel
- [ ] Redimensionnement : Narrow / Medium / Wide
- [ ] Export `InspectorConfig` dans `streamtex/__init__.py`
- [ ] Tests unitaires (decouverte, validation, registre categories)

### Phase 2 : Ameliorations

- [ ] Tracage runtime (`resolve_static`, `st_image`)
- [ ] Preview live pour Mermaid/TikZ dans l'inspecteur
- [ ] Indicateur visuel de fichiers modifies non sauvegardes
- [ ] Historique des modifications (session-based undo stack)

### Phase 3 : Avance

- [ ] Vue diff avant/apres
- [ ] Integration git (status, commit depuis l'UI)
- [ ] Creation de nouveaux fichiers
- [ ] Mode responsive (overlay sur ecrans etroits)
- [ ] Raccourcis clavier (Ctrl+S pour sauver)
