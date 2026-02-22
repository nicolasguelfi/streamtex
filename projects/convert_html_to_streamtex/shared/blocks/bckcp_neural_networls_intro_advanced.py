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
      #674ea7 -> s.project.colors.purple
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.3. Neural networks ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "9.3.1. Main General Information Sources ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.bright_red + s.bold, "StatQuest"), " exceptional  video and material ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=zxagGtF9MeU&list=PLblh5JKOoLUIxGDQs4LFFD--41Vzf-ME1")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.bright_red + s.bold, "3b1b"), "exceptional  video and material ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.bright_red + s.bold, "Serano Academy"), "exceptional  video and material ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/@SerranoAcademy/playlists")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.bright_red + s.bold, "Jeff Heaton"), "exceptional  video and material ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/@HeatonResearch")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "9.3.2. Basic concepts ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heatont81_558_class_03_1_neural_net.ipynbt81_558_class_03_5_weights.ipynb ", "t81_558_class_04_3_regression.ipynb ", "t81_558_class_04_4_backprop.ipynb ", "t81_558_class_04_5_rmse_logloss.ipynb ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heaton ", "To understand step by step the calculations in a neural network ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/playlist?list=PLC112AD1C69432FDB")
        with g.cell():
            st_write(s.project.doc.tables.cell, "fastai ", "Course 3: Neural net foundations ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "link", "https://course.fast.ai/"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://course.fast.ai/Resources/book.html"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "bias ", "Understanding the different usage of the term 'bias' ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.wovenware.com/blog/2020/07/in-machine-learning-bias-bias-and-bias-are-three-different-things/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "9.3.3. Learning ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Intuitive animated introduction ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.3blue1brown.com/topics/neural-networks")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heatont81_558_class_03_1_neural_net.ipynb ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "fastai ", "Book - Chapter 4, MNIST Basics ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "link", "https://course.fast.ai/"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/fastai/fastbook"))
    st_space(size=1)
    st_space(size=1)
