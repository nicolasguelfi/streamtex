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
      #434343 -> s.project.colors.gray
      #666666 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h2, "8.3. Learning AI technical tools ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.3.1. Python ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.3.1.1. main source ", tag=t.h4)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heatont81_558_class_01_2_intro_python.ipynb ", "t81_558_class_01_3_python_collections.ipynb ", "t81_558_class_01_4_python_files.ipynb ", "t81_558_class_01_5_python_functional.ipynb ", "t81_558_class_02_1_python_pandas.ipynb ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.3.1.2. other sources ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "The Python tutorial ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://docs.python.org/3/tutorial/index.html")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Online interactive learning tool ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.learnpython.org/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.3.2. Jupyter Notebooks and Google Colab ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to Jupyter Notebooks")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://docs.jupyter.org/en/latest/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Overview of Google Colaboratory Features ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://colab.research.google.com/drive/16pBJQePbqkz3QFV54L4NIkOn1kwpuRrj")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.3.3. Various ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff HeatonExcellent source of information for any topic related to Artificial Intelligence and data science ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "videos", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff HeatonT81 559:Applications of Generative Artificial Intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/jeffheaton/app_generative_ai")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
