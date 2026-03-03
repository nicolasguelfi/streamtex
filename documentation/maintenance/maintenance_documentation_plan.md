# Plan de maintenance de la documentation StreamTeX

## Contexte

La librairie StreamTeX (v0.3.0) a subi de nombreuses restructurations et ajouts de fonctionnalites. L'ecosysteme de documentation comprend actuellement 4 manuels utilisateur totalisant ~94 blocs, mais **aucun manuel developpeur** pour les contributeurs de la librairie elle-meme. Cette inspection vise a :
1. Garantir que toutes les capacites sont documentees dans les manuels utilisateur
2. Creer un **manuel developpeur** couvrant le repo git, le developpement, la maintenance et le deploiement de la librairie
3. Optimiser la structure des manuels pour une exploitation facile

---

## 1. Etat des lieux

### 1.1 Inventaire de la librairie (100+ API publiques)

| Module | Fonctions/Classes principales |
|--------|-------------------------------|
| `write.py` | `st_write` (tuples, tags, toc_lvl, label, marker) |
| `grid.py` | `st_grid`, `GridController`, `responsive_cols` |
| `container.py` | `st_block`, `st_span` |
| `list.py` | `st_list`, `ListController` |
| `markdown.py` | `st_markdown` (file=) |
| `image.py` | `st_image`, `configure_image_path` |
| `code.py` | `st_code`, `add_wrap_all_option` |
| `space.py` | `st_space`, `st_br` |
| `overlay.py` | `st_overlay`, `OverlayController` |
| `zoom.py` | `add_zoom_options`, `inject_zoom_logic` |
| `mermaid.py` | `st_mermaid` (pan/zoom, file=) |
| `plantuml.py` | `st_plantuml` (server, file=) |
| `tikz.py` | `st_tikz`, `extract_tikz`, `extract_math`, `extract_frames` |
| `latex.py` | `st_latex`, `st_latex_doc` |
| `book.py` | `st_book`, `st_include`, `TOCConfig`, `BannerConfig`, `BannerMode`, `MarkerConfig`, `InspectorConfig` |
| `toc.py` | `st_toc`, `reset_toc_registry`, `toc_entries`, `register_toc_entry` |
| `marker.py` | `st_marker`, `inject_marker_navigation`, `MarkerConfig` |
| `collection.py` | `st_collection`, `CollectionConfig`, `ProjectMeta` |
| `blocks.py` | `LazyBlockRegistry`, `ProjectBlockRegistry`, `BlockNotFoundError` |
| `block_helpers.py` | `BlockHelper`, `show_code`, `show_explanation`, `show_details`, `BlockHelperConfig` |
| `bib.py` | `load_bib`, `cite`, `st_cite`, `st_bibliography`, `BibEntry`, `BibConfig`, `BibFormat`, `CitationStyle`, `BibRefs` |
| `gsheet.py` | `load_gsheet`, `load_gsheet_df`, `GSheetConfig`, `AuthMode` |
| `export.py` | `st_export`, `st_html`, `ExportConfig`, `HtmlExportBuffer` |
| `export_widgets.py` | `st_dataframe`, `st_table`, `st_metric`, `st_json`, `st_graphviz`, `st_*_chart`, `st_audio`, `st_video` |
| `inspector.py` | `InspectorConfig` |
| `link_preview.py` | `LinkConfig`, `inject_link_preview_scaffold` |
| `styles/` | `Style`, `ListStyle`, `StyleGrid`, `StxStyles`, `theme()`, `add_css()` |
| `enums.py` | `Tags`, `ListTypes`, `NumberingMode` |
| `constants.py` | `PAGE_WIDTH`, `PAGE_PADDING` |
| `utils.py` | `generate_key`, `strip_html`, `resolve_content`, `contain_link` |

### 1.2 Structure actuelle des manuels

