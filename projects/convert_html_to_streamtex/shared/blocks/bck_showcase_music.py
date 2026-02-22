import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #1155cc -> s.project.colors.link_blue
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Music ", tag=t.h3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "by MuseNet", "https://soundcloud.com/openai_audio/sonatina?in=openai_audio/sets/musenet&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"), (s.bold + s.italic, "("), (s.project.pres.links.default + s.project.colors.link_blue + s.bold + s.italic, "MuseNet", "https://openai.com/research/musenet"), (s.bold + s.italic, " music published on SoundCloud) "))
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "JukeBox", "https://jukebox.openai.com/?song=794232841"), (s.bold, "with voice generation "), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://jukebox.openai.com/?song=787877257"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://jukebox.openai.com/?song=802882084"))
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.pres.links.link_lg + s.project.colors.link_blue, "Suno", "https://app.suno.ai/create/"), (s.bold, "with voice generation "), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://suno.com/song/4da4b386-e76e-4465-b6fe-b151b2e6849f"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://app.suno.ai/song/c56ab50e-0f62-4470-8603-814b83d9b6b0"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://app.suno.ai/song/d91cb3a3-a40f-4cf4-9694-f0046ca3e978"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://suno.com/song/ec329950-1a0c-45af-bd12-b46eb7de707f"), (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://suno.com/song/b483407f-ec6e-4b6d-8626-be734cda0e0c"))
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
