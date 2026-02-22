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
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Using & Improving LLM", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Approaches", tag=t.h3)
    st_space(size=3)
    with st_list(list_type=lt.ordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, " Prompt Engineering")
        with lst.item():
            st_write(s.project.colors.olive_green + s.bold, " Retrieval-Augmented Generation")
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, " Fine Tuning")
        with lst.item():
            st_write(s.project.colors.salmon + s.bold, " Domain-Specific Language Model ")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Choose based on ", tag=t.h4)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.olive_green, "Effective Results Quality / Needs ")
        with lst.item():
            st_write(s.project.colors.olive_green, "Generalization vs. Specialization")
        with lst.item():
            st_write(s.project.colors.bright_red, "Domain Specificity ")
        with lst.item():
            st_write(s.project.colors.bright_red, "Dataset Quality and Size")
        with lst.item():
            st_write(s.project.colors.salmon, "Resource Availability ")
        with lst.item():
            st_write(s.project.colors.salmon, "Development Time ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green, "Prompt"),
        (s.project.colors.link_blue, " Engineering& "),
        (s.project.colors.burnt_orange, "Persona"),
        (s.project.colors.link_blue, " Engineering "),
        tag=t.h3,
    )
    st_space(size=3)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Clarity and Focus", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Ambiguity/Implicity Reduction")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Avoiding terms that have too many meanings in the context and add explicit content to reduce implicity.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Defining Objectives")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Clearly stating the goal or desired outcome of the prompt.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Direct Questions")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Framing the prompt as a question to guide the AI towards a specific type of response.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Keyword Emphasis")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Using specific keywords or phrases that are central to the prompt's intent.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Precision and Clarity")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Ensuring that the prompt is specific and unambiguous.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Use of Constraints")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Setting specific limits or parameters within the prompt to guide the AI's response.")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Context and Explanation ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Chain of Thought (CoT)")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Instructs the model to explain its reasoning step-by-step, leading to more logical and accurate conclusions.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Domain & History")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Provides the AI with a specific role, expertise, or background context to tailor its response style and accuracy.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Illustrations")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Uses examples, scenarios, or analogies within the prompt to clearly demonstrate the desired output format or logic.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Iterative Incremental Prompts")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Involves refining the output through a sequence of follow-up prompts, gradually adding detail or constraints.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Problem Decomposition")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Breaks a complex task into smaller, manageable sub-components to be solved individually for better overall results.")
    st_space(size=2)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Creativity and Engagement ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Analogies and Metaphors")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Using comparative language to explain or explore concepts in a creative and relative way.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Creativity")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Encouraging imaginative or unconventional responses.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Open-ended")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Encouraging broad, imaginative responses by asking questions without a specific right answer.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Role Play")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Asking the AI to assume a certain role or perspective when responding.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Scenario Completion")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Creating detailed scenarios for the AI to explore or respond to.")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Instructional and Methodological ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Benchmarking")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Assessing the AI's capabilities or progress.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Example Size (Few-shot, One-shot, Zero-shot)")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Refers to how many examples are provided for the AI to learn from or base its response on.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Explicit Instructions")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Directly stating what actions the AI should do or focus on.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Feedback Loop")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Involving a process where the AI's responses are evaluated and used to refine subsequent prompts.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Guided Discovery")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Leading the AI towards a conclusion or discovery through a series of prompts.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Progressive Detailing")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Gradually adding more details to the prompt over multiple interactions to refine the response.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Use of Response Templates")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Providing a structure or format for the AI's response.")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Ethical and Bias Considerations", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Bias Avoidance")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Making an effort to eliminate or reduce biases in AI responses.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Diversity Emphasis")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Ensuring the inclusion of diverse perspectives and avoiding stereotypes.")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "Ethical Value Alignment")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.purple, "Aligning the AI's responses with ethical guidelines or societal values.")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.olive_green + s.bold, "Prompt"),
        (s.project.colors.dark_purple + s.bold, " & "),
        (s.project.colors.burnt_orange + s.bold, "Persona"),
        (s.project.colors.dark_purple + s.bold, " Agents"),
    )
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.olive_green + s.bold, "Prompt ")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.burnt_orange + s.bold, "Persona ")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Impact PE on (med)MMLU ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl, "Measuring Massive Multitask Language Understanding ")
    st_write(s.project.pres.paragraphs.p_lg + s.italic, "Ks of Challenge problems MCQs across 57 areas from basic mathematics to United States history, law, computer science, engineering, medicine ... ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.microsoft.com/en-us/research/blog/steering-at-the-frontier-extending-the-power-of-prompting/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://github.com/microsoft/promptbase"),
    )
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_space(size=1)
    st_space(size=1)
