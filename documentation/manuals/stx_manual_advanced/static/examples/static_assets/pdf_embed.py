pdf_url = "app/static/pdf/sample_document.pdf"
st_html(
    f'<iframe src="{pdf_url}" '
    f'width="100%" height="400" '
    f'style="border:none;"></iframe>'
)
