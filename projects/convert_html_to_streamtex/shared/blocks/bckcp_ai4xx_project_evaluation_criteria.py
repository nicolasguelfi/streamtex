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
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "7. Evaluation Criteria ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.1. Symbolic Aspects (FORM) ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Length"),
                (s.italic, "Definition:"),
                " The length of the presentation should be appropriate—not too long or too short.",
                (s.italic, "Advice:"),
                " Keep your presentation concise and to the point. Aim to cover each topic adequately without digressing. Stick to the recommended time or slide count, and avoid unnecessary filler content. Practicing beforehand can help you stay within the expected length and maintain a steady pace. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Structured"),
                (s.italic, "Definition:"),
                " The presentation should have a logical structure, with a clear beginning,  middle, and end.",
                (s.italic, "Advice:"),
                " Organize your slides logically. Start with a strong introduction that outlines your topic, followed by well-structured sections that flow naturally from one idea to the next, and end with a conclusion that summarizes key points. Using headings, bullet points, and a consistent layout across slides can improve readability and help your audience follow your argument. Use hierarchy and modularity. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Diagrams/Figures"),
                (s.italic, "Definition:"),
                " Use diagrams, charts, and figures to visually represent key ideas and data.",
                (s.italic, "Advice:"),
                " Choose visuals that enhance understanding. Diagrams should clarify complex ideas, and charts should simplify data interpretation. Avoid cluttering slides with too many visuals or overly detailed images; instead, select visuals that directly support the points you're making. Ensure images are high-quality and easy to read. ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.2. Semantics Aspects (SEM) ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "State of the Art (SOTA)"),
                (s.italic, "Definition:"),
                " The presentation should include the latest developments, research, or innovations relevant to the topic.",
                (s.italic, "Advice:"),
                " Conduct a literature review or research to find recent studies, trends, or breakthroughs in your field. Mention these developments to show that you understand the current state of knowledge. Cite (using the ",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "APA standard", "https://apastyle.apa.org/"),
                ") relevant sources and highlight how recent advancements relate to your topic. This will demonstrate depth and currency in your understanding. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Correctness"),
                (s.italic, "Definition:"),
                " The information presented should be accurate and factually correct.",
                (s.italic, "Advice:"),
                " Double-check all facts, figures, and data. Use reliable sources, and verify any statements or claims you make. Avoid overgeneralizations or unsupported assumptions. Accuracy is critical, as even a minor error can undermine your credibility. Make sure you understand each point fully before including it in your presentation. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Complexity"),
                (s.italic, "Definition:"),
                " The presentation should reflect an appropriate level of intellectual complexity, showing a mastery of the subject matter.",
                (s.italic, "Advice:"),
                " Dive deep into the subject matter. Don’t shy away from discussing complex ideas, as long as they are explained clearly. Use technical terms where appropriate and offer a thorough analysis, rather than a surface-level overview. Aim to strike a balance: your content should be challenging enough for a Master's level without being overly technical or obscure. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Usefulness"),
                (s.italic, "Definition:"),
                " The information presented should be relevant and useful to the claimed goals of your work and to the audience.",
                (s.italic, "Advice:"),
                " Clearly identify the goals of your presentation and ensure that each piece of information aligns with these objectives. Consider what your audience hopes to gain from your presentation, and prioritize content that offers practical insights, theoretical applications, or actionable conclusions. This alignment will make your presentation more engaging and valuable, demonstrating its relevance to both the topic and the audience’s interests. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "GenAI"),
                (s.italic, "Definition:"),
                " The report should document the usage and understanding of Generative AI.",
                (s.italic, "Advice:"),
                " Describe clearly how Generative AI contributed to your project, detailing the tools, models, or techniques used and why they were chosen. Explain the impact of GenAI on your project outcomes and provide examples to illustrate your approach. This section should highlight both your practical use of Generative AI and your grasp of its potential and limitations, showing that you leveraged it thoughtfully and effectively to meet project goals. ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.3. Presentation Criteria and Weights ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "FORM ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "SEM ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.4. Report Criteria and Weights ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "FORM ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "SEM")
        with lst.item():
            pass
    st_space(size=1)
    st_space(size=1)
