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
      #434343 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "5.8.5. AI Act ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "MAIN TEXTProposal for a REGULATION OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL LAYING DOWN HARMONISED RULES ON ARTIFICIAL INTELLIGENCE (ARTIFICIAL INTELLIGENCE ACT) AND AMENDING CERTAIN UNION LEGISLATIVE ACTS ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52021PC0206")
        with g.cell():
            st_write(s.project.doc.tables.cell, "ANNEXES ", "to the Proposal for a Regulation of the European Parliament and of the Council LAYING DOWN HARMONISED RULES ON ARTIFICIAL INTELLIGENCE (ARTIFICIAL INTELLIGENCE ACT) AND AMENDING CERTAIN UNION LEGISLATIVE ACTS ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://perma.cc/TDM7-WQL9")
        with g.cell():
            st_write(s.project.doc.tables.cell, "European ParliamentAI Act: a step closer to the first rules on Artificial Intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.europarl.europa.eu/news/en/press-room/20230505IPR84904/ai-act-a-step-closer-to-the-first-rules-on-artificial-intelligence")
        with g.cell():
            st_write(s.project.doc.tables.cell, "European ParliamentProposal for a Regulation on a European approach for Artificial Intelligence ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-regulation-on-artificial-intelligence")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Artificial Intelligence Act Website ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://artificialintelligenceact.com/")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "Do Foundation Model Providers Comply with the Draft EU AI Act? ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.italic, "Do foundation model providers comply with the EU AI Act?"),
        " Stanford Center for Research on Foundation Models. ",
    )
    st_write(s.project.doc.paragraphs.p_body, "Bommasani, R. & al. (2023, June 15).  ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://crfm.stanford.edu/2023/06/15/eu-ai-act.html", link="https://crfm.stanford.edu/2023/06/15/eu-ai-act.html")
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.doc.paragraphs.p_lg + s.project.colors.link_blue, "_", link="https://crfm.stanford.edu/2023/06/15/eu-ai-act.html?utm_source=chatgpt.com")
    st_space(size=2)
    st_space(size=2)
