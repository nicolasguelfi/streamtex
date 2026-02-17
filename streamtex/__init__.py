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

# Enums
from .enums import Tags

# Zoom
from .zoom import add_zoom_options, inject_zoom_logic

# Utilities
from .utils import inject_link_preview_scaffold
