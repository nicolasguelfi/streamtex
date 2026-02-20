"""Bibliography system for StreamTeX.

Provides:
- BibEntry dataclass with extensible fields (via ``extra`` dict)
- BibRegistry singleton (same pattern as TOCRegistry)
- Multi-format import: BibTeX, JSON, RIS, CSL-JSON
- Multi-format output: APA, MLA, IEEE, Chicago, Harvard
- Inline citations: st_cite() and cite()
- Bibliography rendering: st_bibliography()
- BibTeX export: export_bibtex()
- BibRefs proxy: st_refs.key → cite("key") with IDE autocompletion via stubs

The import system is extensible: register new parsers via register_bib_parser().

Usage:
    from streamtex.bib import (
        BibConfig, BibFormat, CitationStyle,
        load_bib, load_bibtex, load_bib_json, load_bib_ris, load_bib_csl_json,
        cite, st_cite, st_bibliography, export_bibtex,
        get_bib_registry, set_bib_config,
        st_refs, generate_bib_stubs,
    )
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BibFormat(Enum):
    """Supported bibliography output formats."""
    APA = "apa"
    MLA = "mla"
    IEEE = "ieee"
    CHICAGO = "chicago"
    HARVARD = "harvard"


class CitationStyle(Enum):
    """How inline citations are displayed."""
    AUTHOR_YEAR = "author_year"
    NUMERIC = "numeric"
    SUPERSCRIPT = "superscript"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BibParseError(Exception):
    """Raised when bibliography parsing fails."""
    pass


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class BibEntry:
    """A single bibliographic reference.

    Core fields cover the most common attributes.  Any additional fields
    (from BibTeX, RIS, CSL-JSON, etc.) are stored in ``extra`` and remain
    accessible for custom formatters.

    To add a new "first-class" field in the future, simply add it as an
    attribute with a default value — all existing parsers/formatters will
    continue to work without modification.
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
    isbn: str = ""
    issn: str = ""
    edition: str = ""
    editor: str = ""
    institution: str = ""
    school: str = ""
    address: str = ""
    month: str = ""
    language: str = ""
    keywords: str = ""
    extra: Dict[str, str] = field(default_factory=dict)

    # --- Computed properties -------------------------------------------------

    @property
    def first_author_last(self) -> str:
        """Last name of the first author."""
        if not self.authors:
            return "Unknown"
        first = self.authors[0]
        if "," in first:
            return first.split(",")[0].strip()
        parts = first.strip().split()
        return parts[-1] if parts else "Unknown"

    @property
    def authors_short(self) -> str:
        """Short form: 'Vaswani et al.' or 'Vaswani & Shazeer'."""
        if not self.authors:
            return "Unknown"

        def _last(author: str) -> str:
            if "," in author:
                return author.split(",")[0].strip()
            parts = author.strip().split()
            return parts[-1] if parts else author

        if len(self.authors) == 1:
            return _last(self.authors[0])
        if len(self.authors) == 2:
            return f"{_last(self.authors[0])} & {_last(self.authors[1])}"
        return f"{_last(self.authors[0])} et al."

    def get_field(self, name: str, default: str = "") -> str:
        """Get any field by name — checks attributes first, then extra."""
        if hasattr(self, name) and name != "extra":
            val = getattr(self, name)
            if isinstance(val, str):
                return val or default
            return default
        return self.extra.get(name, default)


# ---------------------------------------------------------------------------
# Configuration (DI pattern)
# ---------------------------------------------------------------------------

@dataclass
class BibConfig:
    """Configuration for the bibliography system.

    Attributes:
        format: Output format for st_bibliography()
        citation_style: Inline citation display style
        hover_enabled: Show hover preview card on citations
        hover_show_abstract: Include abstract in hover card
        sort_by: "author" | "year" | "key" | "citation_order"
        locale: Language for connector words ("en" or "fr")
    """
    format: BibFormat = BibFormat.APA
    citation_style: CitationStyle = CitationStyle.AUTHOR_YEAR
    hover_enabled: bool = True
    hover_show_abstract: bool = False
    sort_by: str = "author"
    locale: str = "en"


