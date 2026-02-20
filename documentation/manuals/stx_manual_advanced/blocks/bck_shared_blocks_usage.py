"""Shared Blocks Usage: Reusable blocks across multiple StreamTeX projects.

Demonstrates how to create, organize, and consume shared block libraries
using LazyBlockRegistry for cross-project block sharing.
"""

from streamtex import st_write, st_block, st_space, Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Local styles for this block."""
    heading = Style(
        "font-size:2.5rem;font-weight:bold;color:#4A90D9;text-align:center;",
        "sbu_heading",
    )
    section = Style(
        "font-size:1.8rem;font-weight:bold;color:#2EC4B6;",
        "sbu_section",
    )
    subsection = Style(
        "font-size:1.4rem;font-weight:bold;color:#4A90D9;",
        "sbu_subsection",
    )
    info_box = Style(
        "background:rgba(74,144,217,0.08);padding:16px;border-radius:8px;",
        "sbu_info_box",
    )
    highlight_box = Style(
        "background:rgba(46,196,182,0.1);padding:16px;border-radius:8px;"
        "border-left:4px solid #2EC4B6;",
        "sbu_highlight_box",
    )
    tip_box = Style(
        "background:rgba(243,156,18,0.08);padding:16px;border-radius:8px;"
        "border-left:4px solid #F39C12;",
        "sbu_tip_box",
    )
    warning_box = Style(
        "background:rgba(231,76,60,0.08);padding:16px;border-radius:8px;"
        "border-left:4px solid #E74C3C;",
        "sbu_warning_box",
    )


bs = BlockStyles


def build():
    """Comprehensive documentation of shared blocks usage patterns."""

    # ========================================================================
    # TITLE
    # ========================================================================
    st_write(bs.heading, "Shared Blocks Usage", tag=t.h1, toc_lvl="1")
    st_space("v", 1)
    st_write(
        s.large,
        "Reusable block libraries for multi-project StreamTeX architectures",
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 1: What Are Shared Blocks?
    # ========================================================================
    st_write(bs.section, "What Are Shared Blocks?", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(
        "Shared blocks are standard StreamTeX block modules (bck_*.py files with "
        "a build() function) that live outside any single project. They are designed "
        "to be reused across multiple projects without copying files. When you update "
        "a shared block, every project that references it picks up the change "
        "automatically."
    )
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Why share blocks? "),
            "Training courses, corporate templates, and multi-project sites often "
            "need identical headers, footers, style guides, or welcome pages. "
            "Instead of duplicating these across projects, place them in a shared "
            "directory and load them with LazyBlockRegistry.",
        )
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Key principle: "),
            "A shared block is structurally identical to a local block. "
            "It has a BlockStyles class, a build() function, and follows "
            "all the same coding standards. The only difference is where it lives "
            "on disk and how it is loaded.",
        )
    st_space("v", 3)

    # ========================================================================
    # SECTION 2: Directory Structure
    # ========================================================================
    st_write(bs.section, "Directory Structure for Shared Blocks", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(
        "A shared-blocks directory mirrors the standard project structure: "
        "blocks/ for block modules, custom/ for shared styles, and static/ "
        "for shared assets. This consistency means any block can move between "
        "a project and the shared library without changes."
    )
    st_space("v", 1)

    show_code("""\
# Shared block library directory structure
shared-blocks/
  blocks/
    __init__.py               # Module init (imports or discovery)
    bck_header_training.py    # Shared header block
    bck_footer_training.py    # Shared footer block
    bck_welcome.py            # Shared welcome page
    bck_style_basics.py       # Shared style introduction
    bck_best_practices.py     # Shared best practices guide
  custom/
    styles.py                 # SharedStyles class (inherits StreamTeX_Styles)
  static/
    images/                   # Shared image assets
      logo.png
      banner.png
""", language="text")
    st_space("v", 1)

    show_details(
        "The shared-blocks directory can live anywhere on disk.\n"
        "Common locations:\n"
        "  - A sibling directory next to your projects (documentation/manuals/sx_manuals_shared-blocks/)\n"
        "  - A separate Git repository cloned alongside your project\n"
        "  - A monorepo subfolder (libs/sx_manuals_shared-blocks/)\n"
        "LazyBlockRegistry resolves paths to absolute form, so relative paths work."
    )
    st_space("v", 1)

    st_write(bs.subsection, "How This Test Suite Is Organized")
    st_space("v", 1)

    show_code("""\
