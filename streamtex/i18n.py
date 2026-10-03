"""Multilingual documents: the language lives in the address (L1).

The design of the maintainer's two multilingual projects (sumvadis
``postair_lang.py``, D2 of 2026-08-29; all-trainings ``shared/i18n.py``),
documented in the advanced manual since 0.7.26 and now provided here.

- A translatable text is a *leaf* ``{"en": …, "fr": …}`` written in the
  block; :func:`T` picks the language, :func:`TF` a sequence of
  ``st_write`` fragments.
- :func:`current_lang` reads, in order: ``$STX_LANG`` (the static export,
  one pass per language), the address parameter ``?lang=fr`` (what was
  opened is what is projected), the default. No widget, no session state.
- ``st_book(..., lang="auto")`` hands the language to every block
  (``build(lang=…)``) — the same as ``block_kwargs={"lang": current_lang()}``.

These names are NOT exported by ``from streamtex import *``: projects that
already define their own ``T`` / ``current_lang`` keep them. Import them
explicitly: ``from streamtex.i18n import T, TF, current_lang, with_lang``.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ENV_KEY = "STX_LANG"
QUERY_KEY = "lang"

_languages: tuple[str, ...] = ("en", "fr")
_default: str = "en"


def set_languages(languages: Sequence[str], default: str | None = None) -> None:
    """The languages a document can be projected in, and its default.

    A language outside this list in the address is ignored (a wrong suffix
    never breaks a projection); in ``$STX_LANG`` it raises (an export in an
    unknown language is a command error).
    """
    global _languages, _default
    langs = tuple(languages)
    if not langs:
        raise ValueError("set_languages() needs at least one language")
    default = default or langs[0]
    if default not in langs:
        raise ValueError(f"default language {default!r} is not in {langs}")
    _languages, _default = langs, default


def languages() -> tuple[str, ...]:
    return _languages


def default_lang() -> str:
    return _default


def _query_lang() -> str | None:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx(suppress_warning=True) is None:
            return None
        import streamlit as st

        value = st.query_params.get(QUERY_KEY)
    except Exception:  # noqa: BLE001 — no script context (export, checks)
        return None
    return value if value in _languages else None


def current_lang(default: str | None = None) -> str:
    """The language to project now: ``$STX_LANG`` > ``?lang=`` > default."""
    lang = os.environ.get(ENV_KEY) or _query_lang() or default or _default
    if lang not in _languages:
        raise ValueError(f"language {lang!r} is not in {_languages} — check ${ENV_KEY}")
    return lang


def with_lang(url: str, lang: str) -> str:
    """A link to a document in *lang*: the language travels in the address.

    An existing ``lang=`` is replaced, the other parameters and the
    ``#fragment`` are kept.
    """
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != QUERY_KEY]
    query.append((QUERY_KEY, lang))
    return urlunsplit(parts._replace(query=urlencode(query)))


def T(entry, lang: str | None = None, *, strict: bool = False):
    """A leaf ``{"en": …, "fr": …}`` → its text in *lang* (default: :func:`current_lang`).

    A missing language falls back on the default language, then on the
    first value: a missing translation never leaves a hole on screen. An
    EMPTY string is a value (a suffix the language does not need), not a
    missing one. A bare string is returned as is, unless *strict* (then it
    raises: a text that was never turned into a leaf).
    """
    if isinstance(entry, str):
        if strict:
            raise TypeError(f"bare string passed to T() — make it a leaf {{'en': …}}: {entry[:60]!r}")
        return entry
    if not isinstance(entry, dict) or not entry:
        raise TypeError(f"invalid leaf (a non-empty dict of languages expected): {entry!r}")
    lang = lang or current_lang()
    value = entry.get(lang)
    if value is None:
        value = entry.get(_default)
    if value is None:
        value = next(iter(entry.values()))
    return value


def TF(entry, lang: str | None = None, *, strict: bool = False) -> tuple:
    """A leaf of ``st_write`` FRAGMENTS → the tuple to unpack in ``st_write``.

    ``{"en": ("Your turn — ", (KW, "join")), "fr": (…)}``; a plain string
    value is one fragment.
    """
    value = T(entry, lang, strict=strict)
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        return tuple(value)
    raise TypeError(f"invalid fragments: {value!r}")
