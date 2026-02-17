import streamlit as st
import blocks
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

"""
List of st_* functions implemented in the StreamTeX library:

- function()    # parameters

- st_book()     # module_list
- st_write()    # style, txt, link, hover, no_link_decor, tag, toc_lvl, label
- st_image()    # style, width, height, uri, alt, link, hover
- st_space()    # direction, size
- st_br()       #
- st_include()  # module
# context managers
- st_block()    # style
- st_span()     # style
- st_list()     # list_type, l_style, li_style
- st_grid()     # cols, grid_style, cell_styles
- st_overlay()  # style


-----------------------------------

Hierarchy of Styles:


Styles:
- `none`: base style
- `text`: Text Styles enum
- `container`: Container (divs) styles enum
- `visibility`: Element visibility enum (hidden, visible or invisible)
- `project`: User defined styles enum

text
- `decors`: Italic, underline, and no-decoration styles.  
- `weights`: Bold, light, and normal text weights.  
- `alignments`: Text alignment styles (left, center, right).  
- `colors`: Foreground color styles.  
- `bg_colors`: Background color styles.  
- `sizes`: Font size styles (em, px, and pt units).  
- `fonts`: Font families for various types (sans-serif, serif, monospace, etc.).

container
- `sizes`: Container width and height.  
- `bg_colors`: Background color styles.  
- `borders`: Border styles.  
- `paddings`: Padding styles.  
- `margins`: Margin styles.  
- `layouts`: Layout options (e.g., flexbox, table).  
- `flex`: Flexbox-specific layout properties.  
- `lists`: List-specific styles (e.g., Google Docs style).

project
- `colors`: User-defined colors.  
- `titles`: Custom title and subtitle styles. 

"""

class BlockStyles:
    """Custom styles for this block."""
    header_style = s.Giant + s.text.colors.blue + s.center_txt
    grid_cell_style = ns("border: 1px solid gray;") + s.container.paddings.little_padding + s.center_txt
    list_item_style = s.text.colors.green + s.bold
    table_style = s.container.paddings.medium_padding
    
    # google colors
    blue = s.text.colors.alexandra
    red = s.text.colors.vermillion
    yellow = s.text.colors.royal_gold
    green = s.text.colors.retro_green
    
bs = BlockStyles


def build():

    # st_write example
    st_write(bs.header_style, "Dynamic StreamTeX Web page Example", tag=t.h1)

    # st_space example (horizontal)
    st_space("h", "20px")  # Horizontal space for layout adjustment

    # st_write example (with all parameters, must be keyword arguments)
    st_write(s.text.colors.olive,
        'example link',
        tag=t.div,
        link="https://example.com/",
        no_link_decor=True,
        hover=False,
        toc_lvl="1", label="Example ToC Label")
    
    # st_write example (global style + multi-style text)
    st_write(s.text.sizes.Large_size, 
        (bs.blue, 'G'),(bs.red, 'o'),(bs.yellow, 'o'),(bs.blue, 'g'),(bs.green, 'l'),(bs.red, 'e'),
        link="https://google.com/",
        no_link_decor=True)
    
    # st_write example (full use of (style, txt, link) tuple parameters)
    st_write(s.text.sizes.big_size, 
        "It is possible to mix", (s.italic, " different "), 
        "styles this way, you can even make only certain parts of the text contain a ",
        (s.none, "link", "https://example.com/"), "!")
    
    # st_space example (vertical)
    st_space("v", "2em")  # Vertical space

    # st_list example
    with st_list(
        list_type=lt.unordered,
        l_style=s.none,
        li_style=bs.list_item_style
        ) as l:
        with l.item(): st_write("List Item 1")
        with l.item(): 
            st_write("List Item 2")
            with st_list() as l2:
                with l2.item(): st_write("Nested Item 1")
                with l2.item(): st_write("Nested Item 2")
    # This block produces the following nested bullet point list
    '''
    - List Item 1
    - List Item 2
        * Nested Item 1
        * Nested Item 2
    '''

    # st_image example
    st_image(
        style=s.none,
        width="1000px",
        height="100%",
        uri="placeholder.png",
        alt="Placeholder Image",
        link="https://example.com",
        hover=True)

    # st_br example
    st_br()  # Line break

    # st_grid example
    with st_grid(
        cols=3,
        grid_style=s.none,
        cell_styles=bs.grid_cell_style) as g:
        with g.cell(): st_write("Row 1, Col 1")
        with g.cell(): st_write("Row 1, Col 2")
        with g.cell(): st_write("Row 1, Col 3")
        with g.cell(): st_write("Row 2, Col 1")
        with g.cell(): st_write("Row 2, Col 2")
        with g.cell(): st_write("Row 2, Col 3")
    
    # st_grid example (using css grid template strings to create unequal columns)
    with st_grid(
        cols="auto 1fr",
        grid_style=bs.table_style,
        cell_styles=bs.grid_cell_style) as g:
        with g.cell(): st_write("Row 1, Col 1: This column will only be as big as it needs to be")
        with g.cell(): st_write("Row 1, Col 2: This column will occupy the rest of the row space")
        with g.cell(): st_write("Row 2, Col 1: This column will only be as big as it needs to be")
        with g.cell(): st_write("Row 2, Col 2: This column will occupy the rest of the row space")

    # st_grid cell_styles can be a stylegrid (whose operations are as follows: multiplication replaces, addition adds)
    with st_grid(
        cols=3,
        cell_styles = sg.create("A1:B3", s.large) * sg.create("A1:B1, B3", s.text.colors.white + s.container.bg_colors.red_bg)
        ) as g:
        with g.cell(): st_write("A1")
        with g.cell(): st_write("B1")
        with g.cell(): st_write("A2")
        with g.cell(): st_write("B2")
        with g.cell(): st_write("A3")
        with g.cell(): st_write("B3")
    
    with st_block(style=s.center_txt + s.big):
        st_write("This is inside a div.")
        st_write("Normally, st_write defaults to a span tag.")
        st_write("The block styles cascade: All of these are centered")

    with st_span(style=s.bold + s.big):
        st_write("st_block defaults to arranging its contents vertically. ")
        st_write("st_span instead arranges them horizontally in a same line.")
    st_write(s.bold + s.Large, "However, if the line content is to long, it'll overflow, so only use it to align a small amount of content (e.g. aligning small images with text).")
    
    # st_include example
    st_include(block_file_module=blocks.sub_block)
    
    # st_overlay example
    with st_overlay(style=s.Large+bs.red) as o:
        st_image(uri="background.jpg")  # Base layer
            
        with o.layer(top=50, left=50): # 50px top 50px left
            st_write("Overlay Text")


