---
title: "A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution"
subtitle: "MODELSWARD 2026"
date: "11 February 2026"
bibliography: agentic-bpmn-exec.bib
csl: ieee.csl
link-citations: true
colorlinks: true
editor: 
  render-on-save: true
format:
  beamer:
    author: "\\underline{Tiago Sousa}, Nicolas Guelfi and Benoît Ries"
    institute: "University of Luxembourg"
    incremental: false
    aspectratio: 169
    theme: "Frankfurt"
    colortheme: "rose"
    fonttheme: "serif"
    section-titles: false
    header-includes: |
      \usepackage{stmaryrd}
      \usepackage{pifont}
      \usepackage{tikz}
      \usepackage{pgfplots}
      \pgfplotsset{compat=1.18}
      \usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, decorations.pathreplacing, bpmn}
      \titlegraphic{\includegraphics[width=1.5cm]{./images/uni.png}}
      \setbeamertemplate{footline}[page number]
      \setbeamertemplate{headline}{}
    #  \setbeamerfont{section in toc}{size=\footnotesize}
    beameroption: "show notes on second screen"
    slide-level: 2
    output-file: "modelsward-presentation.pdf"
    bibliography: agentic-bpmn-exec.bib
---

# Introduction

## The Problem: Syntactically Valid, Semantically Broken

- **Misconfigured gateways**: parallel splits without corresponding joins

- **Improper event sequencing**: event-based gateways followed by tasks, not catching events

- **Malformed control flows**: deadlocks or unreachable activities

\vspace{0.5em}
\textit{LLM-generated BPMN looks correct but fails at runtime.} [@drakopoulosLLMsSpeakBPMN2025]

\vspace{0.5em}
Consider the most common violation:

## Misconfigured Gateway Logic

\begin{center}
\begin{tikzpicture}[
  node distance=0.7cm and 0.6cm,
  every node/.style={font=\scriptsize},
  bad gateway/.style={parallel gateway, draw=red!70!black, fill=red!15, line width=0.8pt},
  arr/.style={-{Stealth[length=2.5pt]}, thick, structure!70!black},
  badarr/.style={-{Stealth[length=2.5pt]}, thick, red!70!black, dashed},
]
  \node[start event] (start) {};
  \node[task, right=of start] (A) {Task A};
  \node[parallel gateway, right=of A] (split) {};
  \node[task, above right=0.6cm and 0.6cm of split] (B) {Task B};
  \node[task, right=of split] (C) {Task C};
  \node[task, below right=0.6cm and 0.6cm of split] (D) {Task D};
  \node[bad gateway, right=3.0cm of split] (join) {};
  \node[task, right=of join] (E) {Task E};
  \node[end event, right=of E] (end) {};

  \draw[arr] (start) -- (A);
  \draw[arr] (A) -- (split);
  \draw[arr] (split) |- (B);
  \draw[arr] (split) -- (C);
  \draw[arr] (split) |- (D);
  \draw[arr] (B) -| (join);
  \draw[arr] (C) -- (join);
  \draw[badarr] (D.east) -- ++(1.2,0) node[right, red!70!black, font=\tiny] {dead path};
  \draw[arr] (join) -- (E);
  \draw[arr] (E) -- (end);

  \node[below=0.15cm of split, anchor=north east, xshift=0.1cm, structure!70!black, font=\tiny\bfseries] {AND split (3)};
  \node[below=0.15cm of join, red!70!black, font=\tiny\bfseries] {AND join (2/3)};
  \node[below=0.9cm of join, red!70!black, font=\scriptsize\bfseries] {$\rightarrow$ Deadlock};
\end{tikzpicture}
\end{center}

\centering
AND split creates 3 paths $\rightarrow$ AND join expects 2 $\rightarrow$ deadlock.

## Why: Frege's Sense/Reference Distinction

::: {.columns}

::: {.column width="48%"}

::: {.block name="Sense (Sinn)"}
What BPMN *looks like* \newline \scriptsize The mode of presentation of meaning

- Distributional patterns
- Syntactic co-occurrences ($SYR_{BPMN}$)
- LLMs **capture** this
:::

