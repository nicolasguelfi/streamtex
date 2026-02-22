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
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Group Discovery (60') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Training Presentation (15') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Break (15') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Showcase (60')", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Intuitive introduction to AI (30') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "AI & Deep Learning - Part 1&2", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Ethics & Society & AI ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Break (15')", tag=t.h4)
    st_space(size=1)
    st_space(size=2)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Generative "),
        (s.project.colors.gold, "AI"),
        (s.project.colors.burnt_orange, "Practice - Session 1"),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END ", tag=t.h4)
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
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Generative "),
        (s.project.colors.gold, "AI"),
        (s.project.colors.burnt_orange, "Practice - Session 1"),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & SpecializeUse & Demonstrate ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 5", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Introduction to Wordpress ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Wordpress Components"),
        (s.project.colors.burnt_orange, "Wordpress Practical - Session 1"),
        tag=t.h4,
    )
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 6", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Wordpress Plugins"),
        (s.project.colors.burnt_orange, "Content GeneratorsChatBots "),
        tag=t.h4,
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.burnt_orange, "Projects Start"),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Tools Setup ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Wordpress Practical - Session 2 ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 7", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Wordpress with GenAI Bot"),
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.burnt_orange, "Project "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & SpecializeUse & Demonstrate  ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 8", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Wordpress with GenAI Bot"),
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.burnt_orange, "Project "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & SpecializeUse & Demonstrate  ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 9", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Wordpress with GenAI Bot"),
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.burnt_orange, "Project "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Create & SpecializeUse & Demonstrate  ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 10", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Wordpress with GenAI Bot"),
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.forest_green, "Project Demos & User feedbacks "),
        tag=t.h4,
    )
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Training Closure ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
