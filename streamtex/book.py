import streamlit as st
from streamlit.delta_generator import DeltaGenerator as Delta
import time
import os
import importlib.resources as resources

from .styles import Style
from .write import st_write
from .space import st_space, st_br
from .toc import reset_toc_registry, toc_entries, TOCConfig
from .marker import reset_marker_registry, inject_marker_navigation, MarkerConfig, marker_entries
from .enums import Tags
from .utils import inject_link_preview_scaffold
from .zoom import add_zoom_options


def st_book(module_list, toc_config: TOCConfig = None, marker_config: MarkerConfig = None, separator=None, *args, **kwargs):
    """Generates a web page e-book from a list of block modules.

    :param separator: Optional module with a build() function, rendered between each block.
    """
    start_time = time.time()
    print("Starting st_book function...")

    # Load default CSS styles
    load_css("default.css")

    # Ensure the hover card is ready before any content is rendered.
    inject_link_preview_scaffold()

    # Add zoom options to sidebar
    add_zoom_options()

    # Clear previous run's headers
    reset_toc_registry(toc_config)

    # Initialize marker navigation (opt-in)
    if marker_config is not None:
        reset_marker_registry(marker_config)

    # Extract ToC config and create ToC placeholders
    use_toc_sidebar = toc_config is not None
    use_toc_block = use_toc_sidebar and toc_config.toc_position is not None
    if use_toc_sidebar:
        toc_sidebar = build_ToC_sidebar_placeholder()
        toc_block = None
        toc_content_style = None
    if use_toc_block:
        # Determine ToC insertion position
        toc_pos = toc_config.toc_position
        if toc_pos < 0 or toc_pos >= len(module_list):
            toc_pos = len(module_list)
        toc_title_style = toc_config.title_style
        toc_content_style = toc_config.content_style

    # Run the blocks (potentially populating the ToC registry)
    for i, module in enumerate(module_list):

        # Generate Toc at appropriate position
        if use_toc_block and i == toc_pos:
            toc_block = st_toc(toc_title_style)

        st_include(module, *args, **kwargs)

        # Separator between blocks (not after the last one)
        if separator and i < len(module_list) - 1:
            st_include(separator, *args, **kwargs)

        st_space("v", "70px")

    # Generate Toc at appropriate position
    if use_toc_block and toc_pos == len(module_list):
        toc_block = st_toc(toc_title_style)

    # Fill the ToC placeholder
    if use_toc_sidebar:
        populate_toc(toc_sidebar, toc_block, toc_content_style)

    # Inject marker navigation JS (only if markers were registered)
    if marker_config is not None:
        inject_marker_navigation()

    end_time = time.time()
    duration = end_time - start_time
    print(f"st_book function completed in {duration:.2f} seconds.")


def load_css(file_name: str):
    """Loads a CSS file and injects it into the StreamTeX app."""
    try:
        with resources.open_text('streamtex.static', file_name) as f:
            st.html(f'<style>{f.read()}</style>')
    except (FileNotFoundError, ModuleNotFoundError, TypeError) as e:
        print(f"[StreamTeX] CSS resource fallback for '{file_name}': {e}")
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, 'static')
        css_file_path = os.path.join(static_dir, file_name)
        # Read the CSS file
        with open(css_file_path, 'r') as f:
            st.html(f'<style>{f.read()}</style>')


def build_ToC_sidebar_placeholder():
    with st.sidebar:
        st.header("Table of Contents")
        toc_sidebar = st.empty()

    return toc_sidebar


def populate_toc(toc_sidebar: Delta, toc_block: Delta = None, toc_content_style: Style = None):
    toc_entry_list = toc_entries()
    marker_anchors = {m['anchor'] for m in marker_entries()}
    indent_char = "&nbsp;"

    with toc_sidebar.container():
        for entry in toc_entry_list:
            # Indentation based on level
            indent = indent_char * (entry['level'] - 1) * 4

            # Marker indicator dot for TOC entries that are also navigation markers
            dot = ('<span style="opacity:.5;font-size:6px;vertical-align:middle;'
                   'margin-right:4px;">&#9679;</span>'
                   if entry['key_anchor'] in marker_anchors else '')

            # Native Streamlit Link to ID
            st.html(
                f"<span style=\"overflow: hidden; text-overflow: ellipsis; text-wrap: nowrap; word-wrap: normal;\">"
                f"{indent}{dot}<a href=\"#{entry['key_anchor']}\">{entry['title']}</a></span>"
            )
    if toc_block is not None:
        with toc_block.container():
            for entry in toc_entry_list:
                indent = indent_char * (entry['level'] - 1) * 2
                st_write(toc_content_style, f"{indent}{entry['title']}",
                                link=f"#{entry['key_anchor']}", hover=False, no_link_decor=True)
                st_br()


def st_toc(toc_title_style):
    st_write(toc_title_style, "Table of Contents", tag=Tags.div, toc_lvl='1')
    st_space("v", 4)
    toc_block = st.empty()
    st_space("v", "70px")
    return toc_block


def st_include(block_file_module, *args, **kwargs):
    if not block_file_module:
        st.markdown(f":red-background[File {block_file_module.__path__} not found]")
        return

    if not hasattr(block_file_module, 'build'):
        st.markdown(f":red-background[The file {block_file_module.__path__} does not contain a build() function.]")
        return

    module_name = getattr(block_file_module, '__name__', str(block_file_module))
    try:
        block_file_module.build(*args, **kwargs)
    except Exception as e:
        st.markdown(f":red-background[Error in block '{module_name}': {e}]")
        raise
