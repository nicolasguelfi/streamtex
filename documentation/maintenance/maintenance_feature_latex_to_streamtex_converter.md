# Plan de Maintenance : Conversion LaTeX/Beamer vers StreamTeX

> **Date** : 2026-02-28
> **Auteur** : Claude Code (assiste par Nicolas Guelfi)
> **Version** : 3.0
> **Statut** : Plan final — architecture Pandoc JSON AST + fallback regex
> **Pre-requis** : StreamTeX >= 0.2.0, module `streamtex.latex` (st_latex, st_latex_doc), module `streamtex.latex_utils`

---

## Table des matieres

1. [Probleme et objectif](#1-probleme-et-objectif)
2. [Les deux modes de conversion](#2-les-deux-modes-de-conversion)
3. [Architecture : Pandoc JSON AST + fallback regex](#3-architecture--pandoc-json-ast--fallback-regex)
4. [Modele de donnees intermediaire](#4-modele-de-donnees-intermediaire)
5. [Parseur : Pandoc walker + regex fallback](#5-parseur--pandoc-walker--regex-fallback)
6. [Generateur mode minimal](#6-generateur-mode-minimal)
7. [Generateur mode autonome](#7-generateur-mode-autonome)
8. [Conversion Beamer specifique](#8-conversion-beamer-specifique)
9. [Gestion des fichiers et assets](#9-gestion-des-fichiers-et-assets)
10. [CLI et integration](#10-cli-et-integration)
11. [Fichiers a creer/modifier](#11-fichiers-a-creermodifier)
12. [Plan d'implementation](#12-plan-dimplementation)
13. [Tests](#13-tests)
14. [Risques et mitigations](#14-risques-et-mitigations)
15. [Limitations connues](#15-limitations-connues)
16. [Criteres de validation](#16-criteres-de-validation)

---

## 1. Probleme et objectif

### Probleme

De nombreux utilisateurs possedent des projets LaTeX existants (articles, rapports, cours) ou des presentations Beamer qu'ils souhaitent migrer vers StreamTeX pour beneficier de l'interactivite, du deploiement web, et de la navigation enrichie. Aujourd'hui cette migration est 100% manuelle.

### Objectif

Fournir un outil Python en ligne de commande qui :

1. **Prend en entree** un fichier `.tex` (article/rapport) ou un fichier `.tex` Beamer (presentation)
2. **Genere en sortie** un projet StreamTeX complet et fonctionnel (`book.py`, `blocks/`, `custom/`, `setup.py`, etc.)
3. **Propose deux modes** de conversion selon le degre de transformation souhaite

### Perimetre

- **IN** : LaTeX standard (article, report, book), Beamer, packages courants (amsmath, graphicx, hyperref, listings, tabular, itemize/enumerate, theorem)
- **OUT** : Packages exotiques, macros custom complexes (`\newcommand` avec logique), classe memoir, packages PGF/TikZ avances (qui utilisent deja `st_tikz()`)

---

## 2. Les deux modes de conversion

### Mode Minimal (`--mode minimal`)

**Philosophie** : Garder le maximum de LaTeX, minimiser la transformation.

Utilise `st_latex()` et `st_latex_doc()` au maximum. Le projet StreamTeX sert de conteneur de navigation (pagination, TOC, markers) autour du contenu LaTeX existant.

```
Fichier .tex source
    -> Decoupage en fragments logiques (sections)
    -> Chaque fragment -> un bloc StreamTeX avec st_latex_doc(r"...", height=N)
    -> Les formules isolees -> st_latex(r"...")
    -> Les TikZ -> extraits via extract_tikz() -> st_tikz(r"...")
    -> Projet fonctionnel genere
```

**Avantages** :
- Conversion rapide et quasi-automatique
- Fidelite maximale au rendu LaTeX (LaTeX.js cote client)
- Effort minimal de revision post-conversion
- Ideal pour les contenus textuels denses (articles, rapports)

**Inconvenients** :
- Le contenu reste du LaTeX dans des iframes (pas natif Streamlit)
- Pas d'interactivite possible avec le contenu (widgets, toggle, etc.)
- Styles StreamTeX (themes, couleurs projet) non appliques au contenu LaTeX
- Limitations de LaTeX.js (pas de packages custom, pas de `\def`)

### Mode Autonome (`--mode autonomous`)

**Philosophie** : Convertir le maximum vers StreamTeX natif, utiliser LaTeX uniquement en dernier recours.

Chaque element LaTeX est traduit vers son equivalent StreamTeX. Le contenu resultant est du Python pur, stylable, interactif, exportable.

```
Fichier .tex source
    -> Parsing en arbre semantique (sections, paragraphes, listes, etc.)
    -> Chaque element -> appel StreamTeX natif :
        \section{Title}       -> st_write(bs.heading, "Title", toc_lvl="1")
        \textbf{bold}         -> st_write(s.bold, "bold")
        \begin{itemize}       -> st_list(list_type=lt.unordered)
        \begin{lstlisting}    -> st_code(style, code=..., language=...)
        $E=mc^2$              -> st_latex(r"E=mc^2")
        $$\int...$$           -> st_latex(r"\int...")
        \includegraphics      -> st_image(uri=...)
        \begin{tikzpicture}   -> st_tikz(r"...")
        \begin{tabular}       -> st_grid(cols=N)
    -> Seuls les elements non-convertibles -> st_latex_doc(r"...")
    -> Projet fonctionnel genere
```

**Avantages** :
- Contenu natif StreamTeX, stylable avec le systeme de styles
- Compatible themes (light/dark)
- Widgets interactifs possibles apres conversion
- Export HTML natif (pas d'iframe LaTeX.js)
- TOC, markers, recherche fonctionnent sur le texte natif

**Inconvenients** :
- Conversion plus complexe, necessite revision humaine
- Perte de certains details typographiques (espacement LaTeX fin, ligatures)
- Les formules mathematiques restent en `st_latex()` (inevitable)
- Certaines structures LaTeX n'ont pas d'equivalent exact

### Tableau comparatif

| Aspect | Mode Minimal | Mode Autonome |
|--------|-------------|---------------|
| **Effort de conversion** | Faible (~90% auto) | Moyen (~70% auto, 30% revision) |
| **Fidelite visuelle** | Haute (LaTeX.js) | Moyenne (StreamTeX natif) |
| **Interactivite** | Non (contenu dans iframes) | Oui (contenu natif) |
| **Stylabilite** | Non (CSS LaTeX.js separe) | Oui (styles StreamTeX) |
| **Themes light/dark** | Non (light_bg fixe) | Oui |
| **Export HTML** | iframe avec LaTeX.js | HTML natif |
| **Recherche textuelle** | Limitee (texte dans iframe) | Complete |
| **Cas d'usage ideal** | Migration rapide, consultation | Migration complete, formation interactive |

---

## 3. Architecture : Pandoc JSON AST + fallback regex

### 3.1 Choix du moteur de parsing

Le convertisseur repose sur **Pandoc** (via `pypandoc`) comme moteur principal de parsing LaTeX. Pandoc est le convertisseur de documents le plus mature et le mieux maintenu (Haskell, 2026). Il produit un **JSON AST** structure avec des noeuds types (`Header`, `Para`, `Math`, `CodeBlock`, `RawBlock`, `BulletList`, `OrderedList`, `Image`, `Table`, etc.).

| Critere | Pandoc JSON AST |
|---------|----------------|
| Dependances | `pypandoc` + binaire pandoc (ou `pypandoc_binary`) |
| Effort de developpement | ~200 lignes de walker AST |
| Couverture LaTeX | ~85-90% (gere des centaines de packages) |
| Macros custom | Partiel (expanse certaines macros simples) |
| Beamer | Oui (`pandoc -f beamer` reconnait les frames) |
| Math | Excellent (preserve le LaTeX math verbatim) |
| Bibliographie | Excellent (`--citeproc` gere BibTeX/BibLaTeX) |
| Maintenance | Faible (pandoc evolue independamment) |

Un **fallback regex** est conserve pour les utilisateurs ne souhaitant pas installer pandoc (~60-70% de couverture).

### 3.2 Pipeline de conversion

```
LaTeX/Beamer source
    |
    +- (1) Pre-extraction TikZ (via extract_tikz() existant)
    |      -> Les blocs TikZ sont retires AVANT pandoc
    |      -> Remplaces par des marqueurs __TIKZ_N__
    |      -> Rendus directement via st_tikz()
    |
    +- (2) Pandoc JSON AST (pipeline principale)
    |      pandoc -f latex -t json --citeproc
    |      -> AST riche avec types semantiques
    |      -> Walker Python -> LatexNode tree
    |      -> Couverture ~85-90% du contenu
    |
    +- (3) RawBlock fallback (elements non convertis par pandoc)
    |      -> Pandoc produit des noeuds "RawBlock" pour le LaTeX non reconnu
    |      -> Mode minimal : st_latex_doc(raw_content)
    |      -> Mode autonome : tentative regex, sinon st_latex_doc()
    |
    +- (4) Regex direct (fallback si pandoc absent)
           -> Si pypandoc/pandoc non installe
           -> Parseur regex basique
           -> Warning : "Install pandoc for better conversion quality"
```

### 3.3 Dependances

```toml
# pyproject.toml — groupe optionnel
[project.optional-dependencies]
converter = [
    "pypandoc>=1.14",        # Wrapper Python pour pandoc
    "pypandoc_binary>=1.14", # Pandoc binaire bundle (optionnel, evite install systeme)
    "jinja2>=3.1",           # Templates pour generation de code
]
```

L'utilisateur qui n'installe pas le groupe `converter` peut toujours utiliser le parseur regex (fallback).

**pypandoc_binary** : Package PyPI qui inclut le binaire pandoc. Evite a l'utilisateur de devoir installer pandoc via le gestionnaire de paquets systeme. `pypandoc` le detecte automatiquement.

### 3.4 Mapping Pandoc JSON AST -> StreamTeX

| Noeud Pandoc | Type | Mapping StreamTeX |
|-------------|------|-------------------|
| `Header` | Block | `st_write(style, title, toc_lvl=str(level))` |
| `Para` | Block | `st_write(style, *inlines)` |
| `Plain` | Block | `st_write(style, *inlines)` (sans paragraphe) |
| `BulletList` | Block | `st_list(list_type=lt.unordered)` |
| `OrderedList` | Block | `st_list(list_type=lt.ordered)` |
| `CodeBlock` | Block | `st_code(style, code=text, language=lang)` |
| `BlockQuote` | Block | `with st_block(bs.quote):` |
| `Table` | Block | `st_grid(cols=N)` |
| `Figure` / `Image` | Inline/Block | `st_image(uri=path)` |
| `RawBlock "latex"` | Block | `st_latex_doc(content)` (fallback) |
| `Math InlineMath` | Inline | `st_latex(formula)` |
| `Math DisplayMath` | Inline | `st_latex(formula)` (centre) |
| `Strong` | Inline | `(s.bold, text)` tuple |
| `Emph` | Inline | `(s.italic, text)` tuple |
| `Code` | Inline | `(s.text.fonts.monospace, text)` tuple |
| `Link` | Inline | `st_write(style, text, link=url)` |
| `Str` | Inline | Texte brut |
| `Space` | Inline | Espace |
| `SoftBreak` | Inline | Espace |
| `LineBreak` | Inline | `st_br()` |
| `Cite` | Inline | `st_cite(key)` |
| `Div` | Block | Conteneur (attributs preserves) |
| `Span` | Inline | Style inline (attributs preserves) |

Pour Beamer, pandoc avec `-f beamer` produit des `Header level 1` pour les titres de slides et preserve la structure des frames.

### 3.5 Exemple d'AST JSON pandoc

Pour `\section{Introduction}\textbf{Bold} text with $E=mc^2$.` :

```json
{
  "blocks": [
    {"t": "Header", "c": [1, ["introduction", [], []], [{"t": "Str", "c": "Introduction"}]]},
    {"t": "Para", "c": [
      {"t": "Strong", "c": [{"t": "Str", "c": "Bold"}]},
      {"t": "Space"},
      {"t": "Str", "c": "text"},
      {"t": "Space"},
      {"t": "Str", "c": "with"},
      {"t": "Space"},
      {"t": "Math", "c": [{"t": "InlineMath"}, "E=mc^2"]},
      {"t": "Str", "c": "."}
    ]}
  ]
}
```

Chaque noeud a un type (`t`) et un contenu (`c`). L'AST est riche, structure, et directement walkable en Python.

### 3.6 Structure du convertisseur

```
streamtex/
  converter/                         # Nouveau package
    __init__.py                      # API publique : convert_project()
    _pandoc_walker.py                # Walker Pandoc JSON AST -> LatexNode tree
    _regex_parser.py                 # Parseur regex fallback (si pandoc absent)
    _model.py                        # Modele de donnees intermediaire (LatexNode)
    _tikz_extractor.py               # Pre-extraction TikZ avant pandoc
    _generator_minimal.py            # Generateur mode minimal -> blocs StreamTeX
    _generator_autonomous.py         # Generateur mode autonome -> blocs StreamTeX
    _project_scaffold.py             # Generation de l'arborescence projet
    _beamer.py                       # Logique specifique Beamer
    _style_mapper.py                 # Mapping Pandoc AST / LaTeX -> styles StreamTeX
    _asset_manager.py                # Copie/resolution des images et fichiers
    __main__.py                      # CLI (python -m streamtex.converter)
    templates/                       # Templates Jinja2 pour generation code
      block.py.j2                    # Template d'un fichier bloc
      book.py.j2                     # Template du book.py
      styles.py.j2                   # Template des styles projet
      setup.py.j2                    # Template setup.py
      blocks_init.py.j2              # Template blocks/__init__.py
```

### 3.7 Alignement avec l'existant

| Composant existant | Utilisation dans le convertisseur |
|--------------------|----------------------------------|
| `latex_utils.extract_tikz()` | Extraction des blocs TikZ pour les isoler dans `st_tikz()` |
| `latex_utils.extract_math()` | Extraction des formules pour les isoler dans `st_latex()` |
| `latex_utils.extract_frames()` | Extraction des frames Beamer pour la segmentation |
| `latex_utils.is_full_document()` | Detection document complet vs fragment |
| `latex_utils.strip_document_wrapper()` | Extraction du body pour le mode minimal |
| `st_latex()` | Rendu des formules math (les deux modes) |
| `st_latex_doc()` | Rendu des fragments LaTeX (mode minimal) |
| `st_tikz()` | Rendu des diagrammes TikZ (les deux modes) |
| `template_project/` | Scaffold de base pour le projet genere |

---

## 4. Modele de donnees intermediaire

### 4.1 LatexNode — Arbre semantique

```python
"""Intermediate representation for parsed LaTeX content."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Types of LaTeX content nodes."""
    DOCUMENT = "document"         # Racine
    SECTION = "section"           # \section, \subsection, \subsubsection
    PARAGRAPH = "paragraph"       # Texte libre entre commandes
    TEXT = "text"                 # Texte brut (feuille)
    BOLD = "bold"                 # \textbf{...}
    ITALIC = "italic"            # \textit{...}, \emph{...}
    MONOSPACE = "monospace"       # \texttt{...}
    UNDERLINE = "underline"       # \underline{...}
    MATH_INLINE = "math_inline"   # $...$, \(...\)
    MATH_DISPLAY = "math_display" # $$...$$, \[...\], equation env
    LIST_UNORDERED = "list_ul"    # \begin{itemize}
    LIST_ORDERED = "list_ol"      # \begin{enumerate}
    LIST_ITEM = "list_item"       # \item
    CODE = "code"                 # \begin{lstlisting}, \begin{verbatim}
    IMAGE = "image"               # \includegraphics
    TABLE = "table"               # \begin{tabular}
    TABLE_ROW = "table_row"       # Ligne de tableau
    TABLE_CELL = "table_cell"     # Cellule de tableau
    TIKZ = "tikz"                 # \begin{tikzpicture}
    LINK = "link"                 # \href{url}{text}, \url{url}
    FOOTNOTE = "footnote"         # \footnote{...}
    CITATION = "citation"         # \cite{key}
    LABEL = "label"               # \label{key}
    REF = "ref"                   # \ref{key}
    QUOTE = "quote"               # \begin{quote}
    THEOREM = "theorem"           # \begin{theorem}, \begin{lemma}, etc.
    PROOF = "proof"               # \begin{proof}
    RAW_LATEX = "raw_latex"       # Non convertible — reste en LaTeX
    # Beamer specifique
    FRAME = "frame"               # \begin{frame}
    FRAME_TITLE = "frame_title"   # \frametitle{...}
    COLUMNS = "columns"           # \begin{columns}
    COLUMN = "column"             # \begin{column}{width}
    BLOCK_ENV = "block_env"       # \begin{block}{title}
    ALERT_BLOCK = "alert_block"   # \begin{alertblock}{title}
    PAUSE = "pause"               # \pause


@dataclass
class LatexNode:
    """A node in the parsed LaTeX document tree."""
    type: NodeType
    content: str = ""                         # Texte brut ou source LaTeX
    children: list[LatexNode] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    # Metadata keys par type :
    #   SECTION:  {"level": 1|2|3, "title": str}
    #   IMAGE:    {"path": str, "width": str|None, "caption": str|None}
    #   CODE:     {"language": str}
    #   TABLE:    {"cols": int, "alignment": str}  # "llcr" etc.
    #   LINK:     {"url": str}
    #   TIKZ:     {"preamble": str}
    #   CITATION: {"key": str}
    #   FRAME:    {"title": str, "options": str}
    #   COLUMN:   {"width": str}  # "0.5\textwidth" etc.
    #   THEOREM:  {"env_name": str, "title": str|None}  # "theorem", "lemma"...
    #   RAW_LATEX: {"reason": str}  # Pourquoi non convertible


@dataclass
class LatexDocument:
    """Top-level parsed LaTeX document."""
    documentclass: str              # "article", "report", "book", "beamer"
    packages: list[str]             # ["amsmath", "graphicx", ...]
    preamble_commands: list[str]    # \newcommand, \title, \author, etc.
    title: str = ""
    author: str = ""
    date: str = ""
    root: LatexNode = field(default_factory=lambda: LatexNode(NodeType.DOCUMENT))
    bibliography: str | None = None  # Chemin du .bib si present
    images_referenced: list[str] = field(default_factory=list)
```

### 4.2 Exemple d'arbre pour un document simple

Source LaTeX :
```latex
\documentclass{article}
\usepackage{amsmath}
\title{My Paper}
\begin{document}
\section{Introduction}
This is \textbf{bold} text with math $E=mc^2$.
\begin{itemize}
  \item First item
  \item Second item
\end{itemize}
\end{document}
```

Arbre LatexNode :
```
DOCUMENT
  +- SECTION (level=1, title="Introduction")
       +- PARAGRAPH
       |    +- TEXT "This is "
       |    +- BOLD
       |    |    +- TEXT "bold"
       |    +- TEXT " text with math "
       |    +- MATH_INLINE "$E=mc^2$"
       +- LIST_UNORDERED
            +- LIST_ITEM
            |    +- TEXT "First item"
            +- LIST_ITEM
                 +- TEXT "Second item"
```

---

## 5. Parseur : Pandoc walker + regex fallback

### 5.1 Architecture a deux niveaux

```
Couche 1 : _pandoc_walker.py (principal, si pandoc disponible)
    -> Appelle pypandoc pour convertir LaTeX en JSON AST
    -> Walk l'AST et construit l'arbre LatexNode
    -> Les noeuds RawBlock preservent le LaTeX non reconnu

Couche 2 : _regex_parser.py (fallback, si pandoc absent)
    -> Parseur regex basique
    -> Couverture reduite (~60-70%)
    -> Warning a l'utilisateur
```

### 5.2 Walker Pandoc JSON AST (`_pandoc_walker.py`)

```python
"""Pandoc JSON AST walker — converts pandoc output to LatexNode tree."""

from __future__ import annotations
import json
from ._model import LatexDocument, LatexNode, NodeType


def _has_pandoc() -> bool:
    """Check if pandoc is available via pypandoc."""
    try:
        import pypandoc
        pypandoc.get_pandoc_version()
        return True
    except (ImportError, OSError):
        return False


def parse_via_pandoc(
    source: str,
    input_format: str = "latex",
) -> LatexDocument:
    """Parse LaTeX/Beamer source via Pandoc JSON AST.

    Parameters
    ----------
    source : str
        LaTeX source code (body, preamble included).
    input_format : str
        Pandoc input format: "latex" or "beamer".

    Returns
    -------
    LatexDocument
        Parsed document with LatexNode tree.

    Raises
    ------
    RuntimeError
        If pandoc is not available.
    """
    import pypandoc

    # Convert to JSON AST
    ast_json = pypandoc.convert_text(
        source,
        to="json",
        format=input_format,
        extra_args=["--citeproc"] if "\\cite" in source else [],
    )
    ast = json.loads(ast_json)

    # Extract metadata (title, author, date)
    meta = ast.get("meta", {})
    doc = LatexDocument(
        documentclass=input_format,
        packages=[],
        preamble_commands=[],
        title=_extract_meta_string(meta.get("title")),
        author=_extract_meta_string(meta.get("author")),
        date=_extract_meta_string(meta.get("date")),
    )

    # Walk AST blocks
    for block in ast.get("blocks", []):
        node = _walk_block(block)
        if node is not None:
            doc.root.children.append(node)

    return doc


def _walk_block(block: dict) -> LatexNode | None:
    """Convert a Pandoc AST block node to a LatexNode."""
    t = block.get("t", "")
    c = block.get("c")

    if t == "Header":
        level, attrs, inlines = c
        text = _inlines_to_text(inlines)
        node = LatexNode(
            type=NodeType.SECTION,
            content=text,
            metadata={"level": level, "title": text},
        )
        return node

    elif t == "Para" or t == "Plain":
        children = [_walk_inline(i) for i in c]
        return LatexNode(
            type=NodeType.PARAGRAPH,
            children=[ch for ch in children if ch is not None],
        )

    elif t == "BulletList":
        return _walk_list(c, NodeType.LIST_UNORDERED)

    elif t == "OrderedList":
        _, items = c
        return _walk_list(items, NodeType.LIST_ORDERED)

    elif t == "CodeBlock":
        attrs, code = c
        lang = attrs[1][0] if attrs[1] else ""
        return LatexNode(
            type=NodeType.CODE,
            content=code,
            metadata={"language": lang},
        )

    elif t == "BlockQuote":
        children = [_walk_block(b) for b in c]
        return LatexNode(
            type=NodeType.QUOTE,
            children=[ch for ch in children if ch is not None],
        )

    elif t == "RawBlock":
        fmt, content = c
        if fmt == "latex":
            return LatexNode(
                type=NodeType.RAW_LATEX,
                content=content,
                metadata={"reason": "Pandoc RawBlock (unrecognized LaTeX)"},
            )
        return None

    elif t == "Table":
        return _walk_table(c)

    elif t == "Figure":
        # Pandoc 3.x Figure node
        return _walk_figure(c)

    elif t == "Div":
        attrs, blocks = c
        children = [_walk_block(b) for b in blocks]
        return LatexNode(
            type=NodeType.PARAGRAPH,  # Generic container
            children=[ch for ch in children if ch is not None],
        )

    return None


def _walk_inline(inline: dict) -> LatexNode | None:
    """Convert a Pandoc AST inline node to a LatexNode."""
    t = inline.get("t", "")
    c = inline.get("c")

    if t == "Str":
        return LatexNode(type=NodeType.TEXT, content=c)

    elif t == "Space" or t == "SoftBreak":
        return LatexNode(type=NodeType.TEXT, content=" ")

    elif t == "LineBreak":
        return LatexNode(type=NodeType.TEXT, content="\n")

    elif t == "Strong":
        children = [_walk_inline(i) for i in c]
        return LatexNode(
            type=NodeType.BOLD,
            children=[ch for ch in children if ch is not None],
        )

    elif t == "Emph":
        children = [_walk_inline(i) for i in c]
        return LatexNode(
            type=NodeType.ITALIC,
            children=[ch for ch in children if ch is not None],
        )

    elif t == "Code":
        _, text = c
        return LatexNode(type=NodeType.MONOSPACE, content=text)

    elif t == "Math":
        math_type, formula = c
        if math_type.get("t") == "DisplayMath":
            return LatexNode(type=NodeType.MATH_DISPLAY, content=formula)
        else:
            return LatexNode(type=NodeType.MATH_INLINE, content=formula)

    elif t == "Link":
        attrs, inlines, target = c
        url = target[0]
        text = _inlines_to_text(inlines)
        return LatexNode(
            type=NodeType.LINK,
            content=text,
            metadata={"url": url},
        )

    elif t == "Image":
        attrs, inlines, target = c
        path = target[0]
        alt = _inlines_to_text(inlines)
        return LatexNode(
            type=NodeType.IMAGE,
            content=alt,
            metadata={"path": path},
        )

    elif t == "Cite":
        citations, inlines = c
        keys = [cit["citationId"] for cit in citations]
        return LatexNode(
            type=NodeType.CITATION,
            content=", ".join(keys),
            metadata={"keys": keys},
        )

    elif t == "RawInline":
        fmt, content = c
        if fmt == "latex":
            return LatexNode(
                type=NodeType.RAW_LATEX,
                content=content,
                metadata={"reason": "Pandoc RawInline"},
            )

    return None


def _walk_list(items: list, list_type: NodeType) -> LatexNode:
    """Convert a Pandoc list to a LatexNode."""
    list_node = LatexNode(type=list_type)
    for item_blocks in items:
        item_children = [_walk_block(b) for b in item_blocks]
        item = LatexNode(
            type=NodeType.LIST_ITEM,
            children=[ch for ch in item_children if ch is not None],
        )
        list_node.children.append(item)
    return list_node


def _walk_table(c: list) -> LatexNode:
    """Convert a Pandoc Table node to a LatexNode."""
    # Pandoc 3.x table format: [attrs, caption, colspecs, head, bodies, foot]
    # Simplified: extract rows and cells
    node = LatexNode(type=NodeType.TABLE)
    # ... (implementation extracts rows/cells from Pandoc table structure)
    return node


def _walk_figure(c: list) -> LatexNode | None:
    """Convert a Pandoc Figure node to a LatexNode."""
    # Pandoc 3.x: [attrs, caption, blocks]
    # Look for Image inside the blocks
    # ... (implementation)
    return None


def _inlines_to_text(inlines: list) -> str:
    """Extract plain text from a list of Pandoc inline nodes."""
    parts = []
    for i in inlines:
        t = i.get("t", "")
        if t == "Str":
            parts.append(i["c"])
        elif t in ("Space", "SoftBreak"):
            parts.append(" ")
        elif t == "Strong" or t == "Emph":
            parts.append(_inlines_to_text(i["c"]))
    return "".join(parts)


def _extract_meta_string(meta_val: dict | None) -> str:
    """Extract a string from a Pandoc metadata value."""
    if meta_val is None:
        return ""
    t = meta_val.get("t", "")
    if t == "MetaInlines":
        return _inlines_to_text(meta_val.get("c", []))
    if t == "MetaList":
        parts = [_extract_meta_string(item) for item in meta_val.get("c", [])]
        return ", ".join(parts)
    return ""
```

### 5.3 Parseur regex fallback (`_regex_parser.py`)

Le parseur regex est conserve comme fallback pour les utilisateurs sans pandoc. Il gere les commandes basiques (sections, texte, listes, math, images). Les commandes non reconnues deviennent `RAW_LATEX`.

```python
"""Regex-based LaTeX parser — fallback when pandoc is not available."""

import warnings
from ._model import LatexDocument

_PANDOC_WARNING = (
    "Pandoc not found. Using regex fallback parser with reduced coverage (~60-70%). "
    "Install pandoc for better conversion: uv add --group converter pypandoc_binary"
)


def parse_via_regex(source: str) -> LatexDocument:
    """Parse LaTeX source via regex patterns (fallback).

    This parser handles basic LaTeX commands (sections, text formatting,
    lists, math, images) but cannot expand macros or handle complex
    structures. It is used only when pandoc is not available.
    """
    warnings.warn(_PANDOC_WARNING, stacklevel=2)
    # ... (implementation: regex patterns for \section, \textbf, \begin{itemize}, etc.)
```

### 5.4 Interface unifiee

```python
"""_parser.py — facade selecting pandoc or regex."""

from ._model import LatexDocument


def parse_latex(source: str, input_format: str = "latex") -> LatexDocument:
    """Parse LaTeX source into a LatexDocument.

    Uses Pandoc JSON AST if available, falls back to regex parser.
    """
    from ._pandoc_walker import _has_pandoc, parse_via_pandoc

    if _has_pandoc():
        return parse_via_pandoc(source, input_format)

    from ._regex_parser import parse_via_regex
    return parse_via_regex(source)


def parse_latex_file(path: str, encoding: str = "utf-8") -> LatexDocument:
    """Parse a .tex file into a LatexDocument."""
    from pathlib import Path
    source = Path(path).read_text(encoding=encoding)

    # Auto-detect beamer
    input_format = "beamer" if r"\documentclass" in source and "beamer" in source else "latex"
    return parse_latex(source, input_format)
```

### 5.5 Pre-extraction TikZ (`_tikz_extractor.py`)

Pandoc ne gere pas TikZ — il le produit comme `RawBlock`. Les blocs TikZ sont extraits **avant** l'envoi a pandoc et remplaces par des marqueurs :

```python
"""TikZ pre-extraction — removes TikZ blocks before pandoc processing."""

from streamtex.latex_utils import extract_tikz


def extract_and_replace_tikz(source: str) -> tuple[str, list[str]]:
    """Extract TikZ blocks and replace with markers.

    Returns
    -------
    tuple[str, list[str]]
        Modified source (TikZ replaced by __TIKZ_0__, __TIKZ_1__, ...)
        and list of extracted TikZ blocks.
    """
    tikz_blocks = extract_tikz(source)
    modified = source
    for i, block in enumerate(tikz_blocks):
        modified = modified.replace(block, f"__TIKZ_{i}__", 1)
    return modified, tikz_blocks
```

Les marqueurs `__TIKZ_N__` survivent au parsing pandoc (apparaissent comme texte brut dans un `Para`) et sont ensuite reinjectes comme noeuds `TIKZ` dans l'arbre `LatexNode`.

### 5.6 Strategie pour les elements non supportes

| Source | Noeud produit | Traitement generateur |
|--------|---------------|----------------------|
| Pandoc RawBlock | `RAW_LATEX` (content = LaTeX brut) | Minimal -> `st_latex_doc()` / Autonome -> tente regex puis `st_latex_doc()` |
| Pandoc RawInline | `RAW_LATEX` (content = commande LaTeX) | Inline dans le texte : `st_latex_doc()` si complexe, sinon ignore |
| Regex non reconnu | `RAW_LATEX` (content = ligne LaTeX) | Idem |

Le rapport de conversion inclut la liste de tous les `RAW_LATEX` avec leur contenu et leur raison, pour guider la revision manuelle.

---

## 6. Generateur mode minimal

### 6.1 Principe

Chaque section de niveau 1 devient un bloc StreamTeX. Le contenu de la section est passe **tel quel** a `st_latex_doc()`. Seuls les TikZ sont extraits et rendus via `st_tikz()`.

### 6.2 Segmentation

```python
def segment_minimal(doc: LatexDocument) -> list[BlockSpec]:
    """Segment a document into blocks for minimal mode.

    Rules:
    - 1 section de niveau 1 = 1 bloc
    - S'il n'y a pas de section -> 1 seul bloc pour tout le document
    - TikZ extraits dans des appels st_tikz() separes
    - Formules math restent dans st_latex_doc() (LaTeX.js les rend)
    """
```

### 6.3 Exemple de bloc genere (mode minimal)

Source LaTeX (section "Introduction") :
```latex
\section{Introduction}
This is a \textbf{bold} statement.
\begin{itemize}
  \item First item
  \item Second item
\end{itemize}
```

Bloc genere (`bck_01_introduction.py`) :
```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Introduction — converted from LaTeX (minimal mode)."""
    heading = s.project.titles.section_title + s.center_txt
bs = BlockStyles

_LATEX_CONTENT = r"""
\section{Introduction}
This is a \textbf{bold} statement.
\begin{itemize}
  \item First item
  \item Second item
\end{itemize}
"""


def build():
    st_write(bs.heading, "Introduction", tag=t.div, toc_lvl="1")
    st_space("v", 1)
    stx.st_latex_doc(_LATEX_CONTENT, height=300)
```

### 6.4 Regles specifiques mode minimal

| Element LaTeX | Traitement minimal |
|---------------|-------------------|
| `\section{Title}` | Extrait pour TOC StreamTeX (`st_write` + `toc_lvl`), contenu dans `st_latex_doc()` |
| `\subsection{Title}` | Inclus dans `st_latex_doc()` (LaTeX.js rend les sous-sections) |
| Texte, listes, tableaux | Inclus dans `st_latex_doc()` |
| `$...$`, `$$...$$` | Inclus dans `st_latex_doc()` (LaTeX.js rend les math) |
| `\begin{tikzpicture}` | **Extrait** -> `st_tikz(r"...", preamble=...)` |
| `\includegraphics{img}` | Inclus dans `st_latex_doc()` (LaTeX.js ne rend pas les images) + commentaire `# TODO: image` |
| `\bibliography{file}` | Commentaire `# TODO: configure bib_sources in book.py` |

### 6.5 Estimation de la hauteur des iframes

```python
def estimate_height(latex_content: str) -> int:
    """Estimate iframe height based on content length.

    Heuristic: ~20px per line of LaTeX source,
    minimum 150px, maximum 1200px.
    """
    lines = latex_content.strip().count("\n") + 1
    return max(150, min(1200, lines * 20))
```

---

## 7. Generateur mode autonome

### 7.1 Principe

Chaque noeud de l'arbre `LatexNode` est traduit vers un appel StreamTeX natif. Le code Python genere est du StreamTeX pur, sans iframe.

### 7.2 Table de correspondance

| LatexNode type | Code StreamTeX genere |
|----------------|----------------------|
| `SECTION` (level=1) | `st_write(bs.heading, "Title", tag=t.div, toc_lvl="1")` |
| `SECTION` (level=2) | `st_write(bs.sub, "Title", toc_lvl="+1")` |
| `SECTION` (level=3) | `st_write(bs.subsub, "Title", toc_lvl="+1")` |
| `PARAGRAPH` | Concatenation des enfants dans un `st_write()` |
| `TEXT` | Texte brut dans `st_write()` |
| `BOLD` | `(s.bold, "text")` dans un tuple inline |
| `ITALIC` | `(s.italic, "text")` dans un tuple inline |
| `MONOSPACE` | `(s.text.fonts.monospace, "text")` dans un tuple inline |
| `MATH_INLINE` | `stx.st_latex(r"formula")` apres le paragraphe |
| `MATH_DISPLAY` | `stx.st_latex(r"formula")` dans un bloc centre |
| `LIST_UNORDERED` | `with st_list(list_type=lt.unordered, li_style=bs.content) as l:` |
| `LIST_ORDERED` | `with st_list(list_type=lt.ordered, li_style=bs.content) as l:` |
| `LIST_ITEM` | `with l.item(): st_write("text")` |
| `CODE` | `stx.st_code(bs.code_box, code=..., language=...)` |
| `IMAGE` | `stx.st_image(uri="path")` |
| `TABLE` | `with st_grid(cols=N) as g:` + `with g.cell():` |
| `TIKZ` | `stx.st_tikz(r"...", preamble=...)` |
| `LINK` | `st_write(bs.link, "text", link="url")` |
| `QUOTE` | `with st_block(bs.quote):` + contenu |
| `THEOREM` | `with st_block(bs.theorem):` + titre + contenu |
| `FOOTNOTE` | Commentaire `# Footnote: text` (pas d'equivalent natif) |
| `CITATION` | `stx.st_cite("key")` si bib configure, sinon commentaire |
| `RAW_LATEX` | `stx.st_latex_doc(r"...", height=N)  # TODO: manual conversion` |

### 7.3 Gestion du texte mixte (inline)

Le defi principal : un paragraphe LaTeX peut contenir du texte, du gras, de l'italique et des maths dans la meme ligne.

```latex
This is \textbf{bold} and \emph{italic} with $x^2$ math.
```

**Strategie** : Utiliser les tuples inline de `st_write()` :

```python
st_write(
    bs.content,
    "This is ",
    (s.bold, "bold"),
    " and ",
    (s.italic, "italic"),
    " with math:",
)
stx.st_latex(r"x^2")
```

**Probleme** : Les formules math inline ne peuvent pas etre dans un tuple `st_write()` (elles necessitent `st_latex()`). La strategie est de :
1. Grouper le texte avant la formule dans un `st_write()`
2. Rendre la formule via `st_latex()`
3. Continuer avec le texte suivant

Pour les paragraphes avec beaucoup de math inline, un **fallback** vers `st_latex_doc()` est plus lisible :

```python
# Si le paragraphe contient > 3 formules inline -> fallback
stx.st_latex_doc(r"This is text with $x^2$, $y^2$, and $z^2$ everywhere.", height=60)
```

### 7.4 Exemple de bloc genere (mode autonome)

Source LaTeX :
```latex
\section{Introduction}
This is a \textbf{bold} statement with math: $E=mc^2$.

\begin{itemize}
  \item First item
  \item Second item with \emph{emphasis}
\end{itemize}

\begin{tikzpicture}
  \draw (0,0) -- (1,1);
\end{tikzpicture}
```

Bloc genere (`bck_01_introduction.py`) :
```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """Introduction — converted from LaTeX (autonomous mode)."""
    heading = s.project.titles.section_title + s.center_txt
    content = s.large
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    st_write(bs.heading, "Introduction", tag=t.div, toc_lvl="1")
    st_space("v", 1)

    # Paragraph with inline formatting
    st_write(bs.content, "This is ", (s.bold, "bold"), " statement with math:")
    stx.st_latex(r"E=mc^2")
    st_space("v", 1)

    # List
    with st_list(list_type=lt.unordered, li_style=bs.content) as l:
        with l.item():
            st_write("First item")
        with l.item():
            st_write("Second item with ", (s.italic, "emphasis"))
    st_space("v", 1)

    # TikZ diagram (extracted from LaTeX source)
    stx.st_tikz(r"""
\begin{tikzpicture}
  \draw (0,0) -- (1,1);
\end{tikzpicture}
    """.strip())
```

### 7.5 Regles de fallback vers st_latex_doc()

Le generateur autonome bascule vers `st_latex_doc()` quand :

| Condition | Raison |
|-----------|--------|
| Noeud `RAW_LATEX` | Commande non reconnue |
| Paragraphe avec > 3 formules math inline | Lisibilite |
| Environnement `align`, `gather`, `multline` | Multi-ligne math complexe |
| Tableau complexe (multirow, multicolumn) | st_grid ne gere pas les fusions |
| Nested lists > 2 niveaux | st_list ne gere pas l'imbrication profonde |
| Theoremes avec numerotation croisee | Pas d'equivalent natif |

---

## 8. Conversion Beamer specifique

### 8.1 Mapping Beamer -> StreamTeX

Beamer a des concepts qui se mappent naturellement sur StreamTeX :

| Concept Beamer | Concept StreamTeX |
|----------------|-------------------|
| `\begin{frame}` | Un bloc (`bck_XX_title.py`) |
| `\frametitle{Title}` | `st_write(bs.heading, "Title", toc_lvl="1")` |
| `\framesubtitle{Sub}` | `st_write(bs.sub, "Sub")` |
| `\pause` | Ignore (pas d'equivalent interactif) |
| `\begin{columns}` | `st_grid(cols=N)` |
| `\begin{column}{0.5\textwidth}` | `with g.cell():` |
| `\begin{block}{Title}` | `with st_block(bs.info_box):` + titre |
| `\begin{alertblock}{Title}` | `with st_block(bs.alert_box):` + titre |
| `\begin{exampleblock}{Title}` | `with st_block(bs.example_box):` + titre |
| `\alert{text}` | `(s.text.colors.red + s.bold, "text")` |
| `\structure{text}` | `(s.project.colors.primary, "text")` |
| Theme Beamer | `custom/styles.py` avec couleurs du theme |
| `\tableofcontents` | TOCConfig dans book.py |

### 8.2 Mode minimal Beamer

```python
# Chaque frame -> un bloc avec st_latex_doc()
_FRAME_CONTENT = r"""
\frametitle{My Frame Title}
Content of the frame with \textbf{bold} and $math$.
\begin{itemize}
  \item Point 1
  \item Point 2
\end{itemize}
"""

def build():
    st_write(bs.heading, "My Frame Title", tag=t.div, toc_lvl="1")
    st_space("v", 1)
    stx.st_latex_doc(_FRAME_CONTENT, height=400)
```

### 8.3 Mode autonome Beamer

```python
def build():
    st_write(bs.heading, "My Frame Title", tag=t.div, toc_lvl="1")
    st_space("v", 1)

    st_write(bs.content, "Content of the frame with ", (s.bold, "bold"), " and math:")
    stx.st_latex(r"math")
    st_space("v", 1)

    with st_list(list_type=lt.unordered, li_style=bs.content) as l:
        with l.item():
            st_write("Point 1")
        with l.item():
            st_write("Point 2")
```

### 8.4 Conversion des colonnes Beamer

```latex
\begin{columns}
  \begin{column}{0.5\textwidth}
    Left content
  \end{column}
  \begin{column}{0.5\textwidth}
    Right content
  \end{column}
\end{columns}
```

Mode autonome :
```python
with st_grid(
    cols=s.project.containers.responsive_2col,
    grid_style=s.project.containers.gap_24,
) as g:
    with g.cell():
        st_write(bs.content, "Left content")
    with g.cell():
        st_write(bs.content, "Right content")
```

### 8.5 Paginate mode pour Beamer

Les projets convertis depuis Beamer utilisent `paginate=True` par defaut (1 frame = 1 page StreamTeX) :

```python
# book.py genere pour Beamer
st_book(
    module_list,
    toc_config=toc,
    marker_config=MarkerConfig(auto_marker_on_toc=1),
    paginate=True,                           # Un frame par page
    banner=BannerConfig.full(),
)
```

Les projets convertis depuis LaTeX standard utilisent `paginate=False` (mode continu, scroll libre).

---

## 9. Gestion des fichiers et assets

### 9.1 Images

| Cas | Traitement |
|-----|-----------|
| `\includegraphics{img/photo.png}` | Copie dans `static/images/photo.png`, genere `st_image(uri="images/photo.png")` |
| `\includegraphics[width=0.8\textwidth]{img/photo.png}` | Idem + `width="80%"` |
| Chemin relatif au .tex | Resolu relativement au fichier source |
| Image non trouvee | Warning + commentaire `# TODO: image not found: path` |

### 9.2 Bibliographie

| Cas | Traitement |
|-----|-----------|
| `\bibliography{refs}` | Copie `refs.bib` dans le projet, ajoute `bib_sources=["refs.bib"]` dans `book.py` |
| `\cite{key}` | Mode autonome : `stx.st_cite("key")` / Mode minimal : reste dans `st_latex_doc()` |
| Pas de .bib trouve | Warning |

### 9.3 Fichiers TikZ externes

| Cas | Traitement |
|-----|-----------|
| `\input{diagrams/network.tex}` contenant TikZ | Copie dans `static/diagrams/`, genere `st_tikz(file="diagrams/network.tex")` |
| `\input{chapter2.tex}` (sous-fichier standard) | Inline le contenu avant le parsing |

### 9.4 Arborescence du projet genere

```
output_project/
  book.py                       # st_book() avec tous les blocs
  setup.py                      # sys.path setup
  blocks/
    __init__.py                 # ProjectBlockRegistry
    helpers.py                  # BlockHelperConfig (si mode autonome)
    bck_01_introduction.py      # 1 bloc par section (ou frame)
    bck_02_methodology.py
    bck_03_results.py
    ...
  custom/
    styles.py                   # Styles projet (generes a partir du theme Beamer si applicable)
    themes.py                   # Theme dark (template par defaut)
  static/
    images/                     # Images copiees depuis le projet LaTeX
    diagrams/                   # Fichiers TikZ externes
  .streamlit/
    config.toml                 # enableStaticServing = true
```

---

## 10. CLI et integration

### 10.1 Interface en ligne de commande

```bash
# Conversion standard (mode minimal, auto-detect article/beamer)
uv run python -m streamtex.converter input.tex --output ./my_project/

# Mode minimal explicite
uv run python -m streamtex.converter input.tex --mode minimal --output ./my_project/

# Mode autonome
uv run python -m streamtex.converter input.tex --mode autonomous --output ./my_project/

# Beamer avec pagination
uv run python -m streamtex.converter presentation.tex --output ./my_presentation/

# Options
uv run python -m streamtex.converter input.tex \
    --mode autonomous \
    --output ./my_project/ \
    --encoding utf-8 \
    --title "My Course" \
    --page-width 90 \
    --paginate              # Force paginated mode
    --no-paginate           # Force continuous mode
```

### 10.2 API Python

```python
from streamtex.converter import convert_project, ConversionConfig

config = ConversionConfig(
    source="input.tex",
    output_dir="./my_project/",
    mode="minimal",          # ou "autonomous"
    encoding="utf-8",
    title="My Course",       # Override le titre LaTeX
    paginate=None,           # None = auto (True pour Beamer, False sinon)
    page_width=90,
)

result = convert_project(config)
print(f"Generated {result.block_count} blocks")
print(f"Warnings: {result.warnings}")
```

### 10.3 Resultat de conversion

```python
@dataclass
class ConversionResult:
    """Result of a LaTeX to StreamTeX conversion."""
    output_dir: str                     # Chemin du projet genere
    block_count: int                    # Nombre de blocs generes
    blocks: list[str]                   # Noms des fichiers bloc
    mode: str                           # "minimal" ou "autonomous"
    documentclass: str                  # "article", "beamer", etc.
    warnings: list[str]                 # Avertissements (images manquantes, etc.)
    unsupported_commands: list[str]     # Commandes LaTeX non converties
    fallback_count: int                 # Nombre de fallback vers st_latex_doc() (mode autonome)
```

### 10.4 Integration slash commands

Ajouter deux slash commands dans `.claude/commands/migration/` :

| Commande | Fichier | Role |
|----------|---------|------|
| `/migration:latex-convert` | `latex-convert.md` | Conversion d'un fichier LaTeX vers StreamTeX |
| `/migration:beamer-convert` | `beamer-convert.md` | Conversion d'une presentation Beamer vers StreamTeX |

---

## 11. Fichiers a creer/modifier

### Fichiers nouveaux

| Fichier | Lignes estimees | Role |
|---------|-----------------|------|
| `streamtex/converter/__init__.py` | ~30 | API publique : `convert_project()`, `ConversionConfig`, `ConversionResult` |
| `streamtex/converter/_model.py` | ~100 | `NodeType`, `LatexNode`, `LatexDocument` |
| `streamtex/converter/_pandoc_walker.py` | ~250 | Walker Pandoc JSON AST -> arbre `LatexNode` (parseur principal) |
| `streamtex/converter/_regex_parser.py` | ~300 | Parseur regex fallback (si pandoc absent) |
| `streamtex/converter/_tikz_extractor.py` | ~40 | Pre-extraction TikZ avant parsing pandoc |
| `streamtex/converter/_generator_minimal.py` | ~200 | Generateur mode minimal -> blocs Python |
| `streamtex/converter/_generator_autonomous.py` | ~350 | Generateur mode autonome -> blocs Python |
| `streamtex/converter/_beamer.py` | ~150 | Logique specifique Beamer (frames, columns, blocks) |
| `streamtex/converter/_project_scaffold.py` | ~120 | Generation book.py, setup.py, custom/, blocks/__init__.py |
| `streamtex/converter/_style_mapper.py` | ~80 | Mapping Pandoc AST / LaTeX -> styles StreamTeX |
| `streamtex/converter/_asset_manager.py` | ~100 | Copie images, .bib, resolution chemins |
| `streamtex/converter/__main__.py` | ~60 | CLI argparse |
| `streamtex/converter/templates/block.py.j2` | ~40 | Template Jinja2 pour un bloc |
| `streamtex/converter/templates/book.py.j2` | ~50 | Template Jinja2 pour book.py |
| `streamtex/converter/templates/styles.py.j2` | ~60 | Template Jinja2 pour styles.py |
| `streamtex/converter/templates/setup.py.j2` | ~10 | Template pour setup.py |
| `streamtex/converter/templates/blocks_init.py.j2` | ~15 | Template pour blocks/__init__.py |
| `tests/test_converter_pandoc_walker.py` | ~150 | Tests walker Pandoc JSON AST |
| `tests/test_converter_regex_parser.py` | ~150 | Tests parseur regex fallback |
| `tests/test_converter_minimal.py` | ~150 | Tests generateur minimal |
| `tests/test_converter_autonomous.py` | ~200 | Tests generateur autonome |
| `tests/test_converter_beamer.py` | ~150 | Tests specifiques Beamer |
| `tests/test_converter_scaffold.py` | ~100 | Tests generation projet |
| `tests/test_converter_integration.py` | ~100 | Tests end-to-end (fichier .tex -> projet complet) |
| `.claude/commands/migration/latex-convert.md` | ~20 | Slash command |
| `.claude/commands/migration/beamer-convert.md` | ~20 | Slash command |

### Fichiers modifies

| Fichier | Modification |
|---------|-------------|
| `streamtex/__init__.py` | Ajouter import : `from .converter import convert_project, ConversionConfig, ConversionResult` |
| `CLAUDE.md` | Ajouter section converter dans Key Components + workflow |
| `documentation/streamtex_cheatsheet_en.md` | Ajouter section "LaTeX/Beamer Conversion" |
| `pyproject.toml` | Ajouter dependances optionnelles `pypandoc`, `pypandoc_binary`, `jinja2` (groupe `converter`) |

### Total estime

- **~2 500 lignes de code** (converter + templates)
- **~900 lignes de tests**
- **24 fichiers nouveaux** + **4 fichiers modifies**

---

## 12. Plan d'implementation

### Phase 1 : Fondation (3-4 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 1.1 | Modele de donnees (`_model.py`) | `_model.py`, `tests/test_converter_pandoc_walker.py` (partie model) |
| 1.2 | Walker Pandoc (`_pandoc_walker.py`) | `_pandoc_walker.py`, `tests/test_converter_pandoc_walker.py` |
| 1.3 | Parseur regex fallback (`_regex_parser.py`) | `_regex_parser.py`, `tests/test_converter_regex_parser.py` |
| 1.4 | Scaffold projet (`_project_scaffold.py`) + templates | `_project_scaffold.py`, `templates/*.j2`, `tests/test_converter_scaffold.py` |
| 1.5 | Generateur minimal (`_generator_minimal.py`) | `_generator_minimal.py`, `tests/test_converter_minimal.py` |
| 1.6 | CLI basique (`__main__.py`, `__init__.py`) | `__main__.py`, `__init__.py` |

**Livrable** : Conversion d'un article LaTeX simple en mode minimal -> projet StreamTeX fonctionnel.

### Phase 2 : Mode autonome (3-4 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 2.1 | Style mapper (`_style_mapper.py`) | `_style_mapper.py` |
| 2.2 | Generateur autonome — texte, listes, sections | `_generator_autonomous.py`, `tests/test_converter_autonomous.py` |
| 2.3 | Generateur autonome — images, code, tableaux | Extension `_generator_autonomous.py` |
| 2.4 | Asset manager (`_asset_manager.py`) | `_asset_manager.py` |

**Livrable** : Conversion d'un article LaTeX complexe en mode autonome -> projet StreamTeX natif.

### Phase 3 : Beamer (2-3 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 3.1 | Logique Beamer (`_beamer.py`) — frames, columns | `_beamer.py`, `tests/test_converter_beamer.py` |
| 3.2 | Integration Beamer dans les deux generateurs | Extension generateurs |
| 3.3 | Styles Beamer -> styles StreamTeX | Extension `_style_mapper.py` |

**Livrable** : Conversion d'une presentation Beamer -> projet StreamTeX pagine.

### Phase 4 : Polish (1-2 jours)

| Sprint | Tache | Fichiers |
|--------|-------|----------|
| 4.1 | Tests d'integration end-to-end | `tests/test_converter_integration.py` |
| 4.2 | TikZ extractor integration | `_tikz_extractor.py` |
| 4.3 | Documentation (cheatsheet, CLAUDE.md) | Fichiers modifies |
| 4.4 | Slash commands | `.claude/commands/migration/` |

**Livrable** : Outil complet, documente, teste.

**Total estime : 9-13 jours**

---

## 13. Tests

### 13.1 Strategie

```
Tests unitaires (automatises, pytest)
  +- test_converter_pandoc_walker.py  -> Parsing Pandoc AST -> LatexNode tree
  +- test_converter_regex_parser.py   -> Parsing regex fallback
  +- test_converter_minimal.py        -> Generation mode minimal
  +- test_converter_autonomous.py     -> Generation mode autonome
  +- test_converter_beamer.py         -> Parsing et generation Beamer
  +- test_converter_scaffold.py       -> Generation arborescence projet
  +- test_converter_integration.py    -> End-to-end (.tex -> projet fonctionnel)

Fichiers de test LaTeX (fixtures)
  +- tests/fixtures/simple_article.tex
  +- tests/fixtures/complex_article.tex
  +- tests/fixtures/beamer_presentation.tex
  +- tests/fixtures/article_with_tikz.tex
  +- tests/fixtures/article_with_bib.tex
```

### 13.2 Tests du parseur Pandoc (~30 tests)

| Classe | Tests |
|--------|-------|
| `TestParseDocument` | documentclass detection, package extraction, title/author |
| `TestParseSections` | section, subsection, subsubsection, chapter |
| `TestParseText` | textbf, textit, emph, texttt, underline |
| `TestParseMath` | inline $, display $$, equation env, align env |
| `TestParseLists` | itemize, enumerate, nested lists |
| `TestParseImages` | includegraphics with/without options |
| `TestParseTables` | tabular, hline, multicolumn |
| `TestParseCode` | lstlisting, verbatim |
| `TestParseLinks` | href, url |
| `TestParseBeamer` | frame, frametitle, columns, blocks |
| `TestParseUnknown` | Unknown commands -> RAW_LATEX |

### 13.3 Tests du parseur regex (~15 tests)

| Classe | Tests |
|--------|-------|
| `TestRegexSections` | section, subsection detection |
| `TestRegexText` | textbf, textit, emph basic formatting |
| `TestRegexMath` | inline $, display $$ |
| `TestRegexLists` | itemize, enumerate |
| `TestRegexFallback` | Unknown commands -> RAW_LATEX + warning |

### 13.4 Tests des generateurs (~25 tests chacun)

| Classe | Tests |
|--------|-------|
| `TestMinimalSegmentation` | 1 section = 1 bloc, no section = 1 bloc |
| `TestMinimalTikzExtraction` | TikZ extrait en st_tikz() |
| `TestMinimalHeightEstimation` | Estimation hauteur iframe |
| `TestMinimalCodeGeneration` | Python syntaxiquement valide (ast.parse) |
| `TestAutonomousTextConversion` | Paragraphes -> st_write() |
| `TestAutonomousInlineStyles` | Bold/italic -> tuples inline |
| `TestAutonomousMathConversion` | Math -> st_latex() |
| `TestAutonomousListConversion` | itemize/enumerate -> st_list() |
| `TestAutonomousImageConversion` | includegraphics -> st_image() |
| `TestAutonomousTableConversion` | tabular -> st_grid() |
| `TestAutonomousFallback` | Elements complexes -> st_latex_doc() |

### 13.5 Tests d'integration (~10 tests)

| Test | Verification |
|------|-------------|
| `test_simple_article_minimal` | Article simple -> projet fonctionnel (ast.parse ok, fichiers presents) |
| `test_simple_article_autonomous` | Idem mode autonome |
| `test_beamer_minimal` | Beamer -> projet pagine |
| `test_beamer_autonomous` | Beamer -> projet pagine natif |
| `test_article_with_tikz` | TikZ extraits correctement dans les deux modes |
| `test_article_with_images` | Images copiees dans static/ |
| `test_article_with_bib` | .bib copie, bib_sources dans book.py |
| `test_warnings_generated` | Commandes non supportees -> warnings |
| `test_output_ruff_clean` | Code genere passe ruff check |
| `test_book_py_importable` | book.py genere est importable (ast.parse) |

### 13.6 Commandes

```bash
# Tests unitaires
uv run pytest tests/test_converter_pandoc_walker.py -v
uv run pytest tests/test_converter_regex_parser.py -v
uv run pytest tests/test_converter_minimal.py -v
uv run pytest tests/test_converter_autonomous.py -v
uv run pytest tests/test_converter_beamer.py -v
uv run pytest tests/test_converter_scaffold.py -v
uv run pytest tests/test_converter_integration.py -v

# Suite complete
uv run pytest tests/ -v

# Lint du code genere
uv run ruff check streamtex/converter/
```

---

## 14. Risques et mitigations

### R1 : Pandoc non installe

**Description** : L'utilisateur n'a pas pandoc installe. Le fallback regex offre une couverture reduite (~60-70%).

**Mitigation** :
- `pypandoc_binary` installe pandoc automatiquement via PyPI
- Warning clair avec instructions d'installation
- Le mode minimal fonctionne correctement meme avec le fallback regex

### R2 : Qualite visuelle du mode autonome

**Description** : La conversion automatique perd les nuances typographiques de LaTeX. Le resultat StreamTeX natif sera visuellement different du PDF LaTeX.

**Mitigation** :
- Le mode minimal est recommande pour les cas ou la fidelite est critique
- Le mode autonome est explicitement presente comme une base de depart, pas un resultat final
- Les `# TODO:` dans le code genere guident la revision manuelle

### R3 : Estimation de hauteur des iframes incorrecte

**Description** : L'heuristique `lines * 20px` pour le mode minimal peut donner des hauteurs inappropriees.

**Mitigation** :
- L'utilisateur peut ajuster les `height=N` dans les blocs generes
- Possibilite d'ajouter un mode `height="auto"` dans le futur

### R4 : Dependance Jinja2 pour les templates

**Description** : Jinja2 n'est pas une dependance actuelle de StreamTeX.

**Mitigation** :
- Ajoutee comme dependance **optionnelle** (`[converter]` group)
- Alternative : templates string Python simples si Jinja2 est juge trop lourd

### R5 : Conflits de nommage des blocs

**Description** : Les titres de section LaTeX peuvent contenir des caracteres speciaux ou etre tres longs.

**Mitigation** :
- Slugification des titres : `\section{L'introduction a la theorie}` -> `bck_01_lintroduction_a_la_theorie.py`
- Troncature a 50 caracteres max
- Fallback numerique si le slug est vide : `bck_01_section.py`

### R6 : Encodage des fichiers LaTeX

**Description** : Les fichiers LaTeX peuvent utiliser des encodages varies (UTF-8, Latin-1, ASCII).

**Mitigation** :
- Option `--encoding` dans la CLI (defaut UTF-8)
- Detection automatique via `chardet` en fallback (dependance optionnelle)

---

## 15. Limitations connues

| ID | Limitation | Contournement |
|----|-----------|---------------|
| L1 | **Macros custom** (`\newcommand`, `\def`) : non expansees | Pre-traitement manuel ou mode minimal |
| L2 | **Packages non standard** (minted, tcolorbox, pgfplots) : non supportes | Mode minimal -> `st_latex_doc()` (si LaTeX.js supporte) |
| L3 | **Images dans `st_latex_doc()`** : LaTeX.js ne rend pas `\includegraphics` | Le convertisseur extrait les images et les rend via `st_image()` |
| L4 | **Cross-references** (`\ref`, `\label`) : ne fonctionnent pas inter-blocs en mode minimal | Mode autonome -> liens internes StreamTeX |
| L5 | **Bibliographie conditionnelle** : si le `.bib` n'est pas fourni, `\cite` non resolu | Warning + `\cite` conserve comme `[key]` |
| L6 | **Overlays Beamer** (`\pause`, `\only<>`, `\onslide<>`) : pas d'equivalent | Contenu rendu statiquement + commentaire `# TODO` |

---

## 16. Criteres de validation

### Criteres fonctionnels (MUST)

- [ ] Conversion d'un article LaTeX simple (3 sections, texte, listes) -> projet fonctionnel en mode minimal
- [ ] Conversion d'un article LaTeX simple -> projet fonctionnel en mode autonome
- [ ] Conversion d'une presentation Beamer (5 frames) -> projet pagine en mode minimal
- [ ] Conversion d'une presentation Beamer -> projet pagine en mode autonome
- [ ] Extraction TikZ -> `st_tikz()` dans les deux modes
- [ ] Extraction math -> `st_latex()` (mode autonome) ou reste dans `st_latex_doc()` (mode minimal)
- [ ] Copie des images dans `static/images/`
- [ ] Copie du .bib et configuration `bib_sources` dans `book.py`
- [ ] Code Python genere syntaxiquement valide (`ast.parse()` ok)
- [ ] Code Python genere passe `ruff check`
- [ ] CLI fonctionnelle : `uv run python -m streamtex.converter input.tex --output dir/`
- [ ] Rapport de conversion avec warnings et elements non convertis
- [ ] Fallback regex fonctionne si pandoc n'est pas installe

### Criteres de qualite (SHOULD)

- [ ] Les blocs generes suivent les coding standards (BlockStyles class, build() function)
- [ ] Les styles generes sont coherents avec le systeme de styles StreamTeX
- [ ] Les noms de blocs sont lisibles (`bck_01_introduction.py`, pas `bck_01_lintroduction_la_thorie.py`)
- [ ] Les `# TODO:` dans le code guident la revision manuelle
- [ ] La TOC genere est correcte (niveaux de section preserves)
- [ ] Le mode pagine est automatique pour Beamer, continu pour articles

### Criteres de test (MUST)

- [ ] > 100 tests unitaires passent
- [ ] Tests d'integration end-to-end passent
- [ ] Suite complete StreamTeX (892+ tests existants) ne regresse pas
- [ ] `uv run ruff check streamtex/converter/` sans erreur
