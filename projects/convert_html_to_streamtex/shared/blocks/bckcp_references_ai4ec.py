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
      #7f6000 -> s.project.colors.gold
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "5. References ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Abramson, Darren et al. ",
                (s.italic, "Artificial Intelligence and Human Enhancement :  : Affirmative and Critical Approaches in the Humanities /"),
                ". Ed. Herta Nagl-Docekal and Waldemar Zacharasiewicz. Berlin ; De Gruyter, 2022. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Carter, Matt. ",
                (s.italic, "Minds and Computers :  :"),
                (s.project.doc.links.link_body + s.italic, " ", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9922826710007251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,Introduction%20to%20Artificial%20Intelligence,AND&facet=searchcreationdate,include,2020%7C,%7C2024&mode=advanced&offset=0"),
                (s.project.doc.links.link_body + s.project.colors.link_blue + s.italic, "An Introduction to the Philosophy of Artificial Intelligence", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9922826710007251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,Introduction%20to%20Artificial%20Intelligence,AND&facet=searchcreationdate,include,2020%7C,%7C2024&mode=advanced&offset=0"),
                (s.italic, " /"),
                ". Edinburgh: Edinburgh University Press, 2022. Web. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Sepasspour, R. (2023). A reality check and a way forward for the global governance of artificial intelligence. ",
                (s.italic, "Bulletin of the Atomic Scientists"),
                ", ",
                (s.italic, "79"),
                "(5), 304–315.",
                (s.project.doc.links.link_body, " ", "https://doi-org.proxy.bnl.lu/10.1080/00963402.2023.2245249"),
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://doi-org.proxy.bnl.lu/10.1080/00963402.2023.2245249", "https://doi-org.proxy.bnl.lu/10.1080/00963402.2023.2245249"),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DiMatteo, Larry A., Cristina Poncibò, and Michel Cannarsa, eds.",
                (s.project.doc.links.link_body, " ", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9921000584207251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,The%20Cambridge%20Handbook%20of%20Artificial%20Intelligence:%20Global%20Perspectives%20on%20Law%20and%20Ethics,AND&mode=advanced&offset=0"),
                (s.project.doc.links.link_body + s.project.colors.link_blue + s.italic, "The Cambridge Handbook of Artificial Intelligence", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9921000584207251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,The%20Cambridge%20Handbook%20of%20Artificial%20Intelligence:%20Global%20Perspectives%20on%20Law%20and%20Ethics,AND&mode=advanced&offset=0"),
                (s.italic, " :  : Global Perspectives on Law and Ethics /"),
                ". Cambridge, United Kingdom ; Cambridge University Press, 2022. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Voeneky S, Kellmeyer P, Mueller O, Burgard W, eds. ",
                (s.italic, "The Cambridge Handbook of Responsible Artificial Intelligence: Interdisciplinary Perspectives"),
                ". Cambridge University Press; 2022 ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Akram, Faiz et al.",
                (s.project.doc.links.link_body, " ", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9923315360307251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,Introduction%20to%20Artificial%20Intelligence,AND&facet=searchcreationdate,include,2020%7C,%7C2024&mode=advanced&offset=0"),
                (s.project.doc.links.link_body + s.project.colors.link_blue + s.italic, "Toward Artificial General Intelligence :  : Deep Learning, Neural Networks, Generative AI", "https://www.a-z.lu/discovery/fulldisplay?docid=alma9923315360307251&context=L&vid=352LUX_UNI:BIBNET_UNION&lang=fr&search_scope=DN_and_CI_UCV&adaptor=Local%20Search%20Engine&tab=DiscoveryNetwork_UCV&query=title,contains,Introduction%20to%20Artificial%20Intelligence,AND&facet=searchcreationdate,include,2020%7C,%7C2024&mode=advanced&offset=0"),
                (s.italic, " /"),
                ". Ed. Pethuru Raj, Satya Prakash Yadav, and Victor Hugo C. de Albuquerque. Berlin ; De Gruyter, 2023.  ",
            )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "6. Surveys ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.1. Surveys to fill links ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "1")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.gold + s.bold, "Learner Profile")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold, "Click HERE & RightClick & Open in Private Window!", link="https://docs.google.com/forms/d/e/1FAIpQLSfNK3fGeTdBJ50ibzdYv_sxBm5yzTIa6Xt3apWpfxT0NRT72A/viewform")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "2")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "3")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "4")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "7. Shared Folder ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "You can find here other reference files related to the course..")
    st_write(s.project.doc.paragraphs.p_body, "Professor's slides will be uploaded here after the training.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "Training Drive Folder", link="https://drive.google.com/drive/folders/1GwnWZs_RdesbRjU0t6rIbzFCfRHePY80?usp=sharing")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
