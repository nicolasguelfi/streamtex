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
    st_write(s.project.doc.titles.h1, "5. Schedule ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
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
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Course Presentation")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Showcase")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "105")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Intuitive introduction to AI")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "150")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "DEEP LEARNING PART 1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "45")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "195")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/16/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentation & Start")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "30")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "225")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "285")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "300")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering - Practicals")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "390")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "390")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "9/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "480")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/13/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "495")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/13/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering - Practicals")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "585")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/13/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "585")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/13/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Context Engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "675")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "690")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Context Engineering - Practicals")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "780")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "780")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "10/30/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentations & Discussions")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "100")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "880")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/10/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:40PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "895")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/10/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentations & Discussions - ctnd")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "955")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/10/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "975")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/10/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "975")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/10/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt & Context Engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1065")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/24/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1080")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/24/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt & Context Engineering - Practicals")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "75")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1155")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/24/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1155")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "11/24/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1245")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/1/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:30PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1260")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/1/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Prompt Engineering - Practicals")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:45PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "90")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1350")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/1/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "7")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1350")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/1/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentations & Discussions")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "2:00PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "100")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1450")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/15/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "break")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:40PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1465")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/15/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Presentations & Discussions - ctnd")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "3:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "60")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1525")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/15/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "Projects Q/A")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "4:55PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1545")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/15/2025")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "8")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "SESSION END")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "5:15PM")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "0")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "1545")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "12/15/2025")
    st_space(size=1)
    st_space(size=1)
