"""StreamTeX — A Streamlit wrapper for styled content rendering."""

__version__ = "0.2.0"

# Core style system
from .styles import Style, ListStyle, StyleGrid, StreamTeX_Styles, theme

# Content rendering
from .write import st_write
from .image import st_image, configure_image_path
from .code import st_code
from .container import st_block, st_span
from .space import st_space, st_br
from .grid import st_grid
from .list import st_list
from .overlay import st_overlay

# Book orchestration
from .book import st_book, st_include, st_toc, load_css

# Table of Contents
from .toc import reset_toc_registry, toc_entries, TOCConfig

# Marker Navigation
from .marker import st_marker, MarkerConfig

# Enums
from .enums import Tags

# Zoom
from .zoom import add_zoom_options, inject_zoom_logic

# Export
from .export import ExportConfig, st_export

# Export-aware widget wrappers
from .export_widgets import (
    st_dataframe, st_table, st_metric, st_json, st_graphviz,
    st_line_chart, st_bar_chart, st_area_chart, st_scatter_chart,
    st_audio, st_video,
)

# Utilities
from .utils import inject_link_preview_scaffold

# Multi-source block registry and static resolution
from .blocks import (
    LazyBlockRegistry, ProjectBlockRegistry,
    BlockNotFoundError, BlockImportError,
    set_static_sources, get_static_sources, resolve_static
)

# Collection system
from .collection import st_collection, CollectionConfig, ProjectMeta
