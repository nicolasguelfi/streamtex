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
      #3d85c6 -> s.project.colors.sky_blue
      #783e04 -> s.project.colors.burnt_orange
      #9900ff -> s.project.colors.purple
      #a61b00 -> s.project.colors.salmon
      #cc0000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "PRACTICE"),
        (s.project.colors.burnt_orange + s.bold, "-"),
    )
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Basic Quasible Components  ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Quasible Quick StartPractice  ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Step 1 - First Access ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Connect to ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "quasible.ai", "https://www.quasible.ai"),
            )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img48.png")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Go the your account or the training account use the given code to find the associated account")
        with lst.item():
            st_write(s.bold, " Enter your workspace using your learner number")
    st_space(size=4)
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.link_blue + s.bold, "Connect to"),
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, " ", "http://quasible.ai"),
                (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, "Quasible.ai", "http://Quasible.ai"),
            )
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Select the Organisation / Account of the training ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "https://app.quasible.ai/en/ accounts/chat1d250919", link="https://app.quasible.ai/en/")
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=4)
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, "Go to your workspace")
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Step 2 - Persona Creation ", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Select New and Create a Persona")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Name it based on a specific expertise")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Insert a text that defines the expertise ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.salmon + s.bold, " Try to use your expert with the right pane"),
                (s.project.colors.salmon + s.bold, "(Spoiler alert! It will fail)"),
            )
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Create a workflow")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.salmon + s.bold, "Click "),
                (s.project.colors.salmon + s.bold, " to edit the workflow"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.salmon + s.bold, " Click on "),
                (s.project.colors.salmon + s.bold, " to select your Persona"),
            )
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Select your Persona")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Select the Language Model")
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Click on Save")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Check that your workflow is selected")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Test your Persona")
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Step 3 - Import documents", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Import on your computer all the documents available:",
                (s.project.pres.links.link_lg + s.project.colors.purple + s.bold, "HERE", "https://drive.google.com/drive/folders/1nhIIju4cYtKBo0m4_ss9km8hqPy3MV0D?usp=sharing"),
            )
        with lst.item():
            st_write("Import them in Quasible ONE by ONE")
        with lst.item():
            st_write("Click Import / File ")
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img34.png")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Select your file on your computer, check the name and click on Create")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Wait for the end of the analysis")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_body,
                " Check the following features from the ",
                " icon",
            )
        with lst.item():
            pass
    st_write(s.project.pres.titles.h3, "Step 4 - Chat with a PDF", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Open a pdf by clicking on ")
        with lst.item():
            st_write(" Ask a question in the chat input field")
        with lst.item():
            st_write(" Click on ")
        with lst.item():
            st_write(" Read the generated text")
        with lst.item():
            st_write(" Consult References")
        with lst.item():
            st_write(" Test more Chats with the document")
    st_write(s.project.pres.titles.h3, "Step 5 - Chat with Text and CSV Documents", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_body, "(in the folder CV)")
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h3, "Step 6 - Chat with Audio or Video", tag=t.h3)
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Click on Transcribe")
        with lst.item():
            st_write(s.project.colors.olive_green + s.bold, " Wait (especially if the document is long)")
        with lst.item():
            st_write(" Open The transcript")
        with lst.item():
            st_write(" Chat with the Transcript")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.purple + s.bold, "Check the long Summary"),
                " ....",
            )
    st_space(size=4)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img43.png")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Click on ")
        with lst.item():
            st_write(" Chat with the document")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.purple + s.bold, "Explore"),
                " ....",
                (s.project.colors.sky_blue + s.bold, "Step 5 - Chat with WebSite "),
            )
        with lst.item():
            st_write(" Click on ")
        with lst.item():
            st_write(" Click on  ")
        with lst.item():
            st_write("Configure as below")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Use this website:",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "https://demo.gaiwa.ros.lu/", "https://demo.gaiwa.ros.lu/"),
            )
        with lst.item():
            st_write(s.project.colors.olive_green + s.bold, " Wait! (especially if the site is big)")
        with lst.item():
            st_write(" Open a text document")
        with lst.item():
            st_write(s.project.pres.paragraphs.p_body, " Click on ", " in the Chat pane")
        with lst.item():
            st_write("select your website")
        with lst.item():
            st_write(" Ask a question")
    st_space(size=1)
    st_space(size=1)
