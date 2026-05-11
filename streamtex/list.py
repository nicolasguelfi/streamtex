import re
from contextlib import contextmanager
from contextvars import ContextVar

import streamlit as st

from .container import st_block
from .enums import ListType, ListTypes
from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .marker_runtime import is_marker_runtime_enabled
from .styles import ListStyle, Style
from .styles import StxStyles as s
from .utils import generate_key

_current_list_level = ContextVar("list_level", default=0)


def _build_list_item_payload(item_id: str, bullet_content: str, is_ordered: bool) -> str:
    """Return the CSS+marker payload that scopes a single list item.

    Two code paths share the same call site:

    * **Legacy**: emits 4 ``:has()``-scoped rules that turn the parent
      ``stVerticalBlock`` into a flex row with a ``::before`` bullet.
    * **Marker runtime**: emits a sentinel span with
      ``data-stx-kind="list-item"`` + a tiny per-item ``<style>`` for the
      bullet's ``content`` value (a per-item stylesheet is necessary
      because ``content: counter(streamtex-counter, …) '.'`` cannot be
      reliably carried by a CSS custom property).  All other rules
      (flex layout, bullet alignment, marker-cell hide, content wrapper)
      live in the global stylesheet under ``.stx-list-item``.
    """
    if is_marker_runtime_enabled():
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

    # Legacy :has() path — emits 4 rules + the marker span.
    return f"""
    <style>
        /* 1. OUTER CONTAINER (Flex Row) */
        /* This holds the bullet and the content wrapper side-by-side */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{item_id}) {{
            display: flex;
            flex-direction: row;
            align-items: baseline; /* Aligns bullet with the first line of text */
            gap: 0.5rem;
            {"counter-increment: streamtex-counter;" if is_ordered else ""}
        }}

        /* 2. THE BULLET (::before on Outer) */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{item_id})::before {{
            content: {bullet_content};
            flex-shrink: 0;
            text-align: right;
            min-width: 1.2rem;
            color: inherit;
            font-weight: inherit;

            /* Alignment tweak: prevents bullet from jumping if baseline is weird */
            align-self: baseline;
        }}

        /* 3. HIDE THE MARKER CONTAINER */
        /* We hide the technical div that holds our span.{item_id} so it doesn't take up space in the flex row */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{item_id}) > .element-container:has(span.{item_id}) {{
            display: none;
        }}

        /* 4. INNER CONTENT WRAPPER */
        /* The 'st.container()' we yield creates a new stVerticalBlock inside our Outer one.
           We want this wrapper to grow and handle the vertical stacking of its children. */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{item_id}) > .stVerticalBlock {{
            flex-grow: 1;
            width: auto;      /* Let it fill the flex space */
            display: flex;
            flex-direction: column; /* Force children to stack vertically */
            gap: 0;           /* Optional: tighter stacking */
            min-width: 0;     /* CSS Grid/Flex trick to prevent overflow issues */
        }}
    </style>
    """


def _build_list_root_payload(list_id: str, align: str) -> str:
    """Return the CSS+marker payload that scopes the list root container.

    * **Legacy**: a single ``:has()``-scoped rule on the parent
      ``stVerticalBlock``.
    * **Marker runtime**: a sentinel span with ``data-stx-kind="list"``.  The
      single styling rule (counter-reset + gap + width) lives in the global
      stylesheet under ``.stx-list``.  When ``align == "center"`` an extra
      ``data-stx-list-width`` carries the override.
    """
    width_css = "width: fit-content; margin-inline: auto;" if align == "center" else "width: 100%;"

    if is_marker_runtime_enabled():
        width_attr = ' data-stx-list-width="fit-content"' if align == "center" else ''
        return (
            f'<span class="stx-marker {list_id}" '
            f'data-stx-kind="list" data-stx-uid="{list_id}"'
            f'{width_attr} style="display:none"></span>'
        )

    # Legacy :has() path.
    return f"""
    <style>
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{list_id}) {{
            counter-reset: streamtex-counter;
            gap: 0.2rem;
            {width_css}
        }}
    </style>
    """


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

        css_or_marker = _build_list_item_payload(item_id, self.bullet_content, self.is_ordered)

        # Legacy: CSS is injected up-front (outside the st_block).
        # Marker:  the bullet CSS + marker span are injected INSIDE the
        #          st_block so the marker's closest stVerticalBlock is the
        #          block's container (the same one the legacy :has() rule
        #          targeted).
        if not is_marker_runtime_enabled():
            st.html(css_or_marker)

        # Structure:
        # [ st_block (Outer) ]
        #    -> ::before (Bullet)
        #    -> [ st.container (Inner) ]
        #          -> User Content (Stacked)

        # Export wrapper: <li> (suppresses st_block's own <div>)
        if is_export_active():
            export_push_wrapper(f'<li style="{final_style}">')

        with st_block(style=final_style, _export_wrapper=False):
            if is_marker_runtime_enabled():
                st.html(css_or_marker)
            else:
                st.html(f'<span class="{item_id}" style="display:none"></span>')

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

        css_or_marker = _build_list_root_payload(list_id, align)
        if not is_marker_runtime_enabled():
            st.html(css_or_marker)

        # Export wrapper: semantic <ul>/<ol> (suppresses st_block's own <div>)
        if is_export_active():
            export_push_wrapper(f'<{tag} style="{l_style}">')

        _list_base = Style("text-align: left;", "stx-list-base")
        with st_block(style=_list_base + l_style, _export_wrapper=False):
            if is_marker_runtime_enabled():
                st.html(css_or_marker)
            else:
                st.html(f'<span class="{list_id}" style="display:none"></span>')
            yield ListController(li_style=li_style, bullet_content=bullet_content, is_ordered=is_ordered, alt_li_styles=alt_li_styles)

        if is_export_active():
            export_pop_wrapper(f"</{tag}>")

    finally:
        _current_list_level.reset(token)
