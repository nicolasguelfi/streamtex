import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #7f6000 -> s.project.colors.gold
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "5. Schedule ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    with st_grid(cols=6, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "week")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "content")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Start time")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Duration")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "TIMER")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Date")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Group Discovery")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Content")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up COMPUTERS")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase & Playground")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Ethics")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering Practice")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.gold + s.bold, "Interactive Mini-Workshop "), (s.project.colors.gold + s.bold, "on AI & Ethics"))
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & Society")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/28/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.bright_red + s.bold, "Interactive Mini-Workshop "), (s.project.colors.bright_red + s.bold, "on AI & Society (& Ethics)"))
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/29/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "DLH Training Survey")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "205")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/29/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wrap-up discussion")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/29/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/29/2024")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
