"""Title slide — Generative Software Engineering (AI4SE course)."""

from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """Local styles for the title slide."""
    # Title composition
    main_title = s.project.titles.course_title + s.center_txt
    subtitle = s.project.colors.accent + s.Large + s.center_txt
    institution = s.large + s.center_txt + s.project.colors.muted + s.italic

    # Logo container: centered with controlled width
    logo_container = s.center_txt

    # Decorative rule under title
    rule = ns(
        "border: none;"
        "height: 3px;"
        "background: linear-gradient(90deg, transparent, #5B9CF6, #00D4AA, transparent);"
        "margin: 0 20%;",
        "title_rule",
    )

bs = BlockStyles


def build():
    st_space(size=3)

    # --- DLH Logo ---
    with st_block(bs.logo_container):
        st_image(uri="dlh_logo.png", width="160px")

    st_space(size=3)

    # --- Main title ---
    with st_block(s.center_txt):
        st_write(bs.main_title, "Generative Software Engineering", tag=t.div, toc_lvl="1")

    st_space(size=1)

    # --- Decorative gradient rule ---
    st_html(f'<hr style="{bs.rule.css}">')

    st_space(size=2)

    # --- Subtitle / course code ---
    with st_block(s.center_txt):
        st_write(bs.subtitle, "AI4SE", tag=t.div)

    st_space(size=2)

    # --- Institution ---
    with st_block(s.center_txt):
        st_write(bs.institution, "Digital Learning Hub — Luxembourg")

    st_space(size=3)