:::

::: {.column width="48%"}

::: {.block name="Reference (Bedeutung)"}
What BPMN *means at runtime* \newline \scriptsize The actual object or state of affairs

- Token flow, synchronization ($SER_{BPMN}$)
- Reachability, denotational semantics
- LLMs **lack** this
:::

:::

:::

\centering
$\longleftarrow$ \textbf{semantic gap} [@ZeitschriftFuerPhilosophie1892; @bender2020climbing] $\longrightarrow$

\textit{Statistical pattern matching cannot ensure semantic correctness.}

# Related Work

## Related Work

- **Prompt engineering**: improves completeness, but fragile and model-dependent; no formal validation [@buschJustTellMe2023; @weiChainofThoughtPromptingElicits2023; @hassanRethinkingSoftwareEngineering2024]
- **Constrained decoding**: guarantees $SYR_{BPMN}$ (syntax) but cannot verify $SER_{BPMN}$ (semantics) [@shinConstrainedLanguageModels2021; @gengGrammarConstrainedDecodingStructured2023]
- **Multi-agent frameworks**: role-based specialization, but NL coordination lacks type constraints [@qianChatDevCommunicativeAgents2024; @wuAutoGenEnablingNextGen2023; @chenAgentVerseFacilitatingMultiAgent2023]

\vspace{0.5em}

\begin{block}{Gap}
All three approaches enforce \textit{sense} (distributional patterns). None enforce \textit{reference} (execution semantics).
\end{block}

# Methodology

## Approach Overview: From Sense Toward Reference

Three design principles:

\vspace{0.5em}

1. **Agent Specialization**: Narrow generation to type-specific constructs

2. **Hierarchical Validation**: Enforce semantic constraints via simulation

3. **CoT-Articulated Diagnostic Feedback**: Connect violations to execution consequences

\vspace{1em}
\textit{Each mechanism compensates for a specific limitation of distributional learning.}

## Five-Phase, Seven-Agent Architecture

\vspace*{\fill}
\begin{center}
\includegraphics[width=0.85\textwidth,height=0.8\textheight,keepaspectratio]{figures/methodology-phases.pdf}
\end{center}
\vspace*{\fill}

## Agent Specialization: Roles and Responsibilities

\begin{table}
\begin{tabular}{@{}p{0.24\textwidth}p{0.68\textwidth}@{}}
\toprule
Agent & Role \\
\midrule
\textbf{Scenario Parser} & NL $\rightarrow$ structured plan (entities, flows, types) \\[0.3em]
\textbf{5 Generators} & StartEvent, Task, Gateway, IntermediateEvent, EndEvent \\[0.3em]
\textbf{Collector / Validator} & Assembles elements; executes in simulator against validation hierarchy \\[0.3em]
\textbf{Repair Agent} & Analyzes failures via two-stage error mapping $\rightarrow$ targeted regeneration \\
\bottomrule
\end{tabular}
\end{table}

\vspace{0.5em}

Each generator operates on an **isolated subtask**, narrowing the generation space from all BPMN models to type-consistent configurations.

## Instruction Engineering

\begin{center}
\begin{tikzpicture}[
  every node/.style={font=\scriptsize},
  allbox/.style={rectangle, draw=structure!50, fill=structure!8, rounded corners=2pt,
    text width=2.2cm, align=center, inner sep=4pt, font=\tiny\ttfamily},
  subbox/.style={rectangle, draw=structure, fill=structure!20, rounded corners=2pt,
    text width=2.8cm, align=center, inner sep=5pt, font=\tiny},
  arr/.style={-{Stealth[length=3pt]}, thick, structure!60!black},
]
  \node[allbox] (all) at (0,0) {
    behavioral\\cognitive\\
    \textcolor{structure}{\bfseries gateway\_types}\\
    \textcolor{structure}{\bfseries split\_join\_pair}\\
    \textcolor{structure}{\bfseries token\_routing}\\
    \textcolor{gray!40}{event\_placement}\\
    \textcolor{gray!40}{task\_sequencing}\\
    \textcolor{gray!40}{error\_handling}\\
    \textcolor{gray!40}{termination}
  };
  \node[above=0.15cm of all, font=\scriptsize\bfseries, structure!70!black] {9 Rule Categories};

  \draw[arr] (1.8, 0) -- (3.2, 0) node[midway, above, font=\tiny] {filter by type};

  \node[subbox] (gw) at (5.5, 0) {
    \texttt{\bfseries gateway\_types}\\
    \texttt{\bfseries split\_join\_pairing}\\
    \texttt{\bfseries token\_routing}\\[3pt]
    + behavioral, cognitive\\
    + BPMN 2.0.2 exemplars
  };
  \node[above=0.15cm of gw, font=\scriptsize\bfseries, structure!70!black] {Gateway Agent};
