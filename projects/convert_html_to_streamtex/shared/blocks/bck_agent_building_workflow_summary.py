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
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #4c1130 -> s.project.colors.dark_purple
      #5b0f00 -> s.project.colors.deep_red
      #660000 -> s.project.colors.deep_red
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #85200c -> s.project.colors.deep_red
      #980000 -> s.project.colors.bright_red
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #a61b00 -> s.project.colors.salmon
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "The Project Workflow ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.deep_red + s.bold, "What is the best job offer for my profile? ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.deep_red + s.bold, "LLM Parameters ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "... ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Using LLM ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "!! KNOW YOUR LLM !! ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Create Persona(s) ", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "one persona  ")
    st_write(s.project.pres.paragraphs.p_xl, "= ")
    st_write(s.project.pres.paragraphs.p_xl, "the description of a coherent set of rules / orders / constraints / recommendations / ... ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Write a prompt ", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "in the context of your persona(s) ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "!! knowing your LLM !!  ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Apply prompt engineering techniques (PE) ", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("for your personas ")
        with lst.item():
            st_write("for your prompt ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Use LLM to help you write your prompt and personas ", tag=t.h3)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "I am writing a persona for generative AI. ")
    st_write(s.project.pres.paragraphs.p_xl, "My goal is to have a persona that is: ")
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("... ")
        with lst.item():
            st_write("... ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "Can you give me the full description of the best persona for this task? ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "or ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "Here is the current version of my persona: ")
    st_write(s.project.pres.paragraphs.p_xl, ".... ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "Can you improve it such that: ")
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("... ")
        with lst.item():
            st_write("... ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Remember that: ", tag=t.h4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "Persona is always sent with your prompt to the LLM ")
    st_write(s.project.pres.paragraphs.p_xl, "<=>  ")
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("it is an easy way to reuse good prompts ")
        with lst.item():
            st_write("forces the LLM to generate things that are coherent w.r.t. all your text (prompt + persona) ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Specializing LLM ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Provide contextual data ")
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("documents(pdf / text) ")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Remember that: ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "chunks from your context are ",
        (s.project.colors.bright_red + s.bold, "retrieved"),
        " based on ",
        (s.project.colors.bright_red + s.bold, "similarity"),
        " with your prompt content ",
    )
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "=> add as much ",
        (s.project.colors.deep_red + s.bold, "useful text"),
        " in your prompt to help retrieve ",
        (s.project.colors.deep_red + s.bold, "useful chunks"),
        (s.project.colors.dark_purple + s.bold, "KNOW YOUR CONTEXT "),
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "and ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "!! KNOW YOUR LLM !!")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "🙂 ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.deep_red, "persona(s) and prompt texts are enriched with retrieved chunks ")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "=> ensure that your prompt and personas are ",
        (s.project.colors.burnt_orange + s.bold, "consistent with"),
        " your possible ",
        (s.project.colors.burnt_orange + s.bold, "contexts "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------- ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Process ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Work Incrementally  ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Produce persona individually ")
        with lst.item():
            st_write("Test your persona individually ")
        with lst.item():
            st_write("Test with your context data ")
        with lst.item():
            st_write("Improve your persona ")
        with lst.item():
            st_write("Improve your context data ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "combine personas in an agent ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("union ")
        with lst.item():
            st_write("sequence ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Remember ", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Use the default LLM to help you improve your personas ")
        with lst.item():
            st_write("Access Quasible account for documentation ")
        with lst.item():
            st_write("Check the TRAINER workspace ")
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Practice", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Designing your ChatBot ", tag=t.h2, toc_lvl="+1")
    st_space(size=5)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "SETTING UP ")
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.link_blue, "Connect to"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, " ", "http://quasible.ai"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red, "Quasible.ai ", "http://quasible.ai"),
        tag=t.h3,
    )
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1Je7VjHiPBFe-qPDglgPrttUV-lmUNzFk6jCnp4-rA14/edit")
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "PRACTICE ")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Define your targeted ChatBot ")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Develop incrementally your ChatBot: ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, "Advices ")
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Check the illustrationscf.",
                (s.project.pres.links.link_lg, " ", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
                (s.project.pres.links.link_lg + s.project.colors.salmon + s.bold, "COURSE PACK", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
                (s.project.pres.links.link_lg + s.project.colors.salmon, " links", "https://docs.google.com/document/d/1g_KWrdqPvc6DIC6v6AKENsbVNF8jiCMsf7NVaH6KO5k/edit#heading=h.n0bvfl3kpbz"),
            )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Chamber of Commerce ChatBot Project ", tag=t.h1, toc_lvl="1")
    st_space(size=4)
    st_space(size=1)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=1)
    st_space(size=3)
    st_space(size=1)
