import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    emphasis = s.bold + s.big
    italic_note = s.big + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Methodology",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "Approach Overview: From Sense Toward Reference",
        toc_lvl="2",
    )
    st_space(size=2)
    st_write(bs.body, "Three design principles:")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=bs.body) as l:
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Agent Specialization"),
                ": Narrow generation to type-specific constructs",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Hierarchical Validation"),
                ": Enforce semantic constraints via simulation",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "CoT-Articulated Diagnostic Feedback"),
                ": Connect violations to execution consequences",
            )
    st_space(size=2)
    st_write(
        bs.italic_note,
        "Each mechanism compensates for a specific limitation of distributional learning.",
    )
    st_space(size=2)
