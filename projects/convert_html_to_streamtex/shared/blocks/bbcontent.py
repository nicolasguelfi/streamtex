import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.titles.h1, "2 General content of nicolas ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_body, "Ce document")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
