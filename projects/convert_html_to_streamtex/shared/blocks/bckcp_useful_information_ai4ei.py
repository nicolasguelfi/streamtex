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
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "3. Useful information ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.1. Google doc Settings ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "For a better user experience you can ",
        (s.bold, "unselect"),
        " View/Show print layout",
    )
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.2. Miro Board ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_sm,
        "All the manual digital notes made by the instructor during the sessions can be found using the link ",
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://miro.com/app/board/uXjVLQTDx00=/?moveToWidget=3458764618892452650&cot=14"),
        (s.bold, ". "),
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "PLEASE NOTE THAT THE CONTENT CAN BE DELETED JUST AFTER THE SESSION ")
    st_write(s.project.doc.paragraphs.p_body, "(thus ask right away if you want a pdf version of it) ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.3. Google account ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "By default you need to have your own google account. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "This account is used for some or all of the following: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("firefox profile ")
        with lst.item():
            st_write("access to google drive space ")
        with lst.item():
            st_write("access to notebooks ")
        with lst.item():
            st_write("access to AI cloud services ")
        with lst.item():
            st_write("google surveys ")
        with lst.item():
            st_write("... ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "For some specific activities, you might be proposed to use the training gmail account (login and password) given during the session. ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
