import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #2f5a1b -> s.project.colors.forest_green
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "AI & Deep Learning ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=2)
    st_space(size=3)
    st_space(size=5)
    st_space(size=1)
