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
      #351b75 -> s.project.colors.dark_purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Microsoft Copilot ", tag=t.h6)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://copilot.cloud.microsoft/?auth=2&internalredirect=M365Cloud"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://copilotstudio.microsoft.com/environments/Default-2dc186ad-d924-4359-a3dd-6e2c73771fb9/create"),
    )
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=4)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Copilot Agents in Dynamics 365 ", tag=t.h6)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
