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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "10.4. RESNET Transfer Learning ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heatont81_558_class_06_3_resnet.ipynb ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "fastaiBook - Chapter 14, Resnet ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "link", "https://course.fast.ai/"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/fastai/fastbook"))
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
