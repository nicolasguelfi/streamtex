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
      #731b47 -> s.project.colors.dark_purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "The Case of Autonomous Vehicles ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.technologyreview.com/2018/10/24/139313/a-global-ethics-study-aims-to-help-ai-solve-the-self-driving-trolley-problem/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.moralmachine.net/hl/fr"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Moral Machine ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://dspace.mit.edu/bitstream/handle/1721.1/125065/Moral%20Machine%20Paper.pdf?sequence=1#:~:text=")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "233"),
        " countries and territories ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "2"),
        " millions of people ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "40"),
        " million decisions ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare the young ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare pedestrians over passengers ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare more lives ", tag=t.h4)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://bmdv.bund.de/SharedDocs/EN/Articles/DG/automated-and-connected-driving.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "5. ")
    st_write(s.project.pres.paragraphs.p_xl, "Automated and connected technology should prevent accidents wherever this is practically possible.  ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Based on the state of the art, ",
        (s.project.colors.bright_red + s.bold, "the technology must be designed in such a way that critical situations do not arise in the first place"),
        ".  ",
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "These include dilemma situations, in other words a situation in which an automated vehicle has to “decide” which of two evils, between which there can be no trade-off, it necessarily has to perform.  ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "In this context, ",
        (s.project.colors.bright_red + s.bold, "the entire spectrum of technological options – for instance from limiting the scope of application to controllable traffic environments, vehicle sensors and braking performance, signals for persons at risk, right up to preventing hazards by means of “intelligent” road infrastructure – should be used and continuously evolved"),
        ".  ",
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "The significant enhancement of road safety is the objective of development and regulation, starting with the design and programming of the vehicles such that they drive in a defensive and anticipatory manner, posing as little risk as possible to vulnerable road users. ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "9.")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "In the event of unavoidable accident situations, ",
        (s.project.colors.bright_red + s.bold, "any distinction based on personal features"),
        " (age, gender, physical or mental constitution) ",
        (s.project.colors.bright_red + s.bold, "is strictly prohibited"),
        ". ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        " It is also ",
        (s.project.colors.bright_red + s.bold, "prohibited to offset"),
        " victims against one another. ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "General programming to ",
        (s.project.colors.bright_red + s.bold, "reduce the number of personal injuries may be justifiable"),
        ".  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Those parties involved in the generation of mobility risks must ",
        (s.project.colors.bright_red + s.bold, "not sacrifice non-involved parties"),
        ". ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
