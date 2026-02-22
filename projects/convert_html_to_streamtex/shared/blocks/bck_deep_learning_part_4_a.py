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
      #2f5a1b -> s.project.colors.forest_green
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "DEEP LEARNING PART 4 ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=5)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "GAN"),
        (s.project.colors.forest_green, " - Generative Adversarial Network "),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Showcase ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Image Generation ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Text-Guided Image Modification  ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Pizza Manipulation ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Anime Characters Generation ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://utorontomist.medium.com/creating-anime-characters-with-generative-adversarial-networks-865281f13cb8")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Image Colorization ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Image Restoration ", tag=t.h4)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Image Animation ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "GAN Approach ", tag=t.h3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Architecture ", tag=t.h3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Generator ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Discriminator ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Results for Digits Generation ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "2 EPOCHS ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "1000 EPOCHS ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "2 to 1000 EPOCHS ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
