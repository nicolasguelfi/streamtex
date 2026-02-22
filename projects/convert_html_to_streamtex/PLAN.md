# Plan de Conversion HTML → StreamTeX

## Decisions Validees

| Decision | Choix |
|----------|-------|
| **Organisation** | Collection multi-projets (1 sous-projet par cours, 14 projets) |
| **Blocs partages** | TOUS les blocs dans shared/blocks/ + LazyBlockRegistry |
| **Assignation cours** | 1 fichier `blocks.csv` par cours (liste ordonnee des noms de blocs) |
| **Blocs multi-cours** | Un bloc peut apparaitre dans plusieurs CSV (reference partagee) |
| **Couleurs** | Rationaliser (~15 familles) avec dual dark/light via systeme theme StreamTeX |
| **Pipeline** | Entierement automatise (scripts Python) |
| **Images** | Toutes dans shared/ (deduplication totale, reutilisation future) |

---

## 1. Architecture du Projet (Collection)

```
projects/convert_html_to_streamtex/
├── PLAN.md                              # Ce fichier
├── reqs.txt                             # Specifications
├── collection.toml                      # Configuration collection multi-projets
├── exports/                             # Source HTML (gitignored)
│   ├── .manifest.json
│   ├── html/  (359 blocs)
│   └── md/    (359 fichiers markdown)
│
├── shared/                              # Ressources partagees entre TOUS les projets
│   ├── blocks/                          # TOUS les 359 blocs convertis
│   │   ├── __init__.py                  # LazyBlockRegistry
│   │   ├── helpers.py                   # ProjectBlockHelperConfig partagee
│   │   ├── bck_ethics_overview.py
│   │   ├── bck_deep_learning_part_1.py
│   │   ├── bck_training_title_aiai_dlh.py
│   │   ├── bckcp_schedule_ai4ec.py
│   │   ├── ...                          # 359 fichiers bloc
│   │   └── sub/                         # Sous-blocs (blocs complexes decomposes)
│   │       ├── bck_ethics_overview__intro.py
│   │       └── ...
│   ├── custom/                          # Styles et themes partages
│   │   ├── styles.py                    # Palette unifiee + tous les styles
│   │   └── themes.py                    # Dictionnaires dark + light
│   └── static/
│       └── images/                      # TOUTES les images (dedupliquees)
│           ├── training_title_template.png
│           ├── ethics_banner.png
│           ├── diagram_cnn_architecture_001.png
│           └── ... (~714 images uniques)
│
├── courses/                             # 14 sous-projets (1 par cours)
│   ├── gai4as/
│   │   ├── book.py                      # Lit blocks.csv, ref shared blocks
│   │   ├── setup.py                     # PATH setup (shared + local)
│   │   ├── blocks.csv                   # LISTE ORDONNEE des blocs du cours
│   │   ├── custom/                      # Surcharges locales (optionnel)
│   │   │   ├── styles.py               # from shared.custom.styles import *
│   │   │   └── themes.py               # from shared.custom.themes import *
│   │   └── .streamlit/config.toml
│   ├── aiai/
│   │   ├── book.py
│   │   ├── blocks.csv                   # ← Vous fournissez ce fichier
│   │   └── ...
│   ├── ai4ei/
│   ├── idl/
│   ├── ai4lc/
│   ├── aies/
│   ├── chat4h/
│   ├── ai4ec/
│   ├── gaiwa/
│   ├── chat2d/
│   ├── ai4gov/
│   ├── chat1d/
│   ├── dlh/
│   └── ai4xx/
│
└── tools/                               # Pipeline de conversion automatisee
    ├── __init__.py
    ├── html_parser.py                   # HTML → structure intermediaire
    ├── style_extractor.py               # CSS inline → styles StreamTeX
    ├── image_manager.py                 # Deduplication + nommage Vision + registre
    ├── block_generator.py               # Structure → code Python StreamTeX
    ├── book_generator.py                # Lit blocks.csv → genere book.py
    ├── batch_convert.py                 # Orchestrateur principal
    ├── validate_blocks.py              # Verification post-generation
    └── image_registry.json              # Registre images (hash → nom semantique)
```

---

## 2. Systeme de Styles Partages (`shared/custom/styles.py`)

Le projet a **deux familles de blocs** avec des besoins typographiques distincts :

| Aspect | `bck_*` Presentation (slides) | `bckcp_*` Course Pack (document) |
|--------|-------------------------------|----------------------------------|
| **Usage** | Projection live, navigation slides | Lecture async etudiants, impression |
| **Titre principal** | 80-128pt | 20pt |
| **Texte courant** | 42pt (espace visuel) | 12pt (lecture dense) |
| **Densite** | 1 sujet/slide, beaucoup d'espace | 5-10 sections/page, compact |
| **Images** | Grandes (1486-1542px pleine largeur) | Petites (200-650px) |
| **Tables** | Rares, simples (2 cols) | Frequentes, complexes (6-8 cols) |
| **Couleurs** | Vibrantes, variees | Grises, fonctionnelles, accents ponctuels |

Les styles sont organises en 3 niveaux :
1. **Palette de couleurs** — partagee entre les 2 familles (style_id pour dark/light)
2. **Famille Presentation** (`pres.*`) — tailles grandes, espacement large
3. **Famille Document** (`doc.*`) — tailles compact, espacement serre

### 2.1 Palette Rationalisee (~15 familles de couleurs)

Chaque couleur a un `style_id` pour le systeme de theme dark/light.
Les valeurs de base (dans styles.py) sont les couleurs pour le mode **light**.
Le dictionnaire `dark` dans themes.py surcharge les couleurs pour le mode **dark**.

