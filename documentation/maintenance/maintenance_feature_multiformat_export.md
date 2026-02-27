# Multi-Format Export — Feasibility Analysis

**Date**: 2026-02-27
**Status**: Analysis complete, implementation pending

## Objective

Create a local CLI script to export a StreamTeX project into multiple document formats:

- **LaTeX standalone** (article/report)
- **LaTeX Beamer** (presentation slides)
- **Markdown**
- **DOCX** (Word)
- **PPTX** (PowerPoint)

The export should be as complete and faithful as possible given each format's capabilities.

---

## 1. Current Architecture Analysis

### 1.1 No Intermediate Representation (AST)

StreamTeX has **no Abstract Syntax Tree**. Content flows directly:

```
Python API calls (st_write, st_list, st_grid, ...)
    → HTML string generation
        → Dual rendering:
            ├─ Channel 1: st.html() → Streamlit live display
            └─ Channel 2: HtmlExportBuffer → Self-contained HTML document
```

Every rendering function calls `_render(html_string)` which dispatches to both channels simultaneously. There is no semantic intermediate representation between the Python calls and the final HTML.

### 1.2 The Dual-Rendering Pipeline

The existing HTML export system (`streamtex/export.py`) captures all content:

| Component | Role |
|-----------|------|
| `HtmlExportBuffer` | Stack-based HTML fragment accumulator |
| `st_export` | Context manager that activates the buffer |
| `_render()` / `st_html()` | Single bridge — writes to both channels |
| `push_wrapper()` / `pop_wrapper()` | Nesting for containers (st_block, st_grid, st_list) |
| `generate_full_html()` | Produces self-contained HTML document |

### 1.3 Structured Data Already Available

Two components already have structured, non-HTML data:

| Component | Data Model | Directly Exportable |
|-----------|-----------|-------------------|
| **TOC** (`toc.py`) | `toc_entries()` → list of `{level, title, key_anchor}` | Yes — section hierarchy |
| **Bibliography** (`bib.py`) | `BibEntry` dataclass with all standard fields | Yes — BibTeX, RIS, JSON |

### 1.4 Content Elements by Semantic Type

| Element | API | HTML Output | Semantic Data Available |
|---------|-----|------------|------------------------|
| Headings | `st_write(style, text, tag=t.h1, toc_lvl="1")` | `<h1>text</h1>` | Text, level, anchor |
| Paragraphs | `st_write(style, text)` | `<div style="...">text</div>` | Text content |
| Inline mixed | `st_write(style, (s.bold, "word"), " text")` | `<div><span style="font-weight:bold">word</span> text</div>` | Text + inline styles |
| Lists | `st_list(lt.unordered)` + `l.item()` | `<ul><li>...</li></ul>` | Type (ul/ol), items, nesting |
| Grids | `st_grid(cols=N)` + `g.cell()` | `<div style="display:grid">...</div>` | Column count, cell contents |
| Code | `st_code(style, code=str, language=str)` | Pygments HTML with inline styles | Source code, language |
| Images | `st_image(uri=str, alt=str)` | `<img src="..." alt="...">` | URI, alt text, dimensions |
| Mermaid | `st_mermaid(source)` | SVG from mermaid.ink or `<pre>` fallback | Mermaid source code |
| PlantUML | `st_plantuml(source)` | SVG from server or `<pre>` fallback | PlantUML source code |
| TikZ | `st_tikz(source)` | SVG via LaTeX pipeline or `<pre>` fallback | TikZ source code |
| Spacing | `st_space("v", "2em")` | `<div style="padding-top:2em">` | Direction + size (visual only) |
| Containers | `st_block(style)` | `<div style="...">children</div>` | CSS styling (visual only) |

---

## 2. Two Export Strategies

### Strategy A: HTML Parsing (Post-Rendering)

Parse the existing HTML export output with BeautifulSoup (already a dependency).

```
StreamTeX project
    → Run st_export → HtmlExportBuffer → Full HTML document
        → BeautifulSoup parse
            → Walk DOM tree
                → Emit target format
```

**Advantages:**
- Works with 100% of existing content (including dynamic/computed content)
- No changes to the StreamTeX library needed
- Handles all edge cases (loops, conditionals, runtime data)

**Disadvantages:**
- Semantic information lost in HTML (a `<div>` could be a heading, paragraph, or container)
- Style information is CSS strings — must be parsed to extract bold, italic, etc.
- Diagrams are already rendered as SVG — cannot extract source code
- Code blocks are Pygments HTML — must reverse-engineer to get plain source

**Feasibility: 60-70%** content recovery for text-heavy projects.

### Strategy B: Python AST Walking (Pre-Rendering) — Recommended

Walk the Python AST of `build()` functions to extract semantic content before rendering.

