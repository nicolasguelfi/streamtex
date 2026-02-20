import streamlit as st
from streamtex import *
import streamtex as stx
from custom.styles import Styles as s
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt


class BlockStyles:
    body = s.big
    caption = s.medium + s.center_txt + s.italic + s.project.colors.gray_baseline

bs = BlockStyles


def build():
    st_write(
        s.project.titles.slide_title,
        "Five-Phase, Seven-Agent Architecture",
        toc_lvl="2",
    )
    st_space(size=2)
    stx.st_graphviz(
        """
        digraph phases {
            rankdir=LR;
            node [fontsize=10, fontname="serif", shape=box, style="rounded,filled"];
            edge [fontsize=8];

            P1 [label="Phase 1\\nScenario\\nParsing", fillcolor="#BEE3F8"];
            P2 [label="Phase 2\\nElement\\nGeneration", fillcolor="#BEE3F8"];
            P3 [label="Phase 3\\nAssembly &\\nValidation", fillcolor="#C6F6D5"];
            P4 [label="Phase 4\\nError\\nMapping", fillcolor="#FED7D7"];
            P5 [label="Phase 5\\nTargeted\\nRepair", fillcolor="#FEFCBF"];

            P1 -> P2 [label="scenario_plan"];
            P2 -> P3 [label="elements"];
            P3 -> P4 [label="violations", style=dashed, color="#C53030"];
            P4 -> P5 [label="error_map", style=dashed, color="#C53030"];
            P5 -> P3 [label="repaired elements", style=dashed, color="#DD6B20"];

            subgraph cluster_agents {
                label="7 Agents";
                fontsize=9;
                style=dashed;
                color="#718096";

                SP [label="Scenario\\nParser", shape=ellipse, fillcolor="#E2E8F0"];
                G1 [label="StartEvent\\nGenerator", shape=ellipse, fillcolor="#E2E8F0"];
                G2 [label="Task\\nGenerator", shape=ellipse, fillcolor="#E2E8F0"];
                G3 [label="Gateway\\nGenerator", shape=ellipse, fillcolor="#E2E8F0"];
                G4 [label="IntermEvent\\nGenerator", shape=ellipse, fillcolor="#E2E8F0"];
                G5 [label="EndEvent\\nGenerator", shape=ellipse, fillcolor="#E2E8F0"];
                CV [label="Collector /\\nValidator", shape=ellipse, fillcolor="#E2E8F0"];
                RA [label="Repair\\nAgent", shape=ellipse, fillcolor="#E2E8F0"];
            }
        }
        """
    )
    st_space(size=1)
    st_write(
        bs.caption,
        "Five phases with iterative repair loop between validation and generation.",
    )
    st_space(size=2)
