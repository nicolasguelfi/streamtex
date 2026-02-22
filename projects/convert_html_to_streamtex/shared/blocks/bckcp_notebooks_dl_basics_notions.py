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
    st_write(s.project.doc.titles.h2, "11.3. Deep Learning Basics Notions Notebooks ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.link_blue + s.bold, "HERE", link="https://www.dropbox.com/scl/fi/tmb88slx5mvwrhlmnqdoj/notions-240620-1816.zip?rlkey=yhfmgrww48a2k5gbi22yt6kak&dl=1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Might need some gentle programming skills to run on your computer ;) ")
    st_space(size=1)
    st_space(size=1)