# In this repository, shared blocks sit at documentation/manuals/sx_manuals_shared-blocks/
documentation/manuals/
  sx_manuals_shared-blocks/   # Shared block library
    blocks/
      bck_header_training.py
      bck_footer_training.py
      bck_welcome.py
      bck_style_basics.py
      bck_best_practices.py
    custom/
      styles.py               # SharedStyles(StreamTeX_Styles)
    static/
      images/
  sx_manual_intro/            # Project A — uses shared blocks
    book.py
    blocks/
    custom/
    static/
  sx_manual_advanced/         # Project B — also uses shared blocks
    book.py
    blocks/
    custom/
    static/
""", language="text")
    st_space("v", 3)

    # ========================================================================
    # SECTION 3: Loading Shared Blocks
    # ========================================================================
    st_write(
        bs.section,
        "Loading Shared Blocks with LazyBlockRegistry",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation(
        "In your project's book.py, create a LazyBlockRegistry that points to "
        "the shared-blocks/blocks/ directory. The registry uses lazy-loading: "
        "blocks are imported only when first accessed, then cached for all "
        "subsequent uses."
    )
    st_space("v", 1)

    show_code("""\
# book.py — Loading shared blocks
import streamtex as sx
from pathlib import Path

# Resolve the path to the shared blocks directory
_shared_blocks_path = str(
    Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "blocks"
)

# Create a LazyBlockRegistry for shared blocks
shared_blocks = sx.LazyBlockRegistry([_shared_blocks_path])

