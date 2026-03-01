"""Static Resolution Demo — Multi-directory static asset resolution in StreamTeX."""

from custom.styles import Styles as s

from blocks.helpers import show_code, show_details, show_explanation
from streamtex import Style, st_block, st_space, st_write
from streamtex.enums import Tags as t


class BlockStyles:
    """Local styles for the static resolution demo block."""
    heading = s.project.titles.page_title + s.center_txt
    section = s.project.titles.section_title
    subsection = s.project.titles.section_subtitle
    info_box = Style(
        "background:rgba(74,144,217,0.08);padding:16px;border-radius:8px;",
        "sr_info_box",
    )
    highlight_box = Style(
        "background:rgba(46,196,182,0.1);padding:16px;border-radius:8px;"
        "border-left:4px solid #2EC4B6;",
        "sr_highlight_box",
    )
    warning_box = Style(
        "background:rgba(243,156,18,0.08);padding:16px;border-radius:8px;"
        "border-left:4px solid #F39C12;",
        "sr_warning_box",
    )
    tip_box = Style(
        "background:rgba(46,204,113,0.08);padding:16px;border-radius:8px;"
        "border-left:4px solid #2ECC71;",
        "sr_tip_box",
    )


bs = BlockStyles


def build():
    """Comprehensive documentation of static asset resolution in StreamTeX."""

    # ========================================================================
    # TITLE
    # ========================================================================
    st_write(bs.heading, "Static Asset Resolution", tag=t.h1, toc_lvl="1")
    st_space("v", 1)
    st_write(
        s.large,
        "How StreamTeX resolves images and static files across multiple directories",
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 1: What is Static Resolution?
    # ========================================================================
    st_write(bs.section, "What is Static Resolution?", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Static resolution is the mechanism StreamTeX uses to locate image files
and other static assets (JSON data, fonts, etc.) across multiple directories.

Instead of hardcoding absolute paths, you provide a simple filename or relative
path, and StreamTeX searches configured directories in priority order to find it.""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.large,
            (s.text.weights.bold_weight, "Key idea: "),
            """\
When multiple projects share static assets (images, data files),
static resolution lets each project reference them by name without
knowing their exact filesystem location.""",
        )
    st_space("v", 1)

    st_write(
        s.medium,
        """\
The resolution system is defined in streamtex/blocks.py and exposed
as stx.set_static_sources(), stx.get_static_sources(), and stx.resolve_static().
The st_image() function uses it internally for automatic image discovery.""",
    )
    st_space("v", 3)

    # ========================================================================
    # SECTION 2: Configuring Static Sources
    # ========================================================================
    st_write(bs.section, "Configuring Static Sources with set_static_sources()", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Before using static resolution, you must configure the list of directories
to search. This is done once in your project's book.py entry point, before
any blocks are loaded.

The function accepts a list of directory paths
(relative or absolute) and converts them all to absolute paths internally.""")
    st_space("v", 1)

    show_code("""\
import streamtex as stx
from pathlib import Path

# Configure static sources in book.py (called once at startup)
stx.set_static_sources([
    str(Path(__file__).parent / "static"),                              # Local project static
    str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "static"),  # Shared static
])
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Order matters: "),
            """\
The first directory in the list has the highest priority.
If a file exists in multiple directories, the first match wins.
Always place your local project's static/ directory first.""",
        )
    st_space("v", 1)

    show_details("""\
Internally, set_static_sources() calls os.path.abspath() on each path.

This means you can pass relative paths and they will be resolved correctly.

The sources are stored in a module-level global list in streamtex/blocks.py.

You can retrieve the current configuration with stx.get_static_sources().""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 3: resolve_static() — How It Works
    # ========================================================================
    st_write(bs.section, "resolve_static() — How It Searches Directories", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
The resolve_static() function takes a relative path (e.g., 'data/trainers.json')
and searches each configured static source directory in order.

It returns the
absolute path of the first match found. If no match is found in any directory,
it returns the original relative path as a fallback.""")
    st_space("v", 1)

    show_code("""\
import streamtex as stx

# Resolve a data file across static sources
data_path = stx.resolve_static("data/trainers.json")

# The function searches:
#   1. /abs/path/to/project/static/data/trainers.json  -> found? return it
#   2. /abs/path/to/stx_manuals_shared-blocks/static/data/trainers.json  -> found? return it
#   3. Not found anywhere -> returns "data/trainers.json" (original path)

# Use the resolved path
import json
with open(data_path) as f:
    trainers = json.load(f)
""")
    st_space("v", 1)

    st_write(bs.subsection, "The Search Algorithm")
    st_space("v", 1)

    show_code("""\
# Simplified internal logic of resolve_static():
def resolve_static(relative_path: str) -> str:
    for base in _static_sources:
        full_path = os.path.join(base, relative_path)
        if os.path.exists(full_path):
            return full_path        # First match wins
    return relative_path            # Fallback: original path
""")
    st_space("v", 1)

    show_details("""\
resolve_static() uses os.path.exists() which works for both files and directories.

The function is deterministic: given the same sources and filename, it always returns the same result.

It does NOT raise an error when a file is not found — it falls back silently.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 4: Priority Order (First Path Wins)
    # ========================================================================
    st_write(bs.section, "Priority Order (First Path Wins)", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
When the same filename exists in multiple static source directories,
the first directory in the list wins.

This is the priority rule and
it enables a powerful override pattern: projects can replace shared assets
with their own local versions without modifying the shared directory.""")
    st_space("v", 1)

    show_code("""\
import streamtex as stx

# Priority: local > shared > fallback
stx.set_static_sources([
    "static",                  # Highest priority (project-local)
    "../../shared/static",     # Medium priority (team-shared)
    "../../defaults/static",   # Lowest priority (organization defaults)
])

# If logo.png exists in ALL three directories:
# resolve_static("images/logo.png")
# -> returns "/abs/path/to/static/images/logo.png"  (local wins)

# If logo.png only exists in shared and defaults:
# resolve_static("images/logo.png")
# -> returns "/abs/path/to/shared/static/images/logo.png"  (shared wins)
""")
    st_space("v", 1)

    with st_block(bs.highlight_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Override pattern: "),
            """\
A university provides default logos and banners in a shared directory.
Each department can override specific images by placing a same-named file
in their local static/ directory. No configuration changes needed —
the priority order handles it automatically.""",
        )
    st_space("v", 3)

    # ========================================================================
    # SECTION 5: How st_image() Uses Static Resolution Internally
    # ========================================================================
    st_write(
        bs.section,
        "How st_image() Uses Static Resolution Internally",
        toc_lvl="+1",
    )
    st_space("v", 1)

    show_explanation("""\
When you call st_image(uri='logo.png'), the image function detects that
the URI is not a URL, not an absolute path, and not a relative path
(no leading '.', '..', or '/').

It then uses the static resolution system
to search configured directories for the file.""")
    st_space("v", 1)

    st_write(bs.subsection, "The URI Resolution Flow")
    st_space("v", 1)

    show_code("""\
# What happens inside st_image(uri="logo.png"):

# Step 1: Is it a URL? (http://, https://, www.)
#   -> No, continue

# Step 2: Is it an absolute path? (os.path.isabs)
#   -> No, continue

# Step 3: Is it a relative path? (starts with '.', '..', '/')
#   -> No, continue

# Step 4: Static resolution — search configured sources
for base in get_static_sources():
    for subdir in ["images", ""]:
        full_path = os.path.join(base, subdir, uri)
        if os.path.isfile(full_path):
            # Found! Convert to base64 and return
            return encode_to_base64(full_path)

# Step 5: Fallback — use Streamlit's built-in static serving
return f"app/static/images/{uri}"
""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Automatic subdirectory search: "),
            """\
For each static source, st_image() checks both the 'images/'
subdirectory and the root of the static directory. This means
st_image(uri='logo.png') will find the file whether it lives at
static/images/logo.png or static/logo.png.""",
        )
    st_space("v", 1)

    show_code("""\
# All of these work with static resolution:
st_image(uri="logo.png")              # Searches static/images/logo.png, then static/logo.png
st_image(uri="icons/arrow.png")       # Searches static/images/icons/arrow.png, then static/icons/arrow.png

# These bypass static resolution (direct path handling):
st_image(uri="https://example.com/logo.png")   # URL — used directly
st_image(uri="/abs/path/to/logo.png")          # Absolute path — base64 encoded
st_image(uri="./local/logo.png")               # Relative path — resolved from cwd
""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 6: Multi-Directory Patterns
    # ========================================================================
    st_write(bs.section, "Multi-Directory Patterns", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
Static resolution becomes powerful when projects share assets across
multiple directories.

Here are the most common patterns used in
StreamTeX multi-project architectures.""")
    st_space("v", 2)

    st_write(bs.subsection, "Pattern 1: Local + Shared Static")
    st_space("v", 1)

    show_code("""\
# The most common pattern: project-local + shared static directories
# Used in stx_manual_advanced/book.py

stx.set_static_sources([
    str(Path(__file__).parent / "static"),                                  # Project images
    str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "static"), # Shared images
])

# Directory structure:
# documentation/manuals/
#   stx_manual_advanced/
#     static/
#       images/
#         advanced_banner.png    <- Local only
#     book.py
#   stx_manuals_shared-blocks/
#     static/
#       images/
#         training_logo.png      <- Shared across projects
#   stx_manual_intro/
#     static/
#       images/
#         intro_banner.png       <- Local only
#     book.py
""", language="text")
    st_space("v", 2)

    st_write(bs.subsection, "Pattern 2: Override + Base + Defaults")
    st_space("v", 1)

    show_code("""\
# Three-tier pattern: local overrides > team base > org defaults
stx.set_static_sources([
    str(Path(__file__).parent / "static"),           # 1. Project overrides
    str(Path(__file__).parent / "../../team/static"), # 2. Team-level assets
    str(Path(__file__).parent / "../../org/static"),  # 3. Organization defaults
])

# If both team and org have "header.png":
# -> team version is used (higher priority)
# If only org has "footer.png":
# -> org version is used (only match)
""")
    st_space("v", 2)

    st_write(bs.subsection, "Pattern 3: Blocks Alongside Static")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Combining LazyBlockRegistry + set_static_sources: "),
            """\
When shared blocks reference images, both the block source and the
static source must be configured. LazyBlockRegistry handles block
discovery, while set_static_sources handles image discovery.""",
        )
    st_space("v", 1)

    show_code("""\
import streamtex as stx
from pathlib import Path

# Block sources (for LazyBlockRegistry)
shared_blocks_path = str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "blocks")
shared_blocks = stx.LazyBlockRegistry([shared_blocks_path])

