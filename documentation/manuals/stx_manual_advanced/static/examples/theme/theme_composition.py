# Define a base theme
base_theme = {
    "primary_blue": "color: #4A90D9;",
    "primary_text": "color: #333333;",
    "accent_green": "color: #2ECC71;",
}

# Dark variant overrides specific colors
dark_theme = {
    **base_theme,  # Inherit all base colors
    "primary_blue": "color: #7AB8F5;",  # Lighter blue
    "primary_text": "color: #E0E0E0;",  # Lighter text
}

# Activate in book.py
import streamtex.styles as sts
sts.theme = dark_theme
