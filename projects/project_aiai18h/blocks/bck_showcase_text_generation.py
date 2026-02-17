import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    """Custom styles defined locally and used only for this block"""
    blue_title = s.project.colors.blue_01 + s.huge + s.center_txt + s.bold
    lime_bullet = s.text.colors.lime + s.bold
    brown_bold_title = s.project.colors.brown_01 + s.bold + s.LARGE

    red_bold_title = s.project.colors.red_01 + s.bold + s.large
    red_bold_title = s.project.colors.red_01 + s.bold + s.large

    table_cell_style = s.center_txt
    link_style = s.text.colors.blue + s.text.decors.underline_text

    side_padding = ns("padding: 10pt 36pt;")
    
    border = s.container.borders.color(s.text.colors.black) + s.container.borders.solid_border + s.container.borders.size("2px")
bs = BlockStyles


def build():
    # Section Header: Text Generation
    st_write(bs.blue_title, "Text Generation", toc_lvl="2", tag=t.div)
    st_space(size=3)

    # Image Block
    with st_list(lt.unordered, li_style=s.center_txt) as l:
        with l.item(): st_image(uri="gpt_text_generation_01.png", link="https://chat.openai.com")
    st_space(size=10)

    # Table: Chat Models and Links
    with st_grid("1fr auto",
        cell_styles=sg.create("A1,A3,A5", s.project.colors.orange_02) +\
                    sg.create("A2,A4", s.project.colors.red_01) +\
                    sg.create("A1:B5", s.bold + s.LARGE + bs.side_padding + s.center_txt + bs.border) +\
                    sg.create("B1:B5", s.Large)
        ) as g:
        with g.cell(): st_write("OpenAI ChatGPT")
        with g.cell(): st_write("link", link="https://www.datacamp.com/blog/yolo-object-detection-explained")
        
        with g.cell(): st_write("Microsoft CoPilot")
        with g.cell(): st_write("link", link="https://copilot.microsoft.com")
        
        with g.cell(): st_write("perplexity.ai"),
        with g.cell(): st_write("link", link="http://www.perplexity.ai")
        
        with g.cell(): st_write("claude.ai")
        with g.cell(): st_write("link", link="https://claude.ai/")
        
        with g.cell(): st_write("Various chat models comparison")
        with g.cell(): st_write("link", link="https://sdk.vercel.ai/")

        
    st_space(size=5)