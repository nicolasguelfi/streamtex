import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Image demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles

# Sample image URLs for portability
theImageURL = "https://picsum.photos/seed/streamtex1/400/250"
theImageURL2 = "https://picsum.photos/seed/streamtex2/400/250"


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Images", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # Basic image
        st_write(bs.sub, "st_image with URL", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Display images from URLs, local paths, or base64
            with st_image().
        """))
        st_space("v", 1)

        show_code(file="examples/image/image_url.py")
        st_space("v", 1)

        st_image(uri=theImageURL, alt="Sample landscape image")
        st_space("v", 2)

        # Width and height
        st_write(bs.sub, "Width and height control", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control image dimensions with width and height parameters.
        """))
        st_space("v", 1)

        show_code(file="examples/image/image_dimensions.py")
        st_space("v", 1)

        exec_static("examples/image/image_dimensions.py")
        st_space("v", 2)

        # Styled image
        st_write(bs.sub, "Image with style", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Apply StreamTeX styles (borders, padding) to images.
        """))
        st_space("v", 1)

        bordered_img = (s.container.borders.solid_border
                        + s.container.paddings.tiny_padding)
        show_code(file="examples/image/image_styled.py")
        st_space("v", 1)

        st_image(bordered_img, uri=theImageURL2,
                 width="300px", alt="Bordered image")
        st_space("v", 2)

        # Image with link
        st_write(bs.sub, "Image as a link", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Wrap an image in a clickable link with the link parameter.
        """))
        st_space("v", 1)

        theURL = "https://docs.streamlit.io"
        show_code(file="examples/image/image_link.py")
        st_space("v", 1)

        st_image(uri=theImageURL2, width="300px",
                 link=theURL,
                 alt="Click to visit Streamlit docs")
        st_space("v", 2)

        # configure_image_path
        st_write(bs.sub, "configure_image_path()", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Sets the base path for resolving relative image filenames.
        """))
        st_space("v", 1)

        show_code(file="examples/image/image_configure_path.py")
        st_space("v", 1)

        show_details(textwrap.dedent("""\
            Defaults: width="100%", height="auto", link="", hover=True.
            Always set the alt parameter for accessibility.
            The alt text is used by screen readers
            and displayed when images fail to load.
        """))