```
StreamTeX project
    → Import block modules
        → ast.parse(build function)
            → Extract st_write(), st_list(), st_code(), st_image() calls
                → Build semantic tree
                    → Emit target format
```

**Advantages:**
- Preserves all semantic information (heading levels, list types, code language, diagram source)
- 80-85% of content is literal strings — directly extractable from AST
- Can combine with partial execution for dynamic content

**Disadvantages:**
- Dynamic content (loops, variables, computed DataFrames) requires execution context
- Style resolution needs importing `custom/styles.py` to resolve compositions
- Relative TOC levels (`toc_lvl="+1"`) need runtime tracking

**Feasibility: 75-85%** content recovery, higher for educational/documentation projects.

### Recommended: Hybrid Approach (B + A fallback)

1. **Primary**: AST walking for extractable content (string literals, metadata)
2. **Fallback**: Execute `build()` with a mock renderer that captures semantic events
3. **Last resort**: Parse HTML output for anything that escaped both

---

## 3. Content Extractability Assessment

### 3.1 By Block Type

| Block Category | % of Typical Projects | Extractability | Notes |
|---------------|----------------------|----------------|-------|
| Text-heavy (tutorials, docs) | 70% | 85-90% | Mostly string literals |
| Layout-heavy (grids, complex) | 15% | 75-80% | Grid structure extractable, CSS lossy |
| Data/Chart blocks | 10% | 40-60% | Requires execution for DataFrames |
| Interactive (widgets) | 5% | 30-40% | Widgets have no static representation |

### 3.2 By Target Format

| Source Element | Markdown | LaTeX | Beamer | DOCX | PPTX |
|---------------|----------|-------|--------|------|------|
| Headings (h1-h6) | `# Title` | `\section{Title}` | `\frametitle{Title}` | Heading styles | Slide titles |
| Paragraphs | Plain text | Plain text | `\begin{frame}` content | `add_paragraph()` | Text boxes |
| Bold/Italic | `**bold**` / `*italic*` | `\textbf{}` / `\textit{}` | Same | Run formatting | Run formatting |
| Unordered lists | `- item` | `\begin{itemize}` | Same | List style | Bullet shapes |
| Ordered lists | `1. item` | `\begin{enumerate}` | Same | List style | Numbered shapes |
| Code blocks | ` ```python ` | `\begin{lstlisting}` | `\begin{lstlisting}` | Monospace paragraph | Monospace text box |
| Images (URL) | `![alt](url)` | `\includegraphics` | `\includegraphics` | `add_picture()` | `add_picture()` |
| Images (local) | Embed or copy | Copy + `\includegraphics` | Same | Embed in DOCX | Embed in PPTX |
| Tables/Grids | Markdown table | `\begin{tabular}` | `\begin{tabular}` | `add_table()` | `add_table()` |
| Mermaid diagrams | `mermaid` code fence | PNG via mermaid-cli | PNG embedded | PNG embedded | PNG embedded |
| PlantUML diagrams | `plantuml` code fence | PNG via server | PNG embedded | PNG embedded | PNG embedded |
| TikZ diagrams | PNG fallback | Native `\begin{tikzpicture}` | Native | PNG fallback | PNG fallback |
| Links | `[text](url)` | `\href{url}{text}` | `\href{url}{text}` | `add_hyperlink()` | `add_hyperlink()` |
| Bibliography | Reference list | `\bibliography{}` | `\bibliography{}` | Formatted text | Formatted text |
| TOC | Generated from headings | `\tableofcontents` | `\tableofcontents` | Manual generation | N/A |
| Spacing | Blank lines | `\vspace{}` | `\vspace{}` | Paragraph spacing | Ignored |
| Colors/Styles | Lost | `\textcolor{}` (partial) | Partial | Run formatting | Run formatting |

### 3.3 Format Fidelity Estimate

| Format | Structural Fidelity | Visual Fidelity | Diagram Support | Overall |
|--------|-------------------|-----------------|----------------|---------|
| **Markdown** | 90% | 30% (no styling) | Source code only | 70% |
| **LaTeX standalone** | 95% | 60% (via packages) | TikZ native, others as images | 80% |
| **LaTeX Beamer** | 85% | 55% | TikZ native, others as images | 75% |
| **DOCX** | 85% | 50% | Images only | 70% |
| **PPTX** | 60% | 40% | Images only | 55% |

---

## 4. Recommended Python Libraries

### 4.1 Per-Format Libraries

| Format | Library | Version | License | Install | Maturity |
|--------|---------|---------|---------|---------|----------|
| **LaTeX** | PyLaTeX | 1.4.2 | MIT | `uv add pylatex` | Stable, active |
| **Beamer** | PyLaTeX + raw strings | — | MIT | Same as above | Workaround needed (known Beamer issues) |
| **Markdown** | Manual string generation | — | — | None | Trivial |
| **DOCX** | python-docx | 0.8.11 | MIT | `uv add python-docx` | Stable, de-facto standard |
| **PPTX** | python-pptx | 1.0.0 | MIT | `uv add python-pptx` | Stable, widely used |

### 4.2 Complementary Tools

| Tool | Purpose | Library | Notes |
|------|---------|---------|-------|
| HTML parsing | Parse HTML export as fallback | `beautifulsoup4` | **Already a dependency** |
| Pandoc conversion | Multi-format from Markdown | `pypandoc` | Requires Pandoc binary |
| HTML → PDF | High-fidelity PDF from HTML export | `weasyprint` | System dependencies (Cairo, Pango) |
| Diagram rendering | Mermaid → PNG for non-LaTeX exports | `mermaid-py` | **Already a dependency** |
| Template-based DOCX | Jinja2 templates in Word | `docxtpl` | Built on python-docx |

### 4.3 External Binary Dependencies

| Binary | Required For | Install |
|--------|-------------|---------|
| `pdflatex` / `xelatex` | LaTeX → PDF compilation | TeX Live / MacTeX |
| `pandoc` | Multi-format conversion (optional) | `brew install pandoc` |
| `mermaid-cli` (`mmdc`) | Mermaid → PNG/SVG (optional) | `npm install -g @mermaid-js/mermaid-cli` |
| PlantUML server | PlantUML → PNG/SVG | Already used via HTTP |

### 4.4 PyLaTeX Beamer Limitation

PyLaTeX has **known compilation failures** with `documentclass="beamer"` (GitHub issue #214). Two workarounds:

1. **Raw LaTeX injection** — Use PyLaTeX for document structure, inject raw `\begin{frame}...\end{frame}` strings
2. **Hybrid** — Generate the LaTeX source file with PyLaTeX, then manually adjust the preamble before compilation
3. **Alternative**: Generate Markdown → Pandoc → Beamer (more reliable for complex slides)

---

## 5. Proposed Architecture

### 5.1 Module Structure

```
streamtex/
  export_formats/                    # New package
    __init__.py                      # Public API: export_project()
    _ast_walker.py                   # Python AST walker for build() functions
    _content_model.py                # Semantic content tree (ContentNode dataclass)
    _style_resolver.py               # CSS string → semantic properties (bold, color, size)
    _diagram_renderer.py             # Diagram source → PNG/SVG for non-web formats
    markdown_exporter.py             # ContentNode tree → Markdown file
    latex_exporter.py                # ContentNode tree → LaTeX document
    beamer_exporter.py               # ContentNode tree → Beamer presentation
    docx_exporter.py                 # ContentNode tree → DOCX file
    pptx_exporter.py                 # ContentNode tree → PPTX file
