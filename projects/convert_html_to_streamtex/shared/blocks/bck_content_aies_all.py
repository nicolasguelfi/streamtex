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
      #351b75 -> s.project.colors.dark_purple
      #731b47 -> s.project.colors.dark_purple
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 1", tag=t.h3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Training Group Discovery (60') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Training Content (15') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Setting up COMPUTERS (30') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Showcase & Playground (90') ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Text Generation ")
        with lst.item():
            st_write("Media Recognition / Generation ")
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "LUNCH BREAK (60') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 2 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Intuitive introduction to AI (30') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.gold, "AI & Deep Learning (45') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Prompt Engineering (30') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15')", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Ethics & AI (90')", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 3 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "Session introduction (15') ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Prompt Engineering Practice (90') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15')", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Interactive Mini-Workshop  ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "on AI & Ethics (90')", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "LUNCH BREAK (60') ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 4 ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "AI & Society (90') ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Break (15')", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Interactive Mini-Workshop  ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "on AI & Society (& Ethics) (90') ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DLH Training Survey ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Wrap-up discussion", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "!! The End !! ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
