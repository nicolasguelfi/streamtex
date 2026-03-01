import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap
import os
import json


class BlockStyles:
    """Static assets demo styles."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles

# _atomic/ → blocks/ → project root (where book.py and static/ live)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_static_dir = os.path.join(_project_root, "static")


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Static Assets", tag=t.div, toc_lvl="1")
        st_space("v", 2)

        # --- 1. Folder Organization ---
        st_write(bs.sub, "Folder organization", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Organize static files by type under a static/ directory.

            Enable static serving in .streamlit/config.toml.
        """))
        st_space("v", 1)

        show_code(file="examples/static_assets/folder_organization.txt", language="text")
        st_space("v", 2)

        # --- 2. Local Images ---
        st_write(bs.sub, "Local images", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Use configure_image_path() to set the base directory,
            then st_image() with just the filename.
        """))
        st_space("v", 1)

        show_code("""\
configure_image_path("app/static/images")
st_image(uri="sample_gradient.png",
         width="400px", height="250px",
         alt="Sample gradient image")""")
        st_space("v", 1)

        configure_image_path("app/static/images")
        st_image(uri="sample_gradient.png",
                 width="400px", height="250px",
                 alt="Sample gradient image")
        st_space("v", 2)

        # --- 3. Text Files ---
        st_write(bs.sub, "Text files", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Read text files with open() and display
            their content with st_code() or st_write().
        """))
        st_space("v", 1)

        show_code("""\
text_path = os.path.join("static", "texts", "sample_lorem.txt")
with open(text_path) as f:
    content = f.read()
stx.st_code(code=content, language="text")""")
        st_space("v", 1)

        text_path = os.path.join(_static_dir, "texts", "sample_lorem.txt")
        with open(text_path) as f:
            content = f.read()
        stx.st_code(s.project.containers.code_box, code=content, language="text")
        st_space("v", 2)

        # --- 4. PDF Documents ---
        st_write(bs.sub, "PDF documents", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Embed PDFs using st_html() with an iframe
            pointing to the static-served file.
        """))
        st_space("v", 1)

        show_code("""\
pdf_url = "app/static/pdf/sample_document.pdf"
st_html(
    f'<iframe src="{pdf_url}" '
    f'width="100%" height="400" '
    f'style="border:none;"></iframe>'
)""")
        st_space("v", 1)

        pdf_url = "app/static/pdf/sample_document.pdf"
        st_html(
            f'<iframe src="{pdf_url}" '
            f'width="100%" height="400" '
            f'style="border:none;"></iframe>'
        )
        st_space("v", 2)

        # --- 5. Audio Files ---
        st_write(bs.sub, "Audio files", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Play audio with stx.st_audio() (Streamlit native).

            This is an interactive widget, so st.* is correct.
        """))
        st_space("v", 1)

        show_code("""\
audio_path = os.path.join("static", "sounds", "sample_tone.wav")
stx.st_audio(audio_path, format="audio/wav")""")
        st_space("v", 1)

        audio_path = os.path.join(_static_dir, "sounds", "sample_tone.wav")
        stx.st_audio(audio_path, format="audio/wav")
        st_space("v", 2)

        # --- 6. Local Video Files ---
        st_write(bs.sub, "Local video files", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Play local video with stx.st_video() (Streamlit native).

            Place .mp4, .webm, .ogg files in static/videos/.
        """))
        st_space("v", 1)

        show_code("""\
video_path = os.path.join("static", "videos", "chameleon.mp4")
stx.st_video(video_path)""")
        st_space("v", 1)

        video_path = os.path.join(_static_dir, "videos", "chameleon.mp4")
        stx.st_video(video_path)
        st_space("v", 2)

        # --- 7. YouTube Videos ---
        st_write(bs.sub, "YouTube videos", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Embed YouTube videos by reading URLs from a file
            and using stx.st_video() with the URL directly.
        """))
        st_space("v", 1)

        show_code("""\
# Read URL from a file
url_file = os.path.join("static", "videos", "youtube_urls.txt")
with open(url_file) as f:
    youtube_url = f.readline().strip()
stx.st_video(youtube_url)""")
        st_space("v", 1)

        url_file = os.path.join(_static_dir, "videos", "youtube_urls.txt")
        with open(url_file) as f:
            youtube_url = f.readline().strip()
        stx.st_video(youtube_url)
        st_space("v", 2)

        # --- 8. Various Data Files ---
        st_write(bs.sub, "Data files (JSON, CSV, ...)", toc_lvl="+1")
        st_space("v", 1)

        show_explanation(textwrap.dedent("""\
            Load structured data with standard Python libraries
            and display with st_code() or st.dataframe().
        """))
        st_space("v", 1)

        show_code("""\
import json
json_path = os.path.join("static", "various", "sample_data.json")
with open(json_path) as f:
    data = json.load(f)
stx.st_code(code=json.dumps(data, indent=2), language="json")""")
        st_space("v", 1)

        json_path = os.path.join(_static_dir, "various", "sample_data.json")
        with open(json_path) as f:
            data = json.load(f)
        stx.st_code(s.project.containers.code_box,
                   code=json.dumps(data, indent=2), language="json")
        st_space("v", 2)

        show_details(textwrap.dedent("""\
            Static serving requires enableStaticServing = true in config.toml.

            Files under static/ are served at the app/static/ URL prefix.

            Use st_image() for images (StreamTeX native).

            Use stx.st_audio(), stx.st_video() for media (Streamlit interactive widgets).
        """))
