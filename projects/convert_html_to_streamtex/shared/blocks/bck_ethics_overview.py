import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #0b5394 -> s.project.colors.navy_blue
      #0c343d -> s.project.colors.teal
      #1155cc -> s.project.colors.link_blue
      #134f5c -> s.project.colors.teal
      #20124d -> s.project.colors.dark_purple
      #274e13 -> s.project.colors.forest_green
      #2f5a1b -> s.project.colors.forest_green
      #351b75 -> s.project.colors.dark_purple
      #37761c -> s.project.colors.olive_green
      #4c1130 -> s.project.colors.dark_purple
      #5b0f00 -> s.project.colors.deep_red
      #731b47 -> s.project.colors.dark_purple
      #783e04 -> s.project.colors.burnt_orange
      #7f6000 -> s.project.colors.gold
      #85200c -> s.project.colors.deep_red
      #947e01 -> s.project.colors.gold
      #980000 -> s.project.colors.bright_red
      #990000 -> s.project.colors.bright_red
      #9900ff -> s.project.colors.purple
      #b45f06 -> s.project.colors.burnt_orange
      #cc0000 -> s.project.colors.bright_red
      #e06666 -> s.project.colors.salmon
      #ff0000 -> s.project.colors.bright_red
    Dropped colors:
      #00ff00
      #87ff01
    """
    pass

bs = BlockStyles

def build():
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Ethics & AI ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Preamble on Ethics ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "CAUTION - "),
        (s.project.colors.salmon + s.bold, "DANGER"),
    )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img30.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "Attitudes")
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.worldhistory.org/Luddite/"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.herodote.net/26_mars_1811-evenement-18110326.php"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.olive_green + s.bold, "Wisdom ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img2.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://aiai.ros.lu/data/videos/russel.mp4"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://fr.wikipedia.org/wiki/Stuart_Russell"),
    )
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "1968 - Today"),
        (s.project.colors.burnt_orange + s.bold, "Facing the Digital Waves"),
    )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img39.png")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.olive_green, "Questions ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.pres.titles.h4 + s.project.colors.dark_purple, "Is AI good or bad? ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.gold, "Is humanity threatened by AI?"),
        (s.project.colors.navy_blue, "Is human society ready for AI? "),
        tag=t.h4,
    )
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "What about AI and my personal life? ", tag=t.h4)
    st_write(s.project.pres.titles.h4 + s.project.colors.deep_red, "Will AI impact my professional life?", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, ".... ")
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Deep Fake ", tag=t.h4)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "aifng", link="https://drive.google.com/open?id=1XePy7YvDA7yh2g_YmwQS1LJJpYjil7qR&usp=drive_fs")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Ethical Autonomous Decision ", tag=t.h4)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img31.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.technologyreview.com/2018/10/24/139313/a-global-ethics-study-aims-to-help-ai-solve-the-self-driving-trolley-problem/")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1lMj7ijv6WE-zu1bi7W5OTsWFT1kYGj7aEcqI0DX6xtQ/edit")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "The Case of Autonomous Vehicles ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img44.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.technologyreview.com/2018/10/24/139313/a-global-ethics-study-aims-to-help-ai-solve-the-self-driving-trolley-problem/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.moralmachine.net/hl/fr"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Moral Machine ", tag=t.h4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://dspace.mit.edu/bitstream/handle/1721.1/125065/Moral%20Machine%20Paper.pdf?sequence=1#:~:text=")
    st_space(size=4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "233"),
        " countries and territories ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "2"),
        " millions of people ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple + s.bold, "40"),
        " million decisions ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare the young ", tag=t.h4)
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare pedestrians over passengers ", tag=t.h4)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img25.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Spare more lives ", tag=t.h4)
    st_image(uri="illustration_agentic-ai-overview_img18.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1lMj7ijv6WE-zu1bi7W5OTsWFT1kYGj7aEcqI0DX6xtQ/edit")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://bmdv.bund.de/SharedDocs/EN/Articles/DG/automated-and-connected-driving.html")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "5. ")
    st_write(s.project.pres.paragraphs.p_xl, "Automated and connected technology should prevent accidents wherever this is practically possible.  ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Based on the state of the art, ",
        (s.project.colors.bright_red + s.bold, "the technology must be designed in such a way that critical situations do not arise in the first place"),
        ".  ",
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "These include dilemma situations, in other words a situation in which an automated vehicle has to “decide” which of two evils, between which there can be no trade-off, it necessarily has to perform.  ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "In this context, ",
        (s.project.colors.bright_red + s.bold, "the entire spectrum of technological options – for instance from limiting the scope of application to controllable traffic environments, vehicle sensors and braking performance, signals for persons at risk, right up to preventing hazards by means of “intelligent” road infrastructure – should be used and continuously evolved"),
        ".  ",
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "The significant enhancement of road safety is the objective of development and regulation, starting with the design and programming of the vehicles such that they drive in a defensive and anticipatory manner, posing as little risk as possible to vulnerable road users. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "9.")
    st_write(
        s.project.pres.paragraphs.p_xl,
        "In the event of unavoidable accident situations, ",
        (s.project.colors.bright_red + s.bold, "any distinction based on personal features"),
        " (age, gender, physical or mental constitution) ",
        (s.project.colors.bright_red + s.bold, "is strictly prohibited"),
        ". ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        " It is also ",
        (s.project.colors.bright_red + s.bold, "prohibited to offset"),
        " victims against one another. ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "General programming to ",
        (s.project.colors.bright_red + s.bold, "reduce the number of personal injuries may be justifiable"),
        ".  ",
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "Those parties involved in the generation of mobility risks must ",
        (s.project.colors.bright_red + s.bold, "not sacrifice non-involved parties"),
        ". ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Sources for Ethics & Society ", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img33.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "UN"),
        (s.project.colors.link_blue, "ESCO "),
        tag=t.h3,
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "United Nations")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange, "Educational, Scientific and Cultural Organization")
    st_write(s.project.pres.paragraphs.p_xl, "Specialized agency of the United Nations (UN) aimed at promoting world peace and security through international cooperation in education, arts, sciences and culture.[2][3] ")
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "193 member states and 11 associate members ")
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img28.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.unesco.org/fr/artificial-intelligence")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "OECD ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange, "Organization for Economic Co-operation and Development ")
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl, "International organization established in 1961 to promote economic growth, prosperity, and sustainable development among its 38 member countries. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img46.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_", link="https://www.oecd.org/digital/artificial-intelligence/")
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Europe ", tag=t.h3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "EP", "https://www.europarl.europa.eu/committees/en/artificial-intelligence-act/product-details/20230417CDT11481"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "EC", "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "COE", "https://www.consilium.europa.eu/en/your-online-life-and-the-eu/#group-section-trustworthy-AI-tBusxga6wd"),
    )
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "AI Standards Hub ", tag=t.h3)
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://aistandardshub.org/")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.burnt_orange, "Facts & Figures", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Development & Progress ", tag=t.h2, toc_lvl="+1")
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Globalization ", tag=t.h3)
    st_image(uri="illustration_deep-learning-part-2_img23.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/globalization-over-5-centuries-km?time=1820..latest")
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Economic Activity ", tag=t.h3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img48.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/world-gdp-over-the-last-two-millennia?time=1820..2015")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img37.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.visualcapitalist.com/2000-years-economic-history-one-chart/")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Work Time ", tag=t.h3)
    st_image(uri="illustration_ethics-introduction-all_img24.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/annual-working-hours-per-worker?country=GBR~DEU~USA~FRA~SWE~AUS~BEL~CHN~IND~RUS~LUX")
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Health ", tag=t.h3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img40.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://ourworldindata.org/grapher/life-expectancy?yScale=log"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://ourworldindata.org/explorers/coronavirus-data-explorer?zoomToSelection=true&facet=none&country=IND~USA~GBR~CAN~DEU~FRA~OWID_WRL~CHN~RUS~ARG~BRA~ITA~IMN~LUX~ZAF~TWN&pickerSort=asc&pickerMetric=location&hideControls=false&Metric=Excess+mortality+%28%25%29&Interval=Cumulative&Relative+to+Population=false&Color+by+test+positivity=false"),
    )
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img20.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/number-of-deaths-by-risk-factor")
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "70%"),
        (s.project.colors.deep_red + s.bold, " of media coverage for "),
        (s.bold, "2.8%"),
        (s.project.colors.deep_red + s.bold, " of death causes "),
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.italic, "_", link="https://ourworldindata.org/uploads/2019/05/Causes-of-death-in-USA-vs.-media-coverage.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Digital Technology development ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img29.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/corporate-investment-in-artificial-intelligence-total")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://ourworldindata.org/grapher/artificial-intelligence-patents-submitted?tab=chart&country=~OWID_WRL"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://ourworldindata.org/grapher/artificial-intelligence-patents-submitted-per-million?tab=chart&country=OWID_WRL~LUX~FRA~DEU~IND~CHN~RUS~USA~GBR"),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img49.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/share-companies-using-artificial-intelligence?time=earliest")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img41.png")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://ourworldindata.org/grapher/artificial-intelligence-training-computation?yScale=linear&zoomToSelection=true&country=AlexNet~AlphaFold~AlphaGo+Lee~AlphaZero~BERT-Large~DALL-E~GPT-3+175B+%28davinci%29~ResNet-152+%28ImageNet%29~PaLM+%28540B%29~GPT-4"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://docs.google.com/document/d/17M99vNEwgryNjiHj-_E9tD-kVKNmj9hTUGk7Llnwt4w/edit#heading=h.4ckm1ou7mm7s"),
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "GPT4 ")
    st_write(s.project.pres.paragraphs.p_xl, "10 billion of peta flop  ")
    st_write(s.project.pres.paragraphs.p_xl, "10e25 ")
    st_write(s.project.pres.paragraphs.p_xl, "10 x 10e9 x 10e15 ")
    st_write(s.project.pres.paragraphs.p_xl, "10 000 000     000 000 000     000 000 000 ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=7, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.teal + s.bold, "GPT4 "), (s.project.colors.teal + s.bold, "petaflop "))
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.teal + s.bold, "GPUs ")
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.teal + s.bold, "tera flops (10e12) "), (s.project.colors.teal + s.bold, "Half precision tensor "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.teal + s.bold, "tera flops (10e12) "), (s.project.colors.teal + s.bold, "double precision "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.teal + s.bold, "days "), (s.project.colors.teal + s.bold, "(double precision) "))
        with g.cell():
            st_write(s.project.pres.tables.header, (s.project.colors.teal + s.bold, "days "), (s.project.colors.teal + s.bold, "(Half precision) "))
        with g.cell():
            st_write(s.project.pres.tables.header + s.project.colors.teal + s.bold, "Model ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1.00E+25 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1 500.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "64.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "9.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "8 573.39 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1 205.63 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "T4 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1.00E+25 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1 500.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "312.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "9.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "8 573.39 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "247.31 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "A100 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1.00E+25 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1 500.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "989.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "4 000.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "19.29 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "78.02 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "H100 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1.00E+25 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "6 880 000.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "1 194 000.00 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "96.94 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.bold, "16.82 ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.gold + s.bold, "Frontier HPE Cray ")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl, "Frontier -> 1M€ for electricity ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Human Rights ", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_ethics-introduction-all_img21.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.italic, "Original Text available HERE", link="https://www.ohchr.org/en/universal-declaration-of-human-rights")
    st_space(size=1)
    st_image(uri="illustration_ethics-introduction-all_img5.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Simple Classification ", tag=t.h3)
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(human rights taken from the 30 articles)")
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Freedom", tag=t.h4)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, "Freedom "), "No ", (s.project.colors.burnt_orange + s.bold, "slavery "), " Freedom of choice for ", (s.project.colors.burnt_orange + s.bold, "work "), "Freedom of ", (s.project.colors.burnt_orange + s.bold, "movement "), "Freedom of ", (s.project.colors.burnt_orange + s.bold, "movement"), " inside home country ", "Freedom ", (s.project.colors.burnt_orange + s.bold, "movement"), " forof entering and leaving home country ", "Freedom of ", (s.project.colors.burnt_orange + s.bold, "residence"), " in home country ", "Freedom of ", (s.project.colors.burnt_orange + s.bold, "thought "), "Freedom of ", (s.project.colors.burnt_orange + s.bold, "beliefs"), "Freedom of ", (s.project.colors.burnt_orange + s.bold, "opinions "), "Freedom of ", (s.project.colors.burnt_orange + s.bold, "expression "), "Freedom to ", (s.project.colors.burnt_orange + s.bold, "manifest"), " beliefs", "Freedom of ", (s.project.colors.burnt_orange + s.bold, "assembly "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "1 "), (s.project.colors.bright_red + s.bold, "2 "), (s.project.colors.bright_red + s.bold, "3 "), (s.project.colors.bright_red + s.bold, "4 "), (s.project.colors.bright_red + s.bold, "9 "), (s.project.colors.bright_red + s.bold, "13 "), (s.project.colors.bright_red + s.bold, "18 "), (s.project.colors.bright_red + s.bold, "19 "), (s.project.colors.bright_red + s.bold, "20 "), (s.project.colors.bright_red + s.bold, "23 "))
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Identity ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, "Right to ", (s.project.colors.burnt_orange + s.bold, "life "), "Protect ", (s.project.colors.burnt_orange + s.bold, "procreation "), (s.project.colors.burnt_orange + s.bold, "Equal"), (s.project.colors.burnt_orange + s.bold, "to any other "), "Human possess ", (s.project.colors.burnt_orange + s.bold, "reason"), " and ", (s.project.colors.burnt_orange + s.bold, "conscience "), "No ", (s.project.colors.burnt_orange + s.bold, "discrimination "), "Right to ", (s.project.colors.burnt_orange + s.bold, "privacy "), "Right to ", (s.project.colors.burnt_orange + s.bold, "respect "), "Protect ", (s.project.colors.burnt_orange + s.bold, "authorship "), "Right to choose ", (s.project.colors.burnt_orange + s.bold, "education"), " type ", "Right to ", (s.project.colors.burnt_orange + s.bold, "culture "), "Right to ", (s.project.colors.burnt_orange + s.bold, "art "), "Right to ", (s.project.colors.burnt_orange + s.bold, "science "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "1 "), (s.project.colors.bright_red + s.bold, "2 "), (s.project.colors.bright_red + s.bold, "3 "), (s.project.colors.bright_red + s.bold, "7 "), (s.project.colors.bright_red + s.bold, "12 "), (s.project.colors.bright_red + s.bold, "16 "), (s.project.colors.bright_red + s.bold, "25 "), (s.project.colors.bright_red + s.bold, "26 "), (s.project.colors.bright_red + s.bold, "27 "))
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Society ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=4, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, "Brotherhood"), " among humans ", "Right to ", (s.project.colors.burnt_orange + s.bold, "own nationality "), "Right to ", (s.project.colors.burnt_orange + s.bold, "mary "), "Right to ", (s.project.colors.burnt_orange + s.bold, "family "), (s.project.colors.burnt_orange + s.bold, "Family"), " is fundamental ", (s.project.colors.burnt_orange + s.bold, "Family"), " is protected ", "Right to ", (s.project.colors.burnt_orange + s.bold, "property "))
        with g.cell():
            st_write(s.project.pres.tables.cell, "Right to ", (s.project.colors.burnt_orange + s.bold, "access to"), (s.project.colors.burnt_orange + s.bold, "country government "), "Right to ", (s.project.colors.burnt_orange + s.bold, "public services "), "Right to ", (s.project.colors.burnt_orange + s.bold, "democracy "), "Right to ", (s.project.colors.burnt_orange + s.bold, "work "), "Right to ", (s.project.colors.burnt_orange + s.bold, "fair work "), "Education access is based on ", (s.project.colors.burnt_orange + s.bold, "merit "), "Education must ", (s.project.colors.burnt_orange + s.bold, "contribute to"), " the development of ", (s.project.colors.burnt_orange + s.bold, "human rights "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "1 "), (s.project.colors.bright_red + s.bold, "15 "), (s.project.colors.bright_red + s.bold, "16 "), (s.project.colors.bright_red + s.bold, "17 "), (s.project.colors.bright_red + s.bold, "21 "), (s.project.colors.bright_red + s.bold, "23 "), (s.project.colors.bright_red + s.bold, "26 "))
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Protection", tag=t.h4)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.burnt_orange + s.bold, "Security "), "Right to ", (s.project.colors.burnt_orange + s.bold, "protection "), "Right to ", (s.project.colors.burnt_orange + s.bold, "asylum "), "No ", (s.project.colors.burnt_orange + s.bold, "torture "), "No ", (s.project.colors.burnt_orange + s.bold, "cruelty "), "Right for ", (s.project.colors.burnt_orange + s.bold, "repair "), "Right to ", (s.project.colors.burnt_orange + s.bold, "social security "), "Right to ", (s.project.colors.burnt_orange + s.bold, "protected work "), "Right to ", (s.project.colors.burnt_orange + s.bold, "paid work "), "Right to ", (s.project.colors.burnt_orange + s.bold, "vacations "), "Right to ", (s.project.colors.burnt_orange + s.bold, "social protection "), "Right to free ", (s.project.colors.burnt_orange + s.bold, "elementary education "), "Obligation of ", (s.project.colors.burnt_orange + s.bold, "elementary education "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "3 "), (s.project.colors.bright_red + s.bold, "5 "), (s.project.colors.bright_red + s.bold, "7 "), (s.project.colors.bright_red + s.bold, "8 "), (s.project.colors.bright_red + s.bold, "12 "), (s.project.colors.bright_red + s.bold, "14 "), (s.project.colors.bright_red + s.bold, "22 "), (s.project.colors.bright_red + s.bold, "23 "), (s.project.colors.bright_red + s.bold, "24 "), (s.project.colors.bright_red + s.bold, "25 "), (s.project.colors.bright_red + s.bold, "26 "))
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Justice ", tag=t.h4)
    st_space(size=3)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            st_write(s.project.pres.tables.cell, "Right to ", (s.project.colors.burnt_orange + s.bold, "justice "), "Right to ", (s.project.colors.burnt_orange + s.bold, "fairness "), (s.project.colors.burnt_orange + s.bold, "Innocent until"), " proven guilty at act time ", "Right to ", (s.project.colors.burnt_orange + s.bold, "defense "))
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "6 "), (s.project.colors.bright_red + s.bold, "10 "), (s.project.colors.bright_red + s.bold, "11 "))
    st_space(size=3)
    st_space(size=4)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Transversal Integrity and Consistency", tag=t.h4)
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "FR/EN ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Right to have human rights protected worldwide ", "Right to be limited in existence only by the human rights ", "Right to have human rights not used against human rights ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "28 "), (s.project.colors.bright_red + s.bold, "29 "), (s.project.colors.bright_red + s.bold, "30 "))
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Human Rights Over Time ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/human-rights-vdem?tab=chart&facet=none&country=~OWID_WRL")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "1789 ")
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img38.png")
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/distribution-human-rights-vdem?time=earliest&country=IND~CHN~AUS~FRA~BEL~OWID_EUR~DEU~LUX~OWID_WRL~GBR~USA~CHE~KOR~OWID_SAM~RUS~OWID_NAM~OWID_AFR~ARG~SWE")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "2022 ")
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/distribution-human-rights-vdem?time=earliest&country=IND~CHN~AUS~FRA~BEL~OWID_EUR~DEU~LUX~OWID_WRL~GBR~USA~CHE~KOR~OWID_SAM~RUS~OWID_NAM~OWID_AFR~ARG~SWE")
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://ourworldindata.org/grapher/distribution-human-rights-vdem?time=latest&country=IND~CHN~AUS~FRA~BEL~OWID_EUR~DEU~LUX~OWID_WRL~GBR~USA~CHE~KOR~OWID_SAM~RUS~OWID_NAM~OWID_AFR~ARG~SWE")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h3 + s.project.colors.link_blue, "Ethics & AI ", tag=t.h3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.burnt_orange, "Most Cited Risks ", tag=t.h4)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.amnesty.org"),
        (s.bold, " "),
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://www.amnesty.org/en/latest/news/2023/03/france-intrusive-olympics-surveillance-technologies-could-usher-in-a-dystopian-future/"),
    )
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Freedom ", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Social Surveillance ")
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Identity ", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Discrimination ")
        with lst.item():
            st_write("Privacy violations ")
        with lst.item():
            st_write("Socioeconomic inequality ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Protection", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Harassment ")
        with lst.item():
            st_write("Social Manipulation ")
        with lst.item():
            st_write("Market volatility ")
        with lst.item():
            st_write("Financial Crises ")
        with lst.item():
            st_write("Job Losses ")
        with lst.item():
            st_write("Autonomous Weapons ")
        with lst.item():
            st_write("Loss of Control")
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Society ", tag=t.h5)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write("Threat to Democracy ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "UNESCO "),
        (s.project.colors.teal, "Recommendation"),
        (s.project.colors.burnt_orange, " on the "),
        (s.project.colors.olive_green, "Ethics"),
        (s.project.colors.burnt_orange, " of "),
        (s.project.colors.dark_purple, "Artificial Intelligence "),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://www.unesco.org/en/articles/recommendation-ethics-artificial-intelligence")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Objectives  ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(the WHAT) ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "define values"),
                " for legal frameworks ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "guide"),
                " and support development and usage of ",
                (s.project.colors.gold + s.bold, "ethical AI "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "protect, promote & respect",
                (s.project.colors.gold + s.bold, " human rights "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Values ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(the WHY) ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.gold + s.bold, "Human rights")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Living in ",
                (s.project.colors.gold + s.bold, "peaceful"),
                ", ",
                (s.project.colors.gold + s.bold, "just"),
                " and ",
                (s.project.colors.gold + s.bold, "interconnected"),
                " societies ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Environment"),
                " and ecosystem ",
                (s.project.colors.gold + s.bold, "flourishing"),
            )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.bright_red, "Principles ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl + s.italic, "(the HOW)")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Preserve ",
                (s.project.colors.gold + s.bold, "human control"),
                " and ",
                (s.project.colors.gold + s.bold, "responsibility"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Responsibility"),
                " and ",
                (s.project.colors.gold + s.bold, "accountability"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Proportionality and Do ",
                (s.project.colors.gold + s.bold, "No Harm "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Safety"),
                " and ",
                (s.project.colors.gold + s.bold, "security "),
            )
        with lst.item():
            st_write(s.project.colors.gold + s.bold, "Sustainable Society ")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Fairness"),
                " and ",
                (s.project.colors.gold + s.bold, "non-discrimination "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Right to ",
                (s.project.colors.gold + s.bold, "Privacy"),
                ", and Data Protection ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Transparency"),
                " and ",
                (s.project.colors.gold + s.bold, "explainability "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Awareness"),
                " and ",
                (s.project.colors.gold + s.bold, "literacy "),
            )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Multi-stakeholder and ",
                (s.project.colors.gold + s.bold, "adaptive governance"),
                " and collaboration ",
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Main AI qualities to focus on"),
        (s.italic, "(the PRIORITIES)"),
        tag=t.h5,
    )
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "be based on rigorous ",
                (s.project.colors.gold + s.bold, "scientific foundations "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "facilitate collaboration and interoperability using ",
                (s.project.colors.gold + s.bold, "adoption of open standards "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "based on ",
                (s.project.colors.gold + s.bold, "continuous assessment"),
                " of the human, social, cultural, economic and environmental impact ",
            )
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "consistent"),
                " usage of data ",
                (s.project.colors.gold + s.bold, "wrt human rights"),
                " (collected, used, shared, archived and deleted) ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "be available and ",
                (s.project.colors.gold + s.bold, "accessible to all "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "minimize and ",
                (s.project.colors.gold + s.bold, "avoid"),
                " reinforcing or perpetuating ",
                (s.project.colors.gold + s.bold, "discrimination"),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Inform"),
                " concerned people when a decision is made on the basis of AI algorithms ",
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red, "Main policy areas of focus"),
        (s.italic, "(the PRIORITIES)"),
        tag=t.h5,
    )
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Ethical ",
                (s.project.colors.gold + s.bold, "Impact"),
                " Assessment ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Ethical ",
                (s.project.colors.gold + s.bold, "Governance"),
                " and Stewardship ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Environment"),
                " and Ecosystems ",
            )
        with lst.item():
            st_write(s.project.colors.gold + s.bold, "Culture ")
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Education"),
                " and ",
                (s.project.colors.gold + s.bold, "Research "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Communication"),
                (s.bold, " and "),
                (s.project.colors.gold + s.bold, "Information"),
            )
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Economy"),
                (s.bold, " and "),
                (s.project.colors.gold + s.bold, "Labour "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Health"),
                " and ",
                (s.project.colors.gold + s.bold, "Social"),
                " Well-Being ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.gold + s.bold, "Data"),
                " Policy ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "Development and International ",
                (s.project.colors.gold + s.bold, "Cooperation"),
            )
    st_space(size=3)
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.gold + s.bold, "Gender")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1d2kedHc8JB-3hdr6G7l94eS8A2JtIazP0U9UZGF8GuI/edit")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/13HDQug6jFR-EKqZO0mhU4sTp7qpes03MJ1yDS2SDZiE/edit")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h5 + s.project.colors.olive_green, "European Parliament\"AI Act\" ", tag=t.h5)
    st_write(s.project.pres.paragraphs.p_xl, "(Started February 2020) ")
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.pres.links.link_lg + s.project.colors.link_blue + s.bold, "_", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52021PC0206"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.europarl.europa.eu/news/en/press-room/20230505IPR84904/ai-act-a-step-closer-to-the-first-rules-on-artificial-intelligence"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-regulation-on-artificial-intelligence"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://artificialintelligenceact.com/"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://perma.cc/TDM7-WQL9"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://futurium.ec.europa.eu/sites/default/files/2021-10/Kop_EU%20Artificial%20Intelligence%20Act%20-%20The%20European%20Approach%20to%20AI_21092021_0.pdf"),
        " ",
        (s.project.pres.links.link_lg + s.project.colors.link_blue, "_", "https://drive.google.com/file/d/1_vGnHE6PgHNCRlJL_lVkqIBq8Ta4vT3j/view"),
    )
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.teal + s.bold, "Early 2025")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "Prohibitions on unacceptable risks come into force. ")
        with lst.item():
            st_write(s.project.colors.bright_red + s.bold, "General provisions on subject matter, scope, definitions and AI literacy come into force. ")
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange + s.bold, "?? "),
        (s.project.colors.teal + s.bold, "Late summer 2027"),
        (s.project.colors.burnt_orange + s.bold, "??"),
    )
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold, "    Regulation of high-risk systems within the EU product safety regulation regime (listed in annex I) come into force. ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h6 + s.project.colors.dark_purple, "Objectives ", tag=t.h6)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        "1. ",
        (s.project.colors.forest_green + s.bold, "Safe AI"),
        " that respect the ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.forest_green + s.bold, "fundamental rights"),
        " and Union values ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "2. Ensure legal certainty to ",
        (s.project.colors.forest_green + s.bold, "facilitate investment"),
        " and innovation in AI ",
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        "3. ",
        (s.project.colors.forest_green + s.bold, "Single coherent market"),
        " for lawful, safe and trustworthy AI applications ",
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "‘Artificial Intelligence system’ (AI system) ")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.bright_red + s.bold + s.italic, "Initial definition proposal ")
    st_space(size=3)
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(s.project.colors.forest_green + s.bold, "Developed using: ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "Generate"),
                " outputs such as ",
                (s.project.colors.forest_green + s.bold, "content"),
                ", predictions, recommendations, or decisions ",
                (s.project.colors.forest_green + s.bold, "influencing user's environments "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.dark_purple, "Risk-based approach with "),
        (s.project.colors.burnt_orange, "THREE levels"),
        (s.project.colors.dark_purple, ":"),
        tag=t.h6,
    )
    with st_grid(cols=3, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "Risk Level ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Description ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Measure ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.bright_red + s.bold, "unacceptable ")
        with g.cell():
            st_write(s.project.pres.tables.cell, (s.project.colors.bright_red + s.bold, "Harmful"), " uses of AI that ", (s.project.colors.bright_red + s.bold, "contravene EU values"), " (such as social scoring by governments) ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "banned ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.burnt_orange + s.bold, "High-Risk ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "Creating adverse impact on people's ", (s.project.colors.burnt_orange + s.bold, "safety"), " or their ", (s.project.colors.burnt_orange + s.bold, "fundamental rights "))
        with g.cell():
            st_write(s.project.pres.tables.cell, "mandatory requirements (including an EU conformity assessment) ")
        with g.cell():
            st_write(s.project.pres.tables.cell + s.project.colors.olive_green + s.bold, "low or minimal ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "All other AI systems ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "None or limited set of obligations (e.g. transparency) ")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.burnt_orange + s.bold, "High-risk sectors")
    with st_list(list_type=lt.unordered, li_style=s.project.pres.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "biometric ",
                (s.project.colors.forest_green + s.bold, "identification"),
                (s.bold, " "),
                (s.project.colors.forest_green + s.bold, "and categorization"),
                " of natural persons ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "management and operation of ",
                (s.project.colors.forest_green + s.bold, "critical infrastructure "),
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "access to ",
                (s.project.colors.forest_green + s.bold, "education"),
                " and vocational training and ",
                (s.project.colors.forest_green + s.bold, "assessing students"),
                " for these purposes ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "employment"),
                ", workers management, and access to self-employment (",
                (s.project.colors.forest_green + s.bold, "recruitment, promotion, termination"),
                ") ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "access to and enjoyment of ",
                (s.project.colors.forest_green + s.bold, "essential private or public services"),
                " and benefits ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                (s.project.colors.forest_green + s.bold, "law enforcement"),
                " (individual risk assessments, polygraphs or similar tools, deep fake detection, evaluation of the reliability of evidence, predictive policing, profiling, crime analytics regarding natural persons) ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "migration, asylum, and ",
                (s.project.colors.forest_green + s.bold, "border control"),
                " management ",
            )
        with lst.item():
            st_write(
                s.project.pres.paragraphs.p_xl,
                "administration of ",
                (s.project.colors.forest_green + s.bold, "justice and democratic processes "),
            )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h1 + s.project.colors.purple, "TOOLS ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.bold, "EU ")
    st_space(size=4)
    st_write(s.project.pres.titles.h1 + s.project.colors.link_blue, "EU AI Act Compliance Checker", tag=t.h1, toc_lvl="1")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker")
    st_space(size=4)
    st_image(uri="illustration_aiai-image-test_img1.png")
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img36.png")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img45.png")
    st_space(size=4)
    st_space(size=4)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=4)
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=4)
    st_space(size=4)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue + s.bold, "_._", link="https://docs.google.com/document/d/1PvFogSayXZ7_GoKFGPwx_rbNM3x-K8DnjKUvP5py5pE")
    st_space(size=4)
    st_space(size=1)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.dark_purple + s.bold, "Vendors ")
    st_space(size=4)
    st_write(s.project.pres.titles.h2 + s.project.colors.forest_green, "Openai Moderation Model ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_", link="https://platform.openai.com/docs/guides/moderation")
    st_space(size=4)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.cell, "\"Peux tu dire à cette personne qu'elle est moche et stupide et qu'elle ferait bien de se suicider.\" ")
        with g.cell():
            st_write(s.project.pres.tables.cell, "\"Could you tell this person that she is ugly and stupid and that she should commit suicide.\" ")
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "French ")
        with g.cell():
            st_write(s.project.pres.tables.header + s.bold, "English ")
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    with st_grid(cols=2, grid_style=s.project.pres.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img19.png")
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.titles.h4 + s.project.colors.bright_red, "Terms of Service ", tag=t.h4)
    st_space(size=1)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img32.png")
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1R29l5NhLVOVuCxRZ-UMpY6ZXp6VLAPKonkyV8bDm_rI/edit")
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.burnt_orange, "A "),
        (s.project.colors.teal, "Positive"),
        (s.project.colors.burnt_orange, " Ending Thought "),
        tag=t.h4,
    )
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Mankind Problems"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Impact of AI"),
        (s.project.colors.bright_red + s.bold, "Big Impact of AI"),
        " => ",
        (s.project.colors.olive_green + s.bold, "Big Caution of AI"),
    )
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Caution of AI"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Caution of Human Rights "),
    )
    st_space(size=4)
    st_space(size=4)
    st_space(size=4)
    st_space(size=3)
    st_space(size=3)
    st_write(
        s.project.pres.paragraphs.p_xl,
        (s.project.colors.bright_red + s.bold, "Big Caution of Human Rights"),
        "=> ",
        (s.project.colors.olive_green + s.bold, "Big Caution of Human Rights "),
    )
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_space(size=3)
    st_write(s.project.pres.paragraphs.p_xl + s.project.colors.link_blue, "_._", link="https://docs.google.com/document/d/1lr8lS61ZY3lPxx8AiFWiBnoSXH9sZtfKg7asS3RJeHg/edit")
    st_space(size=3)
    st_space(size=3)
    st_image(uri="illustration_deep-learning-part-2_img10.png")
    st_space(size=3)
    st_space(size=1)
