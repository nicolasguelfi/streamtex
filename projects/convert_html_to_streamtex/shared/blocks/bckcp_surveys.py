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
      #7f6000 -> s.project.colors.gold
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "6. Surveys ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.1. Surveys to fill links ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Game - Access to resources")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & Open in Private Window!", link="https://docs.google.com/forms/d/e/1FAIpQLSe2Ot8ImerQhvDYqBuUMQFUZdnBhLenY6dWiFCXiU5N6I0qzw/viewform")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Jeu - présentation individuelle")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & Open in Private Window!", link="https://docs.google.com/forms/d/e/1FAIpQLScl5M6-u2lykUAxh_DRZAxuIvUewTSOUTNmpMBOpzvJ-AbvvA/viewform")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.2. Survey Results Links ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Game - Access to resources")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/1zn5_LrLKJscrTs3-VDa0zo0L8lGvU0kVosWsiUPfI-E/viewanalytics")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Jeu - présentation individuelle")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/19ZRyIZBMyZAq5EL0P09M0OCEQou719JWeVHEQ6Vdjn0/viewanalytics")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "-")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.3. DLH Training Survey ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.link_blue + s.bold, "HERE", link="   https://www.dlh.lu/survey/start/40092ab5-6fcb-45ae-9031-e1201a82d930")
    st_space(size=2)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_space(size=1)
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
