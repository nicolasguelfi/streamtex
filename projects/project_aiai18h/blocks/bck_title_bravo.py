import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    pass
bs = BlockStyles


def build():

    st_write(s.bold + s.Huge + s.project.colors.orange_03 + s.center_txt,
             "BRAVO !", label="bravo", tag=t.div)