```python
from streamtex.styles import Style, StxStyles
from streamtex.styles.core import Text, Container

# ============================================================
# PALETTE DE COULEURS — 15 familles semantiques
# ============================================================
# Mapping depuis les 54 couleurs HTML d'origine :
#
# LIGHT VALUES (base)         | HTML sources consolidees
# forest_green  #274e13       | #274e13, #2f5a1b
# olive_green   #37761c       | #37761c, #188037
# light_green   #6aa84f       | #6aa84f, #93c47d
# link_blue     #1155cc       | #1155cc
# navy_blue     #0b5394       | #0b5394, #1b4587, #063763
# sky_blue      #3d85c6       | #3d85c6, #3c78d8
# teal          #134f5c       | #134f5c, #0c343d, #45818e
# bright_red    #cc0000       | #ff0000, #cc0000, #980000
# deep_red      #660000       | #660000, #5b0f00, #85200c
# salmon        #e06666       | #e06666, #ea9999, #cc4125
# orange        #e69137       | #ff9900, #ffa500, #e69137
# burnt_orange  #b45f06       | #b45f06, #783e04, #a65704
# gold          #7f6000       | #7f6000, #be9000, #947e01
# purple        #674ea7       | #9900ff, #674ea7
# dark_purple   #351b75       | #20124d, #351b75, #731b47, #4c1130
# gray          #666666       | #434343, #666666, #999999
#
# Couleurs NON migrees (theme-controlled):
# #000000 (noir defaut) → theme
# #ffffff (blanc defaut) → theme
# #222222 (near-black) → theme
# #d9d9d9 (light gray bg) → theme
# #00ff00, #87ff01, #ff00ff (neon) → usage unique, ignores
# ============================================================

class ColorsCustom:
    """Couleurs du projet. style_id permet le theme override."""
    forest_green  = Style("color:#274e13;", "clr_forest_green")
    olive_green   = Style("color:#37761c;", "clr_olive_green")
    light_green   = Style("color:#6aa84f;", "clr_light_green")
    link_blue     = Style("color:#1155cc;", "clr_link_blue")
    navy_blue     = Style("color:#0b5394;", "clr_navy_blue")
    sky_blue      = Style("color:#3d85c6;", "clr_sky_blue")
    teal          = Style("color:#134f5c;", "clr_teal")
    bright_red    = Style("color:#cc0000;", "clr_bright_red")
    deep_red      = Style("color:#660000;", "clr_deep_red")
    salmon        = Style("color:#e06666;", "clr_salmon")
    orange        = Style("color:#e69137;", "clr_orange")
    burnt_orange  = Style("color:#b45f06;", "clr_burnt_orange")
    gold          = Style("color:#7f6000;", "clr_gold")
    purple        = Style("color:#674ea7;", "clr_purple")
    dark_purple   = Style("color:#351b75;", "clr_dark_purple")
    gray          = Style("color:#666666;", "clr_gray")

class BgColorsCustom:
    """Background colors avec style_id pour theme override."""
    light_gray_bg = Style("background-color:#f5f5f5;", "bg_light_gray")
    accent_bg     = Style("background-color:rgba(17,85,204,0.08);", "bg_accent")
    warning_bg    = Style("background-color:rgba(204,0,0,0.08);", "bg_warning")
```

### 2.2 Famille A : Presentation (`pres.*`) — blocs `bck_*`

Pour les slides de presentation. Tailles grandes, espacement genereux,
couleurs vibrantes. Pensee pour la projection et la navigation slide-by-slide.

```python
class PresTitles:
    """Titres presentation : grandes tailles pour projection."""
    _base = Text.weights.bold_weight

    h1 = Style.create(_base + Text.sizes.Giant_size, "pres_h1")     # 128pt bold
    h2 = Style.create(_base + Text.sizes.Huge_size, "pres_h2")      # 96pt bold
    h3 = Style.create(_base + Text.sizes.huge_size, "pres_h3")      # 80pt bold
    h4 = Style.create(_base + Text.sizes.Large_size, "pres_h4")     # 48pt bold
    h5 = Style.create(_base + Text.sizes.large_size, "pres_h5")     # 32pt bold
    h6 = Style.create(_base + Text.sizes.big_size, "pres_h6")       # 24pt bold

class PresParas:
    """Paragraphes presentation : memes niveaux que titres, sans bold."""
    p_xl   = Style.create(Text.sizes.Huge_size, "pres_para_xl")     # 96pt
    p_lg   = Style.create(Text.sizes.huge_size, "pres_para_lg")     # 80pt
    p_md   = Style.create(Text.sizes.Large_size, "pres_para_md")    # 48pt
    p_sm   = Style.create(Text.sizes.large_size, "pres_para_sm")    # 32pt
    p_body = Style.create(Text.sizes.big_size, "pres_para_body")    # 24pt

class PresLinks:
    """Liens presentation avec taille adaptee."""
    default = Style.create(
        ColorsCustom.link_blue + Text.decors.underline_text, "pres_link")
    link_lg = Style.create(default + Text.sizes.huge_size, "pres_link_lg")   # 80pt
    link_md = Style.create(default + Text.sizes.Large_size, "pres_link_md")  # 48pt
    link_sm = Style.create(default + Text.sizes.large_size, "pres_link_sm")  # 32pt
    link_body = Style.create(default + Text.sizes.big_size, "pres_link_body")# 24pt

class PresContainers:
    """Conteneurs presentation : padding genereux."""
    slide       = Style("padding:36pt;", "pres_slide")
    section     = Style("padding:24px 0;", "pres_section")
    card        = Style("border-radius:16px;padding:32px;", "pres_card")

class PresGrids:
    """Grilles presentation : gaps larges."""
    gap = Style("gap:36px;", "pres_grid_gap")

class PresLists:
    """Listes presentation : items grands."""
    item = Style.create(Text.sizes.big_size, "pres_lst_item")       # 24pt

class PresTables:
    """Tables presentation : simples, 2 colonnes."""
    header = Style("padding:12px 16px;", "pres_tbl_header") + Text.weights.bold_weight
    cell   = Style("padding:12px 16px;", "pres_tbl_cell")

class Presentation:
    """Famille complete pour blocs bck_* (slides)."""
    titles     = PresTitles
    paragraphs = PresParas
    links      = PresLinks
    containers = PresContainers
    grids      = PresGrids
    lists      = PresLists
    tables     = PresTables
```

