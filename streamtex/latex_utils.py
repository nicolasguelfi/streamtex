"""LaTeX parsing utilities — pure regex extraction, no rendering."""

import re

# ---------------------------------------------------------------------------
# TikZ extraction
# ---------------------------------------------------------------------------

_TIKZ_RE = re.compile(
    r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
    re.DOTALL,
)


def extract_tikz(code: str) -> list[str]:
    r"""Extract ``\begin{tikzpicture}...\end{tikzpicture}`` blocks."""
    return _TIKZ_RE.findall(code)


# ---------------------------------------------------------------------------
# Math extraction
# ---------------------------------------------------------------------------

# Order matters: $$ before $ to avoid partial matches.
_MATH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\$\$(.+?)\$\$", re.DOTALL),       # display $$...$$
    re.compile(r"\\\[(.+?)\\\]", re.DOTALL),        # display \[...\]
    re.compile(r"\\\((.+?)\\\)", re.DOTALL),         # inline \(...\)
    re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL),  # inline $...$
]


def extract_math(code: str) -> list[str]:
    r"""Extract math formulas: ``$...$``, ``$$...$$``, ``\[...\]``, ``\(...\)``."""
    results: list[str] = []
    for pat in _MATH_PATTERNS:
        results.extend(pat.findall(code))
    return results


# ---------------------------------------------------------------------------
# Beamer frame extraction
# ---------------------------------------------------------------------------

_FRAME_RE = re.compile(
    r"\\begin\{frame\}.*?\\end\{frame\}",
    re.DOTALL,
)


def extract_frames(code: str) -> list[str]:
    r"""Extract Beamer ``\begin{frame}...\end{frame}`` blocks."""
    return _FRAME_RE.findall(code)


# ---------------------------------------------------------------------------
# Document detection & stripping
# ---------------------------------------------------------------------------

_DOCCLASS_RE = re.compile(r"\\documentclass")
_BEGIN_DOC_RE = re.compile(r"\\begin\{document\}")
_BODY_RE = re.compile(
    r"\\begin\{document\}(.*?)\\end\{document\}",
    re.DOTALL,
)


def is_full_document(code: str) -> bool:
    r"""Return True if *code* contains ``\documentclass`` or ``\begin{document}``."""
    return bool(_DOCCLASS_RE.search(code) or _BEGIN_DOC_RE.search(code))


def strip_document_wrapper(code: str) -> str:
    r"""Return the body between ``\begin{document}`` and ``\end{document}``.

    If no wrapper is found the original *code* is returned unchanged.
    """
    m = _BODY_RE.search(code)
    if m:
        return m.group(1).strip()
    return code
