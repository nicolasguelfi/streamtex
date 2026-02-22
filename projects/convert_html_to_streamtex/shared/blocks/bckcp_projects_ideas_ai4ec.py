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
      #783e04 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
    Dropped colors:
      #222222
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "1. Projects ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.burnt_orange + s.bold, "TO BE ADDED DURING FOURTH SESSION ")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.bright_red + s.bold, "Projects presentation slides available "),
        (s.project.doc.links.link_md + s.project.colors.link_blue + s.bold, "HERE", "https://docs.google.com/document/d/1DcnKTFIBhvJNciLvY_tkAa7ye8jctlj8lGeTEHRSbJs/edit"),
    )
    st_write(s.project.doc.titles.h2, "1.1. Projects Overview ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Diplomacy ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How can AI improve the diplomatic process?")
        with lst.item():
            st_write("What role does AI play in strengthening European Security?")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Sustainable Development ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("What is the current or predicted impact of AI on SDG (Sustainable Development Goals)?")
        with lst.item():
            st_write("How Can AI Support Environmental Sustainability Initiatives in Europe?")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Health ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("What is the current or predicted impact of AI on health?")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Employment ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Can Artificial Intelligence Drive Job Creation, Innovation, and Industry Resilience in Europe?")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Ethics ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How, where, why and by who AI tools should be controlled?")
        with lst.item():
            st_write("Should each country develop its ChatGPT?")
        with lst.item():
            st_write("How is AI impacting individual freedom in digital spaces?")
        with lst.item():
            st_write("How does AI exacerbate or mitigate discrimination?")
        with lst.item():
            st_write("How can AI combat or contribute to misinformation and social manipulation?")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "AI and Intercultural Dialogue ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("How Can AI Facilitate Intercultural Dialogue and Integration in Europe?")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.2. How can AI improve the diplomatic process? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.2.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI can enhance various aspects of diplomacy, from data-driven decision-making to conflict resolution, by leveraging AI tools for communication, negotiation, and sentiment analysis.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/Case Study", ": AI in Brexit Negotiations ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Big Data and Diplomacy"),
                ": The Brexit negotiations between the UK and the EU were complex, with multiple stakeholders and dynamic public opinions influencing the process. AI was used to analyze large amounts of data from social media, news outlets, and official statements.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Sentiment Analysis Application"),
                ": AI tools like sentiment analysis helped diplomats gauge public sentiment and predict the reaction to different negotiation outcomes. For instance, sentiment analysis of online discussions about Brexit helped negotiators understand public feelings toward key issues, such as trade agreements and immigration.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.2.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature Review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("ROUMATE, Fatima (ed.). Artificial intelligence and digital diplomacy: Challenges and opportunities. 2021. ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.eurasiareview.com/20092024-ai-in-global-diplomacy-opportunities-and-challenges-oped/#:~:text=AI%20can%20assist%20in%20real,without%20relying%20on%20human%20interpreters", "https://www.eurasiareview.com/20092024-ai-in-global-diplomacy-opportunities-and-challenges-oped/#:~:text=AI%20can%20assist%20in%20real,without%20relying%20on%20human%20interpreters"),
                ".",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.linkedin.com/pulse/rise-artificial-intelligence-diplomacy-international-relations-s9rsc", link="https://www.linkedin.com/pulse/rise-artificial-intelligence-diplomacy-international-relations-s9rsc")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Case Studies ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("GEORGIADOU, Elena, ANGELOPOULOS, Spyros, et DRAKE, Helen. Big data analytics and international negotiations: Sentiment analysis of Brexit negotiating outcomes. International Journal of Information Management, 2020, vol. 51, p. 102048. ")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://sonatafy.com/artificial-intelligence-transforming-conflict-resolution/", link="https://sonatafy.com/artificial-intelligence-transforming-conflict-resolution/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://unu.edu/sites/default/files/2023-09/predictive_technologies_conflict_prevention_.pdf", link="https://unu.edu/sites/default/files/2023-09/predictive_technologies_conflict_prevention_.pdf")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.tandfonline.com/doi/abs/10.1080/1369118X.2015.1008542", link="https://www.tandfonline.com/doi/abs/10.1080/1369118X.2015.1008542")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI tools for diplomacy ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.linkedin.com/pulse/amplifying-diplomatic-capabilities-ai-powered-khuwe", link="https://www.linkedin.com/pulse/amplifying-diplomatic-capabilities-ai-powered-khuwe")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://stabilityjournal.org/articles/10.5334/sta.cr", link="https://stabilityjournal.org/articles/10.5334/sta.cr")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://diplomaticacademy.us/2023/10/01/artificial-intelligence-diplomacy/", link="https://diplomaticacademy.us/2023/10/01/artificial-intelligence-diplomacy/")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Challenges and benefits")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://diplomatist.com/2024/05/20/the-use-of-artificial-intelligence-in-foreign-ministries/", link="https://diplomatist.com/2024/05/20/the-use-of-artificial-intelligence-in-foreign-ministries/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.interface-eu.org/storage/archive/files/ai_foreign_policy.pdf", link="https://www.interface-eu.org/storage/archive/files/ai_foreign_policy.pdf")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.2.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review:"),
                " Study existing research on the use of AI in diplomatic processes, including AI's role in negotiation and communication (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Case studies (approaches):"),
                " Analyze examples where AI was employed in international diplomatic efforts to enhance understanding and facilitate negotiations (20 hours).",
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "AI tools for diplomacy:"),
                " Explore and evaluate AI tools used to support diplomatic communication, negotiation strategies, and decision-making processes (15 hours).",
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Challenges and benefits:"),
                " Investigate the potential benefits of AI in diplomacy, as well as the challenges it may pose in diplomatic contexts (25 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_write(s.project.doc.titles.h2, "1.3. What role does AI play in strengthening European Security?  ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.3.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Analyze how AI contributes to European security by enhancing cybersecurity, intelligence gathering, and border control, while also considering ethical implications.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study")
    st_write(s.project.doc.paragraphs.p_body, "Estonia is recognized as a leader in cybersecurity, particularly after facing significant cyberattacks during the 2007 Bronze Soldier controversy. The nation has developed an advanced cyber defense strategy, leveraging AI technologies to safeguard its critical infrastructure and respond to evolving cyber threats effectively.")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.3.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Cybersecurity ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SARKER, Iqbal H., FURHAD, Md Hasan, et NOWROZY, Raza. Ai-driven cybersecurity: an overview, security intelligence modeling and research directions. ",
                (s.italic, "SN Computer Science"),
                ", 2021, vol. 2, no 3, p. 173. ",
            )
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://ieeexplore.ieee.org/document/9458190", link="https://ieeexplore.ieee.org/document/9458190")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Intelligence Gathering Exploration ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.linkedin.com/pulse/artificial-intelligence-national-security-prof-ahmed-banafa-lg71c#:~:text=In%20the%20context%20of%20national,an%20ongoing%20area%20of%20research", "https://www.linkedin.com/pulse/artificial-intelligence-national-security-prof-ahmed-banafa-lg71c#:~:text=In%20the%20context%20of%20national,an%20ongoing%20area%20of%20research"),
                ". ",
            )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Border Control and Surveillance Analysis ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.frontex.europa.eu/assets/Publications/Research/Frontex_AI_Research_Study_2020_executive_summary.pdf", link="https://www.frontex.europa.eu/assets/Publications/Research/Frontex_AI_Research_Study_2020_executive_summary.pdf")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://link.springer.com/chapter/10.1007/978-3-031-58649-1_7#:~:text=Estonia's%20defence%2C%20security%2C%20and%20space,and%20digital%20battlefield%20management%20solutions", "https://link.springer.com/chapter/10.1007/978-3-031-58649-1_7#:~:text=Estonia's%20defence%2C%20security%2C%20and%20space,and%20digital%20battlefield%20management%20solutions"),
                ". ",
            )
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.europarl.europa.eu/RegData/etudes/IDAN/2021/690706/EPRS_IDA(2021)690706_EN.pdf", link="https://www.europarl.europa.eu/RegData/etudes/IDAN/2021/690706/EPRS_IDA(2021)690706_EN.pdf")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.ie-ei.eu/Ressources/FCK/image/Theses/2023/Ciudad_Fontecha_EUDIPLO_Thesis_2023.pdf", link="https://www.ie-ei.eu/Ressources/FCK/image/Theses/2023/Ciudad_Fontecha_EUDIPLO_Thesis_2023.pdf")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.3.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Cybersecurity research:"),
                " Investigate how AI technologies are being used to protect critical infrastructure from cyberattacks and enhance cybersecurity in Europe (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Intelligence gathering exploration:"),
                " Study the role of AI in improving intelligence capabilities for national and European security agencies (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Border control and surveillance analysis:"),
                " Examine the use of AI in securing borders, focusing on the ethical and practical challenges involved (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Ethical considerations:"),
                " Review the ethical implications of AI in European security, especially regarding surveillance and privacy (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_write(s.project.doc.titles.h2, "1.4. What is the current or predicted impact of AI on SDG (Sustainable Development Goals)? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.4.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI is contributing to the achievement of global goals, such as addressing climate change, reducing inequalities, and promoting sustainable development.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("DeepMind's AI for Reducing Energy Consumption in Google Data Centers")
    st_write(s.project.doc.paragraphs.p_body, "DeepMind, an AI company acquired by Google, implemented machine learning models to reduce the energy consumption of Google’s data centers. These centers are notorious for consuming vast amounts of electricity to keep servers cool. Using AI, DeepMind was able to optimize cooling systems, resulting in a 40% reduction in energy used for cooling and a 15% improvement in overall energy efficiency. The AI system processes data from thousands of sensors in the data centers and adjusts cooling mechanisms in real time to reduce the energy footprint.")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.project.doc.links.default + s.project.colors.link_blue + s.italic, "DeepMind Blog:", "https://deepmind.google/discover/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/#:~:text=Our%20machine%20learning%20system%20was,and%20other%20non%2Dcooling%20inefficiencies"),
        (s.project.doc.links.default + s.project.colors.link_blue, " ", "https://deepmind.google/discover/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/#:~:text=Our%20machine%20learning%20system%20was,and%20other%20non%2Dcooling%20inefficiencies"),
        (s.project.doc.links.default + s.project.colors.link_blue + s.italic, "DeepMind AI Reduces Google Data Centre Cooling Bill by 40%.", "https://deepmind.google/discover/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/#:~:text=Our%20machine%20learning%20system%20was,and%20other%20non%2Dcooling%20inefficiencies"),
    )
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.4.2. References and Resources  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature Review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://changeoracle.com/2024/02/26/ai-and-the-sdgs/#:~:text=Artificial%20intelligence%20(AI)%20may%20be,sources%20of%20energy%20and%20efficiency", "https://changeoracle.com/2024/02/26/ai-and-the-sdgs/#:~:text=Artificial%20intelligence%20(AI)%20may%20be,sources%20of%20energy%20and%20efficiency"),
                ".",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://sdg-action.org/can-ai-help-us-achieve-the-sdgs/", link="https://sdg-action.org/can-ai-help-us-achieve-the-sdgs/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.paris21.org/sites/default/files/related_documents/2024-04/the-potential-of-ai-for-the-sdgs-and-official-stats_working-paper_0.pdf", link="https://www.paris21.org/sites/default/files/related_documents/2024-04/the-potential-of-ai-for-the-sdgs-and-official-stats_working-paper_0.pdf")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Current Examples ")
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ROLNICK, David, DONTI, Priya L., KAACK, Lynn H., ",
                (s.italic, "et al."),
                " Tackling climate change with machine learning. ",
                (s.italic, "ACM Computing Surveys (CSUR)"),
                ", 2022, vol. 55, no 2, p. 1-96. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://greenly.earth/en-us/blog/ecology-news/how-can-artificial-intelligence-help-tackle-climate-change", link="https://greenly.earth/en-us/blog/ecology-news/how-can-artificial-intelligence-help-tackle-climate-change")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.weforum.org/agenda/2024/02/ai-combat-climate-change/", link="https://www.weforum.org/agenda/2024/02/ai-combat-climate-change/")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KAACK, Lynn H., DONTI, Priya L., STRUBELL, Emma, ",
                (s.italic, "et al."),
                " Aligning artificial intelligence with climate change mitigation. ",
                (s.italic, "Nature Climate Change"),
                ", 2022, vol. 12, no 6, p. 518-527.",
            )
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/299561597_Intelligence_Unleashed_An_argument_for_AI_in_Education", link="https://www.researchgate.net/publication/299561597_Intelligence_Unleashed_An_argument_for_AI_in_Education")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TAHIRU, Fati. AI in education: A systematic literature review. ",
                (s.italic, "Journal of Cases on Information Technology (JCIT)"),
                ", 2021, vol. 23, no 1, p. 1-20.",
            )
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.unwomen.org/en/news-stories/explainer/2024/05/artificial-intelligence-and-gender-equality", link="https://www.unwomen.org/en/news-stories/explainer/2024/05/artificial-intelligence-and-gender-equality")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.4.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review:"),
                " Examine how AI has been applied to help achieve specific SDGs, focusing on areas like climate action, poverty reduction, and inequality (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Current examples:"),
                " Identify and analyze case studies (approaches) where AI has been used successfully to address one or more SDGs (20 hours).",
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Future potential:"),
                " Investigate emerging AI technologies and their potential to support sustainable development in the future (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Challenges and ethics:"),
                " Discuss the ethical challenges, risks, and limitations of relying on AI to achieve global goals (25 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.5. How Can AI Support Environmental Sustainability Initiatives in Europe? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.5.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Analyze AI's role in supporting environmental sustainability, including its applications in climate monitoring, agriculture, and renewable energy management.")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "Example/case study",
        "The European Space Agency (ESA) has integrated AI into its climate monitoring programs, specifically through the use of satellite data. AI algorithms are employed to analyze large datasets from Earth observation satellites, enabling the monitoring of environmental changes such as deforestation, urbanization, and extreme weather events.",
    )
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.5.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Climate monitoring ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DEWITTE, Steven, CORNELIS, Jan P., MÜLLER, Richard, ",
                (s.italic, "et al."),
                " Artificial intelligence revolutionises weather forecast, climate monitoring and decadal prediction. ",
                (s.italic, "Remote Sensing"),
                ", 2021, vol. 13, no 16, p. 3209. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.esa.int/Enabling_Support/Preparing_for_the_Future/Discovery_and_Preparation/Artificial_intelligence_in_space", link="https://www.esa.int/Enabling_Support/Preparing_for_the_Future/Discovery_and_Preparation/Artificial_intelligence_in_space")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/353896030_Artificial_Intelligence_Revolutionises_Weather_Forecast_Climate_Monitoring_and_Decadal_Prediction", link="https://www.researchgate.net/publication/353896030_Artificial_Intelligence_Revolutionises_Weather_Forecast_Climate_Monitoring_and_Decadal_Prediction")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Sustainable agriculture ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2772375524000212", link="https://www.sciencedirect.com/science/article/pii/S2772375524000212")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2772375524000212#:~:text=AI%2Ddriven%20agriculture%20plays%20a,irrigation%20and%20conserve%20water%20resources", "https://www.sciencedirect.com/science/article/pii/S2772375524000212#:~:text=AI%2Ddriven%20agriculture%20plays%20a,irrigation%20and%20conserve%20water%20resources"),
                ". ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S1877050923015089", link="https://www.sciencedirect.com/science/article/pii/S1877050923015089")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Renewable energy management ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/abs/pii/S0196890424001481", link="https://www.sciencedirect.com/science/article/abs/pii/S0196890424001481")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SHIN, Won, HAN, Jeongyun, et RHEE, Wonjong. AI-assistance for predictive maintenance of renewable energy systems. ",
                (s.italic, "Energy"),
                ", 2021, vol. 221, p. 119775. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RANE, Nitin. Contribution of ChatGPT and other generative artificial intelligence (AI) in renewable and sustainable energy. ",
                (s.italic, "Available at SSRN 4597674"),
                ", 2023. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.weforum.org/agenda/2024/08/how-ai-can-help-revolutionize-solar-power/#:~:text=AI%20algorithms%20analyze%20meteorological%20data,impact%20of%20intermittent%20energy%20supply", "https://www.weforum.org/agenda/2024/08/how-ai-can-help-revolutionize-solar-power/#:~:text=AI%20algorithms%20analyze%20meteorological%20data,impact%20of%20intermittent%20energy%20supply"),
                ". ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.fdmgroup.com/news-insights/ai-in-energy-sector/", link="https://www.fdmgroup.com/news-insights/ai-in-energy-sector/")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.5.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Climate monitoring:"),
                " Study AI tools for tracking and analyzing climate change data (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Sustainable agriculture:"),
                " Investigate AI’s role in optimizing resource use in agricultural practices (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Renewable energy management:"),
                " Research how AI enhances the management and integration of renewable energy sources (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.6. What is the current or predicted impact of AI on health? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.6.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI is transforming the healthcare sector, including disease prediction, diagnostics, telemedicine, personalized treatment, and ethical considerations.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/Case study ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "A study published in ",
        (s.italic, "Communications Medicine"),
        " by Johns Hopkins researchers in March 2024 showcased an innovative application of AI in medical imaging. The researchers developed a deep neural network-based automated detection tool that assists emergency room clinicians in diagnosing COVID-19 by analyzing lung ultrasound images. The tool is specifically designed to identify B-lines—bright, vertical abnormalities on ultrasound images that indicate inflammation in patients with pulmonary complications.",
    )
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.6.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10804900/", link="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10804900/")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare", link="https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2949916X24000616#:~:text=AI%20can%20identify%20patients%20at,increase%20the%20effectiveness%20of%20healthcare", link="https://www.sciencedirect.com/science/article/pii/S2949916X24000616#:~:text=AI%20can%20identify%20patients%20at,increase%20the%20effectiveness%20of%20healthcare")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RAJPURKAR, Pranav, CHEN, Emma, BANERJEE, Oishi, ",
                (s.italic, "et al."),
                " AI in health and medicine. ",
                (s.italic, "Nature medicine"),
                ", 2022, vol. 28, no 1, p. 31-38. ",
            )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI in Diagnostics ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9955430/", link="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9955430/")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.spectral-ai.com/blog/artificial-intelligence-in-medical-diagnosis-how-medical-diagnostics-are-improving-through-ai/", link="https://www.spectral-ai.com/blog/artificial-intelligence-in-medical-diagnosis-how-medical-diagnostics-are-improving-through-ai/")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI in Telemedicine ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SHARMA, Sachin, RAWAL, Raj, et SHAH, Dharmesh. Addressing the challenges of AI-based telemedicine: Best practices and lessons learned. ",
                (s.italic, "Journal of education and health promotion"),
                ", 2023, no 1, p. 338. ",
            )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Personalized Medecine ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.linkedin.com/pulse/personalized-medicine-how-ai-tailoring-treatment-tanveer-bv9xf#:~:text=By%20leveraging%20machine%20learning%20algorithms,treatment%20options%20for%20each%20patient", "https://www.linkedin.com/pulse/personalized-medicine-how-ai-tailoring-treatment-tanveer-bv9xf#:~:text=By%20leveraging%20machine%20learning%20algorithms,treatment%20options%20for%20each%20patient"),
                ".",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/379921191_AI'S_IMPACT_ON_PERSONALIZED_MEDICINE_TAILORING_TREATMENTS_FOR_IMPROVED_HEALTH_OUTCOMES", link="https://www.researchgate.net/publication/379921191_AI'S_IMPACT_ON_PERSONALIZED_MEDICINE_TAILORING_TREATMENTS_FOR_IMPROVED_HEALTH_OUTCOMES")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Ethical Considerations ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S1078143923004179", link="https://www.sciencedirect.com/science/article/pii/S1078143923004179")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8826344/", link="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8826344/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.862322/full", link="https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.862322/full")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.6.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature review:"),
                " Investigate AI’s application in health, including disease prediction, access to healthcare, and diagnostics (15 hours).",
            )
        with lst.item():
            st_write("Choosing a specific European public service as a case study (e.g., healthcare) (10 hours).")
        with lst.item():
            st_write("Researching and understanding the current use of AI in the chosen public service (15 hours).")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "AI in Health"),
                ": Study how AI can support health initiatives related to SDG 3 (Good Health and Well-Being), such as disease prediction and healthcare access.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "AI in Diagnostics:"),
                " Analyze case studies and research on the use of AI for early disease detection and diagnostic tools (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "AI and Telemedicine:"),
                " Study how AI improves telemedicine, particularly in remote healthcare services (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Personalized Medicine:"),
                " Research how AI tailors treatments based on patient data and medical history (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Analyzing ",
                (s.bold, "the impact of AI"),
                " on efficiency, accessibility, and privacy within the chosen service (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Ethical considerations:"),
                " Examine ethical implications and patient data privacy concerns associated with AI in healthcare.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.7. How Can Artificial Intelligence Drive Job Creation, Innovation, and Industry Resilience in Europe? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.7.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI can drive job creation, stimulate innovation, and strengthen industry resilience across Europe. The objective is to evaluate the impact of AI in fostering sustainable economic growth and addressing challenges within the European job market.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study ")
    st_write(s.project.doc.paragraphs.p_body, "The European automotive industry has seen significant transformation through AI, particularly in Germany’s automotive hub. Companies like BMW and Volkswagen have adopted AI for automation, predictive maintenance, and quality control in their manufacturing plants. By streamlining production and fostering innovation in electric and autonomous vehicles, AI has supported job creation in both manufacturing and AI-related fields.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.7.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature Review")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/366416752_Artificial_Intelligence_and_employment_a_systematic_review", link="https://www.researchgate.net/publication/366416752_Artificial_Intelligence_and_employment_a_systematic_review")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.forbes.com/councils/forbesbusinesscouncil/2023/07/26/how-does-artificial-intelligence-create-new-jobs/", link="https://www.forbes.com/councils/forbesbusinesscouncil/2023/07/26/how-does-artificial-intelligence-create-new-jobs/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/377751485_ROLE_OF_ARTIFICIAL_INTELLIGENCE_IN_THE_CREATION_OF_EMPLOYMENT_OPPORTUNITIES", link="https://www.researchgate.net/publication/377751485_ROLE_OF_ARTIFICIAL_INTELLIGENCE_IN_THE_CREATION_OF_EMPLOYMENT_OPPORTUNITIES")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://rudrendupaul.medium.com/ai-powered-economic-forecasting-a-tool-for-economists-and-policy-makers-f1859bd29cb6", link="https://rudrendupaul.medium.com/ai-powered-economic-forecasting-a-tool-for-economists-and-policy-makers-f1859bd29cb6")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.afponline.org/training-resources/resources/articles/Details/the-role-of-ai-in-forecasting-and-where-it-falls-short#:~:text=AI%20algorithms%20are%20based%20on,the%20precision%20of%20its%20forecasts", "https://www.afponline.org/training-resources/resources/articles/Details/the-role-of-ai-in-forecasting-and-where-it-falls-short#:~:text=AI%20algorithms%20are%20based%20on,the%20precision%20of%20its%20forecasts"),
                ".",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RUIZ-REAL, José Luis, URIBE-TORIL, Juan, TORRES, José Antonio, ",
                (s.italic, "et al."),
                " Artificial intelligence in business and economics research: Trends and future. ",
                (s.italic, "Journal of Business Economics and Management"),
                ", 2021, vol. 22, no 1, p. 98-117. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2022.885067/full", link="https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2022.885067/full")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.ecb.europa.eu/press/financial-stability-publications/fsr/special/html/ecb.fsrart202405_02~58c3ce5246.en.html", link="https://www.ecb.europa.eu/press/financial-stability-publications/fsr/special/html/ecb.fsrart202405_02~58c3ce5246.en.html")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Case Study ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Zegami, a startup based in the UK, utilizes AI and machine learning to help businesses visualize and analyze their data. ",
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.insightplatforms.com/platforms/zegami/", "https://www.insightplatforms.com/platforms/zegami/"),
            )
        with lst.item():
            st_write("Tesco, one of the largest supermarket chains in the UK, employs AI-driven predictive analytics to optimize inventory management, forecast demand, and improve customer experience. ")
        with lst.item():
            st_write("The European Central Bank (ECB) has integrated AI into its economic forecasting models to better predict economic growth, inflation, and employment trends across the European Union. ")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.telecomrevieweurope.com/articles/reports-and-coverage/beyond-das-auto-ais-impact-on-the-german-car-industry/", link="https://www.telecomrevieweurope.com/articles/reports-and-coverage/beyond-das-auto-ais-impact-on-the-german-car-industry/")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.7.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Job creation research:"),
                " Investigate AI's potential to create new job opportunities across different sectors in Europe (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Economic forecasting:"),
                " Explore AI models used to predict economic trends and their applications for policymakers (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Support for SMEs:"),
                " Research how AI can help small and medium-sized businesses (SMEs) adapt to post-pandemic challenges (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.8. How, where, why and by whom AI tools should be controlled? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.8.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Examine the need for regulatory frameworks and ethical guidelines to control AI technologies, comparing the roles of governments and private companies.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/Case study ")
    st_write(s.project.doc.paragraphs.p_body, "In May 2019, San Francisco became the first major city in the United States to ban the use of facial recognition technology (FRT) by city agencies. This decision was driven by concerns over privacy, civil liberties, and the potential for racial bias in AI algorithms. The ban highlights the need for regulatory frameworks and ethical guidelines surrounding AI technologies, particularly those used in surveillance.")
    st_write(s.project.doc.paragraphs.p_body + s.project.colors.link_blue, "https://www.nytimes.com/2019/05/14/us/facial-recognition-ban-san-francisco.html", link="https://www.nytimes.com/2019/05/14/us/facial-recognition-ban-san-francisco.html")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.8.2. References and Resources  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature Review  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DALY, Angela, HAGENDORFF, Thilo, HUI, Li, ",
                (s.italic, "et al."),
                " AI, Governance and Ethics: Global Perspectives. 2022. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SIAU, Keng et WANG, Weiyu. Artificial intelligence (AI) ethics: ethics of AI and ethical AI. ",
                (s.italic, "Journal of Database Management (JDM)"),
                ", 2020, vol. 31, no 2, p. 74-87. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://gdpr-info.eu/", link="https://gdpr-info.eu/")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Comparative Analysis ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NANNINI, Luca, BALAYN, Agathe, et SMITH, Adam Leon. Explainability in ai policies: A critical review of communications, reports, regulations, and standards in the eu, us, and uk. In : ",
                (s.italic, "Proceedings of the 2023 ACM conference on fairness, accountability, and transparency"),
                ". 2023. p. 1198-1212. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KUZIEMSKI, Maciej et MISURACA, Gianluca. AI governance in the public sector: Three tales from the frontiers of automated decision-making in democratic settings. ",
                (s.italic, "Telecommunications policy"),
                ", 2020, vol. 44, no 6, p. 101976. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.whitecase.com/insight-our-thinking/ai-watch-global-regulatory-tracker-united-kingdom", link="https://www.whitecase.com/insight-our-thinking/ai-watch-global-regulatory-tracker-united-kingdom")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Legal Framework ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "UZOUGBO, Ngozi Samuel, IKEGWU, Chinonso Gladys, et ADEWUSI, Adefolake Olachi. Legal accountability and ethical considerations of AI in financial services. GSC Advanced Research and Reviews, 2024, vol. 19, no 2, p. 130-142",
                ". ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "HAGENDORFF, Thilo. The ethics of AI ethics: An evaluation of guidelines. ",
                (s.italic, "Minds and machines"),
                ", 2020, vol. 30, no 1, p. 99-120. ",
            )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Ethical guidelines ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.unesco.org/en/artificial-intelligence/recommendation-ethics", link="https://www.unesco.org/en/artificial-intelligence/recommendation-ethics")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.lawfaremedia.org/article/a-comparative-perspective-on-ai-regulation", link="https://www.lawfaremedia.org/article/a-comparative-perspective-on-ai-regulation")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.8.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Literature Review:"),
                " Understanding the basics of AI ethics and law, including key concepts and existing frameworks (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Comparative Analysis:"),
                " Compare different regulatory approaches and their effectiveness in governing AI technologies, focusing on the EU's approach (20 hours).",
            )
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Legal Frameworks:"),
                " Investigate existing and proposed legal frameworks for holding AI systems accountable for their actions (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Ethical Guidelines:"),
                " Explore the ethical guidelines developed for AI, considering cultural differences and the implications of accountability in AI (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Public vs. Private Sector Control"),
                ": Investigate the roles of governments versus private companies in controlling AI technologies.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final Report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.9. Should each country develop its ChatGPT? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.9.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Evaluate whether countries should develop their own language models, considering cultural, economic, and data sovereignty aspects, as well as the balance between collaboration and competition in AI development.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study ")
    st_write(s.project.doc.paragraphs.p_body, "Baidu, one of China's leading technology companies, developed its own generative AI language model called ERNIE (Enhanced Representation through Knowledge Integration). Launched in early 2023, ERNIE Bot was created in response to the growing demand for AI technologies tailored to the Chinese language and cultural context. This case study illustrates the considerations of cultural identity, economic opportunity, and data sovereignty, as well as the balance between collaboration and competition in the global AI landscape.")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.9.2. References and Resources  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Cultural Context Analysis ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://megasisnetwork.medium.com/the-cultural-impact-of-ai-shaping-society-and-identity-03af47bebd41", link="https://megasisnetwork.medium.com/the-cultural-impact-of-ai-shaping-society-and-identity-03af47bebd41")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Case Study  ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.aljazeera.com/economy/2024/4/16/chatgpt-rival-ernie-bot-now-has-200-million-users-chinas-baidu-says", link="https://www.aljazeera.com/economy/2024/4/16/chatgpt-rival-ernie-bot-now-has-200-million-users-chinas-baidu-says")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://en.wikipedia.org/wiki/Ernie_Bot", link="https://en.wikipedia.org/wiki/Ernie_Bot")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://en.wikipedia.org/wiki/Mistral_AI", link="https://en.wikipedia.org/wiki/Mistral_AI")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://mistral.ai/fr/", link="https://mistral.ai/fr/")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Data Sovereignty Investigation ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Data Sovereignty and AI: Challenges and Opportunities.\" ",
                (s.italic, "Computer Law & Security Review. "),
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.brookings.edu/articles/ai-cooperation-on-the-ground-ai-research-and-development-on-a-global-scale/", link="https://www.brookings.edu/articles/ai-cooperation-on-the-ground-ai-research-and-development-on-a-global-scale/")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Collaboration vs Competition ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "\"Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy.\" ",
                (s.italic, "Crown Publishing Group. "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "\"The Global War for Internet Governance.\" ",
                (s.italic, "Yale University Press. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.9.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Cultural context analysis:"),
                " Research how cultural factors influence the development and effectiveness of AI language models in different regions (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Economic impact study:"),
                " Explore the economic considerations of countries creating their own language models compared to using globally developed models (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Data sovereignty investigation:"),
                " Examine issues related to data ownership, privacy, and security in national AI model development (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collaboration vs. competition:"),
                " Analyze the advantages and disadvantages of international cooperation in AI versus nationalistic approaches (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.10. How is AI impacting individual freedom in digital spaces? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.10.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI systems influence or restrict personal freedom, including digital behavior, autonomy, and online expression.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study ")
    st_write(s.project.doc.paragraphs.p_body, "China's Social Credit System, which uses artificial intelligence to monitor, evaluate, and classify the behavior of its citizens and businesses, is a key example of the ethical implications of AI in governance. By collecting and analyzing vast amounts of data, the system tracks activities such as social interactions, financial transactions, and even online behavior, with citizens earning rewards or facing penalties based on their scores.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.10.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://freedomhouse.org/report/freedom-net/2023/repressive-power-artificial-intelligence", link="https://freedomhouse.org/report/freedom-net/2023/repressive-power-artificial-intelligence")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.europarl.europa.eu/RegData/etudes/IDAN/2024/754450/EXPO_IDA(2024)754450_EN.pdf", link="https://www.europarl.europa.eu/RegData/etudes/IDAN/2024/754450/EXPO_IDA(2024)754450_EN.pdf")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://rm.coe.int/cyprus-2020-ai-and-freedom-of-expression/168097fa82", link="https://rm.coe.int/cyprus-2020-ai-and-freedom-of-expression/168097fa82")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://politicsrights.com/ais-impact-on-freedom-of-expression-online/", link="https://politicsrights.com/ais-impact-on-freedom-of-expression-online/")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://aithor.com/essay-examples/the-impact-of-artificial-intelligence-on-human-rights-and-freedoms", link="https://aithor.com/essay-examples/the-impact-of-artificial-intelligence-on-human-rights-and-freedoms")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.10.3. Suggested Steps  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature review on AI's role in social surveillance (15 hours).")
        with lst.item():
            st_write("Investigate the balance between freedom and surveillance in real-world AI applications (15 hours).")
        with lst.item():
            st_write("Analyze legal frameworks like GDPR and their implications on AI surveillance (20 hours).")
        with lst.item():
            st_write("Propose AI development policies ensuring privacy while maintaining security (20 hours).")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_write(s.project.doc.titles.h2, "1.11. How does AI exacerbate or mitigate discrimination? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.11.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI systems might introduce or perpetuate bias and discrimination in different sectors such as hiring, policing, or financial services.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study ")
    st_write(s.project.doc.paragraphs.p_body, "Arguably the most notable example of AI bias is the COMPAS (Correctional Offender Management Profiling for Alternative Sanctions) algorithm used in US court systems to predict the likelihood that a defendant would become a recidivist.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Due to the data that was used, the model that was chosen, and the process of creating the algorithm overall, the model predicted twice as many false positives for recidivism for black offenders (45%) than white offenders (23%).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.11.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature Review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.nature.com/articles/s41599-023-02079-x", link="https://www.nature.com/articles/s41599-023-02079-x")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.chapman.edu/ai/bias-in-ai.aspx", link="https://www.chapman.edu/ai/bias-in-ai.aspx")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "NADEEM, Ayesha, MARJANOVIC, Olivera, ABEDIN, Babak, ",
                (s.italic, "et al."),
                " Gender bias in AI-based decision-making systems: a systematic literature review. ",
                (s.italic, "Australasian Journal of Information Systems"),
                ", 2022, vol. 26. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sap.com/resources/how-ai-can-end-bias", link="https://www.sap.com/resources/how-ai-can-end-bias")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://levity.ai/blog/ai-bias-how-to-avoid", link="https://levity.ai/blog/ai-bias-how-to-avoid")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Case studies ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://datatron.com/real-life-examples-of-discriminating-artificial-intelligence/", link="https://datatron.com/real-life-examples-of-discriminating-artificial-intelligence/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.prolific.com/resources/shocking-ai-bias", link="https://www.prolific.com/resources/shocking-ai-bias")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.techopedia.com/times-ai-bias-caused-real-world-harm", link="https://www.techopedia.com/times-ai-bias-caused-real-world-harm")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.11.3. Suggested Steps  ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Review relevant literature on AI and discrimination (15 hours).")
        with lst.item():
            st_write("Choose a sector for case study (e.g., hiring or criminal justice) (10 hours).")
        with lst.item():
            st_write("Analyze how algorithms might reinforce biases (20 hours).")
        with lst.item():
            st_write("Propose solutions for bias mitigation (15 hours).")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.12. How can AI combat or contribute to misinformation and social manipulation? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.12.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI is both used to spread misinformation (e.g., deepfakes) and how it can be used to counteract it (e.g., misinformation detection tools).")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "Example/case study ",
        "it was revealed that the British consulting firm Cambridge Analytica used data from millions of Facebook users to create psychological profiles. These profiles were then used to target voters with tailored political advertisements, aiming to influence elections. AI-driven data analytics played a crucial role in this manipulation.",
    )
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.12.2. References et Resources ", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://today.ucsd.edu/story/how-ai-can-help-stop-the-spread-of-misinformation", link="https://today.ucsd.edu/story/how-ai-can-help-stop-the-spread-of-misinformation")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.rathenau.nl/en/digitalisering/ai-and-manipulation-social-and-digital-media", link="https://www.rathenau.nl/en/digitalisering/ai-and-manipulation-social-and-digital-media")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://akademie.dw.com/en/generative-ai-is-the-ultimate-disinformation-amplifier/a-68593890", link="https://akademie.dw.com/en/generative-ai-is-the-ultimate-disinformation-amplifier/a-68593890")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ZHOU, Jiawei, ZHANG, Yixuan, LUO, Qianni, ",
                (s.italic, "et al."),
                " Synthetic lies: Understanding ai-generated misinformation and evaluating algorithmic and human solutions. In : ",
                (s.italic, "Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems"),
                ". 2023. p. 1-20. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "FATIMAH, Rafharum, MUMTAZ, Auziah, FAHREZI, Fauzan Muhammad, ",
                (s.italic, "et al."),
                " AI-Generated Misinformation: A Literature Review. ",
                (s.italic, "Indonesian Journal of Artificial Intelligence and Data Mining"),
                ", 2024, vol. 7, no 2, p. 241-254. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://dl.acm.org/doi/abs/10.1145/3581783.3612704", link="https://dl.acm.org/doi/abs/10.1145/3581783.3612704")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.12.3. Suggested steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Literature review on AI’s role in misinformation and social manipulation (10 hours).")
        with lst.item():
            st_write("Analyze a real-world case study, such as the use of deepfakes or AI-driven social media bots (15 hours).")
        with lst.item():
            st_write("Research methods for combating AI-generated misinformation (20 hours).")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.13. How Can AI Facilitate Intercultural Dialogue and Integration in Europe? ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.13.1. Objective ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI can enhance intercultural communication, support community building, and ensure cultural sensitivity in Europe.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Example/case study")
    st_write(s.project.doc.paragraphs.p_body, "Various European initiatives utilize AI technologies to preserve endangered languages. For instance, the \"Living Dictionaries\" project, developed in collaboration with several universities, employs AI to digitize and revitalize languages at risk of extinction.")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.13.2. References and Resources ", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://ieeexplore.ieee.org/document/10438431", link="https://ieeexplore.ieee.org/document/10438431")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/378284156_The_Impact_of_Artificial_Intelligence_on_Language_Translation_A_review", link="https://www.researchgate.net/publication/378284156_The_Impact_of_Artificial_Intelligence_on_Language_Translation_A_review")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://aijourn.com/can-ai-truly-understand-cultural-sensitivity/#:~:text=To%20ensure%20cultural%20accuracy%20and,and%20topics%20for%20specific%20cultures", "https://aijourn.com/can-ai-truly-understand-cultural-sensitivity/#:~:text=To%20ensure%20cultural%20accuracy%20and,and%20topics%20for%20specific%20cultures"),
                ".",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.winyama.com.au/news-room/exploring-ai-cultural-sensitivity-content-diversity", link="https://www.winyama.com.au/news-room/exploring-ai-cultural-sensitivity-content-diversity")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.socialpinpoint.com/ways-to-use-artificial-intelligence-ai-in-community-engagement/", link="https://www.socialpinpoint.com/ways-to-use-artificial-intelligence-ai-in-community-engagement/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.researchgate.net/publication/378043917_AI_for_Social_Good_Leveraging_Artificial_Intelligence_for_Community_Development", link="https://www.researchgate.net/publication/378043917_AI_for_Social_Good_Leveraging_Artificial_Intelligence_for_Community_Development")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://threemagazine.com/ideas/language-headline/", link="https://threemagazine.com/ideas/language-headline/")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.13.3. Suggested Steps ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Language translation study:"),
                " Research how AI tools enhance communication among diverse linguistic groups (20 hours).",
            )
        with lst.item():
            st_write("Understanding the basics of language preservation and revitalization, including the role of AI (15 hours).")
        with lst.item():
            st_write("Researching and creating a database of European languages at risk of extinction (15 hours).")
        with lst.item():
            st_write("Analyzing existing AI initiatives for language preservation in Europe (15 hours).")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Cultural sensitivity analysis:"),
                " Investigate how cultural considerations influence AI technology design for inclusivity (20 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Community engagement:"),
                " Explore AI’s role in fostering community engagement and social cohesion among immigrant populations (15 hours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Final report:"),
                " Report writing (cf. course material)",
            )
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