### 2.3 Famille B : Course Pack Document (`doc.*`) — blocs `bckcp_*`

Pour les syllabi et documents de cours. Tailles compactes optimisees pour la
lecture sur ecran individuel. Couleurs plus sobres. Dense et hierarchique.

```python
class DocTitles:
    """Titres document : tailles compactes pour lecture ecran."""
    _base = Text.weights.bold_weight

    h1 = Style.create(_base + Style("font-size:20pt;", "doc_h1_sz"), "doc_h1")  # 20pt bold
    h2 = Style.create(_base + Text.sizes.medium_size, "doc_h2")                  # 16pt bold
    h3 = Style.create(_base + Style("font-size:14pt;", "doc_h3_sz"), "doc_h3")  # 14pt bold
    h4 = Style.create(_base + Text.sizes.little_size, "doc_h4")                  # 12pt bold
    h5 = Style.create(Text.sizes.little_size, "doc_h5")                           # 12pt normal
    h6 = Style.create(Text.sizes.small_size, "doc_h6")                            # 8pt normal

class DocParas:
    """Paragraphes document : lecture optimisee."""
    p_lg   = Style.create(Style("font-size:20pt;", "doc_para_lg_sz"), "doc_para_lg")  # 20pt
    p_md   = Style.create(Text.sizes.medium_size, "doc_para_md")                       # 16pt
    p_sm   = Style.create(Style("font-size:14pt;", "doc_para_sm_sz"), "doc_para_sm")  # 14pt
    p_body = Style.create(Text.sizes.little_size, "doc_para_body")                     # 12pt

class DocLinks:
    """Liens document : taille lecture standard."""
    default   = Style.create(
        ColorsCustom.link_blue + Text.decors.underline_text, "doc_link")
    link_lg   = Style.create(default + Style("font-size:20pt;", "_dlk_lg"), "doc_link_lg")
    link_md   = Style.create(default + Text.sizes.medium_size, "doc_link_md")        # 16pt
    link_body = Style.create(default + Text.sizes.little_size, "doc_link_body")      # 12pt

class DocContainers:
    """Conteneurs document : padding serre, dense."""
    page       = Style("padding:16px;", "doc_page")
    section    = Style("padding:8px 0;", "doc_section")
    card       = Style("border-radius:8px;padding:16px;", "doc_card")
    bordered   = Style("border:1px solid;border-radius:4px;padding:12px;", "doc_bordered")

class DocGrids:
    """Grilles document : gaps serres."""
    gap = Style("gap:12px;", "doc_grid_gap")

class DocLists:
    """Listes document : items compacts."""
    item       = Style.create(Text.sizes.little_size, "doc_lst_item")      # 12pt
    item_small = Style.create(Text.sizes.small_size, "doc_lst_item_sm")    # 8pt

class DocTables:
    """Tables document : cellules compactes pour tableaux denses (6-8 cols)."""
    header = Style("padding:6px 8px;", "doc_tbl_header") + Text.weights.bold_weight
    cell   = Style("padding:6px 8px;", "doc_tbl_cell")
    border = Style("border:1px solid;", "doc_tbl_border")

class Document:
    """Famille complete pour blocs bckcp_* (course pack / syllabus)."""
    titles     = DocTitles
    paragraphs = DocParas
    links      = DocLinks
    containers = DocContainers
    grids      = DocGrids
    lists      = DocLists
    tables     = DocTables
```

### 2.4 Assemblage final

```python
# === Assemblage ===
class Custom:
    colors      = ColorsCustom
    bg_colors   = BgColorsCustom
    pres        = Presentation     # s.project.pres.titles.h1, s.project.pres.links.link_md
    doc         = Document         # s.project.doc.titles.h1, s.project.doc.links.link_body

class Styles(StxStyles):
    project = Custom
```

**Usage dans les blocs** :
```python
# Bloc bck_* (presentation)
st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Deep Learning")
st_write(s.project.pres.paragraphs.p_body, "Introduction aux reseaux de neurones")
st_write(s.project.pres.links.link_md, "Voir la documentation", link=URL)

# Bloc bckcp_* (course pack)
st_write(s.project.doc.titles.h1, "5. References")
st_write(s.project.doc.paragraphs.p_body, "McKinsey report on AI impact...")
st_write(s.project.doc.links.link_body, "link", link=URL)
```

### 2.5 Themes Dark/Light (`shared/custom/themes.py`)

4 themes au total : `pres_dark`, `pres_light`, `doc_dark`, `doc_light`.
Les couleurs sont partagees. Les surcharges de taille/espacement sont par famille.

