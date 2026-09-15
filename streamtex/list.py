import re
from contextlib import contextmanager
from contextvars import ContextVar

import streamlit as st

from .container import st_block
from .enums import ListType, ListTypes
from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .styles import ListStyle, Style
from .styles import StxStyles as s
from .utils import generate_key

_current_list_level = ContextVar("list_level", default=0)

# ---------------------------------------------------------------------------
# Alignment (0.7.33) — two distinct CSS notions, two distinct parameters.
#
#   text_align  -> `text-align` on the list.  Never touches any width.
#   block_align -> `width: fit-content` + auto margins: places the list BOX,
#                  which makes the list as wide as its content.
#
# Both are carried to the DOM as `data-stx-list-*` attributes on the sentinel
# span; the marker observer forwards every `data-stx-foo` as a `--stx-foo`
# custom property on the list container, and stx_global.css reads those.
#
# The "inside" marker mode — the `list-style-position: inside` semantics that
# keep bullet and text together when the text is centred or right-aligned — is
# NOT carried here (0.7.34).  It follows the EFFECTIVE alignment of each item,
# which is just as often inherited from a container as declared by `text_align`,
# and only the browser can resolve that: the marker observer reads the computed
# `text-align` of every item and stamps `.stx-list-item--inside` on it.  The
# HTML export mirrors the same rule with a few lines of script (see export.py).
# ---------------------------------------------------------------------------
_TEXT_ALIGN_VALUES = ("left", "center", "right", "justify")
_BLOCK_ALIGN_VALUES = ("left", "center", "right")

# `margin-inline: <start> <end>` placing a fit-content list box.
_BLOCK_ALIGN_MARGIN = {"left": "0 auto", "center": "auto", "right": "auto 0"}

# text_align values for which the marker belongs INSIDE the first line.
_INSIDE_ALIGNS = ("center", "right")


def _validate_align(param: str, value: str | None,
                    allowed: tuple[str, ...]) -> str | None:
    """Return *value* unchanged, or raise ``ValueError`` if unknown."""
    if value is None:
        return None
    if value not in allowed:
        expected = ", ".join(repr(v) for v in allowed)
        raise ValueError(
            f"st_list({param}={value!r}): unknown value; "
            f"expected one of {expected} or None"
        )
    return value


def _list_export_css(text_align: str | None, block_align: str | None) -> str:
    """Return the CSS declarations added to the exported ``<ul>``/``<ol>``.

    The export renders real list markup, so the standard properties apply
    directly: ``list-style-position: inside`` is the export twin of the
    flex-box "inside" mode used live.
    """
    parts: list[str] = []
    if text_align:
        parts.append(f"text-align: {text_align};")
        if text_align in _INSIDE_ALIGNS:
            parts.append("list-style-position: inside;")
    if block_align:
        parts.append("width: fit-content;")
        parts.append(f"margin-inline: {_BLOCK_ALIGN_MARGIN[block_align]};")
    return " ".join(parts)


def _build_list_item_payload(item_id: str, bullet_content: str, is_ordered: bool) -> str:
    """Return the per-item bullet CSS + sentinel marker span for a list item.

    The bullet ``content:`` value (which may include ``counter(streamtex-counter,
    decimal) '.'`` for ordered lists) is carried by a tiny per-item
    stylesheet keyed by ``[data-stx-list-item-uid="…"]`` — CSS ``var()``
    cannot reliably carry a ``counter()`` function call across browsers.
    All other rules (flex layout, gap, baseline alignment, marker-cell
    hide, inner content wrapper) live in the global stylesheet under
    ``.stx-list-item``.

    The value is declared on TWO pseudo-elements (0.7.34): the item row, which
    renders the marker in its own column ("outside"), and the item's content
    wrapper, which renders it inline at the start of the first line
    ("inside").  Exactly one of the two is displayed — the global stylesheet
    decides from ``.stx-list-item--inside``, which the marker observer stamps
    from the item's effective ``text-align``.  The wrapper is reached through
    the two shapes Streamlit gives a nested container: a direct
    ``stVerticalBlock`` (≤ 1.55) or one behind an ``stLayoutWrapper`` (≥ 1.56).
    Only one of them exists in a given Streamlit version, so the marker is
    never drawn twice.
    """
    row = f'[data-stx-list-item-uid="{item_id}"]'
    selectors = ", ".join((
        f'{row}::before',
        f'{row} > [data-testid="stVerticalBlock"]::before',
        f'{row} > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]::before',
    ))
    bullet_css = (
        f'<style>{selectors} {{ content: {bullet_content}; }}</style>'
    )
    marker_attrs = (
        f'class="stx-marker {item_id}" '
        f'data-stx-kind="list-item" data-stx-uid="{item_id}"'
    )
    if is_ordered:
        marker_attrs += ' data-stx-ordered'
    return (
        f'{bullet_css}'
        f'<span {marker_attrs} style="display:none"></span>'
    )


