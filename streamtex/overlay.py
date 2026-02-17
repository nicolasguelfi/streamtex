import streamlit as st
from contextlib import contextmanager
from typing import Union
from .styles import Style, StreamTeX_Styles
from .container import st_block

class OverlayController:
    """
    Controller yielded by st_overlay to manage positioned elements.
    """
    def __init__(self):
        pass

    @contextmanager
    def layer(
        self, 
        style: Style = StreamTeX_Styles.none, 
        top: Union[str, int] = None, 
        left: Union[str, int] = None, 
        right: Union[str, int] = None, 
        bottom: Union[str, int] = None
    ):
        """
        Places content at a specific absolute position relative to the parent overlay.
        
        Args:
            style (Style): Additional styling for the placed container.
            top (str | int): CSS top value. Integers are treated as pixels.
            left (str | int): CSS left value. Integers are treated as pixels.
            right (str | int): CSS right value. Integers are treated as pixels.
            bottom (str | int): CSS bottom value. Integers are treated as pixels.
        """
        # Helper to process values (int -> "10px", None -> skip)
        def _fmt(val):
            if isinstance(val, int):
                return f"{val}px"
            return val

        # Construct CSS positioning string
        # We enforce absolute positioning and a high z-index to sit on top of the base layer
        pos_css = "position: absolute; z-index: 10;"
        
        if top is not None: pos_css += f" top: {_fmt(top)};"
        if left is not None: pos_css += f" left: {_fmt(left)};"
        if right is not None: pos_css += f" right: {_fmt(right)};"
        if bottom is not None: pos_css += f" bottom: {_fmt(bottom)};"
        
        # Combine user style with positioning logic
        final_style = f"{style} {pos_css}"
        
        with st_block(style=final_style):
            yield


@contextmanager
def st_overlay(style: Style = StreamTeX_Styles.none):
    """
    Creates a relative container for overlaying elements.
    
    Usage:
        with st_overlay() as o:
            st_image(uri="background.jpg")  # Base layer
            
            with o.layer(top=50, left=50):
                st_write("Overlay Text")
    """
    # 1. Base Container Style
    # position: relative is CRITICAL. It defines the coordinate system for absolute children.
    # display: inline-block ensures the container shrinks to fit the background image size.
    overlay_style = f"{style} position: relative;"
    
    with st_block(style=overlay_style):
        # Yield the controller to the user
        yield OverlayController()