```python
# ============================================================
# Couleurs partagees (base = light)
# ============================================================
_colors_dark = {
    # Greens (plus lumineux sur fond sombre)
    "clr_forest_green":  "color:#7bc96f;",
    "clr_olive_green":   "color:#8fd17e;",
    "clr_light_green":   "color:#a8d99c;",
    # Blues
    "clr_link_blue":     "color:#6db3f8;",
    "clr_navy_blue":     "color:#5ba3e6;",
    "clr_sky_blue":      "color:#7dc4f5;",
    "clr_teal":          "color:#5fb8c9;",
    # Reds
    "clr_bright_red":    "color:#ff6b6b;",
    "clr_deep_red":      "color:#e05555;",
    "clr_salmon":        "color:#f09090;",
    # Oranges
    "clr_orange":        "color:#f5a623;",
    "clr_burnt_orange":  "color:#e8a040;",
    "clr_gold":          "color:#d4a830;",
    # Purples
    "clr_purple":        "color:#a78bfa;",
    "clr_dark_purple":   "color:#8b7ccf;",
    # Gray
    "clr_gray":          "color:#a0a0a0;",
    # Backgrounds
    "bg_light_gray":     "background-color:rgba(255,255,255,0.06);",
    "bg_accent":         "background-color:rgba(109,179,248,0.12);",
    "bg_warning":        "background-color:rgba(255,107,107,0.12);",
}

# ============================================================
# 4 themes
# ============================================================

# Presentation light (base = styles.py defaults)
pres_light = {}

# Presentation dark
pres_dark = {
    **_colors_dark,
}

# Document light (base = styles.py defaults)
doc_light = {}

# Document dark
doc_dark = {
    **_colors_dark,
    # Le document peut necessiter des ajustements specifiques
    # pour la lisibilite en mode sombre a taille 12pt
    "doc_tbl_border": "border:1px solid rgba(255,255,255,0.2);",
    "doc_bordered":   "border:1px solid rgba(255,255,255,0.2);"
                      "border-radius:4px;padding:12px;",
}
```

**Usage dans book.py** :
```python
# Cours presentation (bck_*)
from shared.custom.themes import pres_dark
sts.theme = pres_dark

# Cours document (bckcp_*)
from shared.custom.themes import doc_dark
sts.theme = doc_dark
```

---

## 3. Pipeline de Conversion Automatisee (`tools/`)

### 3.1 Vue d'ensemble du pipeline

Le pipeline a 2 etapes independantes :

**Etape A : Conversion des blocs** (automatisee, executee une fois)
```
exports/html/bck_*/index.html
        │
        ▼
  ┌─────────────────┐
  │  html_parser.py  │  Parse HTML → ParsedBlock (AST simplifie)
  └────────┬────────┘
           │
           ▼
  ┌──────────────────────┐
  │  style_extractor.py  │  Map CSS inline → styles StreamTeX
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  image_manager.py    │  Deduplique, renomme, copie → shared/static/images/
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  block_generator.py  │  Genere fichier .py → shared/blocks/
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  batch_convert.py    │  Orchestre tout (359 blocs → shared/blocks/)
  └──────────────────────┘
```

**Etape B : Generation des projets-cours** (re-executable a chaque mise a jour CSV)
```
courses/{cours}/blocks.csv        # Vous fournissez : liste ordonnee des blocs
        │
        ▼
  ┌──────────────────────┐
  │  book_generator.py   │  Lit blocks.csv → genere book.py pour le cours
  └──────────────────────┘
        │
        ▼
  courses/{cours}/book.py         # Charge les blocs depuis shared/ dans l'ordre CSV
```

**Avantage** : Modifier l'ordre ou le contenu d'un cours = editer son `blocks.csv` + re-executer `book_generator.py`. Pas besoin de reconvertir les blocs.

### 3.2 `html_parser.py` — Analyseur HTML

**Entree** : `index.html` (export Google Docs)
**Sortie** : `ParsedBlock` (structure intermediaire)

```python
from dataclasses import dataclass, field
from bs4 import BeautifulSoup

@dataclass
class ParsedSpan:
    """Un segment de texte avec style inline."""
    text: str
    color: str | None = None        # hex color
    font_size: str | None = None    # e.g. "48pt"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    link: str | None = None

@dataclass
class ParsedElement:
    """Un element HTML (heading, paragraph, image, table, list)."""
    tag: str                             # h1-h6, p, img, table, ul, ol, hr
    spans: list[ParsedSpan] = field(default_factory=list)
    children: list["ParsedElement"] = field(default_factory=list)
    # Image specifique
    image_src: str | None = None
    image_width: str | None = None
    image_height: str | None = None
    # Table specifique
    rows: list[list["ParsedElement"]] = field(default_factory=list)

@dataclass
class ParsedBlock:
    """Resultat complet du parsing d'un bloc HTML."""
    name: str
    elements: list[ParsedElement]
    all_colors: set[str]             # Toutes les couleurs trouvees
    all_font_sizes: set[str]         # Toutes les tailles
    all_images: list[str]            # Chemins images
    has_tables: bool = False
    has_lists: bool = False
    estimated_complexity: str = "simple"  # simple|medium|complex
```

### 3.3 `style_extractor.py` — Mapping CSS → StreamTeX

