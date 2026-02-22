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
    st_write(s.project.doc.titles.h2, "8.4. Practice processes ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
