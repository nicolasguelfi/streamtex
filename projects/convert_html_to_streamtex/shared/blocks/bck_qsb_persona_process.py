import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #2f5a1b -> s.project.colors.forest_green
      #990000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Process to Develop Quasible Personas ", tag=t.h2, toc_lvl="+1")
    st_space(size=4)
    st_space(size=4)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "Persona Requirements"),
                "Describe in a short sentence what is the persona expertise. ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Ask Quasible Persona Expert Agent to ",
                (s.project.colors.bright_red + s.bold, "generate the persona"),
                " for you ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "Create a Persona document"),
                " with the generated text ",
            )
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Test the persona")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "IF the test is not satisfactoryTHEN list the issues and ask the agent to ",
                (s.project.colors.bright_red + s.bold, "improve the persona description"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "IF test is satisfactory THEN ",
                (s.project.colors.bright_red + s.bold, "use the persona in a workflow"),
            )
    st_space(size=1)
