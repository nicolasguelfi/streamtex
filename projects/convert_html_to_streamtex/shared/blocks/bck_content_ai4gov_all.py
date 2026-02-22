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
      #674ea7 -> s.project.colors.purple
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session Practice ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Discover Some Chatbots (30') ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.purple, "Observe"),
        (s.project.colors.burnt_orange, " and "),
        (s.project.colors.dark_purple, "Test"),
        tag=t.h4,
    )
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Evaluate ChatBots (10')", tag=t.h4)
    st_space(size=2)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Prompts & Specialized Domains (20') ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "Designing Prompts for ChatBot Codix (40') ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "Discussion ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "--- ? NEXT TIME ?--- ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Designing Prompts for ChatBot ComCamp")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.navy_blue + s.bold, "Designing Prompts for ChatBot TechLine")
    st_space(size=4)
    st_space(size=3)
    st_space(size=1)
