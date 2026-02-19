"""StreamTeX Collection - Hub for multiple projects."""

import streamlit as st
import setup
from streamtex import st_collection, CollectionConfig
from custom.styles import Styles as s
from custom.themes import dark
import streamtex.styles as sts

st.set_page_config(
    page_title="Course Library",
    layout="wide",
    initial_sidebar_state="collapsed"
)
sts.theme = dark

# Load collection configuration from TOML
config = CollectionConfig.from_toml("collection.toml")

# Display the collection
st_collection(
    config=config,
    home_styles=s,
)
