# StreamTeX Presentation Cheatsheet

Quick reference for creating presentations with StreamTeX + Claude AI skills.

---

## 1. Workflow at a Glance

```
┌─────────────────────────────────────────────────────┐
│  /stx-project:project-init "description..."             │  ← Generate full project
│           ↓                                         │
│  /stx-designer:slide-audit                              │  ← Validate all slides
│           ↓                                         │
│  /stx-designer:slide-fix                                │  ← Auto-fix violations
│           ↓                                         │
│  /stx-designer:slide-new "bck_name — description..."     │  ← Refine one slide
│           ↓                                         │
│  stx run                                            │  ← Preview
│           ↓                                         │
│  /stx-project:project-customize "changes..."            │  ← Adjust theme/fonts
│           ↓                                         │
│  /stx-designer:style-audit + style-refactor             │  ← Ensure consistency
└─────────────────────────────────────────────────────┘
```

---

## 2. Key Commands

### Create a full project

```bash
/stx-project:project-init "Short presentation 'Discover StreamTeX'
  for a general audience. 5 slides, dark theme. Slides:
  1) Title, 2) The Problem, 3) The Solution, 4) Demo, 5) Getting Started.
  Use L1/L2/L3 grid. Generate image prompts."
```

### Create or refine a single slide

```bash
/stx-designer:slide-new "bck_solution — StreamTeX presentation with
  responsive 2-column grid: left = illustration, right = 4 keyword
  bullets. Headline in L1, transition question in L3."
```

### Audit and fix

```bash
/stx-designer:slide-audit       # Check all blocks against design rules
/stx-designer:slide-fix         # Auto-fix violations (spacing, line length, styles)
/stx-designer:style-audit       # Check style consistency across all blocks
/stx-designer:style-refactor    # Extract inline CSS into reusable styles
/stx-designer:block-preview     # Validate block structure (imports, BlockStyles, build)
```

### Customize the project

```bash
/stx-project:project-customize "Switch to teal/orange palette, 48pt body for auditorium"
/stx-project:project-upgrade    # Upgrade to latest StreamTeX conventions
```

### Run

```bash
stx run
```

---

## 3. Slide Grid System (L1 / L2 / L3)

Every slide follows a 3-row grid. Use 1, 2, or all 3 rows.

```
┌─────────────────────────────────────────┐
│  L1 — Headline / citation / hook        │  Full width, centered
├───────────────────┬─────────────────────┤
│  L2C1 — Image     │  L2C2 — Text list   │  50/50, responsive
├───────────────────┴─────────────────────┤
│  L3 — Question / transition / teaser    │  Full width, centered
└─────────────────────────────────────────┘
```

### Row Usage Guide

| Slide type | Rows | Description |
|---|---|---|
| Title | L1 | Title + subtitle + author |
| Content | L1 + L2 | Headline + image/text grid |
| Full | L1 + L2 + L3 | Headline + content + question |
| Quote | L1 | Citation + attribution |
| Question | L1 + L3 | Statement + open question |
| Conclusion | L1 + L2 | Key takeaways + next steps |

### Implementation

```python
def build():
    with st_block(s.center_txt):
        # === L1 — Headline ===
        st_write(bs.headline, "Key Message", tag=t.div, toc_lvl="2")
        st_space(size=2)

        # === L2 — Two-column content ===
        with st_grid(
            cols="repeat(auto-fit, minmax(350px, 1fr))",
            gap="24px",
        ) as g:
            with g.cell():
                st_image(uri="static/images/bck_topic.png", width="100%")
            with g.cell():
                with st_list(l_style=bs.body, li_style=bs.body,
                             list_type=lt.unordered) as l:
                    with l.item():
                        st_write(bs.body, (bs.keyword, "Key"), " — point")
                    with l.item():
                        st_write(bs.body, "Second point")
                    with l.item():
                        st_write(bs.body, "Third point")

        st_space(size=2)

        # === L3 — Transition ===
        st_write(bs.question, "What does this mean for...?", tag=t.div)
```

---

## 4. Font Size Reference

| Element | Size | Style | When to use |
|---|---|---|---|
| Course title | 96pt | `s.Huge` | Title slide only |
| Section title | 80pt | `s.huge` | Slide headlines |
| Subtitle | 48pt | `s.Large + s.bold` | Sub-headings |
| Body text | 32pt | `s.large` | Default for all content |
| Body (minimum) | 24pt | `s.big` | Only if space is tight |
| Body (auditorium) | 48pt | `s.Large` | Projection at 10-20m |
| Decorative | 128pt+ | `s.Giant` / `s.GIANT` | Single words only |

> **Rule**: Never go below 24pt. If content needs smaller, split the slide.

---

## 5. Dark Theme Defaults

