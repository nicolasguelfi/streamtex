import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #660000 -> s.project.colors.deep_red
      #674ea7 -> s.project.colors.purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #cc0000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Interactive Mini-Workshop on AI, Ethics & Society ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange, "Creation of "),
                (s.project.colors.deep_red + s.bold, "groups"),
                (s.project.colors.gold + s.italic, "(if time is short, one group altogether)"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange, "Each group member chooses a specific "),
                (s.project.colors.deep_red + s.bold, "activity"),
                (s.project.colors.burnt_orange, " (professional or not)"),
                (s.italic, "possible choice criteria are:"),
                (s.italic, "- your high own experience- its high potential relation with AI- its frequency in human societies"),
            )
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "For each chosen activity")
        with lst.item():
            pass
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, " General Discussion "),
                (s.project.colors.bright_red + s.bold, "!!! Take some notes during the group session !!! "),
            )
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
