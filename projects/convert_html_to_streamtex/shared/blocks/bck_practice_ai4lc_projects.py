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
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #660000 -> s.project.colors.deep_red
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #cc0000 -> s.project.colors.bright_red
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "AI"),
        (s.project.colors.forest_green, "4"),
        (s.project.colors.dark_purple, "LC"),
        (s.project.colors.link_blue, " "),
        (s.project.colors.purple + s.bold, "Projects"),
    )
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
            st_write("Produce a Generative Agent specialist of a specialized field  of AI for Languages & Cultures: ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.deep_red + s.bold, "AI as a Tool for L&C in Education ")
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, "AI-Powered Product for L&C")
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
    st_space(size=3)
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
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Workload: ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl, "2 ECTS = 2 * 30 hours = 60 hours / student ")
    st_write(s.project.pres.paragraphs.p_xl, "16h = 5 * 3h15 -> lectures ")
    st_write(s.project.pres.paragraphs.p_xl, "8h =  4 x 2h -> lectures notes reading and exercices ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "=> ")
    st_write(s.project.pres.paragraphs.p_xl, "+/- 36 hours / student / project ")
    st_write(s.project.pres.paragraphs.p_xl, "Report writing = +/- 50% = 18h / student / project ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Estimation for a report "),
        (s.project.colors.bright_red + s.bold, "\"NOT\""),
        (s.project.colors.bright_red + s.bold, " generated with AI: "),
    )
    st_write(s.project.pres.paragraphs.p_xl, "15h*student*project ")
    st_write(s.project.pres.paragraphs.p_xl, "_______ ")
    st_write(s.project.pres.paragraphs.p_xl, "6-8h (time to produce a HQ page) ")
    st_write(s.project.pres.paragraphs.p_xl, "= ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "2-3 ",
        (s.project.colors.bright_red + s.bold, "HQ"),
        " pages * student ",
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "GenAI assistant  ")
    st_write(s.project.pres.paragraphs.p_xl, "=> doubles the HQ pages ")
    st_write(s.project.pres.paragraphs.p_xl, "= ")
    st_write(s.project.pres.paragraphs.p_xl, "4-6 HQ pages * student ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.bold, "For a group of "),
        (s.project.colors.bright_red + s.bold, "3"),
        (s.bold, " students "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.bold, "-> report = "),
        (s.project.colors.bright_red + s.bold, "12 - 18"),
        (s.project.colors.bright_red + s.bold, " HQ pages "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Grading: ", tag=t.h3)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Project Presentation Group Grade: ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "50% ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Final report ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "50% ")
    st_space(size=3)
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
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.deep_red, "Possible Generic Structure ", tag=t.h3)
    st_write(s.project.pres.titles.h3 + s.project.colors.deep_red, "for your oral Presentation  ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Remark"),
        ": 3' per student means 4 to 8 lightweight slides ",
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "Possible slides decomposition(for each student) ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(" main objectives and qualities of the individual personas allocated to the student ")
        with lst.item():
            st_write(" example of 1 or 2 questions sent together with the persona's answer ")
        with lst.item():
            st_write(" Presentation of a persona definition text ")
        with lst.item():
            st_write(" Persona definition process (3 slides) ")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Advises : ")
    st_write(s.project.pres.paragraphs.p_xl, "- slide content should be made of few words and images/diagrams when possible ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "- what you say orally provides additional details",
        (s.bold, "Rehearse your oral presentation in advance. "),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "You need to stick to the 3' ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------------------------------------------------------------------- ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "D DAY -> Sending your slides: ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Send me your slides by email at least 15' before the planned date and time of the class presentations. ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "--------------------------------------------------------------------------------- ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
