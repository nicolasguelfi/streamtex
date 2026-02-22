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
      #2f5a1b -> s.project.colors.forest_green
      #5b0f00 -> s.project.colors.deep_red
      #980000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #999999 -> s.project.colors.gray
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.pres.paragraphs.p_md + s.project.colors.link_blue, "_", link="https://docs.google.com/document/d/1txFL_2iyf3umwhowqhRh67ASexGxOS9jcAUIBl2hQ3U/edit?tab=t.0#heading=h.fmzggzy1qs97")
    st_space(size=2)
    st_space(size=2)
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Applied Generative AI for Webmasters ", tag=t.h5)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h5 + s.project.colors.burnt_orange, "Introduction to WordPress ", tag=t.h5)
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.purple, "Agenda", tag=t.h5)
    with st_grid(cols=1, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
    st_space(size=2)
    with st_grid(cols=1, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "What is WordPress? ", tag=t.h1, toc_lvl="1")
    st_space(size=2)
    with st_grid(cols=1, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "Initially: blogging platform. ", "Now: Engine for websites, blogs & e-commerce websites (WooCommerce) ", "Backed by WordPress.com company ", "Content Management System (CMS) ", "Open-Source ", "Easy to Learn ", "Customizable ")
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Who uses WordPress? ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "Meta Newsroom")
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.deep_red + s.bold, "Time Magazine ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.deep_red + s.bold, "The Rolling Stones ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.deep_red + s.bold, "Taylor Swift ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.deep_red + s.bold, "NASA ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.deep_red + s.bold, "Katy Perry ")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "& many more.")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h5 + s.project.colors.purple, "Who uses WordPress? ", tag=t.h5)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_write(s.project.pres.paragraphs.p_sm + s.project.colors.gray, "Source: https://www.wpzoom.com/blog/wordpress-statistics")
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Why WordPress? ", tag=t.h1, toc_lvl="1")
    st_space(size=2)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Cost-Effective ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "Free to use and open-source with a wide range of free themes and plugins. ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Self-host WordPress ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Very cheap to start, e.g. ",
                (s.project.colors.forest_green + s.bold, "4€/month "),
            )
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "> 70,000 plugins ")
        with g.cell():
            st_write(s.project.pres.tables.header, (s.bold, "> "), (s.project.colors.forest_green + s.bold, "30,000"), (s.bold, " plugins "))
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Most of them are free!")
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Ease of Use ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "User-friendly dashboard that allows content management without extensive technical knowledge. ")
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Customization & Flexibility ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "Easily tailor your site’s design and functionality to fit your specific needs. ")
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue, "Themes")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue, "Plugins")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Design & layout ", "Advanced page builder ", "Customisation options ", "Simple vs. Complex ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Analytics ", "Forms ", "CMS plugins (e.g. Recipes) ", "E-commerce (WooCommerce) ")
    st_write(s.project.pres.paragraphs.p_lg + s.bold, "Free & Paid options ")
    st_write(s.project.pres.paragraphs.p_lg, "Themes x Plugins = endless customisation options ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Strong Community Support ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Extensive documentation, forums, and regular community updates ensure help is always available. ")
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "WordPress Forums", "https://wordpress.org/support/forums/"),
                "Supported by a vast network of developers and enthusiasts contributing themes, plugins, and updates. ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.pres.links.link_lg + s.project.colors.link_blue, "WordPress Support", "https://wordpress.com/support/"),
                "Guides for WordPress with detailed explanation of each of the features. ",
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Scalable Platform ", tag=t.h5)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl, "Suitable for everything from a personal blog to a full-fledged eCommerce website. ")
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Security-Focused ", tag=t.h5)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Regular updates and a strong community contribute to a secure environment when best practices are followed. ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("WordPress.com dedicated Security Team ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Popular plugin & theme updated often")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Demo ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple + s.italic, "Practical", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Applied Generative AI for Webmasters ", tag=t.h5)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.titles.h5 + s.project.colors.burnt_orange, "WordPress AI plugins", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.forest_green, "Chatbot Integrations ", tag=t.h5)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl, "- AI integrations are a moving target ")
    st_write(s.project.pres.paragraphs.p_xl, "  → New model capabilities = new possibilities for websites ")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_write(s.project.pres.paragraphs.p_xl, "- For most use cases: ChatGPT or Quasible ")
    st_write(s.project.pres.paragraphs.p_xl, "- For chatbots:")
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=2)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "Demo ", tag=t.h1, toc_lvl="1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple + s.italic, "Practical", tag=t.h1, toc_lvl="1")
    st_space(size=2)
