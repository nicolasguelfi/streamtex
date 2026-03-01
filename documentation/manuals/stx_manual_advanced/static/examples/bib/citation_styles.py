from streamtex.bib import CitationStyle

# (Vaswani et al., 2017) — default
BibConfig(citation_style=CitationStyle.AUTHOR_YEAR)

# [1]
BibConfig(citation_style=CitationStyle.NUMERIC)

# ^1 (superscript)
BibConfig(citation_style=CitationStyle.SUPERSCRIPT)
