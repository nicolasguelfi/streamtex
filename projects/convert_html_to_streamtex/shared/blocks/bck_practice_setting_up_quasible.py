import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0000ff -> s.project.colors.link_blue
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #a64d78 -> s.project.colors.dark_purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Practice")
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green, "Setting up your "),
        (s.project.colors.burnt_orange, "Quasible "),
        (s.project.colors.forest_green, "account "),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                " Signup at ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "quasible.ai", "http://quasible.ai"),
            )
        with lst.item():
            st_write(" Proceed with the following processes: ")
        with lst.item():
            pass
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "Fill the survey", "https://forms.gle/7fzbv5299bRJ17K6A"), (s.project.colors.olive_green + s.bold, "GAI4AS"), (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://app.quasible.ai/en/accounts/gai4as251205"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://docs.google.com/spreadsheets/d/1mdaQRrUY61vARZEQDS5zyy6vQvO_ZuIXTxqS5IafW48/edit?resourcekey=&gid=1041511767#gid=1041511767"))
        with g.cell():
            pass
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "Learners' List", "https://docs.google.com/spreadsheets/d/1mdaQRrUY61vARZEQDS5zyy6vQvO_ZuIXTxqS5IafW48/edit?resourcekey=&gid=1041511767#gid=1041511767"),
        "(to invite to the workspace) ",
    )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "!! WARNING !!  ", tag=t.h5)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange, "Stay on the same device ")
        with lst.item():
            st_write(s.project.colors.teal, "Log-in your quasible account ")
        with lst.item():
            st_write(s.project.colors.burnt_orange, "Check your invitation email to the group account ")
        with lst.item():
            st_write(s.project.colors.teal, "click on the accept invitation button ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.dark_purple, " Go to the Training Workspace ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.purple + s.bold, "Activate the Training Organisation"),
                (s.project.colors.dark_purple, "click on the top left icon (blue P in the image below) "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.burnt_orange + s.bold, "Switch the organisation"),
                (s.project.colors.dark_purple, " to benefit from the credits and capacities of the organisation"),
                (s.project.colors.bright_red + s.bold, "If you stay on "),
                (s.project.colors.link_blue + s.bold, "\"Personal\""),
                (s.project.colors.bright_red + s.bold, " might be blocked"),
                (s.project.colors.dark_purple, " on some features"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.bright_red + s.bold, "Enter your workspace"),
                (s.project.colors.forest_green + s.bold, "use your "),
                (s.project.colors.bright_red + s.bold, "learner ID"),
                (s.project.colors.forest_green + s.bold, " (e.g. Learner01 / Group01 / ... )"),
            )
        with lst.item():
            st_write(s.project.colors.dark_purple + s.bold, " DONE !")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
