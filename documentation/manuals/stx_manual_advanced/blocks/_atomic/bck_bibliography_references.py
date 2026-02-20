import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
from streamtex.bib import cite, st_bibliography, export_bibtex, get_bib_registry
from custom.bib_refs import st_refs
import textwrap


class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
    feature = s.project.titles.feature_title
    content = s.large
    cite_demo = ns(
        "background-color: rgba(74,144,217,0.06); border-radius: 8px; padding: 16px 20px;",
        "cite_demo"
    )

bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Bibliography & References",
                 tag=t.div, toc_lvl="1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            StreamTeX provides a built-in bibliography system.
            Load references from BibTeX, JSON, RIS, or CSL-JSON files.
            Cite inline with hover preview. Render formatted bibliographies in APA, IEEE, MLA, Chicago, or Harvard style.
        """))
        st_space("v", 3)

        # --- Section 1: Loading References ---
        st_write(bs.sub, "1. Loading References", toc_lvl="+1")
        st_space("v", 2)

        show_code(textwrap.dedent("""\
            # In book.py — load references at startup
            from streamtex.bib import BibConfig, BibFormat, CitationStyle
            from pathlib import Path

            st_book(
                module_list,
                bib_sources=[str(Path(__file__).parent / "static" / "references.bib")],
                bib_config=BibConfig(
                    format=BibFormat.APA,
                    citation_style=CitationStyle.AUTHOR_YEAR,
                    hover_enabled=True,
                    hover_show_abstract=True,
                ),
            )
        """))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Supported import formats: .bib (BibTeX), .json (JSON array), .ris (RIS/Zotero), .csl-json (CSL-JSON/Mendeley).
            Add custom formats with register_bib_parser("ext", parser_function).
            References are loaded once per st_book() render and cached in the BibRegistry singleton.
        """))
        st_space("v", 3)

        # --- Section 2: Inline Citations ---
        st_write(bs.sub, "2. Inline Citations with cite() and st_refs", toc_lvl="+1")
        st_space("v", 2)

        show_code(textwrap.dedent("""\
            from streamtex.bib import cite
            from custom.bib_refs import st_refs  # Generated — IDE completion!

            # Option A: cite() with string keys
            st_write(s.big,
                "The Transformer architecture ",
                cite("vaswani2017attention"),
                " revolutionized NLP."
            )

            # Option B: st_refs with IDE autocompletion (recommended)
            st_write(s.big,
                "The Transformer architecture ",
                st_refs.vaswani2017attention,    # ← Ctrl+Space completes!
                " revolutionized NLP."
            )

            # For multi-key citations, use cite() directly:
            cite("lecun2015deep", "goodfellow2016deep")  # (LeCun; Goodfellow)
        """))
        st_space("v", 2)

        # Live demo — using st_refs
        with st_block(bs.cite_demo):
            st_write(s.project.titles.tip_label, "Live result (using st_refs):")
            st_space("v", 1)
            st_write(s.big,
                "The Transformer architecture ",
                st_refs.vaswani2017attention,
                " revolutionized NLP. "
                "Pre-trained models like BERT ",
                st_refs.devlin2019bert,
                " extended this to transfer learning."
            )
            st_space("v", 2)
            st_write(s.big,
                "Scaling laws ",
                st_refs.brown2020language,
                " showed that larger models achieve remarkable few-shot performance, "
                "building on foundational work in deep learning ",
                cite("lecun2015deep", "goodfellow2016deep"),
                "."
            )

        st_space("v", 2)

        show_details(textwrap.dedent("""\
            st_refs.key is equivalent to cite("key") but enables IDE autocompletion.
            For multi-key citations, use cite("key1", "key2") → (Author1; Author2, Year).
            Hover over citations above to see the preview card. Click Copy or Open.
        """))
        st_space("v", 3)

        # --- Section 3: Citation Styles ---
        st_write(bs.sub, "3. Citation Styles", toc_lvl="+1")
        st_space("v", 2)

        show_code(textwrap.dedent("""\
            from streamtex.bib import CitationStyle

            # (Vaswani et al., 2017) — default
            BibConfig(citation_style=CitationStyle.AUTHOR_YEAR)

            # [1]
            BibConfig(citation_style=CitationStyle.NUMERIC)

            # ^1 (superscript)
            BibConfig(citation_style=CitationStyle.SUPERSCRIPT)
        """))
        st_space("v", 3)

        # --- Section 4: Import Formats ---
        st_write(bs.sub, "4. Import Formats", toc_lvl="+1")
        st_space("v", 2)

        cell_style = (s.container.borders.solid_border
                      + s.container.paddings.small_padding)
        header_style = sg.create("A1:D1", cell_style + s.bold + s.large + s.project.colors.primary_blue)
        data_style = sg.create("A2:D5", cell_style + s.large)

        with st_grid(cols=4, cell_styles=header_style + data_style) as g:
            for col in ["Format", "Extension", "Source", "Function"]:
                with g.cell():
                    st_write(col)
            for row in [
                ("BibTeX", ".bib", "LaTeX / Google Scholar", "load_bibtex()"),
                ("JSON", ".json", "Custom / API", "load_bib_json()"),
                ("RIS", ".ris", "Zotero / Mendeley / EndNote", "load_bib_ris()"),
                ("CSL-JSON", ".csl-json", "Zotero native export", "load_bib_csl_json()"),
            ]:
                for cell in row:
                    with g.cell():
                        st_write(cell)

        st_space("v", 2)

        show_code(textwrap.dedent("""\
            # Auto-detect by extension
            from streamtex.bib import load_bib
            entries = load_bib("references.bib")   # BibTeX
            entries = load_bib("refs.ris")          # RIS
            entries = load_bib("refs.json")         # JSON

            # Add a custom parser
            from streamtex.bib import register_bib_parser

            def parse_yaml(path):
                import yaml
                with open(path) as f:
                    data = yaml.safe_load(f)
                return [BibEntry(key=d["key"], ...) for d in data]

            register_bib_parser("yaml", parse_yaml)
        """))
        st_space("v", 3)

        # --- Section 5: Extensible Fields ---
        st_write(bs.sub, "5. Extensible Fields", toc_lvl="+1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            BibEntry has 20+ standard fields (title, authors, year, journal, doi, etc.).
            Any unknown fields from your source files are preserved in the 'extra' dict.
            Access them with entry.get_field("custom_field").
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            entry = BibEntry(
                key="example",
                title="My Paper",
                authors=["Smith, J."],
                year="2024",
                # Standard fields
                isbn="978-3-16-148410-0",
                keywords="AI, deep learning",
                institution="MIT",
                # Extra fields preserved automatically from BibTeX
                extra={"funding": "NSF Grant 12345"},
            )

            entry.get_field("isbn")       # "978-3-16-148410-0"
            entry.get_field("funding")    # "NSF Grant 12345" (from extra)
            entry.get_field("missing", "N/A")  # "N/A"
        """))
        st_space("v", 3)

        # --- Section 6: Registry Info ---
        st_write(bs.sub, "6. Registry Status", toc_lvl="+1")
        st_space("v", 2)

        reg = get_bib_registry()
        all_entries = reg.get_all_entries()
        cited_entries = reg.get_cited_entries()

        gap_style = ns("gap:16px;", "reg_gap")
        with st_grid(cols=3, grid_style=gap_style) as g:
            with g.cell():
                stx.st_metric("Registered", str(len(all_entries)))
            with g.cell():
                stx.st_metric("Cited", str(len(cited_entries)))
            with g.cell():
                stx.st_metric("Available keys", str(len(reg.list_keys())))

        st_space("v", 2)

        if all_entries:
            st_write(bs.feature, "Registered entries:")
            st_space("v", 1)
            for entry in all_entries:
                st_write(s.big, f"  {entry.key}",
                         (s.project.colors.neutral_gray, f" ({entry.entry_type}) "),
                         (s.italic, entry.title[:60] + ("..." if len(entry.title) > 60 else "")))

        st_space("v", 3)

        # --- Section 7: Rendered Bibliography ---
        st_write(bs.sub, "7. Rendered Bibliography (APA)", toc_lvl="+1")
        st_space("v", 2)

        show_code(textwrap.dedent("""\
            from streamtex.bib import st_bibliography

            st_bibliography(
                title="References",
                toc_lvl="1",
                only_cited=True,  # Only show entries cited via cite()
                format=BibFormat.APA,
            )
        """))
        st_space("v", 2)

        st_bibliography(
            title="",
            style=bs.cite_demo,
            only_cited=True,
        )

        st_space("v", 3)

        # --- Section 8: BibTeX Export ---
        st_write(bs.sub, "8. BibTeX Export", toc_lvl="+1")
        st_space("v", 2)

        show_code(textwrap.dedent("""\
            from streamtex.bib import export_bibtex

            bibtex_str = export_bibtex(only_cited=True)
            st.download_button("Download .bib", bibtex_str, "references.bib")
        """))
        st_space("v", 1)

        bibtex_str = export_bibtex(only_cited=True)
        if bibtex_str:
            st.download_button(
                "Download cited references (.bib)",
                bibtex_str,
                "cited_references.bib",
                mime="application/x-bibtex",
                key="bck_bib_download",
            )

        st_space("v", 3)

        # --- Section 9: st_refs & IDE Autocompletion ---
        st_write(bs.sub, "9. st_refs & IDE Autocompletion", toc_lvl="+1")
        st_space("v", 2)

        show_explanation(textwrap.dedent("""\
            st_refs maps attribute access to cite() calls with full IDE autocompletion.
            Generate a typed Python module from your .bib file, then import st_refs
            from there. Your IDE shows all keys with docstrings (title, authors, year).
        """))
        st_space("v", 1)

        show_code(textwrap.dedent("""\
            # Step 1: Generate typed module from your bibliography file
            # Run once (or whenever your .bib changes):
            #   uv run python -m streamtex generate-stubs static/refs.bib -o custom/bib_refs.py

            # Step 2: Import st_refs from the generated module
            from custom.bib_refs import st_refs  # ← IDE sees all keys!

            st_write(s.big,
                "According to ", st_refs.vaswani2017attention,   # Ctrl+Space!
                " the Transformer architecture..."
            )

            # cite() still works for multi-key and prefix/suffix:
            cite("lecun2015deep", "goodfellow2016deep")  # (LeCun; Goodfellow)
            cite("vaswani2017attention", prefix="cf. ", suffix=", p. 42")
        """))
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            The generated .py contains @property definitions with docstrings for each key.
            Unknown keys (added after generation) still work via __getattr__ fallback — just without completion.
            Regenerate with the same command when you add or modify bibliography entries.
        """))
