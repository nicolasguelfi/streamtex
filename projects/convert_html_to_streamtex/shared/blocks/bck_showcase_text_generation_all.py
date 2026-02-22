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
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Text Generation ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.burnt_orange + s.bold, "Reasoning / non-Reasoning ??"), (s.project.colors.forest_green + s.bold, "Deep Research ??"), (s.project.colors.burnt_orange + s.bold, "Agents  ?? "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Playground", "https://platform.openai.com/chat/edit?models=gpt-5"), (s.bold, " ?? "), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Pricing", "https://platform.openai.com/docs/pricing"), (s.bold, " ??"), (s.project.colors.forest_green + s.bold, "Prompt Engineering ??"), (s.project.colors.burnt_orange + s.bold, "Specialized GPTs ?? "))
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "Trainers tool ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://huggingface.co/spaces/university-luxembourg/aiaiapps")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange, "OpenAI ChatGPT ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chatgpt.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.navy_blue, "DeepSeek ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.deepseek.com/")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "Microsoft CoPilot ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://copilot.microsoft.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange, "perplexity.ai ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://www.perplexity.ai")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red, "claude.ai ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://claude.ai/")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "VERCEL"), (s.project.colors.forest_green, " chat models comparison"), (s.italic, "for demo by NG:nicolas.guelfi@ros.lu "))
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://sdk.vercel.ai/playground")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "openrouter"), (s.project.colors.forest_green, " chat models comparison"), (s.italic, "for demo by NG:nicolas.guelfi@bics.lu"))
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://openrouter.ai/chat?room=orc-1761753817-kvyfT4CtleoHHRbCdtE8")
    st_space(size=3)
    st_space(size=1)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
