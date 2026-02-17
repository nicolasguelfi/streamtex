import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
import blocks.trainer_ng_competencies_se_bck


def build(
    trainer_name="Nicolas Guelfi",
    trainer_image="ng_black_white.png",
    trainer_link="https://drive.google.com/file/d/1FaGAxN4-zK2YUBeXsYJsxj3BWA3eJUas/view",
    logo_unilu="logo_unilu.png",
    logo_pi="logo_pi.png",
    logo_unige="logo_unige.png",
    logo_ros="logo_ros.png",
    linkedin_url="https://www.linkedin.com/in/nicolas-guelfi-phd/",
    linkedin_logo="logo_linkedin.gif"
):
    
    center = s.text.alignments.center_align
    g_lists = s.container.lists.g_docs
    large = s.text.sizes.large_size
    Large = s.text.sizes.Large_size
    bronze = s.project.bronze_01_bold
    fit = s.container.layouts.fit + s.container.paddings.size("0", "0.5em", "0", "0")
    center_container = s.container.layouts.center
    
    st_write("This is a link.", link="https://www.google.com", toc_lvl='2')
    
    with st_block(center):
        st_write(s.project.titles.title_purple_01, "Who?")
        st_space("v", 2)
        st_write(s.project.titles.title_green_01, "Trainer(s)", toc_lvl='2')
        st_space("v", 2)
        st_write(s.project.titles.subtitle_blue_01, 
                             trainer_name,
                             link=trainer_link, no_link_decor=True,
                             toc_lvl='+1')
        st_space("v", 2)
        st_image(uri = trainer_image, width="358px")
        
    with st_grid(2,
            grid_style=s.project.low_pad+s.container.layouts.table_layout,
            cell_styles=s.project.low_pad) as g:
        with g.cell(): 
            with st_list(lt.unordered, g_lists, bronze + Large) as l:
                with l.item():
                    st_write("Activities")
                    with st_list(lt.unordered, g_lists, s.reset + large) as l2:
                        with l2.item(): st_write("Education / Training")
                        with l2.item(): st_write("Research / Development")
        
        with g.cell():
            st_include(blocks.trainer_ng_competencies_se_bck)
        
        with g.cell():     
            with st_list(lt.unordered, g_lists, bronze + Large) as l:
                with l.item():
                    st_write("Contexts")
                    with st_list(lt.unordered, g_lists, s.reset + large) as l2:
                        with l2.item():
                            st_write("University of Luxembourg")
                            with st_span():
                                st_image(fit, uri = logo_unilu, height="75px", link="https://www.uni.lu/fstm-en/people/nicolas-guelfi/")
                                st_image(fit, uri = logo_pi, height="75px")
                                st_image(fit, uri = logo_unige, height="75px")
                        with l2.item():
                            with st_block():
                                st_write("Right-On-Skill sarl")
                                st_image(uri = logo_ros, width="33%")
        with g.cell():
            with st_list(lt.unordered, g_lists, s.project.green_01_bold + Large) as l:
                with l.item():
                    st_write("Artificial Intelligence")
                    with st_list(lt.unordered, g_lists, s.reset + large) as l2:
                        with l2.item(): st_write("Generative AI")
                        with l2.item(): st_write("Deep Learning")
                        with l2.item(): st_write("Expert Systems")
    
    with st_block(Large + center_container): # centers the content in the page container
        with st_list(lt.unordered, g_lists, center) as l: # centers the content inside the bullet point container
            with l.item():
                st_write("More information")
                st_image(uri = linkedin_logo, link=linkedin_url, width="250px")