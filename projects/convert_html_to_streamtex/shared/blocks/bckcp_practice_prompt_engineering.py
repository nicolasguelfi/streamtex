import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0000ff -> s.project.colors.link_blue
      #1155cc -> s.project.colors.link_blue
      #37761c -> s.project.colors.olive_green
      #666666 -> s.project.colors.gray
      #674ea7 -> s.project.colors.purple
      #a61b00 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "1. Mini Workshop on Prompt Engineering", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.1. EN - AI Generated Illustrations", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "1.1.1. Prompt Engineering Techniques Illustrations", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.1.1.1. High level categories", tag=t.h4)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.salmon + s.bold + s.italic, "CAT")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.olive_green + s.bold + s.italic, "SCAT")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "EN")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Improvement Techniques")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Clarity and Focus")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/635da8f1-d5cc-459e-b406-9eb9fdb635ac")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Context and Explanation")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/f7994f1a-2cc6-4042-ba01-fac738c3f28f")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Creativity and Engagement")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/f3b14fdd-5a1a-4777-ade4-209866e5ec30")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Ethical and Bias Considerations")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/0416b4dc-e44a-41cf-a78a-2797cc0a75a3")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Instructional and Methodological")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/32b0a0b0-f9c8-42e9-a75b-015f69bbe0b6")
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "1.1.1.2. Specific techniques", tag=t.h4)
    st_space(size=1)
    with st_grid(cols=4, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.salmon + s.bold + s.italic, "CAT")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.olive_green + s.bold + s.italic, "SCAT")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "EN")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "details")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Clarity and Focus")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Ambiguity/Implicity Reduction")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/1dde13a2-24a2-4c90-b656-24882755a9cd")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Avoiding terms that have too many meanings in the context and add explicit content to reduce implicity.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Defining Objectives")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/762c432d-2485-41c7-982b-98065715ccdb")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Clearly stating the goal or desired outcome of the prompt.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Direct Questions")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/21b35d16-726d-4bd9-bd96-0ecc87f3f5cd")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Framing the prompt as a question to guide the AI towards a specific type of response.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Keyword Emphasis")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/a2c6fcd3-aecc-4c9c-9c91-a21304ab781b")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Using specific keywords or phrases that are central to the prompt's intent.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Precision and Clarity")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/3b6a3fb2-f60d-4d42-aecf-0be7127e0aaf")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Ensuring that the prompt is specific and unambiguous.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Use of Constraints")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/6ded5738-19a3-4ab4-9283-e37681e95851")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Setting specific limits or parameters within the prompt to guide the AI's response.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Creativity and Engagement")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Analogies and Metaphors")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/4c0985cb-23c8-44cb-ba39-506f872e9593")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Using comparative language to explain or explore concepts in a creative and relative way.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Creativity")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/746a7863-af5f-4492-9314-4820dc559822")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Encouraging imaginative or unconventional responses.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Open-ended")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/de272e5e-f669-4504-b6df-a45c8cf6411c")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Encouraging broad, imaginative responses by asking questions without a specific right answer.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Role Play")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/e7c02130-7661-4140-9183-1ffc37965c5f")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Asking the AI to assume a certain role or perspective when responding.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Scenario Completion")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/cf8d72be-6891-4c21-afb2-61ebabcb42f4")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Creating detailed scenarios for the AI to explore or respond to.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Ethical and Bias Considerations")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Bias Avoidance")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/63ad8bd6-e17a-4b5c-8b62-2319796315ea")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Making an effort to eliminate or reduce biases in AI responses.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Diversity Emphasis")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/16e3c318-5d52-4d22-989a-6a1473c77c31")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Ensuring the inclusion of diverse perspectives and avoiding stereotypes.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Ethical Value Alignment")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/e1ca5890-99e4-4c05-99ca-7a2b00fc268f")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Aligning the AI's responses with ethical guidelines or societal values.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Instructional and Methodological")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Benchmarking")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/f49a77b4-cabc-48ba-ad5a-2465bba55e13")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Assessing the AI's capabilities or progress.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Example Size (Few-shot, One-shot, Zero-shot)")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/d5e020fc-d7b8-4a38-933b-e53e4020ceb1")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Refers to how many examples are provided for the AI to learn from or base its response on.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Explicit Instructions")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/92f16c3d-ad89-47e9-92a7-166dfa793bc2")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Directly stating what actions the AI should do or focus on.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Feedback Loop")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/93353657-48b8-4af9-8556-13a5c1346055")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Involving a process where the AI's responses are evaluated and used to refine subsequent prompts.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Guided Discovery")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/02620021-19b3-4f8b-8d66-c10ec3ea5d14")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Leading the AI towards a conclusion or discovery through a series of prompts.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Progressive Detailing")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/2565dcdd-589a-4c15-a54f-7879bd399d78")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Gradually adding more details to the prompt over multiple interactions to refine the response.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Use of Response Templates")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/c/fbbfef14-3220-4f80-8116-e60d3f326f5d")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Providing a structure or format for the AI's response.")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.2. FR - AI Generated Illustrations", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "1.2.1. Prompt Engineering Techniques Illustrations", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.1.1. High level categories", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.salmon + s.bold + s.italic, "CATFR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.olive_green + s.bold + s.italic, "SCATFR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "FR")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Techniques d'amélioration")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Clarté et concentration")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Considérations éthiques et de biais")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Contexte et explication")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Créativité et engagement")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Pédagogique et méthodologique")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h5 + s.project.colors.gray, "1.2.1.1.1. Specific techniques ", tag=t.h5)
    st_space(size=1)
    with st_grid(cols=4, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.salmon + s.bold + s.italic, "CATFR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.olive_green + s.bold + s.italic, "SCATFR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "linFR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "detailsFR")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Clarté et concentration")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Accentuation des Mots-clés")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/3432da91-9862-4652-bd7e-0a1fa4da08b0")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Utiliser des mots clés ou des phrases spécifiques qui sont au cœur de l'intention de l'invite.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Définir les objectifs")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/5201f347-2dff-47ec-a14b-6754e06e8d0b")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Indiquer clairement l'objectif ou le résultat souhaité de l'invite.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Précision et clarté")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/95130fe2-18ad-4583-827c-acab41366852")
        with g.cell():
            st_write(s.project.doc.tables.cell, "S'assurer que l'invite est spécifique et sans ambiguïté.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Questions directes")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/06f6dd4c-8c41-4447-b94a-e8dad97f4a4d")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Former l'invite sous forme de question pour guider l'IA vers un type de réponse spécifique.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Réduction de l'ambiguïté/de l'implicite")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/09e571e1-70a7-4032-a498-505288ef322f")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Éviter les termes qui ont trop de significations dans le contexte et ajouter un contenu explicite pour réduire l'implicite.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Utilisation de contraintes")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/4c1c5767-03b7-489b-9cec-2defc290e6ed")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Définition de limites ou de paramètres spécifiques dans l'invite pour guider la réponse de l'IA.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Considérations éthiques et biaisées")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Accentuation de la diversité")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/fc9c9057-2e7d-4973-b946-f194c0b6aa1f")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Assurer l'inclusion de perspectives diverses et évitant les stéréotypes.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Alignement des valeurs éthiques")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/09c19ccf-32c4-48ff-81a7-1d3dbbfb47ef")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Aligner les réponses de l'IA sur les directives éthiques ou les valeurs sociétales.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Contournement des déséquilibres et biais du modèle")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/fe1336ad-27c6-45af-968c-549f1f8eb983")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Faire un effort pour éliminer ou réduire les biais dans les réponses de l'IA.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Créativité et engagement")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Analogies et métaphores")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/593446dd-c46d-4223-a026-c191acb1efcd")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Utiliser un langage comparatif pour expliquer ou explorer des concepts de manière créative et relative.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Jeu de rôle")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/ba630ce2-89ce-4457-bbdb-32e5a17c6ffb")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Demander à l'IA d'assumer un certain rôle ou une certaine perspective lors de la réponse.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "La créativité")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/2f057914-e03b-4227-b56c-616c3f678102")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Encourager les réponses imaginatives ou non conventionnelles.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Ouverture vers des possibles")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/b4007b93-39eb-4fb5-a370-f0d2a48c9528")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Encourager les réponses larges et imaginatives en posant des questions qui n'aient pas qu'une seule bonne réponse spécifique.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Poursuite de scénario")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/0c604643-4157-4964-8eab-f51c1812e476")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Créer des scénarios détaillés pour que l'IA les explore ou y réponde.")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.salmon + s.bold, "Pédagogique et méthodologique")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Comparaison à une alternative")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/c85fec77-2ed1-479d-a462-842dea205738")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Évaluer les capacités ou les progrès de l'IA.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Découverte guidée")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/25a3a152-db18-47b1-8027-c4bb47028788")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Mener l’IA vers une conclusion ou une découverte à travers une série d’invites.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Détails progressifs")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/297de5fb-580d-4572-9991-3d2f89c36672")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Ajouter progressivement plus de détails à l'invite sur plusieurs interactions pour affiner la réponse.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Instructions explicites")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/1192159d-94ea-4c1e-8a00-ecd886511207")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Indiquer directement les actions que l'IA doit faire ou sur lesquelles se concentrer.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Nombre d'exemples (quelques-uns, un, zéro)")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/603792cf-9f54-436b-ac5b-21e35400b80d")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Faire référence au nombre d'exemples fournis à l'IA pour apprendre ou à baser sa réponse.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Retour d'appréciation sur le résultat fourni")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/39f73da4-4ae9-4c0e-8d35-2ecef7211fbc")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Impliquer un processus où les réponses de l'IA sont évaluées et utilisées pour affiner les invites ultérieures.")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.olive_green + s.bold, "Utilisation de formats de réponse")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://chat.openai.com/share/df35925e-6b4b-499e-928d-0b6744d42dbe")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Fournir une structure ou un format pour la réponse de l'IA.")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.3. References", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "General references", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Prompt Engineering Guide with extensive resources ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.promptingguide.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Brex's Prompt Engineering Guide ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/brexhq/prompt-engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Hallucinations with LLMs (WIKIPEDIA) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "Case studies references", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "We Tried To Buy A $1 Ford Bronco From AI Chatbots. It Didn't Work ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.motor1.com/news/701402/ford-bronco-chat-bot/")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=1)
    st_space(size=1)
