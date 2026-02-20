# Proposition : Systeme de references bibliographiques pour StreamTeX

**Date** : 2026-02-20
**Statut** : Proposition (non implemente)
**Priorite** : Moyenne-Haute
**Modules cibles** : `streamtex/bib.py` (nouveau), `streamtex/bib_preview.py` (nouveau)

---

## 1. Contexte et motivation

StreamTeX est utilise dans des contextes pedagogiques et academiques. Les presentations,
cours et documents doivent frequemment citer des references bibliographiques.

Actuellement, les citations sont gerees manuellement dans les blocs via `st_write()` :

```python
st_write(s.medium,
    "Selon ",
    (s.italic, "Vaswani et al. (2017)"),
    ", les transformers ont revolutionne le NLP."
)
```

Ce pattern pose plusieurs problemes :
- **Aucune centralisation** : les references sont eparpillees dans les blocs
- **Pas de formatage standard** : chaque auteur ecrit les citations differemment
- **Pas de bibliographie finale** : pas de liste automatique en fin de document
- **Pas de hover preview** : pas d'apercu au survol comme pour les liens
- **Pas d'export** : pas de generation BibTeX ou bibliographie formatee

### Objectif

Un systeme de references bibliographiques integre a StreamTeX qui :
1. Centralise les references dans un fichier standard (BibTeX, JSON)
2. Permet les citations inline dans les blocs via `st_cite()`
3. Affiche un hover preview au survol de chaque citation
4. Genere automatiquement la bibliographie finale dans plusieurs formats (APA, MLA, IEEE)
5. S'integre au pipeline d'export HTML

### Philosophie StreamTeX respectee

| Principe | Application |
|----------|-------------|
| Zero HTML brut | `st_cite("key")` au lieu de `<sup>[1]</sup>` |
| `stx.*` pour le contenu | `st_cite()`, `st_bibliography()` |
| DI pattern | `BibConfig` injectable, `set_bib_config()` |
| Registre singleton | `BibRegistry` (comme `TOCRegistry`) |
| Dual rendering | Export HTML avec bibliographie complete |
| Hover preview | Extension du pattern `link_preview.py` |
| Style composition | Styles configurables via `Style` objects |

---

## 2. Architecture proposee

### 2.1. Vue d'ensemble des modules

```
streamtex/
  bib.py              ← NOUVEAU : registre, parsing, formatage, st_cite(), st_bibliography()
  bib_preview.py      ← NOUVEAU : scaffold JS/CSS hover card pour citations
  __init__.py          ← ajouter exports bib
```

### 2.2. Modele de donnees

```python
# streamtex/bib.py

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BibFormat(Enum):
    """Supported bibliography output formats."""
    APA = "apa"           # American Psychological Association (7th ed.)
    MLA = "mla"           # Modern Language Association (9th ed.)
    IEEE = "ieee"         # Institute of Electrical and Electronics Engineers
    CHICAGO = "chicago"   # Chicago Manual of Style (author-date)
    HARVARD = "harvard"   # Harvard referencing


class CitationStyle(Enum):
    """How inline citations are displayed."""
    AUTHOR_YEAR = "author_year"   # (Vaswani et al., 2017)
    NUMERIC = "numeric"           # [1]
    SUPERSCRIPT = "superscript"   # ^1


class EntryType(Enum):
    """BibTeX-compatible entry types."""
    ARTICLE = "article"
    BOOK = "book"
    INPROCEEDINGS = "inproceedings"
    CONFERENCE = "conference"
    INCOLLECTION = "incollection"
    PHDTHESIS = "phdthesis"
    MASTERSTHESIS = "mastersthesis"
    TECHREPORT = "techreport"
    MISC = "misc"
    ONLINE = "online"
    UNPUBLISHED = "unpublished"


@dataclass
class BibEntry:
    """A single bibliographic reference.

    Attributes:
        key: Unique identifier (e.g. "vaswani2017attention")
        entry_type: Type of publication (article, book, etc.)
        title: Publication title
        authors: List of author names in "Lastname, Firstname" format
        year: Publication year
        journal: Journal/conference name (for articles/inproceedings)
        volume: Volume number
        number: Issue number
        pages: Page range (e.g. "1-15")
        publisher: Publisher name (for books)
        booktitle: Conference/book title (for inproceedings/incollection)
        doi: Digital Object Identifier
        url: Direct URL to the publication
        abstract: Abstract text (used in hover preview)
        note: Additional notes
        extra: Any extra BibTeX fields not covered above
    """
    key: str
    entry_type: str = "misc"
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    volume: str = ""
    number: str = ""
    pages: str = ""
    publisher: str = ""
    booktitle: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    note: str = ""
    extra: Dict[str, str] = field(default_factory=dict)

    @property
    def first_author_last(self) -> str:
        """Extract the last name of the first author."""
        if not self.authors:
            return "Unknown"
        first = self.authors[0]
        if "," in first:
            return first.split(",")[0].strip()
        parts = first.strip().split()
        return parts[-1] if parts else "Unknown"

    @property
    def authors_short(self) -> str:
        """Short author string: 'Vaswani et al.' or 'Vaswani & Shazeer'."""
        if not self.authors:
            return "Unknown"
        if len(self.authors) == 1:
            return self.first_author_last
        if len(self.authors) == 2:
            a1 = self.authors[0].split(",")[0].strip() if "," in self.authors[0] else self.authors[0].split()[-1]
            a2 = self.authors[1].split(",")[0].strip() if "," in self.authors[1] else self.authors[1].split()[-1]
            return f"{a1} & {a2}"
        return f"{self.first_author_last} et al."
```

### 2.3. Configuration (DI pattern)

```python
@dataclass
class BibConfig:
    """Configuration for the bibliography system.

    Follows the DI pattern established by BlockHelperConfig and ExportConfig.

    Attributes:
        format: Output format for st_bibliography() (APA, MLA, IEEE, etc.)
        citation_style: Inline citation display style (author_year, numeric, superscript)
        hover_enabled: Show hover preview on citations
        hover_show_abstract: Include abstract in hover card (can be long)
        sort_by: How to sort the bibliography ("author", "year", "key", "citation_order")
        locale: Language for "et al.", "and", "Retrieved from", etc.
    """
    format: BibFormat = BibFormat.APA
    citation_style: CitationStyle = CitationStyle.AUTHOR_YEAR
    hover_enabled: bool = True
    hover_show_abstract: bool = False
    sort_by: str = "author"  # "author", "year", "key", "citation_order"
    locale: str = "en"       # "en", "fr"


# Global singleton
_bib_config: BibConfig = BibConfig()


def set_bib_config(config: BibConfig) -> None:
    """Set global bibliography configuration. Call once at project startup."""
    global _bib_config
    _bib_config = config


def get_bib_config() -> BibConfig:
    """Get current bibliography configuration."""
    return _bib_config
```

