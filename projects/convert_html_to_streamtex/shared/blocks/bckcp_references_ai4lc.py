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
    st_write(s.project.doc.titles.h1, "5. References ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "You can find here other reference files related to the course..")
    st_write(s.project.doc.paragraphs.p_body, "Professor's slides will be uploaded here after the training.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "Training Drive Folder", link="https://drive.google.com/drive/folders/1xeiAZd--2v_1GJI3EyOkYgHrdIYEBJjF?usp=sharing")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
