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
      #37761c -> s.project.colors.olive_green
      #666666 -> s.project.colors.gray
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.burnt_orange, "Introduction to ", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.dark_purple, "Quasible Agents ", tag=t.h5)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.bright_red, "Quasible Agent ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "= ", tag=t.h5)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "A generative artificial intelligence "),
        (s.project.colors.dark_purple, "assistant"),
        (s.project.colors.bright_red, " that executes specific "),
        (s.project.colors.dark_purple, "workflows "),
        tag=t.h5,
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Quasible Workflow ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "= ", tag=t.h5)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Structured "),
        (s.project.colors.dark_purple, "process"),
        (s.project.colors.bright_red, " where "),
        (s.project.colors.dark_purple, "personas"),
        (s.project.colors.bright_red, " collaboratesequentially or in combinationutilizing specific language "),
        (s.project.colors.dark_purple, "models "),
        tag=t.h5,
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Agent - "),
        (s.project.colors.gray, "AG_QuasiDoc "),
        tag=t.h5,
    )
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green, "Workflow of"),
        (s.project.colors.bright_red, " "),
        (s.project.colors.gray, "AG_QuasiDoc "),
        tag=t.h5,
    )
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img18.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Variants of ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Agents and Workflows ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "in Business Apps ", tag=t.h2, toc_lvl="+1")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "SAP Joule Agents ", tag=t.h3)
    st_write(s.project.pres.titles.h5 + s.project.colors.link_blue, "_", tag=t.h5)
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img17.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=4)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Microsoft Copilot & Dynamics 365 ", tag=t.h3)
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Salesforce Einstein ", tag=t.h3)
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=4)
    st_space(size=4)
    st_space(size=1)
