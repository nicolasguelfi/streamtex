import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    ref_style = s.medium
    ref_key = s.medium + s.bold + s.project.colors.structure
    ref_authors = s.medium + s.bold
    ref_title = s.medium + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.section_title,
        "References",
        toc_lvl="1",
    )
    st_space(size=2)

    refs = [
        {
            "key": "[Bender & Koller, 2020]",
            "text": "E. M. Bender and A. Koller, "
            '"Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data," '
            "in Proc. 58th Annual Meeting of the ACL, pp. 5185-5198, 2020.",
        },
        {
            "key": "[Busch et al., 2023]",
            "text": "K. Busch, A. Rochlitzer, and D. Sola, "
            '"Just Tell Me: Prompt Engineering in Business Process Management," '
            "in Enterprise, Business-Process and Information Systems Modeling, "
            "Springer, pp. 3-11, 2023.",
        },
        {
            "key": "[Chen et al., 2023]",
            "text": "W. Chen, Y. Su, and J. Zuo, "
            '"AgentVerse: Facilitating Multi-Agent Collaboration and Exploring '
            'Emergent Behaviors," arXiv:2308.10848, 2023.',
        },
        {
            "key": "[Comanici et al., 2025]",
            "text": "G. Comanici, E. Bieber, M. Schaekermann et al., "
            '"Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, '
            'Long Context, and Next Generation Agentic Capabilities," '
            "arXiv:2507.06261, 2025.",
        },
        {
            "key": "[Drakopoulos et al., 2025]",
            "text": "P. Drakopoulos, P. Malousoudis, and N. Nousias, "
            '"Do LLMs Speak BPMN? An Evaluation of Their Process Modeling '
            'Capabilities Based on Quality Measures," 2025.',
        },
        {
            "key": "[Frege, 1892]",
            "text": 'G. Frege, "Uber Sinn und Bedeutung," '
            "Zeitschrift fur Philosophie und philosophische Kritik, "
            "vol. 100, pp. 25-50, 1892.",
        },
        {
            "key": "[Geng et al., 2023]",
            "text": "S. Geng, M. Josifoski, and M. Peyrard, "
            '"Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning," '
            "in Proc. EMNLP, pp. 10932-10952, 2023.",
        },
        {
            "key": "[Hassan et al., 2024]",
            "text": "A. E. Hassan, G. A. Oliva, and D. Lin, "
            '"Rethinking Software Engineering in the Foundation Model Era: '
            'From Task-Driven AI Copilots to Goal-Driven AI Pair Programmers," '
            "arXiv, 2024.",
        },
        {
            "key": "[OpenAI, 2025]",
            "text": '"Introducing GPT-5," OpenAI, October 2025.',
        },
        {
            "key": "[Qian et al., 2024]",
            "text": "C. Qian, W. Liu, and H. Liu, "
            '"ChatDev: Communicative Agents for Software Development," '
            "arXiv:2307.07924, 2024.",
        },
        {
            "key": "[Shin et al., 2021]",
            "text": "R. Shin, C. H. Lin, and S. Thomson, "
            '"Constrained Language Models Yield Few-Shot Semantic Parsers," '
            "arXiv:2104.08768, 2021.",
        },
        {
            "key": "[Team, 2025]",
            "text": "GLM-4.5 Team, A. Zeng, and X. Lv, "
            '"GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models," '
            "arXiv, 2025.",
        },
        {
            "key": "[Wei et al., 2023]",
            "text": "J. Wei, X. Wang, and D. Schuurmans, "
            '"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," '
            "arXiv:2201.11903, 2023.",
        },
        {
            "key": "[Wu et al., 2023]",
            "text": "Q. Wu, G. Bansal, and J. Zhang, "
            '"AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation," '
            "arXiv:2308.08155, 2023.",
        },
        {
            "key": "[Yang et al., 2025]",
            "text": "A. Yang, A. Li, and B. Yang, "
            '"Qwen3 Technical Report," arXiv:2505.09388, 2025.',
        },
    ]

    with st_list(list_type=lt.unordered, li_style=bs.ref_style) as l:
        for ref in refs:
            with l.item():
                st_write(
                    bs.ref_style,
                    (bs.ref_key, ref["key"]),
                    " ",
                    ref["text"],
                )
    st_space(size=2)