### 2.4. Registre de references (pattern TOCRegistry)

```python
class BibRegistry:
    """Singleton registry for bibliographic references.

    Same pattern as TOCRegistry: one global instance, reset per book render.
    Stores all loaded entries + tracks which ones are actually cited.
    """

    def __init__(self):
        self._entries: Dict[str, BibEntry] = {}
        self._cited: List[str] = []  # Ordered list of cited keys (first citation order)
        self._citation_counter: int = 0

    def register(self, entry: BibEntry) -> None:
        """Register a BibEntry. Overwrites if key already exists."""
        self._entries[entry.key] = entry

    def register_many(self, entries: List[BibEntry]) -> None:
        """Register multiple entries at once."""
        for entry in entries:
            self.register(entry)

    def get(self, key: str) -> Optional[BibEntry]:
        """Get a BibEntry by key. Returns None if not found."""
        return self._entries.get(key)

    def cite(self, key: str) -> int:
        """Mark a key as cited and return its citation number (1-based).

        First citation of a key gets the next number. Subsequent citations
        return the same number.
        """
        if key not in self._entries:
            logger.warning(f"BibRegistry: citation key '{key}' not found in registry")
            return 0

        if key not in self._cited:
            self._cited.append(key)
            self._citation_counter += 1

        return self._cited.index(key) + 1

    def get_cited_entries(self) -> List[BibEntry]:
        """Return only the entries that were actually cited, in citation order."""
        return [self._entries[k] for k in self._cited if k in self._entries]

    def get_all_entries(self) -> List[BibEntry]:
        """Return all registered entries."""
        return [*self._entries.values()]

    def list_keys(self) -> List[str]:
        """Return all registered keys."""
        return sorted(self._entries.keys())

    def reset(self) -> None:
        """Reset the registry. Called at the start of each st_book() render."""
        self._entries.clear()
        self._cited.clear()
        self._citation_counter = 0

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        return key in self._entries


# Global singleton
_bib_registry = BibRegistry()


def reset_bib_registry() -> None:
    """Reset the global bibliography registry."""
    _bib_registry.reset()


def get_bib_registry() -> BibRegistry:
    """Get the global bibliography registry."""
    return _bib_registry
```

---

## 3. Chargement des references

### 3.1. Depuis un fichier BibTeX

```python
def load_bibtex(path: str) -> List[BibEntry]:
    """Parse a BibTeX file and return a list of BibEntry objects.

    Uses a lightweight built-in parser (no external dependency).
    Handles standard BibTeX fields. Non-standard fields go into entry.extra.

    Args:
        path: Path to the .bib file

    Returns:
        List of BibEntry objects

    Raises:
        FileNotFoundError: If file doesn't exist
        BibParseError: If BibTeX syntax is invalid

    Example:
        from streamtex import load_bibtex, get_bib_registry

        entries = load_bibtex("static/references.bib")
        get_bib_registry().register_many(entries)
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return _parse_bibtex(content)


class BibParseError(Exception):
    """Raised when BibTeX parsing fails."""
    pass


def _parse_bibtex(content: str) -> List[BibEntry]:
    """Lightweight BibTeX parser.

    Handles the most common BibTeX patterns:
    - @type{key, field = {value}, field = "value", field = number}
    - Concatenated strings (field = {Part 1} # {Part 2})
    - Standard and non-standard fields
    - Comments and @string definitions (ignored)

    Does NOT handle:
    - Cross-references (@crossref)
    - @preamble
    - Complex macro substitutions

    For advanced needs, users can install pybtex and use load_bibtex_pybtex().
    """
    import re

    entries = []
    # Match @type{key, ... }
    # Use a state machine for brace counting to handle nested braces
    pattern = re.compile(r'@(\w+)\s*\{', re.IGNORECASE)

    pos = 0
    while pos < len(content):
        match = pattern.search(content, pos)
        if not match:
            break

        entry_type = match.group(1).lower()
        brace_start = match.end() - 1

        # Skip @comment, @string, @preamble
        if entry_type in ("comment", "string", "preamble"):
            # Find matching closing brace
            pos = _find_matching_brace(content, brace_start)
            continue

        # Find the matching closing brace
        end = _find_matching_brace(content, brace_start)
        if end < 0:
            raise BibParseError(f"Unmatched brace at position {brace_start}")

        body = content[brace_start + 1:end]

        # Extract key (everything before first comma)
        comma_pos = body.find(",")
        if comma_pos < 0:
            pos = end + 1
            continue

        key = body[:comma_pos].strip()
        fields_str = body[comma_pos + 1:]

        # Parse fields
        fields = _parse_bibtex_fields(fields_str)

        # Build BibEntry
        known_fields = {
            "title", "author", "year", "journal", "volume", "number",
            "pages", "publisher", "booktitle", "doi", "url", "abstract", "note"
        }

        authors = []
        if "author" in fields:
            # Split on " and " (BibTeX convention)
            authors = [a.strip() for a in fields["author"].split(" and ")]

        entry = BibEntry(
            key=key,
            entry_type=entry_type,
            title=fields.get("title", ""),
            authors=authors,
            year=fields.get("year", ""),
            journal=fields.get("journal", ""),
            volume=fields.get("volume", ""),
            number=fields.get("number", ""),
            pages=fields.get("pages", ""),
            publisher=fields.get("publisher", ""),
            booktitle=fields.get("booktitle", ""),
            doi=fields.get("doi", ""),
            url=fields.get("url", ""),
            abstract=fields.get("abstract", ""),
            note=fields.get("note", ""),
            extra={k: v for k, v in fields.items() if k not in known_fields},
        )
        entries.append(entry)
        pos = end + 1

    return entries


def _find_matching_brace(content: str, start: int) -> int:
    """Find the position of the matching closing brace."""
    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(content)):
        ch = content[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"' and not in_string:
            in_string = True
            continue
        if ch == '"' and in_string:
            in_string = False
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i

    return -1


def _parse_bibtex_fields(fields_str: str) -> Dict[str, str]:
    """Parse the field=value pairs from a BibTeX entry body."""
    import re

    fields = {}
    # Match: field_name = {value} or field_name = "value" or field_name = number
    pattern = re.compile(
        r'(\w+)\s*=\s*(?:'
        r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'  # {value with {nested} braces}
        r'|"([^"]*)"'                           # "quoted value"
        r'|(\d+)'                                # bare number
        r')',
        re.DOTALL
    )

    for match in pattern.finditer(fields_str):
        name = match.group(1).lower()
        value = match.group(2) or match.group(3) or match.group(4) or ""
        # Clean up LaTeX artifacts
        value = value.replace("\n", " ").strip()
        value = re.sub(r'\s+', ' ', value)
        fields[name] = value

    return fields
```

### 3.2. Depuis un fichier JSON

