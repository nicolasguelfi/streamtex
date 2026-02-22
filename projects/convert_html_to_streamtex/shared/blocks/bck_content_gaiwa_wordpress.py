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
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3, "Session 5", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4, "Introduction to Wordpress ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("What is WordPress?")
        with lst.item():
            st_write("Features of WordPress")
        with lst.item():
            st_write("Who uses WordPress?")
        with lst.item():
            st_write("Why should you use WordPress?")
    st_write(s.project.pres.titles.h5, "Wordpress Main Components", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("How to add a Post?")
        with lst.item():
            st_write("How to add a Page?")
        with lst.item():
            st_write("Featured Image vs. Normal Image")
        with lst.item():
            st_write("How to work with Categories?")
        with lst.item():
            st_write("How to work with Tags?")
        with lst.item():
            st_write("Media Library")
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.olive_green, "BREAK ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Wordpress Practical - Session 1 ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 6", tag=t.h3)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Wordpress AI Plugins", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Chatbase")
        with lst.item():
            st_write("Quasible")
        with lst.item():
            st_write("Personas")
        with lst.item():
            st_write("Contexts")
    st_write(s.project.pres.titles.h6, "BREAK", tag=t.h6)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "MYWOP "),
        (s.project.colors.bright_red, "Project Start "),
        tag=t.h4,
    )
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Objectives for site and ChatBot")
        with lst.item():
            st_write("Tech Stack")
        with lst.item():
            st_write(" Project Phase 1")
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Tools Setup ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "Wordpress Practical - Session 2", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_body, "ChatBot v1 for Italian Cuisine")
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 7", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Session introduction", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "Wordpress Practical - Session 3", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_body + s.bold, "PART 1 ")
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "MYWOP v1 ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_body, "Website content")
    st_write(s.project.pres.paragraphs.p_body, "ChatBot Objectives")
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.titles.h6, "BREAK", tag=t.h6)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_body + s.bold, "PART 2 ")
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "ChatBot v1", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("persona")
        with lst.item():
            st_write("knowledge base")
        with lst.item():
            st_write("test the chatbot")
        with lst.item():
            st_write("integrate into the website")
        with lst.item():
            st_write("discuss results")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 8", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Wordpress Practical - Session 4", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_body, "ChatBot v2 - PART 1")
    st_space(size=1)
    st_write(s.project.pres.titles.h6, "BREAK", tag=t.h6)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Wordpress Practical - Session 4", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_body, "ChatBot v2 - PART 1")
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "Demo / Wrap-up", tag=t.h5)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 9", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Wordpress Practical - Session 5", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_body, "PART 1")
    st_write(s.project.pres.paragraphs.p_body, "ChatBotv3")
    st_write(s.project.pres.titles.h6, "BREAK", tag=t.h6)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Wordpress Practical - Session 5", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_body, "PART 2")
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "Prepare for ChatBots Demos", tag=t.h5)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Demos / Wrap-up", tag=t.h4)
    st_space(size=1)
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Session 10", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4, "SetUp LearnersChatBots Access", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "ChatBots Demos + QA", tag=t.h5)
    st_space(size=1)
    st_write(s.project.pres.titles.h6, "BREAK", tag=t.h6)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "TrainingChatBots WP Demo", tag=t.h4)
    st_space(size=1)
    st_write(s.project.pres.titles.h5, "Q/A", tag=t.h5)
    st_space(size=1)
    st_write(s.project.pres.titles.h4, "Surveys", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h6 + s.project.colors.forest_green, "TRAINING END ", tag=t.h6)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
