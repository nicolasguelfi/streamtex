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
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.4. Main Python libraries ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "datetime ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "keras ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "sklearn ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "tensorflow ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "tqdm ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "json ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "matplotlib ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "numpy ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "os ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "pandas ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "platform ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "seaborn ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "sys ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "time ")
        with lst.item():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
