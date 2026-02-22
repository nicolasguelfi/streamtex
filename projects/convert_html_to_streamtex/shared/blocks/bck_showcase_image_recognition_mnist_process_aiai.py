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
      #37761c -> s.project.colors.olive_green
      #980000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Process ", tag=t.h5)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " connect to Adam W. Harley's visualization tool",
                (s.project.colors.olive_green + s.italic, "(cf. 'MNIST Digit recognition' section of the CoursePack)"),
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://adamharley.com/nn_vis/cnn/2d.html"),
            )
        with lst.item():
            st_write(s.bold, " Make some drawing of digits in the drawing zone")
        with lst.item():
            st_write(s.bold, "Check the prediction(s)")
        with lst.item():
            st_write(s.bold, " Try various \"weird\" digit drawings trying to fool the recognition")
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, " Be prepared to share findings with the group")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
