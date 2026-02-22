import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h1, "2. ChatBot Qualities", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.1. Summary", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=3, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "Expertise & Credibility ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "Communication & Clarity ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "Creativity & Innovation ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Personality & Style ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Empathy & Emotional Approach ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Pedagogical Approach ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Organization & Consistency ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Ethics & Values ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Accessibility & Cultural Openness ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.2. Communication & Clarity ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Clarity of Expression"),
                ": Ability to convey explanations or advice in a way that is easily understood. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Precision"),
                ": Use of precise, unambiguous language. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Simplicity of Language"),
                ": Ability to simplify and use accessible vocabulary. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Adaptability in Communication"),
                ": Adjusting formality (more or less technical, more or less formal) based on the user. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Skill in Summarization"),
                ": Knowing how to condense essential information. ",
            )
    st_write(s.project.doc.titles.h2, "2.3. Empathy & Emotional Approach ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Active Listening"),
                ": Rewording, asking relevant questions, showing understanding. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Sensitivity to Emotions"),
                ": Identifying positive or negative feelings and responding accordingly. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Kindness"),
                ": Using a friendly, reassuring, and non-judgmental tone. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Patience"),
                ": Dealing with user frustration or misunderstanding calmly. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Motivation & Encouragement"),
                ": Providing positive feedback and spurring the desire to improve. ",
            )
    st_write(s.project.doc.titles.h2, "2.4. Expertise & Credibility ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Specialized Knowledge"),
                ": Mastery of a specific field (finance, cooking, travel, etc.). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Multi-Expertise"),
                ": Ability to combine or switch between different domains. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Reliability of Information"),
                ": Basing responses on recognized facts, sources, or methods. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Clarity About Limitations"),
                ": Admitting when a question falls outside the chatbot’s scope. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Up-to-Date Knowledge"),
                ": Demonstrating current understanding, avoiding outdated advice. ",
            )
    st_write(s.project.doc.titles.h2, "2.5. Pedagogical (Teaching) Approach ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Progressive Steps"),
                ": Suggesting simple stages to move forward gradually. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Concrete Examples"),
                ": Providing illustrations, practical cases, or metaphors. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Problem-Solving Explanation"),
                ": Describing the logic that leads to a solution, not just stating the final answer. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Interactive Method"),
                ": Asking the user questions to gauge understanding. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Stimulating Curiosity"),
                ": Encouraging the user to ask more questions and delve deeper. ",
            )
    st_write(s.project.doc.titles.h2, "2.6. Personality & Style ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Warm / Friendly"),
                ": Adopting a welcoming, familiar tone. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Professional / Serious"),
                ": Maintaining a more formal and rigorous manner. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Humorous"),
                ": Adding small notes of humor or mild wit (without overdoing it). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Motivational / Inspiring"),
                ": Emphasizing the user’s potential, helping them surpass themselves. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Neutral / Sober"),
                ": Minimalistic and factual style without emotional emphasis. ",
            )
    st_write(s.project.doc.titles.h2, "2.7. Accessibility & Cultural Openness ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Diversity Awareness"),
                ": Not assuming a single user profile (age, gender, culture). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Inclusive Language"),
                ": Using open-ended phrasing, respectful of cultural sensitivities. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Simplicity of References"),
                ": Avoiding private jokes or country-specific references (unless relevant). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Clarity Regarding Language Barriers"),
                ": Providing vocabulary or paraphrasing if a term may be complex. ",
            )
    st_write(s.project.doc.titles.h2, "2.8. Creativity & Innovation ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Original Ideas"),
                ": Ability to think outside the box and offer innovative solutions. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Adaptability to New Situations"),
                ": Flexibility when questions or scenarios are “out of the box.” ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Openness to Exploration"),
                ": Encouraging the user to experiment, not confining them to a single option. ",
            )
    st_write(s.project.doc.titles.h2, "2.9. Ethics & Values ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Integrity"),
                ": Being transparent about sources and intentions (no manipulation). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Respect for Privacy"),
                ": Avoiding requests for unnecessary personal information. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Responsibility"),
                ": Awareness of the impact of certain advice (e.g., on the environment, on health). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Neutrality / Impartiality"),
                ": Not favoring a product, brand, or opinion without clear justification. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Safety & Precaution"),
                ": Reminding users of basic warnings (e.g., nutrition, DIY, finance). ",
            )
    st_write(s.project.doc.titles.h2, "2.10. Organization & Consistency ", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Methodical Approach"),
                ": Following a logical plan, a clear progression in conversation. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Structured Responses"),
                ": Using hierarchy (lists, bullet points, numbered steps). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Overall Consistency"),
                ": Maintaining the same guiding line (tone, style, vocabulary). ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Time Management"),
                ": Avoiding information overload that overwhelms the user. ",
            )
    st_space(size=1)
    st_space(size=1)
