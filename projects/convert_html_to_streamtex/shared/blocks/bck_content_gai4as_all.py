import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #731b47 -> s.project.colors.dark_purple
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
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1 ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Group Discovery (45') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Training Presentation (15') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Showcase"),
        (s.project.colors.bright_red, " "),
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.bright_red, " "),
        (s.project.colors.burnt_orange, "(45')"),
        tag=t.h4,
    )
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Showcase "),
        (s.project.colors.forest_green, "G"),
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.dark_purple, "4"),
        (s.project.colors.navy_blue, "AS"),
        (s.project.colors.bright_red, " (15') "),
        tag=t.h4,
    )
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Break (15') ", tag=t.h4)
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Intuitive introduction to "),
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.bright_red, " (30') "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Setting up the computers (30') ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Quasible Training Tool (60')", tag=t.h4)
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Break (15')", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Practice - Session 1 (60') ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Wrap-up (15') ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "Session END ", tag=t.h4)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 3", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "AI & DEEP LEARNING ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Using & Specializing LLMs ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "AI Agents Process", tag=t.h4)
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
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Project - Overview ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Project Session 1 & 2 ", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 5", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Ethics & Society ", tag=t.h4)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Project Session 3 ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Ethical Constraints", tag=t.h4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 6", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Project Session 3 ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "Projects Demonstrations ", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DLH Training Survey ", tag=t.h4)
    st_space(size=2)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Training Closure ", tag=t.h4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=3)