_bib_config: BibConfig = BibConfig()


def set_bib_config(config: BibConfig) -> None:
    """Set global bibliography configuration."""
    global _bib_config
    _bib_config = config


def get_bib_config() -> BibConfig:
    """Get current bibliography configuration."""
    return _bib_config


# ---------------------------------------------------------------------------
# Registry (singleton, same pattern as TOCRegistry)
# ---------------------------------------------------------------------------

class BibRegistry:
    """Singleton registry storing bibliographic entries and citation tracking."""

    def __init__(self):
        self._entries: Dict[str, BibEntry] = {}
        self._cited: List[str] = []
        self._counter: int = 0

    def register(self, entry: BibEntry) -> None:
        """Register an entry (overwrites if key exists)."""
        self._entries[entry.key] = entry

    def register_many(self, entries: List[BibEntry]) -> None:
        """Register multiple entries."""
        for entry in entries:
            self.register(entry)

    def get(self, key: str) -> Optional[BibEntry]:
        """Retrieve an entry by key (None if not found)."""
        return self._entries.get(key)

    def cite(self, key: str) -> int:
        """Mark *key* as cited; return its 1-based citation number."""
        if key not in self._entries:
            logger.warning(f"BibRegistry: citation key '{key}' not found")
            return 0
        if key not in self._cited:
            self._cited.append(key)
            self._counter += 1
        return self._cited.index(key) + 1

    def get_cited_entries(self) -> List[BibEntry]:
        """Return cited entries in citation order."""
        return [self._entries[k] for k in self._cited if k in self._entries]

    def get_all_entries(self) -> List[BibEntry]:
        """Return all registered entries."""
        return [*self._entries.values()]

    def list_keys(self) -> List[str]:
        """Return sorted list of all keys."""
        return sorted(self._entries.keys())

    def reset(self) -> None:
        """Clear all entries and citations."""
        self._entries.clear()
        self._cited.clear()
        self._counter = 0

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        return key in self._entries


_bib_registry = BibRegistry()


def reset_bib_registry() -> None:
    """Reset the global bibliography registry."""
    _bib_registry.reset()


def get_bib_registry() -> BibRegistry:
    """Get the global bibliography registry."""
    return _bib_registry


# ===================================================================
# IMPORT: Extensible parser registry
# ===================================================================

# Maps file extension → parser function(path) -> List[BibEntry]
_parsers: Dict[str, Callable[[str], List[BibEntry]]] = {}


def register_bib_parser(extension: str, parser: Callable[[str], List[BibEntry]]) -> None:
    """Register a custom bibliography parser for a file extension.

    Args:
        extension: File extension without dot (e.g. "bib", "ris")
        parser: Callable that takes a file path and returns List[BibEntry]

    Example:
        def parse_yaml(path):
            ...
            return [BibEntry(...)]

        register_bib_parser("yaml", parse_yaml)
    """
    _parsers[extension.lower().lstrip(".")] = parser


def load_bib(path: str) -> List[BibEntry]:
    """Load bibliography entries from a file (auto-detects format by extension).

    Supported extensions: .bib, .json, .ris, .csl-json (and any registered via
    register_bib_parser()).

    Args:
        path: Path to the bibliography file

    Returns:
        List of BibEntry objects

    Raises:
        ValueError: If the file extension is not supported
        FileNotFoundError: If the file does not exist
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Bibliography file not found: {path}")

    ext = _get_extension(path)

    if ext in _parsers:
        return _parsers[ext](path)

    raise ValueError(
        f"Unsupported bibliography format: '.{ext}'. "
        f"Supported: {', '.join(sorted(_parsers.keys()))}. "
        f"Use register_bib_parser() to add custom formats."
    )


def _get_extension(path: str) -> str:
    """Get normalized extension (handles .csl-json → csljson)."""
    base = os.path.basename(path).lower()
    # Handle compound extensions
    if base.endswith(".csl-json") or base.endswith(".csl.json"):
        return "csljson"
    parts = base.rsplit(".", 1)
    return parts[-1] if len(parts) > 1 else ""


# ===================================================================
# PARSER: BibTeX
# ===================================================================

def load_bibtex(path: str) -> List[BibEntry]:
    """Parse a .bib file into BibEntry objects."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return parse_bibtex_string(content)


