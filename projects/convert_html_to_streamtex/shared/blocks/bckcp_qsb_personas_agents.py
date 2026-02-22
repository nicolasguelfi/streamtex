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
      #674ea7 -> s.project.colors.purple
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=2)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "7. Quasible Agents & Personas ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "You can access online demo Quasible Agents ")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "AI Persona Expert ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/ar8zsxa7foneatcr4xjys401")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.bright_red + s.bold, "AI Prompt Expert ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/embed/defy4fgwljsnya4lvp9und5a")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Quasible Documentation AgentAG_QuasiDoc ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/owh21delrcwqxsgeqvm1q6ri")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Quasible Documentation AgentAG_QuasiDoc_FastAndFurious ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/h18hdd8gzge55z3crl0kqcy5")
        with g.cell():
            st_write(s.project.doc.tables.cell, "AG_Language_Expert ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/tj9s2rklhad8y7qnxjr8b5p2")
        with g.cell():
            st_write(s.project.doc.tables.cell, "AG_Multi_Formatter ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/ymfkbsxgeufntawnt23ihwwj")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LC_01_AG_PSN_Résumé_Documentaire ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://app.quasible.ai/en/embed/iz0o1aix6jsf9lvzcyhx3lzj")
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
    st_write(s.project.doc.titles.h1, "6. Quasible Input Data ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.1. Source files ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_lg,
        "You can access raw data for agents ",
        (s.project.doc.links.link_lg + s.project.colors.link_blue + s.bold, "HERE", "https://drive.google.com/drive/folders/1nhIIju4cYtKBo0m4_ss9km8hqPy3MV0D?usp=sharing"),
    )