def _build_list_root_payload(list_id: str, text_align: str | None = None,
                             block_align: str | None = None) -> str:
    """Return the sentinel marker span for a list root container.

    The styling rules (counter-reset, gap, width, margins, alignment) live
    in the global stylesheet under ``.stx-list``; every knob is read from a
    ``--stx-list-*`` custom property.  The marker mode is not among them: it
    is decided per item by the observer from the resolved ``text-align``.  The observer forwards each
    ``data-stx-list-*`` attribute set here onto the list container as that
    property, so an attribute omitted here leaves the CSS fallback in
    place — which is how "inherit from my container" stays the default.
    """
    attrs = ""
    if text_align:
        attrs += f' data-stx-list-text-align="{text_align}"'
    if block_align:
        attrs += (' data-stx-list-width="fit-content"'
                  f' data-stx-list-margin-inline="{_BLOCK_ALIGN_MARGIN[block_align]}"')
    return (
        f'<span class="stx-marker {list_id}" '
        f'data-stx-kind="list" data-stx-uid="{list_id}"'
        f'{attrs} style="display:none"></span>'
    )


class ListController:
    def __init__(self, li_style: Style, bullet_content: str, is_ordered: bool,
                 alt_li_styles: list[Style] | None = None):
        self.li_style = li_style
        self.bullet_content = bullet_content
        self.is_ordered = is_ordered
        self.alt_li_styles = alt_li_styles
        self._item_index = 0

    @contextmanager
    def item(self, style: Style = None):
        """
        Creates a list item with a Flexbox layout:
        [Bullet] [Vertical Stack of Content]
        """
        final_style = self.li_style
        if self.alt_li_styles:
            alt = self.alt_li_styles[self._item_index % len(self.alt_li_styles)]
            final_style = final_style + alt
            self._item_index += 1
        if style:
            final_style = final_style + style

        # We generate a unique ID for the Outer Container (the 'LI')
        item_id = generate_key("li")

        css_and_marker = _build_list_item_payload(item_id, self.bullet_content, self.is_ordered)

        # Structure:
        # [ st_block (Outer) ]
        #    -> ::before (Bullet)
        #    -> [ st.container (Inner) ]
        #          -> User Content (Stacked)

        # Export wrapper: <li> (suppresses st_block's own <div>)
        if is_export_active():
            export_push_wrapper(f'<li style="{final_style}">')

        with st_block(style=final_style, _export_wrapper=False):
            # Per-item bullet stylesheet + sentinel marker span go INSIDE the
            # block so the observer's `closest('[data-testid="stVerticalBlock"]')`
            # finds the block's container (same target as the legacy :has() rule).
            st.html(css_and_marker)

            # THIS IS THE FIX:
            # We open a new container to wrap all user content.
            # This container becomes the second item in the Flex Row,
            # and it naturally stacks its children (st_write, st_list) vertically.
            with st.container():
                yield

        if is_export_active():
            export_pop_wrapper("</li>")