def parse_bibtex_string(content: str) -> List[BibEntry]:
    """Parse BibTeX content string into BibEntry objects."""
    entries = []
    pattern = re.compile(r'@(\w+)\s*\{', re.IGNORECASE)

    pos = 0
    while pos < len(content):
        match = pattern.search(content, pos)
        if not match:
            break

        entry_type = match.group(1).lower()
        brace_start = match.end() - 1

        # Skip non-entry types
        if entry_type in ("comment", "string", "preamble"):
            end = _find_matching_brace(content, brace_start)
            pos = end + 1 if end >= 0 else len(content)
            continue

        end = _find_matching_brace(content, brace_start)
        if end < 0:
            logger.warning(f"BibTeX: unmatched brace at position {brace_start}")
            break

        body = content[brace_start + 1:end]
        comma_pos = body.find(",")
        if comma_pos < 0:
            pos = end + 1
            continue

        key = body[:comma_pos].strip()
        fields = _parse_bibtex_fields(body[comma_pos + 1:])

        entry = _fields_to_entry(key, entry_type, fields)
        entries.append(entry)
        pos = end + 1

    return entries


def _find_matching_brace(content: str, start: int) -> int:
    """Find position of matching closing brace (handles nesting)."""
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
        if ch == '"' and depth > 0:
            in_string = not in_string
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
    """Parse field=value pairs from a BibTeX entry body."""
    fields = {}
    pattern = re.compile(
        r'(\w+)\s*=\s*(?:'
        r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        r'|"([^"]*)"'
        r'|(\d+)'
        r')',
        re.DOTALL
    )
    for match in pattern.finditer(fields_str):
        name = match.group(1).lower()
        value = match.group(2) or match.group(3) or match.group(4) or ""
        value = re.sub(r'\s+', ' ', value.replace("\n", " ")).strip()
        fields[name] = value
    return fields


# ===================================================================
# PARSER: JSON
# ===================================================================

def load_bib_json(path: str) -> List[BibEntry]:
    """Parse a JSON bibliography file.

    Expected format: a JSON array of objects with "key", "title", "authors", etc.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    entries = []
    for item in data:
        if not isinstance(item, dict) or "key" not in item:
            continue
        fields = {k: v for k, v in item.items() if k != "key"}
        entry = _fields_to_entry(item["key"], fields.pop("entry_type", "misc"), fields)
        entries.append(entry)
    return entries


# ===================================================================
# PARSER: RIS (Research Information Systems)
# ===================================================================

def load_bib_ris(path: str) -> List[BibEntry]:
    """Parse a .ris file into BibEntry objects.

    RIS format uses two-letter tags (TY, AU, TI, etc.).
    Reference: https://en.wikipedia.org/wiki/RIS_(file_format)
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return parse_ris_string(content)


def parse_ris_string(content: str) -> List[BibEntry]:
    """Parse RIS content string into BibEntry objects."""
    entries = []
    current_fields: Dict[str, List[str]] = {}
    current_type = "misc"

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # RIS lines: TAG  - VALUE
        match = re.match(r'^([A-Z][A-Z0-9])\s{2}-\s?(.*)', line)
        if not match:
            continue

        tag = match.group(1)
        value = match.group(2).strip()

        if tag == "TY":
            current_type = _ris_type_to_bibtex(value)
            current_fields = {}
        elif tag == "ER":
            # End of record
            entry = _ris_fields_to_entry(current_type, current_fields)
            if entry:
                entries.append(entry)
            current_fields = {}
        else:
            current_fields.setdefault(tag, []).append(value)

    return entries


# RIS type → BibTeX type mapping
_RIS_TYPE_MAP = {
    "JOUR": "article", "JFULL": "article",
    "BOOK": "book", "CHAP": "incollection",
    "CONF": "inproceedings", "CPAPER": "inproceedings",
    "THES": "phdthesis", "RPRT": "techreport",
    "UNPB": "unpublished", "ELEC": "online",
    "GEN": "misc", "MGZN": "article", "NEWS": "article",
}

