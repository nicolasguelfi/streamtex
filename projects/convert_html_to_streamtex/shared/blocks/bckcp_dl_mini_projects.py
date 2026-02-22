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
      #434343 -> s.project.colors.gray
      #4c1130 -> s.project.colors.dark_purple
      #666666 -> s.project.colors.gray
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "12.1. Mini-Projects ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.1. Project Subject - MNIST Product Line ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Field ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Title ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "MNIST Product Line Comparison ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Goal ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Define several variants of the MNIST neural networks of your choice ", "Train them ", "Compare the results with the other variants ", "Display the confusion matrices ", "Display the graphic of recognition level for some validation digits for all variants (cf. \"getFilteredDigits\" function) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "variants ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "with keras ", "with pytorch ")
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.2. Project Subject - FASHION MNIST ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Field ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Title ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "FASHION MNIST Recognition ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Goal ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Define several variants of the MNIST neural networks ", "focus on CNN and RESNET ", "Train them ", "Compare the results with the other variants ", "Display the confusion matrices ", "Display the graphic of recognition level for some validation digits for all variants (cf. \"getFilteredDigits\" function) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "code snippets ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "pytorch ", "torchvision.datasets.FashionMNIST ", "keras ", "tf.keras.datasets.fashion_mnist.load_data()  ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "advise ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "vA -> WITH reuse of the code done for MNIST ", "vB -> WITHOUT reuse of the code done for MNIST ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "links ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "pytorch ", "all datasets ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://pytorch.org/vision/stable/datasets.html#fashion-mnist"), "FashionMNIST github project ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://github.com/zalandoresearch/fashion-mnist"), "keras ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://www.tensorflow.org/datasets/catalog/fashion_mnist"))
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.3. Project Subject - RegressiveMNIST ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Field ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Title ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Regressive MNIST ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Goal ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Define a neural network to estimate the number of pixels over a threshold contained in an MNIST image. ", "i.e. how many pixels over 50 as grey level ", "Train it ", "Analyze the accuracy results and the errors distribution ", "Display the graphic of recognition level for some validation digits (cf. \"getFilteredDigits\" function)  ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "advise ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "vA -> WITH reuse of the code done for MNIST ", "vB -> WITHOUT reuse of the code done for MNIST ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.4. Project Subject - RegressiveCLIPS ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Field ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Title ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Regressive paper clips ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Goal ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Define a neural network that will be trained to estimate the number of paper clips contained in an MNIST image. ", "Train ", "Analyze the accuracy results and the error distribution ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "advise ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "vA -> WITH reuse of the code done for MNIST ", "vB -> WITHOUT reuse of the code done for MNIST ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "links ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "pytorch ", "all datasets ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://pytorch.org/vision/stable/datasets.html#fashion-mnist"), "FashionMNIST github project ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://github.com/zalandoresearch/fashion-mnist"), "keras ", (s.project.doc.links.link_body + s.project.colors.link_blue + s.bold, "HERE", "https://www.tensorflow.org/datasets/catalog/fashion_mnist"))
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.5. Project Subject - Reuse Open Source LLM ", tag=t.h3)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Field ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.forest_green + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Title ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Download and reuse an existing open source LLM ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "Goal ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Download an open source LLM ", "Use it locally to generate text based on your input ", "Advanced task: ", "Use it locally to have a chat that keeps the discussion history ", "More advanced task: ", "Fine tune it with some text corpus found on the web ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.dark_purple + s.bold, "advise ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "use chatGPT to help you design and implement the code ", "\"Can you give me the simplest pytorch code to import the smallest llama and use it locally?\" ", "\"where can I find open source input datasets to fine tune LLAMA such as Shakespeare text to make LLAMA generate texts in a Shakespeare like style and how to implement this in pytorch?\" ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "12.1.6. Project various information ", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "12.1.6.1. Fashion MNIST ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', ''Shirt', 'Sneaker', 'Bag', 'Ankle boot' ")
    st_space(size=1)
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
        with g.cell():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "12.1.6.2. paperCLIPS ", tag=t.h4)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "12.1.6.3. getFilteredDigits ", tag=t.h4)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "12.1.6.4. confusion matrix ", tag=t.h4)
    st_space(size=1)
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    st_space(size=1)
    st_space(size=1)