# Static sources (for image/asset resolution)
stx.set_static_sources([
    str(Path(__file__).parent / "static"),
    str(Path(__file__).parent.parent / "stx_manuals_shared-blocks" / "static"),
])

# Now shared blocks can reference images by name,
# and the static resolver will find them in shared-blocks/static/
""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 7: Fallback Behavior
    # ========================================================================
    st_write(bs.section, "Fallback Behavior When File Is Not Found", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
When a file is not found in any configured static source directory,
both resolve_static() and st_image() have fallback behaviors.

Understanding
these fallbacks helps debug missing asset issues.""")
    st_space("v", 1)

    st_write(bs.subsection, "resolve_static() Fallback")
    st_space("v", 1)

    with st_block(bs.warning_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "No error raised: "),
            """\
resolve_static() does NOT raise an exception when a file is not found.
It silently returns the original relative path. This means errors may
surface later when you try to open or read the file.""",
        )
    st_space("v", 1)

    show_code("""\
import streamtex as stx

# File does not exist in any static source
result = stx.resolve_static("nonexistent.json")
# result = "nonexistent.json"  (original path returned as-is)

# The error surfaces when you try to use the path:
with open(result) as f:       # FileNotFoundError here!
    data = json.load(f)
""")
    st_space("v", 2)

    st_write(bs.subsection, "st_image() Fallback")
    st_space("v", 1)

    with st_block(bs.warning_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Legacy static serving: "),
            """\
When st_image() cannot find a file via static resolution,
it falls back to Streamlit's built-in static serving path:
'app/static/images/{filename}'. This requires
enableStaticServing = true in .streamlit/config.toml.""",
        )
    st_space("v", 1)

    show_code("""\
# If "missing.png" is not found via static resolution:
st_image(uri="missing.png")
# -> Falls back to src="app/static/images/missing.png"
# -> This uses Streamlit's built-in static file serving
# -> Requires .streamlit/config.toml:
#    [server]
#    enableStaticServing = true
""")
    st_space("v", 1)

    show_details("""\
To debug missing images, check:

1. Is set_static_sources() called in book.py before blocks are loaded?
2. Does the file exist in one of the configured directories?
3. Is the filename spelled correctly (case-sensitive on Linux)?
4. Use stx.get_static_sources() to print the current source list.""")
    st_space("v", 3)

    # ========================================================================
    # SECTION 8: Best Practices
    # ========================================================================
    st_write(bs.section, "Best Practices for Organizing Static Assets", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""\
A well-organized static asset structure makes multi-project
architectures easier to maintain.

Follow these guidelines
for clean and predictable asset resolution.""")
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "1. Always call set_static_sources() in book.py"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
Configure sources at the entry point, before any blocks are loaded.
This ensures all blocks see the same resolution configuration.""",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "2. Place local static/ first in the sources list"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
The first source has the highest priority. Local assets should override
shared ones, so list your project's static/ directory first.""",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "3. Use images/ subdirectory for image assets"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
st_image() automatically searches the images/ subdirectory within each
static source. Organize images under static/images/ for automatic discovery.""",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "4. Name files with block prefixes to avoid collisions"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
Follow the naming convention: [block_filename]_image_[index].[ext].
For example, bck_welcome_image_01.png avoids name clashes across blocks.""",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "5. Use resolve_static() for non-image assets"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
For data files (JSON, CSV, text), use stx.resolve_static() explicitly.
st_image() only handles image URIs — other asset types need manual resolution.""",
        )
    st_space("v", 1)

    with st_block(bs.tip_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "6. Debug with get_static_sources()"),
        )
        st_space("v", 1)
        st_write(
            s.medium,
            """\
When assets are not found, print stx.get_static_sources() to verify
the configured paths. Check that directories exist and contain the expected files.""",
        )
    st_space("v", 1)

    show_code("""\
import streamtex as stx

# Debugging: print the current static source configuration
print("Static sources:", stx.get_static_sources())
# -> ['abs/path/to/static', '/abs/path/to/stx_manuals_shared-blocks/static']

# Debugging: check if a specific file resolves correctly
resolved = stx.resolve_static("images/logo.png")
print(f"Resolved: {resolved}")
# -> If found: '/abs/path/to/static/images/logo.png'
# -> If not found: 'images/logo.png' (original path)

import os
print(f"Exists: {os.path.exists(resolved)}")
""")
    st_space("v", 1)

    with st_block(bs.info_box):
        st_write(
            s.medium,
            (s.text.weights.bold_weight, "Summary: "),
            """\
Static resolution is a simple but powerful mechanism.
Configure once in book.py, use simple filenames in blocks,
and let StreamTeX handle the path resolution.
Combined with LazyBlockRegistry, it enables seamless asset sharing
across projects without duplicating files.""",
        )

    st_space("v", 3)
