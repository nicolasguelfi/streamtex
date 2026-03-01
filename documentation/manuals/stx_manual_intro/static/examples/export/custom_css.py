from streamtex.export import ExportConfig

# Print-friendly CSS for exports
export_css = """
@media print {
    body { font-size: 12pt; line-height: 1.5; }
    .no-print { display: none; }
    a { text-decoration: underline; }
}
"""

# Note: Currently, use inline styles in blocks instead
# Future: ExportConfig will support custom_css parameter
st_book([...])