| Manuel | Blocs | Role |
|--------|-------|------|
| **stx_manual_intro** | 16 composites + 13 atomiques = 29 | Fondamentaux (texte, styles, layout, media, navigation, export) |
| **stx_manual_advanced** | 22 composites + 26 atomiques = 48 | Features avancees (overlays, diagrams, data, themes, bib, collections) |
| **stx_manual_deploy** | 9 composites + 3 atomiques = 12 | Deploiement (Docker, Render, HF, GCP, CI/CD) |
| **stx_manuals_collection** | 1 bloc | Hub de decouverte |
| **shared-blocks** | 5 blocs | Composants reutilisables |
| **Total** | **94 blocs** | |

---

## 2. Matrice de couverture fonctionnelle

### 2.1 Features DOCUMENTEES (couverture complete)

| Feature | Intro | Advanced |
|---------|:-----:|:--------:|
| Text rendering (st_write, tuples, tags) | V | V |
| Style composition (Style +/-) | V | V |
| 150+ named colors | V | V |
| Containers (st_block, st_span) | V | V |
| CSS Grid (st_grid, responsive) | V | V |
| Lists (st_list, ordered/unordered/custom) | V | V |
| Images (st_image, base64) | V | V |
| Code highlighting (st_code, Pygments) | V | V |
| Navigation markers (st_marker) | V | V |
| TOC (st_toc, numbering) | V | V |
| Book orchestration (st_book) | V | V |
| HTML export (st_export) | V | - |
| Overlays (st_overlay) | - | V |
| Visibility control | - | V |
| Custom themes (theme()) | - | V |
| Dynamic content / state | - | V |
| Forms / interactivity | - | V |
| Diagrams (Mermaid, PlantUML, TikZ, Graphviz) | - | V |
| Charts / DataViz (streamlit charts) | - | V |
| LaTeX (st_latex, st_latex_doc) | - | V |
| Markdown (st_markdown, file=) | - | V |
| Google Sheets (load_gsheet) | - | V |
| Bibliography (st_cite, st_bibliography) | - | V |
| LazyBlockRegistry | - | V |
| Shared blocks | - | V |
| Static resolution | - | V |
| Export-aware widgets | - | V |
| Block helpers (show_code, show_explanation) | - | V |
| Collections system | - | V |
| Deployment (Docker, Render, HF, GCP, CI/CD) | - | - (Deploy) |

### 2.2 Gaps identifies — Features NON documentees ou insuffisamment couvertes

| # | Feature / API | Module source | Gravite | Notes |
|---|---------------|---------------|---------|-------|
| G1 | `st_latex_doc` (documents LaTeX complets) | `latex.py` | P2 | Seul `st_latex` (math) semble documente en detail, pas `st_latex_doc` |
| G2 | `BannerConfig` / `BannerMode` (FULL, COMPACT, HIDDEN) | `book.py` | P2 | L'API banner n'est documentee nulle part en detail |
| G3 | `InspectorConfig` (live code editor) | `inspector.py` | P2 | Mentionne mais pas documente en profondeur |
| G4 | `LinkConfig` / `inject_link_preview_scaffold()` | `link_preview.py` | P3 | API de configuration des previews de liens non documentee |
| G5 | `ExportConfig` — options avancees | `export.py` | P2 | Seul le flux basique est documente |
| G6 | `load_atomic_block()` — pattern atomique | `blocks.py` | P1 | Le pattern est UTILISE partout mais pas explicitement documente comme pattern |
| G7 | `set_static_sources()` / `resolve_static()` | `blocks.py` | P3 | Documente dans static_resolution_demo mais API peu detaillee |
| G8 | `BibFormat` variantes (MLA, IEEE, CHICAGO, HARVARD) | `bib.py` | P3 | Seul APA montre dans la doc |
| G9 | `register_bib_parser()` — parsers custom | `bib.py` | P3 | API avancee non documentee |
| G10 | `GSheetConfig.AuthMode` (SERVICE_ACCOUNT, OAUTH2) | `gsheet.py` | P3 | Seul le mode PUBLIC semble documente |
| G11 | CLI `stx` — reference complete | `cli/main.py` | P1 | Aucun manuel ne documente la CLI stx |
| G12 | `st_html()` dual-render bridge | `export.py` | P2 | Documente dans intro export, mais merite plus de detail |
| G13 | `NumberingMode` enum | `enums.py` | P3 | Non documente comme reference |
| G14 | `configure_image_path()` — base path globale | `image.py` | P3 | Pas documente explicitement |
| G15 | Export-aware `st_graphviz` (SVG) | `export_widgets.py` | P3 | Non documente specifiquement |
| G16 | `responsive_cols()` helper | `grid.py` | P3 | Utilise en interne, pas documente publiquement |
| G17 | Zoom injection details (`inject_zoom_logic`) | `zoom.py` | P3 | add_zoom_options documente, mais pas l'API bas-niveau |