```python
# custom/styles.py — Dark palette example
class DarkTheme:
    bg_primary = ns("background-color: #1a1a2e;", "dark_bg")
    bg_secondary = ns("background-color: #16213e;", "dark_bg2")
    text_primary = ns("color: #e8e8e8;", "dark_txt")
    text_accent = ns("color: #00d4ff;", "dark_accent")
    text_highlight = ns("color: #e94560;", "dark_highlight")
    text_muted = ns("color: #8892b0;", "dark_muted")
```

> **Rule**: NEVER hardcode `color: black` or `background: white`. Use theme-aware styles.

---

## 6. Text Style Rules

| Rule | Limit |
|---|---|
| Words per bullet | 3–7 max |
| Bullets per list | 3–5 max |
| Style | Telegraphic / keywords — no full sentences |
| Bold colored keywords | 1–2 per bullet max |
| Emojis | 0–1 per slide max |

### Bold Keyword Pattern

```python
# Define in BlockStyles
keyword = s.bold + s.project.colors.accent

# Use in content
with l.item():
    st_write(bs.body, (bs.keyword, "Docker"), " — containerize apps")
```

---

## 7. BlockStyles Template

```python
class BlockStyles:
    """Slide: Topic Name."""
    # L1
    headline = s.project.slide.headline           # or s.huge + s.bold + s.center_txt
    # L2
    body = s.project.slide.body                    # or s.large
    keyword = s.project.slide.keyword              # or s.bold + s.project.colors.accent
    # L3
    question = s.project.slide.question            # or s.big + s.italic + s.center_txt
    # Block-specific only:
    special = s.project.colors.highlight + s.bold + s.Large
bs = BlockStyles
```

> **Rule**: `BlockStyles` only composes project-level styles. Never create raw CSS here.

---

## 8. Image Handling

### With images

```python
st_image(uri="static/images/bck_architecture.png", width="100%")
```

Naming convention: `static/images/bck_{description}.png`

### AI-generated images

```python
# Declarative — generate + display (requires streamtex[ai] + AIImageConfig in book.py)
st_ai_image("Flat vector illustration of microservices architecture, dark bg, cyan accent")

# With overrides
st_ai_image("A futuristic dashboard", provider="google", size="1024x1024")

# Interactive widget — user types prompt in the browser
st_ai_image_widget(default_prompt="A modern cloud architecture diagram")

# Programmatic — generate to file, then use st_image
from streamtex import generate_image
path = generate_image("Minimalist AI brain illustration", provider="openai")
st_image(uri=path, width="100%")
```

### Without images (placeholder + prompt)

```python
with g.cell():
    st_write(bs.placeholder, "[Image: architecture diagram]", tag=t.div)
    # IMAGE PROMPT: "Flat vector illustration of microservices
    #   architecture, dark bg (#1a1a2e), cyan accent (#00d4ff),
    #   minimalist, no text, 16:9 aspect ratio"
    # FILENAME: static/images/bck_architecture.png
```

---

## 9. Slide Breaks

```python
# Between sections within a single block
st_slide_break(marker_label="concept_details")

# Modes
st_slide_break()                                              # Full (rule + spacer + marker)
st_slide_break(config=SlideBreakConfig(mode=SlideBreakMode.MARKER_ONLY))  # Hidden marker
```

---

## 10. Responsive Grid

```python
# CORRECT — wraps on narrow screens
with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", gap="24px") as g:
    ...

# CORRECT — using project preset
with st_grid(cols=s.project.containers.responsive_2col, gap="24px") as g:
    ...

# WRONG — never wraps
with st_grid(cols=2) as g:
    ...
```

Stacking order on narrow screens: L1 → L2C1 (image) → L2C2 (text) → L3

---

## 11. Block File Template (Copy-Paste Ready)

```python
"""Slide: Topic Description."""
from streamtex import *
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """Slide: Topic Description."""
    headline = s.project.slide.headline
    body = s.project.slide.body
    keyword = s.project.slide.keyword
    question = s.project.slide.question
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        # === L1 ===
        st_write(bs.headline, "Title", tag=t.div, toc_lvl="2")
        st_space(size=2)

        # === L2 ===
        with st_grid(
            cols="repeat(auto-fit, minmax(350px, 1fr))",
            gap="24px",
        ) as g:
            with g.cell():
                st_image(uri="static/images/bck_topic.png", width="100%")
            with g.cell():
                with st_list(l_style=bs.body, li_style=bs.body,
                             list_type=lt.unordered) as l:
                    with l.item():
                        st_write(bs.body, (bs.keyword, "Key"), " — point")
                    with l.item():
                        st_write(bs.body, "Second point")
                    with l.item():
                        st_write(bs.body, "Third point")

        st_space(size=2)

        # === L3 ===
        st_write(bs.question, "What does this mean?", tag=t.div)
```

---

## 12. Project Style Template (custom/styles.py)

