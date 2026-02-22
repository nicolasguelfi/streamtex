import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #980000 -> s.project.colors.bright_red
      #ff9900 -> s.project.colors.orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Domains ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "A"),
        (s.project.colors.bright_red, "rtificial "),
        (s.project.colors.gold, "I"),
        (s.project.colors.bright_red, "ntelligence"),
        tag=t.h5,
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.orange, "... ")
    st_space(size=5)
    st_space(size=5)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "A"),
        (s.project.colors.bright_red, "rtificial "),
        tag=t.h5,
    )
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("man-made? ")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("non natural?")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "I"),
        (s.project.colors.bright_red, "ntelligence "),
        tag=t.h5,
    )
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" ability to acquire and apply knowledge and skills?")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" adaptation capabilities?")
        with lst.item():
            st_write(s.project.colors.dark_purple + s.bold, " not stupid?")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "\""),
        (s.project.colors.gold, "Faculty of understanding, conceiving, knowing, and in particular the ability to discern  "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "or "),
        (s.project.colors.teal + s.bold, "establish relationships between facts"),
        (s.project.colors.gold, ", ideas or forms  "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.teal + s.bold, "to achieve knowledge"),
        (s.project.colors.teal, "."),
        (s.project.colors.gold, "Aptitude to "),
        (s.project.colors.teal + s.bold, "adapt a behavior to a new situation"),
        (s.project.colors.gold, ", a skill that is shown in a given situation, skill demonstrated by the choice of means that are used to achieve a specific result.\""),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.dictionnaire-academie.fr/article/A9I1608"),
    )
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "“Viewed narrowly, there seems to be almost "),
                (s.project.colors.burnt_orange + s.bold, "as many"),
                (s.project.colors.forest_green + s.bold, " "),
                (s.project.colors.burnt_orange + s.bold, "definitions"),
                (s.project.colors.forest_green + s.bold, " of intelligence"),
                (s.project.colors.burnt_orange + s.bold, "as"),
                (s.project.colors.forest_green + s.bold, " there were "),
                (s.project.colors.burnt_orange + s.bold, "experts"),
                (s.project.colors.forest_green + s.bold, " asked to define it.”"),
                (s.italic, "Sternberg, R. (2004). intelligence. In The Oxford Companion to the Mind. : Oxford University Press."),
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://arxiv.org/pdf/0706.3639.pdf"),
                " ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.arxiv-vanity.com/papers/0712.3329/"),
            )
    st_space(size=3)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Going Deeper: ", tag=t.h6)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Legg, S., & Hutter, M. (2007). A collection of definitions of intelligence. Frontiers in Artificial Intelligence and applications, 157, 17. ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://arxiv.org/pdf/0706.3639.pdf"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Legg, S., & Hutter, M. (2007). Universal intelligence: A definition of machine intelligence. Minds and machines, 17, 391-444. ",
                (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.arxiv-vanity.com/papers/0712.3329/"),
            )
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
