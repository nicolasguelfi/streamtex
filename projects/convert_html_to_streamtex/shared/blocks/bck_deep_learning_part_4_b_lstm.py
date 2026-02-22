import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #2f5a1b -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #731b47 -> s.project.colors.dark_purple
      #7f6000 -> s.project.colors.gold
      #b45f06 -> s.project.colors.burnt_orange
      #ff9900 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "LSTM - Long Short-Term Memory ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://youtu.be/YCzL96nL7j0?si=YuNY5jJvVNEiQz_n"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.youtube.com/watch?v=8HyCNIVRbSU"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.pluralsight.com/guides/introduction-to-lstm-units-in-rnn"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://link.springer.com/chapter/10.1007/978-3-030-14524-8_11"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "sequence of information ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "when future depends on pasts ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.orange + s.bold, "Input ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.orange + s.bold, "Output ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green, "\"1,2,3\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green, "4 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green, "\"2,4,8,16\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green, "32 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.teal, "\"I love this training and life is beautiful\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "sentiment = "), (s.project.colors.teal, "\"happy\" "))
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.teal, "\"I love this training but I know it will stop one day\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "sentiment = "), (s.project.colors.teal, "\"sad\" "))
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold, "C'est un beau temps  ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold, "It's a beautiful weather  ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold, "C'est un beau temps de parcours ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold, "It's a nice ride ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange, "“I grew up in France,I speak fluent ... \" ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange, "\"French\" ")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Architecture ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(details in a future training?) ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Forget gate -> Input gate -> Output gate ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
