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
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 4", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Mini Project ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & Use & Specialize", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "PART 1 (75') ")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Break (15')", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "PART 2 (60') ")
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Demonstrate & Debrief (45') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "TRAINING SURVEY ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "CLOSURE ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
