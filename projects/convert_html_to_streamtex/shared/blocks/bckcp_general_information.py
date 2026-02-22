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
      #434343 -> s.project.colors.gray
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "2. General information ", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "2.1. Purpose ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "This document is intended to provide all the useful information used during the sessions allowing for studying the topics addressed in the best possible way. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Parts of this document belong to the company RightOnSkill, which grants the University of Luxembourg, in the context of courses organized by Professor Nicolas Guelfi, the free use of this content, provided it is neither redistributed nor commercialized.  ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.2. Confidentiality ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_sm,
        "All information in this document is under ",
        (s.project.colors.bright_red + s.bold, "copyright regulation"),
        ".  ",
    )
    st_write(s.project.doc.paragraphs.p_body, "You are allowed to use it for your own purpose if you participated in a training during which it has been distributed. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "More details can be provided using the contact information given below. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.3. Contact information ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "2.3.1. Prof. Dr. Nicolas Guelfi ", tag=t.h3)
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.project.doc.links.link_body + s.project.colors.link_blue, "nicolas.guelfi@uni.lu", "mailto:nicolas.guelfi@uni.lu"),
        " (OFFICIAL SECURED) ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.project.doc.links.link_body + s.project.colors.link_blue, "nicolas.guelfi@bics.lu", "mailto:nicolas.guelfi@bics.lu"),
        " (NON SECURED) ",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "nicolas.guelfi@ros.lu", link="mailto:nicolas.guelfi@ros.lu")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "nicolas.guelfi@quasible.ai", link="mailto:nicolas.guelfi@quasible.ai")
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "2.3.2. Right On Skill ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Right On Skill ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "contact@rightonskill.com", link="mailto:contact@rightonskill.com")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "2.3.2. Quasible ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "contact@quasible.ai", link="mailto:contact@quasible.ai")
    st_space(size=1)
    st_space(size=1)
