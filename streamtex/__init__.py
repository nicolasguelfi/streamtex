"""StreamTeX — A Streamlit wrapper for styled content rendering."""

# ── Python version gate (must run before any other import) ──────────────
# StreamTeX requires Python ≥ 3.11.  If the interpreter is too old, print a
# clear diagnostic and exit immediately — before the stderr redirect below
# swallows import errors.
import sys as _sys

if _sys.version_info < (3, 11):
    print(
        f"Error: StreamTeX requires Python >= 3.11 (found {_sys.version}).\n"
        "Fix:  uv python install 3.13 && "
        'uv tool install "streamtex[cli]" -U --python 3.13',
        file=_sys.stderr,
    )
    _sys.exit(1)

# Suppress Streamlit "No runtime found" warnings when imported outside a
# Streamlit app (e.g. from the stx CLI).  Streamlit creates per-module loggers
# with their own StreamHandler(stderr) at import time, so we must redirect
# stderr during the initial import cascade.
import io as _io

_real_stderr = _sys.stderr
_sys.stderr = _io.StringIO()

__version__ = "0.5.11"

# Core style system
from .styles import Style, ListStyle, StyleGrid, StxStyles, StreamTeX_Styles, theme

# Content rendering
from .write import st_write
from .image import st_image, configure_image_path
from .code import st_code, add_wrap_all_option
from .markdown import st_markdown
from .container import st_block, st_span
from .space import st_space, st_br
from .grid import st_grid, responsive_cols
from .list import st_list
from .overlay import st_overlay

# Banner configuration
from .banner import BannerConfig, BannerMode

# Book orchestration
from .book import st_book, st_include, st_toc, load_css

# Table of Contents
from .toc import reset_toc_registry, toc_entries, TOCConfig, NumberingMode

# Marker Navigation
from .marker import st_marker, MarkerConfig

# Section spacing
from .spacing import (
    Spacing, SpacingConfig,
    set_spacing, get_spacing,
    set_block_spacing, get_block_spacing,
)

# Slide break (presentation mode)
from .slide import (
    st_slide_break, SlideBreakConfig, SlideBreakMode,
    set_slide_break_config, get_slide_break_config,
    add_slide_break_options,
)

# Presentation profiles (display configurations)
from .presentation_profile import (
    PresentationProfile,
    PageLayout,
    ViewMode,
    SlideBreakDisplayConfig,
    ProfileConfig,
)

# Presentation mode (fullscreen 16/9)
from .presentation import (
    PresentationConfig,
    set_presentation_config, get_presentation_config,
    st_presentation_footer, add_presentation_options,
)

# Enums
from .enums import Tags

# Zoom
from .zoom import add_zoom_options, inject_zoom_logic

# Export
from .export import AssetMode, ExportConfig, ExportMode, st_export, st_html

# PDF Export (requires optional 'pdf' extra)
from .pdf_export import PdfConfig, PdfMode, export_pdf

# Export-aware widget wrappers
from .export_widgets import (
    st_dataframe, st_table, st_metric, st_json, st_graphviz,
    st_line_chart, st_bar_chart, st_area_chart, st_scatter_chart,
    st_audio, st_video,
)

# Diagram rendering
from .mermaid import st_mermaid
from .plantuml import st_plantuml
from .tikz import st_tikz

# LaTeX rendering
from .latex import st_latex, st_latex_doc
from .latex_utils import extract_tikz, extract_math, extract_frames

# Utilities
from .utils import exec_static, inject_link_preview_scaffold, resolve_content

# Multi-source block registry and static resolution
from .blocks import (
    LazyBlockRegistry, ProjectBlockRegistry,
    BlockNotFoundError, BlockImportError,
    load_atomic_block,
    set_static_sources, get_static_sources, resolve_static
)

# Block helpers (3 usage modes: functions, config injection, OOP inheritance)
from .block_helpers import (
    BlockHelperConfig, BlockHelper,
    show_code, show_code_inline, show_explanation, show_details,
    set_block_helper_config, get_block_helper_config
)

# Collection system
from .collection import st_collection, CollectionConfig, ProjectMeta

# Google Sheets import
from .gsheet import (
    GSheetConfig, GSheetSource, GSheetError, AuthMode,
    set_gsheet_config, get_gsheet_config,
    load_gsheet, load_gsheet_df,
)

# Bibliography system
from .bib import (
    BibEntry, BibConfig, BibFormat, CitationStyle, BibParseError,
    BibRegistry, set_bib_config, get_bib_config,
    get_bib_registry, reset_bib_registry,
    load_bib, load_bibtex, load_bib_json, load_bib_ris, load_bib_csl_json,
    register_bib_parser, parse_bibtex_string, parse_ris_string,
    cite, st_cite, st_bibliography, format_entry, export_bibtex,
    st_refs, BibRefs, generate_bib_stubs,
)

# Link behavior configuration
from .link_config import LinkConfig, set_link_config, get_link_config

# AI image generation
from .ai import (
    AIImageConfig, AIImageError, AIImageResult,
    set_ai_image_config, get_ai_image_config,
    generate_image, is_cached, list_providers, get_available_models,
)
from .ai_image import st_ai_image, st_ai_image_widget

# Image management (history, metadata)
from .ai.history import save_version as save_image_version, get_current as get_current_image
from .ai.history import list_versions as list_image_versions, rollback as rollback_image
from .ai.history import rename_image
from .ai.metadata import ImageMetadata

# Browser recommendation banner
from .browser import st_chrome_banner

# Block Inspector (opt-in)
from .inspector import InspectorConfig, FileCategoryRegistry

# Restore stderr after all imports are done
_sys.stderr = _real_stderr
del _real_stderr, _io, _sys
