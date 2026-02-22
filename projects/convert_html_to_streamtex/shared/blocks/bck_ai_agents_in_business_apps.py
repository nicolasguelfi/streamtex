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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Variants ofAgents and Workflowsin Business Apps ", tag=t.h2, toc_lvl="+1")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "SAP Joule Agents ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.sap.com/belgie/resources/what-are-ai-agents#:~:text=Image%3A%20Screenshot%20of%20the%20SAP,Invoice%20agents%20are%20all%20interconnected")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Microsoft Copilot & Dynamics 365 ", tag=t.h3)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Salesforce Einstein ", tag=t.h3)
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=4)
    st_space(size=1)