\end{tikzpicture}
\end{center}

\centering
Selective exposure prevents prompt dilution: each agent sees only pertinent rules.

## Typed State Protocol

\begin{center}
\begin{tikzpicture}[
  every node/.style={font=\scriptsize},
  databox/.style={rectangle, draw=structure!60, fill=structure!10, rounded corners=2pt,
    text width=3.2cm, align=center, minimum height=1cm, inner sep=5pt},
  arr/.style={-{Stealth[length=3pt, width=2.5pt]}, semithick, structure!60!black},
  repairarr/.style={-{Stealth[length=3pt, width=2.5pt]}, semithick, red!60!black, dashed},
  lbl/.style={font=\tiny, fill=white, inner sep=1pt},
  aglbl/.style={font=\fontsize{5.5}{7}\selectfont\bfseries, structure!70!black},
]
  % Top-left: scenario_plan
  \node[databox] (plan) at (0, 0) {
    \texttt{\bfseries scenario\_plan}\\[2pt]
    {\tiny typed elements + flows}
  };
  \node[aglbl, below=2pt of plan] {Parser writes};

  % Top-right: elements
  \node[databox] (elem) at (5.2, 0) {
    \texttt{\bfseries elements}\\[2pt]
    {\tiny id, type, construct code}
  };
  \node[aglbl, below=2pt of elem] {5 Generators write};

  % Bottom-right: validation_result
  \node[databox] (val) at (5.2, -2.4) {
    \texttt{\bfseries validation\_result}\\[2pt]
    {\tiny pass/fail + violations by element}
  };
  \node[aglbl, below=2pt of val] {Simulator writes};

  % Bottom-left: error_map
  \node[databox] (err) at (0, -2.4) {
    \texttt{\bfseries error\_map}\\[2pt]
    {\tiny violations $\rightarrow$ responsible agents}
  };
  \node[aglbl, below=2pt of err] {Repair Agent writes};

  % Clockwise arrows
  \draw[arr] (plan.east) -- (elem.west) node[lbl, midway, above] {constrains};
  \draw[arr] ([xshift=3pt]elem.south east) -- ([xshift=3pt]val.north east)
    node[lbl, midway, right] {assembles + validates};
  \draw[arr] (val.west) -- (err.east) node[lbl, midway, above] {maps violations};
  \draw[repairarr] (err.north) to[out=50, in=230]
    node[lbl, pos=0.45, sloped, above, text=red!60!black] {targeted repair} (elem.south);
\end{tikzpicture}
\end{center}

\centering\scriptsize
No natural language dialogue. Typed schemas enforce structural consistency.

## Six-Level Semantic Validation Hierarchy

| Level | What it checks |
|:------|:---------------|
| 1. Syntactic | One start, $\geq 1$ end, full connectivity, no event-to-event flows |
| 2. Static Semantics | Type constraints, unique IDs, integrity |
| 3. Event Rules | Start: no in; End: no out; Intermediate: both |
| 4. Structural | Task sequence limits, no consecutive service tasks, error handling |
| 5. Topological | Split/join symmetry, loops, exclusivity |
| 6. Reachability | Forward from start, backward from end; dead ends, unreachable islands |

Levels 1--2 = $SYR_{BPMN}$ (syntax) \hfill Levels 3--6 = $SER_{BPMN}$ (semantics) \hfill \textbf{Fail-fast}

