"""Paginated HTML export — one file per page of the page map (#106).

The page-cache build marks where each page of the module's page map starts
(``<!--stx-page:N-->``, #121 decides the pages). This module cuts the
exported document there, names the files, and builds the entry file that
sends a link (``?marker=``, ``?slide=``, ``?page=``, ``#anchor``) to the
right page.

File names never carry a number (author decision ``f1``): the name of the
page's block; when the same block makes several pages, a copy is qualified
by its section — the list block that includes it (pages following the
tree) or the level-1 heading before it (one page per entry) — and, within
one section, by the blocks before it.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter

from .export import _LIST_INSIDE_JS, _PAGE_SENTINEL_RE

_PAGE_OPEN = '<div class="streamtex-page">\n'
_PAGE_CLOSE = "\n</div>\n" + _LIST_INSIDE_JS


def _short(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", (name or "page").rsplit(".", 1)[-1]).strip("-") or "page"


def _ascii_slug(text: str) -> str:
    """A file-name slug: ASCII letters, digits and dashes only (``Séance 3 — x`` → ``seance-3-x``)."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def _section_of(j: int, page: dict, toc: list[dict]) -> str:
    if page.get("start"):
        return _short(page.get("parent", ""))
    label = ""
    for t in toc:
        if t.get("level") == 1 and t.get("page_idx", 0) <= j:
            label = t.get("_reg_label") or t.get("title", "")
    return _ascii_slug(label) if label else ""


def page_file_names(pages: list[dict], toc: list[dict]) -> list[str]:
    """One file name per page, ``<name>.html``, unique, without any number."""
    blocks = [_short(p.get("block", "")) for p in pages]
    count = Counter(blocks)
    used: set[str] = set()
    names: list[str] = []
    for j, b in enumerate(blocks):
        name = b
        if count[b] > 1:
            # a copy: qualified by its section, then by the blocks before it
            section = _section_of(j, pages[j], toc)
            head = [section] if section and section != b else []
            chain: list[str] = []
            name = "--".join(head + [b])
            k = j - 1
            while name in used and k >= 0:
                chain.insert(0, blocks[k])
                k -= 1
                name = "--".join(head + chain + [b])
        k = j + 1
        while name in used:               # identical history: what follows
            name = f"{name}--before-{blocks[k] if k < len(blocks) else 'end'}"
            k += 1
        used.add(name)
        names.append(name)
    return [f"{n}.html" for n in names]


#: A break at the head of a page file: bottom spacing, before-spacer, rule,
#: spacer — dropped, as in the live paginated view (#121 s1).
_EL = r'<div class="stx-el"[^>]*>'
_HEAD_BREAK_RE = re.compile(
    r'\A\s*(?:' + _EL + r'<div style="(?:height|margin-top): [^"]*"></div></div>\s*)?'
    r'(?:' + _EL + r'<div class="stx-slide-break-spacer-before"[^>]*></div></div>\s*)?'
    r'(?:' + _EL + r'<hr class="stx-slide-break-rule"[^>]*></div>\s*)'
    r'(?:' + _EL + r'<div class="stx-slide-break-spacer"[^>]*></div></div>\s*)?'
    r'|\A\s*(?:' + _EL + r'<div class="stx-slide-break-spacer"[^>]*></div></div>\s*)')


def strip_head_break(body: str) -> str:
    """Drop the break at the head of a page (only if one is there)."""
    return _HEAD_BREAK_RE.sub("", body, count=1)


def split_pages(html: str) -> tuple[str, list[tuple[int, str]], str] | None:
    """``(head, [(first page, body)], tail)`` of a document with page sentinels.

    ``None`` when the document has no sentinel (nothing to cut).
    """
    i = html.find(_PAGE_OPEN)
    j = html.rfind(_PAGE_CLOSE)
    if i < 0 or j < 0 or not _PAGE_SENTINEL_RE.search(html):
        return None
    head, body, tail = html[:i + len(_PAGE_OPEN)], html[i + len(_PAGE_OPEN):j], html[j:]
    parts = _PAGE_SENTINEL_RE.split(body)
    lead, rest = parts[0], parts[1:]
    segments: list[tuple[int, str]] = []
    for k in range(0, len(rest), 2):
        n, content = int(rest[k]), rest[k + 1]
        segments.append((n, content))
    if segments and lead.strip():
        segments[0] = (segments[0][0], lead + segments[0][1])
    return head, segments, tail


