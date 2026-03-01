from streamtex.export import ExportConfig

config = ExportConfig(
    enabled=True,                    # Enable/disable export
    page_title="My Document",        # <title> tag
    page_width="100%",             # Page width in export
    page_padding="36pt",             # Page padding/margins
    include_styles=True,             # Include all CSS
    include_images=True,             # Embed images as base64
    prettify_html=False,             # Format HTML (slower)
)

st_book([...], export_config=config)