```python
def load_bib_json(path: str) -> List[BibEntry]:
    """Load bibliography entries from a JSON file.

    Expected format:
    [
        {
            "key": "vaswani2017attention",
            "entry_type": "article",
            "title": "Attention Is All You Need",
            "authors": ["Vaswani, Ashish", "Shazeer, Noam", ...],
            "year": "2017",
            "journal": "NeurIPS",
            ...
        }
    ]

    Args:
        path: Path to the .json file

    Returns:
        List of BibEntry objects
    """
    import json

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array, got {type(data).__name__}")

    entries = []
    for item in data:
        if not isinstance(item, dict):
            continue
        key = item.get("key", "")
        if not key:
            logger.warning(f"Skipping bibliography entry without 'key': {item}")
            continue

        known = {
            "key", "entry_type", "title", "authors", "year", "journal",
            "volume", "number", "pages", "publisher", "booktitle",
            "doi", "url", "abstract", "note"
        }
        extra = {k: v for k, v in item.items() if k not in known}

        entries.append(BibEntry(
            key=key,
            entry_type=item.get("entry_type", "misc"),
            title=item.get("title", ""),
            authors=item.get("authors", []),
            year=str(item.get("year", "")),
            journal=item.get("journal", ""),
            volume=str(item.get("volume", "")),
            number=str(item.get("number", "")),
            pages=item.get("pages", ""),
            publisher=item.get("publisher", ""),
            booktitle=item.get("booktitle", ""),
            doi=item.get("doi", ""),
            url=item.get("url", ""),
            abstract=item.get("abstract", ""),
            note=item.get("note", ""),
            extra=extra,
        ))

    return entries
```

### 3.3. Chargement dans le registre (book.py)

```python
# Ajout dans streamtex/book.py — au debut de st_book()

def st_book(module_list, ..., bib_sources=None, bib_config=None, ...):
    """
    ...
    bib_sources: Optional list of paths to .bib or .json files.
                 Loaded once and registered in the global BibRegistry.
    bib_config: Optional BibConfig to set before rendering.
    """
    # Reset bibliography registry (like toc, marker)
    from .bib import reset_bib_registry, load_bibtex, load_bib_json, set_bib_config

    reset_bib_registry()

    if bib_config:
        set_bib_config(bib_config)

    if bib_sources:
        from .bib import get_bib_registry
        registry = get_bib_registry()
        for source_path in bib_sources:
            if source_path.endswith(".bib"):
                entries = load_bibtex(source_path)
            elif source_path.endswith(".json"):
                entries = load_bib_json(source_path)
            else:
                logger.warning(f"Unknown bibliography format: {source_path}")
                continue
            registry.register_many(entries)

    # ... reste de st_book() inchange ...
```

---

## 4. Citation inline : `st_cite()`

### 4.1. Fonction principale

```python
# streamtex/bib.py

from .export import _render, is_export_active, export_append
from .styles import Style, StxStyles


def st_cite(
    *keys: str,
    style: Optional[Style] = None,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Render one or more inline citations.

    Generates a clickable/hoverable citation marker that shows the reference
    details on hover (like link_preview but for bibliography).

    Args:
        *keys: One or more BibEntry keys to cite (e.g. "vaswani2017attention")
        style: Optional style override for the citation marker
        prefix: Text before the citation (e.g. "cf. ")
        suffix: Text after the citation (e.g. ", p. 42")

    Example:
        # Single citation
        st_cite("vaswani2017attention")
        # → (Vaswani et al., 2017)

        # Multiple citations
        st_cite("vaswani2017attention", "devlin2019bert")
        # → (Vaswani et al., 2017; Devlin et al., 2019)

        # With page number
        st_cite("vaswani2017attention", suffix=", p. 42")
        # → (Vaswani et al., 2017, p. 42)

    Returns:
        The formatted citation HTML string (also rendered via _render())
    """
    cfg = _bib_config
    registry = _bib_registry

    parts = []
    for key in keys:
        entry = registry.get(key)
        if entry is None:
            logger.warning(f"st_cite: key '{key}' not found in BibRegistry")
            parts.append(f"[{key}?]")
            continue

        num = registry.cite(key)  # Mark as cited, get number

        if cfg.citation_style == CitationStyle.AUTHOR_YEAR:
            label = f"{entry.authors_short}, {entry.year}"
        elif cfg.citation_style == CitationStyle.NUMERIC:
            label = str(num)
        elif cfg.citation_style == CitationStyle.SUPERSCRIPT:
            label = str(num)
        else:
            label = f"{entry.authors_short}, {entry.year}"

        parts.append((key, label, entry))

    # Format the combined citation
    if cfg.citation_style == CitationStyle.SUPERSCRIPT:
        sep = ","
        open_br, close_br = "<sup>", "</sup>"
    elif cfg.citation_style == CitationStyle.NUMERIC:
        sep = ", "
        open_br, close_br = "[", "]"
    else:  # AUTHOR_YEAR
        sep = "; "
        open_br, close_br = "(", ")"

    inner_parts = []
    for key, label, entry in parts:
        if isinstance(entry, BibEntry):
            # Hoverable span with data attributes for JS
            hover_attrs = ""
            if cfg.hover_enabled:
                hover_attrs = (
                    f' class="stx-cite"'
                    f' data-bib-key="{key}"'
                    f' data-bib-title="{_escape_attr(entry.title)}"'
                    f' data-bib-authors="{_escape_attr(", ".join(entry.authors))}"'
                    f' data-bib-year="{entry.year}"'
                    f' data-bib-journal="{_escape_attr(entry.journal or entry.booktitle)}"'
                    f' data-bib-doi="{entry.doi}"'
                    f' data-bib-abstract="{_escape_attr(entry.abstract[:200]) if cfg.hover_show_abstract and entry.abstract else ""}"'
                )
            inner_parts.append(f'<span{hover_attrs}>{label}</span>')
        else:
            inner_parts.append(label)  # Unknown key fallback

    citation_text = sep.join(inner_parts)
    full_text = f"{prefix}{open_br}{citation_text}{close_br}{suffix}"

    # Resolve style
    resolved_style = style or StxStyles.none
    html = f'<span style="{resolved_style}" class="stx-citation">{full_text}</span>'

    _render(html)
    return html


def _escape_attr(text: str) -> str:
    """Escape text for use in HTML data attributes."""
    return text.replace('"', '&quot;').replace("'", '&#39;').replace("<", '&lt;').replace(">", '&gt;')
```

### 4.2. Integration avec `st_write()` — mode tuple

Pour permettre les citations inline dans un flux de texte, ajouter un nouveau
type de tuple reconnu par `st_write()` :

