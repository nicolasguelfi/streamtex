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
      #6aa84f -> s.project.colors.light_green
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Speech ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "Whisper", "https://openai.com/research/whisper"),
        ", ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "Revoicer", "https://revoicer.com"),
        ", ... ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/1npHlLoNC4qA1PNMDE-VmuBk_165anr7f/view?usp=sharing"), (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://aiai.ros.lu/data/audio/openai-whisper-en-text-to-fr-audio.mp3"))
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "fal-ai ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.link_blue, "_", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://drive.google.com/file/d/1LHorAt7QXdBbzs0XRm6TsWWBd-9a1fbD/view?usp=sharing")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "notebookLM ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.link_blue, "_", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.light_green, "Podcast Generation ", tag=t.h4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/101UbzIQM6RtL_VznX7nwF2woGGHYaTuD/view?usp=sharing"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/10E3Q_JGPl9H2cNs71omQZEoHa9QAMNaS/view?usp=sharing"),
        tag=t.h4,
    )
    st_space(size=1)
    st_space(size=1)
