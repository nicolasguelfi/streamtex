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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Content")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase GAI4AS")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "135")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up the computers")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Quasible - Overview")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Quasible - Setting Up")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Practice Session 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "165")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wrap-up")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/5/2025")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI & DEEP LEARNING")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Using & Specializing LLMs")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "AI Agents Process")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:30AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "240")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Setting up the computers")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Project - Overview")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Project Session 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Project Session 2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "165")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Wrap-up")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/12/2025")
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Ethics & Society")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9:15AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10:45AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Project Session 3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11:00AM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "LUNCH")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "120")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Session introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Project Session 3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "1:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Projects Demonstrations")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "165")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "DLH Training Survey")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "175")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Training Closure")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "180")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/19/2025")
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
