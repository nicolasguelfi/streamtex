import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    pass
bs = BlockStyles

def build():

    st_write(s.center_txt + s.bold + s.GIANT + s.project.colors.red_01,"GO!", tag=t.div)
    st_image(uri="savana_race_01.png")


