import streamlit as st

# StreamTeX Block Imports
from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

# Project Specific Imports
from custom.styles import Styles as s


# URLs used in this block
PLAYGROUND_URL = "https://platform.openai.com/chat/edit?models=gpt-5"
PRICING_URL = "https://platform.openai.com/docs/pricing"
TRAINERS_TOOL_URL = "https://huggingface.co/spaces/university-luxembourg/aiaiapps"
CHATGPT_URL = "https://chatgpt.com"
DEEPSEEK_URL = "https://chat.deepseek.com/"
COPILOT_URL = "https://copilot.microsoft.com"
PERPLEXITY_URL = "http://www.perplexity.ai"
CLAUDE_URL = "https://claude.ai/"
VERCEL_PLAYGROUND_URL = "https://sdk.vercel.ai/playground"
OPENROUTER_URL = "https://openrouter.ai/chat?room=orc-1761753817-kvyfT4CtleoHHRbCdtE8"


class BlockStyles:
    """
    Local styling for the text generation showcase block.

    Color-mapping summary (from HTML export):
    - .c31, links: #1155cc -> s.project.colors.denim_blue
    - .c22 (DeepSeek): #073763 -> s.project.colors.dark_blue
    - .c28 (ChatGPT, perplexity): #b45f06 -> s.project.colors.orange_accent
    - .c18 (CoPilot, claude): #980000 -> s.project.colors.dark_red
    - .c42 (Trainers): #ff0000 -> s.project.colors.bright_red
    - .c30, .c26, .c35 (green): #274e13 -> s.project.colors.dark_green
    - .c20, .c6, .c43 (brown): #783f04 -> s.project.colors.brown
    - .c11 (VERCEL, openrouter): #20124d -> s.project.colors.dark_purple
    - #000000 (default body text): theme-controlled, not migrated
    """

    # Title: blue, 72pt, bold
    title = s.project.colors.denim_blue + s.bold + s.huge + s.text.decors.decor_none_text

    # Link style for "link" text and inline links (include font size to match surrounding text)
    link_style = s.project.colors.denim_blue + s.text.decors.underline_text + s.Large

    # Topic bullets: brown/green, bold, Large
    bullet_brown = s.project.colors.brown + s.bold + s.Large
    bullet_green = s.project.colors.dark_green + s.bold + s.Large

    # Table cell styling
    cell_style = (
        s.container.borders.solid_border
        + s.container.paddings.small_padding
        + s.center_txt
        + s.container.layouts.vertical_center_layout
    )
    style_fixed_table = Style("table-layout: fixed; width: 100%; border-collapse: collapse;")

    # Tool table: header styles by color
    tool_red = s.project.colors.bright_red + s.bold + s.LARGE
    tool_orange = s.project.colors.orange_accent + s.bold + s.LARGE
    tool_dark_blue = s.project.colors.dark_blue + s.bold + s.Large
    tool_dark_red = s.project.colors.dark_red + s.bold + s.Large
    demo_caption = s.italic + s.LARGE


bs = BlockStyles


def build():
    """Show text generation tools and resources with links."""
    with st_block(s.center_txt):
        st_write(bs.title, "Text Generation", toc_lvl="1")

    st_space(size=4)

    # Hero image
    st_image(uri="bck_showcase_text_generation_all_image_001.png")
    st_space(size=4)

    # Two-column table: Topics | Resources
    with st_grid(
        cols=2,
        grid_style=bs.style_fixed_table,
        cell_styles=bs.cell_style,
    ) as g:
        with g.cell():
            with st_list(lt.unordered, li_style=bs.bullet_brown) as lst:
                with lst.item():
                    st_write(bs.bullet_brown, "Reasoning / non-Reasoning ??")
                with lst.item():
                    st_write(bs.bullet_green, "Deep Research ??")
                with lst.item():
                    st_write(bs.bullet_brown, "Agents ??")
        with g.cell():
            with st_list(lt.unordered, li_style=s.Large) as lst:
                with lst.item():
                    st_write(s.Large, (bs.link_style, "Playground", PLAYGROUND_URL), (s.bold, " ??"))
                with lst.item():
                    st_write(s.Large, (bs.link_style, "Pricing", PRICING_URL), (s.bold, " ??"))
                with lst.item():
                    st_write(bs.bullet_green, "Prompt Engineering ??")
                with lst.item():
                    st_write(bs.bullet_brown, "Specialized GPTs ??")

    st_space(size=4)

    # Tools table: Name | link
    with st_grid(
        cols="4fr 1fr",
        grid_style=bs.style_fixed_table,
        cell_styles=bs.cell_style,
    ) as g:
        with g.cell():
            st_write(bs.tool_red, "Trainers tool")
        with g.cell():
            st_write(bs.link_style, "link", link=TRAINERS_TOOL_URL)

        with g.cell():
            st_write(bs.tool_orange, "OpenAI ChatGPT")
        with g.cell():
            st_write(bs.link_style, "link", link=CHATGPT_URL)

        with g.cell():
            st_write(bs.tool_dark_blue, "DeepSeek")
        with g.cell():
            st_write(bs.link_style, "link", link=DEEPSEEK_URL)

        with g.cell():
            st_write(bs.tool_dark_red, "Microsoft CoPilot")
        with g.cell():
            st_write(bs.link_style, "link", link=COPILOT_URL)

        with g.cell():
            st_write(bs.tool_orange, "perplexity.ai")
        with g.cell():
            st_write(bs.link_style, "link", link=PERPLEXITY_URL)

        with g.cell():
            st_write(bs.tool_dark_red, "claude.ai")
        with g.cell():
            st_write(bs.link_style, "link", link=CLAUDE_URL)

        with g.cell():
            st_write(
                s.bold + s.LARGE,
                (s.project.colors.dark_purple + s.bold + s.LARGE, "VERCEL"),
                (s.project.colors.dark_green + s.bold + s.LARGE, " chat models comparison"),
                tag=t.div,
            )
            st_write(bs.demo_caption, "for demo by NG: nicolas.guelfi@ros.lu", tag=t.div)
        with g.cell():
            st_write(bs.link_style, "link", link=VERCEL_PLAYGROUND_URL)

        with g.cell():
            st_write(
                s.bold + s.LARGE,
                (s.project.colors.dark_purple + s.bold + s.LARGE, "openrouter"),
                (s.project.colors.dark_green + s.bold + s.LARGE, " chat models comparison"),
                tag=t.div,
            )
            st_write(bs.demo_caption, "for demo by NG: nicolas.guelfi@bics.lu", tag=t.div)
        with g.cell():
            st_write(bs.link_style, "link", link=OPENROUTER_URL)
