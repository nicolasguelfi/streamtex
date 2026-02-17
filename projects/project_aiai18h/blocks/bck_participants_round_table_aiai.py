import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

class BlockStyles:
    border = s.container.borders.color(s.text.colors.black) + s.container.borders.solid_border + s.container.borders.size("2px")
bs = BlockStyles


def build():
    
    with st_block(s.text.alignments.center_align):
        st_write(s.project.titles.title_green_01, "Participant(s)", toc_lvl='2')
        st_br()
        st_write(s.project.titles.subtitle_blue_01, "Individual presentations", toc_lvl='+1')

    with st_grid(2,
            grid_style=s.text.sizes.large_size,
            cell_styles=bs.border + s.container.paddings.small_padding) as g:
            # Left Column
            with g.cell():
                with st_list(lt.unordered, li_style=s.text.sizes.large_size) as l:
                    with l.item(): st_write("First name")
                    with l.item(): st_write("Main Activities")
                    with l.item(): 
                        st_write(f"Motivations for participating to ", (s.project.bronze_01_bold, "AIAI"))

            # Right Column
            with g.cell():
                with st_list(lt.unordered, li_style=s.text.sizes.large_size) as l:
                    with l.item(): st_write("Experience (if any)")
                    with l.item(): st_write("sciences")
                    with l.item(): st_write("technologies")
                    with l.item(): st_write("articifical intelligence")
