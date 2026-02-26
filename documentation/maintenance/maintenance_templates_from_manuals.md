# Templates générés depuis les manuels — Plan de développement

> **Date** : 2026-02-26
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 1.0
> **Statut** : Planning

---

## Table des matières

1. [Contexte et motivation](#1-contexte-et-motivation)
2. [Objectifs](#2-objectifs)
3. [Diagnostic de l'existant](#3-diagnostic-de-lexistant)
4. [Architecture cible](#4-architecture-cible)
5. [Convention d'extractibilité des manuels](#5-convention-dextractibilité-des-manuels)
6. [Phase 1 — Audit et normalisation des manuels](#6-phase-1--audit-et-normalisation-des-manuels)
7. [Phase 2 — Script de génération](#7-phase-2--script-de-génération)
8. [Phase 3 — Adaptation des slash commands](#8-phase-3--adaptation-des-slash-commands)
9. [Phase 4 — Suppression des anciens templates](#9-phase-4--suppression-des-anciens-templates)
10. [Phase 5 — Validation et documentation](#10-phase-5--validation-et-documentation)
11. [Fichiers impactés](#11-fichiers-impactés)
12. [Risques et mitigations](#12-risques-et-mitigations)
13. [Critères de validation](#13-critères-de-validation)
14. [Annexe A — Matrice de couverture API actuelle](#annexe-a--matrice-de-couverture-api-actuelle)
15. [Annexe B — Exemple de block extrait](#annexe-b--exemple-de-block-extrait)
16. [Annexe C — Checklist d'exécution](#annexe-c--checklist-dexécution)

---

## 1. Contexte et motivation

### Problème

Le projet maintient aujourd'hui **trois sources distinctes** pour la même information :

| Source | Rôle | Couverture API |
|--------|------|----------------|
| `documentation/template_project/` | Template starter (projet simple) | ~40% |
| `documentation/template_collection/` | Template starter (collection) | ~10% |
| `documentation/manuals/` (intro + advanced + collection) | Documentation interactive | ~95% |

Cette duplication crée plusieurs problèmes :

1. **Divergence** : les templates ne reflètent pas les dernières features (ex. : `BannerConfig`, `st_mermaid()`, `add_zoom_options()` absents du template)
2. **Double maintenance** : chaque nouvelle feature doit être ajoutée au manuel ET au template
3. **Incohérence** : le template contient un bug (`show_tip` importé mais non défini dans `helpers.py`)
4. **Incomplétude** : un utilisateur qui démarre depuis le template ne découvre pas ~60% de l'API

### Solution retenue

**Option C** : les manuels deviennent la source unique de vérité. Un script génère les templates à partir d'eux.

### Bénéfices attendus

- **Zéro divergence** : les templates reflètent toujours l'état des manuels
- **Maintenance unique** : ajouter une feature au manuel suffit — le template suit
- **Couverture garantie** : par construction, le template couvre tout ce que le manuel illustre
- **Évolutivité** : plus la librairie grandit, plus les manuels s'enrichissent, plus les templates sont complets

---

## 2. Objectifs

| # | Objectif | Critère de succès |
|---|----------|-------------------|
| O1 | Les manuels sont la source unique de vérité pour les templates | Aucun contenu de template n'est maintenu manuellement |
| O2 | Un script génère 3 templates (simple, avancé, collection) | `uv run python scripts/generate_templates.py` produit 3 dossiers fonctionnels |
| O3 | Chaque template généré est directement exécutable | `uv run streamlit run templates/*/book.py` démarre sans erreur |
| O4 | Les slash commands utilisent les templates générés | `/project:project-new` copie depuis `documentation/templates/template_simple/` |
| O5 | Les anciens templates manuels sont supprimés | `documentation/template_project/` et `documentation/template_collection/` n'existent plus |

---

## 3. Diagnostic de l'existant

### 3.1 Template projet — features couvertes

```
✅ st_write (texte simple + tuples inline)
✅ st_image (local + URL + clickable)
✅ st_code (language, line_numbers, wrap, styled box)
✅ st_list (ordered, unordered, nested)
✅ st_block, st_span (containers)
✅ st_grid + StyleGrid (CSS grid + cell styling)
✅ st_space, st_br (espacement)
✅ st_overlay + st_include (overlays, composition)
✅ Style composition (+, Style.create())
✅ StxStyles (palettes de styles)
✅ Interactivité (st.button, st.toggle, st.slider, st.color_picker)
✅ BlockStyles + build() (pattern bloc)
✅ ProjectBlockRegistry (lazy loading)
✅ custom/styles.py (hiérarchie de styles projet)
✅ custom/themes.py (thème sombre)
✅ Separator block
✅ Sub-block inclusion (st_include)
```

### 3.2 Template projet — features ABSENTES

```
❌ st_marker() + MarkerConfig (navigation slide-like)
❌ BannerConfig + BannerMode (navigation banners)
❌ TOCConfig (configuration détaillée de la table des matières)
❌ add_zoom_options() + inject_zoom_logic() (zoom responsive)
❌ st_mermaid() (diagrammes Mermaid)
❌ st_plantuml() (diagrammes PlantUML)
❌ st_tikz() (diagrammes TikZ)
❌ st_graphviz() (diagrammes Graphviz)
❌ st_cite() + st_bibliography() (bibliographie)
❌ load_bibtex() + CitationStyle (chargement de références)
❌ ExportConfig + st_export() (export HTML)
❌ st_html() (pont HTML brut)
❌ st_dataframe(), st_table(), st_metric(), st_json() (widgets données)
❌ st_line_chart(), st_bar_chart(), etc. (charts)
❌ load_gsheet() + GSheetConfig (Google Sheets)
❌ BlockHelper (OOP) + BlockHelperConfig (DI avancé)
❌ show_explanation(), show_details() (helpers pédagogiques)
❌ responsive_cols, responsive=True (grilles responsives)
❌ load_css() (CSS externe)
❌ configure_image_path() (chemins d'images)
❌ InspectorConfig (éditeur live)
```

### 3.3 Manuels — répartition des features

| Manuel | Blocks | Features principales couvertes |
|--------|--------|-------------------------------|
| `stx_manual_intro` | ~15 blocks | Fondamentaux + zoom + markers + helpers + responsive intro |
| `stx_manual_advanced` | ~15 blocks | Diagrammes, bibliographie, export, GSheets, banner, lazy-loading, responsive avancé |
| `stx_manuals_collection` | ~5 blocks | st_collection, CollectionConfig, TOML, navigation inter-projets |
| `stx_manuals_shared-blocks` | ~5 blocks | Blocs réutilisables (welcome, header, footer, best practices) |

### 3.4 Bug identifié

Dans `documentation/template_project/blocks/helpers.py` : la fonction `show_tip` est importée dans plusieurs blocks (`bck_02_text_and_styles.py`, etc.) mais **n'est pas définie**. Ce bug sera résolu par la suppression du template manuel (Phase 4).

---

## 4. Architecture cible

### 4.1 Arborescence finale

```
documentation/
  manuals/                              # SOURCE UNIQUE DE VÉRITÉ
    stx_manual_intro/                   # → génère template_simple
    stx_manual_advanced/                # → génère template_advanced
    stx_manuals_collection/             # → génère template_collection
    stx_manuals_shared-blocks/          # → copié dans template_collection

  templates/                            # DOSSIER GÉNÉRÉ
    template_simple/                    # Extrait de stx_manual_intro
      book.py
      setup.py
      .streamlit/config.toml
      custom/
        styles.py
        themes.py
      blocks/
        __init__.py
        helpers.py
        bck_welcome.py                  # Squelette depuis bck_qs_first_block.py etc.
        bck_text_and_styles.py
        bck_containers.py
        bck_grids.py
        bck_lists.py
        bck_images.py
        bck_code.py
        bck_interactivity.py
      static/
        images/

    template_advanced/                  # Extrait de stx_manual_advanced
      book.py
      setup.py
      .streamlit/config.toml
      custom/
        styles.py
        themes.py
      blocks/
        __init__.py
        helpers.py
        bck_welcome.py
        bck_diagrams.py                # Mermaid, PlantUML, TikZ
        bck_bibliography.py
        bck_export.py
        bck_data_widgets.py
        bck_responsive.py
        bck_navigation.py              # Markers, Banner, TOC config
        bck_google_sheets.py
      static/
        images/

    template_collection/                # Extrait de stx_manuals_collection
      book.py
      setup.py
      collection.toml
      .streamlit/config.toml
      custom/
        styles.py
        themes.py
      blocks/
        __init__.py
        helpers.py
        bck_home.py
      shared-blocks/                    # Copié depuis stx_manuals_shared-blocks
      static/
        images/
          covers/

scripts/
  generate_templates.py                 # Script de génération
```

### 4.2 Flux de génération

```
┌─────────────────────────┐
│  stx_manual_intro       │──extract──▶ templates/template_simple/
│  (15 blocks, didactique)│            (8-10 blocks, squelette)
└─────────────────────────┘

┌─────────────────────────┐
│  stx_manual_advanced    │──extract──▶ templates/template_advanced/
│  (15 blocks, didactique)│            (8-10 blocks, squelette)
└─────────────────────────┘

┌─────────────────────────┐
│  stx_manuals_collection │──extract──▶ templates/template_collection/
│  (5 blocks + toml)      │            (3-5 blocks + toml + shared-blocks)
└─────────────────────────┘

┌──────────────────────────┐
│  stx_manuals_shared-blk  │──copy────▶ templates/template_collection/shared-blocks/
└──────────────────────────┘
```

### 4.3 Principe de transformation des blocks

Chaque block du manuel suit le pattern `BlockStyles + build()`. Le script de génération :

1. **Conserve intégralement** :
   - Les imports (`from streamtex import ...`, `from custom.styles import ...`)
   - La classe `BlockStyles` (styles du block)
   - La signature `def build():`

2. **Transforme** :
   - Le corps de `build()` : supprime le contenu pédagogique (appels à `show_code()`, `show_explanation()`, longues démonstrations répétées)
   - Ne garde qu'**un exemple minimal** de chaque feature utilisée dans le block
   - Ajoute des commentaires `# TODO: customize` aux endroits modifiables

3. **Ne touche pas** :
   - `book.py`, `setup.py`, `.streamlit/config.toml` → copiés tels quels (avec ajustement du titre)
   - `custom/styles.py`, `custom/themes.py` → copiés tels quels
   - `blocks/__init__.py`, `blocks/helpers.py` → copiés tels quels

---

## 5. Convention d'extractibilité des manuels

Pour que le script puisse transformer les blocks de manière fiable, les manuels doivent respecter des conventions. Ces conventions sont **légères** et ne changent pas la structure existante — elles ajoutent uniquement des marqueurs.

### 5.1 Marqueurs de section dans les blocks

Chaque block du manuel utilisera des marqueurs de commentaires pour délimiter les zones :

```python
def build():
    # --- FEATURE: st_mermaid ---
    # (contenu qui illustre la feature — gardé dans le template sous forme minimale)
    st_write(bs.heading, "Mermaid Diagrams", tag=t.h2, toc_lvl="1")

    stx.st_mermaid("""
    graph TD
        A[Start] --> B[End]
    """)

    # --- DEMO: st_mermaid advanced ---
    # (contenu pédagogique — supprimé dans le template)
    show_code("""stx.st_mermaid(...)""")
    show_explanation("Mermaid renders client-side using...")

    # Variations supplémentaires pour l'enseignement
    stx.st_mermaid("""sequenceDiagram...""")
    stx.st_mermaid("""pie...""")
    # --- END DEMO ---
```

**Règles des marqueurs** :

| Marqueur | Signification | Traitement par le script |
|----------|---------------|--------------------------|
| `# --- FEATURE: <nom> ---` | Début d'une section feature | **Conservé** dans le template (exemple minimal) |
| `# --- DEMO: <nom> ---` | Début d'une section pédagogique | **Supprimé** dans le template |
| `# --- END DEMO ---` | Fin d'une section pédagogique | **Supprimé** dans le template |

### 5.2 Convention book.py

Le `book.py` de chaque manuel doit contenir un commentaire de métadonnées :

```python
# --- TEMPLATE_META ---
# template_name: template_simple
# template_title: "My StreamTeX Project"
# template_description: "A starter project with core StreamTeX features"
# --- END TEMPLATE_META ---
```

### 5.3 Convention de mapping des blocks

Certains blocks du manuel seront fusionnés ou renommés dans le template. Un fichier de configuration `template_mapping.toml` dans chaque manuel définira ce mapping :

```toml
# documentation/manuals/stx_manual_intro/template_mapping.toml

[template]
name = "template_simple"
title = "My StreamTeX Project"
description = "Starter project with core StreamTeX features"

[blocks]
# Manuel block → Template block (rename, merge, or exclude)
bck_qs_first_block   = "bck_welcome"
bck_qs_text_styles   = "bck_text_and_styles"
bck_qs_containers    = "bck_containers"
bck_qs_grids         = "bck_grids"
bck_qs_lists         = "bck_lists"
bck_qs_images        = "bck_images"
bck_qs_code          = "bck_code"
bck_qs_interactivity = "bck_interactivity"

# Blocks exclus du template (purement pédagogiques)
[exclude]
blocks = [
    "bck_qs_new_project",      # Explique comment créer un projet (méta)
    "bck_zoom_and_responsive",  # Sera dans le book.py directement
]

[copy_as_is]
# Fichiers copiés sans transformation
files = [
    "setup.py",
    ".streamlit/config.toml",
    "custom/styles.py",
    "custom/themes.py",
    "blocks/__init__.py",
    "blocks/helpers.py",
]
```

---

## 6. Phase 1 — Audit et normalisation des manuels

### 6.1 Objectif

S'assurer que les manuels existants sont structurés de manière extractible, sans modifier leur contenu pédagogique.

### 6.2 Tâches

| # | Tâche | Détail |
|---|-------|--------|
| 1.1 | Auditer `stx_manual_intro` | Lister chaque block, identifier les features illustrées, vérifier le pattern `BlockStyles + build()` |
| 1.2 | Auditer `stx_manual_advanced` | Même audit, plus vérifier la couverture des features avancées |
| 1.3 | Auditer `stx_manuals_collection` | Vérifier la couverture collection + shared-blocks |
| 1.4 | Créer `template_mapping.toml` pour chaque manuel | Définir le mapping block → template pour les 3 manuels |
| 1.5 | Ajouter les marqueurs `FEATURE` / `DEMO` | Insérer les commentaires de section dans chaque block des manuels |
| 1.6 | Ajouter `TEMPLATE_META` dans les book.py | Métadonnées pour la génération |
| 1.7 | Vérifier la couverture API | Comparer la matrice (Annexe A) avec les blocks des manuels, combler les lacunes si nécessaire |

### 6.3 Contraintes

- Les marqueurs doivent être **invisibles** pour l'utilisateur du manuel (commentaires Python uniquement)
- Le contenu pédagogique ne doit **pas être modifié** — seuls des commentaires sont ajoutés
- Les `template_mapping.toml` sont des fichiers **déclaratifs** dans chaque dossier de manuel

### 6.4 Estimation

- ~2-3 heures de travail (audit + insertion de marqueurs dans ~35 blocks)

---

## 7. Phase 2 — Script de génération

### 7.1 Objectif

Écrire `scripts/generate_templates.py` qui transforme les manuels en templates exécutables.

### 7.2 Spécification du script

#### Interface CLI

```bash
# Générer tous les templates
uv run python scripts/generate_templates.py

# Générer un template spécifique
uv run python scripts/generate_templates.py --manual stx_manual_intro

# Générer avec dry-run (affiche les transformations sans écrire)
uv run python scripts/generate_templates.py --dry-run

# Nettoyer les templates générés
uv run python scripts/generate_templates.py --clean
```

#### Algorithme principal

```
Pour chaque manuel ayant un template_mapping.toml :
  1. Lire template_mapping.toml
  2. Créer le dossier cible documentation/templates/<template_name>/
  3. Copier les fichiers copy_as_is
  4. Pour chaque block dans [blocks] :
     a. Lire le fichier source
     b. Parser le code Python (module ast)
     c. Extraire : imports, classe BlockStyles, fonction build()
     d. Dans build() : supprimer les zones DEMO, garder les zones FEATURE
     e. Écrire le fichier cible avec le nom mappé
  5. Générer book.py adapté :
     a. Copier le book.py du manuel
     b. Remplacer les noms de blocks selon le mapping
     c. Remplacer le titre avec template_title
     d. Supprimer les références aux blocks exclus
  6. Copier static/ (images placeholder uniquement)
  7. Écrire un README.md listant les features couvertes
```

#### Parsing des blocks (détail de l'étape 4)

Le script utilise deux stratégies complémentaires :

**Stratégie A — Basée sur les marqueurs (préférée)** :
```python
def extract_template_block(source: str) -> str:
    """Supprime les zones DEMO, conserve les zones FEATURE."""
    lines = source.splitlines()
    result = []
    in_demo = False

    for line in lines:
        if "# --- DEMO:" in line:
            in_demo = True
            continue
        if "# --- END DEMO ---" in line:
            in_demo = False
            continue
        if not in_demo:
            result.append(line)

    return "\n".join(result)
```

**Stratégie B — Basée sur les patterns (fallback)** :
Si un block n'a pas de marqueurs, le script utilise des heuristiques :
- Supprimer les appels à `show_code()`, `show_code_inline()`, `show_explanation()`, `show_details()`
- Supprimer les blocs `with st.expander(...)` qui contiennent du contenu pédagogique
- Garder le premier exemple de chaque feature, supprimer les variations

### 7.3 Structure du script

```
scripts/
  generate_templates.py          # Point d'entrée CLI
  template_generator/            # Package de génération (optionnel, si le script grossit)
    __init__.py
    parser.py                    # Parsing des blocks (marqueurs + heuristiques)
    transformer.py               # Transformation du contenu
    writer.py                    # Écriture des fichiers cibles
    config.py                    # Lecture de template_mapping.toml
```

**Note** : si la logique reste simple (~200-300 lignes), un seul fichier `generate_templates.py` suffit.

### 7.4 Gestion du book.py généré

Le `book.py` du template est généré à partir de celui du manuel avec ces transformations :

| Élément dans le manuel | Transformation |
|------------------------|----------------|
| `page_title = "StreamTeX Manual — Intro"` | → `page_title = "My StreamTeX Project"` (depuis template_mapping.toml) |
| `blocks=[blocks.bck_qs_first_block, blocks.bck_qs_text_styles, ...]` | → `blocks=[blocks.bck_welcome, blocks.bck_text_and_styles, ...]` (noms mappés, blocks exclus supprimés) |
| Imports de blocks spécifiques | → Adaptés aux noms mappés |
| Fonctionnalités book (paginate, toc_config, marker_config, banner_config, zoom) | → **Conservées telles quelles** |
| Export config, bib_sources, gsheet_config (si présents) | → **Conservés** (le template avancé les aura, le simple non) |

### 7.5 Tests du script

```python
# tests/test_generate_templates.py

def test_template_mapping_valid():
    """Chaque template_mapping.toml référence des blocks qui existent."""

def test_markers_balanced():
    """Chaque DEMO a un END DEMO correspondant."""

def test_generated_template_has_book():
    """Le template généré contient book.py."""

def test_generated_blocks_have_build():
    """Chaque block généré a une fonction build()."""

def test_generated_blocks_have_blockstyles():
    """Chaque block généré a une classe BlockStyles."""

def test_generated_template_importable():
    """Les imports dans les blocks générés sont cohérents."""

def test_excluded_blocks_not_in_output():
    """Les blocks marqués [exclude] ne sont pas dans le template."""

def test_book_references_only_generated_blocks():
    """Le book.py généré ne référence que les blocks qui existent."""

def test_idempotent():
    """Deux exécutions successives produisent le même résultat."""
```

### 7.6 Estimation

- Script de base : ~4-6 heures
- Tests unitaires : ~2 heures
- Total : ~6-8 heures

---

## 8. Phase 3 — Adaptation des slash commands

### 8.1 Objectif

Les slash commands `/project:project-new` et `/project:collection-new` doivent utiliser les templates générés comme source de référence.

### 8.2 Modifications

#### `/project:project-new` (`.claude/commands/project/project-new.md`)

```diff
 ## Steps

-1. **Read the template**: Read `documentation/template_project/` structure
+1. **Read the template**: Read `documentation/templates/template_simple/` structure
+   - For advanced projects, use `documentation/templates/template_advanced/` instead
    ...

 ## Reference Projects
-- `documentation/template_project/` — canonical template (source of truth)
+- `documentation/templates/template_simple/` — generated simple template (source of truth)
+- `documentation/templates/template_advanced/` — generated advanced template
 - `documentation/manuals/stx_manual_intro/` — Phase 1 intro course example
```

**Ajout d'un argument optionnel** : `$ARGUMENTS` acceptera `--advanced` pour choisir le template avancé.

#### `/project:collection-new` (`.claude/commands/project/collection-new.md`)

```diff
-1. **Read the template**: Read `documentation/template_collection/` structure
+1. **Read the template**: Read `documentation/templates/template_collection/` structure
    ...

 ## Reference Projects
-- `documentation/template_collection/` — canonical template (source of truth)
+- `documentation/templates/template_collection/` — generated collection template
 - `documentation/manuals/stx_manuals_collection/` — working collection example
```

### 8.3 Nouveau slash command (optionnel)

Créer `/developer:generate-templates` :

```markdown
Regenerate StreamTeX templates from manuals.

## Steps
1. Run `uv run python scripts/generate_templates.py`
2. Verify each generated template:
   - `uv run streamlit run documentation/templates/template_simple/book.py`
   - `uv run streamlit run documentation/templates/template_advanced/book.py`
   - `uv run streamlit run documentation/templates/template_collection/book.py`
3. Report the generation results
```

### 8.4 Estimation

- ~1 heure

---

## 9. Phase 4 — Suppression des anciens templates

### 9.1 Objectif

Supprimer `documentation/template_project/` et `documentation/template_collection/` qui ne sont plus la source de vérité.

### 9.2 Précautions

Avant suppression, vérifier que :

| Vérification | Comment |
|--------------|---------|
| Aucune référence résiduelle dans le code | `grep -r "template_project" .` / `grep -r "template_collection" .` |
| Les slash commands pointent vers `templates/` | Vérifier project-new.md et collection-new.md |
| CLAUDE.md mis à jour | Section "Repository Layout" et "Workflows" |
| Les templates générés fonctionnent | `uv run streamlit run documentation/templates/*/book.py` |
| Le contenu utile a été migré | Styles, themes, helpers → vérifier qu'ils existent dans les manuels |

### 9.3 Fichiers à supprimer

```
documentation/template_project/          # 20+ fichiers
documentation/template_collection/       # 15+ fichiers
```

### 9.4 Estimation

- ~30 minutes (vérifications + suppression + mise à jour des références)

---

## 10. Phase 5 — Validation et documentation

### 10.1 Tests automatisés

```bash
# 1. Générer les templates
uv run python scripts/generate_templates.py

# 2. Vérifier que les templates se lancent
uv run streamlit run documentation/templates/template_simple/book.py &
uv run streamlit run documentation/templates/template_advanced/book.py --server.port 8502 &
uv run streamlit run documentation/templates/template_collection/book.py --server.port 8503 &

# 3. Tests unitaires du script
uv run pytest tests/test_generate_templates.py -v

# 4. Tests existants (non-régression)
uv run pytest tests/ -v

# 5. Linter
uv run ruff check scripts/ streamtex/
```

### 10.2 Tests manuels

| Test | Attendu |
|------|---------|
| Créer un projet avec `/project:project-new test_validation` | Le projet se lance et affiche les blocks du template simple |
| Créer un projet avancé avec `/project:project-new test_advanced --advanced` | Le projet inclut diagrammes, bibliographie, export |
| Créer une collection avec `/project:collection-new test_col` | La collection se lance avec la page d'accueil |
| Modifier un block dans le manuel intro | Après re-génération, le changement apparaît dans template_simple |
| Ajouter un nouveau block au manuel advanced | Après ajout au mapping + re-génération, le block apparaît dans template_advanced |

### 10.3 Documentation à mettre à jour

| Fichier | Modification |
|---------|-------------|
| `CLAUDE.md` | Section "Repository Layout" : remplacer `template_project/` et `template_collection/` par `templates/` (généré) |
| `CLAUDE.md` | Section "Workflows" : ajouter workflow "Régénérer les templates" |
| `documentation/coding_standards.md` | Ajouter la convention des marqueurs `FEATURE` / `DEMO` |
| `.claude/commands/project/project-new.md` | Pointer vers les templates générés |
| `.claude/commands/project/collection-new.md` | Pointer vers les templates générés |
| Memory (`MEMORY.md`) | Mettre à jour la section architecture |

### 10.4 Estimation

- ~2 heures

---

## 11. Fichiers impactés

### 11.1 Fichiers créés

| Fichier | Phase | Description |
|---------|-------|-------------|
| `scripts/generate_templates.py` | P2 | Script de génération principal |
| `documentation/manuals/stx_manual_intro/template_mapping.toml` | P1 | Mapping blocks → template simple |
| `documentation/manuals/stx_manual_advanced/template_mapping.toml` | P1 | Mapping blocks → template avancé |
| `documentation/manuals/stx_manuals_collection/template_mapping.toml` | P1 | Mapping blocks → template collection |
| `documentation/templates/` (dossier entier) | P2 | Templates générés (3 sous-dossiers) |
| `tests/test_generate_templates.py` | P2 | Tests du script |

### 11.2 Fichiers modifiés

| Fichier | Phase | Modification |
|---------|-------|-------------|
| Blocks des 3 manuels (~35 fichiers) | P1 | Ajout de marqueurs `FEATURE` / `DEMO` (commentaires uniquement) |
| `book.py` des 3 manuels | P1 | Ajout de `TEMPLATE_META` (commentaire) |
| `.claude/commands/project/project-new.md` | P3 | Pointer vers `templates/template_simple/` |
| `.claude/commands/project/collection-new.md` | P3 | Pointer vers `templates/template_collection/` |
| `CLAUDE.md` | P5 | Mise à jour layout + workflows |
| `documentation/coding_standards.md` | P5 | Convention des marqueurs |

### 11.3 Fichiers supprimés

| Fichier | Phase | Raison |
|---------|-------|--------|
| `documentation/template_project/` (entier) | P4 | Remplacé par templates générés |
| `documentation/template_collection/` (entier) | P4 | Remplacé par templates générés |

---

## 12. Risques et mitigations

| # | Risque | Sévérité | Probabilité | Mitigation |
|---|--------|----------|-------------|------------|
| R1 | Les marqueurs FEATURE/DEMO rendent les manuels moins lisibles | Faible | Faible | Marqueurs = commentaires Python simples, pas visibles par l'utilisateur |
| R2 | Le parsing échoue sur un block complexe | Moyenne | Moyenne | Stratégie B (heuristiques) comme fallback + tests unitaires par block |
| R3 | Le template généré ne se lance pas (imports cassés) | Haute | Faible | Test d'exécution automatique dans la CI + test `test_generated_template_importable` |
| R4 | Les manuels changent de structure, cassant le script | Moyenne | Moyenne | Le script valide la présence des marqueurs et lève une erreur claire si un mapping est invalide |
| R5 | Le dossier `templates/` généré est committé mais diverge des manuels | Faible | Moyenne | Option 1 : gitignorer `templates/` et régénérer à la demande. Option 2 : hook pre-commit qui régénère |
| R6 | Un contributeur modifie un template généré au lieu du manuel source | Moyenne | Moyenne | README dans `templates/` : "NE PAS MODIFIER — fichier généré. Source : documentation/manuals/" |

### Décision sur R5 : gitignore ou commit ?

**Recommandation** : **committer** les templates générés.

Raisons :
- Les utilisateurs qui clonent le repo veulent un template prêt à l'emploi sans exécuter un script
- Les slash commands doivent pouvoir lire les templates immédiatement
- Le script est exécuté à la demande (après modification d'un manuel), pas à chaque commit

Contrepartie : ajouter un check CI qui vérifie que les templates sont à jour :
```bash
uv run python scripts/generate_templates.py
git diff --exit-code documentation/templates/
```

---

## 13. Critères de validation

### Critères obligatoires (Phase terminée = tous verts)

| # | Critère | Phase | Validation |
|---|---------|-------|------------|
| V1 | Les 3 `template_mapping.toml` existent et sont valides | P1 | `uv run python scripts/generate_templates.py --dry-run` sans erreur |
| V2 | Les marqueurs FEATURE/DEMO sont équilibrés dans tous les blocks | P1 | Test `test_markers_balanced` passe |
| V3 | Le script génère 3 templates sans erreur | P2 | `uv run python scripts/generate_templates.py` exit code 0 |
| V4 | Chaque template généré est exécutable | P2 | `uv run streamlit run documentation/templates/*/book.py` démarre |
| V5 | Chaque block généré a `BlockStyles + build()` | P2 | Test `test_generated_blocks_have_build` passe |
| V6 | Le script est idempotent | P2 | Test `test_idempotent` passe |
| V7 | Les slash commands pointent vers les bons templates | P3 | Vérification manuelle |
| V8 | Les anciens templates sont supprimés | P4 | `ls documentation/template_project/` échoue |
| V9 | Tous les tests existants passent | P5 | `uv run pytest tests/ -v` 100% |
| V10 | `ruff check` passe sur le script et les templates | P5 | `uv run ruff check scripts/ documentation/templates/` |

---

## Calendrier récapitulatif

| Phase | Description | Estimation | Pré-requis |
|-------|-------------|------------|------------|
| **P1** | Audit et normalisation des manuels | 2-3h | — |
| **P2** | Script de génération + tests | 6-8h | P1 terminée |
| **P3** | Adaptation des slash commands | 1h | P2 terminée |
| **P4** | Suppression des anciens templates | 30min | P2 + P3 terminées |
| **P5** | Validation et documentation | 2h | P4 terminée |
| **Total** | | **~12-15h** | |

---

## Annexe A — Matrice de couverture API actuelle

Légende : `T` = template_project, `I` = stx_manual_intro, `A` = stx_manual_advanced, `C` = stx_manuals_collection

| Feature | API | T | I | A | C | Template cible |
|---------|-----|---|---|---|---|----------------|
| Texte simple | `st_write()` | ✅ | ✅ | ✅ | ✅ | simple |
| Tuples inline | `st_write(s, "a", (s2, "b"))` | ✅ | ✅ | ✅ | — | simple |
| Images | `st_image()` | ✅ | ✅ | ✅ | — | simple |
| Code | `st_code()` | ✅ | ✅ | ✅ | — | simple |
| Listes | `st_list()` | ✅ | ✅ | ✅ | — | simple |
| Block/Span | `st_block()`, `st_span()` | ✅ | ✅ | ✅ | — | simple |
| Grille | `st_grid()` | ✅ | ✅ | ✅ | ✅ | simple |
| StyleGrid | `StyleGrid.create()` | ✅ | ✅ | ✅ | — | simple |
| Espacement | `st_space()`, `st_br()` | ✅ | ✅ | ✅ | ✅ | simple |
| Overlay | `st_overlay()` | ✅ | ✅ | ✅ | — | simple |
| Inclusion | `st_include()` | ✅ | ✅ | ✅ | — | simple |
| Interactivité | `st.button`, `st.toggle`, etc. | ✅ | ✅ | ✅ | — | simple |
| Style class | `Style()`, `+`, `Style.create()` | ✅ | ✅ | ✅ | ✅ | simple |
| StxStyles | Palettes prédéfinies | ✅ | ✅ | ✅ | ✅ | simple |
| Markers | `st_marker()`, `MarkerConfig` | — | ✅ | ✅ | — | simple |
| Zoom | `add_zoom_options()` | — | ✅ | ✅ | — | simple |
| TOC config | `TOCConfig` détaillé | — | ✅ | ✅ | — | simple |
| Banner config | `BannerConfig`, `BannerMode` | — | — | ✅ | — | avancé |
| Mermaid | `st_mermaid()` | — | — | ✅ | — | avancé |
| PlantUML | `st_plantuml()` | — | — | ✅ | — | avancé |
| TikZ | `st_tikz()` | — | — | ✅ | — | avancé |
| Graphviz | `st_graphviz()` | — | — | ✅ | — | avancé |
| Bibliographie | `st_cite()`, `st_bibliography()` | — | — | ✅ | — | avancé |
| Export | `ExportConfig`, `st_export()` | — | — | ✅ | — | avancé |
| HTML brut | `st_html()` | — | — | ✅ | — | avancé |
| Widgets données | `st_dataframe()`, `st_table()`, etc. | — | — | ✅ | — | avancé |
| Charts | `st_line_chart()`, etc. | — | — | ✅ | — | avancé |
| Google Sheets | `load_gsheet()`, `GSheetConfig` | — | — | ✅ | — | avancé |
| Responsive grid | `responsive_cols`, `responsive=True` | — | — | ✅ | — | avancé |
| Block helpers DI | `BlockHelperConfig`, DI pattern | — | — | ✅ | — | avancé |
| BlockHelper OOP | `BlockHelper` (héritage) | — | — | ✅ | — | avancé |
| Lazy registry | `LazyBlockRegistry` | — | — | ✅ | — | avancé |
| Collection | `st_collection()`, `CollectionConfig` | — | — | — | ✅ | collection |
| TOML config | `collection.toml` | — | — | — | ✅ | collection |
| Shared blocks | Cross-project blocks | — | — | — | ✅ | collection |
| Inspector | `InspectorConfig` | — | — | — | — | (optionnel) |

---

## Annexe B — Exemple de block extrait

### Block source (dans le manuel)

```python
# documentation/manuals/stx_manual_advanced/blocks/bck_diagrams.py

import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation

class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    subheading = s.project.titles.subsection_title

bs = BlockStyles

def build():
    st_write(bs.heading, "Diagram Rendering", tag=t.h2, toc_lvl="1")
    st_space("v", 2)

    # --- FEATURE: st_mermaid ---
    st_write(bs.subheading, "Mermaid Diagrams", tag=t.h3, toc_lvl="+1")
    st_space("v", 1)

    stx.st_mermaid("""
    graph TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Action 1]
        B -->|No| D[Action 2]
    """)

    # --- DEMO: mermaid variations ---
    show_code("""
    stx.st_mermaid(\"\"\"
    graph TD
        A[Start] --> B{Decision}
    \"\"\")
    """)
    show_explanation("Mermaid diagrams render client-side...")

    st_space("v", 2)
    st_write(s.large, "Sequence diagram:")
    stx.st_mermaid("""
    sequenceDiagram
        Alice->>Bob: Hello
        Bob-->>Alice: Hi back
    """)

    st_space("v", 2)
    st_write(s.large, "Pie chart:")
    stx.st_mermaid("""
    pie title Distribution
        "A" : 40
        "B" : 35
        "C" : 25
    """)
    # --- END DEMO ---

    st_space("v", 3)

    # --- FEATURE: st_plantuml ---
    st_write(bs.subheading, "PlantUML Diagrams", tag=t.h3, toc_lvl="+1")
    st_space("v", 1)

    stx.st_plantuml("""
    @startuml
    Alice -> Bob: Hello
    Bob --> Alice: Hi
    @enduml
    """)

    # --- DEMO: plantuml advanced ---
    show_code("""stx.st_plantuml(...)""")
    show_explanation("PlantUML requires a server...")
    # --- END DEMO ---
```

### Block généré (dans le template)

```python
# documentation/templates/template_advanced/blocks/bck_diagrams.py
# GENERATED — Do not edit. Source: documentation/manuals/stx_manual_advanced/

import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s

class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    subheading = s.project.titles.subsection_title

bs = BlockStyles

def build():
    st_write(bs.heading, "Diagram Rendering", tag=t.h2, toc_lvl="1")
    st_space("v", 2)

    # --- FEATURE: st_mermaid ---
    st_write(bs.subheading, "Mermaid Diagrams", tag=t.h3, toc_lvl="+1")
    st_space("v", 1)

    stx.st_mermaid("""
    graph TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Action 1]
        B -->|No| D[Action 2]
    """)

    st_space("v", 3)

    # --- FEATURE: st_plantuml ---
    st_write(bs.subheading, "PlantUML Diagrams", tag=t.h3, toc_lvl="+1")
    st_space("v", 1)

    stx.st_plantuml("""
    @startuml
    Alice -> Bob: Hello
    Bob --> Alice: Hi
    @enduml
    """)
```

**Transformations appliquées** :
1. Import de `show_code`, `show_explanation` → **supprimé** (non utilisés)
2. Zones `DEMO` → **supprimées** (contenu pédagogique)
3. Zones `FEATURE` → **conservées** (un exemple minimal par feature)
4. Commentaire `# GENERATED` → **ajouté** en tête de fichier

---

## Annexe C — Checklist d'exécution

### Phase 1 — Audit et normalisation

- [ ] Lister tous les blocks de `stx_manual_intro` avec leurs features
- [ ] Lister tous les blocks de `stx_manual_advanced` avec leurs features
- [ ] Lister tous les blocks de `stx_manuals_collection` avec leurs features
- [ ] Créer `documentation/manuals/stx_manual_intro/template_mapping.toml`
- [ ] Créer `documentation/manuals/stx_manual_advanced/template_mapping.toml`
- [ ] Créer `documentation/manuals/stx_manuals_collection/template_mapping.toml`
- [ ] Ajouter les marqueurs `FEATURE` / `DEMO` dans les blocks de `stx_manual_intro`
- [ ] Ajouter les marqueurs `FEATURE` / `DEMO` dans les blocks de `stx_manual_advanced`
- [ ] Ajouter les marqueurs `FEATURE` / `DEMO` dans les blocks de `stx_manuals_collection`
- [ ] Ajouter `TEMPLATE_META` dans les `book.py` des 3 manuels
- [ ] Vérifier la couverture API (Annexe A) — toutes les features ont un block source
- [ ] Valider que les manuels se lancent toujours (`uv run streamlit run ...`)

### Phase 2 — Script de génération

- [ ] Créer `scripts/generate_templates.py` — structure de base
- [ ] Implémenter la lecture de `template_mapping.toml`
- [ ] Implémenter la copie des fichiers `copy_as_is`
- [ ] Implémenter l'extraction de blocks (marqueurs FEATURE/DEMO)
- [ ] Implémenter le fallback heuristique (stratégie B)
- [ ] Implémenter la génération de `book.py` adapté
- [ ] Implémenter le nettoyage des imports inutilisés
- [ ] Ajouter le banner `# GENERATED — Do not edit` en tête des fichiers générés
- [ ] Ajouter les options CLI (`--dry-run`, `--clean`, `--manual`)
- [ ] Créer `tests/test_generate_templates.py`
- [ ] Test : `test_template_mapping_valid`
- [ ] Test : `test_markers_balanced`
- [ ] Test : `test_generated_template_has_book`
- [ ] Test : `test_generated_blocks_have_build`
- [ ] Test : `test_generated_blocks_have_blockstyles`
- [ ] Test : `test_excluded_blocks_not_in_output`
- [ ] Test : `test_book_references_only_generated_blocks`
- [ ] Test : `test_idempotent`
- [ ] Exécuter le script et vérifier les 3 templates

### Phase 3 — Slash commands

- [ ] Modifier `.claude/commands/project/project-new.md` → `templates/template_simple/`
- [ ] Ajouter support `--advanced` dans project-new.md
- [ ] Modifier `.claude/commands/project/collection-new.md` → `templates/template_collection/`
- [ ] (Optionnel) Créer `.claude/commands/developer/generate-templates.md`

### Phase 4 — Suppression

- [ ] `grep -r "template_project"` → vérifier zéro référence résiduelle
- [ ] `grep -r "template_collection"` → vérifier zéro référence résiduelle
- [ ] Supprimer `documentation/template_project/`
- [ ] Supprimer `documentation/template_collection/`

### Phase 5 — Validation

- [ ] `uv run python scripts/generate_templates.py` — exit code 0
- [ ] `uv run streamlit run documentation/templates/template_simple/book.py` — démarre
- [ ] `uv run streamlit run documentation/templates/template_advanced/book.py` — démarre
- [ ] `uv run streamlit run documentation/templates/template_collection/book.py` — démarre
- [ ] `uv run pytest tests/ -v` — tous les tests passent
- [ ] `uv run ruff check scripts/ documentation/templates/` — aucune erreur
- [ ] Créer un projet via `/project:project-new test_final` — fonctionne
- [ ] Mettre à jour `CLAUDE.md` (Repository Layout, Workflows)
- [ ] Mettre à jour `documentation/coding_standards.md` (conventions marqueurs)
- [ ] Mettre à jour `MEMORY.md` (architecture)
- [ ] Ajouter un check CI dans `.github/workflows/ci.yml` (templates à jour)