# Now access any shared block by name (dot notation)
# The first access triggers a lazy import; subsequent accesses are cached
shared_blocks.bck_header_training   # -> loads sx_manuals_shared-blocks/blocks/bck_header_training.py
shared_blocks.bck_footer_training   # -> loads sx_manuals_shared-blocks/blocks/bck_footer_training.py
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "How it works internally: "),
            "When you write shared_blocks.bck_name, Python calls __getattr__ on "
            "the registry. It searches the source directories for bck_name.py, "
            "imports it with importlib.util.spec_from_file_location, caches the "
            "module, and returns it. If not found, an AttributeError is raised.",
        )
    st_space("v", 1)

    show_details(
        "LazyBlockRegistry accepts a list of directories, not just one.\n"
        "When multiple directories are provided, they are searched in order.\n"
        "The first directory containing a matching bck_*.py file wins (priority order).\n"
        "See the LazyBlockRegistry block for the full priority and caching documentation."
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 4: Using Shared + Local Blocks Together
    # ========================================================================
    st_write(
        bs.section,
        "Using Shared Blocks Alongside Local Blocks",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation(
        "The real power of shared blocks appears when you combine them with "
        "local blocks in a single st_book() call. Local blocks come from your "
        "project's blocks/ directory (via ProjectBlockRegistry), while shared "
        "blocks come from LazyBlockRegistry. Both are regular Python modules "
        "with a build() function, so st_book() treats them identically."
    )
    st_space("v", 1)

    show_code("""\
# book.py — Combining local and shared blocks in st_book()
import streamlit as st
import setup
import streamtex as sx
from streamtex import st_book, TOCConfig, MarkerConfig
from pathlib import Path

import blocks  # Local blocks (ProjectBlockRegistry in __init__.py)

# Shared blocks via LazyBlockRegistry
_shared_path = str(Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "blocks")
shared_blocks = sx.LazyBlockRegistry([_shared_path])

# Orchestrate: mix local and shared blocks freely
st_book([
    shared_blocks.bck_header_training,    # Shared header (from sx_manuals_shared-blocks/)
    blocks.bck_welcome_intro,             # Local block (from blocks/)
    blocks.bck_text_and_styling,          # Local block
    blocks.bck_grids_and_lists,           # Local block
    shared_blocks.bck_best_practices,     # Shared block
    shared_blocks.bck_footer_training,    # Shared footer (from sx_manuals_shared-blocks/)
], paginate=True)
""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Pattern: "),
            "Use 'blocks.bck_name' for local blocks and "
            "'shared_blocks.bck_name' for shared blocks. "
            "The prefix makes it immediately clear where each block comes from, "
            "improving code readability and maintainability.",
        )
    st_space("v", 1)

    st_write(bs.subsection, "This Project's Actual book.py")
    st_space("v", 1)

    show_explanation(
        "This very project (sx_manual_advanced) uses this exact pattern. "
        "All content blocks are local, but the footer comes from sx_manuals_shared-blocks/. "
        "The relevant extract from book.py:"
    )
    st_space("v", 1)

    show_code("""\
# From documentation/manuals/sx_manual_advanced/book.py (actual code)

import blocks  # Local blocks via ProjectBlockRegistry

# Configure shared blocks
_shared_blocks_path = str(
    Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "blocks"
)
shared_blocks = sx.LazyBlockRegistry([_shared_blocks_path])

st_book([
    blocks.bck_level_badge,                  # Local
    blocks.bck_lazy_block_registry_demo,     # Local
    blocks.bck_shared_blocks_usage,          # Local (this page!)
    blocks.bck_static_resolution_demo,       # Local
    # ... more local blocks ...
    shared_blocks.bck_footer_training,       # Shared (lazy-loaded)
], paginate=True)
""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 5: Shared Styles Pattern
    # ========================================================================
    st_write(
        bs.section,
        "The Shared custom/styles.py Pattern",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation(
        "Shared blocks often need their own style palette that works independently "
        "of any project's custom styles. The shared-blocks/custom/styles.py file "
        "defines a SharedStyles class that inherits from StreamTeX_Styles. This "
        "ensures shared blocks remain self-contained and do not depend on any "
        "specific project's style definitions."
    )
    st_space("v", 1)

    show_code("""\
# shared-blocks/custom/styles.py
from streamtex.styles import StreamTeX_Styles, Style


class SharedStyles(StreamTeX_Styles):
    \"\"\"Shared style palette for training courses.\"\"\"

    class colors:
        \"\"\"Shared color palette\"\"\"
        primary_blue = Style.create(
            StreamTeX_Styles.text.colors.reset, "shared_primary_blue",
            color="#667eea"
        )
        accent_teal = Style.create(
            StreamTeX_Styles.text.colors.reset, "shared_accent_teal",
            color="#20B2AA"
        )
        warning_orange = Style.create(
            StreamTeX_Styles.text.colors.reset, "shared_warning_orange",
            color="#FF8C00"
        )

    class titles:
        \"\"\"Shared title styles\"\"\"
        course_title = StreamTeX_Styles.text.Titles.GIANT + colors.primary_blue
        section_title = StreamTeX_Styles.text.Titles.Large + colors.primary_blue
        subsection_title = StreamTeX_Styles.text.Titles.large + colors.accent_teal
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Key design choice: "),
            "SharedStyles inherits from StreamTeX_Styles, not from any project's "
            "Styles class. This makes shared blocks portable: they work in any "
            "project regardless of that project's custom style definitions.",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Tip: "),
            "Shared blocks should use StreamTeX_Styles (sx.StreamTeX_Styles) or "
            "their own SharedStyles for styling. They should never import from "
            "'custom.styles import Styles as s' because that path resolves to the "
            "consuming project's styles, not the shared library's styles. This "
            "coupling would break portability.",
        )
    st_space("v", 1)

    st_write(bs.subsection, "How Shared Blocks Use SharedStyles")
    st_space("v", 1)

    show_code("""\
# shared-blocks/blocks/bck_header_training.py
import streamtex as sx
from streamtex import st_write, st_block, st_space
from streamtex.styles import Style
from streamtex.enums import Tags as t


class BlockStyles:
    \"\"\"Shared header styles.\"\"\"
    header_bg = Style(
        "background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
        "padding:40px 20px;border-radius:8px;",
        "training_header"
    )


def build():
    \"\"\"Render a standard training course header.\"\"\"
    st_space("v", 1)
    with st_block(BlockStyles.header_bg):
        st_write(
            sx.StreamTeX_Styles.huge + sx.StreamTeX_Styles.text.colors.white,
            "StreamTeX Training Course",
            tag=t.div
        )
        st_write(
            sx.StreamTeX_Styles.large + sx.StreamTeX_Styles.text.colors.white,
            "A Streamlit-based content rendering framework",
            tag=t.div
        )
    st_space("v", 1)
""")
    st_space("v", 1)

    show_details(
        "Notice that the shared block uses sx.StreamTeX_Styles for text styles\n"
        "and defines its own BlockStyles for local layout. It does not import from\n"
        "custom.styles, making it fully portable across projects."
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 6: Static Assets in Shared Blocks
    # ========================================================================
    st_write(
        bs.section,
        "Static Assets in Shared Blocks",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation(
        "When shared blocks reference images or other static assets, those assets "
        "live in shared-blocks/static/. For the image resolver to find them, you "
        "must configure sx.set_static_sources() in your project's book.py to include "
        "both the local static/ directory and the shared static/ directory."
    )
    st_space("v", 1)

    show_code("""\
# book.py — Configure static sources for multi-directory resolution
import streamtex as sx
from pathlib import Path

# Local static directory (highest priority)
_local_static = str(Path(__file__).parent / "static")

# Shared static directory (fallback)
_shared_static = str(
    Path(__file__).parent.parent / "sx_manuals_shared-blocks" / "static"
)

# Register both sources: local first, shared second
sx.set_static_sources([
    _local_static,      # Checked first (project-specific assets)
    _shared_static,     # Checked second (shared assets)
])
""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Resolution order: "),
            "When a block calls st_image(uri='images/logo.png'), the image resolver "
            "searches the static sources in order. If logo.png exists in the project's "
            "local static/images/, that version is used. Otherwise, the shared "
            "static/images/logo.png is used. This lets projects override shared "
            "assets when needed.",
        )
    st_space("v", 1)

    show_code("""\
# Shared block referencing a shared image
from streamtex import st_image

def build():
    # This image will be resolved from shared-blocks/static/images/
    # unless the consuming project has its own static/images/logo.png
    st_image(uri="images/logo.png")
""")
    st_space("v", 1)

    show_details(
        "set_static_sources() must be called before any block's build() runs.\n"
        "Place it at the top of book.py, after setup but before st_book().\n"
        "The order of paths matters: first path has highest priority.\n"
        "See the Static Resolution Demo block for detailed resolution mechanics."
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 7: Creating Your Own Shared Block Library
    # ========================================================================
    st_write(
        bs.section,
        "Creating Your Own Shared Block Library",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation(
        "Follow these steps to create a reusable shared block library from scratch."
    )
    st_space("v", 1)

    st_write(bs.subsection, "Step 1: Create the Directory Structure")
    st_space("v", 1)

    show_code("""\
# Create the shared library directory
mkdir -p my-shared-blocks/blocks
mkdir -p my-shared-blocks/custom
mkdir -p my-shared-blocks/static/images

# Create the __init__.py for the blocks package
touch my-shared-blocks/blocks/__init__.py
""", language="bash")
    st_space("v", 1)

    st_write(bs.subsection, "Step 2: Write the Shared Styles")
    st_space("v", 1)

    show_code("""\
# my-shared-blocks/custom/styles.py
from streamtex.styles import StreamTeX_Styles, Style


class SharedStyles(StreamTeX_Styles):
    \"\"\"Organization-wide style palette.\"\"\"

    class colors:
        brand_primary = Style.create(
            StreamTeX_Styles.text.colors.reset, "brand_primary",
            color="#1A73E8"
        )
        brand_accent = Style.create(
            StreamTeX_Styles.text.colors.reset, "brand_accent",
            color="#34A853"
        )

    class titles:
        page_title = StreamTeX_Styles.text.Titles.huge + colors.brand_primary
""")
    st_space("v", 1)

    st_write(bs.subsection, "Step 3: Write a Shared Block")
    st_space("v", 1)

    show_code("""\
# my-shared-blocks/blocks/bck_org_header.py
\"\"\"Organization-wide header block.\"\"\"

import streamtex as sx
from streamtex import st_write, st_block, st_space
from streamtex.styles import Style
from streamtex.enums import Tags as t


class BlockStyles:
    \"\"\"Organization header styles.\"\"\"
    banner = Style(
        "background:linear-gradient(135deg, #1A73E8 0%, #34A853 100%);"
        "padding:32px 24px;border-radius:12px;",
        "org_banner"
    )

bs = BlockStyles


def build():
    \"\"\"Render the organization header.\"\"\"
    with st_block(bs.banner):
        st_write(
            sx.StreamTeX_Styles.huge + sx.StreamTeX_Styles.text.colors.white,
            "My Organization",
            tag=t.div
        )
        st_write(
            sx.StreamTeX_Styles.large + sx.StreamTeX_Styles.text.colors.white,
            "Powered by StreamTeX",
            tag=t.div
        )
    st_space("v", 2)
""")
    st_space("v", 1)

    st_write(bs.subsection, "Step 4: Consume from a Project")
    st_space("v", 1)

    show_code("""\
# my-project/book.py
import streamlit as st
import setup
import streamtex as sx
from streamtex import st_book
from pathlib import Path

import blocks  # Local blocks

# Load shared blocks
_shared_path = str(
    Path(__file__).parent.parent / "my-shared-blocks" / "blocks"
)
shared = sx.LazyBlockRegistry([_shared_path])

# Configure shared static assets
sx.set_static_sources([
    str(Path(__file__).parent / "static"),
    str(Path(__file__).parent.parent / "my-shared-blocks" / "static"),
])

# Build the book with both local and shared blocks
st_book([
    shared.bck_org_header,           # Shared header
    blocks.bck_intro,                # Local content
    blocks.bck_chapter_1,            # Local content
    blocks.bck_chapter_2,            # Local content
    shared.bck_org_footer,           # Shared footer
], paginate=True)
""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 8: Best Practices
    # ========================================================================
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    show_explanation(
        "Follow these guidelines to keep your shared block architecture "
        "clean, portable, and maintainable across all consuming projects."
    )
    st_space("v", 1)

    # Practice 1: Self-contained blocks
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "1. Keep shared blocks self-contained"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "A shared block should never import from a project-specific "
            "custom/styles.py. Use sx.StreamTeX_Styles or define styles locally "
            "in the block's BlockStyles class. This ensures the block works "
            "in any project without modification.",
        )
    st_space("v", 1)

    show_code("""\
# GOOD: Self-contained shared block
import streamtex as sx
from streamtex.styles import Style

class BlockStyles:
    title = sx.StreamTeX_Styles.Large + sx.StreamTeX_Styles.bold
    container = Style("padding:16px;border-radius:8px;", "shared_container")

# BAD: Coupled to a specific project
from custom.styles import Styles as s  # Which project's styles?
class BlockStyles:
    title = s.project.titles.section_title  # Breaks in other projects!
""")
    st_space("v", 1)

    # Practice 2: No external dependencies
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "2. Avoid external dependencies"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "Shared blocks should depend only on streamtex and streamlit. "
            "If a block needs additional packages, document it clearly or "
            "consider whether the block truly belongs in the shared library.",
        )
    st_space("v", 1)

    # Practice 3: Static assets with set_static_sources
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "3. Use set_static_sources() for images"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "Every project that consumes shared blocks with images must call "
            "sx.set_static_sources() in its book.py. Include the shared static "
            "directory after the local one so project assets take priority.",
        )
    st_space("v", 1)

    # Practice 4: Override via priority
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "4. Override shared blocks with priority sources"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "To customize a shared block for one project, create an overrides/ "
            "directory with the same filename and place it first in the "
            "LazyBlockRegistry sources list. The first source wins.",
        )
    st_space("v", 1)

    show_code("""\
# Override pattern: project-specific version takes priority
shared = sx.LazyBlockRegistry([
    "blocks/overrides",          # Project overrides (checked first)
    "../../sx_manuals_shared-blocks/blocks", # Shared originals (checked second)
])

# If blocks/overrides/bck_header.py exists, it is used
# Otherwise, sx_manuals_shared-blocks/blocks/bck_header.py is used
shared.bck_header  # -> resolves to highest-priority source
""")
    st_space("v", 1)

    # Practice 5: Consistent naming
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "5. Use consistent naming conventions"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "Prefix shared block filenames to indicate their purpose: "
            "bck_header_*, bck_footer_*, bck_shared_*. This makes it clear "
            "at a glance which blocks are designed to be shared versus "
            "project-specific.",
        )
    st_space("v", 1)

    # Practice 6: Style IDs must be unique
    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "6. Use unique style IDs across projects"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "Style IDs are global (they generate CSS class names). Prefix shared "
            "style IDs with 'shared_' or your organization name to avoid collisions "
            "with project-specific styles.",
        )
    st_space("v", 1)

    show_code("""\
# Shared styles with prefixed IDs to avoid collisions
Style("color:#667eea;", "shared_primary_blue")    # Prefixed with 'shared_'
Style("padding:24px;", "acme_card_container")      # Prefixed with org name

# Avoid generic IDs that may clash with project styles
Style("color:#667eea;", "primary_blue")            # Risk of collision!
""")
    st_space("v", 1)

    # Practice 7: Documentation
    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "7. Document your shared library"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            "Include a README in the shared-blocks/ root that lists all available "
            "blocks, their purpose, and any configuration they expect. This helps "
            "new projects discover and adopt shared blocks quickly.",
        )
    st_space("v", 3)

    # ========================================================================
    # SUMMARY
    # ========================================================================
    with st_block(bs.highlight_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Summary: "),
            "Shared blocks let you build once and reuse everywhere. "
            "Use LazyBlockRegistry to load them, set_static_sources() for images, "
            "keep blocks self-contained with no project-specific imports, "
            "and leverage priority ordering for project-specific overrides.",
        )
    st_space("v", 3)
