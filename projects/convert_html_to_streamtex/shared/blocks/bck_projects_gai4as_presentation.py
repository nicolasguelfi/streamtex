import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0000ff -> s.project.colors.link_blue
      #1155cc -> s.project.colors.link_blue
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "GAI4AS Project"),
        (s.project.colors.olive_green, "Presentation "),
        tag=t.h3,
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "Subjects in COURESPACK", link="https://docs.google.com/document/d/15TaOGPMeEMkox_beICZdaJVSYXJJfjIVvCsqqW6oPjk/edit#heading=h.w72q51o6zgbm")
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_space(size=4)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "tot")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.link_blue + s.bold, "Sub-Domain")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "37")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Support administratif")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "35")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Communication interne")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "34")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Communication Interne")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "32")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Stratégie d’entreprise")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "31")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Gestion des agendas")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "31")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Traitement du courrier")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Gestion des contrats")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Gestion des outils bureautiques")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Gestion documentaire")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Communication Externe")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Rédaction et gestion des contrats")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "30")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Campagnes promotionnelles")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "29")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Développement de l’activité")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "28")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Coordination des Événements")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "28")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Développement des compétences")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "27")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Coordination interservices")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
