import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "Quasible ID"),
        (s.project.colors.gold + s.bold, " and Group ID "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "Fill the survey", "https://forms.gle/7fzbv5299bRJ17K6A"), (s.project.colors.olive_green + s.bold, "AI4EIS2-26"), (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://app.quasible.ai/en/accounts/gai4as251205"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://docs.google.com/spreadsheets/d/1mdaQRrUY61vARZEQDS5zyy6vQvO_ZuIXTxqS5IafW48/edit?resourcekey=&gid=1041511767#gid=1041511767"))
        with g.cell():
            pass
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "!! WARNING !!  ", tag=t.h5)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange, "Stay on the same device ")
        with lst.item():
            st_write(s.project.colors.teal, "Log-in your quasible account ")
        with lst.item():
            st_write(s.project.colors.burnt_orange, "Check your invitation email to the group account ")
        with lst.item():
            st_write(s.project.colors.teal, "click on the accept invitation button ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
