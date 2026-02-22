# Session 1 — 2026-02-21 : Création du pipeline HTML→StreamTeX

> Première session du projet de conversion Google Docs → StreamTeX.

---

## Objectif

Convertir ~359 fichiers HTML (exportés depuis Google Docs) en blocs StreamTeX Python, pour un système de multi-projets de cours (présentations et documents).

---

## Architecture du pipeline

```
exports/html/
  bck_title_break/index.html      ← HTML exporté Google Docs
  bck_ethics_overview/index.html
  bckcp_schedule_aiai/index.html
  ...

    ↓ [html_parser.py]

ParsedBlock (intermediate representation)
  - name, elements[], spans[], all_colors, all_images
  - estimated_complexity (simple/medium/complex)

    ↓ [style_extractor.py]  (mapping CSS → StreamTeX styles)

Style expressions: "s.project.pres.titles.h1 + s.project.colors.forest_green"

    ↓ [block_generator.py]

shared/blocks/bck_title_break.py   ← Bloc StreamTeX complet
shared/blocks/bck_ethics_overview.py
...

    ↓ [batch_convert.py]  (orchestrateur)

359 blocs générés + shared/blocks/__init__.py (LazyBlockRegistry)
```

---

## Outils créés

### 1. `tools/html_parser.py`
- Parse les HTML Google Docs → `ParsedBlock`
- Extrait : structure (headings, paragraphs, tables, lists, images), inline styles (couleurs, tailles, bold/italic), liens
- Gère les spécificités Google Docs (styles inline CSS, `<span>` imbriqués, images en base64/référence)
- API publique : `parse_html(html_path: Path) -> ParsedBlock`
- Structures : `ParsedBlock`, `ParsedElement`, `ParsedSpan`

### 2. `tools/style_extractor.py`
- Mappe les valeurs CSS extraites vers des expressions de style StreamTeX
- **Deux familles** : `pres` (bck_* → slides) et `doc` (bckcp_* → course pack)
- **COLOR_MAP** : 54 couleurs HTML hex → 15 styles sémantiques de projet
- **Size brackets** : Pres (36pt→p_xl, 28pt→p_lg, 24pt→p_md, 20pt→p_sm, 0→p_body)
- **Heading map** : h1-h6 → `s.project.{pres|doc}.titles.h{1-6}`
- **Link map** : Tailles adaptées pour éviter le 12pt par défaut
- API : `get_family()`, `map_color()`, `map_font_size()`, `map_heading()`, `map_link_style()`, `compose_style()`

### 3. `tools/block_generator.py`
- Génère des fichiers Python StreamTeX complets depuis `ParsedBlock`
- Structure standard : imports, `BlockStyles` class, `build()` function
- Gère : headings, paragraphs, tables (`st_grid`), lists (`st_list`), images (`st_image`), mixed inline styles (tuples)
- Nettoyage Unicode (zero-width spaces, Google Docs icons, variation selectors)
- API : `generate_block(parsed, image_registry) -> str`

### 4. `tools/batch_convert.py`
- CLI orchestrateur pour convertir tous les blocs
- Options : `--filter`, `--dry-run`, `--force`, `--limit`
- Génère automatiquement `shared/blocks/__init__.py` avec `LazyBlockRegistry`
- Statistiques : simple/medium/complex/skipped/errors

### 5. `tools/validate_blocks.py`
- Validation structurelle des blocs générés
- Vérifie : imports, `BlockStyles` class, `build()` function, syntaxe Python
- Alertes : images non trouvées dans le registre

### 6. `tools/book_generator.py`
- Génère `book.py` pour un cours à partir d'un fichier `blocks.csv`
- Configure : pagination, TOC, markers, thème, inspector

### 7. `tools/image_manager.py`
- Gestion des images extraites de Google Docs
- Registre MD5 → noms sémantiques
- Détection des doublons cross-blocs

---

## Styles et thèmes créés

### `shared/custom/styles.py`
- **15 couleurs sémantiques** avec `style_id` pour override thème
- **Famille Pres** (slides) : h1=48pt→h6=16pt, centré, paragraphes 16-36pt
- **Famille Doc** (course pack) : h1=20pt→h6=10pt, compact, paragraphes 12-20pt
- Links avec tailles adaptées (évite 12pt par défaut)
- Containers, grids, lists, tables pour chaque famille

### `shared/custom/themes.py`
- 4 thèmes : `pres_light`, `pres_dark`, `doc_light`, `doc_dark`
- Couleurs dark = neon/fluo (override par `style_id`)

---

## Commandes Claude Code créées

4 slash commands dans `.claude/commands/` :
- `/convert-html-batch` — Lancer le pipeline batch
- `/convert-html-block` — Convertir un seul bloc
- `/audit-conversion` — Auditer la qualité d'un bloc converti
- `/generate-course` — Générer book.py pour un cours

---

## Résultats de la session

- **Pipeline fonctionnel** : Parse → Extract → Generate → Validate
- **Premiers tests** sur quelques blocs individuels
- **Mapping couleurs** : 54 hex → 15 styles sémantiques
- **Architecture posée** : deux familles (pres/doc), thèmes, registre lazy

---

## Problèmes identifiés (à résoudre en session 2)

1. `map_link_style` : TypeError string vs int pour font_size
2. Import paths : nécessite d'exécuter depuis `projects/convert_html_to_streamtex/`
3. `parsed.complexity` → attribut correct = `parsed.estimated_complexity`
4. Couleurs non mappées à découvrir lors du batch complet
