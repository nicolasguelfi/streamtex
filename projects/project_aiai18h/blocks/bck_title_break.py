import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    pass
bs = BlockStyles


def build():

    st_write(s.project.titles.title_green_01 + s.center_txt, 
             "Break", toc_lvl='2', tag=t.div)



