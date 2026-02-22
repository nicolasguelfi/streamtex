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
      #134f5c -> s.project.colors.teal
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #3c78d8 -> s.project.colors.sky_blue
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Administrative & Support  ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h2 + s.project.colors.bright_red, "Tasks of Interest ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Fill the Google Sheet ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Administrative and Support Services "),
        (s.project.colors.teal, "Tasks "),
        tag=t.h4,
    )
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Link in your "),
        (s.project.colors.sky_blue, "COURSEPACK "),
        tag=t.h5,
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://docs.google.com/spreadsheets/d/1ulPngZ1iHvZtMghlyyNJPgK-YCWRk4mIUIWWZTXYJQ0/edit?usp=sharing")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