```

### 5.2 Content Model (Intermediate Representation)

```python
@dataclass
class ContentNode:
    type: str               # "heading", "paragraph", "list", "code", "image",
                            # "grid", "diagram", "space", "container", "link"
    text: str = ""          # Text content (stripped of HTML)
    children: list = None   # Nested nodes (for lists, grids, containers)
    metadata: dict = None   # Format-specific data:
                            #   heading: {level: int, toc_anchor: str}
                            #   list: {list_type: "ul"|"ol"}
                            #   code: {language: str, line_numbers: bool}
                            #   image: {uri: str, alt: str, width: str}
                            #   diagram: {type: "mermaid"|"plantuml"|"tikz", source: str}
                            #   link: {url: str, text: str}
                            #   grid: {cols: int}
    style_hints: dict = None  # Semantic style properties extracted from CSS:
                              #   {bold: bool, italic: bool, color: str, font_size: str}
```

### 5.3 Export Pipeline

```
1. Load project
   └─ Import book.py → get module_list (ordered blocks)
   └─ Import custom/styles.py → resolve style compositions

2. For each block:
   ├─ AST walk build() → extract ContentNode tree (80% of content)
   ├─ Execute build() with mock renderer → capture remaining content
   └─ Merge results

3. Build document tree
   └─ TOC from toc_entries()
   └─ Bibliography from BibRegistry
   └─ Ordered list of block content trees

4. Export to target format
   └─ Markdown: string generation
   └─ LaTeX: PyLaTeX document construction
   └─ Beamer: PyLaTeX + raw frame injection
   └─ DOCX: python-docx document construction
   └─ PPTX: python-pptx slide construction
```

### 5.4 CLI Interface

```bash
# Export a project to all formats
uv run python -m streamtex.export_formats projects/AI4SE --format all

