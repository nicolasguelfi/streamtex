import streamlit as st
import streamtex.styles as sts
from custom.themes import light_theme, dark_theme

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

col1, col2 = st.columns(2)
with col1:
    if st.button("Light Theme"):
        st.session_state.theme = "light"
with col2:
    if st.button("Dark Theme"):
        st.session_state.theme = "dark"

# Apply selected theme
if st.session_state.theme == "light":
    sts.theme = light_theme
else:
    sts.theme = dark_theme

# Now render blocks - they use the active theme
st_book(blocks=[...])
