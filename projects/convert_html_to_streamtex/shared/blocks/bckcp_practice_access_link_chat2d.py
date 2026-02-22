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
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "4. Practice Resources ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_lg,
        "Consult the document available ",
        (s.project.doc.links.link_lg + s.project.colors.link_blue + s.bold, "HERE", "https://docs.google.com/document/d/1ANgxJ6topPP_jNLiI4lgMxPxunbmBHxcmhE8tfqkv8U"),
    )
    st_space(size=1)
    st_space(size=1)