```python
# Nouveau pattern dans write.py :
# st_write(s.medium, "Selon ", cite("vaswani2017"), ", les transformers...")

# Option 1 : Fonction cite() qui retourne un fragment HTML injectable
def cite(*keys: str, **kwargs) -> str:
    """Return citation HTML fragment for use in st_write tuples.

    Unlike st_cite() which renders immediately, cite() returns a string
    suitable for embedding in st_write():

        st_write(s.medium, "Selon ", cite("vaswani2017"), ", les transformers...")

    This is the RECOMMENDED way to mix citations with prose.
    """
    cfg = _bib_config
    registry = _bib_registry

    parts = []
    for key in keys:
        entry = registry.get(key)
        if entry is None:
            parts.append(f"[{key}?]")
            continue

        num = registry.cite(key)

        if cfg.citation_style == CitationStyle.AUTHOR_YEAR:
            label = f"{entry.authors_short}, {entry.year}"
        elif cfg.citation_style == CitationStyle.NUMERIC:
            label = str(num)
        elif cfg.citation_style == CitationStyle.SUPERSCRIPT:
            label = str(num)
        else:
            label = f"{entry.authors_short}, {entry.year}"

        hover_attrs = ""
        if cfg.hover_enabled:
            hover_attrs = (
                f' class="stx-cite"'
                f' data-bib-key="{key}"'
                f' data-bib-title="{_escape_attr(entry.title)}"'
                f' data-bib-authors="{_escape_attr(", ".join(entry.authors))}"'
                f' data-bib-year="{entry.year}"'
                f' data-bib-journal="{_escape_attr(entry.journal or entry.booktitle)}"'
                f' data-bib-doi="{entry.doi}"'
            )
        parts.append(f'<span{hover_attrs}>{label}</span>')

    if cfg.citation_style == CitationStyle.SUPERSCRIPT:
        return "<sup>" + ",".join(parts) + "</sup>"
    elif cfg.citation_style == CitationStyle.NUMERIC:
        return "[" + ", ".join(parts) + "]"
    else:
        return "(" + "; ".join(parts) + ")"
```

**Utilisation dans un bloc :**

```python
from streamtex.bib import cite

def build():
    st_write(s.medium,
        "Selon ",
        cite("vaswani2017"),
        ", les transformers ont revolutionne le NLP. "
        "Cette architecture a ete etendue par ",
        cite("devlin2019", "brown2020"),
        " pour le pre-entrainement a grande echelle."
    )
```

---

## 5. Hover preview pour les citations

### 5.1. Nouveau module : `streamtex/bib_preview.py`

Ce module etend le pattern de `link_preview.py` avec un hover card specifique aux
references bibliographiques.

```python
# streamtex/bib_preview.py

import textwrap
import streamlit as st


def inject_bib_preview_scaffold():
    """Inject the bibliography hover card and JS event listeners.

    Same pattern as inject_link_preview_scaffold() but for citations.
    Targets elements with class='stx-cite' and reads data-bib-* attributes.
    """

    css = """
    <style>
        #stx-bib-card {
            position: fixed;
            z-index: 999998;
            display: none;
            width: 380px;
            max-width: 90vw;
            background: #1a1a2e;
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            font-family: 'Georgia', 'Times New Roman', serif;
            padding: 16px 20px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            color: #e0e0e0;
        }
        #stx-bib-card.visible { display: block; opacity: 1; }

        .stx-bib-title {
            font-size: 14px;
            font-weight: 600;
            color: #f0f0f0;
            line-height: 1.4;
            margin-bottom: 6px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .stx-bib-authors {
            font-size: 12px;
            color: #a0a0c0;
            margin-bottom: 4px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .stx-bib-venue {
            font-size: 11px;
            font-style: italic;
            color: #8080b0;
            margin-bottom: 4px;
        }
        .stx-bib-doi {
            font-size: 10px;
            color: #6090d0;
        }
        .stx-bib-abstract {
            font-size: 11px;
            color: #b0b0c0;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* Citation marker styling */
        .stx-cite {
            cursor: help;
            border-bottom: 1px dotted rgba(96, 144, 208, 0.5);
        }
        .stx-cite:hover {
            border-bottom-color: #6090d0;
        }
    </style>
    """

    js = textwrap.dedent("""
    <script>
    (function() {
        var existing = document.getElementById('stx-bib-card');
        if (!existing) {
            var card = document.createElement('div');
            card.id = 'stx-bib-card';
            card.innerHTML = [
                '<div class="stx-bib-title"></div>',
                '<div class="stx-bib-authors"></div>',
                '<div class="stx-bib-venue"></div>',
                '<div class="stx-bib-doi"></div>',
                '<div class="stx-bib-abstract"></div>',
            ].join('');
            document.body.appendChild(card);
        }

        var card = document.getElementById('stx-bib-card');
        var titleEl = card.querySelector('.stx-bib-title');
        var authorsEl = card.querySelector('.stx-bib-authors');
        var venueEl = card.querySelector('.stx-bib-venue');
        var doiEl = card.querySelector('.stx-bib-doi');
        var abstractEl = card.querySelector('.stx-bib-abstract');

        function attachBibListeners() {
            var cites = document.querySelectorAll('.stx-cite');

            cites.forEach(function(cite) {
                if (cite.dataset.bibListener) return;
                cite.dataset.bibListener = "true";

                cite.addEventListener('mouseenter', function() {
                    var title = cite.dataset.bibTitle || '';
                    var authors = cite.dataset.bibAuthors || '';
                    var year = cite.dataset.bibYear || '';
                    var journal = cite.dataset.bibJournal || '';
                    var doi = cite.dataset.bibDoi || '';
                    var abstract = cite.dataset.bibAbstract || '';

                    if (!title && !authors) return;

                    titleEl.textContent = title;
                    authorsEl.textContent = authors + (year ? ' (' + year + ')' : '');
                    venueEl.textContent = journal;
                    doiEl.textContent = doi ? 'DOI: ' + doi : '';
                    doiEl.style.display = doi ? 'block' : 'none';
                    abstractEl.textContent = abstract;
                    abstractEl.style.display = abstract ? 'block' : 'none';

                    var rect = cite.getBoundingClientRect();
                    var top = rect.bottom + 8;
                    var left = rect.left;

                    if (left + 380 > window.innerWidth) left = window.innerWidth - 400;
                    if (top + 200 > window.innerHeight) top = rect.top - 220;
                    if (left < 10) left = 10;

                    card.style.top = top + 'px';
                    card.style.left = left + 'px';
                    card.classList.add('visible');
                });

                cite.addEventListener('mouseleave', function() {
                    card.classList.remove('visible');
                });
            });
        }

        // MutationObserver for dynamically added citations
        if (window._stxBibObs) window._stxBibObs.disconnect();
        window._stxBibObs = new MutationObserver(attachBibListeners);
        window._stxBibObs.observe(document.body, { childList: true, subtree: true });

        setTimeout(attachBibListeners, 500);
    })();
    </script>
    """)

    st.html(css)
    st.html(js)
```

### 5.2. Injection dans `st_book()`

