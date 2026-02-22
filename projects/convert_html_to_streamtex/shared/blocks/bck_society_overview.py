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
    Dropped colors:
      #00ff00
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Society & AI ", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Employment ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Previous Evolutions ", tag=t.h4)
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/employment-by-economic-sector?stackMode=relative")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Forecasted Evolutions ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Simulations",
        (s.project.pres.links.link_lg, " ", "https://www.mckinsey.com/featured-insights/artificial-intelligence/notes-from-the-ai-frontier-modeling-the-impact-of-ai-on-the-world-economy"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "show", "https://www.mckinsey.com/featured-insights/artificial-intelligence/notes-from-the-ai-frontier-modeling-the-impact-of-ai-on-the-world-economy"),
        " that by 2030 about ",
        (s.project.colors.burnt_orange + s.bold, "70%"),
        (s.bold, " "),
        "of companies will have ",
        (s.bold, "adopted"),
        " some sort ",
        (s.bold, "of AI technology "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "By Sector or Country ", tag=t.h5)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.pwc.co.uk/services/economics/insights/the-impact-of-automation-on-jobs.html")
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.pwc.co.uk/services/economics/insights/the-impact-of-automation-on-jobs.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.pwc.co.uk/services/economics/insights/the-impact-of-automation-on-jobs.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
