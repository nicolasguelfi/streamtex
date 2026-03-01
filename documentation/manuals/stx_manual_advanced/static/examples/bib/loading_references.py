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
