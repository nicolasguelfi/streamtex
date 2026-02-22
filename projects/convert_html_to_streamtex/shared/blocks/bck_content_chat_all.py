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
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Group Discovery (60') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Presentation (15') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Showcase (30') ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Text Generation ")
        with lst.item():
            st_write("Media Recognition / Generation ")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Break (15') ", tag=t.h4)
    st_space(size=3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Intuitive introduction to AI (30') ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "AI & Deep Learning - Part 1 (30') ", tag=t.h4)
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END ", tag=t.h4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "AI & Deep Learning - Part 2", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Ethics & Society & AI", tag=t.h4)
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Generative "),
        (s.project.colors.gold, "AI"),
        (s.project.colors.burnt_orange, " "),
        (s.project.colors.burnt_orange, "Workshop"),
        tag=t.h4,
    )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 3", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "LLM & ChatBots ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Creation & SpecializationTechniques", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 4", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Mini Project ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & SpecializeUse & Demonstrate ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
