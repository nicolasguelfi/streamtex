import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    pass
bs = BlockStyles


def build():
    st_write(s.large + s.project.colors.accent,
             "This text lives in a separate block file, "
             "included via st_include().")