```python
from streamtex.styles import Style as ns
from streamtex import StxStyles as s_base


class Styles:
    """Project-wide styles — single source of truth."""

    class project:
        class colors:
            primary = ns("color: #00d4ff;", "primary")
            accent = ns("color: #e94560;", "accent")
            muted = ns("color: #8892b0;", "muted")
            highlight = ns("color: #f0db4f;", "highlight")

        class slide:
            headline = s_base.huge + s_base.bold + s_base.center_txt
            body = s_base.large
            keyword = s_base.bold + ns("color: #00d4ff;", "kw_color")
            question = s_base.big + s_base.italic + s_base.center_txt
            placeholder = ns(
                "color: #8892b0; font-style: italic; "
                "border: 2px dashed #8892b0; padding: 40px; "
                "text-align: center;", "placeholder",
            )

        class containers:
            responsive_2col = ns(
                "grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));",
                "resp_2col",
            )
```

---

## 13. Audit Checklist (Self-Check)

Before submitting any slide, verify:

- [ ] Fits on 16:9 screen without scrolling
- [ ] Uses L1/L2/L3 grid (or valid subset)
- [ ] Grid is responsive (`repeat(auto-fit, minmax(...))`)
- [ ] All text is telegraphic (3-7 words per bullet)
- [ ] Fonts >= 24pt body, >= 48pt titles
- [ ] Dark theme — no hardcoded light colors
- [ ] Image or placeholder with generation prompt
- [ ] Max 3-5 bullets per list
- [ ] Bold keywords for emphasis (not overused)
- [ ] Styles in `custom/styles.py`, not inline
- [ ] Slide breaks named with descriptive `marker_label`
- [ ] Emojis: 0-1 per slide max

---

## 14. Prompt Writing Tips

### Good prompt structure

```
Short presentation "[Title]" for [audience].
[N] slides, [theme], [visual style].

1) [Slide name] — [key content / message]
2) [Slide name] — [key content / message]
...

Use L1/L2/L3 grid. Generate image prompts.
Style: telegraphic keywords, bold colored accents.
```

### What to include

| Element | Why |
|---|---|
| **Audience** | Drives vocabulary, depth, font size |
| **Slide count** | Sets scope and density |
| **Theme** (dark/light) | Determines palette generation |
| **Per-slide content** | Avoids generic filler |
| **Visual preferences** | Grids, image style, color direction |

### What to avoid

| Bad | Good |
|---|---|
| "Make slides" | "5-slide intro to Docker for beginners, dark theme" |
| "Add content" | "Add comparison grid: VM vs Container, 3 bullets each" |
| "Fix the style" | "Refactor inline CSS in bck_solution to use BlockStyles" |

---

## 15. Agent Reference

| Agent | Profile | Purpose |
|---|---|---|
| **Slide Designer** | project, documentation | Creates blocks with L1/L2/L3 grid, design rules, dark theme |
| **Slide Reviewer** | project, documentation | Validates completed slides (structure, visual, formatting) |
| **Project Architect** | project | Plans full project structure from description |
| **Presentation Designer** | presentation | Stricter rules for live projection (48pt+, keywords only) |

---

## 16. Command Reference

| Command | What it does |
|---|---|
| `/stx-project:project-init` | Generate full project from description |
| `/stx-project:project-customize` | Adjust theme, fonts, colors |
| `/stx-project:project-upgrade` | Upgrade to latest conventions |
| `/stx-designer:slide-new` | Create or regenerate one slide |
| `/stx-designer:slide-audit` | Validate all slides |
| `/stx-designer:slide-fix` | Auto-fix violations |
| `/stx-designer:style-audit` | Check style consistency |
| `/stx-designer:style-refactor` | Extract/optimize styles |
| `/stx-designer:block-new` | Create block from blueprint |
| `/stx-designer:block-preview` | Validate block structure |

---

## 17. File Structure

```
my-presentation/
├── book.py                        # st_book([blocks...], paginate=True)
├── blocks/
│   ├── __init__.py                # ProjectBlockRegistry
│   ├── helpers.py                 # BlockHelperConfig
│   ├── bck_title.py
│   ├── bck_content.py
│   └── bck_conclusion.py
├── custom/
│   ├── __init__.py
│   ├── styles.py                  # All project styles
│   └── themes.py                  # Dark/light overrides
├── static/images/                 # bck_description.png
└── .streamlit/
    └── config.toml
```

Block naming: `bck_{short_description}.py`
Image naming: `bck_{short_description}.png`

> **Naming advice**: Do NOT prefix block files with numbers (`bck_01_`, `bck_02_`, ...).
> Numbered prefixes are not maintainable — inserting a new block between two existing ones
> forces renaming all subsequent files and their image references. Use descriptive names only
> (`bck_title.py`, `bck_architecture.py`). The block ordering is defined in `book.py`.
