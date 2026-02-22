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
      #ff9900 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "4. Notebooks links ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.orange + s.bold, "NO MORE AVAILABLE AFTER TRAINING END ")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Learner01")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold, "link", link="http://5528a6eafb6b50b6-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner02")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6e2398bfcfe7f539-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner03")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7c7da03689cd9687-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner04")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7f9fc8cd9adc67cc-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner05")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://322334af4c467d5e-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner06")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://29252365cd3bb949-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner07")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://37c21b7b1e6bde34-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner08")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7b6e062bafaee614-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner09")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://4c6a3b9cea3f3f95-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner10")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://2db7895f0bd07c9b-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner11")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://26902fc424404160-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner12")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7d33f2003ded9842-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner13")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://4e98a1184fc7e593-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner14")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://475c82c9e1d1cbe8-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner15")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7047fc75d632ff81-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner16")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://aad02525b4d18b1-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner17")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6d09dfcfdfe8cb23-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner18")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://468938a3581a80b4-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner19")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://7635826f06f2eb3c-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner20")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6eb74ff6c47f228d-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner21")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6c8fd01bd5cfb8e2-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner22")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://1716f72f58204dd6-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner23")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://731f80861f210663-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner24")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://399cefc8abd36064-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.gold + s.bold, "Learner25")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6f8df63bc6f4a755-dot-us-west1.notebooks.googleusercontent.com")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
