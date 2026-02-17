import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    border = s.container.borders.color(s.text.colors.black) + s.container.borders.solid_border + s.container.borders.size("2px")
bs = BlockStyles

def build(
    gpt_image="chat_gpt_sample_01_en.png",
    llm_symbol="llm_symbolism.png",
    bear_gif_1="bear_walking_01.gif",
    bear_gif_2="bear_walking_02.gif",
    bear_gif_3="bear_walking_03.gif",
    deep_fake_gif="showcase_deep_fake_01.gif"
    ):
    
    with st_grid(2, cell_styles= bs.border + s.container.paddings.little_padding + s.container.layouts.vertical_center_layout) as g:
        # First Row
        with g.cell(): st_image(uri = gpt_image)
        with g.cell(): st_image(uri = llm_symbol)
        # Second Row
        with g.cell():
            with st_grid(3, cell_styles= s.container.paddings.small_padding) as gg:
                with gg.cell(): st_image(uri = bear_gif_1)
                with gg.cell(): st_image(uri = bear_gif_2)
                with gg.cell(): st_image(uri = bear_gif_3)
            st_write(s.text.alignments.center_align+s.text.sizes.Large_size,
                    (ns("color: #274e13;"), "prompt"), " + snow + ", (ns("color: #660000;"), "cartoon"),
                    tag=t.div)
        with g.cell(): st_image(uri = deep_fake_gif)
        # Third Row
        with g.cell(): st_image(uri = "showcase_dl_maths_01.gif")
        with g.cell(): st_image(s.container.sizes.height_auto, uri = "showcase_dl_maths_02.gif")