```python
# streamtex/book.py — dans st_book(), apres inject_link_preview_scaffold()

from .bib_preview import inject_bib_preview_scaffold
from .bib import get_bib_config

# Injecter le scaffold si la bibliographie est activee
if get_bib_config().hover_enabled:
    inject_bib_preview_scaffold()
```

---

## 6. Rendu de la bibliographie finale : `st_bibliography()`

```python
# streamtex/bib.py

def st_bibliography(
    *,
    style: Optional[Style] = None,
    title: str = "References",
    title_style: Optional[Style] = None,
    toc_lvl: Optional[str] = None,
    only_cited: bool = True,
    format: Optional[BibFormat] = None,
) -> None:
    """Render the full bibliography list.

    Typically called at the end of the last block or as a dedicated block.

    Args:
        style: Style for the bibliography container
        title: Section title (rendered via st_write)
        title_style: Style for the title. If None, uses StxStyles.big + bold.
        toc_lvl: If set, the title is registered in the TOC
        only_cited: If True, only show entries that were cited via st_cite()/cite()
        format: Override the BibConfig format for this specific rendering

    Example:
        # As a dedicated block: blocks/bck_bibliography.py
        def build():
            st_bibliography(
                title="References",
                toc_lvl="1",
                only_cited=True,
            )
    """
    from .write import st_write
    from .container import st_block
    from .space import st_space

    cfg = _bib_config
    fmt = format or cfg.format
    registry = _bib_registry

    entries = registry.get_cited_entries() if only_cited else registry.get_all_entries()

    if not entries:
        return

    # Sort entries
    if cfg.sort_by == "author":
        entries = sorted(entries, key=lambda e: (e.first_author_last.lower(), e.year))
    elif cfg.sort_by == "year":
        entries = sorted(entries, key=lambda e: (e.year, e.first_author_last.lower()))
    elif cfg.sort_by == "key":
        entries = sorted(entries, key=lambda e: e.key.lower())
    # "citation_order" = keep insertion order (default from get_cited_entries)

    # Title
    ts = title_style or (StxStyles.big + StxStyles.bold)
    if title:
        st_write(ts, title, toc_lvl=toc_lvl)
        st_space("v", 2)

    # Render each entry
    with st_block(style):
        for i, entry in enumerate(entries):
            formatted = _format_entry(entry, fmt, i + 1)
            _render(f'<p style="margin-bottom:8px;text-indent:-2em;padding-left:2em;">{formatted}</p>')


def _format_entry(entry: BibEntry, fmt: BibFormat, number: int) -> str:
    """Format a single BibEntry according to the specified format."""
    if fmt == BibFormat.APA:
        return _format_apa(entry)
    elif fmt == BibFormat.MLA:
        return _format_mla(entry)
    elif fmt == BibFormat.IEEE:
        return _format_ieee(entry, number)
    elif fmt == BibFormat.CHICAGO:
        return _format_chicago(entry)
    elif fmt == BibFormat.HARVARD:
        return _format_harvard(entry)
    else:
        return _format_apa(entry)  # Fallback


def _format_apa(entry: BibEntry) -> str:
    """Format in APA 7th edition style.

    Pattern:
        Author, A. A., & Author, B. B. (Year). Title. Journal, Volume(Number), Pages. DOI
    """
    parts = []

    # Authors
    if entry.authors:
        author_strs = []
        for i, author in enumerate(entry.authors):
            if i == len(entry.authors) - 1 and i > 0:
                author_strs.append(f"& {author}")
            else:
                author_strs.append(author)
        parts.append(", ".join(author_strs))

    # Year
    if entry.year:
        parts.append(f"({entry.year})")

    # Title
    if entry.title:
        if entry.entry_type in ("article", "inproceedings", "conference"):
            parts.append(f"{entry.title}.")
        else:
            parts.append(f"<i>{entry.title}</i>.")

    # Journal/Venue
    if entry.journal:
        venue = f"<i>{entry.journal}</i>"
        if entry.volume:
            venue += f", <i>{entry.volume}</i>"
            if entry.number:
                venue += f"({entry.number})"
        if entry.pages:
            venue += f", {entry.pages}"
        venue += "."
        parts.append(venue)
    elif entry.booktitle:
        parts.append(f"In <i>{entry.booktitle}</i>.")

    # Publisher
    if entry.publisher and entry.entry_type in ("book", "incollection"):
        parts.append(f"{entry.publisher}.")

    # DOI
    if entry.doi:
        parts.append(f'https://doi.org/{entry.doi}')

    return " ".join(parts)


def _format_ieee(entry: BibEntry, number: int) -> str:
    """Format in IEEE style.

    Pattern:
        [1] A. Author and B. Author, "Title," Journal, vol. X, no. Y, pp. Z, Year.
    """
    parts = [f"[{number}]"]

    # Authors (initials first)
    if entry.authors:
        ieee_authors = []
        for author in entry.authors:
            if "," in author:
                last, first = author.split(",", 1)
                initials = ". ".join(n[0] for n in first.strip().split() if n) + "."
                ieee_authors.append(f"{initials} {last.strip()}")
            else:
                ieee_authors.append(author)

        if len(ieee_authors) <= 2:
            parts.append(" and ".join(ieee_authors) + ",")
        else:
            parts.append(", ".join(ieee_authors[:-1]) + ", and " + ieee_authors[-1] + ",")

    # Title
    if entry.title:
        parts.append(f'"{entry.title},"')

    # Venue
    if entry.journal:
        venue = f"<i>{entry.journal}</i>"
        if entry.volume:
            venue += f", vol. {entry.volume}"
        if entry.number:
            venue += f", no. {entry.number}"
        if entry.pages:
            venue += f", pp. {entry.pages}"
        parts.append(venue + ",")
    elif entry.booktitle:
        parts.append(f"in <i>{entry.booktitle}</i>,")

    # Year
    if entry.year:
        parts.append(f"{entry.year}.")

    return " ".join(parts)


def _format_mla(entry: BibEntry) -> str:
    """Format in MLA 9th edition style.

    Pattern:
        Author. "Title." Journal, vol. X, no. Y, Year, pp. Z.
    """
    parts = []

    if entry.authors:
        parts.append(entry.authors[0] + ".")

    if entry.title:
        if entry.entry_type in ("article", "inproceedings"):
            parts.append(f'"{entry.title}."')
        else:
            parts.append(f"<i>{entry.title}</i>.")

    if entry.journal:
        venue = f"<i>{entry.journal}</i>"
        if entry.volume:
            venue += f", vol. {entry.volume}"
        if entry.number:
            venue += f", no. {entry.number}"
        if entry.year:
            venue += f", {entry.year}"
        if entry.pages:
            venue += f", pp. {entry.pages}"
        parts.append(venue + ".")

    return " ".join(parts)


def _format_chicago(entry: BibEntry) -> str:
    """Format in Chicago author-date style."""
    parts = []

    if entry.authors:
        parts.append(entry.authors[0] + ".")

    if entry.year:
        parts.append(f"{entry.year}.")

    if entry.title:
        parts.append(f'"{entry.title}."')

    if entry.journal:
        parts.append(f"<i>{entry.journal}</i>")
        if entry.volume:
            parts.append(f"{entry.volume}")
            if entry.number:
                parts[-1] += f", no. {entry.number}"
        if entry.pages:
            parts.append(f": {entry.pages}.")

    return " ".join(parts)


def _format_harvard(entry: BibEntry) -> str:
    """Format in Harvard style."""
    parts = []

    if entry.authors:
        parts.append(entry.authors[0])

    if entry.year:
        parts.append(f"({entry.year})")

    if entry.title:
        if entry.entry_type in ("article", "inproceedings"):
            parts.append(f"'{entry.title}',")
        else:
            parts.append(f"<i>{entry.title}</i>,")

    if entry.journal:
        parts.append(f"<i>{entry.journal}</i>,")
        if entry.volume:
            parts.append(f"vol. {entry.volume},")
        if entry.pages:
            parts.append(f"pp. {entry.pages}.")

    return " ".join(parts)
```

