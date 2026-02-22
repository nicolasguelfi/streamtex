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
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h1, "1. Useful information ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.1. Google doc Settings ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "For a better user experience you can ",
        (s.bold, "unselect"),
        " View/Show print layout",
    )
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.2. Access to COURSEPACK ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Go to ",
                (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "aiai.ros.lu", "https://aiai.ros.lu"),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Click on ",
                (s.project.colors.bright_red + s.bold, "\"Go\" "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Fill the form with ",
                (s.bold, "YOUR"),
                " gmail email address",
                (s.project.colors.salmon + s.bold, "USE THE CODE PRINTED ON YOUR PAPER "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Check your email at ",
                (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "mail.google.com", "https://mail.google.com"),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Click on the ",
                (s.project.colors.gold + s.bold, "COURSEPACK"),
                " link",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.3. Miro Board ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_sm,
        "All the manual digital notes made by the instructor during the sessions can be found using the link ",
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://miro.com/app/board/uXjVP08beHM=/?share_link_id=359755889796"),
        (s.bold, ". "),
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "PLEASE NOTE THAT THE CONTENT CAN BE DELETED JUST AFTER THE SESSION ")
    st_write(s.project.doc.paragraphs.p_body, "(thus ask right away if you want a pdf version of it) ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.4. Google account ", tag=t.h2, toc_lvl="+1")
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
            st_write("... ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "For some specific activities, you might be proposed to use the training gmail account (login and password) given during the session. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.5. Google Meet ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("install google chrome (if not already done) ")
        with lst.item():
            pass
        with lst.item():
            st_write("install on your computer ")
        with lst.item():
            st_write("launch chrome ")
        with lst.item():
            st_write("connect to the meeting room ")
        with lst.item():
            pass
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.6. Access to COMPUTERS @ DLH ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "The default login for every computer in the room is :  ")
    st_write(s.project.doc.paragraphs.p_body, "Username: student_dlh  ")
    st_write(s.project.doc.paragraphs.p_body, "Password: dlh ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "IF you have been provided with chromebooks then you do not need to login! ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.7. Backup notebooks folder ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_sm + s.project.colors.burnt_orange + s.italic, "If you have practical sessions on virtual computers hosted on GCP: ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("open a terminal ")
        with lst.item():
            st_write("copy and paste the following line:SOURCE=/home/jupyter/git/aiai/notebooks && TARGET=/home/jupyter/BCK_01 ")
        with lst.item():
            st_write("IF the target folder existsTHEN copy and paste the following line:rm -Rf $TARGET ")
        with lst.item():
            st_write("copy and paste the following line:mkdir -p \"$TARGET\" && cp -R \"$SOURCE\"/* \"$TARGET\" ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.8. Set Dark Mode on firefox / chrome ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(" install the DarkReader extension ")
        with lst.item():
            pass
        with lst.item():
            st_write(" set the following settings ")
        with lst.item():
            pass
        with lst.item():
            st_write("Screenshots")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