## Process Simulator

\begin{center}
\begin{tikzpicture}[
  every node/.style={font=\scriptsize},
  box/.style={rectangle, draw=structure, fill=structure!10, rounded corners=2pt,
    minimum height=0.7cm, inner sep=5pt},
  simbox/.style={rectangle, draw=structure!80!black, fill=structure!25, rounded corners=2pt,
    minimum height=1cm, minimum width=2.4cm, inner sep=5pt, font=\scriptsize\bfseries},
  violbox/.style={rectangle, draw=red!40!black, fill=red!8, rounded corners=2pt,
    inner sep=5pt, font=\tiny, align=left},
  ok/.style={rectangle, draw=green!50!black, fill=green!8, rounded corners=2pt,
    minimum height=0.35cm, inner sep=3pt, font=\tiny\bfseries},
  arr/.style={-{Stealth[length=3pt]}, thick, structure!60!black},
  greenarr/.style={-{Stealth[length=3pt]}, thick, green!50!black},
  redarr/.style={-{Stealth[length=3pt]}, thick, red!60!black},
  feedbackarr/.style={-{Stealth[length=3pt]}, thick, red!60!black, dashed},
]
  \node[box] (model) at (0, 0) {Assembled BPMN};
  \node[simbox] (sim) at (3.8, 0) {Isolated Simulator};
  \node[font=\tiny, text=structure!60!black, below=0.15cm of sim] {evaluates $\llbracket m \rrbracket$ via token flow};

  % Fork point east of simulator
  \coordinate (fork) at (5.8, 0);

  % Pass branch (upward)
  \node[ok] (valid) at (8.2, 0.9) {\ding{51} All 6 levels pass};

  % Fail branch (downward) - single grouped box
  \node[violbox] (violations) at (8.2, -1.2) {%
    \textbf{Operational manifestations:}\\[2pt]
    \textbullet~Deadlock scenarios\\
    \textbullet~Unreachable paths\\
    \textbullet~Unsynchronized token flows};

  % Arrows
  \draw[arr] (model) -- (sim);
  \draw[arr] (sim.east) -- (fork);
  \draw[greenarr] (fork) |- node[pos=0.25, right, font=\tiny, text=green!50!black] {pass} (valid.west);
  \draw[redarr] (fork) |- node[pos=0.25, right, font=\tiny, text=red!60!black] {fail} (violations.west);

  % Feedback loop: violations feed CoT diagnostic back to model
  \draw[feedbackarr] (violations.south) -- ++(0,-0.35) -| (model.south)
    node[pos=0.5, below, font=\tiny\itshape, text=red!60!black] {CoT-articulated diagnostic feedback};
\end{tikzpicture}
\end{center}

\centering
Semantic correctness depends on \textbf{execution behavior}, not syntactic analysis alone.

## CoT-Articulated Diagnostic Feedback

::: {.block name="Generic Feedback"}
\textit{``Path symmetry constraint violated.''}
:::

::: {.block name="CoT-Articulated Feedback"}
\textit{``Split gateway creates 3 paths but join expects 2 $\rightarrow$ token accumulation $\rightarrow$ deadlock. Fix: add third incoming flow to join.''}
:::

\vspace{0.5em}

**Repair loop:** \quad Generate $\rightarrow$ Validate $\rightarrow$ Map errors $\rightarrow$ Repair agents $\rightarrow$ Re-validate

# Evaluation & Results

## Experimental Setup

::: {.columns}

::: {.column width="50%"}

**Test Suite**

- 40 scenarios across 6 difficulty levels
- Aligned to validation hierarchy levels
- Total: $N = 360$ (40 $\times$ 9 models)

\vspace{0.5em}

**Baseline:** Monolithic single-prompt + post-hoc validation

**Proposed:** Full multi-agent architecture with iterative repair

:::

::: {.column width="50%"}

**9 LLMs Evaluated**

