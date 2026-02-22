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
      #37761c -> s.project.colors.olive_green
      #434343 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #ff00ff
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h2, "0.1. Showcase ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.1. Text Generation ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Tool ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "OpenAI ChatGPT ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.datacamp.com/blog/yolo-object-detection-explained")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Microsoft CoPilot ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://copilot.microsoft.com")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Google Gemini ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://gemini.google.com")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Meta Llama ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.meta.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "perplexity.ai ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="http://www.perplexity.ai")
        with g.cell():
            st_write(s.project.doc.tables.cell, "claude.ai ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://claude.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.olive_green + s.bold, "VERCEL"), "chat models comparison ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://sdk.vercel.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.project.colors.olive_green + s.bold, "together.ai"), " chat models comparison ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://api.together.xyz/playground")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "RIGHTONSKILL"), "chat models comparison", (s.project.colors.bright_red + s.bold, "Use the training CODE as \"Access Key\" "))
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://huggingface.co/spaces/university-luxembourg/llms")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.2. MNIST Digit recognition ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "MNIST Digit Recognition Online ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Main page ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://adamharley.com/nn_vis/"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "2DANN", "https://adamharley.com/nn_vis/mlp/2d.html"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "2DCNN", "https://adamharley.com/nn_vis/cnn/2d.html"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "3DANN", "https://adamharley.com/nn_vis/mlp/3d.html"), (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "3DCNN", "https://adamharley.com/nn_vis/cnn/3d.html"))
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.3. RealTime Object Detection with YOLO ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Explanations on YOLO ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.datacamp.com/blog/yolo-object-detection-explained")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Online tutorial ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://colab.research.google.com/github/ultralytics/yolov5/blob/master/tutorial.ipynb")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Android app")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell, "iPhone app")
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.4. Rock-Paper-Scissors ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://tenso.rs/demos/rock-paper-scissors/", link="https://tenso.rs/demos/rock-paper-scissors/")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.5. Teachable Machine ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://teachablemachine.withgoogle.com/train/image", link="https://teachablemachine.withgoogle.com/train/image")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.6. Image Generator", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Tool ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "deepdreamgenerator"), (s.italic, "NOTE: If you use our gmail account outside the session slot but still in the overall training time frame and if you are required a verification code then send us an email to get it. "))
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://deepdreamgenerator.com")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "crayon ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.craiyon.com/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "DALL-E ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://openai.com/index/dall-e-3/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "fotor ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.fotor.com/images/create")
        with g.cell():
            st_write(s.project.doc.tables.cell, "designer.microsoft.com ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://sdk.vercel.ai/")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "0.1.7. Find another AI", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Tool ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue, "easywithai.com", link="https://easywithai.com/")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://easywithai.com/")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.8. Music generation ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Muse net ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://soundcloud.com/openai_audio/chopin-f-minor-etude?in=openai_audio/sets/musenet&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing", link="https://soundcloud.com/openai_audio/chopin-f-minor-etude?in=openai_audio/sets/musenet&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "JukeBox ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://jukebox.openai.com/", link="https://jukebox.openai.com/")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Suno - with voice generation ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://app.suno.ai/create/", link="https://app.suno.ai/create/")
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "_", "https://app.suno.ai/song/c56ab50e-0f62-4470-8603-814b83d9b6b0"),
        (s.bold, " "),
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "_", "https://app.suno.ai/song/d91cb3a3-a40f-4cf4-9694-f0046ca3e978"),
        (s.bold, " "),
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "_", "https://suno.com/song/ec329950-1a0c-45af-bd12-b46eb7de707f"),
        (s.bold, " "),
        (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "_", "https://suno.com/song/b483407f-ec6e-4b6d-8626-be734cda0e0c"),
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "0.1.9. Speech generation ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Whisper ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://openai.com/research/whisper", link="https://openai.com/research/whisper")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.2.10. Video generation from text ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Google Veo ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://deepmind.google/models/veo/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Google Flow ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://labs.google/fx/tools/flow/unsupported-country")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Sora ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=HK6y8DAPN_0")
        with g.cell():
            st_write(s.project.doc.tables.cell, "pika.art ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=6b10jGNNbXQ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "VideoPoet ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=70wZKfx6Ylk")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Meta Movie Gen ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://ai.meta.com/research/movie-gen/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Text-to-4D paper ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://make-a-video3d.github.io/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.2.10. Multimodal AI", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "fal-ai text to videoltx / kling / ... ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://fal.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "fal-ai text to speechplaya - tts v3 / ... ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://fal.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "notebookLMchatbot services and podcast generator ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://notebooklm.google.com/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://ai.meta.com/research/movie-gen/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://make-a-video3d.github.io/")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.2.10. Local Models ", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LM Studio application ", "for LLMs ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://lmstudio.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "DrawThingsfor images ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://drawthings.ai/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://make-a-video3d.github.io/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://make-a-video3d.github.io/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://make-a-video3d.github.io/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
