import streamlit as st 
import setup
from streamtex import st_book, TOCConfig
import blocks
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts



st.set_page_config(page_title="StreamTeX 1.53.0 Test Book",
                    page_icon=None,
                    layout="wide",
                    initial_sidebar_state="collapsed",
                    menu_items=None)

toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    title_style=s.project.titles.title_giant_green_01 + s.center_txt + s.text.wrap.nowrap,
    content_style=s.large + s.text.colors.reset)

sts.theme = dark

st_book([
    blocks.bck_welcome_screen_aiai,
    blocks.bck_training_title_aiai_dlh,
    blocks.bck_showcase_glimpse_aiai,
    blocks.bck_trainer_ng,
    blocks.bck_participants_round_table_aiai,
    blocks.bck_domains_terms_aiai,
    blocks.bck_it_computers_ai_users,
    blocks.bck_title_content,
    blocks.bck_image_dog_sherlock,
    blocks.bck_content_aiai_all,
    blocks.bck_session_01_course_docs,
    blocks.bck_image_dog_02_practice,
    blocks.bck_practice_course_pack_access,
    blocks.bck_game_your_profile,
    blocks.bck_setting_up_notebooks_aiai,
    blocks.bck_image_go_practice,
    blocks.bck_title_bravo,
    blocks.bck_image_two_racoons_01,
    blocks.bck_title_break,
    blocks.bck_image_break_frog_orange,
    blocks.bck_image_welcome_back_giraffe_01,
    blocks.bck_showcase_aiai_content,
    blocks.bck_showcase_text_generation,
    blocks.bck_showcase_image_recognition_mnist_intro_aiai
    
], toc_config=toc)







