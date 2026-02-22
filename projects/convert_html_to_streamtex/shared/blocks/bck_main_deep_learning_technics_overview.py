import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #063763 -> s.project.colors.navy_blue
      #1155cc -> s.project.colors.link_blue
      #20124d -> s.project.colors.dark_purple
      #2f5a1b -> s.project.colors.forest_green
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #660000 -> s.project.colors.deep_red
      #783e04 -> s.project.colors.burnt_orange
      #980000 -> s.project.colors.bright_red
      #b45f06 -> s.project.colors.burnt_orange
      #ff0000 -> s.project.colors.bright_red
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Main Deep Learning Technics ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "CNN"),
        (s.project.colors.burnt_orange + s.italic, "(Convolutional Neural Network) "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Recognition ", tag=t.h5)
    st_image(uri="illustration_deep-learning-part-2_img19.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "GAN (Generative Adversarial Network) ", tag=t.h4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Generation ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "(deep fake) ")
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/brief-history-of-ai")
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img18.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Stable Diffusion ", tag=t.h4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Generation ", tag=t.h5)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://erdem.pl/2023/11/step-by-step-visual-introduction-to-diffusion-models")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Transformers  ", tag=t.h4)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.dark_purple, "Generation ", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.dark_purple, "from  ....  to  .... ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Generation ", tag=t.h5)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Image Recognition / Understanding", tag=t.h5)
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green, "Protein Generation"),
        (s.italic, "(method to reliably determine a protein’s structure from its sequence of amino acids alone) "),
        tag=t.h5,
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Opens doors to faster solutions in health, food, and the environment. ")
    st_space(size=5)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, ".... ")
    st_image(uri="illustration_deep-learning-part-2_img23.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "Google DeepMind", link="https://deepmind.google/")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.deep_red + s.bold, "Understanding protein folding helps:")
        with lst.item():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "AI & Deep Learning", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Inside"),
        (s.project.colors.forest_green, " Transformers"),
        (s.project.colors.burnt_orange + s.italic, "(GPT = Generative Pre-trained Transformer) "),
        tag=t.h2,
        toc_lvl="+1",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Attention  ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "is all you need ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.youtube.com/watch?v=4Bdc55j80l8"),
        (s.project.colors.bright_red + s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://towardsdatascience.com/all-you-need-to-know-about-attention-and-transformers-in-depth-understanding-part-1-552f0b41d021#8607"),
    )
    st_space(size=5)
    st_space(size=5)
    st_space(size=5)
    st_space(size=3)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img24.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Mechanism Details ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img25.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Tokenizer ", tag=t.h4)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_space(size=2)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Visualize LLM Tokens ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://tokenvisualizer.netlify.app/")
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Encoder ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Embeddings ", tag=t.h5)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img20.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img20.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://medium.com/%40daniellefranca96/battle-of-the-top-llama-3-claude-3-gpt4-omni-gemini-1-5-pro-light-and-more-3ff560cf6b58"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "http://mparing-gpt-4o-llama-3-1-and-claude-3-5-sonnet?utm_source=chatgpt.com"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "http://anakin.ai/blog/llama-3-2-vs-gpt-4-vs-openai-o1-vs-gemini-ultra-vs-claude-3-5-which-ai-model-is-right-for-you/"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Attention ", tag=t.h5)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img22.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Interactive Visualization ", tag=t.h5)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "Paris is a city located in ... ")
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img10.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://poloclub.github.io/transformer-explainer/")
    st_space(size=3)