```python
# Table de mapping couleur HTML → style projet
COLOR_MAP = {
    "#274e13": "s.project.colors.forest_green",
    "#2f5a1b": "s.project.colors.forest_green",
    "#37761c": "s.project.colors.olive_green",
    "#188037": "s.project.colors.olive_green",
    "#6aa84f": "s.project.colors.light_green",
    "#93c47d": "s.project.colors.light_green",
    "#1155cc": "s.project.colors.link_blue",
    "#0b5394": "s.project.colors.navy_blue",
    "#1b4587": "s.project.colors.navy_blue",
    "#063763": "s.project.colors.navy_blue",
    "#3d85c6": "s.project.colors.sky_blue",
    "#3c78d8": "s.project.colors.sky_blue",
    "#134f5c": "s.project.colors.teal",
    "#0c343d": "s.project.colors.teal",
    "#45818e": "s.project.colors.teal",
    "#ff0000": "s.project.colors.bright_red",
    "#cc0000": "s.project.colors.bright_red",
    "#980000": "s.project.colors.bright_red",
    "#660000": "s.project.colors.deep_red",
    "#5b0f00": "s.project.colors.deep_red",
    "#85200c": "s.project.colors.deep_red",
    "#e06666": "s.project.colors.salmon",
    "#ea9999": "s.project.colors.salmon",
    "#cc4125": "s.project.colors.salmon",
    "#a61b00": "s.project.colors.salmon",
    "#ff9900": "s.project.colors.orange",
    "#ffa500": "s.project.colors.orange",
    "#e69137": "s.project.colors.orange",
    "#b45f06": "s.project.colors.burnt_orange",
    "#783e04": "s.project.colors.burnt_orange",
    "#a65704": "s.project.colors.burnt_orange",
    "#7f6000": "s.project.colors.gold",
    "#be9000": "s.project.colors.gold",
    "#947e01": "s.project.colors.gold",
    "#9900ff": "s.project.colors.purple",
    "#674ea7": "s.project.colors.purple",
    "#20124d": "s.project.colors.dark_purple",
    "#351b75": "s.project.colors.dark_purple",
    "#731b47": "s.project.colors.dark_purple",
    "#4c1130": "s.project.colors.dark_purple",
    "#a64d78": "s.project.colors.dark_purple",
    "#434343": "s.project.colors.gray",
    "#666666": "s.project.colors.gray",
    "#999999": "s.project.colors.gray",
}

# Table de mapping taille → style
SIZE_MAP = {
    range(128, 257): "s.Giant",    # 128pt
    range(96, 128):  "s.Huge",     # 96pt
    range(80, 96):   "s.huge",     # 80pt
    range(64, 80):   "s.LARGE",    # 64pt
    range(48, 64):   "s.Large",    # 48pt
    range(32, 48):   "s.large",    # 32pt
    range(24, 32):   "s.big",      # 24pt
    range(16, 24):   "s.medium",   # 16pt
    range(12, 16):   "s.little",   # 12pt (default)
    range(8, 12):    "s.small",    # 8pt
    range(0, 8):     "s.tiny",     # 4pt
}

# Mapping heading tag → style titre projet
HEADING_MAP = {
    "h1": "s.project.titles.h1",
    "h2": "s.project.titles.h2",
    "h3": "s.project.titles.h3",
    "h4": "s.project.titles.h4",
    "h5": "s.project.titles.h5",
    "h6": "s.project.titles.h6",
}
```

### 3.4 `image_manager.py` — Gestion des images

Fonctionnalites :
1. **Inventaire** : Scan toutes les images, calcule MD5
2. **Deduplication** : Identifie les doublons par hash (714 uniques sur 911)
3. **Nommage par Vision** : Appelle Claude Haiku Vision pour analyser chaque image
   unique et generer un nom semantique `{type}_{sous-type}_{tags}.png`
4. **Registre** : `image_registry.json` avec mapping hash → nom + origines
5. **Deploiement** : Copie les images dedupliquees et renommees dans `shared/static/images/`
6. **Mise a jour refs** : `update_image_refs.py` pour propager les renommages dans les blocs

Voir section 5 pour les details du nommage et le pipeline Vision.

### 3.5 `blocks.csv` — Fichier de definition d'un cours

Chaque cours a un fichier `blocks.csv` dans son dossier. Ce fichier est fourni par
l'utilisateur et contient la liste ordonnee des noms exacts des blocs du cours.

**Format** :
```csv
block_name
bck_training_title_gai4as
bck_welcome_screen_gai4as
bck_content_session_2_gai4as
bck_ethics_overview
bck_practice_gai4as_project
bckcp_references_gai4as
```

**Regles** :
- Une colonne : `block_name`
- L'ordre des lignes = l'ordre des blocs dans le `book.py`
- Les noms doivent correspondre exactement aux noms des blocs dans `shared/blocks/`
- Un meme bloc peut apparaitre dans plusieurs fichiers CSV de cours differents
- Lignes vides et lignes commencant par `#` sont ignorees (commentaires)

**Exemple avec commentaires** :
```csv
block_name
# === Titre et accueil ===
bck_training_title_gai4as
bck_welcome_screen_gai4as

# === Session 2 ===
bck_content_session_2_gai4as
bck_ethics_overview
bck_practice_gai4as_s2

# === Session 3 ===
bck_content_session_3_gai4as
bck_deep_learning_part_1
```

**Detection automatique du type de famille** :
Le `book_generator.py` determine automatiquement quel theme appliquer :
- Si le CSV contient majoritairement des `bck_*` → theme `pres_dark` (presentation)
- Si le CSV contient majoritairement des `bckcp_*` → theme `doc_dark` (document)
- Si mixte → le book.py gere les deux familles

Chaque bloc sait quelle famille de styles utiliser grace a son prefixe :
- `bck_*` → `s.project.pres.*`
- `bckcp_*` → `s.project.doc.*`

### 3.6 `book_generator.py` — Generateur de book.py a partir du CSV

Lit le `blocks.csv` d'un cours et genere le `book.py` correspondant.

