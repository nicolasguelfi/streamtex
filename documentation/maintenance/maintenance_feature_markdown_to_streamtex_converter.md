# Plan de Maintenance : Conversion Markdown vers StreamTeX

> **Date** : 2026-02-28
> **Auteur** : Claude Code (assiste par Nicolas Guelfi)
> **Version** : 1.0
> **Statut** : Plan initial — architecture markdown-it-py + SyntaxTreeNode walker
> **Pre-requis** : StreamTeX >= 0.2.0, module `streamtex.markdown` (st_markdown)

---

## Table des matieres

1. [Probleme et objectif](#1-probleme-et-objectif)
2. [Les deux modes de conversion](#2-les-deux-modes-de-conversion)
3. [Architecture : markdown-it-py + SyntaxTreeNode walker](#3-architecture--markdown-it-py--syntaxtreenode-walker)
4. [Modele de donnees intermediaire](#4-modele-de-donnees-intermediaire)
5. [Parseur : markdown-it-py walker](#5-parseur--markdown-it-py-walker)
6. [Generateur mode minimal](#6-generateur-mode-minimal)
7. [Generateur mode full StreamTeX](#7-generateur-mode-full-streamtex)
8. [Gestion des fichiers et assets](#8-gestion-des-fichiers-et-assets)
9. [CLI et integration](#9-cli-et-integration)
10. [Fichiers a creer/modifier](#10-fichiers-a-creermodifier)
11. [Plan d'implementation](#11-plan-dimplementation)
12. [Tests](#12-tests)
13. [Risques et mitigations](#13-risques-et-mitigations)
14. [Limitations connues](#14-limitations-connues)
15. [Criteres de validation](#15-criteres-de-validation)

---

## 1. Probleme et objectif

### Probleme

De nombreux utilisateurs possedent du contenu Markdown existant (documentations, cours, tutoriels, articles, README, notes) qu'ils souhaitent transformer en projets StreamTeX pour beneficier de la navigation paginee, du systeme de styles, de l'export HTML et de l'interactivite Streamlit. Aujourd'hui cette migration est 100% manuelle.

Le Markdown est le format de contenu le plus repandu dans l'ecosysteme developpeur (GitHub, GitLab, MkDocs, Jupyter, Obsidian, Notion export, etc.). Un importateur Markdown represente le chemin de migration le plus accessible pour les nouveaux utilisateurs StreamTeX.

### Objectif

Fournir un outil Python en ligne de commande qui :

1. **Prend en entree** un ou plusieurs fichiers `.md` (ou un dossier contenant des `.md`)
2. **Genere en sortie** un projet StreamTeX complet et fonctionnel (`book.py`, `blocks/`, `custom/`, `setup.py`, etc.)
3. **Propose deux modes** de conversion selon le degre de transformation souhaite

### Perimetre

- **IN** : Markdown standard (CommonMark), GFM (tables, task lists, strikethrough), math LaTeX (`$...$`, `$$...$$`), code blocks avec langage, images, liens, front matter YAML, listes imbriquees, blockquotes, lignes horizontales
- **OUT** : Extensions Markdown proprietaires (Obsidian `[[wiki links]]`, Notion databases, MDX composants React), HTML inline complexe (formulaires, scripts)

---

## 2. Les deux modes de conversion

### Mode Minimal (`--mode minimal`)

**Philosophie** : Garder le Markdown tel quel, utiliser `st_markdown()` pour le rendu natif Streamlit.

Chaque fichier ou section de niveau 1 devient un bloc StreamTeX qui rend le contenu Markdown via `st_markdown()`. Le projet StreamTeX fournit la navigation (pagination, TOC, markers) autour du contenu Markdown existant.

```
Fichier(s) .md source
    -> Decoupage en fragments logiques (titres de niveau 1)
    -> Chaque fragment -> un bloc StreamTeX avec st_markdown(r"...")
    -> Les blocs de code -> st_code() pour un meilleur controle
    -> Les math $$...$$ -> st_latex() pour un rendu isole
    -> Projet fonctionnel genere
```

**Avantages** :
- Conversion quasi-instantanee et 100% automatique
- Fidelite maximale (Streamlit rend le Markdown nativement)
- Tres peu de code Python genere (un `st_markdown()` par section)
- Le contenu reste editable en Markdown (`file="section.md"`)
- Ideal pour les documentations, tutoriels, notes

**Inconvenients** :
- Le contenu reste du Markdown brut (pas de styles StreamTeX)
- Pas de controle fin sur le rendu (polices, couleurs, espacement)
- Pas de support theme light/dark pour le contenu (Streamlit gere)
- L'export HTML est un simple `<div>` avec Markdown converti
- Pas de layouts complexes (grilles, overlays)

### Mode Full StreamTeX (`--mode full`)

**Philosophie** : Convertir chaque element Markdown vers son equivalent StreamTeX natif. Le contenu resultant est du Python pur, entierement stylable et interactif.

```
Fichier(s) .md source
    -> Parsing en arbre syntaxique (markdown-it-py AST)
    -> Chaque element -> appel StreamTeX natif :
        # Title            -> st_write(bs.heading, "Title", toc_lvl="1")
        ## Subtitle        -> st_write(bs.sub, "Subtitle", toc_lvl="+1")
        **bold**           -> (s.bold, "bold") dans st_write()
        *italic*           -> (s.italic, "italic") dans st_write()
        `code`             -> (s.text.fonts.monospace, "code") dans st_write()
        - item             -> st_list(list_type=lt.unordered)
        1. item            -> st_list(list_type=lt.ordered)
        ```python           -> st_code(style, code=..., language="python")
        ![alt](img.png)    -> st_image(uri="img.png")
        $E=mc^2$           -> st_latex(r"E=mc^2")
        $$\int...$$        -> st_latex(r"\int...")
        | A | B |          -> st_grid(cols=N) ou st_table()
        > quote            -> st_block(bs.quote) + st_write()
        [text](url)        -> st_write(style, "text", link="url")
        ---                -> st_space("v", 2)
    -> Projet fonctionnel genere
```

**Avantages** :
- Contenu natif StreamTeX, stylable avec le systeme de styles
- Compatible themes (light/dark)
- Widgets interactifs possibles apres conversion
- Export HTML natif de qualite (dual rendering pipeline)
- TOC, markers, recherche fonctionnent sur le texte natif
- Layouts avances possibles (st_grid pour les tableaux)

**Inconvenients** :
- Conversion plus complexe, peut necessite revision humaine
- Le contenu n'est plus editable en Markdown (c'est du Python)
- Perte de la simplicite du Markdown (verbeux en Python)
- Les formules mathematiques restent en `st_latex()` (inevitable)

### Tableau comparatif

| Aspect | Mode Minimal | Mode Full StreamTeX |
|--------|-------------|---------------------|
| **Effort de conversion** | Quasi-nul (~98% auto) | Moyen (~85% auto, 15% revision) |
| **Fidelite visuelle** | Haute (Streamlit natif) | Moyenne → Haute (styles StreamTeX) |
| **Stylabilite** | Non (rendu Markdown brut) | Oui (styles StreamTeX complets) |
| **Interactivite** | Non (contenu statique) | Oui (contenu natif Python) |
| **Themes light/dark** | Partiel (Streamlit gere) | Oui (controle total) |
| **Export HTML** | Basique (Markdown → HTML) | Natif (dual pipeline) |
| **Recherche textuelle** | Oui (texte rendu) | Oui (texte natif) |
| **Editabilite post-conversion** | Oui (fichiers .md conserves) | Non (code Python) |
| **Cas d'usage ideal** | Import rapide, documentation | Migration complete, cours interactif |

---

## 3. Architecture : markdown-it-py + SyntaxTreeNode walker

### 3.1 Choix du moteur de parsing

Le convertisseur repose sur **markdown-it-py** comme moteur de parsing. C'est le parseur Markdown Python le plus complet et le mieux maintenu (2026).

| Critere | markdown-it-py |
|---------|---------------|
| Version | 4.0.0 (aout 2025) |
| Maintenu par | Executable Books Project (MyST, Jupyter Book) |
| Downloads PyPI | ~305M/mois (via Rich, MyST, Jupyter Book) |
| CommonMark | 100% conforme (v0.31.2) |
| GFM | Built-in preset `"gfm-like"` : tables, strikethrough, task lists, autolinks |
| Math | Plugin `dollarmath` ($..$ et $$..$$) |
| Code blocks | Natif (fenced avec langage) |
| Front matter | Plugin `front_matter_plugin` (YAML entre `---`) |
| Images/liens | Support complet natif |
| AST | Token stream + `SyntaxTreeNode` avec `.walk()`, `.children`, `.next_sibling` |
| Plugins | 15+ plugins officiels (`mdit-py-plugins`) |
| Adopte par | MyST-Parser, Jupyter Book, Rich, Read the Docs |

#### Pourquoi pas les alternatives

| Librairie | Raison d'exclusion |
|-----------|--------------------|
| **mistune** 3.2.0 | Pas 100% CommonMark, pas de front matter, AST dict sans `.walk()` |
| **marko** 2.2.2 | Pas de plugin math, pas de front matter, communaute restreinte |
| **mistletoe** 1.5.1 | Math renderer-only (pas de token), abandonne par Executable Books |
| **commonmark.py** 0.9.1 | **Deprecie** — les mainteneurs recommandent markdown-it-py |
| **pypandoc** | Necessite binaire Pandoc (~100MB), excessif pour du Markdown |

### 3.2 Pipeline de conversion

```
Fichier(s) Markdown (.md)
    |
    +- (1) Front matter extraction (YAML)
    |      -> Titre, auteur, date, metadata custom
    |      -> Utilise pour book.py et styles projet
    |
    +- (2) Parsing markdown-it-py
    |      md = MarkdownIt("gfm-like")
    |          .use(dollarmath_plugin)
    |          .use(front_matter_plugin)
    |          .use(tasklists_plugin)
    |      tokens = md.parse(source)
    |      tree = SyntaxTreeNode(tokens)
    |
    +- (3) Tree walking -> MdNode tree
    |      -> Chaque SyntaxTreeNode -> MdNode intermediaire
    |      -> Normalisation des types (heading, paragraph, list, code, math, image, table, ...)
    |
    +- (4) Segmentation en blocs
    |      -> Decoupage par heading de niveau 1
    |      -> Chaque segment = 1 fichier bloc StreamTeX
    |
    +- (5) Generation de code Python
    |      -> Mode minimal : st_markdown() + st_code() + st_latex()
    |      -> Mode full : st_write() + st_list() + st_code() + st_latex() + st_image() + st_grid()
    |
    +- (6) Scaffold projet
           -> book.py, blocks/__init__.py, custom/styles.py, setup.py
           -> Copie des assets (images)
```

### 3.3 Dependances

```toml
# pyproject.toml — groupe optionnel
[project.optional-dependencies]
md-converter = [
    "markdown-it-py>=3.0",    # Parseur Markdown CommonMark + GFM
    "mdit-py-plugins>=0.4",   # Plugins officiels (math, front matter, task lists)
    "jinja2>=3.1",            # Templates pour generation de code
]
```

**Note** : `markdown-it-py` est deja une dependance transitive de `rich` (qui est une dependance de `streamlit`). Le groupe `md-converter` garantit neanmoins la version minimale et ajoute les plugins officiels.

### 3.4 Mapping markdown-it-py tokens -> StreamTeX

| Token markdown-it-py | Type | Mapping StreamTeX (mode full) |
|---------------------|------|-------------------------------|
| `heading_open` (h1) | Block | `st_write(bs.heading, title, toc_lvl="1")` |
| `heading_open` (h2) | Block | `st_write(bs.sub, title, toc_lvl="+1")` |
| `heading_open` (h3-h6) | Block | `st_write(bs.subsub, title, toc_lvl="+1")` |
| `paragraph_open` | Block | `st_write(bs.content, *inlines)` |
| `bullet_list_open` | Block | `st_list(list_type=lt.unordered)` |
| `ordered_list_open` | Block | `st_list(list_type=lt.ordered)` |
| `list_item_open` | Block | `with l.item():` |
| `fence` (code block) | Block | `st_code(bs.code_box, code=text, language=lang)` |
| `code_inline` | Inline | `(s.text.fonts.monospace, text)` tuple |
| `math_block` ($$...$$) | Block | `st_latex(r"formula")` |
| `math_inline` ($...$) | Inline | `st_latex(r"formula")` apres le paragraphe |
| `image` | Inline | `st_image(uri=path)` |
| `table_open` | Block | `st_grid(cols=N)` ou `stx.st_table()` |
| `blockquote_open` | Block | `with st_block(bs.quote):` |
| `strong_open` | Inline | `(s.bold, text)` tuple |
| `em_open` | Inline | `(s.italic, text)` tuple |
| `s_open` (strikethrough) | Inline | `(s.text.decorations.strikethrough, text)` tuple |
| `link_open` | Inline | `st_write(style, text, link=url)` |
| `hr` | Block | `st_space("v", 2)` |
| `softbreak` | Inline | Espace |
| `hardbreak` | Inline | `st_br()` |
| `html_block` | Block | `stx.st_html(html_content)` (fallback) |
| `html_inline` | Inline | Ignore ou `st_html()` si significatif |
| `front_matter` | Meta | Extraction title/author/date pour book.py |

### 3.5 Structure du convertisseur

```
streamtex/
  md_converter/                      # Nouveau package
    __init__.py                      # API publique : convert_md_project()
    _parser.py                       # markdown-it-py setup + MdNode tree builder
    _model.py                        # Modele de donnees intermediaire (MdNode)
    _generator_minimal.py            # Generateur mode minimal -> blocs StreamTeX
    _generator_full.py               # Generateur mode full -> blocs StreamTeX
    _project_scaffold.py             # Generation de l'arborescence projet
    _style_mapper.py                 # Mapping elements Markdown -> styles StreamTeX
    _asset_manager.py                # Copie/resolution des images
    _front_matter.py                 # Extraction et parsing du front matter YAML
    __main__.py                      # CLI (python -m streamtex.md_converter)
    templates/                       # Templates Jinja2 pour generation code
      block.py.j2                    # Template d'un fichier bloc
      block_minimal.py.j2            # Template bloc mode minimal
      book.py.j2                     # Template du book.py
      styles.py.j2                   # Template des styles projet
      setup.py.j2                    # Template setup.py
      blocks_init.py.j2              # Template blocks/__init__.py
```

### 3.6 Alignement avec l'existant

| Composant existant | Utilisation dans le convertisseur |
|--------------------|----------------------------------|
| `st_markdown()` | Rendu Markdown natif (mode minimal) |
| `st_write()` | Rendu texte style (mode full) |
| `st_code()` | Rendu des blocs de code (les deux modes) |
| `st_latex()` | Rendu des formules math (les deux modes) |
| `st_image()` | Rendu des images (mode full) |
| `st_list()` | Rendu des listes (mode full) |
| `st_grid()` | Rendu des tableaux (mode full) |
| `st_block()` | Blockquotes et conteneurs (mode full) |
| `st_html()` | HTML brut inline (fallback) |
| `template_project/` | Scaffold de base pour le projet genere |
| `resolve_content()` | Pattern `file=` pour charger les .md (mode minimal) |

---

## 4. Modele de donnees intermediaire

### 4.1 MdNode — Arbre syntaxique

```python
"""Intermediate representation for parsed Markdown content."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class MdNodeType(Enum):
    """Types of Markdown content nodes."""
    DOCUMENT = "document"             # Racine
    HEADING = "heading"               # # Title, ## Subtitle, etc.
    PARAGRAPH = "paragraph"           # Texte libre
    TEXT = "text"                     # Texte brut (feuille)
    BOLD = "bold"                     # **bold**
    ITALIC = "italic"                # *italic*
    STRIKETHROUGH = "strikethrough"   # ~~strikethrough~~
    MONOSPACE = "monospace"           # `code`
    LINK = "link"                     # [text](url)
    IMAGE = "image"                   # ![alt](url)
    MATH_INLINE = "math_inline"       # $...$
    MATH_DISPLAY = "math_display"     # $$...$$
    CODE_BLOCK = "code_block"         # ```language ... ```
    LIST_UNORDERED = "list_ul"        # - item
    LIST_ORDERED = "list_ol"          # 1. item
    LIST_ITEM = "list_item"           # Element de liste
    TASK_ITEM = "task_item"           # - [ ] / - [x]
    TABLE = "table"                   # | A | B | ... |
    TABLE_ROW = "table_row"           # Ligne de tableau
    TABLE_CELL = "table_cell"         # Cellule de tableau
    BLOCKQUOTE = "blockquote"         # > quote
    HORIZONTAL_RULE = "hr"            # ---
    LINE_BREAK = "line_break"         # Saut de ligne
    HTML_BLOCK = "html_block"         # HTML brut (bloc)
    HTML_INLINE = "html_inline"       # HTML brut (inline)
    FRONT_MATTER = "front_matter"     # YAML front matter


@dataclass
class MdNode:
    """A node in the parsed Markdown document tree."""
    type: MdNodeType
    content: str = ""                         # Texte brut ou source
    children: list[MdNode] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    # Metadata keys par type :
    #   HEADING:       {"level": 1-6}
    #   CODE_BLOCK:    {"language": str, "info": str}
    #   IMAGE:         {"src": str, "alt": str, "title": str|None}
    #   LINK:          {"href": str, "title": str|None}
    #   TABLE:         {"cols": int, "alignments": list[str]}  # "left"|"center"|"right"
    #   TABLE_CELL:    {"align": str|None, "is_header": bool}
    #   TASK_ITEM:     {"checked": bool}
    #   FRONT_MATTER:  {"yaml": dict}  # Parsed YAML data
    #   HTML_BLOCK:    {"raw": str}


@dataclass
class MdDocument:
    """Top-level parsed Markdown document."""
    source_file: str = ""                     # Chemin du fichier source
    root: MdNode = field(default_factory=lambda: MdNode(MdNodeType.DOCUMENT))
    # Front matter metadata (extracted from YAML)
    title: str = ""
    author: str = ""
    date: str = ""
    extra_meta: dict = field(default_factory=dict)
    images_referenced: list[str] = field(default_factory=list)
```

### 4.2 Exemple d'arbre pour un document simple

Source Markdown :
```markdown
---
title: My Tutorial
author: Nicolas Guelfi
---

# Introduction

This is **bold** text with math $E=mc^2$.

- First item
- Second item

```python
print("hello")
```
```

Arbre MdNode :
```
DOCUMENT
  +- FRONT_MATTER (yaml: {title: "My Tutorial", author: "Nicolas Guelfi"})
  +- HEADING (level=1, content="Introduction")
  +- PARAGRAPH
  |    +- TEXT "This is "
  |    +- BOLD
  |    |    +- TEXT "bold"
  |    +- TEXT " text with math "
  |    +- MATH_INLINE "E=mc^2"
  |    +- TEXT "."
  +- LIST_UNORDERED
  |    +- LIST_ITEM
  |    |    +- TEXT "First item"
  |    +- LIST_ITEM
  |         +- TEXT "Second item"
  +- CODE_BLOCK (language="python", content='print("hello")')
```

---

## 5. Parseur : markdown-it-py walker

### 5.1 Configuration du parseur

```python
"""Markdown parser — markdown-it-py with GFM + math + front matter plugins."""

from __future__ import annotations
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from ._model import MdDocument, MdNode, MdNodeType


def _create_parser() -> MarkdownIt:
    """Create a configured markdown-it-py parser with all plugins."""
    md = (
        MarkdownIt("gfm-like")
        .use(dollarmath_plugin, double_inline=True)
        .use(front_matter_plugin)
        .use(tasklists_plugin)
    )
    return md
```

### 5.2 Walker SyntaxTreeNode -> MdNode

```python
def parse_markdown(source: str, source_file: str = "") -> MdDocument:
    """Parse Markdown source into a MdDocument.

    Parameters
    ----------
    source : str
        Markdown source text.
    source_file : str
        Original file path (for reference in generated code).

    Returns
    -------
    MdDocument
        Parsed document with MdNode tree.
    """
    md = _create_parser()
    tokens = md.parse(source)
    tree = SyntaxTreeNode(tokens)

    doc = MdDocument(source_file=source_file)

    for node in tree.children:
        md_node = _walk_node(node)
        if md_node is not None:
            # Extract front matter into document metadata
            if md_node.type == MdNodeType.FRONT_MATTER:
                _apply_front_matter(doc, md_node)
            else:
                doc.root.children.append(md_node)

    return doc


def _walk_node(node: SyntaxTreeNode) -> MdNode | None:
    """Convert a SyntaxTreeNode to a MdNode."""
    ntype = node.type

    # --- Block-level tokens ---

    if ntype == "heading":
        level = int(node.tag[1])  # h1 -> 1, h2 -> 2, etc.
        children = _walk_inline_children(node)
        text = _extract_text(node)
        return MdNode(
            type=MdNodeType.HEADING,
            content=text,
            children=children,
            metadata={"level": level},
        )

    elif ntype == "paragraph":
        children = _walk_inline_children(node)
        return MdNode(
            type=MdNodeType.PARAGRAPH,
            children=children,
        )

    elif ntype == "bullet_list":
        items = [_walk_node(child) for child in node.children]
        return MdNode(
            type=MdNodeType.LIST_UNORDERED,
            children=[i for i in items if i is not None],
        )

    elif ntype == "ordered_list":
        items = [_walk_node(child) for child in node.children]
        return MdNode(
            type=MdNodeType.LIST_ORDERED,
            children=[i for i in items if i is not None],
        )

    elif ntype == "list_item":
        children = []
        for child in node.children:
            n = _walk_node(child)
            if n is not None:
                children.append(n)
        # Check for task list item
        is_task = node.attrGet("class") == "task-list-item"
        checked = node.attrGet("checked") is not None
        if is_task:
            return MdNode(
                type=MdNodeType.TASK_ITEM,
                children=children,
                metadata={"checked": checked},
            )
        return MdNode(
            type=MdNodeType.LIST_ITEM,
            children=children,
        )

    elif ntype == "fence":
        info = node.info.strip() if node.info else ""
        return MdNode(
            type=MdNodeType.CODE_BLOCK,
            content=node.content.rstrip("\n"),
            metadata={"language": info},
        )

    elif ntype == "code_block":
        return MdNode(
            type=MdNodeType.CODE_BLOCK,
            content=node.content.rstrip("\n"),
            metadata={"language": ""},
        )

    elif ntype == "math_block" or ntype == "math_block_double":
        return MdNode(
            type=MdNodeType.MATH_DISPLAY,
            content=node.content.strip(),
        )

    elif ntype == "blockquote":
        children = []
        for child in node.children:
            n = _walk_node(child)
            if n is not None:
                children.append(n)
        return MdNode(
            type=MdNodeType.BLOCKQUOTE,
            children=children,
        )

    elif ntype == "table":
        return _walk_table(node)

    elif ntype == "hr":
        return MdNode(type=MdNodeType.HORIZONTAL_RULE)

    elif ntype == "html_block":
        return MdNode(
            type=MdNodeType.HTML_BLOCK,
            content=node.content,
            metadata={"raw": node.content},
        )

    elif ntype == "front_matter":
        return _walk_front_matter(node)

    return None


def _walk_inline_children(node: SyntaxTreeNode) -> list[MdNode]:
    """Walk inline children of a block node."""
    children = []
    if node.children:
        for child in node.children:
            if child.type == "inline":
                children.extend(_walk_inline_node(child))
            else:
                n = _walk_node(child)
                if n is not None:
                    children.append(n)
    return children


def _walk_inline_node(node: SyntaxTreeNode) -> list[MdNode]:
    """Walk inline-level tokens."""
    results = []
    if not node.children:
        # Leaf text node
        if node.content:
            results.append(MdNode(type=MdNodeType.TEXT, content=node.content))
        return results

    for child in node.children:
        ntype = child.type

        if ntype == "text":
            results.append(MdNode(type=MdNodeType.TEXT, content=child.content))

        elif ntype == "softbreak":
            results.append(MdNode(type=MdNodeType.TEXT, content=" "))

        elif ntype == "hardbreak":
            results.append(MdNode(type=MdNodeType.LINE_BREAK))

        elif ntype == "strong":
            inline_children = _walk_inline_node(child)
            results.append(MdNode(
                type=MdNodeType.BOLD,
                children=inline_children,
            ))

        elif ntype == "em":
            inline_children = _walk_inline_node(child)
            results.append(MdNode(
                type=MdNodeType.ITALIC,
                children=inline_children,
            ))

        elif ntype == "s":  # strikethrough
            inline_children = _walk_inline_node(child)
            results.append(MdNode(
                type=MdNodeType.STRIKETHROUGH,
                children=inline_children,
            ))

        elif ntype == "code_inline":
            results.append(MdNode(
                type=MdNodeType.MONOSPACE,
                content=child.content,
            ))

        elif ntype == "math_inline" or ntype == "math_inline_double":
            results.append(MdNode(
                type=MdNodeType.MATH_INLINE,
                content=child.content,
            ))

        elif ntype == "link":
            href = child.attrGet("href") or ""
            title = child.attrGet("title")
            text = _extract_text(child)
            inline_children = _walk_inline_node(child)
            results.append(MdNode(
                type=MdNodeType.LINK,
                content=text,
                children=inline_children,
                metadata={"href": href, "title": title},
            ))

        elif ntype == "image":
            src = child.attrGet("src") or ""
            alt = child.attrGet("alt") or child.content or ""
            title = child.attrGet("title")
            results.append(MdNode(
                type=MdNodeType.IMAGE,
                content=alt,
                metadata={"src": src, "alt": alt, "title": title},
            ))

        elif ntype == "html_inline":
            results.append(MdNode(
                type=MdNodeType.HTML_INLINE,
                content=child.content,
            ))

        else:
            # Recurse for unknown inline containers
            results.extend(_walk_inline_node(child))

    return results


def _walk_table(node: SyntaxTreeNode) -> MdNode:
    """Convert a table SyntaxTreeNode to a MdNode table."""
    table_node = MdNode(type=MdNodeType.TABLE)
    # Extract alignment from thead cells if available
    alignments = []

    for child in node.children:
        if child.type in ("thead", "tbody"):
            for row_node in child.children:
                if row_node.type == "tr":
                    row = MdNode(type=MdNodeType.TABLE_ROW)
                    is_header = child.type == "thead"
                    for cell_node in row_node.children:
                        align = cell_node.attrGet("style")  # e.g. "text-align:center"
                        cell_children = _walk_inline_children(cell_node)
                        text = _extract_text(cell_node)
                        cell = MdNode(
                            type=MdNodeType.TABLE_CELL,
                            content=text,
                            children=cell_children,
                            metadata={"align": align, "is_header": is_header},
                        )
                        row.children.append(cell)
                        if is_header and align:
                            alignments.append(align)
                    table_node.children.append(row)

    # Store column count and alignments
    if table_node.children:
        first_row = table_node.children[0]
        table_node.metadata["cols"] = len(first_row.children)
        table_node.metadata["alignments"] = alignments

    return table_node


def _walk_front_matter(node: SyntaxTreeNode) -> MdNode:
    """Parse YAML front matter."""
    import yaml
    try:
        data = yaml.safe_load(node.content) or {}
    except Exception:
        data = {}
    return MdNode(
        type=MdNodeType.FRONT_MATTER,
        content=node.content,
        metadata={"yaml": data},
    )


def _apply_front_matter(doc: MdDocument, node: MdNode) -> None:
    """Apply front matter metadata to the document."""
    data = node.metadata.get("yaml", {})
    doc.title = data.get("title", "")
    doc.author = data.get("author", "")
    doc.date = data.get("date", "")
    doc.extra_meta = {k: v for k, v in data.items() if k not in ("title", "author", "date")}


def _extract_text(node: SyntaxTreeNode) -> str:
    """Extract plain text from a SyntaxTreeNode (recursively)."""
    if node.content:
        return node.content
    parts = []
    if node.children:
        for child in node.children:
            parts.append(_extract_text(child))
    return "".join(parts)


def parse_markdown_file(path: str, encoding: str = "utf-8") -> MdDocument:
    """Parse a .md file into a MdDocument."""
    from pathlib import Path
    source = Path(path).read_text(encoding=encoding)
    return parse_markdown(source, source_file=path)
```

---

## 6. Generateur mode minimal

### 6.1 Principe

Chaque titre de niveau 1 (`# Title`) definit un bloc StreamTeX. Le contenu Markdown entre deux titres de niveau 1 est passe directement a `st_markdown()`. Exceptions : les blocs de code et les formules display math sont extraits pour un meilleur rendu.

### 6.2 Segmentation

```python
def segment_minimal(doc: MdDocument) -> list[BlockSpec]:
    """Segment a document into blocks for minimal mode.

    Rules:
    - 1 heading de niveau 1 = 1 bloc
    - S'il n'y a pas de heading -> 1 seul bloc pour tout le document
    - Les blocs de code sont extraits vers st_code() (meilleur controle)
    - Les formules display math sont extraites vers st_latex()
    - Le reste est rendu via st_markdown()
    """
```

### 6.3 Strategie de rendu minimal

| Element Markdown | Traitement minimal |
|------------------|--------------------|
| `# Title` | Extrait pour TOC StreamTeX (`st_write` + `toc_lvl`), separateur de blocs |
| `## - ######` | Inclus dans `st_markdown()` (Streamlit rend les sous-titres) |
| Texte, listes, liens, images | Inclus dans `st_markdown()` |
| `**bold**`, `*italic*` | Inclus dans `st_markdown()` |
| `$...$` | Inclus dans `st_markdown()` (Streamlit supporte LaTeX inline) |
| `$$...$$` | **Extrait** → `st_latex(r"...")` (meilleur rendu isole) |
| `` ```language `` | **Extrait** → `st_code(bs.code_box, code=..., language=...)` |
| `| table |` | Inclus dans `st_markdown()` (Streamlit rend les tables GFM) |
| `> blockquote` | Inclus dans `st_markdown()` |
| `![alt](img)` | Inclus dans `st_markdown()` + copie image dans `static/` |
| `---` | Inclus dans `st_markdown()` |
| HTML inline | Inclus dans `st_markdown(unsafe_allow_html=True)` |
| Front matter YAML | Extrait → titre book.py, metadata |

### 6.4 Exemple de bloc genere (mode minimal)

Source Markdown (section "Introduction") :
```markdown
# Introduction

This is **bold** text with a [link](https://example.com).

## Details

Some details here with math $E=mc^2$.

```python
def hello():
    print("Hello, world!")
```

$$\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}$$
```

Bloc genere (`bck_01_introduction.py`) :
```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Introduction — converted from Markdown (minimal mode)."""
    heading = s.project.titles.section_title + s.center_txt
    code_box = s.project.containers.code_box
bs = BlockStyles

_MD_CONTENT = r"""
This is **bold** text with a [link](https://example.com).

## Details

Some details here with math $E=mc^2$.
"""


def build():
    st_write(bs.heading, "Introduction", tag=t.div, toc_lvl="1")
    st_space("v", 1)
    stx.st_markdown(_MD_CONTENT)
    st_space("v", 1)
    stx.st_code(bs.code_box, code='def hello():\n    print("Hello, world!")', language="python")
    st_space("v", 1)
    stx.st_latex(r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}")
```

### 6.5 Variante : fichiers .md externes

En mode minimal, les fichiers Markdown source peuvent etre conserves et charges via `file=` :

```python
def build():
    st_write(bs.heading, "Introduction", tag=t.div, toc_lvl="1")
    st_space("v", 1)
    stx.st_markdown(file="sections/introduction.md")
```

Cela permet de continuer a editer le contenu en Markdown apres la conversion. Le flag `--keep-md-files` active ce mode.

---

## 7. Generateur mode full StreamTeX

### 7.1 Principe

Chaque noeud de l'arbre `MdNode` est traduit vers un appel StreamTeX natif. Le code Python genere est du StreamTeX pur, entierement stylable.

### 7.2 Table de correspondance

| MdNode type | Code StreamTeX genere |
|-------------|----------------------|
| `HEADING` (level=1) | `st_write(bs.heading, "Title", tag=t.div, toc_lvl="1")` |
| `HEADING` (level=2) | `st_write(bs.sub, "Title", toc_lvl="+1")` |
| `HEADING` (level=3-6) | `st_write(bs.subsub, "Title", toc_lvl="+1")` |
| `PARAGRAPH` | `st_write(bs.content, *inlines)` |
| `TEXT` | Texte brut dans `st_write()` |
| `BOLD` | `(s.bold, "text")` dans un tuple inline |
| `ITALIC` | `(s.italic, "text")` dans un tuple inline |
| `STRIKETHROUGH` | `(bs.strikethrough, "text")` dans un tuple inline |
| `MONOSPACE` | `(s.text.fonts.monospace, "text")` dans un tuple inline |
| `LINK` | `st_write(bs.content, "text", link="url")` |
| `IMAGE` | `stx.st_image(uri="path")` |
| `MATH_INLINE` | `stx.st_latex(r"formula")` apres le paragraphe |
| `MATH_DISPLAY` | `stx.st_latex(r"formula")` bloc centre |
| `CODE_BLOCK` | `stx.st_code(bs.code_box, code=..., language=...)` |
| `LIST_UNORDERED` | `with st_list(list_type=lt.unordered, li_style=bs.content) as l:` |
| `LIST_ORDERED` | `with st_list(list_type=lt.ordered, li_style=bs.content) as l:` |
| `LIST_ITEM` | `with l.item(): st_write("text")` |
| `TASK_ITEM` | `with l.item(): st_write("[ ] " or "[x] " + text)` |
| `TABLE` | `with st_grid(cols=N) as g:` + cellules |
| `BLOCKQUOTE` | `with st_block(bs.quote):` + contenu |
| `HORIZONTAL_RULE` | `st_space("v", 2)` |
| `LINE_BREAK` | `st_br()` |
| `HTML_BLOCK` | `stx.st_html(html)  # TODO: convert to StreamTeX` |

### 7.3 Gestion du texte mixte (inline)

Meme defi que pour le convertisseur LaTeX : un paragraphe Markdown peut contenir du texte, du gras, de l'italique, du code inline et des maths dans la meme ligne.

```markdown
This is **bold** and *italic* with `code` and $x^2$ math.
```

**Strategie** : Utiliser les tuples inline de `st_write()` :

```python
# Le texte et le formatage inline sont dans un seul st_write()
st_write(
    bs.content,
    "This is ",
    (s.bold, "bold"),
    " and ",
    (s.italic, "italic"),
    " with ",
    (s.text.fonts.monospace, "code"),
    " and math:",
)
# Les formules math sont rendues separement
stx.st_latex(r"x^2")
```

**Seuil de fallback** : Si un paragraphe contient > 3 formules math inline, basculer vers `st_markdown()` pour la lisibilite :

```python
# Paragraphe avec beaucoup de math inline -> fallback st_markdown()
stx.st_markdown(r"This is text with $x^2$, $y^2$, $z^2$, and $w^2$ everywhere.")
```

### 7.4 Exemple de bloc genere (mode full)

Source Markdown :
```markdown
# Introduction

This is a **bold** statement with math: $E=mc^2$.

- First item
- Second item with *emphasis*

```python
print("hello")
```

| Name | Value |
|------|-------|
| Pi   | 3.14  |
| e    | 2.72  |
```

Bloc genere (`bck_01_introduction.py`) :
```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """Introduction — converted from Markdown (full StreamTeX mode)."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    content = s.large
    code_box = s.project.containers.code_box
    quote = s.project.containers.info_box
bs = BlockStyles


def build():
    st_write(bs.heading, "Introduction", tag=t.div, toc_lvl="1")
    st_space("v", 1)

    # Paragraph with inline formatting
    st_write(bs.content, "This is a ", (s.bold, "bold"), " statement with math:")
    stx.st_latex(r"E=mc^2")
    st_space("v", 1)

    # List
    with st_list(list_type=lt.unordered, li_style=bs.content) as l:
        with l.item():
            st_write("First item")
        with l.item():
            st_write("Second item with ", (s.italic, "emphasis"))
    st_space("v", 1)

    # Code block
    stx.st_code(bs.code_box, code='print("hello")', language="python")
    st_space("v", 1)

    # Table
    with st_grid(cols=2, grid_style=s.project.containers.gap_8) as g:
        with g.cell():
            st_write(bs.content + s.bold, "Name")
        with g.cell():
            st_write(bs.content + s.bold, "Value")
        with g.cell():
            st_write(bs.content, "Pi")
        with g.cell():
            st_write(bs.content, "3.14")
        with g.cell():
            st_write(bs.content, "e")
        with g.cell():
            st_write(bs.content, "2.72")
```

### 7.5 Regles de fallback vers st_markdown()

Le generateur full bascule vers `st_markdown()` quand :

| Condition | Raison |
|-----------|--------|
| HTML inline complexe (`<div>`, `<table>`, `<form>`) | Pas d'equivalent StreamTeX |
| Paragraphe avec > 3 formules math inline | Lisibilite du code genere |
| Listes imbriquees > 2 niveaux | st_list ne gere pas l'imbrication profonde |
| Tableau avec cellules contenant du formatage complexe | st_grid simple ne gere pas |
| Elements Markdown non reconnus | Catch-all |

---

## 8. Gestion des fichiers et assets

### 8.1 Images

| Cas | Traitement |
|-----|-----------|
| `![alt](images/photo.png)` | Copie dans `static/images/photo.png`, genere `st_image(uri="images/photo.png")` |
| `![alt](https://example.com/img.png)` | URL conservee telle quelle : `st_image(uri="https://...")` |
| Chemin relatif au .md | Resolu relativement au fichier source |
| Image non trouvee | Warning + commentaire `# TODO: image not found: path` |

### 8.2 Multi-fichiers Markdown

Le convertisseur accepte un dossier contenant plusieurs `.md` :

```bash
uv run python -m streamtex.md_converter docs/ --output ./my_project/
```

**Strategie d'assemblage** :

| Cas | Traitement |
|-----|-----------|
| Un seul fichier `.md` | 1 fichier = 1 projet, sections = blocs |
| Plusieurs fichiers `.md` | 1 fichier = 1 ou N blocs (selon les `# Title`) |
| Fichier `index.md` ou `README.md` | Premier bloc du projet |
| Ordre des fichiers | Alphabetique par defaut, ou via `--order file1.md,file2.md` |
| Front matter `order: N` | Permet de specifier l'ordre dans le front matter |

### 8.3 Arborescence du projet genere

```
output_project/
  book.py                       # st_book() avec tous les blocs
  setup.py                      # sys.path setup
  blocks/
    __init__.py                 # ProjectBlockRegistry
    helpers.py                  # BlockHelperConfig (si mode full)
    bck_01_introduction.py      # 1 bloc par section h1
    bck_02_getting_started.py
    bck_03_advanced.py
    ...
  custom/
    styles.py                   # Styles projet
    themes.py                   # Theme dark (template par defaut)
  static/
    images/                     # Images copiees depuis les sources Markdown
    sections/                   # Fichiers .md originaux (si --keep-md-files)
  .streamlit/
    config.toml                 # enableStaticServing = true
```

---

## 9. CLI et integration

### 9.1 Interface en ligne de commande

```bash
# Conversion standard (mode minimal, un fichier)
uv run python -m streamtex.md_converter input.md --output ./my_project/

# Mode minimal explicite
uv run python -m streamtex.md_converter input.md --mode minimal --output ./my_project/

# Mode full StreamTeX
uv run python -m streamtex.md_converter input.md --mode full --output ./my_project/

# Dossier contenant plusieurs .md
uv run python -m streamtex.md_converter docs/ --output ./my_project/

# Conserver les fichiers .md (mode minimal avec file=)
uv run python -m streamtex.md_converter input.md --mode minimal --keep-md-files --output ./my_project/

# Options
uv run python -m streamtex.md_converter input.md \
    --mode full \
    --output ./my_project/ \
    --encoding utf-8 \
    --title "My Tutorial" \
    --page-width 90 \
    --paginate              # Force paginated mode
    --no-paginate           # Force continuous mode
    --order "intro.md,setup.md,advanced.md"  # Ordre des fichiers
```

### 9.2 API Python

```python
from streamtex.md_converter import convert_md_project, MdConversionConfig

config = MdConversionConfig(
    source="input.md",           # Fichier ou dossier
    output_dir="./my_project/",
    mode="minimal",              # ou "full"
    encoding="utf-8",
    title="My Tutorial",         # Override le titre front matter
    paginate=None,               # None = auto (False par defaut)
    page_width=90,
    keep_md_files=False,         # Conserver les .md dans static/sections/
    file_order=None,             # None = alphabetique
)

result = convert_md_project(config)
print(f"Generated {result.block_count} blocks")
print(f"Warnings: {result.warnings}")
```

### 9.3 Resultat de conversion

```python
@dataclass
class MdConversionResult:
    """Result of a Markdown to StreamTeX conversion."""
    output_dir: str                     # Chemin du projet genere
    block_count: int                    # Nombre de blocs generes
    blocks: list[str]                   # Noms des fichiers bloc
    mode: str                           # "minimal" ou "full"
    source_files: list[str]             # Fichiers .md traites
    warnings: list[str]                 # Avertissements
    fallback_count: int                 # Nombre de fallback vers st_markdown() (mode full)
    front_matter: dict                  # Metadata extraites du front matter
```

### 9.4 Integration slash commands

Ajouter une slash command dans `.claude/commands/migration/` :

| Commande | Fichier | Role |
|----------|---------|------|
| `/migration:md-convert` | `md-convert.md` | Conversion de fichier(s) Markdown vers StreamTeX |

---

## 10. Fichiers a creer/modifier

### Fichiers nouveaux

| Fichier | Lignes estimees | Role |
|---------|-----------------|------|
| `streamtex/md_converter/__init__.py` | ~30 | API publique : `convert_md_project()`, `MdConversionConfig`, `MdConversionResult` |
| `streamtex/md_converter/_model.py` | ~70 | `MdNodeType`, `MdNode`, `MdDocument` |
| `streamtex/md_converter/_parser.py` | ~300 | markdown-it-py setup + MdNode tree walker |
| `streamtex/md_converter/_generator_minimal.py` | ~180 | Generateur mode minimal -> blocs StreamTeX |
| `streamtex/md_converter/_generator_full.py` | ~350 | Generateur mode full -> blocs StreamTeX |
| `streamtex/md_converter/_project_scaffold.py` | ~120 | Generation book.py, setup.py, custom/, blocks/__init__.py |
| `streamtex/md_converter/_style_mapper.py` | ~60 | Mapping elements Markdown -> styles StreamTeX |
| `streamtex/md_converter/_asset_manager.py` | ~80 | Copie images, resolution chemins |
| `streamtex/md_converter/_front_matter.py` | ~40 | Extraction et parsing du front matter YAML |
| `streamtex/md_converter/__main__.py` | ~70 | CLI argparse |
| `streamtex/md_converter/templates/block.py.j2` | ~40 | Template Jinja2 pour un bloc (mode full) |
| `streamtex/md_converter/templates/block_minimal.py.j2` | ~25 | Template bloc (mode minimal) |
| `streamtex/md_converter/templates/book.py.j2` | ~50 | Template du book.py |
| `streamtex/md_converter/templates/styles.py.j2` | ~60 | Template des styles projet |
| `streamtex/md_converter/templates/setup.py.j2` | ~10 | Template pour setup.py |
| `streamtex/md_converter/templates/blocks_init.py.j2` | ~15 | Template pour blocks/__init__.py |
| `tests/test_md_converter_parser.py` | ~200 | Tests walker markdown-it-py |
| `tests/test_md_converter_minimal.py` | ~150 | Tests generateur minimal |
| `tests/test_md_converter_full.py` | ~200 | Tests generateur full |
| `tests/test_md_converter_scaffold.py` | ~100 | Tests generation projet |
| `tests/test_md_converter_integration.py` | ~100 | Tests end-to-end (.md -> projet complet) |
| `.claude/commands/migration/md-convert.md` | ~20 | Slash command |

### Fichiers modifies

| Fichier | Modification |
|---------|-------------|
| `streamtex/__init__.py` | Ajouter import : `from .md_converter import convert_md_project, MdConversionConfig, MdConversionResult` |
| `CLAUDE.md` | Ajouter section md_converter dans Key Components + workflow |
| `documentation/streamtex_cheatsheet_en.md` | Ajouter section "Markdown Import" |
| `pyproject.toml` | Ajouter dependances optionnelles `markdown-it-py`, `mdit-py-plugins`, `jinja2` (groupe `md-converter`) |

### Total estime

- **~1 500 lignes de code** (converter + templates)
- **~750 lignes de tests**
- **22 fichiers nouveaux** + **4 fichiers modifies**

---

## 11. Plan d'implementation

### Phase 1 : Fondation (2-3 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 1.1 | Modele de donnees (`_model.py`) | `_model.py` |
| 1.2 | Parseur markdown-it-py (`_parser.py`) | `_parser.py`, `tests/test_md_converter_parser.py` |
| 1.3 | Front matter extraction (`_front_matter.py`) | `_front_matter.py` |
| 1.4 | Scaffold projet (`_project_scaffold.py`) + templates | `_project_scaffold.py`, `templates/*.j2`, `tests/test_md_converter_scaffold.py` |
| 1.5 | Generateur minimal (`_generator_minimal.py`) | `_generator_minimal.py`, `tests/test_md_converter_minimal.py` |
| 1.6 | CLI basique (`__main__.py`, `__init__.py`) | `__main__.py`, `__init__.py` |

**Livrable** : Conversion d'un fichier Markdown simple en mode minimal -> projet StreamTeX fonctionnel.

### Phase 2 : Mode full (3-4 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 2.1 | Style mapper (`_style_mapper.py`) | `_style_mapper.py` |
| 2.2 | Generateur full — texte, listes, headings | `_generator_full.py`, `tests/test_md_converter_full.py` |
| 2.3 | Generateur full — images, code blocks, math | Extension `_generator_full.py` |
| 2.4 | Generateur full — tables, blockquotes, task lists | Extension `_generator_full.py` |
| 2.5 | Asset manager (`_asset_manager.py`) | `_asset_manager.py` |

**Livrable** : Conversion d'un fichier Markdown complexe en mode full -> projet StreamTeX natif.

### Phase 3 : Multi-fichiers et polish (2-3 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 3.1 | Support multi-fichiers (dossier de .md) | Extension `_parser.py`, `__main__.py` |
| 3.2 | Option `--keep-md-files` | Extension `_generator_minimal.py` |
| 3.3 | Tests d'integration end-to-end | `tests/test_md_converter_integration.py` |
| 3.4 | Documentation (cheatsheet, CLAUDE.md) | Fichiers modifies |
| 3.5 | Slash command | `.claude/commands/migration/md-convert.md` |

**Livrable** : Outil complet, documente, teste.

**Total estime : 7-10 jours**

---

## 12. Tests

### 12.1 Strategie

```
Tests unitaires (automatises, pytest)
  +- test_md_converter_parser.py       -> Parsing Markdown -> MdNode tree
  +- test_md_converter_minimal.py      -> Generation mode minimal
  +- test_md_converter_full.py         -> Generation mode full
  +- test_md_converter_scaffold.py     -> Generation arborescence projet
  +- test_md_converter_integration.py  -> End-to-end (.md -> projet fonctionnel)

Fichiers de test Markdown (fixtures)
  +- tests/fixtures/simple_doc.md
  +- tests/fixtures/complex_doc.md
  +- tests/fixtures/doc_with_math.md
  +- tests/fixtures/doc_with_tables.md
  +- tests/fixtures/doc_with_front_matter.md
  +- tests/fixtures/multi_file_docs/
       +- index.md
       +- chapter1.md
       +- chapter2.md
```

### 12.2 Tests du parseur (~35 tests)

| Classe | Tests |
|--------|-------|
| `TestParseHeadings` | h1-h6, content extraction, level metadata |
| `TestParseParagraphs` | simple text, multi-paragraph, empty paragraphs |
| `TestParseInlineFormatting` | bold, italic, strikethrough, code inline, nested bold+italic |
| `TestParseMath` | inline $, display $$, multiple formulas |
| `TestParseCodeBlocks` | fenced with language, fenced without language, indented code |
| `TestParseLists` | unordered, ordered, nested 1 level, task lists (checked/unchecked) |
| `TestParseImages` | local path, URL, alt text, title |
| `TestParseLinks` | text+href, title, autolinks |
| `TestParseTables` | simple, with alignment, header row, multi-row |
| `TestParseBlockquotes` | simple, nested, with formatting inside |
| `TestParseHR` | horizontal rule detection |
| `TestParseFrontMatter` | YAML title/author/date, extra metadata, invalid YAML |
| `TestParseHTMLBlocks` | raw HTML block, inline HTML |
| `TestParseEmpty` | empty document, whitespace only |

### 12.3 Tests du generateur minimal (~20 tests)

| Classe | Tests |
|--------|-------|
| `TestMinimalSegmentation` | 1 h1 = 1 bloc, no h1 = 1 bloc, multiple h1 |
| `TestMinimalCodeExtraction` | code blocks extraits vers st_code() |
| `TestMinimalMathExtraction` | display math extrait vers st_latex() |
| `TestMinimalMarkdownPassthrough` | contenu passe a st_markdown() |
| `TestMinimalKeepMdFiles` | option --keep-md-files genere file= |
| `TestMinimalCodeGeneration` | Python syntaxiquement valide (ast.parse) |

### 12.4 Tests du generateur full (~30 tests)

| Classe | Tests |
|--------|-------|
| `TestFullHeadings` | h1 -> st_write + toc_lvl, h2 -> toc_lvl="+1" |
| `TestFullParagraphs` | paragraphes -> st_write(bs.content, ...) |
| `TestFullInlineStyles` | bold/italic/mono -> tuples inline |
| `TestFullMath` | inline -> st_latex(), display -> st_latex() |
| `TestFullCodeBlocks` | fence -> st_code(style, code=, language=) |
| `TestFullLists` | ul -> st_list(lt.unordered), ol -> st_list(lt.ordered) |
| `TestFullImages` | -> st_image(uri=) |
| `TestFullTables` | -> st_grid(cols=N) |
| `TestFullBlockquotes` | -> st_block(bs.quote) |
| `TestFullLinks` | -> st_write(style, text, link=url) |
| `TestFullFallback` | elements complexes -> st_markdown() |
| `TestFullCodeGeneration` | Python syntaxiquement valide (ast.parse) |

### 12.5 Tests d'integration (~10 tests)

| Test | Verification |
|------|-------------|
| `test_simple_doc_minimal` | Doc simple -> projet fonctionnel (ast.parse ok, fichiers presents) |
| `test_simple_doc_full` | Idem mode full |
| `test_doc_with_math` | Formules LaTeX converties correctement |
| `test_doc_with_tables` | Tables rendues (st_markdown ou st_grid) |
| `test_doc_with_images` | Images copiees dans static/ |
| `test_multi_file_minimal` | Dossier de .md -> projet multi-blocs |
| `test_multi_file_full` | Idem mode full |
| `test_front_matter_used` | Titre/auteur utilises dans book.py |
| `test_output_ruff_clean` | Code genere passe ruff check |
| `test_book_py_importable` | book.py genere est importable (ast.parse) |

### 12.6 Commandes

```bash
# Tests unitaires
uv run pytest tests/test_md_converter_parser.py -v
uv run pytest tests/test_md_converter_minimal.py -v
uv run pytest tests/test_md_converter_full.py -v
uv run pytest tests/test_md_converter_scaffold.py -v
uv run pytest tests/test_md_converter_integration.py -v

# Suite complete
uv run pytest tests/ -v

# Lint
uv run ruff check streamtex/md_converter/
```

---

## 13. Risques et mitigations

### R1 : Differences de rendu Markdown entre parseurs

**Description** : Le Markdown rendu par Streamlit (`st.markdown()`) et celui parse par markdown-it-py peuvent differer sur certains edge cases (indentation de listes, HTML inline, etc.).

**Mitigation** :
- markdown-it-py et Streamlit utilisent tous deux des parseurs CommonMark-compatibles
- Les differences sont mineures et limitees aux edge cases
- Le mode minimal passe le contenu directement a Streamlit (fidelite maximale)

### R2 : Math inline dans les paragraphes (mode full)

**Description** : Les formules `$...$` inline ne peuvent pas etre incluses dans les tuples `st_write()`. Elles necessitent un appel `st_latex()` separe, ce qui casse le flux du paragraphe.

**Mitigation** :
- Les paragraphes avec <= 3 formules : texte avant/apres chaque formule dans des `st_write()` separes
- Les paragraphes avec > 3 formules : fallback vers `st_markdown()` (meilleure lisibilite)
- Commentaire `# TODO: inline math split` pour revision manuelle

### R3 : Tables complexes

**Description** : Les tables Markdown avec du formatage dans les cellules (bold, code, liens) sont difficiles a rendre via `st_grid()`.

**Mitigation** :
- Tables simples (texte uniquement) → `st_grid()` avec `st_write()` par cellule
- Tables complexes → fallback `st_markdown()` ou `stx.st_table()` (export-aware)
- Le convertisseur detecte la complexite des cellules et choisit la strategie

### R4 : Images avec chemins relatifs

**Description** : Les chemins relatifs dans le Markdown (`![](../images/photo.png)`) doivent etre resolus par rapport au fichier source, puis copies dans `static/`.

**Mitigation** :
- Resolution basee sur `pathlib.Path` relative au fichier source
- Copie dans `static/images/` avec aplatissement des chemins
- Warning si le fichier image n'est pas trouve

### R5 : Front matter YAML invalide

**Description** : Le front matter peut contenir du YAML invalide ou des types inattendus.

**Mitigation** :
- `yaml.safe_load()` avec try/except (ignore le front matter invalide)
- Warning affiche avec le contenu problematique
- Valeurs par defaut pour title, author, date

---

## 14. Limitations connues

| ID | Limitation | Contournement |
|----|-----------|---------------|
| L1 | **Liens wiki Obsidian** (`[[page]]`) : non supportes | Pre-traitement pour convertir en liens standard `[page](page.md)` |
| L2 | **MDX composants React** : non supportes | Supprimer les composants MDX avant conversion |
| L3 | **Mermaid dans Markdown** (` ```mermaid `) : rendu comme code | Post-traitement : remplacer `st_code` par `st_mermaid` |
| L4 | **HTML inline complexe** (formulaires, scripts) : passe brut | Mode minimal : `unsafe_allow_html=True` / Mode full : `st_html()` |
| L5 | **Listes imbriquees > 2 niveaux** : st_list ne gere pas | Fallback vers `st_markdown()` |
| L6 | **Footnotes Markdown** (`[^1]`) : non supportes par defaut | Activer le plugin `footnote_plugin` de mdit-py-plugins (a ajouter) |
| L7 | **Admonitions/callouts** (Obsidian `> [!note]`) : non supportes | Pre-traitement ou plugin custom |

---

## 15. Criteres de validation

### Criteres fonctionnels (MUST)

- [ ] Conversion d'un fichier Markdown simple (3 sections, texte, listes) -> projet fonctionnel en mode minimal
- [ ] Conversion d'un fichier Markdown simple -> projet fonctionnel en mode full
- [ ] Conversion d'un dossier de fichiers .md -> projet multi-blocs
- [ ] Front matter YAML extrait et utilise (titre, auteur dans book.py)
- [ ] Blocs de code extraits vers `st_code()` (les deux modes)
- [ ] Formules math extraites vers `st_latex()` (les deux modes)
- [ ] Images copiees dans `static/images/`
- [ ] Tables GFM rendues (st_markdown ou st_grid)
- [ ] Code Python genere syntaxiquement valide (`ast.parse()` ok)
- [ ] Code Python genere passe `ruff check`
- [ ] CLI fonctionnelle : `uv run python -m streamtex.md_converter input.md --output dir/`
- [ ] Option `--keep-md-files` fonctionne (mode minimal avec `file=`)

### Criteres de qualite (SHOULD)

- [ ] Les blocs generes suivent les coding standards (BlockStyles class, build() function)
- [ ] Les styles generes sont coherents avec le systeme de styles StreamTeX
- [ ] Les noms de blocs sont lisibles (`bck_01_introduction.py`)
- [ ] La TOC genere est correcte (niveaux de heading preserves)
- [ ] Blocs Mermaid dans le Markdown detectes avec un `# TODO: use st_mermaid()` comment

### Criteres de test (MUST)

- [ ] > 95 tests unitaires passent
- [ ] Tests d'integration end-to-end passent
- [ ] Suite complete StreamTeX (892+ tests existants) ne regresse pas
- [ ] `uv run ruff check streamtex/md_converter/` sans erreur
