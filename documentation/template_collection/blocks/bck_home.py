"""Home page block for the collection hub."""

import streamlit as st
from streamtex import *
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Styles for the collection home page."""

    heading = s.project.titles.main_title + s.center_txt
    subtitle = Style(
        "font-size:1.4rem;opacity:0.7;text-align:center;",
        "home_subtitle",
    )
    card = Style(
        "background:rgba(40,44,52,0.8);border-radius:12px;padding:24px;"
        "border:1px solid rgba(255,255,255,0.08);",
        "project_card",
    )


bs = BlockStyles


def build():
    """Render the collection home page."""

    st_space("v", 3)

    st_write(bs.heading, "My Collection", tag=t.h1)
    st_space("v", 1)
    st_write(bs.subtitle, "Choose a project below to get started")
    st_space("v", 3)

    # Example: display project cards in a grid
    # Replace this with your actual CollectionConfig projects
    projects = [
        {"title": "Project 1", "desc": "Description of project 1", "url": "#"},
        {"title": "Project 2", "desc": "Description of project 2", "url": "#"},
    ]

    gap_style = Style("gap:24px;", "home_grid_gap")
    with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", grid_style=gap_style):
        for proj in projects:
            with st_block(bs.card):
                st_write(s.Large + s.text.weights.bold_weight, proj["title"])
                st_space("v", 1)
                st_write(s.medium, proj["desc"])
                st_space("v", 1)
                st.link_button("Open", proj["url"])

    st_space("v", 3)