- GPT-5 [@openaiIntroducingGPT52025], GPT-5 Mini, GPT-5 Nano
- Gemini 2.5 Pro, Flash, Flash Lite [@comaniciGemini25Pushing2025]
- Grok-4 Fast
- Qwen3 Coder 30B [@yangQwen3TechnicalReport2025]
- GLM-4.6 [@teamGLM45AgenticReasoning2025]

:::

:::

## Agentic Architecture Nearly Doubles Semantic Conformance

::: {.columns}

::: {.column width="55%"}

\begin{center}
\begin{tikzpicture}
\begin{axis}[
  ybar,
  width=6.5cm,
  height=5.5cm,
  bar width=0.35cm,
  ymin=0, ymax=100,
  ylabel={Percentage (\%)},
  ylabel style={font=\scriptsize},
  symbolic x coords={Pass Rate, 1st Attempt, 1st Repair},
  xtick=data,
  x tick label style={font=\tiny, align=center},
  y tick label style={font=\tiny},
  legend style={font=\tiny, at={(0.5,1.02)}, anchor=south, legend columns=2},
  nodes near coords,
  nodes near coords style={font=\tiny},
  every axis plot/.append style={fill opacity=0.85},
  enlarge x limits=0.25,
]
\addplot[fill=structure!70, draw=structure] coordinates {(Pass Rate,84.2) (1st Attempt,25.0) (1st Repair,56.8)};
\addplot[fill=gray!40, draw=gray!60] coordinates {(Pass Rate,46.4) (1st Attempt,5.8) (1st Repair,8.0)};
\legend{Proposed, Baseline}
\end{axis}
\end{tikzpicture}
\end{center}

:::

::: {.column width="45%"}

\vspace{1.5em}

**\textcolor{structure}{+37.8 pp}** pass rate

\vspace{0.5em}

**\textcolor{structure}{331\%}** first-attempt improvement

\vspace{0.5em}

**\textcolor{structure}{7$\times$}** first-repair success

\vspace{1em}

\textit{Improves both initial generation and error recovery.}

:::

:::

## Conformance by Validation Level

\begin{center}
\begin{tikzpicture}
\begin{axis}[
  ybar,
  width=10cm,
  height=5.5cm,
  bar width=0.35cm,
  ymin=0, ymax=105,
  ylabel={Pass Rate (\%)},
  ylabel style={font=\scriptsize},
  symbolic x coords={Syntax, Static Sem., Event, Structural, Topological, Integration},
  xtick=data,
  x tick label style={font=\tiny, align=center},
  y tick label style={font=\tiny},
  legend style={font=\tiny, at={(0.98,0.98)}, anchor=north east},
  nodes near coords,
  nodes near coords style={font=\tiny},
  every axis plot/.append style={fill opacity=0.85},
  enlarge x limits=0.12,
]
\addplot[fill=structure!70, draw=structure] coordinates {(Syntax,95.2) (Static Sem.,88.9) (Event,88.9) (Structural,87.5) (Topological,75.7) (Integration,72.1)};
\addplot[fill=gray!40, draw=gray!60] coordinates {(Syntax,53.2) (Static Sem.,50.0) (Event,49.1) (Structural,48.6) (Topological,44.8) (Integration,40.5)};
\legend{Proposed, Baseline}
\end{axis}
% Braces for SYR and SER - positioned below the x-axis tick labels
\draw[decorate, decoration={brace, amplitude=4pt, mirror}, thick, structure!70!black] (0.55,-0.9) -- (2.8,-0.9) node[midway, below=4pt, font=\tiny] {$SYR_{BPMN}$};
\draw[decorate, decoration={brace, amplitude=4pt, mirror}, thick, structure!70!black] (3.1,-0.9) -- (8.8,-0.9) node[midway, below=4pt, font=\tiny] {$SER_{BPMN}$};
\end{tikzpicture}
\end{center}

\vspace{-0.5em}
\centering\small
+30.9 to +42.0 pp across all levels \quad $|$ \quad Declining gradient: local (95\%) $\rightarrow$ global (72\%)

## Per-Model Impact: Decomposition vs. Feedback

::: {.columns}

::: {.column width="48%"}

