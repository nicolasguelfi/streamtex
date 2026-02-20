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
        "Typed State Protocol",
        toc_lvl="2",
    )
    st_space(size=2)
    stx.st_graphviz(
        """
        digraph protocol {
            rankdir=LR;
            node [fontsize=10, fontname="serif", shape=box, style="rounded,filled"];
            edge [fontsize=9];

            plan [label="scenario_plan\\n\\ntyped elements + flows", fillcolor="#BEE3F8"];
            elem [label="elements\\n\\nid, type, construct code", fillcolor="#BEE3F8"];
            val [label="validation_result\\n\\npass/fail + violations\\nby element", fillcolor="#C6F6D5"];
            err [label="error_map\\n\\nviolations -> responsible\\nagents", fillcolor="#FED7D7"];

            plan -> elem [label="constrains"];
            elem -> val [label="assembles +\\nvalidates"];
            val -> err [label="maps violations"];
            err -> elem [label="targeted repair", style=dashed, color="#C53030"];

            plan_lbl [shape=plaintext, label="Parser writes", fontsize=8, fontcolor="#2c5282"];
            elem_lbl [shape=plaintext, label="5 Generators write", fontsize=8, fontcolor="#2c5282"];
            val_lbl [shape=plaintext, label="Simulator writes", fontsize=8, fontcolor="#2c5282"];
            err_lbl [shape=plaintext, label="Repair Agent writes", fontsize=8, fontcolor="#2c5282"];

            {rank=same; plan; plan_lbl;}
            {rank=same; elem; elem_lbl;}
            {rank=same; val; val_lbl;}
            {rank=same; err; err_lbl;}
        }
        """
    )
    st_space(size=2)
    st_write(
        bs.caption,
        "No natural language dialogue. Typed schemas enforce structural consistency.",
    )
    st_space(size=2)
