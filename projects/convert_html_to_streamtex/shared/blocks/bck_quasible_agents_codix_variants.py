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
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Codix Dissected ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "_ ")
    st_space(size=5)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://app.quasible.ai/en/agents/v095e2a9ostisbvqe1g0x8o7")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini A", "https://app.quasible.ai/embed/pggsoabtuadck0txvzwpk5i8"),
        (s.bold, "Codix Mini Mistral (Magistral Medium)"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini B", "https://app.quasible.ai/en/embed/xmg753az8rrrfvbx3toi9l95"),
        (s.bold, "Codix Mini Mistral (Mistral Large)"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini C", "https://app.quasible.ai/en/embed/n9mhg6h1rnolvvs9e3b0wfol"),
        (s.bold, "Codix Mini GPT5"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini D", "https://app.quasible.ai/en/embed/rgecg3mvlyn43v52xdnfy8oa"),
        (s.bold, "Codix Mini Gemini (2.5 Flash)"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini E", "https://app.quasible.ai/en/embed/c0mw67pwxaat0e6qa6vm6xyp"),
        (s.bold, "Codix Gemini(Pro 2.5)"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Mini F", "https://app.quasible.ai/en/embed/sq59l2iz73hh40vs91rpw4jf"),
        (s.bold, "Codix Mini DeepSeek (Reasoner v3.1)"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Codix Full G", "https://app.quasible.ai/en/embed/v095e2a9ostisbvqe1g0x8o7"),
        (s.bold, "Codix FULL Mistral (Mistral Large)"),
    )
    st_space(size=2)
    st_space(size=1)
