"""Deep links into a paginated book — open a deck at a given page or marker.

Two URL parameters are honoured by ``st_book(paginate=True)`` on the first
run of a session (and by the static HTML export, client-side):

- ``?marker=<key-or-slug>`` — the stable ``key=`` given to ``st_marker()``,
  or the slug of the marker label (``"Electricity"`` → ``electricity``);
- ``?page=<n>`` — a 1-based page number.

``?marker=`` wins over ``?page=`` when both are present. Invalid values are
ignored (the book opens on page 1); no other parameter is read or modified,
so a project's own ``?lang=`` travels untouched.

:func:`page_url` builds such a link without computing page numbers.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .toc import TOCRegistry

#: Query-string parameter names.
PAGE_PARAM = "page"
MARKER_PARAM = "marker"

_MARKER_PREFIX = "stx-marker-"


def _first(value: Any) -> Optional[str]:
    """Normalise a query value (str, list of str, None) to a stripped str."""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def find_marker(markers: Sequence[Mapping[str, Any]], ref: str) -> Optional[Mapping[str, Any]]:
    """Return the first marker entry matching *ref*, or ``None``.

    Match order: explicit ``key`` (language-independent, set by
    ``st_marker(key=...)``), exact anchor, then the slug of the label —
    either as the ``stx-marker-<slug>-<idx>`` anchor prefix or as the slug
    of the label itself (auto markers bridged from TOC headings).
    """
    ref = (ref or "").strip()
    if not ref:
        return None
    for m in markers:
        if m.get("key") and m["key"] == ref:
            return m
    for m in markers:
        if m.get("anchor") == ref:
            return m
    slug = TOCRegistry.get_key_anchor(ref)
    if not slug:
        return None
    for m in markers:
        anchor = m.get("anchor") or ""
        if anchor.startswith(f"{_MARKER_PREFIX}{slug}-"):
            return m
        if TOCRegistry.get_key_anchor(m.get("label") or "") == slug:
            return m
    return None


def resolve_initial_page(params: Mapping[str, Any],
                         markers: Sequence[Mapping[str, Any]],
                         total: int) -> tuple[int, Optional[int]]:
    """Resolve ``(page_idx, marker_idx)`` from URL *params*.

    ``page_idx`` is 0-based and bounded to ``[0, total)``; ``marker_idx`` is
    the global marker index to scroll to inside the page, or ``None``.
    Never raises: anything unusable resolves to ``(0, None)``.
    """
    if total <= 0:
        return 0, None
    ref = _first(params.get(MARKER_PARAM))
    if ref:
        m = find_marker(markers, ref)
        if m is not None:
            page = int(m.get("page_idx", 0) or 0)
            return max(0, min(page, total - 1)), int(m.get("index", 0))
    raw = _first(params.get(PAGE_PARAM))
    if raw:
        try:
            n = int(raw)
        except ValueError:
            return 0, None
        if 1 <= n <= total:
            return n - 1, None
    return 0, None


def page_url(base: str, *, marker: Optional[str] = None,
             page: Optional[int] = None, **params: Any) -> str:
    """Build a deep link into a paginated book.

    Merges ``marker`` / ``page`` (and any extra keyword, e.g. ``lang="fr"``)
    into the query string of *base*, keeping the parameters *base* already
    carries — a hub can wrap a link produced by its own ``with_lang()``.
    ``page`` is 1-based. The fragment of *base* is preserved.

    >>> page_url("https://x/waves?lang=en", marker="electricity")
    'https://x/waves?lang=en&marker=electricity'
    """
    scheme, netloc, path, query, fragment = urlsplit(base)
    items = [(k, v) for k, v in parse_qsl(query, keep_blank_values=True)
             if k not in (MARKER_PARAM, PAGE_PARAM) and k not in params]
    for k, v in params.items():
        if v is not None:
            items.append((k, str(v)))
    if marker:
        items.append((MARKER_PARAM, str(marker)))
    elif page is not None:
        if int(page) < 1:
            raise ValueError("page_url: page is 1-based (>= 1)")
        items.append((PAGE_PARAM, str(int(page))))
    return urlunsplit((scheme, netloc, path, urlencode(items), fragment))
