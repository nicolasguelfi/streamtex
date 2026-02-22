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
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Speech ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "Whisper", link="https://openai.com/research/whisper")
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue, "_", link="https://aiai.ros.lu/data/audio/openai-whisper-en-text-to-fr-audio.mp3")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
