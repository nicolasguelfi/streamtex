import streamlit as st
import setup
from streamtex import st_book, TOCConfig, MarkerConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts


st.set_page_config(
    page_title="MODELSWARD 2026 — Agentic BPMN Framework",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.section_title + s.center_txt + s.text.wrap.nowrap,
    sidebar_max_level=2,
    content_style=s.large + s.text.colors.reset,
)

marker = MarkerConfig()

sts.theme = dark

st_book(
    [
        blocks.bck_title,
        blocks.bck_intro_problem,
        blocks.bck_intro_gateway,
        blocks.bck_intro_frege,
        blocks.bck_related_work,
        blocks.bck_method_overview,
        blocks.bck_method_architecture,
        blocks.bck_method_agents,
        blocks.bck_method_instructions,
        blocks.bck_method_protocol,
        blocks.bck_method_validation,
        blocks.bck_method_simulator,
        blocks.bck_method_feedback,
        blocks.bck_eval_setup,
        blocks.bck_eval_conformance,
        blocks.bck_eval_by_level,
        blocks.bck_eval_per_model,
        blocks.bck_eval_efficiency,
        blocks.bck_discuss_limitations,
        blocks.bck_conclusion,
        blocks.bck_questions,
        blocks.bck_references,
    ],
    toc_config=toc,
    marker_config=marker,
)
