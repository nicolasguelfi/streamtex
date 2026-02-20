import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    caption = s.big + s.center_txt + s.italic

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Process Simulator",
        toc_lvl="2",
    )
    st_space(size=2)
    stx.st_graphviz(
        """
        digraph simulator {
            rankdir=LR;
            node [fontsize=10, fontname="serif", shape=box, style="rounded,filled"];
            edge [fontsize=9];

            model [label="Assembled\\nBPMN", fillcolor="#BEE3F8"];
            sim [label="Isolated Simulator\\n\\nevaluates model\\nvia token flow", fillcolor="#C6F6D5", penwidth=2];
            valid [label="All 6 levels pass", fillcolor="#C6F6D5", fontcolor="#276749"];
            violations [label="Operational manifestations:\\n- Deadlock scenarios\\n- Unreachable paths\\n- Unsynchronized token flows", fillcolor="#FED7D7", fontcolor="#C53030"];

            model -> sim;
            sim -> valid [label="pass", color="#276749", fontcolor="#276749"];
            sim -> violations [label="fail", color="#C53030", fontcolor="#C53030"];
            violations -> model [label="CoT-articulated\\ndiagnostic feedback", style=dashed, color="#C53030", fontcolor="#C53030"];
        }
        """
    )
    st_space(size=2)
    st_write(
        bs.caption,
        "Semantic correctness depends on execution behavior, not syntactic analysis alone.",
    )
    st_space(size=2)
