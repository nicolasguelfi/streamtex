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
