"""Unit tests for streamtex.latex_utils — pure LaTeX parsing utilities."""

from streamtex.latex_utils import (
    extract_frames,
    extract_math,
    extract_tikz,
    is_full_document,
    strip_document_wrapper,
)


# ---------------------------------------------------------------------------
# extract_tikz
# ---------------------------------------------------------------------------

class TestExtractTikz:
    def test_single_block(self):
        code = r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}"
        result = extract_tikz(code)
        assert len(result) == 1
        assert r"\draw (0,0) -- (1,1);" in result[0]

    def test_multiple_blocks(self):
        code = (
            r"\begin{tikzpicture}\draw (0,0);\end{tikzpicture}"
            " some text "
            r"\begin{tikzpicture}\draw (1,1);\end{tikzpicture}"
        )
        assert len(extract_tikz(code)) == 2

    def test_no_tikz(self):
        assert extract_tikz("Hello world") == []

    def test_multiline(self):
        code = "\\begin{tikzpicture}\n  \\draw (0,0) -- (1,1);\n\\end{tikzpicture}"
        result = extract_tikz(code)
        assert len(result) == 1
        assert "\\draw" in result[0]


# ---------------------------------------------------------------------------
# extract_math
# ---------------------------------------------------------------------------

class TestExtractMath:
    def test_inline_dollar(self):
        code = "The formula $E = mc^2$ is famous."
        result = extract_math(code)
        assert any("E = mc^2" in m for m in result)

    def test_display_double_dollar(self):
        code = "Display: $$\\int_0^1 f(x) dx$$"
        result = extract_math(code)
        assert any("\\int_0^1 f(x) dx" in m for m in result)

    def test_display_bracket(self):
        code = "Display: \\[a^2 + b^2 = c^2\\]"
        result = extract_math(code)
        assert any("a^2 + b^2 = c^2" in m for m in result)

    def test_inline_paren(self):
        code = "Inline \\(x + y\\) formula."
        result = extract_math(code)
        assert any("x + y" in m for m in result)

    def test_no_math(self):
        assert extract_math("No math here.") == []


# ---------------------------------------------------------------------------
# extract_frames
# ---------------------------------------------------------------------------

class TestExtractFrames:
    def test_single_frame(self):
        code = "\\begin{frame}\n\\frametitle{Title}\nContent\n\\end{frame}"
        result = extract_frames(code)
        assert len(result) == 1
        assert "\\frametitle{Title}" in result[0]

    def test_multiple_frames(self):
        code = (
            "\\begin{frame}A\\end{frame}"
            " preamble "
            "\\begin{frame}B\\end{frame}"
        )
        assert len(extract_frames(code)) == 2

    def test_no_frames(self):
        assert extract_frames("\\section{Intro}") == []


# ---------------------------------------------------------------------------
# is_full_document
# ---------------------------------------------------------------------------

class TestIsFullDocument:
    def test_documentclass(self):
        assert is_full_document("\\documentclass{article}\n\\begin{document}\nHi\n\\end{document}")

    def test_begin_document(self):
        assert is_full_document("\\begin{document}\nHi\n\\end{document}")

    def test_fragment(self):
        assert not is_full_document("\\section{Intro}\nSome text.")

    def test_empty(self):
        assert not is_full_document("")


# ---------------------------------------------------------------------------
# strip_document_wrapper
# ---------------------------------------------------------------------------

class TestStripDocumentWrapper:
    def test_strips_wrapper(self):
        code = "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}"
        result = strip_document_wrapper(code)
        assert result == "Hello World"
        assert "\\begin{document}" not in result
        assert "\\end{document}" not in result

    def test_no_wrapper_returns_unchanged(self):
        code = "\\section{Intro}\nSome text."
        assert strip_document_wrapper(code) == code
