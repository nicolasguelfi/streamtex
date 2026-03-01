"""Atomic block — Syntax Highlighting: Pygments language browser with filter."""

import csv
import textwrap

import pandas as pd
import streamlit as st

import streamtex as stx
from streamtex import *
from streamtex.enums import Tags as t

from blocks.helpers import show_explanation
from custom.styles import Styles as s


class BlockStyles:
    """Syntax highlighting block styles."""

    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle


bs = BlockStyles


def build():
    """Pygments language browser with interactive text_input filter."""
    with st_block(s.center_txt):
        st_write(bs.heading, "Syntax Highlighting", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        st_write(bs.sub, "Supported languages (Pygments)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            The **language** parameter of **st_code()** accepts any Pygments
            lexer short name for syntax highlighting.

            Below is the complete list of all supported languages.
            Use the search field to filter by name or description.
        """))
        st_space("v", 1)

        # Load CSV
        csv_path = stx.resolve_static("examples/code/pygments_languages.csv")
        languages = []
        if csv_path:
            with open(csv_path, encoding="utf-8") as f:
                languages = sorted(
                    [*csv.DictReader(f)], key=lambda r: r["language"].lower()
                )

        # Search field (Streamlit native widget)
        search = st.text_input(
            "Filter languages",
            key="bck_syntax_lang_filter",
            placeholder="Type to filter (e.g. python, java, css...)",
        )

        # Filter logic
        if search:
            tokens = search.lower().split()
            filtered = [
                lang
                for lang in languages
                if all(
                    tok in (lang["language"] + " " + lang["description"]).lower()
                    for tok in tokens
                )
            ]
        else:
            filtered = languages[:20]

        # Counter
        if search:
            st_write(s.small, f"{len(filtered)} of {len(languages)} languages")
        else:
            st_write(s.small, f"Top 20 of {len(languages)} languages")
        st_space("v", 1)

        # Single st.dataframe — one React component instead of N st_grid() calls
        if filtered:
            df = pd.DataFrame(filtered)[["language", "description", "url"]]
            df.columns = ["Language", "Description", "Site"]
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Site": st.column_config.LinkColumn("Site", display_text="Link"),
                },
            )
        elif search:
            st_write(s.large, f'No language matching "{search}"')