---

## 7. Export BibTeX

```python
# streamtex/bib.py

def export_bibtex(*, only_cited: bool = True) -> str:
    """Generate BibTeX output from the registry.

    Args:
        only_cited: If True, only export entries that were cited

    Returns:
        BibTeX formatted string

    Example:
        bibtex_str = export_bibtex()
        st.download_button("Download .bib", bibtex_str, "references.bib")
    """
    entries = (
        _bib_registry.get_cited_entries() if only_cited
        else _bib_registry.get_all_entries()
    )

    lines = []
    for entry in entries:
        lines.append(f"@{entry.entry_type}{{{entry.key},")

        fields = [
            ("title", entry.title),
            ("author", " and ".join(entry.authors)),
            ("year", entry.year),
            ("journal", entry.journal),
            ("booktitle", entry.booktitle),
            ("volume", entry.volume),
            ("number", entry.number),
            ("pages", entry.pages),
            ("publisher", entry.publisher),
            ("doi", entry.doi),
            ("url", entry.url),
            ("abstract", entry.abstract),
            ("note", entry.note),
        ]
        # Add extra fields
        fields.extend(entry.extra.items())

        for name, value in fields:
            if value:
                lines.append(f"  {name} = {{{value}}},")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)
```

---

## 8. Utilisation complete dans un projet

### 8.1. Fichier BibTeX du projet

```bibtex
% static/references.bib

@article{vaswani2017attention,
    title = {Attention Is All You Need},
    author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and
              Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and
              Kaiser, Lukasz and Polosukhin, Illia},
    year = {2017},
    journal = {Advances in Neural Information Processing Systems},
    volume = {30},
    pages = {5998--6008},
    doi = {10.48550/arXiv.1706.03762},
    abstract = {The dominant sequence transduction models are based on complex
                recurrent or convolutional neural networks...},
}

@inproceedings{devlin2019bert,
    title = {BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding},
    author = {Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina},
    year = {2019},
    booktitle = {Proceedings of NAACL-HLT},
    pages = {4171--4186},
    doi = {10.18653/v1/N19-1423},
}
```

### 8.2. Configuration dans book.py

```python
# book.py

import streamlit as st
import setup
import blocks

import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig
from streamtex.bib import BibConfig, BibFormat, CitationStyle
from pathlib import Path

st.set_page_config(page_title="Mon cours", layout="wide")

# Configuration bibliographie
bib_config = BibConfig(
    format=BibFormat.APA,
    citation_style=CitationStyle.AUTHOR_YEAR,
    hover_enabled=True,
    hover_show_abstract=True,
    sort_by="author",
)

bib_sources = [
    str(Path(__file__).parent / "static" / "references.bib"),
]

module_list = [
    blocks.bck_intro,
    blocks.bck_transformers,
    blocks.bck_bibliography,  # Bloc dedie pour la bibliographie
]

st_book(
    module_list,
    paginate=True,
    toc_config=TOCConfig(numerate_titles=True),
    marker_config=MarkerConfig(auto_marker_on_toc=1),
    bib_sources=bib_sources,
    bib_config=bib_config,
)
```

### 8.3. Utilisation dans un bloc

```python
# blocks/_atomic/bck_transformers_intro.py

import streamlit as st
from streamtex import *
from streamtex.bib import cite
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation

class BlockStyles:
    pass

def build():
    st_write(s.project.titles.section_title, "Architecture Transformer", toc_lvl="1")
    st_space("v", 2)

    st_write(s.big,
        "L'architecture Transformer ",
        cite("vaswani2017attention"),
        " a revolutionne le traitement du langage naturel. "
        "Basee sur le mecanisme d'attention, elle permet de capturer "
        "les dependances a longue distance sans recurrence."
    )

    st_space("v", 2)

    st_write(s.big,
        "Les modeles pre-entraines comme BERT ",
        cite("devlin2019bert"),
        " ont ensuite generalise cette architecture "
        "pour le transfer learning en NLP."
    )
```

### 8.4. Bloc bibliographie

```python
# blocks/bck_bibliography.py

from streamtex import *
from streamtex.bib import st_bibliography
from custom.styles import Styles as s

class BlockStyles:
    pass

def build():
    st_bibliography(
        title="References",
        title_style=s.project.titles.section_title,
        toc_lvl="1",
        only_cited=True,
    )
```

---

## 9. Compatibilite avec le pipeline d'export

### 9.1. Citations inline

