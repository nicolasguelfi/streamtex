import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

def build():
    # The following nested bullet point list is the expected result of the code below
    '''
    - Software Engineering
        * Requirements engineering
        * Critical systems
    '''
    with st_list(lt.unordered, s.container.lists.g_docs, s.project.green_01_bold + s.text.sizes.Large_size) as l:
        with l.item():
            st_write("Software Engineering")
            with st_list(lt.unordered, s.container.lists.g_docs, s.reset + s.text.sizes.large_size) as l2: # this call knows it is nested and will adjust and use list styles accordingly
                with l2.item(): st_write("Requirements engineering")
                with l2.item(): st_write("Critical systems")


