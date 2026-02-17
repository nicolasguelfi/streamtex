import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    pass
bs = BlockStyles


def build():

    st_write("This text is in a different block, but is being included in another block using st_include().")