# RIS tag → BibEntry field mapping
_RIS_TAG_MAP = {
    "TI": "title", "T1": "title",
    "JO": "journal", "JF": "journal", "JA": "journal", "T2": "booktitle",
    "VL": "volume", "IS": "number",
    "SP": "pages_start", "EP": "pages_end",
    "PB": "publisher", "PY": "year", "Y1": "year", "DA": "date",
    "DO": "doi", "UR": "url", "AB": "abstract",
    "N1": "note", "KW": "keywords",
    "SN": "isbn", "LA": "language",
    "CY": "address", "ET": "edition",
    "ED": "editor",
}


def _ris_type_to_bibtex(ris_type: str) -> str:
    return _RIS_TYPE_MAP.get(ris_type.upper(), "misc")


def _ris_fields_to_entry(entry_type: str, fields: Dict[str, List[str]]) -> Optional[BibEntry]:
    """Convert RIS field dict to BibEntry."""
    # Authors
    authors = fields.get("AU", []) or fields.get("A1", [])

    # Build key from first author + year
    year = ""
    for tag in ("PY", "Y1", "DA"):
        if tag in fields:
            year_val = fields[tag][0]
            year = year_val[:4]  # Extract YYYY
            break

    first_author_last = "unknown"
    if authors:
        first = authors[0]
        first_author_last = first.split(",")[0].strip().lower() if "," in first else first.split()[-1].lower()

    key = f"{first_author_last}{year}"

    # Resolve simple fields
    result_fields: Dict[str, Any] = {"authors": authors}
    for ris_tag, bib_field in _RIS_TAG_MAP.items():
        if ris_tag in fields:
            result_fields[bib_field] = fields[ris_tag][0]

    # Handle pages (SP/EP → "start-end")
    sp = result_fields.pop("pages_start", "")
    ep = result_fields.pop("pages_end", "")
    if sp:
        result_fields["pages"] = f"{sp}-{ep}" if ep else sp

    # Handle date → year
    if "date" in result_fields and "year" not in result_fields:
        result_fields["year"] = result_fields.pop("date")[:4]
    result_fields.pop("date", None)

    # Keywords (may be multiple KW tags)
    if "KW" in fields:
        result_fields["keywords"] = "; ".join(fields["KW"])

    return _fields_to_entry(key, entry_type, result_fields)


# ===================================================================
# PARSER: CSL-JSON (Zotero/Mendeley native format)
# ===================================================================

