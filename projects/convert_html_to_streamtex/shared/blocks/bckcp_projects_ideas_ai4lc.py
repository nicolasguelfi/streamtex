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
      #434343 -> s.project.colors.gray
      #666666 -> s.project.colors.gray
      #783e04 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    Dropped colors:
      #222222
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "6. Projects ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.burnt_orange + s.bold, "TO BE ADDED DURING THE SESSION ")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.bright_red + s.bold, "Projects presentation slides available "),
        (s.project.doc.links.link_md + s.project.colors.link_blue + s.bold, "HERE", "https://docs.google.com/document/d/1k_6ncSl1WvEvq-AuhBEweopoqrt9uMPTgrFc8HMDsw8/edit"),
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.1. Projects Overview", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Linguistic Quality and Generative AI (GenAI) ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("What is the linguistic quality of generative AI?")
        with lst.item():
            st_write("How do existing GenAI models compare in linguistic writing?")
        with lst.item():
            st_write("How do existing GenAI models compare in cultural diversity writing?")
        with lst.item():
            st_write("How to generate or detect GenAI fake data?")
        with lst.item():
            st_write("How Effective is Named Entity Recognition (NER) for Identifying Cultural and Linguistic Entities Across Languages?")
        with lst.item():
            st_write("How Can AI Assist Journalists in Content Creation and Reporting?")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Education sector ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Can AI Enhance Personalized and Accessible Language Learning in Multilingual Classrooms?")
        with lst.item():
            st_write("How Can AI Assist in Creating Culturally Relevant Educational Materials?")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Cultural and Linguistic Bias Detection ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Does Language Diversity Bias Affect Multilingual Information Access?")
        with lst.item():
            st_write("What Cultural Biases Exist in AI-Powered Translation Tools, and How Do They Impact Cross-Cultural Communication?")
        with lst.item():
            st_write("Does Generative AI Exhibit Gender Bias When Processing Gendered Languages?")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI for Cross-Cultural Communication and Understanding ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Can AI Facilitate Cross-Cultural Understanding in Multilingual Settings?")
        with lst.item():
            st_write("How Do AI-Powered Language Models Handle Humor, Sarcasm, and Other Culturally Specific Expressions Across Languages?")
        with lst.item():
            st_write("How Can AI Assist in Creating Multilingual Glossaries for Academic and Technical Terminology?")
        with lst.item():
            st_write("How Do AI-Powered Translation Tools Affect Correctness in Cross-Cultural Communication?")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI for Language Preservation and Cultural Heritage ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("What Impact Does AI Have on Language Preservation?")
        with lst.item():
            st_write("Can AI Support Cultural Heritage Preservation?")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Multilingual User Interaction ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Can AI-Driven Sentiment Analysis Improve Multilingual Social Media Engagement?")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.2. Project ideas ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.1. What is the Linguistic Quality of Generative AI? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.1.1. Objective  ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Evaluate the linguistic proficiency of generative AI models, focusing on grammar, fluency, coherence, and style across different languages. Assess how these models handle linguistic features like syntax, morphology, and vocabulary, and how they perform in generating text that is contextually and culturally appropriate.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.1.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Linguistic Quality Analysis in Generative AI Output ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GAMBETTA, Daniele, GEZICI, Gizem, GIANNOTTI, Fosca, ",
                (s.italic, "et al."),
                " A linguistic analysis of undesirable outcomes in the era of generative AI. ",
                (s.italic, "arXiv preprint arXiv:2410.12341"),
                ", 2024. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Multilingual and Cross-Lingual Capabilities in Generative AI Models ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://arxiv.org/html/2406.16135v1", link="https://arxiv.org/html/2406.16135v1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cultural and Stylistic Adaptation in Generative AI ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S0268401224000720", link="https://www.sciencedirect.com/science/article/pii/S0268401224000720")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.1.3. Suggested Steps  ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Each student selects one article related to linguistic quality in AI, focusing on a specific feature (e.g., grammar, coherence, or cultural style). Analyze how these aspects affect generative text quality in multilingual settings.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Model Selection"),
                ": Identify the AI models to evaluate, such as GPT-4, GPT-3, BERT, or other generative models, ensuring they cover multiple languages with different linguistic structures (e.g., English, Chinese, Arabic, Hindi, etc.).",
            )
        with lst.item():
            st_write(s.bold, "Focused Evaluation Tasks: ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Group Comparison and Integration:"),
                " After conducting individual evaluations, discuss as a group to integrate insights from each student’s findings. Compare results across the two languages to identify patterns in model performance and linguistic quality.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.2. How do existing GenAI models compare in linguistic writing? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.2.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Compare the linguistic writing capabilities of various generative AI models (e.g., GPT, Llama, BERT) by assessing their grammar, fluency, coherence, and style across different languages. This project will evaluate how well these models perform in generating linguistically accurate and contextually appropriate text.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.2.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Linguistic Quality of Generative AI Models  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GAMBETTA, Daniele, GEZICI, Gizem, GIANNOTTI, Fosca, ",
                (s.italic, "et al."),
                " A linguistic analysis of undesirable outcomes in the era of generative AI. ",
                (s.italic, "arXiv preprint arXiv:2410.12341"),
                ", 2024. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cross-Model Evaluation of AI in Language Generation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHANG, Yupeng, WANG, Xu, WANG, Jindong, ",
                (s.italic, "et al."),
                " A survey on evaluation of large language models. ",
                (s.italic, "ACM Transactions on Intelligent Systems and Technology"),
                ", 2024, vol. 15, no 3, p. 1-45. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "IORLIAM, Aamo et INGIO, Joseph Abunimye. A comparative analysis of generative artificial intelligence tools for natural language processing. ",
                (s.italic, "Journal of Computing Theories and Applications ISSN"),
                ", 2024, vol. 3024, p. 9104. ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.2.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Each student chooses one article related to model evaluation in AI, focusing on aspects like grammar, fluency, or contextual relevance. Analyze how these features impact language quality.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Model Selection"),
                ": Select 2-3 generative AI models (e.g., GTP-4, BERT, Llama) and focus and the linguistic quality of generated text in that language.  ",
            )
        with lst.item():
            st_write(s.bold, "Focused Linguistic Evaluation ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Group Comparison and Integration:"),
                " After conducting individual evaluations, discuss as a group to integrate insights from each student’s findings. Compare results across the two languages to identify patterns in model performance and linguistic quality.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.3. How do existing GenAI models compare in cultural diversity writing? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.3.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "To evaluate how well generative AI models (e.g., GPT-4, Llama, BERT) represent cultural diversity in their outputs. This project will assess the extent to which these models can generate culturally sensitive, contextually appropriate, and diverse perspectives across different topics. ")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.3.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cultural Representation in AI-Generated Text ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.mdpi.com/2571-9408/7/3/70", link="https://www.mdpi.com/2571-9408/7/3/70")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Bias and Diversity in Language Models ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TAO, Yan, VIBERG, Olga, BAKER, Ryan S., ",
                (s.italic, "et al."),
                " Cultural bias and cultural alignment of large language models. ",
                (s.italic, "PNAS nexus"),
                ", 2024, vol. 3, no 9, p. pgae346. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cross-cultural sensitivity in AI ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/377030161_Leveraging_Generative_AI_for_Cross-Cultural_Knowledge_Exchange_in_Higher_Education", link="https://www.researchgate.net/publication/377030161_Leveraging_Generative_AI_for_Cross-Cultural_Knowledge_Exchange_in_Higher_Education")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.3.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review"),
                ": Each student selects an article focusing on cultural diversity or bias in AI. Analyze how these studies define and measure cultural sensitivity in AI-generated text.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Model Selection"),
                ": Choose two to three generative AI models for analysis, such as GPT-4, Llama, or BERT, ensuring they are widely used and well-documented.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Prompt Development and Testing"),
                ": ",
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Group Comparison and Integration:"),
                " After conducting individual evaluations, discuss as a group to integrate insights from each student’s findings. Compare results across the two languages to identify patterns in model performance and linguistic quality.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.4. How to Generate or Detect GenAI Fake Data? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.4.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate the mechanisms behind generating and detecting fake data produced by generative AI models, focusing on text generation and the implications for various fields, including education, journalism, and social media.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Case Studies/Examples ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "OpenAI's ChatGPT"),
                ": Studies have demonstrated how ChatGPT can generate convincing but potentially misleading or entirely fabricated information. This capability poses challenges in determining the authenticity of information produced by AI.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Fake News Detection"),
                ": Platforms like Snopes and FactCheck.org utilize AI to identify misleading content. Research highlights how these systems analyze linguistic patterns, source credibility, and metadata to flag potentially false information. This illustrates practical applications of detecting AI-generated fake data.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Generative Adversarial Networks (GANs)"),
                ": GANs have been widely used to generate synthetic data that can closely resemble real-world data. Research illustrates how GANs can produce realistic images, text, and other data forms, raising concerns about the potential for misuse in creating fake information.",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.4.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Fake News Detection Techniques ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DWIVEDI, Sanjeev M. et WANKHADE, Sunil B. Survey on fake news detection techniques. In : ",
                (s.italic, "Image Processing and Capsule Networks: ICIPCN 2020"),
                ". Springer International Publishing, 2021. p. 342-348. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "HIRIYANNAIAH, Srinidhi, SRINIVAS, A. M. D., SHETTY, Gagan K., ",
                (s.italic, "et al."),
                " A computationally intelligent agent for detecting fake news using generative adversarial networks. In : ",
                (s.italic, "Hybrid Computational Intelligence"),
                ". Academic Press, 2020. p. 69-96. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CARAMANCION, Kevin Matthe. Harnessing the power of ChatGPT to decimate mis/disinformation: Using ChatGPT for fake news detection. In : ",
                (s.italic, "2023 IEEE World AI IoT Congress (AIIoT)"),
                ". IEEE, 2023. p. 0042-0046. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Threat of Deepfakes and AI-Generated Content ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOTHA, Johnny et PIETERSE, Heloise. Fake news and deepfakes: A dangerous threat for 21st century information security. In : ",
                (s.italic, "ICCWS 2020 15th International Conference on Cyber Warfare and Security. Academic Conferences and publishing limited"),
                ". 2020. p. 57. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SHARMA, Mridul et KAUR, Mandeep. A review of Deepfake technology: an emerging AI threat. ",
                (s.italic, "Soft Computing for Security Applications: Proceedings of ICSCS 2021"),
                ", 2022, p. 605-619. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Generative AI’s Impact on Fake news ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LOTH, Alexander, KAPPES, Martin, et PAHL, Marc-Oliver. Blessing or curse? A survey on the Impact of Generative AI on Fake News. ",
                (s.italic, "arXiv preprint arXiv:2404.03021"),
                ", 2024. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LO, Chung Kwan. What is the impact of ChatGPT on education? A rapid review of the literature. ",
                (s.italic, "Education Sciences"),
                ", 2023, vol. 13, no 4, p. 410. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Generative Adversarial Networks (GANs) and Data Generation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GOODFELLOW, Ian, POUGET-ABADIE, Jean, MIRZA, Mehdi, ",
                (s.italic, "et al."),
                " Generative adversarial networks. ",
                (s.italic, "Communications of the ACM"),
                ", 2020, vol. 63, no 11, p. 139-144. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "WHITTAKER, Lucas, KIETZMANN, Tim C., KIETZMANN, Jan, ",
                (s.italic, "et al."),
                " “All around me are synthetic faces”: the mad world of AI-generated media. ",
                (s.italic, "IT Professional"),
                ", 2020, vol. 22, no 5, p. 90-99. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.4.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Each student selects one article about generating or detecting AI-generated fake data. Focus on current challenges and techniques in detecting fake text.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study: "),
                "Choose one case studies (ChatGPT, fake news detection, or GANs) and examine how it approaches fake data. Discuss the methods, strengths, and limitations of the chosen case study.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material).",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.5. How Effective is Named Entity Recognition (NER) for Identifying Cultural and Linguistic Entities Across Languages? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.5.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Assess the accuracy and inclusiveness of AI-driven NER models when identifying culturally specific entities in multiple languages.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "spaCy's NER in Multilingual Contexts",
                (s.bold, ": "),
                "spaCy has been utilized in various studies to evaluate its effectiveness in recognizing named entities across different languages, including Arabic, Hindi, and Japanese. In one study, spaCy’s NER model showed proficiency in identifying common entities like names and locations but struggled with culturally specific references.",
            )
        with lst.item():
            st_write("A comparative analysis of BERT-based NER models demonstrated their ability to identify named entities in multiple languages. The study revealed that while BERT performed well in recognizing standard entities, it faced challenges with non-Western cultural entities. Instances of bias were noted, particularly in the recognition of names and terms unique to specific cultural backgrounds.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.5.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Multilingual NER and Cultural Inclusiveness ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "AL-RFOU, Rami, KULKARNI, Vivek, PEROZZI, Bryan, ",
                (s.italic, "et al."),
                " Polyglot-NER: Massive multilingual named entity recognition. In : ",
                (s.italic, "Proceedings of the 2015 SIAM International Conference on Data Mining"),
                ". Society for Industrial and Applied Mathematics, 2015. p. 586-594. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "PIRES, T. How multilingual is multilingual BERT. ",
                (s.italic, "arXiv preprint arXiv:1906.01502"),
                ", 2019. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NOTHMAN, Joel, RINGLAND, Nicky, RADFORD, Will, ",
                (s.italic, "et al."),
                " Learning multilingual named entity recognition from Wikipedia. ",
                (s.italic, "Artificial Intelligence"),
                ", 2013, vol. 194, p. 151-175. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Deep learning techniques in cross-lingual NER ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KADIDAM, Venkata Vamsi. ",
                (s.italic, "Cross Lingual Named Entity Recognition using Deep Learning"),
                ". 2024. Thèse de doctorat. CALIFORNIA STATE UNIVERSITY NORTHRIDGE. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GOYAL, Archana, GUPTA, Vishal, et KUMAR, Manish. Recent named entity recognition and classification techniques: a systematic review. ",
                (s.italic, "Computer Science Review"),
                ", 2018, vol. 29, p. 21-43. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "NER Performance on Specific Language Families ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MOHIT, Behrang. Named entity recognition. In : ",
                (s.italic, "Natural language processing of semitic languages"),
                ". Berlin, Heidelberg : Springer Berlin Heidelberg, 2014. p. 221-245. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.5.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review"),
                ": Each student reviews one article related to NER, focusing on cross-lingual and cultural challenges. Look for studies involving models like spaCy and BERT.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Model Selection: "),
                "Choose two NER models (e.g., spaCy, BERT, Multilingual BERT) and evaluate their performance in identifying named entities in different languages and cultures.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Studies:"),
                " analyze a case study comparing how NER models perform in identifying named entities from widely spoken languages and those with culturally unique entities (e.g., Arabic, Japanese, Hindi).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf.course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.6. How Can AI Assist Journalists in Content Creation and Reporting? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.6.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI technologies can enhance journalistic practices, from content creation to reporting and data analysis. Search AI’s capabilities in automating tasks such as writing, edition, translation, fact-checking, and improving audience engagement, as well as the implications of these technologies for journalistic integrity, efficiency, and ethical considerations. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Case Studies ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The AP uses AI-powered tools to automate routine reporting tasks, such as financial and sports news, freeing up journalists for more in-depth investigations. This AI system is able to produce hundreds of reports quickly, ensuring timely dissemination of news. While it helps maintain speed and accuracy, human oversight is essential for checking the content's context and ensuring its credibility.")
        with lst.item():
            st_write("Reuters has developed an AI-powered tool called News Tracer, which uses machine learning to detect breaking news on social media platforms. The system scans social media for early indicators of breaking events and then verifies the information using reliable sources.")
        with lst.item():
            st_write("AI tools like ClaimBuster are used in newsrooms to automatically flag statements for potential fact-checking.")
        with lst.item():
            st_write("The BBC employs AI for content recommendation and audience engagement. Their AI systems analyze user behavior to recommend relevant articles, videos, and stories in real-time.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.6.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Journalism - Overview and Case Studies ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BROUSSARD, Meredith, DIAKOPOULOS, Nicholas, GUZMAN, Andrea L., ",
                (s.italic, "et al."),
                " Artificial intelligence and journalism. ",
                (s.italic, "Journalism & mass communication quarterly"),
                ", 2019, vol. 96, no 3, p. 673-695. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NGUYEN, An T., KHAROSEKAR, Aditya, KRISHNAN, Saumyaa, ",
                (s.italic, "et al."),
                " Believe it or not: designing a human-ai partnership for mixed-initiative fact-checking. In : ",
                (s.italic, "Proceedings of the 31st annual ACM symposium on user interface software and technology"),
                ". 2018. p. 189-199. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Ethical and Trust Considerations in AI-driven Journalism ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "OPDAHL, Andreas L., TESSEM, Bjørnar, DANG-NGUYEN, Duc-Tien, ",
                (s.italic, "et al."),
                " Trustworthy journalism through AI. ",
                (s.italic, "Data & Knowledge Engineering"),
                ", 2023, vol. 146, p. 102182. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "AISSANI, Rahima, ABDALLAH, Rania Abdel-Qader, TAHA, Sawsan, ",
                (s.italic, "et al."),
                " Artificial Intelligence Tools in media and journalism: Roles and concerns. In : ",
                (s.italic, "2023 International Conference on Multimedia Computing, Networking and Applications (MCNA)"),
                ". IEEE, 2023. p. 19-26. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Future implications and perception of AI in Newsrooms ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ABDULMAJEED, Maha et FAHMY, Nagwa. Meta-analysis of AI Research in Journalism: Challenges, Opportunities and Future Research Agenda for Arab Journalism. In : ",
                (s.italic, "European, Asian, Middle Eastern, North African Conference on Management & Information Systems"),
                ". Cham : Springer International Publishing, 2022. p. 213-225. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "OKSYMETS, Viktoriia. ",
                (s.italic, "The impact of artificial intelligence on journalism practices and content creation"),
                ". 2024. Thèse de doctorat. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NOAIN SÁNCHEZ, Amaya, ",
                (s.italic, "et al."),
                " Addressing the Impact of Artificial Intelligence on Journalism: The perception of experts, journalists and academics. 2022. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.6.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Each student reviews an article on AI in journalism, focusing on how AI assists with tasks like writing, editing, and fact-checking.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study"),
                ": Review AI applications in real-world journalism (e.g., AP’s automated reporting, Reuters' News Tracer, BBC’s audience engagement). Discuss how these tools improve efficiency and accuracy.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.7. How Can AI Enhance Personalized and Accessible Language Learning in Multilingual Classrooms? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.7.1. Objective  ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI can adapt language learning and educational materials for multilingual classrooms, focusing on personalized content and accessibility improvements.")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Use cases/examples: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Duolingo and Google’s language tools analyze user progress to personalize vocabulary and syntax practice. This adaptation helps students from diverse linguistic backgrounds learn at their own pace, providing tailored content to improve engagement and retention.")
        with lst.item():
            st_write("AI-driven accessibility features on platforms like Coursera use real-time translation, subtitles, and simplified content to support multilingual learners, allowing students with varied language proficiencies to access educational materials equitably.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.7.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Personalized Learning and Educational Tools ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "PRATAMA, Muh Putra, SAMPELOLO, Rigel, et LURA, Hans. Revolutionizing education: harnessing the power of artificial intelligence for personalized learning. ",
                (s.italic, "Klasikal: Journal of education, language teaching and science"),
                ", 2023, vol. 5, no 2, p. 350-357. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "WEI, Ling. Artificial intelligence in language instruction: impact on English learning achievement, L2 motivation, and self-regulated learning. ",
                (s.italic, "Frontiers in Psychology"),
                ", 2023, vol. 14, p. 1261955. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Multilingual Classrooms and Learning Accessibility ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2666920X2400078X", link="https://www.sciencedirect.com/science/article/pii/S2666920X2400078X")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ANIS, Muneeba. Leveraging artificial intelligence for inclusive English language teaching: Strategies and implications for learner diversity. ",
                (s.italic, "Journal of Multidisciplinary Educational Research"),
                ", 2023, vol. 12, no 6, p. 54-70. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KHASAWNEH, Dr Mohamad Ahmad Saleem Khasawneh. Improving the Learning of Language Proficiency at Tertiary Education Level Through AI-Driven Assessment Models and Automated Feedback Systems. ",
                (s.italic, "Migration Letters"),
                ", vol. 21, no 2, p. 712-726. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Practical Applications and Tools for AI in Language Learning ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("GOUVI, SAPMM, LAVIDAS, Konstantinos, et KOMIS, Vassilis. The use of ChatGPT as a learning tool to improve foreign language writing in a multilingual and multicultural classroom. 2023. ")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.7.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Each student reviews research on AI in education, focusing on how AI is used to personalize language learning and improve accessibility in multilingual classrooms.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Use case:"),
                " Review how platforms like Duolingo, Google, and Coursera use AI to adapt content and improve accessibility for multilingual students. Discuss the impact of these tools on student engagement and outcomes.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material).",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.8. How Can AI Assist in Creating Culturally Relevant Educational Materials? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.8.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine AI tools that generate educational content tailored to specific cultural contexts and languages, enhancing relevance and engagement. ")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Example Studies:"),
        " Analysis of AI-generated lesson plans or learning resources from platforms like Khan Academy or custom solutions.",
    )
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Khan Academy, through machine translation and human-in-the-loop reviews, has localized its educational content into multiple languages, like Spanish, Portuguese, and Hindi. AI is used to translate and adapt content, and it learns from human feedback to improve translation accuracy over time. This approach not only makes the content linguistically accessible but also culturally relevant, as idioms, metaphors, and examples are adjusted for local contexts.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.8.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI-Driven Education and Cultural Adaptation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2666920X2400078X", link="https://www.sciencedirect.com/science/article/pii/S2666920X2400078X")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TAHIRU, Fati. AI in education: A systematic literature review. ",
                (s.italic, "Journal of Cases on Information Technology (JCIT)"),
                ", 2021, vol. 23, no 1, p. 1-20. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "HOLMES, Wayne et TUOMI, Ilkka. State of the art and practice in AI in education. ",
                (s.italic, "European Journal of Education"),
                ", 2022, vol. 57, no 4, p. 542-570. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BECK, Joseph, STERN, Mia, et HAUGSJAA, Erik. Applications of AI in Education. ",
                (s.italic, "XRDS: Crossroads, The ACM Magazine for Students"),
                ", 1996, vol. 3, no 1, p. 11-15. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Enhancing Cultural Sensitivity in AI Education Tools ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BENBOUJJA, Fouzi, HARTNICK, Elizabeth, ZABLAH, Evelyn, ",
                (s.italic, "et al."),
                " Overcoming language barriers in pediatric care: a multilingual, AI-driven curriculum for global healthcare education. ",
                (s.italic, "Frontiers in Public Health"),
                ", 2024, vol. 12, p. 1337395. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.teacherph.com/contextual-adaptability-cultural-sensitivity-ai-driven-education/", link="https://www.teacherph.com/contextual-adaptability-cultural-sensitivity-ai-driven-education/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://elearningindustry.com/shaping-new-cultural-norms-in-learning-with-ai", link="https://elearningindustry.com/shaping-new-cultural-norms-in-learning-with-ai")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://teachflow.ai/revolutionizing-education-how-ai-empowers-cultural-and-history-learning/", link="https://teachflow.ai/revolutionizing-education-how-ai-empowers-cultural-and-history-learning/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2666920X24000651", link="https://www.sciencedirect.com/science/article/pii/S2666920X24000651")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://school-education.ec.europa.eu/en/discover/news/artificial-intelligence-asset-language-learning-europe#:~:text=In%20recent%20years%2C%20artificial%20intelligence,NLP", link="https://school-education.ec.europa.eu/en/discover/news/artificial-intelligence-asset-language-learning-europe#:~:text=In%20recent%20years%2C%20artificial%20intelligence,NLP")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.techrxiv.org/users/706999/articles/699001-enhancing-multicultural-and-multilingual-education-through-problem-based-teaching-with-conversational-ai-a-chatgpt-perspective", link="https://www.techrxiv.org/users/706999/articles/699001-enhancing-multicultural-and-multilingual-education-through-problem-based-teaching-with-conversational-ai-a-chatgpt-perspective")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/377620998_Enhancing_Multicultural_and_Multilingual_Education_through_Problem-Based_Teaching_with_Conversational_AI_A_ChatGPT_Perspective", link="https://www.researchgate.net/publication/377620998_Enhancing_Multicultural_and_Multilingual_Education_through_Problem-Based_Teaching_with_Conversational_AI_A_ChatGPT_Perspective")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.8.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review"),
                ": Each student conducts a review of current literature on AI tools used for cultural adaptation and localization in education. Focus on how these tools adjust language, examples, and metaphors to match specific cultural contexts.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study"),
                ": Select case studies of platforms like Khan Academy, Duolingo, and Google’s literacy tools. Examine how these platforms use AI to improve cultural relevance in their educational materials. Discuss the strengths and limitations of each approach.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.9. How Does Language Diversity Bias Affect Multilingual Information Access? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.9.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate how AI-driven systems, such as search engines and recommendation algorithms, can introduce linguistic biases, affecting the accessibility of information across different languages.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Case Study/Example"), ": ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Analyzing Google Search results for multilingual queries reveals that the algorithm tends to prioritize English content over other languages, particularly for niche or technical topics. This impacts access for users seeking information in their native language and highlights how search algorithms may limit linguistic diversity online.")
        with lst.item():
            st_write("YouTube’s recommendation system, driven by AI, often suggests content based on global popularity, which can favor English-language videos over those in other languages. This prioritization affects content visibility for non-English speakers and reduces accessibility to culturally relevant information")
        with lst.item():
            st_write("Wikipedia’s use of machine translation to expand articles in different languages sometimes results in inconsistent content availability across languages. High-quality articles in English may not be accurately or fully available in other languages, creating an information gap for non-English readers and reinforcing language hierarchy in information access.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.9.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Bias in AI Algorithms for Multilingual Content ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "JIANG, Yang, HAO, Jiangang, FAUSS, Michael, ",
                (s.italic, "et al."),
                " Detecting ChatGPT-generated essays in a large-scale writing assessment: Is there a bias against non-native English speakers?. ",
                (s.italic, "Computers & Education"),
                ", 2024, vol. 217, p. 105070. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Impact on Information Accessibility and Equity ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://ar5iv.labs.arxiv.org/html/2311.01870", link="https://ar5iv.labs.arxiv.org/html/2311.01870")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHEN, Huan, CHAN-OLMSTED, Sylvia, et THAI, My. Culture Sensitivity and Information Access: A Qualitative Study among Ethnic Groups. ",
                (s.italic, "The Qualitative Report"),
                ", 2023, vol. 28, no 8, p. 2504-2522. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI Effectiveness in Multilingual Context ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "OCHIENG, Millicent, GUMMA, Varun, SITARAM, Sunayana, ",
                (s.italic, "et al."),
                " Beyond Metrics: Evaluating LLMs' Effectiveness in Culturally Nuanced, Low-Resource Real-World Scenarios. ",
                (s.italic, "arXiv preprint arXiv:2406.00343"),
                ", 2024. ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.9.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review: "),
                "Conduct a review of existing literature on AI-induced linguistic bias, focusing on the prevalence of English-language prioritization and its effects on access to information in other languages.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study Analysis:"),
                " Examine studies on platforms such as Google, YouTube, Wikipedia, and Spotify to understand how linguistic bias manifests in each system. Identify patterns and specific algorithmic decisions that contribute to this bias.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.10. What Cultural Biases Exist in AI-Powered Translation Tools, and How Do They Impact Cross-Cultural Communication? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.10.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine biases in AI translation models, such as Google Translate or DeepL, that might inadvertently reinforce stereotypes or misinterpret cultural expressions.")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Case Study/Example"),
        ": Analyze translations for idiomatic phrases or gendered language across several languages to observe biases in tone, context, or representation. You could also evaluate how these tools handle dialects or regional variations, affecting cultural accuracy in communication.",
    )
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Idiomatic and Cultural Expression Misinterpretation in DeepL: "),
                "DeepL, a popular translation tool, often struggles with idiomatic expressions that lack direct equivalents across languages. For instance, translating French idioms like \"avoir le cafard\" (literally \"to have the cockroach,\" meaning \"to feel down\") into English may yield inaccurate or literal translations, which fail to capture the cultural connotation. Such errors can lead to misinterpretations and hinder effective communication between cultures.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Regional Dialects and Variations in Microsoft Translator: "),
                "Microsoft Translator has implemented specialized translation models for certain regional dialects, such as Latin American Spanish and European Spanish. However, inconsistencies still arise, especially when translating idioms, colloquialisms, or regional slang, which can lead to misunderstandings. In cross-cultural business communication, for example, these nuances are critical, and failure to account for them may result in unintended disrespect or miscommunication.",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.10.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cultural Misinterpretation in Idiomatic Expressions ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BENYAHIA, Moad. Examining the Efficiency of Machine Translation in Translating English Idioms used in American Media. ",
                (s.italic, "Journal of Translation and Language Studies"),
                ", 2024, vol. 5, no 2, p. 43-55. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Bias in Gendered Language Translation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MUTASHAR, Mohammed Kadhim. Navigating Ethics in AI-Driven Translation for a Human-Centric Future. ",
                (s.italic, "Academia Open"),
                ", 2024, vol. 9, no 2, p. 10.21070/acopen. 9.2024. 9407-10.21070/acopen. 9.2024. 9407. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Regional Dialects and Linguistic Variations ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TANG, Kenan, SONG, Peiyang, QIN, Yao, ",
                (s.italic, "et al."),
                " Creative and Context-Aware Translation of East Asian Idioms with GPT-4. ",
                (s.italic, "arXiv preprint arXiv:2410.00988"),
                ", 2024. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Additional References: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ZAKI, Muhammad Zayyanu et AHMED, Umar. Bridging linguistic divides: The impact of ai-powered translation systems on communication equity and inclusion. ",
                (s.italic, "Journal of translation and language studies"),
                ", 2024, vol. 5, no 2, p. 20–30-20–30. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHARLES-KENECHI, Sandra. Artificial Intelligence in Translation Studies: Benefits and Challenges. ",
                (s.italic, "Cascades, Journal of the Department of French & International Studies"),
                ", 2024, vol. 2, no 1, p. 5-15. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.10.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review: "),
                "Review existing research on biases in AI translation, especially focusing on idiomatic expressions, gender, and regional dialects. Summarize key findings from at least one article that discusses how AI translation tools handle cultural differences.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collect and Compare Translations: "),
                "Choose 5-10 idiomatic phrases, proverbs, or gendered expressions from your own language and translate them using popular tools (e.g., Google Translate, DeepL). Compare the translations and note any biases, misinterpretations, or cultural inaccuracies.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.11. Does GenAI Exhibit Gender Bias When Processing Gendered Languages? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.11.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how language models handle gendered languages and assess if biases are introduced in languages with grammatical gender.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("An evaluation of GPT-3's responses in gendered languages like French and Spanish shows that the model often defaults to masculine forms when generating responses related to professions, reflecting societal stereotypes.")
        with lst.item():
            st_write("A study of BERT's performance in Arabic revealed that the model struggled with gender-neutral language, often assigning gendered adjectives based on contextual cues that perpetuated existing gender biases.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.11.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Bias in Gendered Language Usage ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GHOSH, Sourojit et CALISKAN, Aylin. Chatgpt perpetuates gender bias in machine translation and ignores non-gendered pronouns: Findings across bengali and five other low-resource languages. In : ",
                (s.italic, "Proceedings of the 2023 AAAI/ACM Conference on AI, Ethics, and Society"),
                ". 2023. p. 901-912. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Challenges in Gender-Neutral Language Processing ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "O’CONNOR, Sinead et LIU, Helen. Gender bias perpetuation and mitigation in AI technologies: challenges and opportunities. ",
                (s.italic, "AI & SOCIETY"),
                ", 2024, vol. 39, no 4, p. 2045-2057. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Debiaising Word Embeddings ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOLUKBASI, Tolga, CHANG, Kai-Wei, ZOU, James Y., ",
                (s.italic, "et al."),
                " Man is to computer programmer as woman is to homemaker? debiasing word embeddings. ",
                (s.italic, "Advances in neural information processing systems"),
                ", 2016, vol. 29. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Additional References: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("NADEEM, Ayesha, ABEDIN, Babak, et MARJANOVIC, Olivera. Gender bias in AI: A review of contributing factors and mitigating strategies. 2020. ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BLODGETT, Su Lin, BAROCAS, Solon, DAUMÉ III, Hal, ",
                (s.italic, "et al."),
                " Language (technology) is power: A critical survey of\" bias\" in nlp. ",
                (s.italic, "arXiv preprint arXiv:2005.14050"),
                ", 2020. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NEWSTEAD, Toby, EAGER, Bronwyn, et WILSON, Suze. How AI can perpetuate–or help mitigate–gender bias in leadership. ",
                (s.italic, "Organizational Dynamics"),
                ", 2023, vol. 52, no 4, p. 100998. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://arxiv.org/html/2401.10016v1", link="https://arxiv.org/html/2401.10016v1")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.11.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review"),
                ": Conduct a review of existing literature that discusses gender bias in AI language models, particularly those trained on gendered languages. Identify the key causes of these biases (e.g., training data, societal norms, gender imbalances) and the implications for users in multilingual and multicultural contexts.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.12. How Can AI Facilitate Cross-Cultural Understanding in Multilingual Settings? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.12.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate AI applications that help bridge cultural differences in communication, focusing on tools that enhance understanding of cultural norms and practices.")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Case Studies:  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Smartling integrates translation and localization services with cultural insights, allowing businesses to tailor their messaging for different cultural contexts. By providing users with cultural nuances and idiomatic expressions, Smartling enhances cross-cultural communication, helping organizations avoid potential misunderstandings and connect more effectively with global audiences.")
        with lst.item():
            st_write("Culture Wizard offers online training modules that combine language learning with cultural awareness. These modules help users understand key cultural differences and practices relevant to various regions, facilitating smoother interactions in multilingual settings. ")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.12.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Cross-Cultural Communication and Localization ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KHASAWNEH, Mohamad Ahmad Saleem. The Potential of Ai in Facilitating Cross-Cultural Communication Through Translation. ",
                (s.italic, "Journal of Namibian Studies: History Politics Culture"),
                ", 2023, vol. 37, p. 107-130. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI for Language Learning and Cultural Awareness ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KHARCHENKO, Julia, ROOSTA, Tanya, CHADHA, Aman, ",
                (s.italic, "et al."),
                " How well do llms represent values across cultures? empirical analysis of llm responses based on hofstede cultural dimensions. ",
                (s.italic, "arXiv preprint arXiv:2406.14805"),
                ", 2024. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI Ethics and Cultural Sensitivity ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHEN, Huan, CHAN-OLMSTED, Sylvia, et THAI, My. Culture Sensitivity and Information Access: A Qualitative Study among Ethnic Groups. ",
                (s.italic, "The Qualitative Report"),
                ", 2023, vol. 28, no 8, p. 2504-2522. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.12.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Investigate existing AI applications aimed at cross-cultural communication, focusing on how they address cultural nuances, idioms, and norms.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study"),
                " Analysis: Examine case studies of companies (e.g., Smartling, Culture Wizard) that have implemented AI tools to enhance cross-cultural understanding. Analyze the effectiveness of these tools in real-world scenarios.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.13. How Do AI-Powered Language Models Handle Humor, Sarcasm, and Other Culturally Specific Expressions Across Languages? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.13.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate the effectiveness of AI language models in understanding and generating culturally relevant humor, sarcasm, and other expressions that rely on cultural context, tone, and social norms.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Stanford University researchers assessed GPT-3's ability to generate humor in English, Spanish, and Mandarin. They found that while the model produced some relevant jokes, it struggled with puns and culturally specific references, revealing limitations in understanding humor across diverse cultures.")
        with lst.item():
            st_write("At the University of Cambridge, researchers tested ChatGPT’s ability to adapt jokes for British, American, and Indian contexts. While the model reformulated jokes, it often missed critical cultural nuances, highlighting the need for improved cultural context in AI training for better humor recognition in multilingual settings.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.13.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI and Cross-Cultural Humor Understanding ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MIROWSKI, Piotr, LOVE, Juliette, MATHEWSON, Kory, ",
                (s.italic, "et al."),
                " A Robot Walks into a Bar: Can Language Models Serve as Creativity SupportTools for Comedy? An Evaluation of LLMs’ Humour Alignment with Comedians. In : ",
                (s.italic, "The 2024 ACM Conference on Fairness, Accountability, and Transparency"),
                ". 2024. p. 1622-1636. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Sarcasm Detection and Irony in AI ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "JOSHI, Aditya, BHATTACHARYYA, Pushpak, et CARMAN, Mark J. Automatic sarcasm detection: A survey. ",
                (s.italic, "ACM Computing Surveys (CSUR)"),
                ", 2017, vol. 50, no 5, p. 1-22. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ILIĆ, Suzana, MARRESE-TAYLOR, Edison, BALAZS, Jorge A., ",
                (s.italic, "et al."),
                " Deep contextualized word representations for detecting sarcasm and irony. ",
                (s.italic, "arXiv preprint arXiv:1809.09795"),
                ", 2018. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KUMAR, Yogesh et GOEL, Nikita. AI-Based learning techniques for sarcasm detection of social media tweets: State-of-the-art survey. ",
                (s.italic, "SN Computer Science"),
                ", 2020, vol. 1, no 6, p. 318. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cultural Context and Social Norms in AI Language Models ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RAMEZANI, Aida et XU, Yang. Knowledge of cultural moral norms in large language models. ",
                (s.italic, "arXiv preprint arXiv:2306.01857"),
                ", 2023. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Additional references"), ":  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MIROWSKI, Piotr, MATHEWSON, Kory W., PITTMAN, Jaylen, ",
                (s.italic, "et al."),
                " Co-writing screenplays and theatre scripts with language models: Evaluation by industry professionals. In : ",
                (s.italic, "Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems"),
                ". 2023. p. 1-34. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.13.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Investigate how humor, sarcasm, and culturally specific expressions are handled in AI models, including challenges related to tone, social context, and linguistic peculiarities.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "AI Model Evaluation"),
                ": Assess various AI models (e.g., GPT-3, BERT, ChatGPT) for their ability to generate humor and recognize sarcasm across different languages, including English, Spanish, and Mandarin. Test for accuracy in detecting and producing culturally relevant expressions.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.14. How Can AI Assist in Creating Multilingual Glossaries for Academic and Technical Terminology? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.14.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Assess how AI can help build comprehensive multilingual glossaries, aiding students and professionals working in multilingual environments.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("OpenAI's GPT-3 has been used to extract and translate technical terms from academic papers, creating multilingual glossaries that capture specialized terminology. The model's contextual understanding aids in accurate translations, although it struggles with niche terms lacking direct equivalents.")
        with lst.item():
            st_write("Microsoft Translator has been utilized to create multilingual glossaries for technical documentation in fields like engineering. While it effectively translates common terms, it encounters difficulties with industry-specific jargon, highlighting the need for further refinement in technical contexts.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.14.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI and Translation Models for Technical Terminology ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.bitkom.org/sites/default/files/2020-12/201217_sof8_ai-in-technical-translation.pdf", link="https://www.bitkom.org/sites/default/files/2020-12/201217_sof8_ai-in-technical-translation.pdf")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2772941924000012", link="https://www.sciencedirect.com/science/article/pii/S2772941924000012")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2405844024041379", link="https://www.sciencedirect.com/science/article/pii/S2405844024041379")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Human-in-the-Loop for Enhancing AI Terminology Translation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KHAN, Fatima. Human-in-the-Loop Approaches to Improving Machine Translation. ",
                (s.italic, "Academic Journal of Science and Technology"),
                ", 2024, vol. 7, no 1, p. 1− 8-1− 8. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "YANG, Xinyi, ZHAN, Runzhe, WONG, Derek F., ",
                (s.italic, "et al."),
                " Human-in-the-loop machine translation with large language model. ",
                (s.italic, "arXiv preprint arXiv:2310.08908"),
                ", 2023. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cross-Domain AI for Multilingual Term Mapping and Refinement ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Empowering Multilingual AI: Cross-Lingual Transfer Learning")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BRINGMANN, Anna et ZHUKOVA, Anastasia. Domain Adaptation of Multilingual Semantic Search--Literature Review. ",
                (s.italic, "arXiv preprint arXiv:2402.02932"),
                ", 2024. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://aclanthology.org/2022.acl-long.482.pdf", link="https://aclanthology.org/2022.acl-long.482.pdf")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.14.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Begin by reviewing key literature on the use of AI in technical and academic translation, focusing on its ability to generate accurate multilingual glossaries. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Explore AI Models:"),
                " Investigate the capabilities of AI language models (e.g., GPT-3, Microsoft Translator) in extracting and translating technical terms. Test these models with real-world academic and technical content.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.15. How Do AI-Powered Translation Tools Affect Correctness in Cross-Cultural Communication? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.15.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate the accuracy and correctness of AI-powered translation tools in transmitting culturally sensitive information and ensuring the intended meaning is preserved when translating between languages with different cultural norms and linguistic structures.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Studies have shown that AI tools like Google Translate sometimes misinterpret or oversimplify complex concepts, especially in languages with different syntactic or grammatical structures. For example, translating idiomatic expressions or culture-bound terms can lead to loss of meaning or incorrect interpretations, particularly in languages with rich context-dependent expressions (e.g., Japanese to English)")
        with lst.item():
            st_write("Research involving formal texts, like business communications, has revealed that AI translation tools like DeepL and Microsoft Translator can struggle with industry-specific jargon, leading to inaccuracies in technical translations. This is often due to the model's inability to fully grasp specialized terminology or context-specific nuances that go beyond the literal meaning of the words.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.15.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI Translation Models and their capabilities ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2405844024041379", link="https://www.sciencedirect.com/science/article/pii/S2405844024041379")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.nature.com/articles/s41599-024-03726-7", link="https://www.nature.com/articles/s41599-024-03726-7")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Accuracy in AI Translation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2772941924000012", link="https://www.sciencedirect.com/science/article/pii/S2772941924000012")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchsquare.com/article/rs-2814154/v2", link="https://www.researchsquare.com/article/rs-2814154/v2")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/370364647_The_Impacts_and_Challenges_of_Artificial_Intelligence_Translation_Tool_on_Translation_Professionals", link="https://www.researchgate.net/publication/370364647_The_Impacts_and_Challenges_of_Artificial_Intelligence_Translation_Tool_on_Translation_Professionals")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Cross-Cultural Communication and Ethics in AI Translation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2589004224021035", link="https://www.sciencedirect.com/science/article/pii/S2589004224021035")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/374417280_The_Potential_Of_Ai_In_Facilitating_Cross-Cultural_Communication_Through_Translation", link="https://www.researchgate.net/publication/374417280_The_Potential_Of_Ai_In_Facilitating_Cross-Cultural_Communication_Through_Translation")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://aclanthology.org/2022.acl-long.482.pdf", link="https://aclanthology.org/2022.acl-long.482.pdf")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Additional References"), ":  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://about.fb.com/news/2020/10/first-multilingual-machine-translation-model/", link="https://about.fb.com/news/2020/10/first-multilingual-machine-translation-model/")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.15.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Examine the role of context, culture, and linguistic structures in translation and how AI models handle these factors. Investigate how translation tools handle context-dependent expressions, politeness markers, and cultural references, and how this impacts translation correctness.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Model Comparison"),
                ": Evaluate the translation accuracy of multiple AI tools (e.g., Google Translate, DeepL, Microsoft Translator) across different languages with varying linguistic structures and cultural contexts. Focus on accuracy in translating idiomatic expressions, cultural references, and technical jargon.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study Analysis"),
                ": Conduct case studies involving real-world examples of translations that are prone to errors, such as business emails, official documentation, or social media posts.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material) ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.16. What Impact Does AI Have on Language Preservation? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.16.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI can be used to document and preserve endangered languages, focusing on machine learning models that help in language revitalization efforts.")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Example Studies:")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The Endangered Languages Project leverages AI technologies to document and preserve endangered languages. It uses machine learning algorithms to analyze and catalog linguistic data, including audio recordings and text resources.")
        with lst.item():
            st_write("Google's Linguistic Data Consortium works on developing AI tools for minority language documentation. This initiative focuses on using speech recognition and natural language processing technologies to collect and archive language data for endangered languages. ")
        with lst.item():
            st_write("Mozilla’s Common Voice Project: An open-source platform that collects voice samples in underrepresented languages, providing data for AI to improve speech recognition in these languages. ")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.16.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI for Language Documentation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/379076488_Artificial_intelligence's_role_in_the_realm_of_endangered_languages_Documentation_and_teaching", link="https://www.researchgate.net/publication/379076488_Artificial_intelligence's_role_in_the_realm_of_endangered_languages_Documentation_and_teaching")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Language Preservation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.propulsiontechjournal.com/index.php/journal/article/view/6122", link="https://www.propulsiontechjournal.com/index.php/journal/article/view/6122")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/370127283_Revitalizing_Endangered_Languages_AI-powered_language_learning_as_a_catalyst_for_language_appreciation", link="https://www.researchgate.net/publication/370127283_Revitalizing_Endangered_Languages_AI-powered_language_learning_as_a_catalyst_for_language_appreciation")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Speech Recognition and NLP for Endangered Languages ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://arxiv.org/pdf/2204.11909", link="https://arxiv.org/pdf/2204.11909")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MOHANTY, Sushree Sangita, PARIDA, Shantipriya, et DASH, Satya Ranjan. Role of NLP for corpus development of endangered languages. ",
                (s.italic, "Grenze International Journal of Engineering and Technology. Jan Issue. Grenze ID"),
                ", 2023, vol. 1. ",
            )
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.16.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review"),
                ": Research AI technologies like NLP and speech recognition as applied to endangered languages. Focus on ethical challenges, community involvement, and cultural sensitivity.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study Analysis:"),
                " Analyze specific cases (e.g., Mozilla’s Common Voice, Google’s language initiatives) to assess their success and the limitations of AI for low-resource languages. Highlight key technological, cultural, and community challenges.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.17. Can AI Support Cultural Heritage Preservation? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.17.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate the potential of AI to assist in preserving cultural heritage by digitizing and generating multilingual versions of traditional narratives and terminologies.")
    st_write(s.project.doc.paragraphs.p_body, (s.bold, "Examples/Case Studies"), ":")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("UNESCO has implemented AI technologies in its Global Digital Library initiative, which aims to digitize and translate traditional narratives and cultural texts into multiple languages. This effort enhances access to cultural heritage materials and supports preservation by making them available to diverse linguistic communities.")
        with lst.item():
            st_write("Google's Art and Culture platform employs AI to generate multilingual descriptions of cultural artifacts and heritage sites. By using machine learning algorithms, the platform translates and contextualizes cultural content, making it accessible to a global audience while preserving the original meaning and significance of the narratives involved.")
        with lst.item():
            st_write("AI in Archaeology (GlobalXplorer): This AI-based tool, supported by crowdsourcing, assists in identifying and preserving archaeological sites by analyzing satellite images to prevent artifact looting.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.17.2. References and Resources ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Cultural Preservation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://isprs-archives.copernicus.org/articles/XLVIII-M-2-2023/1149/2023/isprs-archives-XLVIII-M-2-2023-1149-2023.pdf", link="https://isprs-archives.copernicus.org/articles/XLVIII-M-2-2023/1149/2023/isprs-archives-XLVIII-M-2-2023-1149-2023.pdf")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/383675771_The_review_of_AI_and_cultural_heritage_protectionTaking_the_whole_process_of_cultural_heritage_protection_as_an_example", link="https://www.researchgate.net/publication/383675771_The_review_of_AI_and_cultural_heritage_protectionTaking_the_whole_process_of_cultural_heritage_protection_as_an_example")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI for cultural artifact digitalization ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/abs/pii/S1296207424001468", link="https://www.sciencedirect.com/science/article/abs/pii/S1296207424001468")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.europarl.europa.eu/thinktank/en/document/EPRS_BRI(2023)747120", link="https://www.europarl.europa.eu/thinktank/en/document/EPRS_BRI(2023)747120")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://hal.science/hal-04399935/document", link="https://hal.science/hal-04399935/document")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.17.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review:"),
                " Begin with a literature review of AI's role in cultural heritage preservation. Research AI’s application in digitization, restoration, and accessibility of artifacts and the implications of data representation.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study:"),
                " Study prominent AI-based cultural projects (e.g., Google Arts & Culture, GlobalXplorer) to assess their techniques for artifact preservation and accessibility, focusing on how AI handles cultural context and diversity.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "6.2.18. How Can AI-Driven Sentiment Analysis Improve Multilingual Social Media Engagement? ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.18.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI-driven sentiment analysis tools can enhance brands' understanding of audience reactions across different languages and cultures on social media, helping brands tailor their communication strategies for diverse global audiences.")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Example Studies:")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Brandwatch employs AI-driven sentiment analysis to monitor social media engagement for brands across various languages. The tool analyzes posts and comments in real-time, categorizing sentiment and providing insights into audience reactions.")
        with lst.item():
            st_write("Hootsuite offers a social listening tool that utilizes sentiment analysis to gauge public opinion about brands globally. The tool processes data from multiple languages and identifies trends in audience sentiment. While it effectively highlights positive or negative reactions, it also faces hurdles in managing context-specific language. ")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.18.2. References and Resources ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "AI in Sentiment Analysis for Multilingual Social Media ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/abs/pii/S1568494621002969", link="https://www.sciencedirect.com/science/article/abs/pii/S1568494621002969")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/335985551_Sentiment_Analysis_in_Social_Media_Based_on_English_Language_Multilingual_Processing_Using_Three_Different_Analysis_Techniques", link="https://www.researchgate.net/publication/335985551_Sentiment_Analysis_in_Social_Media_Based_on_English_Language_Multilingual_Processing_Using_Three_Different_Analysis_Techniques")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Challenges in Cross-Cultural Sentiment Analysis ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/372199689_Challenges_and_Issues_in_Sentiment_Analysis_A_Comprehensive_Survey", link="https://www.researchgate.net/publication/372199689_Challenges_and_Issues_in_Sentiment_Analysis_A_Comprehensive_Survey")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://aclanthology.org/2022.acl-long.482.pdf", link="https://aclanthology.org/2022.acl-long.482.pdf")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "YE, Liu, WEI, Cheng, et YIMENG, Yin. Cross cultural Comparative Study on Emotional Analysis of Social Media. ",
                (s.italic, "Procedia Computer Science"),
                ", 2023, vol. 221, p. 634-641. ",
            )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Social Media and Audience Engagement with AI ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.researchgate.net/publication/379299506_Enhancing_audience_engagement_through_ai-powered_social_media_automation", link="https://www.researchgate.net/publication/379299506_Enhancing_audience_engagement_through_ai-powered_social_media_automation")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "6.2.18.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review:"),
                " Begin by reviewing existing literature on AI-driven sentiment analysis tools and their application in social media marketing. Focus on how sentiment analysis is implemented for multilingual engagement and identify gaps or challenges.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case Study Analysis:"),
                " Conduct detailed case studies of tools like Brandwatch and Hootsuite to evaluate how well they perform sentiment analysis across multiple languages and cultures. Assess the challenges these tools face in understanding cultural context and language-specific nuances.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Report writing"),
                " (cf. course material)",
            )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
