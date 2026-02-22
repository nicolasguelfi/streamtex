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
      #9900ff -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h1, "7. AI Tools Competition and Rankings ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.1. competitions ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.2. Leader boards ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard", link="https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://chat.lmsys.org/?leaderboard", link="https://chat.lmsys.org/?leaderboard")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "SuperGLUE Benchmark"),
        " - An extension of the GLUE benchmark that includes more challenging tasks designed to push the limits of language models. Visit the SuperGLUE leaderboard at",
        (s.project.doc.links.link_body, " ", "https://super.gluebenchmark.com/"),
        (s.project.doc.links.link_body + s.project.colors.link_blue, "SuperGLUE Benchmark", "https://super.gluebenchmark.com/"),
        ". ",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://www.trustbit.tech/en/llm-leaderboard-maerz-2024", link="https://www.trustbit.tech/en/llm-leaderboard-maerz-2024")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://rank.opencompass.org.cn/home", link="https://rank.opencompass.org.cn/home")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://huggingface.co/spaces/DontPlanToEnd/UGI-Leaderboard", link="https://huggingface.co/spaces/DontPlanToEnd/UGI-Leaderboard")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "-> Medical Domain ")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://huggingface.co/blog/leaderboard-medicalllm", link="https://huggingface.co/blog/leaderboard-medicalllm")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.3. Kaggle data sets ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "link", link="https://www.kaggle.com/competitions?listOption=completed&sortOption=reward&participationFilter=open")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.4. Benchmarks ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "TO BE CHECKED & UPDATED ")
    st_space(size=1)
    with st_grid(cols=4, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold + s.italic, "CAT")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold + s.italic, "NAME")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold + s.italic, "DESCR")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.link_blue + s.bold + s.italic, "link")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Code Generation")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Codex HumanEval")
        with g.cell():
            st_write(s.project.doc.tables.cell, "benchmark designed to evaluate code synthesis models. It provides programming problems that the models should solve by generating correct and functional code. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://paperswithcode.com/sota/code-generation-on-humaneval")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "HumanEval")
        with g.cell():
            st_write(s.project.doc.tables.cell, "HumanEval is designed to evaluate code generation capabilities of language models. It consists of programming problems that require generating functioning code snippets. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/openai/human-eval")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Natural2Code")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This benchmark assesses a model's ability to generate code from natural language descriptions. It's designed to test how well a model can interpret human instructions and translate them into executable code. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/aixcoder-plugin/nl2code-dataset")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "General Reasoning and Understanding")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "BIG-bench Hard")
        with g.cell():
            st_write(s.project.doc.tables.cell, "BIG-bench Hard includes tasks from the broader BIG-bench benchmark that are specifically designed to be more challenging. It aims to test the abilities of large language models across tasks that require complex reasoning and detailed understanding. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/google/BIG-bench")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Quality Evaluation - Ethics")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "BBQ (Bias Benchmark for Question Answering):")
        with g.cell():
            st_write(s.project.doc.tables.cell, "measure bias in question answering systems. It evaluates how a model's answers might reflect or amplify societal biases found in its training data. The benchmark consists of question-answer pairs that are annotated to indicate potential biases, offering a structured way to assess and address bias in language models. This helps developers understand biases in model responses and work towards more equitable AI systems. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://paperswithcode.com/dataset/bbq")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "BOLD (Benchmarks for Out-of-distribution generalization in Language understanding and Dialogue)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "collection of tasks aimed at evaluating the robustness of language models to changes in distribution. It provides datasets across several natural language understanding domains (like sentiment analysis, paraphrasing, etc.) with a focus on testing how well models perform on \"out-of-distribution\" examples—scenarios that are not well-represented in the training data but are likely to be encountered in real-world applications. This benchmark is important for assessing a model's ability to generalize beyond its training constraints. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/jc-audet/WOODS")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "RealToxicityPrompts")
        with g.cell():
            st_write(s.project.doc.tables.cell, "ataset aimed at investigating the extent to which language models generate toxic content. It consists of 100K sentence-level prompts from English web text, each paired with toxicity scores. This dataset serves as a testbed for evaluating the tendency of language models to produce offensive or harmful language and the effectiveness of different methods to prevent such undesirable output. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/allenai/real-toxicity-prompts")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "ToxiGen")
        with g.cell():
            st_write(s.project.doc.tables.cell, "benchmark designed to assess the toxicity of responses generated by language models. It includes a large, diverse dataset of prompts that are specifically curated to explore different types of harmful outputs that may be produced by language models. The goal is to measure how a model generates or refrains from generating toxic text in response to both provocative and neutral prompts. This helps in understanding and mitigating undesirable behaviors in AI systems. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://paperswithcode.com/dataset/toxigen")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Quality Evaluation - Generated text")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "TruthfulQA")
        with g.cell():
            st_write(s.project.doc.tables.cell, "evaluates if language models produce truthful answers to questions. It contains 817 questions across 38 categories like health and law, designed to avoid common misconceptions. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://paperswithcode.com/dataset/truthfulqa")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning - Advanced Mathematical")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "MATH Dataset")
        with g.cell():
            st_write(s.project.doc.tables.cell, "The MATH dataset specifically tests a model's capability in mathematical reasoning, covering problems from algebra, calculus, and other areas. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/deepmind/mathematics_dataset")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning - Common Sense")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Commonsense Reasoning Benchmarks (e.g., CommonsenseQA, COPA)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "These benchmarks test a model's ability to apply commonsense knowledge to new situations. They involve answering questions or deciding between two plausible scenarios based on common sense. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.tau-nlp.org/commonsenseqa")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "WinoGrande")
        with g.cell():
            st_write(s.project.doc.tables.cell, "large-scale dataset for common sense reasoning, consisting of 44k problems. It was designed to be a more difficult version of the original Winograd Schema Challenge, with a focus on debiasing to avoid spurious correlations often exploited by machine learning models. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://paperswithcode.com/dataset/winogrande")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning - Commonsense")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "HellaSwag")
        with g.cell():
            st_write(s.project.doc.tables.cell, "HellaSwag is a commonsense reasoning dataset for evaluating a model's ability to predict endings to stories or descriptions of scenes. It emphasizes the need for models to understand nuanced, everyday situations. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://rowanzellers.com/hellaswag/")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning - Mathematical")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "GSM-8K (Grade School Math 8K)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This benchmark challenges models to solve grade-school level math problems. It tests a model's reasoning and arithmetic problem-solving abilities. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/openai/grade-school-math")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning - Science")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "AI2 Reasoning Challenge (ARC)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "designed to promote research in the area of question-answering, particularly questions that require complex reasoning and understanding of science. It tests the ability of AI systems to reason and to understand complex texts usually seen in science examinations and is considered a stringent test of AI's natural language understanding. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://allenai.org/data/arc")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Reasoning and Understanding")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "DROP (Discrete Reasoning Over Paragraphs)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This benchmark evaluates the natural language understanding and reasoning skills of a model over paragraphs. It involves answering questions that require discrete operations over the contents of a given passage, such as addition, counting, or sorting. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://allennlp.org/drop")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - Audio")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "CoVoST 2 (Common Voice ST 2)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "CoVoST 2 is a multilingual speech-to-text translation corpus. It assesses a model's capability to translate spoken words from one language to audio transcriptions in another language. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://huggingface.co/datasets/covost2")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "FLEURS")
        with g.cell():
            st_write(s.project.doc.tables.cell, "FLEURS is a benchmark for evaluating a model's performance on multilingual, few-shot language learning. It focuses on automatic speech recognition tasks. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://huggingface.co/datasets/google/fleurs")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - General Language")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "GLUE Benchmark")
        with g.cell():
            st_write(s.project.doc.tables.cell, "GLUE is a collection of nine different tasks designed to measure a model's ability to understand the English language. These tasks include question answering, sentiment analysis, and textual entailment among others. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://gluebenchmark.com/")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - Image")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "DocVQA")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Similar to TextVQA, but focused on document images. It challenges models to answer questions based on the content and layout of various types of documents. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://rrc.cvc.uab.es/?ch=17&com=evaluation&task=3")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "TextVQA")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This benchmark involves reading and answering questions about texts that appear within images, such as signs or labels. It combines OCR (Optical Character Recognition) with VQA. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://textvqa.org/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "VQAv2 (Visual Question Answering version 2)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "VQAv2 tests a model's understanding of visual content. It involves answering questions about images, requiring a model to comprehend both the text and the visual information. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://visualqa.org/")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - Multitask Language")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "MMLU (Massive Multitask Language Understanding)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This is a multitask benchmark with a large collection of tasks designed to evaluate a model's general language understanding across a broad range of subjects and question types. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/Helw150/mmlu")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - Text")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "BoolQ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "BoolQ is a question-answering dataset where the task is to answer yes/no questions. These questions are natural and originate from Google search queries, requiring comprehension of a given passage to provide a correct answer. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/google-research-datasets/boolean-questions")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "LAMBADA (LAnguage Modeling Broadened to Account for Discourse Aspects)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LAMBADA evaluates the capabilities of computational models for text understanding and prediction, specifically in the context of long-range dependencies in text. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://zenodo.org/record/2630551")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Natural Questions")
        with g.cell():
            st_write(s.project.doc.tables.cell, "real user questions from Google search queries paired with Wikipedia articles. The goal is for models to provide answers by understanding and extracting relevant information from the articles. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://ai.google.com/research/NaturalQuestions/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "RACE (Reading Comprehension Dataset From Examinations)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "RACE is a large-scale reading comprehension dataset that comes from English exams for middle and high school Chinese students. It consists primarily of MCQs and is designed to assess the comprehension ability of language models by requiring them to choose the correct answer from several options after understanding a given passage. This makes it a highly relevant benchmark for testing MCQ handling ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://huggingface.co/datasets/ehovy/race")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "SQuAD (Stanford Question Answering Dataset)")
        with g.cell():
            st_write(s.project.doc.tables.cell, "SQuAD is a benchmark focused on question answering based on a given passage of text. It tests a model's ability to parse and understand detailed narratives and then answer questions about them. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://rajpurkar.github.io/SQuAD-explorer/")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "SuperGLUE Benchmark")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Building on GLUE, SuperGLUE includes more challenging tasks and is designed to push the capabilities of language understanding systems further. It includes tasks like question answering under more complex scenarios and requires deeper language understanding. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://super.gluebenchmark.com/")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.purple + s.bold, "Understanding - Video")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "Perception Test MCQA")
        with g.cell():
            st_write(s.project.doc.tables.cell, "This benchmark involves multiple-choice questions that test a model's understanding of video content. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://multimediaeval.github.io/editions/2020/tasks/mc")
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.doc.tables.cell + s.bold, "VATEX")
        with g.cell():
            st_write(s.project.doc.tables.cell, "VATEX is a large-scale, high-quality multilingual dataset for video captioning. The task is to generate descriptive captions for videos, which requires understanding and synthesizing visual and audio content. ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://eric-xw.github.io/vatex-website/")
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
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