def load_bib_csl_json(path: str) -> List[BibEntry]:
    """Parse a CSL-JSON file into BibEntry objects.

    CSL-JSON is the native export format of Zotero and other reference managers.
    Reference: https://citeproc-js.readthedocs.io/en/latest/csl-json/markup.html
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    entries = []
    for item in data:
        if not isinstance(item, dict):
            continue
        entry = _csl_item_to_entry(item)
        if entry:
            entries.append(entry)
    return entries


# CSL type → BibTeX type
_CSL_TYPE_MAP = {
    "article-journal": "article", "article": "article",
    "book": "book", "chapter": "incollection",
    "paper-conference": "inproceedings",
    "thesis": "phdthesis", "report": "techreport",
    "webpage": "online", "manuscript": "unpublished",
}


def _csl_item_to_entry(item: Dict) -> Optional[BibEntry]:
    """Convert a single CSL-JSON item to BibEntry."""
    entry_type = _CSL_TYPE_MAP.get(item.get("type", ""), "misc")

    # Authors
    authors = []
    for author in item.get("author", []):
        family = author.get("family", "")
        given = author.get("given", "")
        if family and given:
            authors.append(f"{family}, {given}")
        elif family:
            authors.append(family)

    # Year (from "issued" date-parts)
    year = ""
    issued = item.get("issued", {})
    date_parts = issued.get("date-parts", [[]])
    if date_parts and date_parts[0]:
        year = str(date_parts[0][0])

    # Key
    key = item.get("id", "")
    if not key:
        first_last = authors[0].split(",")[0].strip().lower() if authors else "unknown"
        key = f"{first_last}{year}"

    # Journal (container-title in CSL)
    journal = item.get("container-title", "")
    if isinstance(journal, list):
        journal = journal[0] if journal else ""

    # Pages
    pages = item.get("page", "")

    fields: Dict[str, Any] = {
        "authors": authors,
        "title": item.get("title", ""),
        "year": year,
        "journal": journal,
        "volume": str(item.get("volume", "")),
        "number": str(item.get("issue", "")),
        "pages": pages,
        "publisher": item.get("publisher", ""),
        "doi": item.get("DOI", ""),
        "url": item.get("URL", ""),
        "abstract": item.get("abstract", ""),
        "isbn": item.get("ISBN", ""),
        "issn": item.get("ISSN", ""),
        "language": item.get("language", ""),
    }

    return _fields_to_entry(key, entry_type, fields)


# ===================================================================
# Shared field → BibEntry builder
# ===================================================================

# Fields that are directly mapped to BibEntry attributes
_KNOWN_FIELDS = {
    "title", "year", "journal", "volume", "number", "pages",
    "publisher", "booktitle", "doi", "url", "abstract", "note",
    "isbn", "issn", "edition", "editor", "institution", "school",
    "address", "month", "language", "keywords",
}


def _fields_to_entry(key: str, entry_type: str, fields: Dict[str, Any]) -> BibEntry:
    """Build a BibEntry from a flat dict of fields + extras."""
    # Extract authors
    authors = fields.pop("authors", [])
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(" and ")]
    elif "author" in fields:
        raw = fields.pop("author")
        authors = [a.strip() for a in raw.split(" and ")] if isinstance(raw, str) else raw

    kwargs: Dict[str, Any] = {"key": key, "entry_type": entry_type, "authors": authors}
    extra: Dict[str, str] = {}

    for k, v in fields.items():
        k_lower = k.lower()
        if k_lower in _KNOWN_FIELDS:
            kwargs[k_lower] = str(v) if not isinstance(v, str) else v
        else:
            extra[k_lower] = str(v) if not isinstance(v, str) else v

    kwargs["extra"] = extra
    return BibEntry(**kwargs)


# ===================================================================
# Register built-in parsers
# ===================================================================

register_bib_parser("bib", load_bibtex)
register_bib_parser("json", load_bib_json)
register_bib_parser("ris", load_bib_ris)
register_bib_parser("csljson", load_bib_csl_json)


# ===================================================================
# CITATION: inline
# ===================================================================

def cite(*keys: str, prefix: str = "", suffix: str = "") -> str:
    """Return citation HTML fragment for use in st_write().

    Unlike st_cite() which renders immediately, cite() returns a string
    for embedding inline:

        st_write(s.big, "Selon ", cite("vaswani2017"), " les transformers...")

    Args:
        *keys: One or more BibEntry keys
        prefix: Text before citation (e.g. "cf. ")
        suffix: Text after citation (e.g. ", p. 42")

    Returns:
        HTML string (e.g. "(Vaswani et al., 2017)")
    """
    cfg = _bib_config
    parts = []

    for key in keys:
        entry = _bib_registry.get(key)
        if entry is None:
            logger.warning(f"cite: key '{key}' not found")
            parts.append(f"[{key}?]")
            continue

        num = _bib_registry.cite(key)

        if cfg.citation_style == CitationStyle.AUTHOR_YEAR:
            label = f"{entry.authors_short}, {entry.year}"
        elif cfg.citation_style == CitationStyle.NUMERIC:
            label = str(num)
        else:  # SUPERSCRIPT
            label = str(num)

        hover_attrs = ""
        if cfg.hover_enabled:
            # Resolve best URL: DOI link > explicit URL > empty
            ref_url = ""
            if entry.doi:
                ref_url = f"https://doi.org/{entry.doi}"
            elif entry.url:
                ref_url = entry.url
            hover_attrs = (
                f' class="stx-cite"'
                f' data-bib-key="{key}"'
                f' data-bib-title="{_escape_attr(entry.title)}"'
                f' data-bib-authors="{_escape_attr(", ".join(entry.authors))}"'
                f' data-bib-year="{entry.year}"'
                f' data-bib-journal="{_escape_attr(entry.journal or entry.booktitle)}"'
                f' data-bib-doi="{entry.doi}"'
                f' data-bib-url="{_escape_attr(ref_url)}"'
                f' data-bib-volume="{entry.volume}"'
                f' data-bib-pages="{entry.pages}"'
                f' data-bib-abstract="{_escape_attr(entry.abstract[:200]) if cfg.hover_show_abstract and entry.abstract else ""}"'
            )
        parts.append(f'<span{hover_attrs}>{label}</span>')

    # Assemble
    if cfg.citation_style == CitationStyle.SUPERSCRIPT:
        inner = ",".join(parts)
        return f"{prefix}<sup>{inner}</sup>{suffix}"
    elif cfg.citation_style == CitationStyle.NUMERIC:
        inner = ", ".join(parts)
        return f"{prefix}[{inner}]{suffix}"
    else:
        inner = "; ".join(parts)
        return f"{prefix}({inner}){suffix}"


def st_cite(*keys: str, prefix: str = "", suffix: str = "",
            style=None) -> None:
    """Render inline citation(s) immediately via _render().

    Args:
        *keys: One or more BibEntry keys
        prefix: Text before citation
        suffix: Text after citation
        style: Optional Style override for the citation span
    """
    from .export import _render
    from .styles import StxStyles

    resolved_style = style or StxStyles.none
    html = f'<span style="{resolved_style}" class="stx-citation">{cite(*keys, prefix=prefix, suffix=suffix)}</span>'
    _render(html)


def _escape_attr(text: str) -> str:
    """Escape text for HTML data attributes."""
    return (text.replace("&", "&amp;").replace('"', "&quot;")
            .replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;"))


# ===================================================================
# BIBLIOGRAPHY: rendering
# ===================================================================

def st_bibliography(*, style=None, title: str = "References",
                    title_style=None, toc_lvl: Optional[str] = None,
                    only_cited: bool = True,
                    format: Optional[BibFormat] = None) -> None:
    """Render the full bibliography list.

    Args:
        style: Style for the bibliography container
        title: Section title
        title_style: Style for the title
        toc_lvl: Register title in TOC at this level
        only_cited: Only show cited entries (vs all registered)
        format: Override BibConfig format
    """
    from .export import _render
    from .write import st_write
    from .container import st_block
    from .space import st_space
    from .styles import StxStyles

    cfg = _bib_config
    fmt = format or cfg.format

    entries = _bib_registry.get_cited_entries() if only_cited else _bib_registry.get_all_entries()
    if not entries:
        return

    # Sort
    entries = _sort_entries(entries, cfg.sort_by)

    # Title
    ts = title_style or (StxStyles.big + StxStyles.bold)
    if title:
        st_write(ts, title, toc_lvl=toc_lvl)
        st_space("v", 2)

    # Entries
    with st_block(style):
        for i, entry in enumerate(entries):
            formatted = format_entry(entry, fmt, i + 1)
            anchor_id = f"bib-{entry.key}"
            _render(
                f'<p id="{anchor_id}" style="margin-bottom:10px;text-indent:-2em;'
                f'padding-left:2em;line-height:1.6;">{formatted}</p>'
            )


def _sort_entries(entries: List[BibEntry], sort_by: str) -> List[BibEntry]:
    """Sort bibliography entries."""
    if sort_by == "author":
        return sorted(entries, key=lambda e: (e.first_author_last.lower(), e.year))
    elif sort_by == "year":
        return sorted(entries, key=lambda e: (e.year, e.first_author_last.lower()))
    elif sort_by == "key":
        return sorted(entries, key=lambda e: e.key.lower())
    # "citation_order" = keep as-is
    return entries


# ===================================================================
# FORMATTERS
# ===================================================================

def format_entry(entry: BibEntry, fmt: BibFormat, number: int = 0) -> str:
    """Format a BibEntry in the specified style."""
    formatters = {
        BibFormat.APA: _format_apa,
        BibFormat.MLA: _format_mla,
        BibFormat.IEEE: _format_ieee,
        BibFormat.CHICAGO: _format_chicago,
        BibFormat.HARVARD: _format_harvard,
    }
    formatter = formatters.get(fmt, _format_apa)
    if fmt == BibFormat.IEEE:
        return formatter(entry, number)
    return formatter(entry)


def _format_apa(entry: BibEntry) -> str:
    """APA 7th edition: Author, A. A., & Author, B. B. (Year). Title. Journal, Vol(No), Pages. DOI"""
    parts = []

    if entry.authors:
        auth = ", ".join(entry.authors[:-1])
        if len(entry.authors) > 1:
            auth += f", & {entry.authors[-1]}"
        else:
            auth = entry.authors[0]
        parts.append(auth)

    if entry.year:
        parts.append(f"({entry.year}).")
    else:
        parts[-1] += "." if parts else ""

    if entry.title:
        if entry.entry_type in ("article", "inproceedings", "conference"):
            parts.append(f"{entry.title}.")
        else:
            parts.append(f"<i>{entry.title}</i>.")

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

    if entry.publisher and entry.entry_type in ("book", "incollection"):
        parts.append(f"{entry.publisher}.")

    if entry.doi:
        parts.append(f'<a href="https://doi.org/{entry.doi}" style="color:#6090d0;">https://doi.org/{entry.doi}</a>')
    elif entry.url:
        parts.append(f'<a href="{entry.url}" style="color:#6090d0;">{entry.url}</a>')

    return " ".join(parts)


def _format_mla(entry: BibEntry) -> str:
    """MLA 9th edition."""
    parts = []

    if entry.authors:
        parts.append(f"{entry.authors[0]}.")

    if entry.title:
        if entry.entry_type in ("article", "inproceedings"):
            parts.append(f'&ldquo;{entry.title}.&rdquo;')
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


def _format_ieee(entry: BibEntry, number: int = 0) -> str:
    """IEEE style: [N] A. Author, "Title," Journal, vol. X, pp. Y, Year."""
    parts = [f"[{number}]"] if number else []

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

    if entry.title:
        parts.append(f'&ldquo;{entry.title},&rdquo;')

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

    if entry.year:
        parts.append(f"{entry.year}.")

    return " ".join(parts)


def _format_chicago(entry: BibEntry) -> str:
    """Chicago author-date style."""
    parts = []

    if entry.authors:
        parts.append(f"{entry.authors[0]}.")

    if entry.year:
        parts.append(f"{entry.year}.")

    if entry.title:
        parts.append(f'&ldquo;{entry.title}.&rdquo;')

    if entry.journal:
        venue = f"<i>{entry.journal}</i>"
        if entry.volume:
            venue += f" {entry.volume}"
            if entry.number:
                venue += f", no. {entry.number}"
        if entry.pages:
            venue += f": {entry.pages}"
        parts.append(venue + ".")

    return " ".join(parts)


def _format_harvard(entry: BibEntry) -> str:
    """Harvard referencing style."""
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


# ===================================================================
# EXPORT: BibTeX output
# ===================================================================

def export_bibtex(*, only_cited: bool = True) -> str:
    """Generate BibTeX output from the registry.

    Returns a string suitable for saving as a .bib file.
    """
    entries = (
        _bib_registry.get_cited_entries() if only_cited
        else _bib_registry.get_all_entries()
    )

    lines = []
    for entry in entries:
        lines.append(f"@{entry.entry_type}{{{entry.key},")

        field_pairs = [
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
            ("isbn", entry.isbn),
            ("issn", entry.issn),
            ("edition", entry.edition),
            ("editor", entry.editor),
            ("institution", entry.institution),
            ("school", entry.school),
            ("address", entry.address),
            ("month", entry.month),
            ("language", entry.language),
            ("keywords", entry.keywords),
        ]
        # Add extra fields
        field_pairs.extend(entry.extra.items())

        for name, value in field_pairs:
            if value:
                lines.append(f"  {name} = {{{value}}},")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)


# ===================================================================
# BibRefs: IDE-completable proxy for cite()
# ===================================================================

class BibRefs:
    """Proxy object that maps attribute access to cite() calls.

    Usage in blocks::

        from streamtex.bib import st_refs

        st_write(s.big,
            "The Transformer architecture ", st_refs.vaswani2017attention,
            " revolutionized NLP."
        )

    This is equivalent to ``cite("vaswani2017attention")``.

    For full IDE autocompletion, generate a project-specific file::

        uv run python -m streamtex generate-stubs static/refs.bib -o custom/bib_refs.py

    Then import from there::

        from custom.bib_refs import st_refs  # IDE completes all keys!

    For multi-key citations, use cite() directly::

        cite("lecun2015deep", "goodfellow2016deep")  # (LeCun; Goodfellow)
    """

    def __getattr__(self, key: str) -> str:
        if key.startswith("_"):
            raise AttributeError(f"BibRefs has no attribute '{key}'")
        return cite(key)

    def __repr__(self) -> str:
        keys = _bib_registry.list_keys()
        return f"BibRefs({len(keys)} entries: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''})"


# Global singleton — import and use directly (dynamic, no IDE completion)
st_refs = BibRefs()


# ===================================================================
# Code generation for IDE autocompletion
# ===================================================================

def generate_bib_stubs(*source_paths: str, output_path: str = "") -> str:
    """Generate a Python module with a typed BibRefs class for IDE autocompletion.

    Reads one or more bibliography source files (.bib, .json, .ris, .csl-json),
    parses them, and generates a ``.py`` file with ``@property`` definitions
    for every key.  Each property has a docstring (title, authors, year) and
    calls ``cite(key)`` at runtime.

    The generated class includes ``__getattr__`` as a fallback so that keys
    added to the .bib after generation still work (without completion).

    Args:
        *source_paths: Paths to bibliography files.
        output_path: Where to write the .py file. If empty, returns the
            content as a string without writing.

    Returns:
        The generated module content as a string.

    CLI usage::

        uv run python -m streamtex generate-stubs refs.bib -o custom/bib_refs.py
    """
    all_entries: List[BibEntry] = []
    for path in source_paths:
        try:
            all_entries.extend(load_bib(path))
        except Exception as e:
            logger.warning(f"generate_bib_stubs: skipping {path}: {e}")

    # Sort for stable output
    all_entries.sort(key=lambda e: e.key)

    lines = [
        '"""Auto-generated BibRefs for IDE autocompletion.',
        '',
        'Generated by:',
        '    uv run python -m streamtex generate-stubs <files> -o <output.py>',
        '',
        'Do not edit manually — regenerate when bibliography sources change.',
        '"""',
        '',
        'from streamtex.bib import cite',
        '',
        '',
        'class _ProjectBibRefs:',
        '    """Bibliography references with IDE autocompletion.',
        '',
        '    Each property calls cite(key) and returns an HTML string',
        '    for embedding in st_write().',
        '',
        '    Unknown keys fall back to cite() dynamically (no completion).',
        '    """',
        '',
    ]

    if not all_entries:
        lines.append('    pass')
    else:
        for entry in all_entries:
            # Escape quotes in docstring
            title = (entry.title or entry.key).replace('"', '\\"')
            authors_short = entry.authors_short if entry.authors else "Unknown"
            doc = f"{title} — {authors_short}"
            if entry.year:
                doc += f" ({entry.year})"

            lines.append('    @property')
            lines.append(f'    def {entry.key}(self) -> str:')
            lines.append(f'        """{doc}"""')
            lines.append(f'        return cite("{entry.key}")')
            lines.append('')

    # __getattr__ fallback for keys not yet in the generated file
    lines.append('    def __getattr__(self, key: str) -> str:')
    lines.append('        if key.startswith("_"):')
    lines.append('            raise AttributeError(f"_ProjectBibRefs has no attribute \'{key}\'")')
    lines.append('        return cite(key)')
    lines.append('')
    lines.append('')
    lines.append('st_refs = _ProjectBibRefs()')
    lines.append('')

    content = "\n".join(lines)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Generated {output_path} ({len(all_entries)} entries)")

    return content
