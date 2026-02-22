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
      #660000 -> s.project.colors.deep_red
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Projects Presentation ", tag=t.h2, toc_lvl="+1")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Objectives ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Team based project ")
        with lst.item():
            st_write("Produce a Generative Agent specialist of a specialized field  related to European Citizens and European Governance: ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.teal + s.bold, "AI and Diplomacy ")
        with lst.item():
            st_write(s.project.colors.deep_red + s.bold, "AI and Sustainable Development ")
        with lst.item():
            st_write(s.project.colors.teal + s.bold, "AI and Health ")
        with lst.item():
            st_write(s.project.colors.deep_red + s.bold, "AI and Employment ")
        with lst.item():
            st_write(s.project.colors.teal + s.bold, "AI and Ethics ")
        with lst.item():
            st_write(s.project.colors.deep_red + s.bold, "AI and Intercultural Dialogue ")
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, "AI and ...")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Organization ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.bold, "Create groups of +/- 4 students BUT "),
                (s.project.colors.deep_red + s.bold, "6 groups maximum"),
                (s.bold, " for the class "),
            )
        with lst.item():
            st_write(s.bold, "Define the specialized field ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Allocate sub-fields to group members ")
        with lst.item():
            st_write(s.bold, "Follow an iterative and incremental approach to: ")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Report ", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Title, group number and authors ")
        with lst.item():
            st_write("Abstract ")
        with lst.item():
            st_write("Introduction ")
        with lst.item():
            st_write("Generative Agent Specialist Sections ")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Presentation(s) ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("cf. schedule for exact dates ")
        with lst.item():
            st_write("Duration 3' per student= 9' for a group of 3= 12' for a group of 4+ 5 minutes of answers to questions ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Content for each student ")
        with lst.item():
            pass
        with lst.item():
            st_write("Goal for each studentDemonstrate by practice on the project that parts or all of the knowledge and know-hows related to the course learning outcomes have been acquired (cf. course card). ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Advises:Work enough to have concrete results to presentFocus on commuting meaningful and useful information with enough detailsDo not present only goals / outlineDo not be only list results but choose at least one to detail.Focus on showing your capability to understand the project related information that is related to artificial intelligence. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Constraints: ", tag=t.h3)
    st_space(size=2)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" Make use of generative AI for your work (report and presentations) ")
        with lst.item():
            st_write(" All produced content must be \"academically valid\" ")
        with lst.item():
            st_write(" All claims / information must be supported by some academic references ")
        with lst.item():
            st_write(" You need to be capable to answer an 'understanding' question related to the content of your report/presentations. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Workload: ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl, "5 ECTS = 5 * 30 hours = 150 hours ")
    st_write(s.project.pres.paragraphs.p_xl, "21h = 14 * 1h30 -> lectures ")
    st_write(s.project.pres.paragraphs.p_xl, "21h =  14 x 1h30 -> lectures notes reading and exercices ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "=> ")
    st_write(s.project.pres.paragraphs.p_xl, "+/- 100 hours / student / project ")
    st_write(s.project.pres.paragraphs.p_xl, "Report writing = +/- 40% = 40h ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "-> ",
        (s.project.colors.bright_red + s.bold, "5 hours per week average per student over 20 weeks "),
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "If the work period for the project is "),
        (s.project.colors.forest_green + s.bold, "P"),
        (s.project.colors.burnt_orange, " calendar weeksIf work period for a presentation is "),
        (s.project.colors.forest_green + s.bold, "N"),
        (s.project.colors.burnt_orange, " calendar weeks "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "-> each student presentation should present the result of a work of "),
        (s.project.colors.forest_green + s.bold, "(100/P)*N hours"),
        (s.project.colors.burnt_orange, " of work "),
    )
    st_write(s.project.pres.paragraphs.p_xl, "e.g. project last over 20 calendar weeksif first presentation at week 5 -> (100/20)x5=25 hours of work per student ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Estimation for a report \"fully\" generated without AI: ")
    st_write(s.project.pres.paragraphs.p_xl, "40h*student*project ")
    st_write(s.project.pres.paragraphs.p_xl, "_______ ")
    st_write(s.project.pres.paragraphs.p_xl, "+/- 6h (time to produce one HQ page) ")
    st_write(s.project.pres.paragraphs.p_xl, "= ")
    st_write(s.project.pres.paragraphs.p_xl, "6-8 HQ pages * student ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "GenAI assistant  ")
    st_write(s.project.pres.paragraphs.p_xl, "=> doubles the HQ pages ")
    st_write(s.project.pres.paragraphs.p_xl, "= ")
    st_write(s.project.pres.paragraphs.p_xl, "12-16 HQ pages * student ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Grading: ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Continuous control Q/A grade: ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "50% = 20% + 30% ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Final report ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "50% ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "WARNING ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "As clearly stated above, the objectives of your projects include the following: ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "1) Goal for each student ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "	Demonstrate through the project that parts or all of the ",
        (s.project.colors.forest_green + s.bold, "knowledge and skills"),
        " related to the course learning outcomes have been ",
        (s.project.colors.forest_green + s.bold, "acquired"),
        " (cf. course card). ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "2) ",
        (s.project.colors.forest_green + s.bold, "Produce a Generative Agent"),
        " specialist of a specialized field related to ",
        (s.project.colors.burnt_orange + s.bold, "European Citizens and European Governance"),
        ". ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Regarding the first point provided in the project description, it is mentioned that you should focus on your ability to demonstrate in your presentations and report that the ",
        (s.project.colors.forest_green + s.bold, "knowledge acquired"),
        " during the course ",
        (s.project.colors.forest_green + s.bold, "is well understood"),
        ". ",
    )
    st_write(s.project.pres.paragraphs.p_xl, "This means that the majority of your project should focus on a subset of the concepts, methods and tools in artificial intelligence covered in the course sessions. ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "This implies that ",
        (s.project.colors.forest_green + s.bold, "you should be able to define, explain and illustrate"),
        " the type of artificial intelligence at the ",
        (s.project.colors.forest_green + s.bold, "foundation of your Generative Agent"),
        ".  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "You should also be able to demonstrate that you can ",
        (s.project.colors.forest_green + s.bold, "analyze the quality of your Generative Agent "),
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Ensure that you selected the ",
        (s.project.colors.forest_green + s.bold, "adequate bibliographical references"),
        " necessary to your project aim and adapted to your non scientific and non technical profile. ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "As for the second point, the primary objective of your project is to ",
        (s.project.colors.forest_green + s.bold, "Produce a Generative Agent"),
        " specialist in a ",
        (s.bold, "context freely chosen"),
        " based on your master program and personal interests.  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "You must therefore be very careful to ",
        (s.project.colors.forest_green + s.bold, "keep the focus on generative artificial intelligence"),
        " and its contribution to the context of interest. ",
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Use this information to regularly check that you are on the right track with your project or make adjustments to redirect your efforts if necessary. ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Do not hesitate to send me a preliminary version of your presentation/report well in advance if you would like feedback. ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Sending your slides: ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "To get advises: ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "-> "),
        (s.bold, " by email "),
        (s.project.colors.dark_purple + s.bold, "at least 1 week before the presentation date & time "),
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "For the evaluation day: ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.bold, "-> by email at least 15' "),
        (s.project.colors.dark_purple + s.bold, "before the presentation date & time"),
    )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
