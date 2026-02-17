"""Image utility functions: base64 encoding, MIME detection, URL/path detection."""

import os
import base64


def _is_url(path: str):
    """Checks if the given path is a URL."""
    return path.startswith(("http://", "https://", "www."))


def _is_absolute_path(path: str):
    """Checks if the given path is an absolute path."""
    return os.path.isabs(path)


def _is_relative_path(path: str):
    """Checks if the given path is a relative path."""
    return path.startswith((".", "..", "/", "\\"))


def _get_mime_type(file_path: str):
    """Determine the MIME type based on the file extension."""
    extension = file_path.lower().split('.')[-1]
    if extension == "png":
        return "image/png"
    elif extension in ["jpg", "jpeg"]:
        return "image/jpeg"
    elif extension == "gif":
        return "image/gif"
    else:
        return None


def _get_base64_encoded_image(file_path: str):
    """Converts an image to a base64 encoded string."""
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
