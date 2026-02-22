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
    st_write(s.project.doc.titles.h2, "10.6. LSTM - Long Short-Term Memory ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "StatsQuest ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://youtu.be/YCzL96nL7j0?si=YuNY5jJvVNEiQz_n")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Jeff Heatont81_558_class_10_2_lstm.ipynb ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/playlist?list=PLjy4p-07OYzulelvJ5KVaT2pDlxivl_BN"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "code", "https://github.com/jeffheaton/t81_558_deep_learning"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "Understanding LSTM Networks ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://colah.github.io/posts/2015-08-Understanding-LSTMs/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Dissecting LSTMs ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://jaketae.github.io/study/dissecting-lstm/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Illustrated Guide to LSTM's: A step by step explanation ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "video", "https://www.youtube.com/watch?v=8HyCNIVRbSU"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "text", "https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21"))
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to LSTM Units in RNN ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "text", link="https://www.pluralsight.com/guides/introduction-to-lstm-units-in-rnn")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
