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
      #274e13 -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Video Generation from text ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "\" Elon Musk in a space suit, "),
        (s.project.colors.forest_green + s.bold, "3D animation"),
        (s.project.colors.burnt_orange + s.bold, " "),
        (s.project.colors.forest_green + s.bold, "\" "),
    )
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img29.png")
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "pika.art "),
        (s.project.colors.forest_green, "(Nov. 2023)"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://pika.art/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.youtube.com/@Pika_Labs"),
        tag=t.h4,
    )
    st_space(size=4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.link_blue, "_", link="https://pika.art/")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img23.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "VideoPoet "),
        (s.project.colors.forest_green, "(Google - Dec. 2023)"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://sites.research.google/videopoet/"),
        tag=t.h4,
    )
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.youtube.com/watch?v=70wZKfx6Ylk")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Sora "),
        (s.project.colors.forest_green, "(OpenAI - Feb. 2024) "),
        tag=t.h4,
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://openai.com/sora/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://youtu.be/HK6y8DAPN_0?t=71"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://youtu.be/HK6y8DAPN_0?t=208"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.youtube.com/watch?v=HK6y8DAPN_0"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "Movie Gen "),
        (s.project.colors.forest_green, "(from Meta - Oct. 2024) "),
        tag=t.h4,
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://ai.meta.com/research/movie-gen/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.youtube.com/watch?v=FHSSx4dUs7E"),
    )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Meta AI SAM ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img28.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/1P_-BUui1W4o3Doi3VsFci-9I9PXu7v1w/view?usp=drive_link"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/1P_-BUui1W4o3Doi3VsFci-9I9PXu7v1w/view?usp=sharing"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/drive/folders/1kyV-ehaxyUJwbrJG_MkTPYI8_EOYjoPQ?usp=sharing"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://sam2.metademolab.com/demo"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.aidemos.meta.com/"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "DeepDreamGenerator ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://ai.meta.com/research/movie-gen/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img20.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "fal-ai ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.link_blue, "_", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green, "ltx-video"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://fal.ai/models/fal-ai/ltx-video"),
        tag=t.h4,
    )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_deep-learning-part-2_img19.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_agentic-ai-overview_img18.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green, "kling-video"),
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://fal.ai/models/fal-ai/kling-video/v1.6/standard/text-to-video"),
        tag=t.h4,
    )
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_deep-learning-part-2_img20.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://docs.google.com/document/d/1lHrvXi_qKY-qPPQEJtvAers3BZY4HNKmNIHQVwFtmsY/edit")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "FR ")
    st_write(s.project.pres.paragraphs.p_xl, "Un caméléon coloré, dessiné dans un style de bande dessinée, travaille frénétiquement à un bureau encombré. Il répond au téléphone avec une main, tape sur un ordinateur avec une autre, jongle avec des papiers de bureau grâce à sa queue, et passe d’une tâche à l’autre : administration, ressources humaines, support informatique. La scène est dynamique, humoristique et légèrement chaotique, montrant le caméléon comme un homme-orchestre débordé, changeant constamment de couleur et d’expression pour s’adapter à chaque mission. En arrière-plan : un petit bureau en désordre, rempli de dossiers, avec des téléphones qui sonnent et des alertes e-mail qui apparaissent partout. ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "EN")
    st_write(s.project.pres.paragraphs.p_xl, "A colorful cartoon-style chameleon working frantically at a cluttered desk. The chameleon is answering phone calls with one hand, typing on a computer with another, juggling office papers with its tail, and switching between administrative, HR, and IT support tasks. The scene should be dynamic, humorous, and slightly chaotic, showing the chameleon as an overwhelmed one-man band of office work, constantly shifting colors and expressions to adapt to each task. Background: a small, messy office full of files, phones ringing, email alerts popping up. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Google Veo 3 & Flow ", tag=t.h5)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "(May. 2025)", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img10.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/1VcZaabjrQjlxPEQSBz6rlnl2D5AAxpFC/view?usp=sharing"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://deepmind.google/models/veo/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://labs.google/flow/about"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://labs.google/flow/tv/channel/window-seat/VDZ7mcesLDYxhKR75mCm?random=true"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/open?id=1VK0xZXoKsQvxvO3UHQ3yj8YQqZ-uWEx2&usp=drive_fs"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://gemini.google.com/app/3e28713410e67aa2?utm_source=gemini&utm_medium=web&utm_campaign=gemini_veo2_lp_deeplink&hl=en"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://labs.google/fx/tools/flow/project/61cfb5f8-f75b-48ad-be3a-ab4181bde243"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=2)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img17.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://aiai.ros.lu/data/videos/promptleon.mp4"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://docs.google.com/videos/d/1EP0HJLXyp7xTNCS6zt5ZmavXDsSRWhqgLXejViR1SLA/edit?scene=id.g354c2ebc_0_2#scene=id.g354c2ebc_0_2"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "OpenAI Sora 2 ", tag=t.h5)
    st_write(s.project.pres.titles.h4 + s.project.colors.forest_green, "(Oct. 2025)", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img25.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.youtube.com/watch?v=1PaoWKvcJP0&list=PLOXw6I10VTv8scMJVOydXK4kfd2k4p-yl&index=2"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.youtube.com/playlist?list=PLOXw6I10VTv8scMJVOydXK4kfd2k4p-yl"),
    )
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Quick & Fake ? ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "aifng", link="https://drive.google.com/open?id=1XePy7YvDA7yh2g_YmwQS1LJJpYjil7qR&usp=drive_fs")
    st_space(size=3)
