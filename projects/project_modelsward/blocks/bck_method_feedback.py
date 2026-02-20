import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    feedback_text = s.big + s.italic
    emphasis = s.bold + s.big

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "CoT-Articulated Diagnostic Feedback",
        toc_lvl="2",
    )
    st_space(size=2)
    with st_block(s.project.containers.beamer_block_red):
        st_write(s.project.titles.block_title, "Generic Feedback")
        st_space(size=1)
        st_write(bs.feedback_text, '"Path symmetry constraint violated."')
    st_space(size=2)
    with st_block(s.project.containers.beamer_block_green):
        st_write(s.project.titles.block_title, "CoT-Articulated Feedback")
        st_space(size=1)
        st_write(
            bs.feedback_text,
            '"Split gateway creates 3 paths but join expects 2 -> token accumulation -> deadlock. Fix: add third incoming flow to join."',
        )
    st_space(size=2)
    st_write(
        bs.body,
        (bs.emphasis, "Repair loop:"),
        "  Generate -> Validate -> Map errors -> Repair agents -> Re-validate",
    )
    st_space(size=2)