```python
import csv
from pathlib import Path

def generate_book_py(course_dir: Path, shared_blocks_path: Path) -> str:
    """Genere book.py pour un cours a partir de son blocks.csv."""
    csv_file = course_dir / "blocks.csv"
    block_names = []

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["block_name"].strip()
            if name and not name.startswith("#"):
                block_names.append(name)

    # Generer le code book.py
    lines = [
        'import streamlit as st',
        'import setup',
        'from streamtex import st_book, TOCConfig, MarkerConfig, LazyBlockRegistry',
        'import streamtex.styles as sts',
        'from shared.custom.styles import Styles as s',
        'from shared.custom.themes import dark',
        '',
        'st.set_page_config(',
        f'    page_title="{course_dir.name.upper()}",',
        '    layout="wide",',
        '    initial_sidebar_state="expanded"',
        ')',
        '',
        'st.sidebar.title("Table of Contents")',
        '',
        '# Theme',
        'sts.theme = dark',
        '',
        '# Charger les blocs partages',
        f'shared = LazyBlockRegistry(["{shared_blocks_path}"])',
        '',
        '# Liste des blocs (ordre defini par blocks.csv)',
        'module_list = [',
    ]

    for name in block_names:
        lines.append(f'    shared.{name},')

    lines += [
        ']',
        '',
        'toc = TOCConfig(',
        '    numerate_titles=False,',
        '    toc_position=0,',
        ')',
        '',
        'marker = MarkerConfig(',
        '    auto_marker_on_toc=1,',
        '    show_nav_ui=True,',
        '    next_keys=["PageDown"],',
        '    prev_keys=["PageUp"],',
        ')',
        '',
        'st_book(module_list, toc_config=toc, marker_config=marker, paginate=True)',
    ]

    return "\n".join(lines)
```

**Usage** :
```bash
# Generer book.py pour un cours
uv run python tools/book_generator.py courses/gai4as

# Generer book.py pour TOUS les cours
uv run python tools/book_generator.py --all

# Re-generer apres modification d'un blocks.csv
uv run python tools/book_generator.py courses/aiai
```

**Avantage** : Pour reorganiser un cours, il suffit d'editer `blocks.csv` et
de re-executer `book_generator.py`. Aucune reconversion des blocs necessaire.

### 3.7 `block_generator.py` — Generation de code StreamTeX

Genere un fichier .py complet a partir d'un `ParsedBlock` :

```python
def generate_block(parsed: ParsedBlock, image_registry: dict) -> str:
    """Genere le code Python StreamTeX pour un bloc."""
    lines = []

    # 1. Imports standard
    lines.append("import streamlit as st")
    lines.append("from streamtex import *")
    lines.append("import streamtex as stx")
    lines.append("from streamtex.styles import Style as ns, StyleGrid as sg")
    lines.append("from streamtex.enums import Tags as t, ListTypes as lt")
    lines.append("from custom.styles import Styles as s")
    lines.append("")

    # 2. BlockStyles avec color-mapping
    lines.append("class BlockStyles:")
    lines.append('    """Styles locaux a ce bloc."""')
    lines.append(f"    # Color mapping: {generate_color_mapping(parsed)}")
    lines.append(f"    # Dropped colors: {generate_dropped_colors(parsed)}")
    # Ajouter styles locaux si necessaire
    lines.append("    pass")
    lines.append("")
    lines.append("bs = BlockStyles")
    lines.append("")

    # 3. build() function
    lines.append("def build():")
    for element in parsed.elements:
        lines.extend(generate_element(element, image_registry))

    return "\n".join(lines)
```

### 3.8 `batch_convert.py` — Orchestrateur principal

Convertit TOUS les blocs HTML vers shared/blocks/. L'assignation aux cours est
faite separement via les fichiers blocks.csv et book_generator.py.

```python
def main():
    """Pipeline complet de conversion HTML → shared/blocks/."""
    exports_dir = Path("exports/html")
    output_dir  = Path(".")

    # Phase 1: Inventaire et deduplication images
    print("Phase 1: Image inventory & deduplication...")
    registry = build_image_inventory(exports_dir)
    deploy_images(registry, output_dir / "shared" / "static" / "images")
    save_registry(registry, output_dir / "tools" / "image_registry.json")
    print(f"  {len(registry)} images uniques deployees")

    # Phase 2: Parse tous les blocs HTML
    print("Phase 2: Parsing HTML blocks...")
    blocks = {}
    for block_dir in sorted(exports_dir.iterdir()):
        if block_dir.is_dir():
            html_file = block_dir / "index.html"
            if html_file.exists():
                blocks[block_dir.name] = parse_html(html_file)

    # Phase 3: Generer les fichiers StreamTeX dans shared/blocks/
    print("Phase 3: Generating StreamTeX blocks...")
    dest_dir = output_dir / "shared" / "blocks"
    dest_dir.mkdir(parents=True, exist_ok=True)
    stats = {"simple": 0, "medium": 0, "complex": 0, "decomposed": 0}

    for block_name, parsed in blocks.items():
        code = generate_block(parsed, registry)
        (dest_dir / f"{block_name}.py").write_text(code)
        stats[parsed.estimated_complexity] += 1

        # Decomposer les blocs complexes en sous-blocs si necessaire
        if should_decompose(parsed):
            sub_blocks = decompose_block(parsed, registry)
            sub_dir = dest_dir / "sub"
            sub_dir.mkdir(exist_ok=True)
            for sub_name, sub_code in sub_blocks.items():
                (sub_dir / f"{sub_name}.py").write_text(sub_code)
            stats["decomposed"] += 1

    # Phase 4: Generer __init__.py pour le registre
    generate_registry_init(dest_dir)

    # Phase 5: Rapport
    print(f"\nDone! {len(blocks)} blocks converted to shared/blocks/")
    print(f"  Simple: {stats['simple']}")
    print(f"  Medium: {stats['medium']}")
    print(f"  Complex: {stats['complex']}")
    print(f"  Decomposed into sub-blocks: {stats['decomposed']}")
    print(f"\nNext steps:")
    print(f"  1. Create blocks.csv for each course in courses/{{course}}/")
    print(f"  2. Run: uv run python tools/book_generator.py --all")
```

---

## 4. Skills/Commandes Claude

### 4.1 Nouvelle skill : `/convert-html-block`

**But** : Convertir un bloc HTML specifique en StreamTeX (pour corrections manuelles ou blocs complexes).

