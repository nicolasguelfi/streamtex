import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0b5394 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Text Generation ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.pres.links.link_lg + s.project.colors.navy_blue + s.bold, "chatgpt.com", link="https://chatgpt.com")
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.pres.links.link_lg + s.project.colors.navy_blue + s.bold, "models comparison", link="https://sdk.vercel.ai/")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
