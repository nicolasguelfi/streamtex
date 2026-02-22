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
    st_write(s.project.doc.paragraphs.p_md + s.project.colors.burnt_orange + s.bold, "TO BE ADDED DURING THE SESSION ")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_md,
        (s.project.colors.bright_red + s.bold, "Projects presentation slides available "),
        (s.project.doc.links.link_md + s.project.colors.link_blue + s.bold, "HERE", "https://docs.google.com/document/d/1zxFHjG5wKkIbjrATgmZx_mgdgbgngsyADq17Bm7qisw/edit"),
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.1. Projects Overview", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Three types of project  ")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "(TOOL) AI as a Tool in a Startup:"),
                " This focuses on how startups utilize AI technologies to enhance operations, optimize decision-making, and gain competitive advantages. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "(POWER) AI-Powered Product Startups:"),
                " These inquiries center on the development of innovative products that leverage AI to address specific challenges, creating unique value propositions across sectors like healthcare, finance, and education. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "(START) Project About Startup Ideas:"),
                " This area encourages the generation of new startup concepts centered around AI applications, helping entrepreneurs identify emerging opportunities and design impactful solutions. ",
            )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Project titles organized by categories ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Market Trends and Product Development ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Financial Sector  ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Healthcare Sector  ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Sustainability and GreenTech ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "SpaceTech ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Education sector ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Customer Service and Business Operations ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Supply Chain and Logistics ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Intellectual Property and Compliance ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.2. Projects Ideas", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.1. How Can AI Be Used to Predict Market Trends ? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.1.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Analyze how AI can be utilized to predict market trends, providing entrepreneurs with valuable insights into future customer needs, emerging technologies, and industry shifts.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(s.project.doc.paragraphs.p_body, "Tool exploration: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Google Trends"),
                " allows users to analyze search data over time, identifying what topics are trending globally or regionally. By utilizing ",
                (s.bold, "machine learning"),
                " algorithms, entrepreneurs can track changes in consumer interests and predict potential shifts in market demand. For example, a startup might use Google Trends to observe a surge in searches related to eco-friendly products, prompting them to adjust their product line to meet emerging consumer preferences.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "TrendHunter"),
                " specializes in identifying emerging trends through crowd-sourced data, AI analysis, and expert insights using ",
                (s.bold, "natural language processing"),
                " and ",
                (s.bold, "machine learning"),
                ". Startups can utilize this platform to understand consumer behavior and preferences, gaining foresight into potential market disruptions. An example is a fashion startup that uses TrendHunter to anticipate upcoming color palettes and styles, allowing them to design collections that resonate with future customer desires.",
            )
    st_write(s.project.doc.titles.h4, "1.2.1.2. References and Resources", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Literature Review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "UMAMAHESWARI, Dr D. Role of Artificial Intelligence in Marketing Strategies and Performance. ",
                (s.italic, "Migration Letters"),
                ", 2024, vol. 21, no S4, p. 1589-1599. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "OKELEKE, Patrick Azuka, AJIGA, Daniel, FOLORUNSHO, Samuel Olaoluwa, ",
                (s.italic, "et al."),
                " Predictive analytics for market trends using AI: A study in consumer behavior. 2024. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "PRADEEP, A. K., APPEL, Andrew, et STHANUNATHAN, Stan. ",
                (s.italic, "AI for marketing and product innovation: Powerful new tools for predicting trends, connecting with customers, and closing sales"),
                ". John Wiley & Sons, 2018. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BHARADIYA, Jasmin Praful. Machine learning and AI in business intelligence: Trends and opportunities. ",
                (s.italic, "International Journal of Computer (IJC)"),
                ", 2023, vol. 48, no 1, p. 123-134. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "AIKEN, Milam W. et BSAT, Mohammad. Forecasting market trends with neural networks. ",
                (s.italic, "Inf. Syst. Manag."),
                ", 1999, vol. 16, no 4, p. 1-7. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.sciencedirect.com/science/article/pii/S2590291124000615", link="https://www.sciencedirect.com/science/article/pii/S2590291124000615")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://platforce.io/ai-powered-forecasting-use-ai-to-predict-future-market-trends-sales-performance-and-customer-behavior/", link="https://platforce.io/ai-powered-forecasting-use-ai-to-predict-future-market-trends-sales-performance-and-customer-behavior/")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Tools ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://trends.google.com/trends/", link="https://trends.google.com/trends/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.trendhunter.com/", link="https://www.trendhunter.com/")
    st_write(s.project.doc.titles.h4, "1.2.1.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Explore Google Trends and TrendHunter to understand their functionalities and applications in market trend prediction.")
        with lst.item():
            st_write("Research one or more startups or companies that successfully implemented AI tools for market trend analysis and strategy adjustment.")
        with lst.item():
            st_write("Analyze how the companies selected use AI predictions to influence their product development or marketing strategies.")
        with lst.item():
            st_write("Discuss the risks and benefits of relying on AI-driven market predictions, including potential pitfalls.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.2. How Can AI Drive Product Development? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.2.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI can assist in product design and development by analyzing customer data, improving product features, and predicting future product trends.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/ Example ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "A notable AI tool for product development is ",
        (s.bold, "Autodesk’s Dreamcatcher"),
        ". This generative design software allows companies to input specific design goals and constraints, automating and optimizing the design process. For instance, a furniture manufacturer might use Dreamcatcher to create ergonomic chair designs that meet specific aesthetic and functional requirements, significantly reducing the design cycle time.The primary AI technology behind Dreamcatcher is ",
        (s.bold, "generative design"),
        ", which utilizes ",
        (s.bold, "optimization algorithms"),
        " and ",
        (s.bold, "machine learning"),
        " to explore various design possibilities.",
    )
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "One prominent example is ",
        (s.bold, "Nike"),
        ", which employs AI in various aspects of product development, particularly in shoe design. By using AI algorithms to analyze customer preferences and performance data, Nike has developed innovative features that enhance comfort and functionality. For example, their ",
        (s.bold, "Nike By You"),
        " customization platform uses AI to suggest designs based on consumer data, allowing customers to create personalized footwear that meets their specific needs.",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "Nike's AI systems rely on ",
        (s.bold, "deep learning"),
        " for analyzing customer preferences and performance data. Specifically, they might use ",
        (s.bold, "natural language processing (NLP)"),
        " for processing customer feedback and ",
        (s.bold, "computer vision"),
        " for analyzing and optimizing shoe designs.",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "1.2.2.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.autodesk.com/", link="https://www.autodesk.com/")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "OGUNDIPE, Damilola Oluwaseun, BABATUNDE, Sodiq Odetunde, et ABAKU, Emmanuel Adeyemi. AI and product management: A theoretical overview from idea to market. ",
                (s.italic, "International Journal of Management & Entrepreneurship Research"),
                ", 2024, vol. 6, no 3, p. 950-969. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.businessinsider.com/nikes-designs-of-the-future-2016-4", link="https://www.businessinsider.com/nikes-designs-of-the-future-2016-4")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MARSHALL, Anthony, BIECK, Christian, DENCIK, Jacob, ",
                (s.italic, "et al."),
                " How generative AI will drive enterprise innovation. ",
                (s.italic, "Strategy & Leadership"),
                ", 2024, vol. 52, no 1, p. 23-28. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LIU, Chenang, TIAN, Wenmeng, et KAN, Chen. When AI meets additive manufacturing: Challenges and emerging opportunities for human-centered products development. ",
                (s.italic, "Journal of Manufacturing Systems"),
                ", 2022, vol. 64, p. 648-656. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GUJAR, Praveen, PANYAM, Sriram, et PALIWAL, Gunjan. AI Integrated Product Development: Building Sustainable Competitive Advantage. ",
                (s.italic, "IEEE Engineering Management Review"),
                ", 2024. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.delve.com/insights/how-collaborating-with-ai-is-transforming-product-development", link="https://www.delve.com/insights/how-collaborating-with-ai-is-transforming-product-development")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://sloanreview.mit.edu/article/when-generative-ai-meets-product-development/", link="https://sloanreview.mit.edu/article/when-generative-ai-meets-product-development/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.leewayhertz.com/ai-in-product-development/", link="https://www.leewayhertz.com/ai-in-product-development/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.virtasant.com/ai-today/ai-in-product-development-netflix-bmw", link="https://www.virtasant.com/ai-today/ai-in-product-development-netflix-bmw")
    st_write(s.project.doc.titles.h4, "1.2.2.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Review Autodesk’s Dreamcatcher and similar AI tools for product design.")
        with lst.item():
            st_write("Select one or more companies that have utilized AI in product development (e.g., Nike) and analyze how AI has improved their product design process.")
        with lst.item():
            st_write("Examine how AI impacts product features and development timelines, focusing on specific innovations introduced by the selected company.")
        with lst.item():
            st_write("Facilitate a discussion on AI's role in creativity and its implications for competition and innovation in product development.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_write(s.project.doc.titles.h3, "1.2.3. How Can AI Help Entrepreneurs Identify Funding Opportunities? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.3.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI tools can assist entrepreneurs in identifying funding opportunities, predicting investor interest, and optimizing pitch strategies for venture capital.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(s.project.doc.paragraphs.p_body, "Funding Platforms Exploration:")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Crunchbase"),
                " provides extensive information about businesses, investors, and funding rounds. By leveraging ",
                (s.bold, "machine learning"),
                " algorithms, it analyzes historical data and patterns in investor behavior, enabling startups to identify potential investors that align with their business model and funding needs. For instance, startups can find investors based on industry focus, previous investments, and funding amounts, which helps tailor their approach and pitch effectively.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Clearco"),
                " (formerly Clearbanc) specializes in revenue-based financing for startups, particularly in the e-commerce and SaaS sectors. Its ",
                (s.bold, "AI algorithms"),
                " assess a startup's financial health by analyzing growth metrics and revenue patterns. It uses ",
                (s.bold, "machine learning"),
                " to offer funding based on future sales projections without taking equity. Startups using Clearco have been able to secure fast, data-driven funding that aligns with their growth trajectories, allowing them to scale without diluting ownership.",
            )
    st_write(s.project.doc.titles.h4, "1.2.3.2. References and Resources", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Literature Review ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SHEPHERD, Dean A. et MAJCHRZAK, Ann. Machines augmenting entrepreneurs: Opportunities (and threats) at the Nexus of artificial intelligence and entrepreneurship. ",
                (s.italic, "Journal of Business Venturing"),
                ", 2022, vol. 37, no 4, p. 106227. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TUNG, Tran Minh, OANH, Vo Thi Kim, CUC, Tran Thi Kim, ",
                (s.italic, "et al."),
                " AI-Powered Innovation: How Entrepreneurs Can Leverage Artificial Intelligence for Business Success. ",
                (s.italic, "NATURALISTA CAMPANO"),
                ", 2024, vol. 28, no 1, p. 605-618. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GIUGGIOLI, Guglielmo et PELLEGRINI, Massimiliano Matteo. Artificial intelligence as an enabler for entrepreneurs: a systematic literature review and an agenda for future research. ",
                (s.italic, "International Journal of Entrepreneurial Behavior & Research"),
                ", 2023, vol. 29, no 4, p. 816-837. ",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Tools")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.crunchbase.com/", link="https://www.crunchbase.com/")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://clear.co/", link="https://clear.co/")
    st_write(s.project.doc.titles.h4, "1.2.3.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Explore how Crunchbase and Clearco or other platforms utilize AI for investor matching and revenue-based funding.")
        with lst.item():
            st_write("Research one or more successful startups that have leveraged these platforms to secure funding.")
        with lst.item():
            st_write("Analyze the role of AI-driven insights in improving the startup's pitch strategies and investor relations.")
        with lst.item():
            st_write("Discuss potential biases in AI algorithms and their impact on funding access for minority or underrepresented founders.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.4. How FinTech Startups Develop AI-Powered Products for Enhancing Financial Security and Asset Management? (POWER)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.4.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Analyze how FinTech startups develop AI-powered products specifically designed to enhance digital payments, prevent fraud, and optimize asset management, catering to the evolving needs of financial institutions.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Tokeny Solutions (2017) ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Tokeny Solutions developed an AI-powered blockchain platform designed to secure digital assets by leveraging ",
        (s.bold, "machine learning"),
        " for real-time fraud detection. Their product enhances trust and transparency in digital payments, especially for financial institutions dealing with tokenized assets.",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Governance.com")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Governance.com developed a governance platform powered by AI that helps asset managers optimize operations. The platform uses ",
        (s.bold, "machine learning algorithms"),
        " to track regulatory changes and monitor investment portfolios, providing actionable insights that streamline compliance and risk management for startups.",
    )
    st_write(s.project.doc.titles.h4, "1.2.4.2. References and Resources ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHIKRI, HASSAN et KASSOU, MANAR. FINANCIAL REVOLUTION: INNOVATION POWERED BY FINTECH AND ARTIFICIAL INTELLIGENCE. ",
                (s.italic, "Journal of Theoretical and Applied Information Technology"),
                ", 2024, vol. 102, no 9. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RAJPUT, Rohan Singh, DHONI, Pan Singh, PATEL, Ritesh, ",
                (s.italic, "et al."),
                " ",
                (s.italic, "AI-Driven Innovations"),
                ". Cari Journals USA LLC, 2024. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BHATNAGAR, Sumit et MAHANT, Roshan. Unleashing the Power of AI in Financial Services: Opportunities, Challenges, and Implications. ",
                (s.italic, "Artificial Intelligence (AI)"),
                ", 2024, vol. 4, no 1. ",
            )
        with lst.item():
            st_write("WADHWA, Vanshika et KUMAR, D. Sathish. ROLE AND IMPACT OF AI IN FINTECH INDUSTRY. ")
        with lst.item():
            st_write("BANDARU, Adithya Nandan Naidu. Strategic Insights into AI-Driven Financial Services with a Focus on Opportunities and Challenges for Emerging Fintech Ventures. ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SHARMA, GARGI, SOLANKI, UMESH, et SOLANKI, VIKAS. Fintech and Artificial Intelligence: An Overview of Contribution to Banking, Investment, Financial Education, and Microfinance. ",
                (s.italic, "Applications of Artificial Intelligence in Business and Finance 5.0"),
                ", 2024. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://neontri.com/blog/artificial-intelligence-fintech/#:~:text=AI%20systems%20continuously%20monitor%20network,information%20and%20maintaining%20customer%20trust", "https://neontri.com/blog/artificial-intelligence-fintech/#:~:text=AI%20systems%20continuously%20monitor%20network,information%20and%20maintaining%20customer%20trust"),
                ". ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://startups.epam.com/blog/ai-in-fintech", link="https://startups.epam.com/blog/ai-in-fintech")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://impressit.io/blog/ai-in-fintech", link="https://impressit.io/blog/ai-in-fintech")
    st_write(s.project.doc.titles.h4, "1.2.4.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research the Role of AI in FinTech: Investigate the applications of AI in enhancing digital payments, fraud prevention, and asset management within the FinTech sector.")
        with lst.item():
            st_write("Analyze Case Studies: Examine the AI-powered platforms developed by Tokeny Solutions and Governance.com or other startups, focusing on their features, functionalities, and the types of AI utilized.")
        with lst.item():
            st_write("Evaluate Impact on Financial Operations: Explore how these AI products improve the efficiency and effectiveness of financial operations, including their role in regulatory compliance and risk management.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.5. What is a good startup project for an AI-powered product in the finance sector? (START)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.5.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate the potential of AI-powered products in the finance sector to enhance services like fraud detection, risk management, and personalized banking.")
    st_write(s.project.doc.titles.h4, "1.2.5.2. Ideas Related to the Finance Sector", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI for Fraud Detection: Developing systems that analyze transactions in real-time to detect and prevent fraudulent activity.")
        with lst.item():
            st_write("AI Credit Scoring: Creating algorithms that assess creditworthiness using non-traditional data points.")
        with lst.item():
            st_write("AI for Risk Assessment: Building tools that assess the risk of investment portfolios using predictive analytics.")
        with lst.item():
            st_write("Robo-Advisors: Automated investment platforms that provide personalized investment advice based on user preferences.")
        with lst.item():
            st_write("Personal Finance Management Tools: Apps that use AI to help users budget and save based on their spending habits.")
        with lst.item():
            st_write("AI for Customer Service: Chatbots that assist customers with inquiries about banking services 24/7.")
        with lst.item():
            st_write("Sentiment Analysis for Investment: Tools that analyze social media and news sentiment to predict stock movements.")
        with lst.item():
            st_write("AI in Compliance Monitoring: Automating regulatory compliance checks using AI to identify potential violations.")
        with lst.item():
            st_write("Predictive Analytics for Loan Approval: Using AI to predict the likelihood of loan repayment for applicants.")
        with lst.item():
            st_write("AI-Powered Wealth Management: Personalized wealth management services that adjust based on market conditions and user goals.")
    st_write(s.project.doc.titles.h4, "1.2.5.3. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DEVAN, Munivel, PRAKASH, Sanjeev, et JANGOAN, Suhas. Predictive maintenance in banking: leveraging AI for real-time data analytics. ",
                (s.italic, "Journal of Knowledge Learning and Science Technology ISSN: 2959-6386 (online)"),
                ", 2023, vol. 2, no 2, p. 483-490. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MARGARET, D. Sheela, ELANGOVAN, N., BALAJI, Vedha, ",
                (s.italic, "et al."),
                " The influence and impact of AI-powered intelligent assistance for banking services. In : ",
                (s.italic, "International Conference on Emerging Trends in Business and Management (ICETBM 2023)"),
                ". Atlantis Press, 2023. p. 374-385. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MORI, Margherita. AI-powered virtual assistants in the realms of banking and financial services. ",
                (s.italic, "Virtual assistant"),
                ", 2021, vol. 1, p. 65-93. ",
            )
        with lst.item():
            st_write(s.bold, "Fraud Detection")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "AI Credit scoring")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Robot Advisor")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Risk Assessment")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Sentiment Analysis for Investment ")
        with lst.item():
            pass
    st_write(s.project.doc.titles.h4, "1.2.5.4. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Define a new service in the finance sector: Identify a pressing need or gap in financial services that could be addressed with an AI-powered solution.")
        with lst.item():
            st_write("Design an AI-based idea to provide this service: Develop a concept for how AI can be leveraged to offer this new financial service, such as fraud detection, credit scoring, or wealth management.")
        with lst.item():
            st_write("Conduct a market analysis: Research the potential market for this service, including target customers, competitors, and the overall demand.")
        with lst.item():
            st_write("Present the product requirements: Outline the key requirements of the AI-powered product, detailing its features, performance goals, and user expectations.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_write(s.project.doc.titles.h3, "1.2.6. How Companies Develop AI-Powered Products for the Healthcare Sector? (POWER)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.6.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how startups develop AI-powered products to revolutionize healthcare by improving patient diagnosis, personalized treatment, medical research, and operational efficiencies in healthcare systems.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(s.project.doc.paragraphs.p_body, "Owkin (2020):")
    st_write(
        s.project.doc.paragraphs.p_body,
        "A French-American startup leveraging AI to accelerate drug discovery and improve cancer diagnostics. By analyzing patient data with ",
        (s.bold, "machine learning models"),
        ", they provide insights into treatment efficacy and disease progression.",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Kahun (2021):")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Kahun developed an AI-powered clinical assistant that uses medical literature to help doctors make evidence-based diagnoses. The tool integrates with electronic health records and supports real-time decision-making in hospitals through the application of ",
        (s.bold, "machine learning"),
        ".",
    )
    st_write(s.project.doc.titles.h4, "1.2.6.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOHR, Adam et MEMARZADEH, Kaveh. The rise of artificial intelligence in healthcare applications. In : ",
                (s.italic, "Artificial Intelligence in healthcare"),
                ". Academic Press, 2020. p. 25-60. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DAVENPORT, Thomas et KALAKOTA, Ravi. The potential for artificial intelligence in healthcare. ",
                (s.italic, "Future healthcare journal"),
                ", 2019, vol. 6, no 2, p. 94-98. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOHR, Adam et MEMARZADEH, Kaveh (ed.). ",
                (s.italic, "Artificial intelligence in healthcare"),
                ". Academic Press, 2020. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LAU, Annie YS, STACCINI, Pascal, ",
                (s.italic, "et al."),
                " Artificial intelligence in health: new opportunities, challenges, and practical implications. ",
                (s.italic, "Yearbook of medical informatics"),
                ", 2019, vol. 28, no 01, p. 174-178. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BAJWA, Junaid, MUNIR, Usman, NORI, Aditya, ",
                (s.italic, "et al."),
                " Artificial intelligence in healthcare: transforming the practice of medicine. ",
                (s.italic, "Future healthcare journal"),
                ", 2021, vol. 8, no 2, p. e188-e194. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SUN, George et ZHOU, Yi-Hui. AI in healthcare: navigating opportunities and challenges in digital communication. ",
                (s.italic, "Frontiers in Digital Health"),
                ", 2023, vol. 5, p. 1291132. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BAIRAGYA, Devyani, TRIPATHY, Hrudaya Kumar, BHOI, Akash Kumar, ",
                (s.italic, "et al."),
                " Impact of artificial intelligence in health care: A study. ",
                (s.italic, "Hybrid Artificial Intelligence and IoT in Healthcare"),
                ", 2021, p. 311-328. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://medium.com/datatobiz/top-5-companies-developing-ai-products-in-healthcare-5f7f006aed63", link="https://medium.com/datatobiz/top-5-companies-developing-ai-products-in-healthcare-5f7f006aed63")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare", link="https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare")
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
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://builtin.com/artificial-intelligence/artificial-intelligence-healthcare", link="https://builtin.com/artificial-intelligence/artificial-intelligence-healthcare")
    st_write(s.project.doc.titles.h4, "1.2.6.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Investigate AI in Healthcare: Explore the various applications of AI in healthcare, focusing on areas such as diagnosis, treatment personalization, and operational efficiency.")
        with lst.item():
            st_write("Examine Case Studies: Analyze AI-powered products from selected companies, noting their development processes and the technologies employed.")
        with lst.item():
            st_write("Assess Impact: Evaluate the effects of these AI products on healthcare outcomes, including improvements in patient care and operational effectiveness.")
        with lst.item():
            st_write("Report writing (cf. course material)")
    st_write(s.project.doc.titles.h3, "1.2.7. What is a good startup project for an AI-powered product in the healthcare sector? (START)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.7.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "The goal is to explore how AI-powered products can be developed to solve pressing challenges in healthcare, such as diagnostics, personalized medicine, or remote patient monitoring.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "3.8.2 Ideas Related to Healthcare sector ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI for predictive healthcare: Developing AI systems that predict patient health risks based on medical data.")
        with lst.item():
            st_write("AI for Medical Imaging: AI-powered image analysis to detect diseases from scans (e.g., cancer detection).")
        with lst.item():
            st_write("AI for Drug Discovery: Accelerating the process of drug development by analyzing biological data to identify potential compounds.")
        with lst.item():
            st_write("AI for Remote Health Monitoring: Products that use AI to monitor patients in real-time, enabling early intervention.")
        with lst.item():
            st_write("AI Virtual Health Assistants: Building chatbots that provide patients with personalized health advice based on their symptoms.")
        with lst.item():
            st_write("AI in Mental Health: Developing AI tools that analyze speech or text data to assess mental health conditions and provide resources.")
        with lst.item():
            st_write("AI-Enhanced Telemedicine: Platforms that utilize AI to triage patients based on symptoms before they meet with healthcare providers.")
        with lst.item():
            st_write("AI for Personalized Treatment Plans: Using AI to analyze patient data and develop customized treatment protocols.")
        with lst.item():
            st_write("AI for Administrative Automation: Automating repetitive administrative tasks in healthcare settings to improve efficiency.")
        with lst.item():
            st_write("AI for Health Education: Creating personalized educational platforms that use AI to tailor content based on patient learning styles.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example ")
    st_write(s.project.doc.paragraphs.p_body, "Healx (Founded in 2021): Healx leverages AI to identify new drug therapies for rare diseases by analyzing vast biomedical datasets to speed up drug discovery and bring treatments to market faster.")
    st_write(s.project.doc.titles.h4, "1.2.7.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOHR, Adam et MEMARZADEH, Kaveh. The rise of artificial intelligence in healthcare applications. In : ",
                (s.italic, "Artificial Intelligence in healthcare"),
                ". Academic Press, 2020. p. 25-60. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DAVENPORT, Thomas et KALAKOTA, Ravi. The potential for artificial intelligence in healthcare. ",
                (s.italic, "Future healthcare journal"),
                ", 2019, vol. 6, no 2, p. 94-98. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOHR, Adam et MEMARZADEH, Kaveh (ed.). ",
                (s.italic, "Artificial intelligence in healthcare"),
                ". Academic Press, 2020. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LAU, Annie YS, STACCINI, Pascal, ",
                (s.italic, "et al."),
                " Artificial intelligence in health: new opportunities, challenges, and practical implications. ",
                (s.italic, "Yearbook of medical informatics"),
                ", 2019, vol. 28, no 01, p. 174-178. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BAJWA, Junaid, MUNIR, Usman, NORI, Aditya, ",
                (s.italic, "et al."),
                " Artificial intelligence in healthcare: transforming the practice of medicine. ",
                (s.italic, "Future healthcare journal"),
                ", 2021, vol. 8, no 2, p. e188-e194. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SUN, George et ZHOU, Yi-Hui. AI in healthcare: navigating opportunities and challenges in digital communication. ",
                (s.italic, "Frontiers in Digital Health"),
                ", 2023, vol. 5, p. 1291132. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BAIRAGYA, Devyani, TRIPATHY, Hrudaya Kumar, BHOI, Akash Kumar, ",
                (s.italic, "et al."),
                " Impact of artificial intelligence in health care: A study. ",
                (s.italic, "Hybrid Artificial Intelligence and IoT in Healthcare"),
                ", 2021, p. 311-328. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://medium.com/datatobiz/top-5-companies-developing-ai-products-in-healthcare-5f7f006aed63", link="https://medium.com/datatobiz/top-5-companies-developing-ai-products-in-healthcare-5f7f006aed63")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare", link="https://www.techtarget.com/healthtechanalytics/feature/Top-12-ways-artificial-intelligence-will-impact-healthcare")
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
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://builtin.com/artificial-intelligence/artificial-intelligence-healthcare", link="https://builtin.com/artificial-intelligence/artificial-intelligence-healthcare")
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
    st_write(s.project.doc.titles.h4, "1.2.7.3. Suggested Steps", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Define a new healthcare service: Identify a healthcare need that can be addressed with AI, such as improving diagnostics, enhancing personalized treatments, or optimizing remote patient monitoring.")
        with lst.item():
            st_write("Develop an AI-based idea: Create an AI-powered solution that provides this new healthcare service, such as an AI-driven diagnostic tool or an AI-based health monitoring system.")
        with lst.item():
            st_write("Conduct a market analysis: Research existing healthcare solutions, competitors, and the potential demand for your AI-powered product.")
        with lst.item():
            st_write("Present the product requirements: Outline the key specifications and features needed to develop the AI-powered product, including technical and functional requirements.")
        with lst.item():
            st_write("Report writing (cf. course material)")
    st_write(s.project.doc.titles.h3, "1.2.8. How GreenTech Startups Develop AI-Powered Products to Enhance Sustainability and Resource Efficiency? (POWER)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.8.1. Objective ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how GreenTech startups develop AI-powered products that improve energy consumption management, water resource optimization, and environmental sustainability.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/ Example")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Luxsense ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Luxsense develops an AI-driven energy management system that optimizes energy usage in buildings. Their product uses ",
        (s.bold, "machine learning"),
        " to predict energy demands and adjust consumption, allowing businesses to lower energy waste and reduce their environmental impact.",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "APATEQ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "APATEQ develops an AI-powered water purification system that optimizes water treatment processes. Their AI algorithms utilize ",
        (s.bold, "machine learning"),
        " to analyze water quality in real-time and adjust treatment methods, enabling startups to manage water resources more efficiently and sustainably.",
    )
    st_write(s.project.doc.titles.h4, "1.2.8.2. References and Resources ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MOHAMMADI LANBARAN, Naiyer, NAUJOKAITIS, Darius, KAIRAITIS, Gediminas, ",
                (s.italic, "et al."),
                " Overview of Startups Developing Artificial Intelligence for the Energy Sector. ",
                (s.italic, "Applied Sciences"),
                ", 2024, vol. 14, no 18, p. 8294. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ELIAS, Oluwafemi, AWOTUNDE, Opeyemi Joseph, OLADEPO, Oladiipo Ishola, ",
                (s.italic, "et al."),
                " The evolution of green fintech: Leveraging AI and IoT for sustainable financial services and smart contract implementation. ",
                (s.italic, "World Journal of Advanced Research and Reviews"),
                ", 2024, vol. 23, no 1, p. 2710-2723. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RENZETTI, Carlo. ",
                (s.italic, "Machine learning technologies in the greentech industry: a case study"),
                ". 2024. Thèse de doctorat. Instituto Superior de Economia e Gestão. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "SALEHI, Majid. Climate Crusaders: The Top 5 Innovators in the Climate Change Battle. ",
                (s.italic, "Available at SSRN 4431536"),
                ", 2023. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "JORZIK, Philip, ANTONIO, Jerome L., KANBACH, Dominik K., ",
                (s.italic, "et al."),
                " Sowing the seeds for sustainability: A business model innovation perspective on artificial intelligence in green technology startups. ",
                (s.italic, "Technological forecasting and social change"),
                ", 2024, vol. 208, p. 123653. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "APPIO, Francesco Paolo, PLATANIA, Federico, et HERNANDEZ, Celina Toscano. Pairing AI and Sustainability: Envisioning Entrepreneurial Initiatives for Virtuous Twin Paths. ",
                (s.italic, "IEEE Transactions on Engineering Management"),
                ", 2024. ",
            )
    st_write(s.project.doc.titles.h4, "1.2.8.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research the applications of AI in enhancing sustainability and resource efficiency across various sectors, including energy, water management, and waste reduction.")
        with lst.item():
            st_write("Examine the AI-powered solutions developed by Luxsense and APATEQ or other companies. Assess their methodologies, technologies used, and the specific sustainability challenges they address.")
        with lst.item():
            st_write("Analyze the tangible benefits of these AI solutions, focusing on energy consumption reduction, water resource optimization, and overall environmental sustainability. Consider metrics such as energy savings, cost reduction, and improved resource management.")
        with lst.item():
            st_write("Discuss how these innovations contribute to the larger goals of sustainability and environmental stewardship, including their potential to influence industry practices and consumer behavior.")
        with lst.item():
            st_write("Report writing (cf. course material)")
    st_write(s.project.doc.titles.h3, "1.2.9. What is a good startup project for an AI-powered product in the GreenTech sector? (START)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.9.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Investigate how AI-powered products can contribute to sustainability, enhance energy efficiency, and promote environmental conservation within the GreenTech sector.")
    st_write(s.project.doc.titles.h4, "1.2.9.2. Ideas related to the GreenTech sector", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI for Energy Management: Systems that optimize energy usage in buildings through real-time data analysis.")
        with lst.item():
            st_write("AI-Powered Waste Management: Tools that analyze waste patterns to improve recycling and waste disposal processes.")
        with lst.item():
            st_write("AI for Renewable Energy Forecasting: Predictive tools for energy production from renewable sources like solar and wind.")
        with lst.item():
            st_write("AI in Sustainable Agriculture: Applications that monitor crop health and optimize resource usage in farming.")
        with lst.item():
            st_write("AI for Carbon Footprint Tracking: Tools that help individuals and businesses calculate and reduce their carbon emissions.")
        with lst.item():
            st_write("AI for Water Management: Systems that monitor water quality and usage to promote conservation.")
        with lst.item():
            st_write("AI-Powered Eco-Friendly Transportation: Solutions that optimize route planning for reduced fuel consumption.")
        with lst.item():
            st_write("AI for Environmental Monitoring: Tools that analyze environmental data for conservation efforts and regulatory compliance.")
    st_write(s.project.doc.titles.h4, "1.2.9.3. References and Resources", tag=t.h4)
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
            st_write(
                s.project.doc.paragraphs.p_body,
                "KAACK, Lynn H., DONTI, Priya L., STRUBELL, Emma, ",
                (s.italic, "et al."),
                " Aligning artificial intelligence with climate change mitigation. ",
                (s.italic, "Nature Climate Change"),
                ", 2022, vol. 12, no 6, p. 518-527. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ADERIBIGBE, Adebayo Olusegun, ANI, Emmanuel Chigozie, OHENHEN, Peter Efosa, ",
                (s.italic, "et al."),
                " Enhancing energy efficiency with ai: a review of machine learning models in electricity demand forecasting. ",
                (s.italic, "Engineering Science & Technology Journal"),
                ", 2023, vol. 4, no 6, p. 341-356.",
            )
        with lst.item():
            st_write("Climate monitoring ")
        with lst.item():
            pass
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Renewable energy management ")
        with lst.item():
            pass
    st_write(s.project.doc.titles.h4, "1.2.9.4. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Define a new service in GreenTech: Identify a specific need within the GreenTech sector that can promote sustainability, energy efficiency, or environmental conservation. ")
        with lst.item():
            st_write("Develop an AI-based idea: Design an AI-powered service that addresses the chosen GreenTech need. ")
        with lst.item():
            st_write("Conduct a market analysis: Research existing GreenTech solutions and competitors, and analyze the demand for AI-powered products in the sustainability space.")
        with lst.item():
            st_write("Present the product requirements: Detail the product's requirements, including specific features and capabilities needed to deliver the AI-based service effectively.")
        with lst.item():
            st_write("Report writing (cf. course material)")
    st_write(s.project.doc.titles.h3, "1.2.10. How SpaceTech Startups Develop AI-Powered Products? (POWER)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.10.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how SpaceTech startups leverage AI technologies to create innovative products that improve satellite data analysis, enhance communication systems, and optimize various aspects of space missions.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Spire Global")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Spire Global develops AI-powered systems to process vast amounts of satellite data for weather forecasting, ship tracking, and aviation monitoring. Their AI algorithms, which primarily use ",
        (s.bold, "machine learning"),
        ", streamline data analysis and enhance the accuracy of satellite-based services, contributing to space exploration and defense sectors.",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Kleos Space")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Kleos Space develops AI-driven geospatial analysis tools to enhance satellite communication and defense applications. Their AI products utilize ",
        (s.bold, "machine learning"),
        " to analyze satellite data in real-time, offering improved accuracy and speed for space intelligence and communication systems.",
    )
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "Guoxing Aerospace Technology, based in Chengdu, China, builds satellites with AI technology for autonomous decision-making about which photos or data to collect and how to proceed. Their systems employ ",
        (s.bold, "machine learning"),
        " to optimize the data collection process.",
    )
    st_write(s.project.doc.titles.h4, "1.2.10.2. References and Resources ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://spire.com/", link="https://spire.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://kleos.space/", link="https://kleos.space/")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "BOUCETTA, Anfal Yousra, BAZIZ, Meriem, HAMDAD, Leila, ",
                (s.italic, "et al."),
                " Optimizing for Edge-AI Based Satellite Image Processing: A Survey of Techniques. In : ",
                (s.italic, "2024 IEEE Mediterranean and Middle-East Geoscience and Remote Sensing Symposium (M2GARSS)"),
                ". IEEE, 2024. p. 83-87. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "GHIGLIONE, Max et SERRA, Vittorio. Opportunities and challenges of ai on satellite processing units. In : ",
                (s.italic, "Proceedings of the 19th ACM international conference on computing Frontiers"),
                ". 2022. p. 221-224. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MADI, Matteo et SOKOLOVA, Olga (ed.). ",
                (s.italic, "Artificial Intelligence for Space: AI4SPACE: Trends, Applications, and Perspectives"),
                ". CRC Press, 2023. ",
            )
        with lst.item():
            st_write("HOSLI, Allisha V. Navigating the Legal Complexities of Artificial Intelligence in Outer Space. ")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://aict-hub.co/wp-content/uploads/2024/08/Space-tech-booklet.pdf", link="https://aict-hub.co/wp-content/uploads/2024/08/Space-tech-booklet.pdf")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.restack.io/p/ai-for-space-exploration-answer-emerging-space-tech-startups-cat-ai", link="https://www.restack.io/p/ai-for-space-exploration-answer-emerging-space-tech-startups-cat-ai")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.linkedin.com/pulse/6-ai-space-startups-you-should-know-what-can-leverage-fl%C3%BCckiger", link="https://www.linkedin.com/pulse/6-ai-space-startups-you-should-know-what-can-leverage-fl%C3%BCckiger")
    st_write(s.project.doc.titles.h4, "1.2.10.3. Suggested Steps  ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Investigate AI Applications: Explore how AI is leveraged across various SpaceTech domains, including data analysis, communication systems, and mission optimization.")
        with lst.item():
            st_write("Analyze Case Studies: Examine the AI-powered products from companies like Spire Global and Kleos Space, focusing on their technologies and the challenges they address.")
        with lst.item():
            st_write("Evaluate Impact: Assess the improvements these AI products bring to space operations, including efficiency, accuracy, and decision-making.")
        with lst.item():
            st_write("Report writing (cf. course material) ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.11. What is a good startup project for an AI-powered product in the education sector? (START)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.11.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine the application of AI-powered products in the education sector to enhance learning experiences, personalize education, and improve administrative efficiency.")
    st_write(s.project.doc.titles.h4, "1.2.11.2. Ideas related to the Education sector", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("AI-Powered Tutoring Systems: Personalized tutoring platforms that adapt to individual learning styles and paces.")
        with lst.item():
            st_write("AI for Curriculum Development: Tools that analyze student performance data to help educators tailor curriculum content.")
        with lst.item():
            st_write("AI for Student Assessment: Automated grading systems that use AI to provide more objective assessments of student work.")
        with lst.item():
            st_write("Virtual Classrooms: Platforms that integrate AI to enhance remote learning experiences with interactive tools.")
        with lst.item():
            st_write("AI-Based Language Learning Apps: Applications that use AI to provide personalized language learning experiences.")
        with lst.item():
            st_write("AI for Predictive Analytics in Education: Systems that predict student success and identify at-risk students.")
        with lst.item():
            st_write("AI in Special Education: Tools that support learning for students with disabilities through personalized content and pacing.")
        with lst.item():
            st_write("Career Guidance Systems: AI-powered platforms that match students with potential career paths based on their skills and interests.")
    st_write(s.project.doc.titles.h4, "1.2.11.3. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHARLES, Frank. AI-powered personalized mobile education for New Zealand students. ",
                (s.italic, "International Journal Software Engineering and Computer Science (IJSECS)"),
                ", 2023, vol. 3, no 1, p. 33-39. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RAZAK, Abdul, NAYAK, M. Pandya, MANOHARAN, Geetha, ",
                (s.italic, "et al."),
                " Reigniting the power of artificial intelligence in education sector for the educators and students competence. In : ",
                (s.italic, "Artificial Intelligence and Machine Learning in Smart City Planning"),
                ". Elsevier, 2023. p. 103-116. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LIMNA, Pongsakorn, JAKWATANATHAM, Somporch, SIRIPIPATTANAKUL, Sutithep, ",
                (s.italic, "et al."),
                " A review of artificial intelligence (AI) in education during the digital era. ",
                (s.italic, "Advance Knowledge for Executives"),
                ", 2022, vol. 1, no 1, p. 1-9. ",
            )
        with lst.item():
            st_write(s.bold, "AI-Powered Tutoring Systems")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "AI for student assessment")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Virtual Classrooms")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "AI-based Language learning")
        with lst.item():
            pass
    st_write(s.project.doc.titles.h4, "1.2.11.4. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Define a new service in education: Identify a key educational challenge that can be addressed using AI-powered solutions. ")
        with lst.item():
            st_write("Develop an AI-based idea: Design an AI-powered service that meets the identified educational need.")
        with lst.item():
            st_write("Conduct a market analysis: Research existing AI solutions in education, analyze competitors, and evaluate the demand for personalized education and AI-enhanced administrative efficiency.")
        with lst.item():
            st_write("Present the product requirements: Specify the product's features, functionality, and technical aspects to deliver a successful AI-powered educational solution.")
        with lst.item():
            st_write("Report writing (cf. course material)")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.12. How EdTech Companies Develop AI-Powered Products to Enhance Education? (POWER)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.12.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how startups and companies leverage AI to create products that enhance various aspects of education, such as curriculum development, assessment, student engagement, and accessibility.")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Case Study/Example ")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Riiid Labs (2020)"),
        "Riiid Labs, an AI education company, developed a personalized learning platform using  ",
        (s.bold, "machine learning algorithms"),
        " to tailor content and assessments based on individual learning styles and needs. Their AI-powered solution provides real-time feedback and adapts the learning pace to ensure better engagement and improved learning outcomes.",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Squirrel AI (2021)"),
        "Squirrel AI developed an intelligent adaptive learning system that focuses on automating the teaching process. By using ",
        (s.bold, "machine learning"),
        ", the system identifies student weaknesses and provides customized learning pathways, enhancing education by delivering targeted learning interventions to help students overcome learning challenges more efficiently.",
    )
    st_write(s.project.doc.titles.h4, "1.2.12.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "PEDRO, Francesc, SUBOSA, Miguel, RIVAS, Axel, ",
                (s.italic, "et al."),
                " Artificial intelligence in education: Challenges and opportunities for sustainable development. 2019. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CHARLES, Frank. AI-powered personalized mobile education for New Zealand students. ",
                (s.italic, "International Journal Software Engineering and Computer Science (IJSECS)"),
                ", 2023, vol. 3, no 1, p. 33-39. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "RAZAK, Abdul, NAYAK, M. Pandya, MANOHARAN, Geetha, ",
                (s.italic, "et al."),
                " Reigniting the power of artificial intelligence in education sector for the educators and students competence. In : ",
                (s.italic, "Artificial Intelligence and Machine Learning in Smart City Planning"),
                ". Elsevier, 2023. p. 103-116. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LIMNA, Pongsakorn, JAKWATANATHAM, Somporch, SIRIPIPATTANAKUL, Sutithep, ",
                (s.italic, "et al."),
                " A review of artificial intelligence (AI) in education during the digital era. ",
                (s.italic, "Advance Knowledge for Executives"),
                ", 2022, vol. 1, no 1, p. 1-9. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.vktr.com/ai-disruption/5-ai-case-studies-in-education/", link="https://www.vktr.com/ai-disruption/5-ai-case-studies-in-education/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://theintellify.com/ai-in-education/", link="https://theintellify.com/ai-in-education/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://fpt-is.com/en/insights/artificial-intelligence-in-education-an-overview/", link="https://fpt-is.com/en/insights/artificial-intelligence-in-education-an-overview/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.itransition.com/ai/education", link="https://www.itransition.com/ai/education")
    st_write(s.project.doc.titles.h4, "1.2.12.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research AI’s role in enhancing educational tools and platforms: Investigate how AI is being used to improve learning experiences, course delivery, or educational resource management.")
        with lst.item():
            st_write("Study AI-powered products developed by recent EdTech companies: Analyze the products created by startups such as Squirrel AI, Riiid Labs or other companies to understand their approach and impact on education.")
        with lst.item():
            st_write("Explore the impact of AI products on learning outcomes: Examine how AI-powered tools have improved student engagement, personalized learning experiences, or overall academic performance.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_write(s.project.doc.titles.h3, "1.2.13. How Can AI-Powered Customer Service Automation Enhance Business Operations? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.13.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine the impact of AI-powered customer service automation tools, including chatbots, on enhancing customer experiences, reducing operational costs, and increasing scalability for startups.")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Case Study/Example",
        "Popular AI-powered chatbots such as Zendesk and Intercom utilize ",
        (s.bold, "machine learning"),
        " and ",
        (s.bold, "natural language processing"),
        " to provide efficient customer service solutions, enabling startups to manage high volumes of inquiries without compromising quality. For instance, Zendesk offers customizable chatbot solutions that automate responses, streamline ticketing processes, and provide analytics on customer interactions.",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "Companies like H&M and Spotify successfully implement AI chatbots to manage customer inquiries. For example, Spotify employs AI chatbots that use ",
        (s.bold, "machine learning"),
        " and ",
        (s.bold, "natural language processing"),
        " to handle inquiries efficiently, leading to improved customer satisfaction through instant responses and personalized recommendations. Analysis of these cases reveals how chatbots have reduced operational costs, improved response times, and effectively managed complex queries that previously required human intervention.",
    )
    st_write(s.project.doc.titles.h4, "1.2.13.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "MIT SLOAN MANAGEMENT REVIEW. ",
                (s.italic, "How AI Is Transforming the Organization"),
                ". MIT Press, 2020. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.virtasant.com/ai-today/ai-in-customer-experience-spotify-airbnb-ikea#:~:text=Spotify%20employs%20AI%20in%20customer,a%20new%20era%20of%20personalization", "https://www.virtasant.com/ai-today/ai-in-customer-experience-spotify-airbnb-ikea#:~:text=Spotify%20employs%20AI%20in%20customer,a%20new%20era%20of%20personalization"),
                ". ",
            )
        with lst.item():
            st_write("ALDOSERI, Abdulaziz, AL-KHALIFA, Khalifa, et HAMOUDA, Abdelmagid. A roadmap for integrating automation with process optimization for AI-powered digital transformation. 2023. ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "VIJAYAKUMAR, Harsha. Revolutionizing customer experience with AI: a path to increase revenue growth rate. In : ",
                (s.italic, "2023 15th International Conference on Electronics, Computers and Artificial Intelligence (ECAI)"),
                ". IEEE, 2023. p. 1-6. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "REDDY, Surendranadha Reddy Byrapu. Enhancing Customer Experience through AI-Powered Marketing Automation: Strategies and Best Practices for Industry 4.0. ",
                (s.italic, "Journal of Artificial Intelligence Research"),
                ", 2022, vol. 2, no 1, p. 36-46. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "POTLA, Ravi Teja. Enhancing Customer Relationship Management (CRM) through AI-Powered Chatbots and Machine Learning. ",
                (s.italic, "Distributed Learning and Broad Applications in Scientific Research"),
                ", 2023, vol. 9, p. 364-383. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KUMAR, V., ASHRAF, Abdul R., et NADEEM, Waqar. AI-powered marketing: What, where, and how?. ",
                (s.italic, "International Journal of Information Management"),
                ", 2024, vol. 77, p. 102783. ",
            )
    st_write(s.project.doc.titles.h4, "1.2.13.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research various AI technologies (e.g., chatbots, virtual assistants, automated ticketing systems) and their roles in enhancing customer service operations.")
        with lst.item():
            st_write("Examine companies that have successfully integrated AI into their customer service processes. Assess the impact on efficiency, cost reduction, and customer satisfaction.")
        with lst.item():
            st_write("Determine the effectiveness of AI solutions in managing customer inquiries, including response times, resolution rates, and overall customer experience improvements.")
        with lst.item():
            st_write("Discuss potential challenges associated with AI implementation, such as privacy concerns, customer trust, and the impact on human jobs.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.14. How Can AI Optimize Supply Chain Operations for Startups? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.14.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Analyze how AI can help startups optimize their supply chain operations by improving demand forecasting, inventory management, and logistics.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Tools such as ClearMetal and SAP Integrated Business Planning leverage AI for predictive analytics in supply chains. These platforms utilize ",
        (s.bold, "machine learning algorithms"),
        " to enhance demand forecasting accuracy, streamline inventory management, and improve logistics efficiency.",
    )
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Companies like Amazon and Walmart implement AI technologies to optimize their supply chains. For instance, Amazon employs AI-driven analytics to enhance inventory turnover, minimize operational costs, and increase customer satisfaction by ensuring timely product availability. Analysis of these companies highlights the significant impact of AI on supply chain performance metrics.")
    st_write(s.project.doc.titles.h4, "1.2.14.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "DASH, Rupa, MCMURTREY, Mark, REBMAN, Carl, ",
                (s.italic, "et al."),
                " Application of artificial intelligence in automation of supply chain management. ",
                (s.italic, "Journal of Strategic Innovation and Sustainability"),
                ", 2019, vol. 14, no 3. ",
            )
        with lst.item():
            st_write("SHARIF, SYED MUHAMMAD et SHAIKH, HAMZA AHMED. Analyzing Value Proposition of AI Startups and Young Companies in the Field of Supply Chain. 2023. ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "HAHN, Gerd J. Industry 4.0: a supply chain innovation perspective. ",
                (s.italic, "International Journal of Production Research"),
                ", 2020, vol. 58, no 5, p. 1425-1441. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://gjia.georgetown.edu/2024/02/05/the-role-of-ai-in-developing-resilient-supply-chains/#:~:text=Specifically%2C%20AI%20can%20add%20value,the%20accuracy%20of%20demand%20forecasting", "https://gjia.georgetown.edu/2024/02/05/the-role-of-ai-in-developing-resilient-supply-chains/#:~:text=Specifically%2C%20AI%20can%20add%20value,the%20accuracy%20of%20demand%20forecasting"),
                ". ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://blog.dataiku.com/generative-ai-use-cases-in-supply-chain?utm_id=14648494489--127992686115--646704739577--ai%20in%20supply%20chain&utm_source=emea-adwords&utm_medium=paid-search&utm_campaign=GLO%20CONTENT%20Generative%20AI%20June%202023&gad_source=1&gclid=Cj0KCQjwsc24BhDPARIsAFXqAB2wSG3z02_R5_pixZaX9gIDH3c0nk7pwLkIIh_rt0AyCWITyE2lwMIaAqkmEALw_wcB", link="https://blog.dataiku.com/generative-ai-use-cases-in-supply-chain?utm_id=14648494489--127992686115--646704739577--ai%20in%20supply%20chain&utm_source=emea-adwords&utm_medium=paid-search&utm_campaign=GLO%20CONTENT%20Generative%20AI%20June%202023&gad_source=1&gclid=Cj0KCQjwsc24BhDPARIsAFXqAB2wSG3z02_R5_pixZaX9gIDH3c0nk7pwLkIIh_rt0AyCWITyE2lwMIaAqkmEALw_wcB")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.oracle.com/scm/ai-supply-chain/#:~:text=increasingly%20globalized%20future.-,What%20Is%20AI%20in%20Supply%20Chain%3F,more%20efficiency%20than%20traditional%20software", "https://www.oracle.com/scm/ai-supply-chain/#:~:text=increasingly%20globalized%20future.-,What%20Is%20AI%20in%20Supply%20Chain%3F,more%20efficiency%20than%20traditional%20software"),
                ". ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ZAMANI, Efpraxia D., SMYTH, Conn, GUPTA, Samrat, ",
                (s.italic, "et al."),
                " Artificial intelligence and big data analytics for supply chain resilience: a systematic literature review. ",
                (s.italic, "Annals of Operations Research"),
                ", 2023, vol. 327, no 2, p. 605-632. ",
            )
    st_write(s.project.doc.titles.h4, "1.2.14.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research AI tools like ClearMetal and SAP Integrated Business Planning to understand their functionalities and applications in supply chain optimization. ")
        with lst.item():
            st_write("Select one or more companies (e.g., Amazon or Walmart) that utilize AI in its supply chain and analyze its effects on inventory turnover, operational costs, and customer satisfaction. ")
        with lst.item():
            st_write("Evaluate the role of AI in enhancing supply chain visibility and efficiency for startups. ")
        with lst.item():
            st_write("Report writing (cf. course material). ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.15. How Can AI Improve Intellectual Property (IP) Management for Startups? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.15.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Explore how AI technologies can enhance the management of intellectual property (IP) for startups, focusing on IP creation, protection, and enforcement.")
    st_write(s.project.doc.paragraphs.p_body, "Case Study/ Example")
    st_write(
        s.project.doc.paragraphs.p_body,
        "IPwe utilizes AI-driven analytics to improve IP management for startups. By leveraging ",
        (s.bold, "blockchain technology "),
        "and ",
        (s.bold, "machine learning"),
        ", IPwe helps businesses identify and manage their patents effectively. The platform offers tools for analyzing patent portfolios, assessing patent value, and facilitating licensing opportunities. Startups that have used IPwe have reported improved visibility into their IP assets, enabling better strategic decisions regarding patent filings and enforcement.",
    )
    st_write(s.project.doc.titles.h4, "1.2.15.2. References and Resources", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://coingeek.com/ipwe-blockchain-smart-pool-taps-into-ai-to-handle-patent-analytics/", link="https://coingeek.com/ipwe-blockchain-smart-pool-taps-into-ai-to-handle-patent-analytics/")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "LEE, Jyh-An, HILTY, Reto, et LIU, Kung-Chung (ed.). ",
                (s.italic, "Artificial intelligence and intellectual property"),
                ". Oxford University Press, 2021. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "KOP, Mauritz. AI & intellectual property: Towards an articulated public domain. ",
                (s.italic, "Tex. Intell. Prop. LJ"),
                ", 2019, vol. 28, p. 297. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "CALVIN, Nathan et LEUNG, Jade. Who owns artificial intelligence? A preliminary analysis of corporate intellectual property strategies and why they matter. ",
                (s.italic, "Future of Humanity Institute, February"),
                ", 2020. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "TREQUATTRINI, Raffaele, LARDO, Alessandra, CUOZZO, Benedetta, ",
                (s.italic, "et al."),
                " Intangible assets management and digital transformation: evidence from intellectual property rights-intensive industries. ",
                (s.italic, "Meditari Accountancy Research"),
                ", 2022, vol. 30, no 4, p. 989-1006. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.rst.software/blog/28-ways-to-boost-your-supply-chain-business-with-artificial-intelligence", link="https://www.rst.software/blog/28-ways-to-boost-your-supply-chain-business-with-artificial-intelligence")
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "1.2.15.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Investigate AI technologies currently being used for IP management, focusing on tools like IPwe and their functionalities.")
        with lst.item():
            st_write("Analyze one or more case studies to understand how AI improves the management of intellectual property, including specific examples of startups that have benefited from the platform.")
        with lst.item():
            st_write("Examine the challenges startups face in IP management and how AI can address these issues.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "1.2.16. How Can AI Assist Startups in Navigating International Tax Compliance? (TOOL)", tag=t.h3)
    st_write(s.project.doc.titles.h4, "1.2.16.1. Objective", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Examine how AI technologies can help startups manage international tax compliance, focusing on automating processes, ensuring accuracy, and reducing the risk of non-compliance.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Case Study/Example ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Avalara is a leading provider of tax compliance automation software that utilizes AI, specifically ",
        (s.bold, "machine learning"),
        ", to assist startups with international tax regulations. The platform automates sales tax calculations, tax reporting, and compliance processes across multiple jurisdictions. Startups using Avalara have reported significant reductions in manual processing time, minimized errors in tax filings, and increased confidence in compliance with local tax laws, thereby reducing the risk of audits and penalties.",
    )
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "KPMG Luxembourg has embraced ",
        (s.bold, "generative AI"),
        " and ",
        (s.bold, "machine learning"),
        " to enhance its tax compliance services for startups and larger firms alike. By integrating generative AI tools with traditional tax compliance platforms, KPMG helps businesses navigate complex international tax regulations across various jurisdictions. ",
    )
    st_write(s.project.doc.titles.h4, "1.2.16.2. References and Resources ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.avalara.com/us/en/index.html", link="https://www.avalara.com/us/en/index.html")
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://www.avalara.com/in/en/resources/press/future-of-ai-and-ml-in-taxtech-space.html", link="https://www.avalara.com/in/en/resources/press/future-of-ai-and-ml-in-taxtech-space.html")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "ADELAKUN, Beatrice Oyinkansola, NEMBE, Joseph Kuba, OGUEJIOFOR, Bisola Beatrice, ",
                (s.italic, "et al."),
                " Legal frameworks and tax compliance in the digital economy: a finance perspective. ",
                (s.italic, "Engineering Science & Technology Journal"),
                ", 2024, vol. 5, no 3, p. 844-853. ",
            )
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://kpmg.com/lu/en/blogs/home/posts/2023/12/how-generative-ai-tools-will-transform-tax-landscape.html", link="https://kpmg.com/lu/en/blogs/home/posts/2023/12/how-generative-ai-tools-will-transform-tax-landscape.html")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.pwc.com/gx/en/services/tax/connected-tax-compliance/build-trust-ai-tax-compliance.html", link="https://www.pwc.com/gx/en/services/tax/connected-tax-compliance/build-trust-ai-tax-compliance.html")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.datarails.com/8-ways-ai-can-enhance-tax-compliance/", link="https://www.datarails.com/8-ways-ai-can-enhance-tax-compliance/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://gaper.io/ai-and-tax-season/", link="https://gaper.io/ai-and-tax-season/")
    st_write(s.project.doc.titles.h4, "1.2.16.3. Suggested Steps ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Research AI tools available for international tax compliance, emphasizing functionalities and benefits.")
        with lst.item():
            st_write("Analyze one or more case studies to understand how AI can streamline tax compliance processes for startups.")
        with lst.item():
            st_write("Investigate the common challenges startups face in international tax compliance and how AI can address these issues.")
        with lst.item():
            st_write("Report writing (cf. course material).")
    st_space(size=1)
