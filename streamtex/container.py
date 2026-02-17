import streamlit as st
from contextlib import contextmanager
from .styles import Style, StreamTeX_Styles
from .utils import generate_key

@contextmanager
def st_block(style: Style = StreamTeX_Styles.none):
    """A Context Manager that wraps content within a styled container."""
    
    # 1. Generate a unique ID to scope the CSS to this specific block
    block_id = generate_key("block")
    
    # 2. Inject CSS that targets the container immediately following this style block
    # We use the :has() selector or adjacent sibling combinators to target the container
    css = f"""
    <style>
        {f'''
        div:has(> .stVerticalBlock > .element-container > .stHtml > span.{block_id}) {{
            height: 100%;
            flex-direction: row;

        }}
        ''' if False else ""}
        
        /* Target the specific container wrapper */
        div:has(> .element-container > .stHtml > span.{block_id}) {{
            {str(style)}
        }}
        
        .element-container:has(.stHtml > span.{block_id}) {{
            width: auto;
        }}
    </style>
    """
    
    # 3. Render the styles
    st.html(css)
    
    # 4. Create a native Streamlit container
    with st.container():
        # Insert a marker div so our CSS knows which container to target
        st.html(f'<span class="{block_id}" style="display:none;"></span>')
        yield
        
        
@contextmanager
def st_span(style: Style = StreamTeX_Styles.none):
    """
    A Context Manager that wraps content within a styled container.
    Its contents are inserted in the same line.
    """
    
    # 1. Generate a unique ID to scope the CSS to this specific block
    block_id = generate_key("span")
    
    # 2. Inject CSS that targets the container immediately following this style block
    # We use the :has() selector or adjacent sibling combinators to target the container
    css = f"""
    <style>
        div:has(> .element-container > .stHtml > span.{block_id}) > * {{
            /* make elements only occupy the width they need */
            width: auto;
        }}
        
        /* Target the specific container wrapper */
        div:has(> .element-container > .stHtml > span.{block_id}) {{
            /* make elements stay in same line*/
            display: flex; flex-direction: row;
            
            /* allow for whitespace to show*/
            white-space: pre;
            
            {str(style)}
        }}
        
        .element-container:has(.stHtml > span.{block_id}) {{
            width: auto;
        }}
    </style>
    """
    
    # 3. Render the styles
    st.html(css)
    
    # 4. Create a native Streamlit container
    with st.container():
        # Insert a marker div so our CSS knows which container to target
        st.html(f'<span class="{block_id}" style="display:none;"></span>')
        yield
        
        
        
