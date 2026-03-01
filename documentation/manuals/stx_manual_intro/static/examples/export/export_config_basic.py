from streamtex.export import ExportConfig

# ExportConfig fields:
#   enabled: bool       = False   (st_book sets this to True)
#   page_title: str     = "StreamTeX Export"
#   page_width: str     = "100%"
#   page_padding: str   = "36pt"

# The simplest way: just set export_title in st_book()
st_book([...], export_title="My Document Title")
