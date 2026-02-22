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
      #274e13 -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #cc4125 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.olive_green, "AI Bill of Rights", "https://www.whitehouse.gov/ostp/ai-bill-of-rights/"),
        (s.project.colors.bright_red, "MAKING AUTOMATED SYSTEMS WORK FOR THE AMERICAN PEOPLE "),
        tag=t.h5,
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.whitehouse.gov/ostp/ai-bill-of-rights/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.state.gov/risk-management-profile-for-ai-and-human-rights/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.reuters.com/technology/artificial-intelligence/california-governor-vetoes-contentious-ai-safety-bill-2024-09-29/"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.forest_green, "The five principles include: ", tag=t.h6)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Protection from unsafe and ineffective systems ")
        with lst.item():
            pass
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Protection from algorithmic discrimination ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.project.colors.burnt_orange + s.bold, " Data privacy protection ")
        with lst.item():
            pass
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Provisions for",
                (s.bold, " "),
                (s.project.colors.burnt_orange + s.bold, "notice and explanation "),
            )
        with lst.item():
            pass
    st_space(size=2)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Provisions for",
                (s.project.colors.burnt_orange + s.bold, " human alternatives "),
            )
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "BUT ")
    st_space(size=5)
    st_space(size=5)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "The Blueprint for an AI Bill of Rights ",
        (s.project.colors.salmon + s.bold, "is non-binding and does not constitute U.S. government policy"),
        (s.project.colors.salmon, "."),
        " It ",
        (s.project.colors.burnt_orange + s.bold, "does not"),
        " supersede, modify, or direct an interpretation of any existing statute, regulation, policy, or international instrument. It ",
        (s.project.colors.burnt_orange + s.bold, "does not"),
        " constitute binding guidance for the public or Federal agencies and therefore... ",
        (s.project.colors.burnt_orange + s.bold, "does not"),
        " require compliance with the principles described herein. It also ",
        (s.project.colors.burnt_orange + s.bold, "is not determinative of what the U.S. government’s position"),
        (s.bold, " will"),
        " be in any international negotiation.  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Adoption of these principles ",
        (s.project.colors.burnt_orange + s.bold, "may not meet the requirements"),
        " of existing statutes, regulations, policies, or international instruments, or the requirements of the Federal agencies that enforce them.  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "These principles ",
        (s.project.colors.burnt_orange + s.bold, "are not intended to"),
        ", and do not, prohibit or ",
        (s.project.colors.burnt_orange + s.bold, "limit any lawful activity of a government agency"),
        ", including law enforcement, national security, or intelligence activities. ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
