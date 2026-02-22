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
      #274e13 -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #cc4125 -> s.project.colors.salmon
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.olive_green, "European Parliament\"AI Act\" ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "(Started February 2020) ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52021PC0206"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://www.europarl.europa.eu/news/en/press-room/20230505IPR84904/ai-act-a-step-closer-to-the-first-rules-on-artificial-intelligence"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.europarl.europa.eu/news/en/press-room/20230505IPR84904/ai-act-a-step-closer-to-the-first-rules-on-artificial-intelligence"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-regulation-on-artificial-intelligence"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-regulation-on-artificial-intelligence"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://artificialintelligenceact.com/"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://artificialintelligenceact.com/"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://perma.cc/TDM7-WQL9"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://perma.cc/TDM7-WQL9"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://futurium.ec.europa.eu/sites/default/files/2021-10/Kop_EU%20Artificial%20Intelligence%20Act%20-%20The%20European%20Approach%20to%20AI_21092021_0.pdf"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://futurium.ec.europa.eu/sites/default/files/2021-10/Kop_EU%20Artificial%20Intelligence%20Act%20-%20The%20European%20Approach%20to%20AI_21092021_0.pdf"),
        (s.project.pres.links.link_lg + s.project.colors.bright_red + s.bold, " ", "https://drive.google.com/file/d/1_vGnHE6PgHNCRlJL_lVkqIBq8Ta4vT3j/view"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://drive.google.com/file/d/1_vGnHE6PgHNCRlJL_lVkqIBq8Ta4vT3j/view"),
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.teal + s.bold, "Early 2025 ")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Prohibitions on unacceptable risks come into force. ")
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "General provisions on subject matter, scope, definitions and AI literacy come into force. ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "?? "),
        (s.project.colors.teal + s.bold, "Late summer 2027"),
        (s.project.colors.burnt_orange + s.bold, "?? "),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "    Regulation of high-risk systems within the EU product safety regulation regime (listed in annex I) come into force. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Objectives ", tag=t.h6)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "1. ",
        (s.project.colors.forest_green + s.bold, "Safe AI"),
        " that respect the ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "fundamental rights"),
        " and Union values ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "2. Ensure legal certainty to ",
        (s.project.colors.forest_green + s.bold, "facilitate investment"),
        " and innovation in AI ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "3. ",
        (s.project.colors.forest_green + s.bold, "Single coherent market"),
        " for lawful, safe and trustworthy AI applications ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "‘Artificial Intelligence system’ (AI system) ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold + s.italic, "Initial definition proposal ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, "Developed using: ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "Generate"),
                " outputs such as ",
                (s.project.colors.forest_green + s.bold, "content"),
                ", predictions, recommendations, or decisions ",
                (s.project.colors.forest_green + s.bold, "influencing user's environments "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "BUT ")
    st_space(size=5)
    st_space(size=5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.forest_green + s.bold, "July 2023 ")
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=1)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "January 2024 for March 13th vote "),
        (s.project.colors.bright_red, "(voted!) "),
        tag=t.h6,
    )
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.pres.titles.h6 + s.project.colors.link_blue, "_", tag=t.h6)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "April 2024 "),
        (s.project.colors.bright_red, "(amended!)"),
        tag=t.h6,
    )
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Risk-based approach with "),
        (s.project.colors.burnt_orange, "THREE levels"),
        (s.project.colors.dark_purple, ":"),
        tag=t.h6,
    )
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "Risk Level ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Description ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Measure ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "unacceptable ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "Harmful"), " uses of AI that ", (s.project.colors.bright_red + s.bold, "contravene EU values"), " (such as social scoring by governments) ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "banned ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange + s.bold, "High-Risk ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Creating adverse impact on people's ", (s.project.colors.burnt_orange + s.bold, "safety"), " or their ", (s.project.colors.burnt_orange + s.bold, "fundamental rights "))
        with g.cell():
            st_write(s.project.pres.tables.cell, "mandatory requirements (including an EU conformity assessment) ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green + s.bold, "low or minimal ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "All other AI systems ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "None or limited set of obligations (e.g. transparency) ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "High-risk sectors")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "biometric ",
                (s.project.colors.forest_green + s.bold, "identification"),
                (s.bold, " "),
                (s.project.colors.forest_green + s.bold, "and categorization"),
                " of natural persons ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "management and operation of ",
                (s.project.colors.forest_green + s.bold, "critical infrastructure "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "access to ",
                (s.project.colors.forest_green + s.bold, "education"),
                " and vocational training and ",
                (s.project.colors.forest_green + s.bold, "assessing students"),
                " for these purposes ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "employment"),
                ", workers management, and access to self-employment (",
                (s.project.colors.forest_green + s.bold, "recruitment, promotion, termination"),
                ") ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "access to and enjoyment of ",
                (s.project.colors.forest_green + s.bold, "essential private or public services"),
                " and benefits ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "law enforcement"),
                " (individual risk assessments, polygraphs or similar tools, deep fake detection, evaluation of the reliability of evidence, predictive policing, profiling, crime analytics regarding natural persons) ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "migration, asylum, and ",
                (s.project.colors.forest_green + s.bold, "border control"),
                " management ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "administration of ",
                (s.project.colors.forest_green + s.bold, "justice and democratic processes "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "Transparency obligations for systems that")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "(i) ",
        (s.project.colors.forest_green + s.bold, "interact with humans"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "(ii) are used to ",
        (s.project.colors.forest_green + s.bold, "detect emotions"),
        " or determine association with (social) ",
        (s.project.colors.forest_green + s.bold, "categories based on biometric data"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "(iii) ",
        (s.project.colors.forest_green + s.bold, "generate or manipulate content"),
        " (‘deep fakes’).  ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "TOOLS ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "EU ")
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.link_blue, "EU AI Act Compliance Checker", tag=t.h1, toc_lvl="1")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=5)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "... and "),
        (s.project.colors.burnt_orange + s.bold, "... "),
    )
    st_space(size=5)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "First"),
        (s.project.colors.bright_red + s.bold, " law ... "),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "which impact for Europein the "),
        (s.project.colors.salmon + s.bold, "AI race"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "? ")
    st_space(size=5)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "BUT ...")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
