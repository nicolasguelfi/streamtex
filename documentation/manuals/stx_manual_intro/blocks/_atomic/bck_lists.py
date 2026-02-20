import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """List demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    list_item = s.large
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Lists", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Unordered list
        st_write(bs.sub, "Unordered list (lt.unordered)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Render bullet-point lists with st_list and lt.unordered.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_list(list_type=lt.unordered,
                         li_style=bs.list_item) as l:
                with l.item(): st_write("First unordered item")
                with l.item(): st_write("Second unordered item")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.unordered, li_style=bs.list_item) as l:
            with l.item(): st_write("First unordered item")
            with l.item(): st_write("Second unordered item")
            with l.item(): st_write("Third unordered item")
        st_space("v", 2)

        # Ordered list
        st_write(bs.sub, "Ordered list (lt.ordered)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Render numbered lists with lt.ordered.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_list(list_type=lt.ordered,
                         li_style=bs.list_item) as l:
                with l.item(): st_write("Step one")
                with l.item(): st_write("Step two")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.ordered, li_style=bs.list_item) as l:
            with l.item(): st_write("Step one")
            with l.item(): st_write("Step two")
            with l.item(): st_write("Step three")
        st_space("v", 2)

        # Nested lists
        st_write(bs.sub, "Nested lists", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Nest st_list contexts for multi-level hierarchies.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_list(list_type=lt.unordered,
                         li_style=bs.list_item) as l:
                with l.item():
                    st_write("Parent item A")
                    with st_list(list_type=lt.unordered,
                                 li_style=bs.list_item) as l2:
                        with l2.item(): st_write("Child A.1")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.unordered, li_style=bs.list_item) as l:
            with l.item():
                st_write("Parent item A")
                with st_list(list_type=lt.unordered,
                             li_style=bs.list_item) as l2:
                    with l2.item(): st_write("Child A.1")
                    with l2.item():
                        st_write("Child A.2")
                        with st_list(list_type=lt.unordered,
                                     li_style=bs.list_item) as l3:
                            with l3.item(): st_write("Grandchild A.2.a")
                            with l3.item(): st_write("Grandchild A.2.b")
            with l.item(): st_write("Parent item B")
        st_space("v", 2)

        # ListStyle with custom symbols (g_docs)
        st_write(bs.sub, "ListStyle with custom symbols", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use ListStyle for custom bullet symbols at each nesting level.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_list(list_type=lt.unordered,
                         l_style=s.container.lists.g_docs,
                         li_style=bs.list_item) as l:
                with l.item(): st_write("Level 1 symbol")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.unordered,
                     l_style=s.container.lists.g_docs,
                     li_style=bs.list_item) as l:
            with l.item():
                st_write("Level 1 symbol")
                with st_list(list_type=lt.unordered,
                             l_style=s.container.lists.g_docs,
                             li_style=bs.list_item) as l2:
                    with l2.item():
                        st_write("Level 2 symbol")
                        with st_list(list_type=lt.unordered,
                                     l_style=s.container.lists.g_docs,
                                     li_style=bs.list_item) as l3:
                            with l3.item(): st_write("Level 3 symbol")
            with l.item(): st_write("Another level 1")
        st_space("v", 2)

        # Ordered lowercase
        st_write(bs.sub,
                 "Ordered lowercase (ordered_lowercase)",
                 toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use ordered_lowercase for alphabetical (a, b, c) list markers.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with st_list(list_type=lt.ordered,
                         l_style=s.container.lists.ordered_lowercase,
                         li_style=bs.list_item) as l:
                with l.item(): st_write("Item a")
                with l.item(): st_write("Item b")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.ordered,
                     l_style=s.container.lists.ordered_lowercase,
                     li_style=bs.list_item) as l:
            with l.item(): st_write("Item a")
            with l.item(): st_write("Item b")
            with l.item(): st_write("Item c")
        st_space("v", 2)

        # Per-item style override
        st_write(bs.sub, "Per-item style override", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Override the style of individual items with l.item(style=...).
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            with l.item(style=s.text.colors.coral):
                st_write("Highlighted item (coral override)")
        """))
        st_space("v", 1)

        with st_list(list_type=lt.unordered, li_style=bs.list_item) as l:
            with l.item(): st_write("Normal item")
            with l.item(style=s.text.colors.coral):
                st_write("Highlighted item (coral override)")
            with l.item(): st_write("Normal item")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Defaults: list_type=lt.unordered, l_style=none, li_style=none.
            Set a consistent li_style on the list.
            Override per-item only when needed for emphasis.
        """))
