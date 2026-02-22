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
      #783e04 -> s.project.colors.burnt_orange
      #a61b00 -> s.project.colors.salmon
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Generative AI Workshop", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "SETTING UP ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.link_blue, " Gen AI environment / tool"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red, "Quasible.ai", "http://Quasible.ai"),
        tag=t.h3,
    )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "PRACTICE ")
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Select an account / workspace ")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, "Create a stand alone Chat")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "Create a Text Document ")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Import a pdf document ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Chat with a pdf document ")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Create a persona")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Experiment with persona contexts ")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Test your persona ")
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Practice the techniques presented  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Check the illustrationscf. ",
                (s.project.pres.links.link_lg + s.project.colors.salmon + s.bold, "COURSE PACK", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
                (s.project.pres.links.link_lg + s.project.colors.salmon, " links", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
