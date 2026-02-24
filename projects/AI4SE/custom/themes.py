"""Dark theme overrides for AI4SE project.

Keys are style_ids (from custom/styles.py), values are replacement CSS strings.
These override the base styles when the dark theme is active.
"""

dark = {
    # Colors (boost brightness for dark surfaces)
    "primary": "color: #7AB8F5;",
    "accent": "color: #33E6C4;",
    "highlight": "color: #FFC964;",

    # Titles (brighter in dark mode)
    "course_title": "color: #7AB8F5; font-weight: bold; font-size: 128pt;",
    "section_title": "color: #7AB8F5; font-weight: bold; font-size: 80pt;",
    "section_subtitle": "color: #33E6C4; font-weight: bold; font-size: 48pt;",

    # Labels
    "tip_label": "color: #7AB8F5; font-weight: bold; font-size: 32pt;",
    "highlight_label": "color: #FFC964; font-weight: bold; font-size: 32pt;",

    # Backgrounds (stronger opacity in dark mode)
    "primary_bg": "background-color: rgba(91, 156, 246, 0.15);",
    "accent_bg": "background-color: rgba(0, 212, 170, 0.15);",
    "code_box": (
        "background-color: rgba(91, 156, 246, 0.10);"
        "border: 1px solid rgba(91, 156, 246, 0.30);"
        "border-radius: 6px;"
        "padding: 12px;"
    ),
}
