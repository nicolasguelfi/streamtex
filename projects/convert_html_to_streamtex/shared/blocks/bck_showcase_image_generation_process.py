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
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Process ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " connect to the Deep Dream Generator site ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "HERE", "https://deepdreamgenerator.com"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " \"Log In\" and click on \"Google\":",
                " with the default aiailearner google account ",
                (s.italic, "(see printed paper)"),
            )
        with lst.item():
            pass
        with lst.item():
            st_write(" click on \"Generate\"")
        with lst.item():
            st_write(" set the text (and parameters) ")
        with lst.item():
            st_write(" Click on Generate")
    st_space(size=1)
