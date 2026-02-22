import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #4c1130 -> s.project.colors.dark_purple
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #a61b00 -> s.project.colors.salmon
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=5)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Practice", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Designing your ChatBot ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://app.quasible.ai/en/workspaces/numaya-xv4l"),
        (s.project.colors.burnt_orange, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://app.quasible.ai/en/embed/p18z32qf5uheld0su4n3er2s"),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "SETTING UP ")
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.link_blue, "Connect to"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, " ", "http://quasible.ai"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red, "Quasible.ai ", "http://quasible.ai"),
        tag=t.h3,
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "PRACTICE ")
    st_space(size=4)
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.salmon + s.bold, " Define your targeted ChatBot"),
                (s.project.colors.forest_green + s.bold, "cf. COURSEPACK for ideas"),
            )
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Develop incrementally your ChatBot: ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, "Advices ")
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Check the illustrationscf.",
                (s.project.pres.links.link_lg, " ", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
                (s.project.pres.links.link_lg + s.project.colors.salmon + s.bold, "COURSE PACK", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
                (s.project.pres.links.link_lg + s.project.colors.salmon, " links", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
            )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_body + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1KRpO8EAEfPaDQ9b78nTxPjLJpwanTw_U_mdXo4EVkxY/edit")
    st_space(size=3)
    st_space(size=3)
