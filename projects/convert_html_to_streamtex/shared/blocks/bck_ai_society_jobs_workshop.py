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
      #660000 -> s.project.colors.deep_red
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Re/Up-Skilling for AI ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange, " Each participant should fill the AI Jobs sheet "),
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "HERE", "https://docs.google.com/spreadsheets/d/1UgwO5K7GBm2675ZyKi-kKISKzqNy6Q2p35hHq4NIIH0/edit#gid=1039760689"),
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange, " Creation of "),
                (s.project.colors.deep_red + s.bold, "groups"),
                (s.project.colors.gold + s.italic, "(if time is short, one group altogether) "),
            )
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.colors.burnt_orange, "For each group, work altogether to: ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "General Discussion "),
                (s.project.colors.bright_red + s.bold, "!!! Take some notes during the group session !!! "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
