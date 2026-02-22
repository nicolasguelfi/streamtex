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
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h1, " Google Meet ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("connect to the meeting room ")
        with lst.item():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
