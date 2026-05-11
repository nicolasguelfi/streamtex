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


def _build_list_item_payload(item_id: str, bullet_content: str, is_ordered: bool) -> str:
    """Return the per-item bullet CSS + sentinel marker span for a list item.

    The bullet ``content:`` value (which may include ``counter(streamtex-counter,
    decimal) '.'`` for ordered lists) is carried by a tiny per-item
    stylesheet keyed by ``[data-stx-list-item-uid="…"]`` — CSS ``var()``
    cannot reliably carry a ``counter()`` function call across browsers.
    All other rules (flex layout, gap, baseline alignment, marker-cell
    hide, inner content wrapper) live in the global stylesheet under
    ``.stx-list-item``.
    """
    bullet_css = (
        f'<style>'
        f'[data-stx-list-item-uid="{item_id}"]::before'
        f'{{ content: {bullet_content}; }}'
        f'</style>'
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


def _build_list_root_payload(list_id: str, align: str) -> str:
    """Return the sentinel marker span for a list root container.

    The single styling rule (counter-reset + gap + default width) lives in
    the global stylesheet under ``.stx-list``.  ``align="center"`` is
    forwarded as ``data-stx-list-width="fit-content"`` so the global
    stylesheet can override the default 100% width.
    """
    width_attr = ' data-stx-list-width="fit-content"' if align == "center" else ''
    return (
        f'<span class="stx-marker {list_id}" '
        f'data-stx-kind="list" data-stx-uid="{list_id}"'
        f'{width_attr} style="display:none"></span>'
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
    align: str = None,
    alt_li_styles: list[Style] | None = None,
):
    """
    A context manager representing a list (ordered or unordered) with optional styles and support for nested lists.

    :param list_type: The type of list, either ordered (`<ol>`) or unordered (`<ul>`). Defaults to unordered.
    :param l_style: A `Style` object for the entire list. Supports custom list-level styles for `ListStyle`.
    :param li_style: A `Style` object for individual list items. Defaults to `StxStyles.none`.
    :param align: Optional alignment for list items as a block (e.g. ``"center"``).
        When set, the list container uses ``align-items: <align>`` so that
        bullet + text form a centered unit.  Defaults to ``None`` (no change).
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

        marker = _build_list_root_payload(list_id, align)

        # Export wrapper: semantic <ul>/<ol> (suppresses st_block's own <div>)
        if is_export_active():
            export_push_wrapper(f'<{tag} style="{l_style}">')

        _list_base = Style("text-align: left;", "stx-list-base")
        with st_block(style=_list_base + l_style, _export_wrapper=False):
            st.html(marker)
            yield ListController(li_style=li_style, bullet_content=bullet_content, is_ordered=is_ordered, alt_li_styles=alt_li_styles)

        if is_export_active():
            export_pop_wrapper(f"</{tag}>")

    finally:
        _current_list_level.reset(token)
