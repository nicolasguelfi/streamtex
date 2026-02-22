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
      #2f5a1b -> s.project.colors.forest_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practice - CoursePack Access", tag=t.h2, toc_lvl="+1")
    st_space(size=5)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Process", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Please proceed to the following process: ")
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Start your computer (if not started) ")
        with lst.item():
            st_write(" Open a session using the institution identification information(if not already opened) ")
        with lst.item():
            st_write(" Launch chrome/firefox application ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Go to ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "aiai.ros.lu", "https://aiai.ros.lu"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Click on ",
                (s.project.colors.bright_red + s.bold, "\"Go\""),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Fill the form with ",
                (s.bold, "YOUR"),
                " ",
                (s.project.colors.forest_green + s.bold, "MAIN"),
                (s.project.colors.forest_green + s.bold, " "),
                (s.project.colors.forest_green + s.bold, "email address"),
                (s.project.colors.salmon + s.bold, "USE "),
                (s.project.colors.burnt_orange + s.bold, "THE CODE"),
                (s.project.colors.salmon + s.bold, " PRINTED ON PAPER"),
            )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://forms.gle/g8u9egDTtxhXjLfS8")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "GAI4AS"),
        (s.project.colors.forest_green + s.bold, "251205 "),
    )
    st_space(size=3)
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Check your email(s)")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Click on the ",
                (s.project.colors.gold + s.bold, "PROVIDED"),
                " link(s)",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://forms.gle/g8u9egDTtxhXjLfS8"),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