Les citations sont rendues via `_render()`, donc automatiquement incluses dans
l'export HTML. Les `data-bib-*` attributes sont preserves dans le HTML exporte
mais le hover JS ne sera pas actif (pas de JavaScript dans l'export statique).

### 9.2. Bibliographie finale

`st_bibliography()` utilise `_render()` pour chaque entree. L'export HTML
contiendra la bibliographie formatee complete.

### 9.3. Bouton de telechargement BibTeX

```python
# Dans un bloc
bibtex_str = export_bibtex(only_cited=True)
st.download_button(
    "Telecharger .bib",
    bibtex_str,
    "references.bib",
    mime="application/x-bibtex",
    key="bck_bib_download"
)
```

Le `st.download_button` est un widget Streamlit interactif, invisible dans l'export
(comportement standard).

---

## 10. Tests unitaires

### 10.1. Fichier : `tests/test_bib.py`

```python
# tests/test_bib.py

import pytest
from streamtex.bib import (
    BibEntry, BibConfig, BibFormat, CitationStyle,
    BibRegistry, BibParseError,
    load_bibtex, load_bib_json, export_bibtex,
    _format_apa, _format_ieee, _format_mla,
    _parse_bibtex,
)


class TestBibEntry:
    def test_first_author_last_comma_format(self):
        e = BibEntry(key="test", authors=["Vaswani, Ashish"])
        assert e.first_author_last == "Vaswani"

    def test_first_author_last_space_format(self):
        e = BibEntry(key="test", authors=["Ashish Vaswani"])
        assert e.first_author_last == "Vaswani"

    def test_authors_short_single(self):
        e = BibEntry(key="test", authors=["Vaswani, Ashish"])
        assert e.authors_short == "Vaswani"

    def test_authors_short_two(self):
        e = BibEntry(key="test", authors=["Vaswani, Ashish", "Shazeer, Noam"])
        assert e.authors_short == "Vaswani & Shazeer"

    def test_authors_short_three_plus(self):
        e = BibEntry(key="test", authors=["Vaswani, A", "Shazeer, N", "Parmar, N"])
        assert e.authors_short == "Vaswani et al."

    def test_no_authors(self):
        e = BibEntry(key="test")
        assert e.first_author_last == "Unknown"
        assert e.authors_short == "Unknown"


class TestBibRegistry:
    def setup_method(self):
        self.reg = BibRegistry()

    def test_register_and_get(self):
        e = BibEntry(key="test1", title="Test Title")
        self.reg.register(e)
        assert self.reg.get("test1") is e

    def test_get_unknown_returns_none(self):
        assert self.reg.get("unknown") is None

    def test_cite_returns_number(self):
        self.reg.register(BibEntry(key="a"))
        self.reg.register(BibEntry(key="b"))
        assert self.reg.cite("a") == 1
        assert self.reg.cite("b") == 2
        assert self.reg.cite("a") == 1  # Same number on second cite

    def test_cite_unknown_returns_zero(self):
        assert self.reg.cite("unknown") == 0

    def test_get_cited_entries_order(self):
        self.reg.register(BibEntry(key="b"))
        self.reg.register(BibEntry(key="a"))
        self.reg.cite("b")
        self.reg.cite("a")
        cited = self.reg.get_cited_entries()
        assert [e.key for e in cited] == ["b", "a"]

    def test_reset(self):
        self.reg.register(BibEntry(key="a"))
        self.reg.cite("a")
        self.reg.reset()
        assert len(self.reg) == 0
        assert self.reg.get_cited_entries() == []

    def test_contains(self):
        self.reg.register(BibEntry(key="a"))
        assert "a" in self.reg
        assert "b" not in self.reg


class TestBibTeXParser:
    def test_simple_article(self):
        bib = '''
        @article{test2024,
            title = {Test Title},
            author = {Smith, John and Doe, Jane},
            year = {2024},
            journal = {Test Journal},
        }
        '''
        entries = _parse_bibtex(bib)
        assert len(entries) == 1
        assert entries[0].key == "test2024"
        assert entries[0].title == "Test Title"
        assert entries[0].authors == ["Smith, John", "Doe, Jane"]
        assert entries[0].year == "2024"
        assert entries[0].journal == "Test Journal"

    def test_multiple_entries(self):
        bib = '''
        @article{a, title={A}}
        @book{b, title={B}}
        '''
        entries = _parse_bibtex(bib)
        assert len(entries) == 2
        assert entries[0].key == "a"
        assert entries[1].key == "b"

    def test_skips_comments(self):
        bib = '''
        @comment{This is a comment}
        @article{real, title={Real}}
        '''
        entries = _parse_bibtex(bib)
        assert len(entries) == 1

    def test_bare_number_year(self):
        bib = '@article{test, year = 2024}'
        entries = _parse_bibtex(bib)
        assert entries[0].year == "2024"

    def test_quoted_values(self):
        bib = '@article{test, title = "Quoted Title"}'
        entries = _parse_bibtex(bib)
        assert entries[0].title == "Quoted Title"

    def test_nested_braces(self):
        bib = '@article{test, title = {A {B} C}}'
        entries = _parse_bibtex(bib)
        assert entries[0].title == "A {B} C"

    def test_empty_input(self):
        assert _parse_bibtex("") == []
        assert _parse_bibtex("% just a comment") == []


class TestFormatAPA:
    def test_article(self):
        e = BibEntry(
            key="test", entry_type="article",
            authors=["Smith, J.", "Doe, J."],
            year="2024", title="Test Title",
            journal="Test Journal", volume="10", number="2", pages="1-15",
            doi="10.1234/test"
        )
        result = _format_apa(e)
        assert "Smith, J." in result
        assert "(2024)" in result
        assert "Test Title" in result
        assert "<i>Test Journal</i>" in result
        assert "10.1234/test" in result


class TestFormatIEEE:
    def test_numbered(self):
        e = BibEntry(
            key="test", entry_type="article",
            authors=["Smith, John"],
            year="2024", title="Test Title",
            journal="IEEE Trans.", volume="5", pages="10-20"
        )
        result = _format_ieee(e, 1)
        assert result.startswith("[1]")
        assert "J. Smith" in result
        assert '"Test Title,"' in result


class TestExportBibTeX:
    def test_exports_valid_bibtex(self):
        from streamtex.bib import _bib_registry
        _bib_registry.reset()
        _bib_registry.register(BibEntry(
            key="test2024", entry_type="article",
            title="Test", authors=["Smith, J."], year="2024"
        ))
        _bib_registry.cite("test2024")

        result = export_bibtex(only_cited=True)
        assert "@article{test2024," in result
        assert "title = {Test}" in result
        assert "author = {Smith, J.}" in result
        assert "year = {2024}" in result

        _bib_registry.reset()
```

Estimation : **~50 tests** couvrant le parsing BibTeX, le registre, le formatage
(APA/IEEE/MLA/Chicago/Harvard), l'export, et les cas limites.

---

## 11. Arbre de fichiers impactes

| Fichier | Action | Risque |
|---------|--------|--------|
| `streamtex/bib.py` | CREER | Nul (nouveau module) |
| `streamtex/bib_preview.py` | CREER | Nul (nouveau module) |
| `streamtex/__init__.py` | MODIFIER (imports bib) | Faible |
| `streamtex/book.py` | MODIFIER (bib_sources, bib_config params + reset + scaffold) | Modere |
| `tests/test_bib.py` | CREER | Nul |
| `documentation/coding_standards.md` | MODIFIER (section Bib) | Nul |
| `CLAUDE.md` | MODIFIER (mentionner bib.py) | Nul |

**Seul `book.py` est structurellement modifie** (ajout de 2 parametres optionnels
a `st_book()` et ~15 lignes de setup). Le reste est additif.

---

## 12. Plan d'implementation par phases

### Phase 1 : Modele de donnees et registre (1-2h)

1. Creer `streamtex/bib.py` avec `BibEntry`, `BibConfig`, `BibRegistry`
2. Implementer `set_bib_config()`, `get_bib_config()`, `reset_bib_registry()`
3. Creer `tests/test_bib.py` (~20 tests registre + modele)
4. Verifier : `uv run pytest tests/ -v`

### Phase 2 : Parseur BibTeX et JSON (2-3h)

1. Implementer `_parse_bibtex()` et `load_bibtex()`
2. Implementer `load_bib_json()`
3. Ajouter tests du parseur (~15 tests)
4. Tester avec un vrai fichier .bib

### Phase 3 : Formatage bibliographique (2h)

1. Implementer `_format_apa()`, `_format_ieee()`, `_format_mla()`
2. Implementer `_format_chicago()`, `_format_harvard()`
3. Implementer `st_bibliography()` et `export_bibtex()`
4. Ajouter tests de formatage (~15 tests)

### Phase 4 : Citations inline (1-2h)

1. Implementer `st_cite()` et `cite()`
2. Tester l'integration avec `st_write()`
3. Ajouter exports dans `__init__.py`

### Phase 5 : Hover preview (1-2h)

1. Creer `streamtex/bib_preview.py` (scaffold JS/CSS)
2. Integrer dans `st_book()` (reset, chargement, injection scaffold)
3. Test visuel dans un projet demo

### Phase 6 : Integration et documentation (1h)

1. Modifier `st_book()` pour accepter `bib_sources` et `bib_config`
2. Mettre a jour `coding_standards.md` et `CLAUDE.md`
3. Creer un bloc de demonstration dans les manuels

### Phase 7 : Bloc de demonstration (optionnel, 1h)

1. Creer `static/references.bib` dans stx_manual_advanced
2. Creer `blocks/_atomic/bck_bibliography_demo.py`
3. Montrer les 3 styles de citation et le rendu bibliographique

---

## 13. Alternatives evaluees et rejetees

### Alternative 1 : Utiliser pybtex comme dependance obligatoire

`pybtex` est un parseur BibTeX complet avec formatage. Rejete car :
- Ajoute une dependance lourde pour un usage qui peut etre leger
- Le parseur built-in couvre 95% des cas d'usage
- Peut etre offert comme backend optionnel (`uv add pybtex`)

### Alternative 2 : CSL (Citation Style Language)

CSL est le standard pour le formatage bibliographique (utilise par Zotero, Mendeley).
Rejete pour la Phase 1 car :
- Necessite un processeur CSL (citeproc-py, 5000+ lignes)
- Sur-ingenierie pour un premier passage
- A reconsiderer pour une version 0.4.0 si les 5 formats built-in ne suffisent pas

### Alternative 3 : Integration Zotero API

Charger les references directement depuis une bibliotheque Zotero.
Rejete pour la Phase 1 car : ajout de complexite (auth, API), mais excellent
candidat pour une Phase 2 (comme le backend API v4 pour Google Sheets).

### Alternative 4 : Annotation `@bib` dans le texte

Pattern `st_write(s.medium, "Selon @vaswani2017 les transformers...")` avec parsing
du `@key` dans le texte brut. Rejete car : fragile (collision avec emails, usernames),
pas explicite, contraire a la philosophie StreamTeX (fonctions explicites vs markup).

---

## 14. Diagramme d'architecture

```
┌───────────────────────────────────────────────────────────┐
│  book.py — st_book(bib_sources=[...], bib_config=...)     │
│                                                           │
│  1. reset_bib_registry()                                  │
│  2. load_bibtex("refs.bib") → BibRegistry.register_many() │
│  3. inject_bib_preview_scaffold() [JS/CSS hover]          │
│  4. Render blocks...                                      │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│  Bloc utilisateur (bck_intro.py)                          │
│                                                           │
│  st_write(s.big,                                          │
│      "Selon ", cite("vaswani2017"), ", les transformers..." │
│  )                                                        │
│                                                           │
│  # cite() → BibRegistry.cite("vaswani2017") → #1         │
│  # → <span class="stx-cite" data-bib-*>...</span>        │
│  # → rendu via _render() (Streamlit + Export)             │
└───────────────────────────┬───────────────────────────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
┌──────────────────────┐  ┌───────────────────────────┐
│  Hover Preview (JS)  │  │  Export HTML (statique)    │
│                      │  │                           │
│  .stx-cite:hover     │  │  <span>citations inline   │
│  → #stx-bib-card     │  │  <p>bibliographie APA     │
│  → title, authors,   │  │                           │
│    year, journal,    │  │  Pas de hover JS dans     │
│    DOI, abstract     │  │  l'export (comportement   │
│                      │  │  standard)                │
└──────────────────────┘  └───────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│  bck_bibliography.py                                      │
│                                                           │
│  st_bibliography(                                         │
│      title="References",                                  │
│      toc_lvl="1",                                         │
│      format=BibFormat.APA,                                │
│      only_cited=True                                      │
│  )                                                        │
│  # → Genere la liste formatee des references citees       │
│  # → Export HTML inclut la bibliographie                  │
│                                                           │
│  bibtex_str = export_bibtex()                             │
│  st.download_button("Download .bib", bibtex_str, ...)     │
│  # → Widget interactif (absent de l'export)               │
└───────────────────────────────────────────────────────────┘
```

### Flux de donnees complet

```
.bib / .json file
    │
    ▼ load_bibtex() / load_bib_json()
    │
BibRegistry (singleton)
    │
    ├──→ cite("key") ──→ <span class="stx-cite" data-bib-*>label</span>
    │                        │
    │                        ├──→ _render() → Streamlit iframe
    │                        └──→ _render() → Export buffer
    │
    ├──→ st_bibliography() ──→ Formatted entries (APA/IEEE/MLA...)
    │                             │
    │                             └──→ _render() → Both pipelines
    │
    └──→ export_bibtex() ──→ BibTeX string ──→ st.download_button()
```

---

## 15. Questions ouvertes

1. **Faut-il supporter la resolution automatique de DOI (crossref API) pour enrichir
   les entrees incompletes ?** Ajoute une dependance reseau mais reduit la saisie manuelle.

2. **La fonction `cite()` doit-elle etre importee depuis `streamtex` directement
   (`from streamtex import cite`) ou depuis `streamtex.bib` ?** Position actuelle :
   exporter depuis `__init__.py` pour la commodite.

3. **Faut-il un mode "footnote" pour les citations (note de bas de page) ?**
   Les footnotes sont complexes en HTML/Streamlit. A evaluer pour une version future.

4. **Faut-il un helper `show_reference()` dans block_helpers.py ?** Un helper type
   `show_reference("vaswani2017")` qui affiche la reference complete dans un bloc style.
   Potentiellement utile pour les slides pedagogiques.

5. **Crossref avec TOC** : Faut-il que `st_bibliography()` genere des ancres pour
   que `cite("key")` puisse linker vers l'entree dans la bibliographie (comme LaTeX) ?
   Faisable avec le pattern `#anchor` existant dans `contain_link()`.

---

*Proposition generee le 2026-02-20 apres analyse approfondie du projet StreamTeX v0.2.0.*
*Aucun fichier modifie. Ce document est un plan d'implementation a valider.*