@contextmanager
def st_list(
    list_type: ListType = ListTypes.unordered,
    l_style: Style = s.none,
    li_style: Style = s.none,
    text_align: str | None = None,
    block_align: str | None = None,
    align: str | None = None,
    alt_li_styles: list[Style] | None = None,
):
    """
    A context manager representing a list (ordered or unordered) with optional styles and support for nested lists.

    :param list_type: The type of list, either ordered (`<ol>`) or unordered (`<ul>`). Defaults to unordered.
    :param l_style: A `Style` object for the entire list. Supports custom list-level styles for `ListStyle`.
    :param li_style: A `Style` object for individual list items. Defaults to `StxStyles.none`.
    :param text_align: Alignment of the list TEXT — ``"left"``, ``"center"``,
        ``"right"``, ``"justify"`` or ``None``.  Mirrors the CSS pair
        ``text-align`` + ``list-style-position: inside``: for ``"center"``
        and ``"right"`` the bullet moves INTO the first line of each item so
        bullet and text stay together.  Never changes any width, so the list
        keeps filling its cell and a nested list keeps the full width of its
        item — the safe choice inside a grid.  ``None`` (default) sets
        nothing and the list inherits the alignment of its container, like
        any other HTML element; an INHERITED ``center`` or ``right`` moves
        the bullet into the line just the same (0.7.34), so declaring the
        alignment once on the container — or on
        ``PresentationConfig(text_align=…)`` — is enough.
    :param block_align: Placement of the list BOX — ``"left"``, ``"center"``,
        ``"right"`` or ``None``.  Shrinks the list to ``width: fit-content``
        and places it with automatic margins; the bullet column stays
        aligned and the group is placed as a unit.  **It makes the list as
        wide as its content**, so editing one item changes the list width:
        avoid it in a grid whose geometry must stay stable — use
        ``text_align`` there.
    :param align: Deprecated synonym of ``block_align`` (kept for backward
        compatibility, no runtime warning).  Prefer ``block_align`` for the
        box placement, or ``text_align`` when the intent is to align text.
    :param alt_li_styles: Optional list of ``Style`` objects to cycle through for each item.
        Applied after ``li_style`` and before the per-item ``style`` argument.
        The style at index ``i % len(alt_li_styles)`` is merged for the i-th item.

    Notes:
    - Supports nested lists recursively, with the nesting level affecting the style if `l_style` is a `ListStyle`.

    ## Syntax Example:
    ```
    with st_list(
        list_type=lt.unordered,
        l_style=s.none,
        li_style=bs.list_item_style
        ) as l:
        with l.item(): st_write("List Item 1")
        with l.item():
            st_write("List Item 2")
            with st_list() as l2:
                with l2.item(): st_write("Nested Item 1")
                with l2.item(): st_write("Nested Item 2")
    ```
    """
    text_align = _validate_align("text_align", text_align, _TEXT_ALIGN_VALUES)
    block_align = _validate_align("block_align", block_align, _BLOCK_ALIGN_VALUES)
    align = _validate_align("align", align, _BLOCK_ALIGN_VALUES)
    if block_align is None:
        block_align = align

    current_level = _current_list_level.get()
    next_level = current_level + 1
    token = _current_list_level.set(next_level)

    try:
        # Resolve Bullet Content
        bullet_content = "'•'"
        is_ordered = (list_type == ListTypes.ordered)

        if is_ordered:
            counter_style = "decimal"
            style_str = str(l_style)
            match = re.search(r"list-style-type\s*:\s*([\w-]+)", style_str)
            if match:
                counter_style = match.group(1)
            bullet_content = f"counter(streamtex-counter, {counter_style}) '.'"

        elif isinstance(l_style, ListStyle) and l_style.symbols:
            idx = (next_level - 1) % len(l_style.symbols)
            symbol_char = l_style.symbols[idx]
            bullet_content = f"'{symbol_char}'"
        else:
            if next_level == 2:
                bullet_content = "'○'"
            elif next_level >= 3:
                bullet_content = "'■'"

        list_id = generate_key("ul")
        tag = "ol" if is_ordered else "ul"

        marker = _build_list_root_payload(list_id, text_align, block_align)

        # Export wrapper: semantic <ul>/<ol> (suppresses st_block's own <div>)
        if is_export_active():
            _extra = _list_export_css(text_align, block_align)
            _base = f"{l_style}".strip()
            if _base and _extra:
                _style_attr = f"{_base.rstrip(';')}; {_extra}"
            else:
                _style_attr = _base or _extra
            export_push_wrapper(f'<{tag} style="{_style_attr}">')

        # NOTE (0.7.33): the list root used to carry a hard-coded inline
        # `text-align: left`, added to stop an inherited alignment from
        # splitting bullet and text.  That floor also made alignment
        # un-inheritable for every user.  The default now lives in the
        # global stylesheet as the fallback of `--stx-list-text-align`
        # (`inherit`), and the split is cured properly by the "inside"
        # mode that `text_align=` switches on.
        with st_block(style=l_style, _export_wrapper=False):
            st.html(marker)
            yield ListController(li_style=li_style, bullet_content=bullet_content, is_ordered=is_ordered, alt_li_styles=alt_li_styles)

        if is_export_active():
            export_pop_wrapper(f"</{tag}>")

    finally:
        _current_list_level.reset(token)
