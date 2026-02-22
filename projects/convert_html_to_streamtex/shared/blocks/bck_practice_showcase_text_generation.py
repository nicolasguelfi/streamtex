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
      #1b4587 -> s.project.colors.navy_blue
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #5b0f00 -> s.project.colors.deep_red
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #980000 -> s.project.colors.bright_red
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff9900 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Playground Practice  ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Experiment Generative AI tools ", tag=t.h4)
    st_space(size=3)
    st_space(size=4)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "{"),
        (s.project.colors.deep_red + s.bold, "Text"),
        (s.project.colors.bright_red + s.bold, ", "),
        (s.project.colors.navy_blue + s.bold, "image"),
        (s.project.colors.bright_red + s.bold, ", "),
        (s.project.colors.dark_purple + s.bold, "sound"),
        (s.project.colors.bright_red + s.bold, ",...} "),
        (s.project.colors.teal + s.bold, "to"),
        (s.project.colors.bright_red + s.bold, " {"),
        (s.project.colors.deep_red + s.bold, "Text"),
        (s.project.colors.bright_red + s.bold, ", "),
        (s.project.colors.navy_blue + s.bold, "image"),
        (s.project.colors.bright_red + s.bold, ", "),
        (s.project.colors.dark_purple + s.bold, "sound"),
        (s.project.colors.bright_red + s.bold, ",...} "),
        (s.project.colors.forest_green + s.bold, "AI based "),
        (s.project.colors.burnt_orange + s.bold, "Generation "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Text Generation ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Connect to a GenAI ChatBot like  ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "chatgpt.com", "https://chatgpt.com/"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Click on ",
                (s.project.colors.forest_green + s.bold, "\"Continue with Google\""),
                (s.project.colors.orange + s.bold, "using "),
                (s.project.colors.forest_green + s.bold, "your"),
                (s.project.colors.orange + s.bold, " gmail account orusing "),
                (s.project.colors.forest_green + s.bold, "your"),
                (s.project.colors.orange + s.bold, " "),
                (s.project.colors.bright_red + s.bold, "openai"),
                (s.project.colors.orange + s.bold, " account "),
            )
        with lst.item():
            pass
        with lst.item():
            st_write(" Start a chat using the prompt field ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Choose your ",
                (s.project.colors.gold + s.bold, "own best domain of expertise "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Start a chat to ",
                (s.project.colors.gold + s.bold, "test its capacity"),
                " to answer questions from your domain ",
            )
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Objectives:")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
