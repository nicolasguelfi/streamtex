"""Glossary for StreamTeX: define a term once, get its definition on hover (#12).

Provides:
- GlossaryRegistry singleton, separate from the bibliography: a term never
  takes a citation number and never appears in ``st_bibliography()``
- Loading from YAML or JSON (``LLM: Large Language Model``) and from ``.bib``
  files (``@glossary{LLM, title = {...}, note = {...}}``)
- Inline term: ``gloss("LLM")`` — the definition shows on hover and focus,
  in pure CSS (``default.css``), so it survives the HTML export; the print CSS
  hides it and underlines the term with dots
- The list of terms: ``st_glossary()``

Usage:
    st_book([...], glossary_sources=["glossary.yaml"])
    st_write(s.big, "How ", gloss("LLM"), " models generate text")
    st_write(s.big, gloss("LLM", text="large language models"))
    st_glossary(title="Glossary", only_used=True)

A term is a ``BibEntry`` with ``entry_type="glossary"``: ``title`` is the
definition shown on hover, ``note`` the longer explanation, and
``extra["abbreviation"]`` the form shown in the text (default: the key).
"""

import json
import logging
import os
from dataclasses import dataclass
from html import escape
from typing import Any, Dict, List, Optional

from .bib import BibEntry, _fields_to_entry, _get_extension, load_bib, register_bib_parser

logger = logging.getLogger(__name__)

GLOSSARY_TYPE = "glossary"


@dataclass
class GlossaryConfig:
    """Glossary behaviour.

    Attributes:
        strict: An unknown key raises ``KeyError`` instead of a warning and ``[key?]``.
    """
    strict: bool = False


_glossary_config = GlossaryConfig()


def set_glossary_config(config: GlossaryConfig) -> None:
    """Set the global glossary configuration."""
    global _glossary_config
    _glossary_config = config


def get_glossary_config() -> GlossaryConfig:
    """Get the global glossary configuration."""
    return _glossary_config


class GlossaryRegistry:
    """Singleton registry of glossary terms and the ones the text used."""

    def __init__(self):
        self._entries: Dict[str, BibEntry] = {}
        self._used: List[str] = []

    def register(self, entry: BibEntry) -> None:
        """Register a term (overwrites if key exists)."""
        self._entries[entry.key] = entry

    def register_many(self, entries: List[BibEntry]) -> None:
        """Register several terms."""
        for entry in entries:
            self.register(entry)

    def get(self, key: str) -> Optional[BibEntry]:
        """Retrieve a term by key (None if not found)."""
        return self._entries.get(key)

    def use(self, key: str) -> None:
        """Mark *key* as used in the text."""
        if key in self._entries and key not in self._used:
            self._used.append(key)

    def get_used_entries(self) -> List[BibEntry]:
        """Return the used terms, in order of first use."""
        return [self._entries[k] for k in self._used if k in self._entries]

    def get_all_entries(self) -> List[BibEntry]:
        """Return all registered terms."""
        return [*self._entries.values()]

    def reset(self) -> None:
        """Clear all terms and uses."""
        self._entries.clear()
        self._used.clear()

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        return key in self._entries


_glossary_registry = GlossaryRegistry()


def reset_glossary_registry() -> None:
    """Reset the global glossary registry."""
    _glossary_registry.reset()


def get_glossary_registry() -> GlossaryRegistry:
    """Get the global glossary registry."""
    return _glossary_registry


# ===================================================================
# LOADING
# ===================================================================

def is_glossary(entry: BibEntry) -> bool:
    """True for a glossary term (``entry_type="glossary"``)."""
    return entry.entry_type == GLOSSARY_TYPE


def _parse_glossary_data(data: Any, path: str) -> List[BibEntry]:
    """Terms from parsed YAML/JSON: a mapping ``key: definition | {fields}``, or a list of ``{key, ...}``."""
    if isinstance(data, dict):
        items = [(k, v if isinstance(v, dict) else {"title": v}) for k, v in data.items()]
    elif isinstance(data, list):
        items = [(d["key"], {k: v for k, v in d.items() if k != "key"})
                 for d in data if isinstance(d, dict) and "key" in d]
    elif data is None:
        items = []
    else:
        raise ValueError(f"{path}: expected a mapping or a list of terms, got {type(data).__name__}")
    entries = []
    for key, fields in items:
        fields = {k: "" if v is None else v for k, v in fields.items()}
        entries.append(_fields_to_entry(str(key), str(fields.pop("entry_type", GLOSSARY_TYPE)), fields))
    return entries