::: {.block name="Weaker Models: Decomposition"}
GLM-4.6: 15\% $\rightarrow$ 97.5\% \textbf{(+82.5 pp)}

Flash Lite: 0\% $\rightarrow$ 82.5\% \textbf{(+82.5 pp)}

\vspace{0.3em}
\textit{Architecture compensates for limited base capabilities.}
:::

:::

::: {.column width="48%"}

::: {.block name="Stronger Models: CoT Feedback"}
GPT-5: 97.5\% $\rightarrow$ 92.5\%, but self-correction: 15\% $\rightarrow$ \textbf{67.5\%}

Nano: 57.5\% (still +7.5 pp)

\vspace{0.3em}
\textit{CoT feedback improves error recovery, not initial generation.}
:::

:::

:::

\vspace{0.5em}
\centering
Best overall: Gemini 2.5 Pro \& GLM-4.6 at 97.5\% \quad $|$ \quad Weakest: GPT-5 Nano at 57.5\%

## Validation Efficiency

::: {.columns}

::: {.column width="55%"}

| Metric | Proposed | Baseline |
|:-------|:--------:|:--------:|
| Avg repair attempts | **0.66** | 1.99 |
| Avg validation attempts | **1.54** | 2.54 |
| Self-correction rate | **29.2%** | 3.9% |

:::

::: {.column width="45%"}

\vspace{1em}

67% fewer repairs

39% fewer validations

+25.3 pp self-correction

:::

:::

\vspace{1em}
Execution time: +35\% (86s vs. 64s), modest overhead for +38 pp gain

# Discussion

## Limitations and Future Directions

\begin{center}
\begin{tikzpicture}[
  every node/.style={font=\scriptsize},
  lim/.style={rectangle, draw=red!25, fill=red!3, rounded corners=2pt,
    text width=4.8cm, align=left, inner sep=5pt},
  fut/.style={rectangle, draw=structure!50, fill=structure!8, rounded corners=2pt,
    text width=4cm, align=left, inner sep=5pt},
  arr/.style={-{Stealth[length=2.5pt]}, semithick, structure!50!black},
]
  \node[font=\scriptsize\bfseries, red!40!black] at (-2.5, 1.9) {Current Limitation};
  \node[font=\scriptsize\bfseries, structure!70!black] at (3.8, 1.9) {Future Direction};

  \node[lim] (l1) at (-2.5, 1.05) {\textbf{Standardized prompts}\\limits performance ceiling};
  \node[fut] (f1) at (3.8, 1.05) {Model-specific prompt\\optimization};
  \draw[arr] (l1.east) -- (f1.west);

  \node[lim] (l2) at (-2.5, -0.05) {\textbf{Global constraints hardest}\\topological/integration at 72--76\%};
  \node[fut] (f2) at (3.8, -0.05) {Emerging verification\\approaches};
  \draw[arr] (l2.east) -- (f2.west);

  \node[lim] (l3) at (-2.5, -1.15) {\textbf{Spec-derived test suite}\\no industrial processes};
  \node[fut] (f3) at (3.8, -1.15) {Industrial-scale\\validation};
  \draw[arr] (l3.east) -- (f3.west);
\end{tikzpicture}
\end{center}

# Conclusion

## Conclusion: From Sense to Reference

Three architectural mechanisms bridge the semantic gap:

\vspace{0.5em}

1. **Agent specialization** $\rightarrow$ better initial conformance (25.0% vs. 5.8% first-attempt)

2. **Hierarchical validation** $\rightarrow$ systematic $SER_{BPMN}$ checking via simulation

3. **CoT feedback** $\rightarrow$ 7$\times$ first-repair success rate

\vspace{1em}

\centering
**Up to 70 pp improvement across 9 diverse LLM architectures.**

## {.plain}

\vspace{2em}

\centering

\Large A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution

\normalsize

\vspace{1em}

\underline{Tiago Sousa}, Nicolas Guelfi, Benoît Ries

University of Luxembourg


\vspace{2em}

\Large \textbf{Questions?}


:::: allowframebreaks

# References

::: {#refs}
:::
::::