"""LazyBlockRegistry: Multi-source lazy-loading block management.

Demonstrates how LazyBlockRegistry enables enterprise-scale block loading
from multiple source directories with priority, caching, and attribute access.
"""

from custom.styles import Styles as s

from blocks.helpers import show_code, show_details, show_explanation
from streamtex import Style, st_block, st_space, st_write
from streamtex.enums import Tags as t


class BlockStyles:
    """Local styles for this block."""
    heading = s.project.titles.page_title + s.center_txt
    section = s.project.titles.section_title
    subsection = s.project.titles.section_subtitle
    info_box = Style(
        "background:rgba(74,144,217,0.08);padding:16px;border-radius:8px;",
        "lbr_info_box",
    )
    highlight_box = Style(
        "background:rgba(46,196,182,0.1);padding:16px;border-radius:8px;"
        "border-left:4px solid #2EC4B6;",
        "lbr_highlight_box",
    )
    comparison_box = Style(
        "background:rgba(243,156,18,0.08);padding:16px;border-radius:8px;"
        "border-left:4px solid #F39C12;",
        "lbr_comparison_box",
    )


bs = BlockStyles


def build():
    """Comprehensive documentation of LazyBlockRegistry."""

    # ========================================================================
    # TITLE
    # ========================================================================
    st_write(bs.heading, "LazyBlockRegistry", tag=t.h1, toc_lvl="1")
    st_space("v", 1)
    st_write(
        s.large,
        "Multi-source lazy-loading for enterprise-scale block management",
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 1: What is LazyBlockRegistry?
    # ========================================================================
    st_write(bs.section, "What is LazyBlockRegistry?", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
LazyBlockRegistry is a block loader that searches multiple directories
for block modules. Blocks are imported lazily (on first access) and cached
for subsequent calls. This enables sharing blocks across projects without
copying files.""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Key idea: "),
            """\
Instead of duplicating blocks across projects, place shared blocks
in a common directory and point LazyBlockRegistry at it.
Each project can combine its own local blocks with shared ones.""",
        )
    st_space("v", 1)

    st_write(
        s.medium,
        """\
The registry is defined in streamtex/blocks.py and exposed via
the top-level streamtex namespace as stx.LazyBlockRegistry.""",
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 2: Creating a Registry
    # ========================================================================
    st_write(bs.section, "Creating a Registry", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Create a LazyBlockRegistry by passing a list of directory paths.
Each path is a folder containing bck_*.py block files.
The registry resolves paths to absolute form automatically.""")
    st_space("v", 1)

    show_code("""\
import streamtex as stx
from pathlib import Path

# Point to a shared blocks directory
shared_path = str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "blocks")

# Create the registry
shared_blocks = stx.LazyBlockRegistry([shared_path])
""")
    st_space("v", 1)

    show_details("""\
Paths can be relative or absolute.
The constructor calls os.path.abspath() on each path internally.
You can pass multiple directories for multi-source resolution.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 3: Accessing Blocks
    # ========================================================================
    st_write(bs.section, "Accessing Blocks via Attribute Access", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Access blocks by name using dot notation (attribute access).
The registry searches source directories, imports the module,
and returns it. The returned module has a build() function
that st_book() calls to render the block.""")
    st_space("v", 1)

    show_code("""\
# Access a block — triggers lazy import on first access
module = shared_blocks.bck_header_training

# The module has a build() function
module.build()  # Renders the block content

# Use directly in st_book() — st_book calls build() for you
from streamtex import st_book
st_book([
    shared_blocks.bck_header_training,   # Lazy-loaded here
    blocks.bck_content_01,               # Local block
    shared_blocks.bck_footer_training,   # Lazy-loaded here
])
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "How __getattr__ works: "),
            """\
When you write shared_blocks.bck_name, Python calls the
registry's __getattr__ method. It searches each source directory
for a file named bck_name.py, imports it with importlib.util,
caches the module, and returns it.""",
        )
    st_space("v", 1)

    show_details("""\
If the block is not found in any source directory, an AttributeError is raised.
Special attributes (starting with '_') are excluded to prevent infinite recursion.
The error message includes the list of searched directories for easy debugging.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 4: Priority Order
    # ========================================================================
    st_write(bs.section, "Priority Order (First Source Wins)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
When the same block name exists in multiple source directories,
the first directory in the list wins. This is the priority rule:
sources are searched in order, and the first match is used.""")
    st_space("v", 1)

    show_code("""\
import streamtex as stx

# Priority: project_overrides > shared_blocks > fallback_blocks
registry = stx.LazyBlockRegistry([
    "blocks/overrides",     # Highest priority (checked first)
    "../../shared/blocks",  # Medium priority
    "../../fallback/blocks", # Lowest priority (checked last)
])

# If bck_header.py exists in both "overrides" and "shared",
# the version from "overrides" is used.
registry.bck_header  # -> loads from blocks/overrides/bck_header.py
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Use case: "),
            """\
A university has standard course headers/footers in a shared directory.
Each professor can override specific blocks in their project's local
override directory without modifying the shared originals.""",
        )
    st_space("v", 3)

    # ========================================================================
    # SECTION 5: Caching Behavior
    # ========================================================================
    st_write(bs.section, "Caching Behavior", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Once a block is loaded, it is stored in an internal cache dictionary.
Subsequent accesses return the cached module instantly without re-importing.
Blocks that were not found are also tracked to avoid repeated filesystem searches.""")
    st_space("v", 1)

    show_code("""\
# Internal cache structure:
# registry._cache = {}       # block_name -> module
# registry._not_found = set() # block names already searched (not found)

# First access: filesystem search + import + cache
module = registry.bck_welcome  # Slow (disk I/O + import)

# Second access: instant cache hit
module = registry.bck_welcome  # Fast (dict lookup)

# Not-found blocks are also cached to avoid repeated searches
try:
    registry.bck_nonexistent  # Searches all directories once
except AttributeError:
    pass

# Subsequent attempts skip the search entirely
try:
    registry.bck_nonexistent  # Instant AttributeError (cached miss)
except AttributeError:
    pass
""")
    st_space("v", 1)

    show_details("""\
The cache uses a simple dict: self._cache[block_name] = module.
Not-found blocks use a set: self._not_found for O(1) lookup.
There is no cache invalidation — blocks are loaded once per process lifetime.
This is by design: Streamlit reruns the script on each interaction,
but the registry persists across reruns via module-level state.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 6: Comparison with ProjectBlockRegistry
    # ========================================================================
    st_write(
        bs.section,
        "LazyBlockRegistry vs ProjectBlockRegistry",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation("""\
StreamTeX provides two registries for different use cases.
LazyBlockRegistry is for cross-project shared blocks.
ProjectBlockRegistry is for a single project's blocks/ directory.""")
    st_space("v", 1)

    st_write(bs.subsection, "ProjectBlockRegistry (Single-Project)")
    st_space("v", 1)

    with st_block(bs.comparison_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Purpose: "),
            "Manage blocks within a single project's blocks/ directory.",
        )
        st_space("v", 1)
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Features: "),
            """\
Manifest-based discovery, block type detection (atomic vs composite),
introspection (list_blocks, get_stats, load_all).""",
        )
        st_space("v", 1)
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Usage: "),
            "Typically used in blocks/__init__.py to auto-discover all bck_*.py files.",
        )

    st_space("v", 1)

    show_code("""\
# blocks/__init__.py — ProjectBlockRegistry for local blocks
from pathlib import Path
from streamtex import ProjectBlockRegistry

registry = ProjectBlockRegistry(Path(__file__).parent)

def __getattr__(name):
    return registry.get(name)

# Usage in book.py:
import blocks
blocks.bck_welcome       # Auto-discovered from blocks/bck_welcome.py
blocks.bck_content_01    # Auto-discovered from blocks/bck_content_01.py
""")
    st_space("v", 2)

    st_write(bs.subsection, "LazyBlockRegistry (Multi-Source)")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Purpose: "),
            """\
Load blocks from external directories (shared blocks,
other projects, override folders).""",
        )
        st_space("v", 1)
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Features: "),
            """\
Multi-source with priority, lazy-loading, caching,
attribute access.""",
        )
        st_space("v", 1)
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Usage: "),
            "Created in book.py to reference shared blocks alongside local ones.",
        )

    st_space("v", 2)

    st_write(bs.subsection, "When to Use Which?")
    st_space("v", 1)

    show_details("""\
Use ProjectBlockRegistry for your project's own blocks/ directory.
Use LazyBlockRegistry when you need blocks from outside your project.
They work together: local blocks via ProjectBlockRegistry,
shared blocks via LazyBlockRegistry, combined in st_book().""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 7: Real-World Example from book.py
    # ========================================================================
    st_write(bs.section, "Real-World Example: This Project's book.py", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
This very project (stx_manual_advanced) uses both registries.
Local blocks come from blocks/ via ProjectBlockRegistry.
Shared blocks come from stx_manuals_shared-blocks/ via LazyBlockRegistry.""")
    st_space("v", 1)

    show_code("""\
# book.py — stx_manual_advanced

import streamlit as st
import setup
import streamtex as stx
from streamtex import st_book, TOCConfig, MarkerConfig
from pathlib import Path

import blocks  # Local blocks (ProjectBlockRegistry in __init__.py)

# Configure shared blocks (LazyBlockRegistry)
_shared_blocks_path = str(
    Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "blocks"
)
shared_blocks = stx.LazyBlockRegistry([_shared_blocks_path])

# Configure static sources for multi-directory image resolution
stx.set_static_sources([
    str(Path(__file__).parent / "static"),       # Local static first
    str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "static"),
])

# Orchestrate: mix local and shared blocks
st_book([
    blocks.bck_level_badge,                  # Local block
    blocks.bck_lazy_block_registry_demo,     # Local block (this page!)
    blocks.bck_shared_blocks_usage,          # Local block
    # ... more local blocks ...
    shared_blocks.bck_footer_training,       # Shared block (lazy-loaded)
], paginate=True)
""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Key pattern: "),
            """\
Local blocks use 'blocks.bck_name' (via ProjectBlockRegistry).
Shared blocks use 'shared_blocks.bck_name' (via LazyBlockRegistry).
Both appear in the same st_book() call seamlessly.""",
        )
    st_space("v", 2)

    st_write(bs.subsection, "The stx_manuals_shared-blocks/ Directory Structure")
    st_space("v", 1)

    show_code("""\
documentation/manuals/
  stx_manuals_shared-blocks/
    blocks/
      bck_header_training.py    # Shared header for training courses
      bck_footer_training.py    # Shared footer for training courses
      bck_welcome.py            # Shared welcome page
      bck_style_basics.py       # Shared style introduction
      bck_best_practices.py     # Shared best practices
    static/
      images/                   # Shared images
  stx_manual_intro/              # Uses shared blocks via LazyBlockRegistry
  stx_manual_advanced/           # Uses shared blocks via LazyBlockRegistry
""", language="text")
    st_space("v", 1)

    show_details("""\
Multiple projects can share the same blocks without duplication.
Update a shared block once, and all projects that reference it get the change.
Each project can also override shared blocks by placing a same-named file
in a higher-priority source directory.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 8: Best Practices
    # ========================================================================
    st_write(bs.section, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Follow these guidelines when working with LazyBlockRegistry
to keep your multi-project architecture clean and maintainable.""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "1. Keep shared blocks self-contained"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
Shared blocks should not depend on project-specific custom/styles.py.
Use StxStyles directly or accept styles as parameters.""",
        )

    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "2. Use set_static_sources() for shared images"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
When shared blocks reference images, configure stx.set_static_sources()
in book.py so the image resolver can find assets across directories.""",
        )

    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "3. Place overrides in a dedicated directory"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
If you need to customize a shared block for one project,
create an overrides/ folder and list it first in the sources array.""",
        )

    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "4. Use repr() for debugging"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
Call repr(registry) or print(registry) to see the current state:
source paths and number of cached blocks.""",
        )

    st_space("v", 1)

    show_code("""\
import streamtex as stx

registry = stx.LazyBlockRegistry(["shared/blocks", "fallback/blocks"])
print(registry)
# -> LazyBlockRegistry(sources=['/abs/shared/blocks', '/abs/fallback/blocks'], cached=0)

_ = registry.bck_header
print(registry)
# -> LazyBlockRegistry(sources=[...], cached=1)
""")

    st_space("v", 3)
