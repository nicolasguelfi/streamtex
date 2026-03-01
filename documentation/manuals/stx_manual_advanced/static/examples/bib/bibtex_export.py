from streamtex.bib import export_bibtex

bibtex_str = export_bibtex(only_cited=True)
st.download_button("Download .bib", bibtex_str, "references.bib")
