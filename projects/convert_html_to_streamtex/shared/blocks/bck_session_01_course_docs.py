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
      #20124d -> s.project.colors.dark_purple
      #2f5a1b -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 1 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Course documentation ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "©"),
        (s.project.colors.bright_red + s.bold, " "),
        (s.project.colors.bright_red + s.bold, "DO NOT DISTRIBUTE"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Main Documents & Usage ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.olive_green, "Course"),
                (s.project.colors.burnt_orange, " "),
                (s.project.colors.teal, "Pack"),
                (s.project.colors.burnt_orange, " Document "),
            )
        with lst.item():
            pass
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red, "Practice"),
                (s.project.colors.burnt_orange, " "),
                (s.project.colors.teal, "Pack"),
                (s.project.colors.burnt_orange, " Document "),
            )
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("all material for practice sessions ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange, "Training "),
                (s.project.colors.dark_purple, "Slides"),
            )
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
