import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #434343 -> s.project.colors.gray
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.4.3. Practice - MNIST_Keras 2 ", tag=t.h3)
    st_space(size=1)
