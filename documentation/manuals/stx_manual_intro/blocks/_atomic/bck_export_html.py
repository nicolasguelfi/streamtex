import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Export HTML demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Export HTML", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. Download HTML button ---
        st_write(bs.sub, "The Download HTML button", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            st_book() enables HTML export by default.
            A "Download HTML" button appears in the sidebar.
            The exported file is a self-contained HTML document.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Export is enabled by default in st_book()
            st_book([
                blocks.bck_00_welcome,
                blocks.bck_01_architecture,
                # ...
            ], export_title="My Course")

            # The sidebar shows a "Download HTML" button automatically.
        """))
        st_space("v", 2)

        # --- 2. How it works ---
        st_write(bs.sub, "How it works: dual rendering", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Every stx.* content call goes through st_html(),
            which sends HTML to both Streamlit and an export buffer.
            Context managers (st_block, st_grid, st_list) push/pop
            wrapper tags so the exported HTML keeps the nesting structure.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Dual rendering pipeline (simplified)
            #
            #   stx.st_write(...)
            #        |
            #   st_html(html)
            #        |
            #   +----+----+
            #   |         |
            # st.html() buffer.append()
            #              |
            #       generate_full_html()
            #              |
            #     self-contained .html file
        """), language="text")
        st_space("v", 2)

        # --- 3. Customization ---
        st_write(bs.sub, "Customization", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Control the export with the export_title parameter
            and the ExportConfig dataclass.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from streamtex.export import ExportConfig

            # ExportConfig fields:
            #   enabled: bool       = False   (st_book sets this to True)
            #   page_title: str     = "StreamTeX Export"
            #   page_width: str     = "100%"
            #   page_padding: str   = "36pt"

            # The simplest way: just set export_title in st_book()
            st_book([...], export_title="My Document Title")
        """))
        st_space("v", 2)

        # --- 4. Disable export ---
        st_write(bs.sub, "Disabling export", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Pass export=False to st_book() to hide the
            Download button and skip buffer accumulation.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            st_book([
                blocks.bck_00_welcome,
                # ...
            ], export=False)  # No download button
        """))
        st_space("v", 2)

        # --- 5. Details ---
        show_details(textwrap.dedent("""\
            The exported file embeds all CSS and base64 images.
            Interactive features (markers, zoom) are not included.
            The HTML is fully self-contained: no external dependencies.
        """))
        st_space("v", 2)

        # --- 6. ExportConfig detailed ---
        st_write(bs.sub, "ExportConfig: Full configuration", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            ExportConfig is a dataclass that controls every aspect of HTML export.
            Use it for fine-grained control over the exported document.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from streamtex.export import ExportConfig

            config = ExportConfig(
                enabled=True,                    # Enable/disable export
                page_title="My Document",        # <title> tag
                page_width="100%",             # Page width in export
                page_padding="36pt",             # Page padding/margins
                include_styles=True,             # Include all CSS
                include_images=True,             # Embed images as base64
                prettify_html=False,             # Format HTML (slower)
            )

            st_book([...], export_config=config)
        """))
        st_space("v", 2)

        # --- 7. CSS customization ---
        st_write(bs.sub, "Custom CSS in exports", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Add custom CSS rules that only apply to the exported HTML.
            Use for print-specific styling or responsive layouts.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            from streamtex.export import ExportConfig

            # Print-friendly CSS for exports
            export_css = \"\"\"
            @media print {
                body { font-size: 12pt; line-height: 1.5; }
                .no-print { display: none; }
                a { text-decoration: underline; }
            }
            \"\"\"

            # Note: Currently, use inline styles in blocks instead
            # Future: ExportConfig will support custom_css parameter
            st_book([...])
        """))
        st_space("v", 2)

        # --- 8. Image optimization ---
        st_write(bs.sub, "Image handling in exports", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            All images are embedded as base64 in the exported HTML.
            Large images increase file size significantly.
            Optimize images before export for smaller files.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Large images slow down export
            st_image("huge_photo.png")  # ~5MB when embedded

            # Smaller images are better
            st_image("icon.png")  # ~50KB when embedded

            # Use image compression:
            # - JPG for photos (lossy, smaller)
            # - PNG for graphics (lossless)
            # - WebP for web (best compression, but less supported)

            # Recommendation: Keep images < 500KB before export
        """))
        st_space("v", 2)

        # --- 9. File size and performance ---
        st_write(bs.sub, "Export file size optimization", toc_lvl="+1")
        st_space("v", 1)

        st_write(s.large, """\
**What increases file size:**
- High-resolution images (use 72dpi or 96dpi)
- Many large images (prefer diagrams/SVG)
- Embedded fonts (if ever supported)
- Minified CSS (small benefit)

**Typical sizes:**
- Text-only document: 50-200 KB
- With images (optimized): 500 KB - 2 MB
- Complex layouts: 1-5 MB

**Best practices:**
- Compress images before including
- Use CSS instead of images for simple graphics
- Remove interactive elements from exported content
- Test export size regularly
        """)
        st_space("v", 2)

        # --- 10. Advanced: multi-format export ---
        st_write(bs.sub, "Exporting to multiple formats (future)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Currently, StreamTeX exports to HTML only.
            Future versions may support PDF, Markdown, or other formats.
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Current (HTML only)
            st_book([...], export_title="My Document")

            # Future possibility (not yet implemented)
            # st_book([...],
            #     export_title="My Document",
            #     export_formats=["html", "pdf", "markdown"])
        """))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Export is useful for sharing static documents.
            For interactive content, keep using Streamlit streaming.
            Export works best with text-heavy or diagram-heavy content.
        """))
