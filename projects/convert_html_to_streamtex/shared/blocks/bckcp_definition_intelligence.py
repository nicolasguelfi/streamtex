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
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h2, "8.1.  Definitions of intelligence ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Legg, S., & Hutter, M. (2007). A collection of definitions of intelligence. Frontiers in Artificial Intelligence and applications, 157, 17. (",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "link", "https://arxiv.org/pdf/0706.3639.pdf"),
                ") ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Legg, S., & Hutter, M. (2007). Universal intelligence: A definition of machine intelligence. Minds and machines, 17, 391-444. (",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "link", "https://www.arxiv-vanity.com/papers/0712.3329/"),
                ") ",
            )
    st_space(size=1)
    st_space(size=1)
