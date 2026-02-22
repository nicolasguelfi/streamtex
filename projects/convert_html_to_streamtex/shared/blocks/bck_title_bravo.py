import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #cc4125 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.salmon + s.bold, "BRAVO ! ")
    st_space(size=3)
    st_space(size=1)
