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
      #2f5a1b -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
      #ff9900 -> s.project.colors.orange
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Practice - "),
        (s.project.colors.forest_green, "Setting up the "),
        (s.project.colors.burnt_orange, "NOTEBOOKS "),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " open the ",
                (s.bold, "COURSEPACK"),
                " in a new tab in your browser ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "  Go to section: \"",
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "Notebooks links", "https://docs.google.com/document/d/1jD9QnYHHqqvCcXieubpwAvoix1GiPzcgOj6XROhhbBI/edit?tab=t.0#heading=h.fhxl49mk9k3e"),
                "\" ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " click on \"link\" of  YOUR ",
                (s.project.colors.orange + s.bold, "Notebook URL"),
                (s.project.colors.burnt_orange + s.bold, "(use your number printed on the paper sheet) "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " connect using ",
                (s.bold, "YOUR gmail"),
                " account (same one used in the resources access form) ",
            )
        with lst.item():
            st_write(" You should see a screen close to this one:")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.italic, "(optional)"),
                " ",
                (s.project.colors.gold + s.bold, "Discover"),
                " the NOTEBOOK environment ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.italic, "(optional)"),
                " Bookmark the notebookdrag the ",
                " below in the bookmarks bar",
            )
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.italic, "(optional)"),
                " Backup notebooks folder",
                (s.project.colors.olive_green + s.bold, "cf. section \"Backup notebooks folder\"  in the "),
                (s.bold, "COURSEPACK"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Open Notebook ",
                (s.project.colors.olive_green + s.bold + s.italic, "-> ask the trainer"),
            )
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, "Duplicate the notebook")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
