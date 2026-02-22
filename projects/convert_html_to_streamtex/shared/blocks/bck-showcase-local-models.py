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
      #188037 -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
    Dropped colors:
      #87ff01
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Local Models ", tag=t.h1, toc_lvl="1")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "WARNING", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "Requires a powerful computer  ")
    st_write(s.project.pres.paragraphs.p_xl, "<=>  ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange, "$$$$$$$$ ")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "lmstudio ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://lmstudio.ai/")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "calme 78B ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://huggingface.co/MaziyarPanahi/calme-3.2-instruct-78b")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "advanced iteration of ",
        (s.project.colors.olive_green, "Qwen/Qwen2.5-72B "),
    )
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "lmstudio demo ", tag=t.h5)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
