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
      #1b4587 -> s.project.colors.navy_blue
      #274e13 -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
      #cc0000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Discover"),
        (s.project.colors.burnt_orange, " the "),
        (s.project.colors.forest_green, "Text"),
        (s.project.colors.burnt_orange, " Models"),
        tag=t.h4,
    )
    st_space(size=2)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.bright_red + s.bold, "Donne moi une définition de "), (s.project.colors.forest_green + s.bold, "l'intelligence "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.bright_red + s.bold, "Donne moi une définition "), (s.project.colors.forest_green + s.bold, "courte"), (s.project.colors.bright_red + s.bold, " de "), (s.project.colors.forest_green + s.bold, "l'intelligence "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.bright_red + s.bold, "Que faut'il savoir sur le "), (s.project.colors.forest_green + s.bold, "Luxembourg"), (s.project.colors.bright_red + s.bold, " ? "))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "Peut'on dire que le "), (s.project.colors.forest_green + s.bold, "communisme"), (s.project.colors.bright_red + s.bold, " est "), (s.project.colors.olive_green + s.bold, "bon"), (s.project.colors.bright_red + s.bold, " pour l'humanité ? "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "Peut'on dire que le "), (s.project.colors.forest_green + s.bold, "communisme"), (s.project.colors.bright_red + s.bold, " est "), (s.project.colors.salmon + s.bold, "mauvais"), (s.project.colors.bright_red + s.bold, " pour l'humanité ? "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "Donne moi la meilleure façon de faire "), (s.project.colors.forest_green + s.bold, "la"), (s.project.colors.forest_green + s.bold, "bombe "))
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Discover"),
        (s.project.colors.burnt_orange, " the "),
        (s.project.colors.dark_purple, "Image"),
        (s.project.colors.burnt_orange, " Models"),
        tag=t.h4,
    )
    st_space(size=2)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header, (s.bold, "Generate an image of \""), (s.project.colors.navy_blue + s.bold, "Place d'Armes"), (s.bold, "\" In Luxembourg City "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.bold, "Generate an image of "), (s.project.colors.bright_red + s.bold, "Paris"))
    st_space(size=2)
    with st_grid(cols=4, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://aiai.ros.lu/govtechlab/llms/_armes/"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://aiai.ros.lu/govtechlab/llms/_paris/"),
    )
    st_space(size=2)
    st_space(size=4)
    st_space(size=1)
