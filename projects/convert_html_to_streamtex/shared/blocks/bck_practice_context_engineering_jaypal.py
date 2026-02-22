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
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Prompt & Context Engineering  ", tag=t.h1, toc_lvl="1")
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Practicals ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Context  ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "A restaurant ChatBot for answering customer questions about the menu ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Data ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "in the data folder  ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "LINK", link="https://drive.google.com/drive/folders/1nhIIju4cYtKBo0m4_ss9km8hqPy3MV0D?usp=sharing")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Process ", tag=t.h5)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Create 10 prompts ", tag=t.h6)
    st_write(s.project.pres.paragraphs.p_xl, "to test all the types of questions you envision that could be asked to your chatbot. ")
    st_space(size=4)
    st_space(size=2)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Create two Quasible chatbots ", tag=t.h6)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "One with context made of the ",
        (s.bold, "PDF"),
        " version of the menuOne with context made of the ",
        (s.bold, "MARKDOWN"),
        " version of the menu ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Both use the same Persona text:",
        (s.project.colors.burnt_orange + s.bold, "\"jaypal-Persona.md\" "),
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Proceed to your Validation testing campaign ", tag=t.h6)
    st_write(s.project.pres.paragraphs.p_xl, "all the 10 prompts sent to each ChatBot ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Collect the results in ",
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "THIS", "https://docs.google.com/document/d/1T1KKm3KDiWqWGMx_OnIjo9-eceMXgjzYRBg2c5eTHL8/edit?tab=t.0"),
        " ",
        " google doc ",
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Produce a Critical analysis ", tag=t.h6)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Insert a ",
        (s.bold, "critical analysis"),
        " for each test: ",
    )
    st_write(s.project.pres.paragraphs.p_xl, "1 - Completeness wrt menu ")
    st_write(s.project.pres.paragraphs.p_xl, "2 - Correctness wrt menu ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Prompt Improvement: ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Use Promptès to get an improved version of the test prompts  ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "LINK", link="https://app.quasible.ai/en/embed/defy4fgwljsnya4lvp9und5a")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Remind the prompt context and the quality objectives(Completeness or correctness) ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Test the improved prompts ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Redo the test campaign with your 10 new prompts ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Compare the results ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
