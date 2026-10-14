"""Pages that follow the composition tree — ``st_book(paginate_by=…)`` (#121).

A module given as a tree (list blocks that ``st_include`` other blocks) can be
paginated finer than one page per entry. Two walks of an entry exist:

- the **dry walk**, during the page-cache build: every inclusion is recorded
  with its *path* inside the entry (child ordinals, ``(1, 0)`` = first child
  of the second child) and its depth; marker / TOC registrations and search
  text are recorded in walk order. When the entry ends, the page-starting
  inclusions are computed and every registration gets its page;
- the **gate**, when one page is shown: the entry runs, the page-starting
  inclusion of the page renders, the other page-starting inclusions are not
  executed, and content of the other pages is executed but neither drawn nor
  registered (it comes from the cache, through the pre-seed and post-seed).

Vocabulary: a **leaf** is an inclusion that includes no other block (an atom
or a composite). The entry has depth 0; an inclusion made while depth ``d``
is built has depth ``d + 1``.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar

logger = logging.getLogger(__name__)

ENTRY = "entry"
LEAF = "leaf"


def normalize_paginate_by(value) -> str | int:
    """``"entry"``, ``"leaf"`` or a depth ``N >= 1``; ``ValueError`` otherwise.

    ``0`` is a synonym of ``"entry"``; ``"depth:N"`` of ``N``.
    """
    v = value
    if isinstance(v, str) and v.startswith("depth:"):
        try:
            v = int(v[len("depth:"):])
        except ValueError:
            v = value
    if v == ENTRY or (isinstance(v, int) and not isinstance(v, bool) and v == 0):
        return ENTRY
    if v == LEAF:
        return LEAF
    if isinstance(v, int) and not isinstance(v, bool) and v >= 1:
        return v
    raise ValueError("paginate_by must be 'entry', a positive int, 'depth:N' or 'leaf' "
                     f"— got {value!r}")


#: The paginate_by of the book being rendered (set by st_book).
_PAGINATE_BY: ContextVar[str | int] = ContextVar("stx_paginate_by", default=ENTRY)


def paginate_by() -> str | int:
    return _PAGINATE_BY.get()


def set_paginate_by(value) -> None:
    _PAGINATE_BY.set(normalize_paginate_by(value))


def page_starts(nodes: dict[tuple, dict], mode) -> list[tuple]:
    """The page-starting inclusions of one entry, in walk order.

    *nodes*: ``path -> {"depth", "page", "children"}`` (the root ``()`` is
    the entry). ``page=False`` keeps an inclusion and its subtree on the
    enclosing page; ``page=True`` starts a page with the whole subtree.
    """
    starts: list[tuple] = []
    children: dict[tuple, list[tuple]] = {}
    for p in nodes:
        if p:
            children.setdefault(p[:-1], []).append(p)
    for lst in children.values():
        lst.sort()

    def visit(path):
        for c in children.get(path, []):
            node = nodes[c]
            override = node.get("page")
            leaf = node.get("children", 0) == 0
            if override is False:
                continue
            if override is True:
                starts.append(c)
                continue
            if mode == LEAF:
                if leaf:
                    starts.append(c)
                else:
                    visit(c)
            else:
                d = node["depth"]
                if d == mode or (d < mode and leaf):
                    starts.append(c)
                elif d < mode:
                    visit(c)

    visit(())
    return starts


class _Walk:
    """Path bookkeeping shared by the dry walk and the gate."""

    def __init__(self):
        self._counters: list[int] = []
        self._paths: list[tuple] = []

    def _next_path(self) -> tuple:
        if not self._paths:
            return ()
        parent = self._paths[-1]
        n = self._counters[-1]
        self._counters[-1] += 1
        return parent + (n,)

    def _push(self, path: tuple) -> None:
        self._paths.append(path)
        self._counters.append(0)

    def _pop(self) -> int:
        self._paths.pop()
        return self._counters.pop()


class DryWalk(_Walk):
    """Records one entry during the cache build."""

    def __init__(self, mode, collector=None, buffer_pos=None):
        super().__init__()
        self.mode = mode
        self.nodes: dict[tuple, dict] = {}
        self.events: list[tuple] = []
        self.collector = collector
        self._seg = 0
        self._buffer_pos = buffer_pos
        self.exit_pos: dict[tuple, int | None] = {}   # export position after each inclusion (#106)

    def _segment(self) -> None:
        if self.collector is not None:
            self._seg += 1
            seg = -self._seg            # negative: never a page index
            self.collector.set_block(seg)
            self.events.append(("s", seg))

    # --- st_include hooks -------------------------------------------------
    def enter(self, block, page) -> tuple:
        path = self._next_path()
        self.nodes[path] = {"depth": len(path), "page": page, "children": 0,
                            "name": getattr(block, "__name__", repr(block))}
        return path

    def skip(self, path) -> bool:
        return False

    def begin(self, path) -> None:
        self.events.append(("enter", path))
        self._push(path)
        self._segment()

    def end(self, path) -> None:
        self.nodes[path]["children"] = self._pop()
        self.events.append(("exit", path))
        if self._buffer_pos is not None:
            self.exit_pos[path] = self._buffer_pos()
        self._segment()

    # --- registrations ----------------------------------------------------
    def note(self, kind: str, idx: int) -> None:
        self.events.append((kind, idx))

    def muted(self) -> bool:
        return False

    def suppress_break(self) -> bool:
        return False

    # --- result -----------------------------------------------------------
    def assign(self) -> tuple[list[tuple], dict[tuple[str, int], int]]:
        """``(starts, {(kind, idx): local page})`` for the entry just walked."""
        starts = page_starts(self.nodes, self.mode)
        index = {p: i for i, p in enumerate(starts)}
        n = len(starts)
        seen, inside, inside_path = 0, None, None
        out: dict[tuple[str, int], int] = {}
        for ev in self.events:
            kind, val = ev
            if kind == "enter":
                if inside is None and val in index:
                    inside, inside_path = index[val], val
                    seen = inside + 1
            elif kind == "exit":
                if val == inside_path:
                    inside, inside_path = None, None
            else:
                if n == 0:
                    local = 0
                elif inside is not None:
                    local = inside
                else:
                    local = min(seen, n - 1)
                out[(kind, val)] = local
        return starts, out


class Gate(_Walk):
    """Renders one page of an entry (live paginated view)."""

    def __init__(self, target: tuple, starts: list[tuple]):
        super().__init__()
        self.target = tuple(target)
        self.starts = [tuple(s) for s in starts]
        self._start_set = set(self.starts)
        self.t = self.starts.index(self.target)
        self.n = len(self.starts)
        self.seen = 0
        self.inside = 0              # depth inside the target's subtree
        self.met = False

    def enter(self, block, page) -> tuple:
        return self._next_path()

    def skip(self, path) -> bool:
        if self.inside or path == self.target or path not in self._start_set:
            return False
        self.seen += 1               # another page's page-starting inclusion
        return True

    def begin(self, path) -> None:
        self._push(path)
        if self.inside:
            self.inside += 1
        elif path == self.target:
            self.inside = 1
            self.seen = self.t + 1
            self.met = True

    def end(self, path) -> None:
        self._pop()
        if self.inside:
            self.inside -= 1

    def note(self, kind: str, idx: int) -> None:
        pass

    def visible(self) -> bool:
        return bool(self.inside) or self.seen == self.t or (
            self.t == self.n - 1 and self.seen == self.n)

    def muted(self) -> bool:
        return not self.visible()

    def suppress_break(self) -> bool:
        """A break in the page's leading region draws no rule nor spacer (#121)."""
        return not self.inside and self.seen == self.t


#: The walk of the entry being rendered, if any.
_CURRENT: ContextVar[_Walk | None] = ContextVar("stx_page_walk_current", default=None)


def current() -> _Walk | None:
    return _CURRENT.get()


def activate(walk: _Walk | None):
    return _CURRENT.set(walk)


def deactivate(token) -> None:
    _CURRENT.reset(token)


def muted() -> bool:
    """True while content of another page runs (nothing drawn, nothing registered)."""
    w = _CURRENT.get()
    return w is not None and w.muted()


def suppress_break() -> bool:
    w = _CURRENT.get()
    return w is not None and w.suppress_break()


def note(kind: str, idx: int) -> None:
    w = _CURRENT.get()
    if w is not None:
        w.note(kind, idx)
