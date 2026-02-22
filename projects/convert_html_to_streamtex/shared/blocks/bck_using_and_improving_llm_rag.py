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
      #274e13 -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #45818e -> s.project.colors.teal
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #e69137 -> s.project.colors.orange
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #c17aa0 (unmapped)
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "RAG"),
        (s.project.colors.purple, " for ChatBot Design "),
        tag=t.h1,
        toc_lvl="1",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Introduction ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "Retrieval Augmented Generation (RAG)")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "retrieve"),
                (s.project.colors.bright_red, " "),
                (s.project.colors.bright_red + s.bold, "relevant"),
                (s.bold, " information"),
                " from a knowledge base ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "combine"),
                " with default text generation ",
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Why is it important ? ", tag=t.h3)
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, "Hallucination")
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "2. Outdated information ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "3. Lack of knowledge in specialized domains ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "4. Too Large contexts(cost or accuracy) ")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://research.google/blog/titans-miras-helping-ai-have-long-term-memory/?utm_source=alphasignal&utm_campaign=2025-12-05&lid=19gWYCZkexaaOnZUS"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://arxiv.org/abs/2407.04841"),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "RAG is not just retrieval ! ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.teal + s.bold, "Need to orchestrate all interactions")
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Instructions ")
        with lst.item():
            st_write(s.project.colors.orange + s.bold, "Context")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "RAG is not just retrieval ! ", tag=t.h3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.burnt_orange, "it’s a full reasoning pipeline ", tag=t.h3)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.olive_green, "RAG reasoning starts with 2 pillars", tag=t.h3)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "RAG Architecture ", tag=t.h3)
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
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "RAG Engineering ", tag=t.h3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "", tag=t.h6)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=3)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Lots of moving parts to reach great performance ! ", tag=t.h6)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "RAG Benefits ", tag=t.h3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "Enhanced Relevance "), (s.project.colors.bright_red, "	Improved Quality "), (s.project.colors.dark_purple, "Versatility "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red, "Efficient Retrieval "), (s.project.colors.dark_purple, "Trust & Transparency "), (s.project.colors.bright_red, "Customization & Control "), (s.project.colors.dark_purple, "Cost-Effectiveness "))
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Applications ", tag=t.h3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.dark_purple, "Conversational AI "), (s.project.colors.bright_red, "	Fact Checking "), (s.project.colors.dark_purple, "Advanced Question Answering "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red, "Sentiment Analysis "), (s.project.colors.dark_purple, "Content Generation "), (s.project.colors.bright_red, "Code Generation"))
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "… and many others ")
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
