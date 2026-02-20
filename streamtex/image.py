import os
import streamlit as st
from .styles import Style, StreamTeX_Styles
from .export import _render
from .utils import __is_url, __is_absolute_path, __is_relative_path, __get_mime_type, __get_base64_encoded_image, contain_link
from .blocks import get_static_sources

_static_image_base = "app/static/images"


def configure_image_path(base_path: str):
    """Configure the base path used to resolve static image URIs."""
    global _static_image_base
    _static_image_base = base_path

def st_image(
    style: Style = StreamTeX_Styles.none,
    width="100%", height="auto",
    uri: str="", alt:str="",
    link:str="", hover:bool=True
):
    """
    Generates an HTML `img` tag based on the image URI, with optional styles, link wrapping, and hover effects.

    :param style: A `Style` object defining CSS styles to apply to the image. Defaults to `StreamTeX_Styles.none`.
    :param width: The width of the image. Can be a string (e.g., "50%") or an integer (e.g., 100). Defaults to "100%".
    :param height: The height of the image. Can be a string (e.g., "300px") or an integer (e.g., 300). Defaults to "100%".
    :param uri: The image URI. Can be:
        - A URL (e.g., "https://example.com/image.png").
        - An absolute path (e.g., "C:User/images/image.png").
        - A relative path (e.g., "/images/image.png". This can start with '.', '..', '/' and backslash).
        - A static path (e.g., images/image.png).
    :param alt: The alternative text for the image, used for accessibility or when the image cannot be displayed.
    :param link: An optional hyperlink to wrap around the image. Defaults to an empty string (no link).
    :param hover: If True, enables hover functionality for the image link. Defaults to True.
    :return: A string containing the HTML `img` tag, optionally wrapped in a hyperlink.

    Notes:
    - URLs are used directly as the `src` attribute.
    - Local files are base64 encoded for compatibility with browsers that don't allow local file paths in HTML.
    - If the URI cannot be resolved or is unsupported, the `src` attribute is left empty.
    - The function wraps the image tag in a link if `link` is provided, using the `contain_link` function.
    """
    # 1. Convert integer sizes to pixel-based strings
    if isinstance(width, int):
        width = f"{width}px"
    if isinstance(height, int):
        height = f"{height}px"
    
    # 2. Get the source (URL or Base64)
    img_src = get_image_src(uri)

    # 3. Show placeholder if image not found
    if not img_src:
        placeholder = (
            f'<div style="border:2px dashed #888;padding:16px;text-align:center;'
            f'color:#888;border-radius:4px;margin:8px 0;">'
            f'Image not found: {uri}</div>'
        )
        _render(placeholder)
        return

    # 4. Construct the CSS style string
    css_style = f"{str(style)} width: {width}; height: {height};"

    # 5. Construct the HTML
    html_content = f'<img src="{img_src}" alt="{alt}" style="{css_style}">'
    
    # 6. Handle Link Wrapping
    html_content = contain_link(html_content, link, False, hover)

    # 7. Render
    _render(html_content)

def get_image_src(uri: str) -> str:
    """
    Resolves the image source from a URL, absolute path, relative path, or static file.
    """
    img_src = ""
    if __is_url(uri):
        # If it's a URL, use it directly
        img_src = uri
    elif __is_absolute_path(uri) or __is_relative_path(uri):
        # If it's an absolute or relative path, try converting the file to base64
        file_path = uri if __is_absolute_path(uri) else os.path.join(os.getcwd(), uri)
        
        # Check if file exists before trying to read it
        if os.path.exists(file_path):
            mime_type = __get_mime_type(file_path)
            encoded_image = __get_base64_encoded_image(file_path)
            if mime_type and encoded_image:
                # Use base64 encoding for local files with correct MIME type
                img_src = f"data:{mime_type};base64,{encoded_image}"
            else:
                img_src = ""  # Unsupported format or encoding failed
        else:
            img_src = "" # File not found
    else:
        # If no specific relative or absolute indicator, try configured static sources first
        static_sources = get_static_sources()

        for base in static_sources:
            # Try multiple common subdirectories in static sources
            for subdir in ["images", ""]:
                if subdir:
                    full_path = os.path.join(base, subdir, uri)
                else:
                    full_path = os.path.join(base, uri)

                if os.path.isfile(full_path):
                    mime_type = __get_mime_type(full_path)
                    encoded_image = __get_base64_encoded_image(full_path)
                    if mime_type and encoded_image:
                        img_src = f"data:{mime_type};base64,{encoded_image}"
                        return img_src

        # Fallback: use legacy static path (for Streamlit's built-in static serving)
        img_src = f"{_static_image_base}/{uri}"

    return img_src