def build_page_documents(html: str, pages: list[dict], toc: list[dict]):
    """The page files of a document: ``(files_by_page, [(file, document, pages in file)])``.

    A page the export could not cut (its start was inside an open container)
    stays in the file of the previous page.
    """
    split = split_pages(html)
    if split is None:
        return None
    head, segments, tail = split
    names = page_file_names(pages, toc)
    total = len(pages)
    firsts = [n for n, _ in segments]
    files_by_page: list[str] = []
    seg = 0
    for p in range(total):
        while seg + 1 < len(firsts) and firsts[seg + 1] <= p:
            seg += 1
        files_by_page.append(names[firsts[seg]])
    docs = []
    for k, (n, content) in enumerate(segments):
        last = firsts[k + 1] if k + 1 < len(firsts) else total
        body = strip_head_break(content) if k else content
        docs.append((names[n], head + body + tail, list(range(n, last))))
    return files_by_page, docs


def to_subfolder(html: str) -> str:
    """Asset paths of a file one folder below the continuous file: ``data/`` → ``../data/``."""
    html = re.sub(r'((?:src|href|poster)=")data/', r"\1../data/", html)
    return re.sub(r'url\((["\']?)data/', r"url(\1../data/", html)


#: A link of a page to a marker, a slide or a page of the document (``?marker=``, ``?slide=``, ``?page=``).
_DEEP_HREF_RE = re.compile(r'href="\?([^"#]*\b(?:marker|slide|page)=[^"]*)"')


def to_entry_links(html: str, entry: str) -> str:
    """A page's links ``?marker=``, ``?slide=``, ``?page=`` → *entry* (``../deck.html``).

    The entry file (or the continuous file) knows every page and sends the
    link to the right one: the address the export guarantees, whatever a
    page file's own script does (board ``note1``, l1).
    """
    return _DEEP_HREF_RE.sub(lambda m: f'href="{entry}?{m.group(1)}"', html)


_ENTRY_TEMPLATE = """<!DOCTYPE html>
<html lang="__LANG__"><head><meta charset="UTF-8"><title>__TITLE__</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body><noscript><a href="__FIRST__">__TITLE__</a></noscript>
<script>
(function () {
  var NAV = __NAV__;
  function slugOf(t) {
    var s = String(t || '').toLowerCase()
      .replace(/[.'"!?@#$%^&*()+=\\[\\]{}|\\\\\\/<>,;:~`]/g, '-')
      .replace(/[-\\s]+/g, '-').replace(/^-+|-+$/g, '');
    return s || 'section';
  }
  function go(page, anchor) {
    var f = NAV.files[page] || NAV.files[0];
    location.replace(NAV.prefix + f + (anchor ? '#' + anchor : '') );
  }
  function byRef(ref) {
    var i, m = NAV.markers;
    for (i = 0; i < m.length; i++) if (m[i].key && m[i].key === ref) return m[i];
    for (i = 0; i < m.length; i++) if (m[i].anchor === ref || m[i].toc_anchor === ref) return m[i];
    var s = slugOf(ref);
    for (i = 0; i < m.length; i++) if (slugOf(m[i].label) === s) return m[i];
    for (i = 0; i < NAV.toc.length; i++) if (NAV.toc[i].anchor === ref) return NAV.toc[i];
    return null;
  }
  var q = new URLSearchParams(location.search), m = null, n;
  if (q.get('marker')) m = byRef(q.get('marker').trim());
  if (!m && /^\\d+$/.test(q.get('slide') || '')) {
    n = parseInt(q.get('slide'), 10);
    var seen = 0;
    for (var i = 0; i < NAV.markers.length && !m; i++) {
      if (NAV.markers[i].stop !== false && ++seen === n) m = NAV.markers[i];
    }
  }
  if (!m && /^\\d+$/.test(q.get('page') || '')) {
    n = parseInt(q.get('page'), 10);
    if (n >= 1 && n <= NAV.files.length) { go(n - 1, ''); return; }
  }
  if (!m && location.hash) m = byRef(decodeURIComponent(location.hash.slice(1)));
  if (m) go(m.page || 0, m.anchor); else go(0, '');
})();
</script></body></html>
"""


def nav_markers(markers: list[dict]) -> list[dict]:
    keep = ("anchor", "toc_anchor", "key", "label", "stop")
    return [{**{k: m[k] for k in keep if k in m}, "page": m.get("page_idx", 0)} for m in markers]


def build_entry_html(files_by_page: list[str], prefix: str, markers: list[dict],
                     toc: list[dict], title: str, lang: str = "en") -> str:
    """The entry file of a paginated export: it sends any link to its page."""
    nav = {"files": files_by_page, "prefix": prefix, "markers": nav_markers(markers),
           "toc": [{"anchor": t.get("key_anchor"), "page": t.get("page_idx", 0)}
                   for t in toc if t.get("key_anchor")]}
    first = prefix + (files_by_page[0] if files_by_page else "")
    return (_ENTRY_TEMPLATE.replace("__NAV__", json.dumps(nav, ensure_ascii=False))
            .replace("__FIRST__", first).replace("__TITLE__", title).replace("__LANG__", lang))