---

## 3. Recommandations structurelles

### 3.1 Structure actuelle vs proposee

La structure actuelle en 3 manuels utilisateur + 1 hub est **globalement bonne** pour les utilisateurs. Le manuel Advanced est cependant tres volumineux (48 blocs). En revanche, il manque totalement un **manuel developpeur** pour les contributeurs de la librairie.

**Structure recommandee : 4 manuels + 1 hub (ajout d'un manuel Developer)**

| Manuel | Role | Changements proposes |
|--------|------|----------------------|
| **Intro** (29 blocs) | Fondamentaux utilisateur | + Ajouter un bloc CLI Quick Start (G11) |
| **Advanced** (48 blocs) | Features avancees utilisateur | Reorganiser les sections internes (voir 3.2) |
| **Deploy** (12 blocs) | Deploiement utilisateur | + Reference CLI stx deploy/publish (G11) |
| **Developer** (NOUVEAU) | Developpeurs de la librairie | Repo, architecture, dev, tests, CI/CD, release, maintenance |
| **Collection Hub** (1 bloc) | Decouverte | + Ajouter carte vers le nouveau manuel Developer |

### 3.2 Nouveau manuel : `stx_manual_developer`

**Public cible** : Contributeurs et mainteneurs de la librairie StreamTeX

**Structure** : 11 composites + ~30 atomiques

### 3.3 Reorganisation du manuel Advanced

Sections internes proposees (via TOC niveaux) :

```
Advanced Manual — Reorganisation
├── Section 1: Architecture & Patterns
├── Section 2: UI Avancee
├── Section 3: Navigation & Book
├── Section 4: Langages documentaires
├── Section 5: Donnees & Integrations
├── Section 6: Export
```

---

## 4. Actions concretes (30 items)

### Priorite P0 — Manuel Developpeur (NOUVEAU)
A0a-A0l: Scaffolder et creer tous les blocs du manuel developpeur

### Priorite P1 — Gaps critiques manuels utilisateur
A1-A6: CLI quickstart, CLI reference, atomic blocks pattern, banner config, inspector config

### Priorite P2 — Completude fonctionnelle
A7-A12: LaTeX documents, export advanced, bibliography enrichment, hover/preview, gsheet, reorganisation

### Priorite P3 — Polish et reference
A13-A22: API docs manquantes, shared-blocks update, collection hub, upgrade guide, references

---

## 5. Plan d'execution

### Phase 0 : Manuel Developpeur (A0a-A0l)
### Phase 1 : Gaps P1 manuels utilisateur (A1-A6)
### Phase 2 : Gaps P2 (A7-A12)
### Phase 3 : Polish P3 (A13-A22)

---

## 6. Statut

- [x] Plan cree et sauvegarde
- [ ] Phase 0 : Manuel Developpeur
- [ ] Phase 1 : Gaps P1
- [ ] Phase 2 : Gaps P2
- [ ] Phase 3 : Polish P3
