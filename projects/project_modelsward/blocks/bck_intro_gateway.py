import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    caption = s.big + s.center_txt + s.project.colors.red_error

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Misconfigured Gateway Logic",
        toc_lvl="2",
    )
    st_space(size=2)
    stx.st_graphviz(
        """
        digraph G {
            rankdir=LR;
            node [fontsize=10, fontname="serif"];
            edge [fontsize=8];

            start [shape=circle, label="", width=0.3, style=filled, fillcolor="#68d391"];
            A [shape=box, label="Task A", style="rounded,filled", fillcolor="#EBF8FF"];
            split [shape=diamond, label="+", style=filled, fillcolor="#BEE3F8"];
            B [shape=box, label="Task B", style="rounded,filled", fillcolor="#EBF8FF"];
            C [shape=box, label="Task C", style="rounded,filled", fillcolor="#EBF8FF"];
            D [shape=box, label="Task D", style="rounded,filled", fillcolor="#EBF8FF"];
            join [shape=diamond, label="+", style=filled, fillcolor="#FED7D7", color="#C53030", penwidth=2];
            E [shape=box, label="Task E", style="rounded,filled", fillcolor="#EBF8FF"];
            end_node [shape=doublecircle, label="", width=0.3, style=filled, fillcolor="#FC8181"];

            start -> A;
            A -> split;
            split -> B;
            split -> C;
            split -> D;
            B -> join;
            C -> join;
            D -> dead [style=dashed, color="#C53030", label="dead path"];
            dead [shape=plaintext, label="dead path", fontcolor="#C53030"];
            join -> E;
            E -> end_node;

            split_label [shape=plaintext, label="AND split (3)", fontcolor="#2c5282"];
            join_label [shape=plaintext, label="AND join (2/3)\\nDeadlock!", fontcolor="#C53030"];

            {rank=same; split; split_label;}
            {rank=same; join; join_label;}
        }
        """
    )
    st_space(size=2)
    st_write(
        bs.caption,
        "AND split creates 3 paths -> AND join expects 2 -> deadlock.",
    )
    st_space(size=2)
