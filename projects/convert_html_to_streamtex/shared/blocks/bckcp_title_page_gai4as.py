import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #85200c -> s.project.colors.deep_red
      #990000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=2)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=2)
    st_write(
        s.project.doc.paragraphs.p_lg,
        (s.project.colors.forest_green + s.bold + s.italic, "G"),
        (s.project.colors.burnt_orange + s.bold + s.italic, "AI"),
        (s.project.colors.dark_purple + s.bold + s.italic, "4"),
        (s.project.colors.navy_blue + s.bold + s.italic, "AS"),
    )
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.olive_green + s.bold, "COURSEPACK ")
    st_space(size=2)
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.gold + s.bold + s.italic, "Utilisation Pratique de l' "),
        (s.project.colors.burnt_orange + s.bold + s.italic, "IA"),
        (s.project.colors.gold + s.bold + s.italic, " "),
        (s.project.colors.forest_green + s.bold + s.italic, "G"),
        (s.project.colors.gold + s.bold + s.italic, "énérative"),
        (s.project.colors.bright_red + s.bold + s.italic, " pour les "),
        (s.project.colors.dark_purple + s.bold + s.italic, "Services "),
        (s.project.colors.navy_blue + s.bold + s.italic, "A"),
        (s.project.colors.dark_purple + s.bold + s.italic, "dministratifs et de "),
        (s.project.colors.navy_blue + s.bold + s.italic, "S"),
        (s.project.colors.dark_purple + s.bold + s.italic, "upport"),
    )
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.forest_green + s.bold + s.italic, "-")
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.gold + s.bold + s.italic, "Applied "),
        (s.project.colors.forest_green + s.bold + s.italic, "G"),
        (s.project.colors.gold + s.bold + s.italic, "enerative "),
        (s.project.colors.burnt_orange + s.bold + s.italic, "AI"),
    )
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.bright_red + s.bold + s.italic, "for "),
        (s.project.colors.navy_blue + s.bold + s.italic, "A"),
        (s.project.colors.dark_purple + s.bold + s.italic, "dministration "),
    )
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.dark_purple + s.bold + s.italic, "and "),
        (s.project.colors.navy_blue + s.bold + s.italic, "S"),
        (s.project.colors.dark_purple + s.bold + s.italic, "upport Services"),
    )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.link_blue + s.bold, "aiai.ros.lu", link="https://aiai.ros.lu")
    st_space(size=1)
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.bright_red + s.bold, " Confidential  ")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.bright_red + s.bold, "DO NOT DISTRIBUTE ")
    st_space(size=2)
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.deep_red + s.bold + s.italic, "NO EDIT RIGHTS CAN BE GRANTED ")
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.deep_red + s.bold + s.italic, "Thus please do not request them ;) ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
