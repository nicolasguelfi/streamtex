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
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "(Artificial) Neural Network ", tag=t.h3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Layers: input, output, hidden ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
