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
    st_space(size=1)
    with st_grid(cols=6, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Session")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Content")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:30AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up the computers")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:30AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING - Part 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING - Part 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Ethics & Society")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "135")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Generative AI Workshop")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2024")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 1 - 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LLM PART 3 - 4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up computers")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Mini Project Part 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Mini Project Part 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Mini Project Debriefing")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Introduction to Wordpress")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "35")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress main components")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:35AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "80")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:20AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "95")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:35AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "85")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress AI Plugins")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "BREAK")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "MYWOP Project Start")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Tools Setup")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 3 - PART 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:20AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "80")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "BREAK")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:20AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "95")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 3 - PART 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:35AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "85")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 4 - PART 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "BREAK")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 4 - PART 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Demo / Wrap-up")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 5 - PART 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "BREAK")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wordpress Practical - Session 5 - PART 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Demos / Wrap-up")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:30AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "9")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SetUp LearnersChatBots Access")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "ChatBots Demos + QA")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "135")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "BREAK")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "TrainingChatBots WP Demo")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Q/A")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "210")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Surveys")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "225")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "TRAINING END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "225")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/13/2024")
    st_space(size=1)
    st_space(size=1)
