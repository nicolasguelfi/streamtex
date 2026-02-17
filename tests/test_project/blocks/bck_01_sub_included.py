import streamlit as st
from streamtex import *
import streamtex as sx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """Sub-included block styles."""
    content = s.large + s.project.colors.success_green
bs = BlockStyles


def build():
    st_write(BlockStyles.content,
             "This content comes from bck_01_sub_included.py,")
    st_br()
    st_write(BlockStyles.content, "rendered via st_include().")
