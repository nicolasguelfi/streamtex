stx.st_latex_doc(r"""
\section{Mathematical Content}

\subsection{Equations}

The Cauchy-Schwarz inequality states:

$$\left(\sum_{k=1}^{n} a_k b_k\right)^2 \leq
  \left(\sum_{k=1}^{n} a_k^2\right)
  \left(\sum_{k=1}^{n} b_k^2\right)$$

\subsection{Theorem Environment}

\begin{quote}
\textbf{Theorem} (Fundamental Theorem of Calculus).
Let $f$ be a continuous function on $[a,b]$. Then:
$$\int_a^b f(x)\,dx = F(b) - F(a)$$
where $F$ is any antiderivative of $f$.
\end{quote}

\subsection{Constants}

Some fundamental constants:

\begin{itemize}
  \item Pi: $\pi \approx 3.14159$
  \item Euler's number: $e \approx 2.71828$
  \item Golden ratio: $\varphi \approx 1.61803$
\end{itemize}
""", height=600, light_bg=True, hyphenate=False)
