"""Hover effects and link preview demonstration."""

import streamlit as st
from streamtex import *
from streamtex.styles import Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s


class BlockStyles:
    """Styles for hover and preview demo."""

    heading = s.project.titles.section_title + s.center_txt
    section = s.project.titles.section_subtitle
    feature_box = Style(
        "background:rgba(100,150,200,0.1);padding:16px;border-radius:8px;border-left:4px solid rgba(100,150,200,0.5);",
        "feature_box",
    )
    demo_container = Style(
        "background:rgba(200,150,100,0.08);padding:12px;border-radius:6px;",
        "demo_container",
    )


bs = BlockStyles


def build():
    """Demonstrate hover effects and link preview."""

    st_write(bs.heading, "Hover Effects & Link Preview", tag=t.h1, toc_lvl="1")
    st_space("v", 2)

    # Section 1: Overview
    st_write(bs.section, "Automatic Hover Effects", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.feature_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Feature: "),
            "StreamTeX automatically adds hover preview cards for any links "
            "in your content when you enable hover effects.",
        )
    st_space("v", 2)

    # Section 2: How Hover Works
    st_write(bs.section, "How Hover Preview Works", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "When you hover over a link with ",
        (s.text.weights.bold_weight, "hover=True"),
        " enabled, a preview card appears showing:",
    )
    st_space("v", 1)

    with st_list(list_type="ul"):
        st_write(s.medium, "Page title from meta tags (if available)")
        st_write(s.medium, "Brief description")
        st_write(s.medium, "Favicon from the domain")
        st_write(s.medium, "Preview thumbnail (if available)")

    st_space("v", 2)

    # Section 3: When to Use
    st_write(bs.section, "When to Use Hover Preview", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Hover preview is enabled by default in st_write() when you include links.",
    )
    st_space("v", 1)

    with st_block(bs.feature_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Perfect for: "),
            "Documentation, tutorials, references, and educational content "
            "where users benefit from quick previews of linked resources.",
        )

    st_space("v", 2)

    # Section 4: Demo with Real Links
    st_write(bs.section, "Live Demo: Hover Over Links", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Try hovering over these links to see the preview card appear:",
    )
    st_space("v", 2)

    with st_block(bs.demo_container):
        st_write(
            s.large,
            "Popular StreamTeX Resources:",
            tag=t.div,
        )
        st_space("v", 1)

        st_write(
            s.medium,
            "• ",
            (s.project.colors.primary_blue, "Documentation", "https://github.com/streamtex"),
        )
        st_space("v", 0.5)

        st_write(
            s.medium,
            "• ",
            (s.project.colors.primary_blue, "PyPI Package", "https://pypi.org/project/streamtex"),
        )
        st_space("v", 0.5)

        st_write(
            s.medium,
            "• ",
            (s.project.colors.primary_blue, "GitHub Repository", "https://github.com/streamtex/streamtex"),
        )

    st_space("v", 2)

    # Section 5: Code Examples
    st_write(bs.section, "Code Examples", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.medium + s.text.weights.bold_weight, "Enable hover (default):")
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
from streamtex import st_write

# Hover is ON by default
st_write(
    s.medium,
    "Check out ",
    (s.text.colors.blue, "this link", "https://example.com"),
    " for more info"
)
""")

    st_space("v", 2)

    st_write(s.medium + s.text.weights.bold_weight, "Disable hover (if needed):")
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
from streamtex import st_write

# Turn off hover preview for this link
st_write(
    s.medium,
    "External link: ",
    (s.text.colors.blue, "no preview", "https://example.com"),
    hover=False  # Disable preview for this specific link
)
""")

    st_space("v", 2)

    # Section 6: Advanced: Customize Links
    st_write(bs.section, "Advanced: Links with Styling", toc_lvl="+1")
    st_space("v", 1)

    st_write(
        s.medium,
        "Combine link styling with hover for rich interactive experiences:",
    )
    st_space("v", 1)

    with st_block(s.project.containers.code_box):
        st_code("python", """\
from streamtex import st_write
from streamtex.styles import Style

# Custom link style
link_style = s.medium + s.text.weights.bold_weight + s.text.colors.primary_blue

st_write(
    link_style + s.text.decors.underline_text,
    (link_style, "Important Reference", "https://example.com"),
    "with hover preview enabled by default"
)
""")

    st_space("v", 2)

    # Section 7: Best Practices
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    with st_list(list_type="ol"):
        st_write(
            s.medium,
            "Keep hover ON for external references and documentation links",
        )
        st_write(
            s.medium,
            "Use underline or color to indicate links visually",
        )
        st_write(
            s.medium,
            "Include meaningful link text (not 'click here')",
        )
        st_write(
            s.medium,
            "Disable hover only for internal navigation or UI links",
        )
        st_write(
            s.medium,
            "Test with various URLs to see different preview formats",
        )

    st_space("v", 3)
