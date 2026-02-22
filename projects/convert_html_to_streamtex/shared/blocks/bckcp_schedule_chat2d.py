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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "5. Schedule ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    with st_grid(cols=7, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Session")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Step")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Game Title")
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
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Group Discovery")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Content")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "6:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "6:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up the computers")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "8:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING - Part 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "8:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "220")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/19/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING - Part 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Ethics & Society")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "6:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Generative AI Workshop")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session Survey")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "8:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "220")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/20/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Setting up computers ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell, "15 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 1 - LANGCHAIN Basics")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "6:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "135")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 2 - CHAINS")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "225")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "285")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/21/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 3 - RETRIEVAL&MEMORY")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 4 - MICHELINE RAGBOT")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "7:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.gold + s.bold, "DLH Training Survey "), (s.project.colors.gold + s.bold, "& Session Survey"))
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "8:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "11")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "220")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "12")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:10PM")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "220")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "13")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:10PM")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "220")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "14")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:10PM")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:10PM")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3/22/2024")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
