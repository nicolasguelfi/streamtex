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
      #4c1130 -> s.project.colors.dark_purple
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff9900 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Session 3 ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.orange, "Content ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "LLM & ChatBots ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Creation & SpecializationTechniques", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "PART 1 (90') ")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Break (15')", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "PART 2 (90') ")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