def load_glossary_yaml(path: str) -> List[BibEntry]:
    """Parse a YAML glossary file (``LLM: Large Language Model`` or ``LLM: {title: ..., note: ...}``)."""
    try:
        import yaml
    except ImportError as e:                               # pragma: no cover — PyYAML is a dependency
        raise ImportError("A YAML glossary needs PyYAML: uv add pyyaml") from e
    with open(path, encoding="utf-8") as f:
        return _parse_glossary_data(yaml.safe_load(f), path)


register_bib_parser("yaml", load_glossary_yaml)
register_bib_parser("yml", load_glossary_yaml)


def load_glossary(path: str) -> List[BibEntry]:
    """Load the glossary terms of a file: ``.yaml``/``.yml``, ``.json`` or ``.bib``.

    A JSON mapping (``{"LLM": "Large Language Model"}``) is read like YAML;
    a JSON list goes through the bibliography loader. Entries that are not of
    type ``glossary`` (the references of a shared ``.bib``) are left out.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Glossary file not found: {path}")
    if _get_extension(path) == "json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return _parse_glossary_data(data, path)
    return [e for e in load_bib(path) if is_glossary(e)]


# ===================================================================
# INLINE TERM
# ===================================================================

def _shown(entry: BibEntry) -> str:
    return entry.extra.get("abbreviation") or entry.key


def gloss(key: str, text: Optional[str] = None) -> str:
    """Return a glossary term as an HTML fragment for ``st_write()``.

    The term is underlined with dots; its definition shows on hover and on
    keyboard focus, in CSS only, live and in the HTML export.

        st_write(s.big, "How ", gloss("LLM"), " models generate text")

    Args:
        key: The term's key in the glossary sources.
        text: The words shown in the text (default: the term's abbreviation, or its key).

    Returns:
        HTML string. An unknown key gives ``[key?]`` and a warning, or raises
        ``KeyError`` with ``GlossaryConfig(strict=True)``.
    """
    entry = _glossary_registry.get(key)
    if entry is None:
        if _glossary_config.strict:
            raise KeyError(f"gloss: unknown glossary key {key!r} (GlossaryConfig(strict=True)) — "
                           "add it to the glossary sources or fix the key")
        logger.warning(f"gloss: key '{key}' not found")
        return f"[{escape(key)}?]"
    _glossary_registry.use(key)
    tip = f"<b>{escape(entry.title)}</b>" if entry.title else ""
    if entry.note:
        tip += ("<br>" if tip else "") + escape(entry.note)
    return (f'<span class="stx-gloss" tabindex="0">{escape(text or _shown(entry))}'
            f'<span class="stx-gloss-tip" role="tooltip">{tip or escape(_shown(entry))}</span></span>')


# ===================================================================
# LIST OF TERMS
# ===================================================================

def st_glossary(*, style=None, title: str = "Glossary",
                title_style=None, term_style=None, entry_style=None,
                toc_lvl: Optional[str] = None,
                only_used: bool = True) -> None:
    """Render the list of glossary terms, sorted alphabetically.

    Each term reads ``LLM — Large Language Model. Its note.`` and carries the
    anchor ``gloss-<key>``. It is the printed form of the hover definitions.

    Args:
        style: Style for the list container.
        title: Section title (``""``: none).
        title_style: Style for the title.
        term_style: Style for the term (default: bold).
        entry_style: Style for each entry (font size, colour…).
        toc_lvl: Register the title in the TOC at this level.
        only_used: Only the terms used by ``gloss()`` (vs all registered).
    """
    from .container import st_block
    from .export import _render
    from .space import st_space
    from .styles import StxStyles
    from .write import st_write

    entries = _glossary_registry.get_used_entries() if only_used else _glossary_registry.get_all_entries()
    if not entries:
        return
    entries = sorted(entries, key=lambda e: (_shown(e).casefold(), e.key))

    if title:
        st_write(title_style or (StxStyles.big + StxStyles.bold), title, toc_lvl=toc_lvl)
        st_space("v", 2)
    term_css = term_style.css if term_style else "font-weight:bold;"
    entry_css = entry_style.css if entry_style else ""
    with st_block(style):
        for entry in entries:
            text = ". ".join(escape(t) for t in (entry.title, entry.note) if t)
            _render(f'<p id="gloss-{escape(entry.key)}" class="stx-glossary-entry" '
                    f'style="margin-bottom:10px;line-height:1.6;overflow-wrap:anywhere;{entry_css}">'
                    f'<span style="{term_css}">{escape(_shown(entry))}</span>'
                    f'{" — " + text if text else ""}</p>')
