import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

def build():

    class BStyles:
        Giant = s.text.sizes.Giant_size
        LARGE = s.text.sizes.LARGE_size
        large = s.text.sizes.large_size

        bold = s.text.weights.bold_weight
        green = s.project.colors.green_01

        center_txt = s.text.alignments.center_align
        center_container = s.container.layouts.center

        blue = s.project.colors.blue_dark_01
        bronze =  s.project.colors.bronze_01 
        
        bronze_under = bronze + s.text.decors.underline_text + Giant 
        green_title = s.project.titles.title_giant_green_01
        red_title = s.project.titles.title_red_01 
        blue_bold = blue + bold
        blue_sub = s.project.titles.subtitle_blue_01

    bs = BStyles

    with st_block(bs.center_txt + bs.LARGE):
        
        st_write(bs.green_title + bs.center_txt, "Domains", toc_lvl='1')
        st_space("v", 3)
        st_write(bs.red_title, (bs.bronze_under, "A"), "rtificial ", (bs.bronze_under, "I"), "ntelligence",
                 toc_lvl='+3')
        st_space("v", 3)
        st_write(s.project.colors.orange_01 + bs.Giant, "...")        
        st_space("v", 3)
        st_image(uri="monkey_01.jpg")
        st_space("v", 3)
        st_write(bs.red_title, (bs.bronze, 'A'), "rticifical", toc_lvl='+3')
        st_br()

        with st_list(lt.unordered, li_style=bs.LARGE + bs.center_container) as l: 
            with l.item(): st_write("man-made?")
            with l.item(): st_write("non-natural?")
            
        st_space("v", 3)
        st_write(bs.red_title, (bs.bronze, 'I'), "ntelligence", toc_lvl='+3')
        
        with st_block(bs.LARGE):
            with st_list(lt.unordered, li_style=bs.center_container) as l: 
                with l.item(): st_write("not stupid?")
                with l.item(): st_write("ability to acquire and apply knowledge and skills?")
                with l.item(): st_write("adaptation capabilities?") 
        
        st_space("v", 3)
        st_write(bs.bronze, 
                 "\"Faculty of understanding, conceiving, knowing, and in particular the ability to discern or ",
                 (bs.blue_bold, "establish relationships between facts, ideas or forms to achieve knowledge."),
                 "<br/><br/> Aptitude to ",
                 (bs.blue_bold, "adapt a behavior to a new situation"), 
                 ", a skill that is shown in a given situation, skill demonstrated by the choice of means that are used to achieve a specific result.\""
            )
        st_br()
        st_write(bs.blue_sub, "_", link="https://www.dictionnaire-academie.fr/article/A9I1608")
        st_space("v", 6)
        
        st_write(bs.green + bs.bold + s.text.sizes.Large_size,
                "\"Viewed narrowly, there seems to be almost ",
                (bs.bronze, "as many definitions"), " of intelligence ",
                (bs.bronze, "as"), " there were ", (bs.bronze, "experts"), " asked to define it.\"")
        
        st_space("v", 1)
        st_write(s.text.decors.italic_text + bs.large, "Sternberg R. (2004). intelligence. </br> In The Oxford Companion to the Mind. : Oxford University Press.")
        st_br()
        
        with st_block(s.container.layouts.span_center):
            st_write(bs.blue_sub, "_", link="https://arxiv.org/pdf/0706.3639.pdf")
            st_space("h") 
            st_write(bs.blue_sub, "_", link="https://www.arxiv-vanity.com/papers/0712.3329/")

        st_space("v", 3) 
        st_write(s.project.titles.subtitle_purple_01, "Going Deeper: ", toc_lvl='+4')
        
        with st_list(lt.ordered, li_style = bs.large + bs.center_txt) as l:
            with l.item():
                st_write("Legg, S., & Hutter, M. (2007). A collection of definitions of intelligence. Frontiers in Artificial Intelligence and applications, 157, 17.")
                st_space() 
                st_write(bs.blue_sub, "_", link="https://arxiv.org/pdf/0706.3639.pdf")
            
            with l.item():
                st_write("Legg, S., & Hutter, M. (2007). Universal intelligence: A definition of machine intelligence. Minds and machines, 17, 391-444. ")
                st_space()
                st_write(bs.blue_sub, "_", link="https://www.arxiv-vanity.com/papers/0712.3329/")