**Workflow** :
1. Lit le HTML source du bloc
2. Lit les styles projet (shared/custom/styles.py)
3. Analyse couleurs, polices, layout
4. Genere le code StreamTeX
5. Applique les regles de migration (color fidelity, inline text, etc.)
6. Second-pass verification

### 4.2 Nouvelle skill : `/convert-html-batch`

**But** : Lancer le pipeline de conversion Python.

**Arguments** :
- `--all` : Convertir tous les blocs HTML → shared/blocks/
- `--filter "bck_title_*"` : Filtrer par pattern de nom
- `--dry-run` : Simuler sans ecrire
- `--force` : Ecraser les blocs existants

### 4.3 Nouvelle skill : `/generate-course`

**But** : Generer le book.py d'un cours a partir de son blocks.csv.

**Arguments** :
- `<course>` : Nom du cours (ex: gai4as)
- `--all` : Generer pour tous les cours qui ont un blocks.csv

**Usage** :
```
/generate-course gai4as
/generate-course --all
```

### 4.3 Nouvelle skill : `/audit-conversion`

**But** : Verifier la qualite d'une conversion.

**Checks** :
- Toutes les couleurs non-default migrees
- Images renommees et copiees
- Pas de HTML brut
- Inline mixed-style utilise tuples
- Font size dans les liens
- Second-pass checklist complete

### 4.4 Agent : `html-migration-agent`

**But** : Agent autonome pour blocs complexes (multi-pass avec verification).

---

## 5. Gestion des Images

### 5.1 Emplacement unique

Toutes les images dans `shared/static/images/`, nommees semantiquement.

```
shared/static/images/
├── animal_frog_orange-wall.png                  # Break slide (grenouille)
├── animal_koala_sleeping-tree.png               # Break slide (koala)
├── animal_dolphins_ocean-jump.png               # Break slide (dauphins)
├── banner_training-title_university-logo.png    # Template titre formation (27 blocs)
├── banner_ethics_eu-ai-act.png                  # Banniere ethique EU
├── diagram_cnn_architecture-layers.png          # Schema CNN
├── diagram_neuron_activation-function.png       # Schema neurone
├── screenshot_colab_notebook-setup.png          # Capture Colab
├── screenshot_wordpress_dashboard-main.png      # Capture WordPress
├── icon_tensorflow_logo.png                     # Logo TensorFlow
├── chart_ai-impact_jobs-by-sector.png           # Graphique McKinsey
└── ... (~714 images uniques)
```

### 5.2 Convention de nommage — Analyse par Vision

Le nommage est genere automatiquement par un **modele de vision** (Claude)
qui analyse le contenu de chaque image et produit un nom en 3 parties :

**Format** : `{type}_{sous-type}_{tags}.ext`

| Partie | Description | Exemples |
|--------|-------------|----------|
| **type** | Categorie principale | `animal`, `diagram`, `screenshot`, `banner`, `icon`, `chart`, `photo`, `logo`, `illustration` |
| **sous-type** | Sujet specifique | `frog`, `cnn`, `colab`, `training-title`, `tensorflow` |
| **tags** | Details distinctifs (1-3 mots, separes par `-`) | `orange-wall`, `architecture-layers`, `notebook-setup` |

