import streamlit as st
from streamtex import *
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

data = [
    ["Order", "TaskCategory", "TaskDescription", "HR", "EST"],
    ["1", "SOTA", "Read SOTA on prompt engineering for LLM on OpenAI website; experiment with the techniques in the context.", "AF", "4.0"],
    ["2", "SOTA", "Do a SOTA of LLM-based MCQ generation and evaluation approaches. Selection criteria: journal paper (15 to 30+ pages), high scientific quality, accessible open-source project. Output in a Google Sheet; add some columns based on your BSP goals (MCQ generation/evaluation + NN model type, libraries like PyTorch/Keras, etc.). Add a column for usefulness classification (1/2/3).", "AF", "6.0"],
    ["3", "Environment Setup", "Install a Python environment on a personal computer with the OpenAI library. Experiment with the API using the key (to be stored in a local variable), make a query, and catch the output.", "AF", "2.0"],
    ["4", "Knowledge Synthesis", "Write a short synthesis of knowledge acquired in a Google Doc.", "AF", "4.0"],
    ["5", "SOTA", "Perform a SOTA of GitHub projects on MCQ generation and evaluation.", "AF", "6.0"],
    ["6", "Knowledge Synthesis", "Write a short synthesis of knowledge acquired in the SOTA.", "AF", "2.0"],
    ["7", "Software Description", "Description des fonctions du logiciel que tu proposerais - inclure les références soit aux projets GitHub soit aux papiers du SOTA - préciser les grandes lignes pour la conception.", "AF", "4.0"],
    ["8", "MCQ Creation", "Write MCQ questions about LLM learning for a starting-level audience.", "AF", "2.0"],
    ["9", "Documentation", "Write the terminology in your report.", "AF", "3.0"]
]

class BStyles:
         center_txt = s.text.alignments.center_align
         bold = s.text.weights.bold_weight
bs = BStyles

def build():

    with st_block(bs.center_txt):
        st_write(s.text.colors.green + s.text.sizes.huge_size + bs.center_txt + bs.bold,
                    "Game - Your Profile", tag=t.h2,
                    toc_lvl='2') 
        st_image(uri = "goats_01.png")
        
        with st_grid(2,
            grid_style=s.text.sizes.Large_size + ns("background-color: #ead1dc;") + s.container.margins.size("0", "36pt") + s.container.sizes.width_auto,
            cell_styles=s.text.alignments.center_align + bs.bold) as g:
            with g.cell():
                st_write(s.project.colors.bronze_01, "Jeu - présentation individuelle")
            with g.cell():
                st_write(s.project.colors.blue_01, "Click HERE & RightClick & ",
                        (s.project.colors.red_01, "Open!"),
                        link="https://docs.google.com/forms/d/e/1FAIpQLScl5M6-u2lykUAxh_DRZAxuIvUewTSOUTNmpMBOpzvJ-AbvvA/viewform")
        
        st_write(s.text.decors.italic_text + s.text.sizes.large_size + bs.center_txt,
                 "(Check the 'end of game link' to see the results)")
    
    #html += st_sheet("https://docs.google.com/spreadsheets/d/1_NZyEhhMQXAwew2mwJcu-oeBtNzW0PPFi2PcnVOOsFg/edit?usp=sharing",
    #                 os.path.join(cfg.documents_path,"sheet_key.json"),
    #                 "Sheet1!A1:E10",
    #                 style_grid=sg.create("A1:A10", s.text.sizes.large_size),
    #                 fetch_styles=True,
    #                 override_styles=True)
    


   # html += st_table(cell_styles=sg.create("A1:E10", s.text.sizes.large_size) * sg.create("A1:C10, E10", s.text.colors.white_color + s.container.bg_colors.red_bg_color) ,
    #                block_list=data)
