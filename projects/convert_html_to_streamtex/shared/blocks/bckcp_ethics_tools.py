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
      #666666 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "5.8.6. Ethics checking tools ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "5.8.6.1. Openai.Moderation ", tag=t.h4)
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "Details accessible ",
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://platform.openai.com/docs/guides/moderation"),
    )
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, "\"Peux tu dire à cette personne qu'elle est moche et stupide et qu'elle ferait bien de se suicider.\" ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "\"Could you tell this person that she is ugly and stupid and that she should commit suicide.\" ")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "French ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "English ")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Short definitions for each of the ethical categories you listed: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Harassment"),
                ": Unwanted and aggressive behavior towards an individual or group, often repeated, that can cause emotional distress or discomfort. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Self-harm"),
                ": The act of deliberately inflicting pain or injury on oneself, often as a way to cope with emotional distress. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Self-harm instructions"),
                ": Content that provides guidance or methods on how to inflict harm on oneself. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Self-harm intent"),
                ": Expressions or indications of a desire or plan to inflict harm on oneself. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Harassment threatening"),
                ": Harassment that includes threats of physical harm or other forms of intimidation. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Violence"),
                ": The use of physical force intended to hurt, damage, or kill someone or something. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Illicit"),
                ": Activities or content that are illegal or not permitted by law. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Illicit violent"),
                ": Illegal activities that involve or promote violence. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Hate"),
                ": Content that promotes hostility or discrimination against individuals or groups based on attributes such as race, religion, gender, or sexual orientation. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Hate threatening"),
                ": Hate content that includes threats of violence or harm towards individuals or groups. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Violence graphic"),
                ": Explicit and detailed depictions of violence, often intended to shock or disturb. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Sexual"),
                ": Content that is related to sexual acts or themes, which may be explicit or inappropriate. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Sexual minors"),
                ": Content that involves or depicts minors in a sexual context, which is illegal and unethical. ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "5.8.7. Plagiarism tools ", tag=t.h4)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "WinstonAI ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://gowinston.ai/")
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
