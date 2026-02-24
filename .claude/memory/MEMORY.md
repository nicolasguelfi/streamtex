# StreamTeX — Mémoire de projet

## Version & santé
- **Version**: 0.2.0 | Python >=3.10 | Streamlit >=1.54.0
- **Dépendances**: beautifulsoup4, requests, watchdog | Dev: pytest, ruff
- **Tests**: 129 tests, tous passent (2026-02-18)
- **Commits**: 5 sur main (dernier: `a323b49` — marker sidebar)
- **État git**: modifications non commitées (feature export HTML)

## Modules de la bibliothèque (streamtex/)
- `__init__.py` — API publique (re-exports)
- `styles/` — Système de styles (Style, ListStyle, StyleGrid, theme)
- `write.py` — st_write (rendu texte, tuples inline)
- `book.py` — st_book, st_include, st_toc, load_css
- `container.py` — st_block, st_span
- `grid.py` — st_grid (CSS Grid)
- `list.py` — st_list
- `image.py` / `image_utils.py` — st_image, base64, MIME
- `toc.py` — Table of Contents (registre global singleton)
- `marker.py` — **Nouveau** : navigation par marqueurs (slide-like, PageUp/PageDown)
- `zoom.py` — Contrôle zoom
- `overlay.py` — Positionnement absolu
- `code.py` — st_code
- `space.py` — st_space, st_br
- `enums.py` — Tags
- `export.py` — **Nouveau** : export HTML self-contained (dual rendering, buffer avec pile)
- `link_preview.py` — Scaffold hover preview
- `utils.py` — Utilitaires (generate_key, contain_link, etc.)

## Projets existants (projects/)
- `project_aiai18h` — projet utilisateur
- `project_html_example` — exemple de migration HTML

## Slash commands (.claude/commands/ — nommage domaine-action, sous-dossiers par catégorie)
- **designer/**: `/designer:slide-audit` `/designer:slide-fix` `/designer:slide-new` `/designer:block-new` `/designer:block-preview` `/designer:style-audit` `/designer:style-refactor` `/designer:presentation-audit` `/designer:presentation-fix`
- **developer/**: `/developer:test-run` `/developer:lint` `/developer:deploy`
- **migration/**: `/migration:conversion-audit` `/migration:html-convert-batch` `/migration:html-convert-block` `/migration:html-export` `/migration:html-migrate`
- **project/**: `/project:project-new` `/project:collection-new` `/project:project-upgrade` `/project:course-generate`

## Système design (.claude/designer/)
- **Shared skills**: `visual-design-rules.md` `style-conventions.md` `streamtex-quick-reference.md`
- **Shared agents**: `slide-designer.md` `slide-reviewer.md`
- **ros_designer_default/**: Rôle "Présentation live" (10-20m distance)
  - Skills: `presentation-design-rules.md` (9 règles, override base)
  - Agents: `presentation-designer.md`

## Changements structurels
- **PAGE_WIDTH → "100%"** (était "1224pt") : pleine largeur navigateur par défaut, configurable via `st_book(page_width="1224pt")`
- **Zoom Fill mode** ajouté : `Math.min(2, available/pageWidth)` — remplit toujours la largeur disponible (contrairement à Fit qui cap à 1)
- **page_width param** propagé dans `st_book → add_zoom_options → inject_zoom_logic` et `ExportConfig`

## Développement récent
- **export.py** ajouté : export HTML self-contained
  - `_render()` = pont unique content → st.html() + buffer
  - HtmlExportBuffer avec pile push/pop pour le nesting (st_block, st_grid, st_list)
  - st_book(..., export=True) → bouton "Download HTML" en sidebar
  - test_export_guard.py scanne l'AST pour vérifier qu'aucun st.html() non whitelisté n'est ajouté
  - `_export_wrapper=False` param sur st_block pour que st_list/item() fournisse ses propres wrappers sémantiques
- **marker.py** ajouté (commit 1934b74): navigation slide-like avec MarkerConfig
  - Registre global singleton (même pattern que toc.py)
  - Widget flottant JS avec prev/next/liste popup
  - Keyboard nav (PageUp/PageDown configurable)
  - Scroll tracking automatique
  - Utilise `components.html()` car `st.html()` strip les scripts depuis Streamlit 1.54+

## Gotchas connus
- `.cursor/rules/env-setup/RULE.md` référence encore `conda activate` → obsolète (projet migré à uv)
- `st.html()` supprime les `<script>` depuis Streamlit 1.54+ → utiliser `components.html()` pour le JS
- `from streamtex import *` importe le module `streamtex.list` → masque le builtin `list()`. Utiliser `[*iterable]` au lieu de `list(iterable)` dans les blocs.
- **scrollEl = `.stMain`** : Le conteneur de scroll de Streamlit est `.stMain` (section avec overflow:auto). Ne PAS remonter l'arbre DOM depuis le contenu — risque de tomber sur un wrapper intermédiaire qui ne scrolle pas toujours.
- **Scroll tracker marker.py** : Le scroll tracker doit initialiser `best = -1` (pas 0) et ne modifier `currentIdx` que si un marker est trouvé (`best >= 0`). Sinon, quand les iframes n'ont pas encore chargé, il reset à 0 (mauvais).
- **Init timer marker.py** : Le `setTimeout(500)` d'init doit être sauvegardé dans `initTimer` et annulé dans le cleanup, sinon un init "fantôme" de l'exécution précédente peut consommer `_stxMarkerStartIdx`.

## Préférences utilisateur
- Langue d'échange: français
- Environnement: uv (jamais pip/conda/python direct)

## Fichiers mémoire détaillés
- *(à créer au besoin: decisions.md, debugging.md, patterns.md)*
