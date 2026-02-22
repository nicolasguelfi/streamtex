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
      #7f6000 -> s.project.colors.gold
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Appendix ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=5)
    st_space(size=5)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Notebooks URLs ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "Learner01")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.link_blue + s.bold, "link", link="http://72a7798fb60ac3-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner02")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://492e64b805d980cd-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner03")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://77dd355152e33b48-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner04")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://386646442c904225-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner05")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://771dff63ae14020a-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner06")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://50ca95eb643dd15f-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner07")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://680758624614cfcd-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner08")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6fcda3e5cb55a740-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner09")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://35bcfeab41fc2870-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner10")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://6ae6d2be302eb902-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner11")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://2f53ec06289b6409-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner12")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://79a821196eb0563c-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner13")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://2c3e95fd11dc5bd5-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner14")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://3759bd77df56dc7d-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner15")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://22e47b92f1db49db-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner16")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://3a204e72f6e86c4f-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner17")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://26ecd37cefb16969-dot-us-west1.notebooks.googleusercontent.com")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Learner18")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://17cfbbcac67eaa37-dot-us-west1.notebooks.googleusercontent.com")
    st_space(size=3)
    st_space(size=5)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Games Results ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "Nb")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.gold + s.bold, "Game Title")
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "link")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Game - Individual Presentation")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/19ZRyIZBMyZAq5EL0P09M0OCEQou719JWeVHEQ6Vdjn0/viewanalytics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "2")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Game - End of Session Feedback")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/18Ja0quGc5evYAtuTMqRkZ8VRY5eYpWCzoojox9UhzY8/viewanalytics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "3")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Game - Ethics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/14ykXV9mh_ZKsz-gsz0zmN2IehFslwJlAyWfDyYRu20c/viewanalytics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Jeu - société")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/1uio-fG9pNmEv80HzV1TMZEHOaQynL90I7cErTX7yR34/viewanalytics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "5")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Game - Further Interests")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/1cVz2ih_ksi1I1AGOYDiJZrEHLjRLa7zk3LNRpdP82uo/viewanalytics")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "6")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Game - Access to resources")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue + s.bold, "Results HERE!", link="https://docs.google.com/forms/d/1zn5_LrLKJscrTs3-VDa0zo0L8lGvU0kVosWsiUPfI-E/viewanalytics")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "-")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "-")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Table of Content ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=5)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Applications settings ", tag=t.h2, toc_lvl="+1")
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Firefox settings ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" launch firefox ")
        with lst.item():
            st_write(" click on the right menu icon")
        with lst.item():
            st_write(" click on the bookmark bar icon for the Session documents ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Google Doc View ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" use firefox ")
        with lst.item():
            st_write(" use the accountaiailearner@gmail.com	 ")
        with lst.item():
            st_write(" Deactivate View / Show print layout ")
        with lst.item():
            st_write(" Select View / Zoom / Fit ")
        with lst.item():
            st_write(" You should see this: ")
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Set Dark Mode ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" install the DarkReader extension ")
        with lst.item():
            st_write(" set the following settings ")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "OR ")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
