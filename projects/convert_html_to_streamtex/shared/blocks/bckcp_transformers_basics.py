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
    st_write(s.project.doc.titles.h2, "5.7. Transformers ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "3b1b - 3blue 1brown great explanation videos on deep learning ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=LPZh9BOjkQs&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi&index=5")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Visualize Completion ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://poloclub.github.io/transformer-explainer/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Visualize Tokenization ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://tokenvisualizer.netlify.app/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Visualize Embeddings ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://projector.tensorflow.org/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Compare existing LLM results ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://sdk.vercel.ai/playground")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Illustrated Guide to Transformers Neural Network: A step by step explanation ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=4Bdc55j80l8")
        with g.cell():
            st_write(s.project.doc.tables.cell, "All you need to know about ‘Attention’ and ‘Transformers’ — In-depth Understanding — Part 1 ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://towardsdatascience.com/all-you-need-to-know-about-attention-and-transformers-in-depth-understanding-part-1-552f0b41d021#8607")
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
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://poloclub.github.io/transformer-explainer/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