# Export to a specific format
uv run python -m streamtex.export_formats projects/AI4SE --format docx
uv run python -m streamtex.export_formats projects/AI4SE --format latex
uv run python -m streamtex.export_formats projects/AI4SE --format beamer
uv run python -m streamtex.export_formats projects/AI4SE --format markdown
uv run python -m streamtex.export_formats projects/AI4SE --format pptx

# Output directory (default: <project>/exports/)
uv run python -m streamtex.export_formats projects/AI4SE --format docx --output ./output/

# Options
--include-diagrams      # Render diagrams as images (requires mermaid-cli, plantuml server)
--include-bibliography   # Include formatted bibliography
--toc                   # Include table of contents
--template TEMPLATE     # Use custom template (DOCX/PPTX/LaTeX)
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Est. 2-3 days)

| Task | Description |
|------|------------|
| Content model | `ContentNode` dataclass + tree builder |
| AST walker | Walk `build()` functions, extract `st_write/st_list/st_code/st_image` calls |
| Style resolver | Parse CSS strings → semantic hints (bold, italic, color) |
| Markdown exporter | First exporter — validates the content model |
| CLI skeleton | `__main__.py` with argparse |

### Phase 2: Core Exporters (Est. 3-4 days)

| Task | Description |
|------|------------|
| LaTeX exporter | Full document with sections, lists, code (lstlisting), images |
| DOCX exporter | Headings, paragraphs, lists, code blocks, images, tables |
| Test suite | Unit tests per exporter + integration tests on manual_intro blocks |

### Phase 3: Presentation Formats (Est. 2-3 days)

| Task | Description |
|------|------------|
| Beamer exporter | Frame generation from page boundaries, TikZ native passthrough |
| PPTX exporter | Slide layout from page boundaries, image embedding |
| Diagram rendering | Mermaid/PlantUML → PNG pipeline for non-web formats |

### Phase 4: Polish (Est. 1-2 days)

| Task | Description |
|------|------------|
| Custom templates | Support user-provided DOCX/PPTX/LaTeX templates |
| Bibliography | BibTeX export for LaTeX, formatted references for others |
| TOC generation | Per-format TOC rendering |
| Documentation | CLI usage guide + cheatsheet section |

**Total estimate: 8-12 days** for full implementation.

---

## 7. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dynamic content in blocks (loops, variables) | Content missed by AST walker | Medium | Fallback to mock-renderer execution |
| PyLaTeX Beamer compilation failures | Beamer output broken | High | Use raw LaTeX strings for frames |
| Style composition complexity | Bold/italic/color not detected | Medium | Parse common CSS patterns (font-weight, font-style) |
| Diagram rendering dependencies | PNG not generated | Low | Graceful fallback to source code in code block |
| Relative `toc_lvl` ("+1", "-1") | Heading levels incorrect | Medium | Track state during AST walk |
| `from streamtex import *` masks builtins | AST resolution harder | Low | Known pattern, handle explicitly |
| Large images (base64 in blocks) | DOCX/PPTX file size | Low | Decode and embed as binary |

---

## 8. What Will NOT Be Exported

These elements have no meaningful static representation:

| Element | Reason |
|---------|--------|
| Streamlit widgets (buttons, sliders, selectbox) | Interactive-only, no static value |
| Pan/zoom state (Mermaid, PlantUML diagrams) | JavaScript runtime state |
| Dark mode / theme switching | CSS variable resolution |
| Sidebar navigation | Streamlit-specific UI |
| Block Inspector | Development tool |
| Zoom/width controls | Browser-specific CSS |
| Hover effects (link previews) | JavaScript-only |
| Animated transitions | CSS animations |

---

## 9. Decision Matrix

| Approach | Effort | Coverage | Maintenance | Recommendation |
|----------|--------|----------|-------------|----------------|
| **A: HTML parsing only** | Low (3-5d) | 60-70% | Low | Quick win, limited fidelity |
| **B: AST walking only** | Medium (6-8d) | 75-85% | Medium | Good for static content |
| **C: Hybrid (B + mock renderer + A fallback)** | High (8-12d) | 85-90% | Higher | Best coverage |
| **D: Pandoc from Markdown** | Low (2-3d) | 65-75% | Low | Good for DOCX/PDF via Markdown |

**Recommendation**: Start with **Phase 1 (Markdown) + Phase 2 (LaTeX + DOCX)** using AST walking (Strategy B). Add mock renderer and PPTX/Beamer later. This delivers 80% of the value in 50% of the time.

---

## 10. Dependencies to Add

```toml
# pyproject.toml — new optional dependency group
[project.optional-dependencies]
export = [
    "pylatex>=1.4",
    "python-docx>=0.8",
    "python-pptx>=1.0",
]
```

No changes to core dependencies. Export libraries are **optional** — only needed when running the export CLI.