**Regles** :
- Tout en minuscules, mots separes par `-` dans chaque partie
- Parties separees par `_`
- Tags suffisamment distinctifs pour differencier des images similaires
- En anglais uniquement
- Pas de numeros sequentiels (sauf si necessaire pour lever l'ambiguite)

**Exemples complets** :
```
animal_frog_orange-wall.png
animal_koala_sleeping-tree.png
diagram_cnn_architecture-layers.png
diagram_neuron_weighted-sum.png
screenshot_colab_notebook-setup.png
screenshot_wordpress_plugin-install.png
banner_training-title_university-logo.png
chart_ai-impact_jobs-by-sector.png
icon_tensorflow_logo.png
photo_classroom_students-laptops.png
illustration_backpropagation_gradient-flow.png
```

### 5.3 Pipeline de nommage dans `image_manager.py`

```python
import anthropic
import base64

def analyze_image_for_naming(image_path: Path) -> str:
    """Utilise Claude Vision pour generer un nom semantique."""
    client = anthropic.Anthropic()

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    mime = "image/png"  # Toutes les images sont PNG

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Haiku suffit pour cette tache
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": mime, "data": image_data},
                },
                {
                    "type": "text",
                    "text": (
                        "Generate a filename for this image using this format: "
                        "{type}_{subtype}_{tags}\n"
                        "- type: category (animal, diagram, screenshot, banner, icon, "
                        "chart, photo, logo, illustration)\n"
                        "- subtype: specific subject (1 word, lowercase)\n"
                        "- tags: 1-3 distinctive words separated by hyphens\n"
                        "Examples: animal_frog_orange-wall, diagram_cnn_architecture-layers\n"
                        "Reply with ONLY the filename, no extension, no explanation."
                    ),
                },
            ],
        }],
    )
    return response.content[0].text.strip().lower()
```

**Deduplication + nommage** :
1. Calculer MD5 de toutes les images
2. Pour chaque hash unique, analyser UNE image via Vision
3. Stocker le nom genere dans le registre
4. Si le nom genere est ambigu ou duplique, ajouter un suffixe numerique (`_02`)

**Cout estime** : ~714 appels Haiku Vision ≈ $0.50 (tres faible)

### 5.4 Registre (`tools/image_registry.json`)

```json
{
  "629bf6c79d8e7f18...": {
    "name": "banner_training-title_university-logo.png",
    "type": "banner",
    "subtype": "training-title",
    "tags": "university-logo",
    "originals": [
      {"block": "bck_training_title_aiai_dlh", "file": "image1.png"},
      {"block": "bck_training_title_chat_dlh", "file": "image1.png"},
      {"block": "bck_training_title_gai4as", "file": "image1.png"}
    ],
    "width": 1600,
    "height": 1052,
    "size_bytes": 1547823
  },
  "4e475247fed6d433...": {
    "name": "banner_ethics_eu-ai-act-framework.png",
    "type": "banner",
    "subtype": "ethics",
    "tags": "eu-ai-act-framework",
    "originals": [
      {"block": "bck_ethics_overview", "file": "image3.png"},
      {"block": "bck_focus_aies", "file": "image1.png"}
    ],
    "width": 1600,
    "height": 900,
    "size_bytes": 892345
  }
}
```

### 5.5 Script de mise a jour des references

Si une image est renommee :
1. Mettre a jour `image_registry.json` (nouveau nom)
2. Executer `tools/update_image_refs.py` qui :
   - Scanne tous les fichiers `.py` dans `shared/blocks/`
   - Trouve les `st_image(uri="ancien_nom.png")`
   - Remplace par le nouveau nom
   - Rapporte les modifications

```bash
uv run python tools/update_image_refs.py --old "banner_ethics_eu.png" --new "banner_ethics_eu-ai-act.png"
```

---

## 6. Decomposition en Sous-Blocs

Pour les blocs complexes (> ~150 lignes de code genere ou > 10 images) :

### Convention de nommage
```
blocks/bck_ethics_overview.py              # Bloc parent (compositing)
blocks/sub/bck_ethics_overview__intro.py    # Sous-bloc introduction
blocks/sub/bck_ethics_overview__eu.py       # Sous-bloc cadre EU
blocks/sub/bck_ethics_overview__us.py       # Sous-bloc cadre US
```

### Pattern du bloc parent
```python
import streamtex as stx
from streamtex import st_include

bck_intro = stx.load_atomic_block("bck_ethics_overview__intro", __file__)
bck_eu    = stx.load_atomic_block("bck_ethics_overview__eu", __file__)
bck_us    = stx.load_atomic_block("bck_ethics_overview__us", __file__)

class BlockStyles:
    pass

def build():
    st_include(bck_intro)
    st_include(bck_eu)
    st_include(bck_us)
```

### Criteres de decomposition automatique
Le script decide de decomposer si :
- Le HTML source > 20 KB
- Plus de 10 images
- Plus de 5 tables
- Plus de 3 niveaux de titres distincts

---

## 7. Phases de Realisation

### Phase 0 : Infrastructure (fondations)
**Livrable** : Structure projet fonctionnelle, styles, images

1. Creer la structure de dossiers (collection.toml, shared/, courses/, tools/)
2. Implementer `shared/custom/styles.py` (palette, titres, paragraphes, liens, etc.)
3. Implementer `shared/custom/themes.py` (dark + light)
4. Implementer `tools/image_manager.py` (inventaire, deduplication, registre)
5. Executer la deduplication images → deployer dans shared/static/images/
6. Creer les skills Claude (/convert-html-block, /convert-html-batch, /generate-course, /audit-conversion)
7. Tester manuellement avec 5 blocs (1 titre, 1 contenu, 1 table, 1 liste, 1 image)

### Phase 1 : Pipeline de conversion (Etape A)
**Livrable** : Scripts Python fonctionnels + 359 blocs dans shared/blocks/

1. Implementer `tools/html_parser.py`
2. Implementer `tools/style_extractor.py`
3. Implementer `tools/block_generator.py`
4. Implementer `tools/batch_convert.py`
5. Tester sur 20 blocs representatifs (couvrant toutes les complexites)
6. Affiner les mappings couleurs/tailles si necessaire
7. Executer `batch_convert.py --all` → 359 blocs dans shared/blocks/
8. Verification automatisee (validate_blocks.py)

### Phase 2 : Definition des cours (Etape B)
**Livrable** : 14 projets-cours fonctionnels

1. Implementer `tools/book_generator.py`
2. **Vous fournissez** les 14 fichiers `blocks.csv` (un par cours)
3. Executer `book_generator.py --all` → genere les 14 book.py
4. Generer setup.py + .streamlit/config.toml pour chaque cours
5. Tester chaque cours : `uv run streamlit run courses/{cours}/book.py`

### Phase 3 : Validation et QA
**Livrable** : Projet deployable

1. Lancer chaque cours individuellement
2. Comparaison visuelle HTML vs StreamTeX sur 10% des blocs
3. Verification couleurs dark/light mode
4. Verification images (pas de 404, dimensions correctes)
5. Corrections finales (via `/convert-html-block` pour les blocs problematiques)

### Workflow Iteratif Post-Livraison

Apres la livraison initiale, modifier un cours est simple :
```
1. Editer courses/{cours}/blocks.csv  (ajouter/supprimer/reordonner des lignes)
2. uv run python tools/book_generator.py courses/{cours}
3. uv run streamlit run courses/{cours}/book.py  (tester)
```

Pour ajouter un nouveau cours :
```
1. mkdir courses/{nouveau_cours}
2. Creer courses/{nouveau_cours}/blocks.csv
3. uv run python tools/book_generator.py courses/{nouveau_cours}
```

---

## 8. Estimation du Volume

| Element | Quantite |
|---------|----------|
| Blocs dans shared/blocks/ | 359 fichiers .py |
| Sous-blocs (complexes decomposes) | ~50-80 fichiers .py |
| Images uniques | ~714 fichiers PNG |
| Fichiers blocks.csv (fournis par vous) | 14 |
| Cours (book.py generes) | 14 |
| Scripts outils | 7 fichiers Python |
| Styles/themes partages | 2 fichiers (styles.py + themes.py) |
| Skills Claude | 4 (/convert-html-block, /convert-html-batch, /generate-course, /audit-conversion) |
| **Total fichiers generes** | **~450-470 fichiers Python** |
