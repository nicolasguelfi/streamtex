import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

def build(dog_img="dog_sherlock.png"):

    st_image(uri = dog_img)
