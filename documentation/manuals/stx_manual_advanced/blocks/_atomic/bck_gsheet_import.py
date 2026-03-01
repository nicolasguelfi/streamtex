import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature = s.project.titles.feature_title
    content = s.large

bs = BlockStyles

# ============================================================================
# Demo data: real public Google Sheet + static fallback
# ============================================================================
# This public Google Sheet contains demo course data:
# https://docs.google.com/spreadsheets/d/1BxiMkKxX2z7dOlV3p1FHPHlAYMbXNpUjQclVw7JNHCQ/edit
#
# If the sheet is unreachable, we fall back to static data.
DEMO_SHEET_ID = "1BxiMkKxX2z7dOlV3p1FHPHlAYMbXNpUjQclVw7JNHCQ"

FALLBACK_DATA = [
    {"Student": "Alice", "Course": "AI Fundamentals", "Grade": "92", "Semester": "S1"},
    {"Student": "Bob", "Course": "AI Fundamentals", "Grade": "87", "Semester": "S1"},
    {"Student": "Charlie", "Course": "Deep Learning", "Grade": "95", "Semester": "S1"},
    {"Student": "Diana", "Course": "Deep Learning", "Grade": "88", "Semester": "S1"},
    {"Student": "Eve", "Course": "NLP", "Grade": "91", "Semester": "S2"},
    {"Student": "Frank", "Course": "NLP", "Grade": "84", "Semester": "S2"},
]


def _load_demo_data():
    """Try loading from Google Sheets, fall back to static data."""
    try:
        src = GSheetSource(sheet_id=DEMO_SHEET_ID, tab="Sheet1")
        cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC, cache_ttl=600)
        data = load_gsheet(src, config=cfg)
        if data:
            return data, True
    except Exception:
        pass
    return FALLBACK_DATA, False


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Google Sheets Data Import",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            StreamTeX can import data directly from Google Sheets.
            Supports public sheets (no auth) and private sheets (service account or OAuth2).
            Data integrates seamlessly with stx.st_dataframe, stx.st_table, and all chart widgets.
        """))
        st_space("v", 3)

        # --- Section 1: Configuration ---
        st_write(bs.sub, "1. Configuration", toc_lvl="+1")
        st_space("v", 2)

        show_code(file="examples/gsheet/config_auth_modes.py")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Credentials are resolved in order: explicit path > GSHEET_CREDENTIALS env > GOOGLE_APPLICATION_CREDENTIALS env.
            For deployed apps, set the GSHEET_CREDENTIALS environment variable.
            Cache TTL (seconds): 0 = no cache, None = cache forever, 300 = 5 minutes.
        """))
        st_space("v", 3)

        # --- Section 2: Loading Data ---
        st_write(bs.sub, "2. Loading Data", toc_lvl="+1")
        st_space("v", 2)

        show_code(file="examples/gsheet/loading_data.py")
        st_space("v", 3)

        # --- Section 3: Live Demo ---
        st_write(bs.sub, "3. Live Demo", toc_lvl="+1")
        st_space("v", 2)

        data, is_live = _load_demo_data()

        if is_live:
            with st_block(s.project.containers.good_callout):
                st_write(s.large + s.bold, "Data loaded from Google Sheets (live)")
        else:
            with st_block(s.project.containers.note_callout):
                st_write(s.large + s.bold, "Using static fallback data (sheet unreachable)")

        st_space("v", 2)

        # Show as dataframe
        st_write(bs.feature, "stx.st_dataframe()", toc_lvl="+1")
        st_space("v", 1)
        stx.st_dataframe(data, use_container_width=True)
        st_space("v", 2)

        # Show as metrics
        st_write(bs.feature, "Computed metrics", toc_lvl="+1")
        st_space("v", 1)

        try:
            grades = [float(row.get("Grade", 0)) for row in data if row.get("Grade")]
            avg = sum(grades) / len(grades) if grades else 0
            top = max(grades) if grades else 0
            count = len(data)
        except (ValueError, TypeError):
            avg, top, count = 0, 0, 0

        gap = ns("gap:24px;", "metric_gap")
        with st_grid(cols=3, grid_style=gap) as g:
            with g.cell():
                stx.st_metric("Students", str(count))
            with g.cell():
                stx.st_metric("Average Grade", f"{avg:.1f}")
            with g.cell():
                stx.st_metric("Top Grade", f"{top:.0f}")

        st_space("v", 3)

        # --- Section 4: Using in blocks ---
        st_write(bs.sub, "4. Pattern: Data in Blocks", toc_lvl="+1")
        st_space("v", 2)

        show_code(file="examples/gsheet/data_in_blocks.py")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Define GSheetSource at module level (loaded once per session).
            Use @st.cache_data for fine-grained caching if needed.
            Data flows through the standard export pipeline: stx.st_dataframe generates both Streamlit widget and HTML fallback.
        """))
