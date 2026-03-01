from streamtex.bib import st_bibliography

st_bibliography(
    title="References",
    toc_lvl="1",
    only_cited=True,  # Only show entries cited via cite()
    format=BibFormat.APA,
)
