import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    emphasis = s.bold + s.big
    highlight = s.project.titles.emphasis_structure + s.Large + s.center_txt

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "Conclusion",
        toc_lvl="1",
    )
    st_space(size=2)
    st_write(
        s.project.titles.slide_title,
        "Conclusion: From Sense to Reference",
        toc_lvl="2",
    )
    st_space(size=2)
    st_write(bs.body, "Three architectural mechanisms bridge the semantic gap:")
    st_space(size=2)
    with st_list(list_type=lt.ordered, li_style=bs.body) as l:
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Agent specialization"),
                " -> better initial conformance (25.0% vs. 5.8% first-attempt)",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "Hierarchical validation"),
                " -> systematic SER_BPMN checking via simulation",
            )
        with l.item():
            st_write(
                bs.body,
                (bs.emphasis, "CoT feedback"),
                " -> 7x first-repair success rate",
            )
    st_space(size=3)
    st_write(
        bs.highlight,
        "Up to 70 pp improvement across 9 diverse LLM architectures.",
    )
    st_space(size=2)
