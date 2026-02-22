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
      #2f5a1b -> s.project.colors.forest_green
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Transfer Learning ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.datacamp.com/tutorial/transfer-learning")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.researchgate.net/publication/338540456_Basics_of_Deep_Learning_A_Radiologist%27s_Guide_to_Understanding_Published_Radiology_Articles_on_Deep_Learning")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "ResNet ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.navy_blue + s.italic, "Residual Networks (ResNet) ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Neural network trained for optimal image recognition ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Won the ImageNet classification challenge in 2015 ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Problem ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "In deepness gradients can become useless ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.geeksforgeeks.org/residual-networks-resnet-deep-learning/")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Solution ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Skip blocks  of degrading layers  ")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Resnet Architecture ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
