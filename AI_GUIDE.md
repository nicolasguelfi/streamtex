# StreamTeX AI Guide

Use StreamTeX with **Claude Code** or **Cursor** to create presentations, courses,
and web-books — without writing Python code.

---

## Prerequisites

| Tool | Required | Install |
|------|:--------:|---------|
| Python >= 3.11 | Yes | [python.org](https://www.python.org/downloads/) |
| uv | Yes | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| StreamTeX CLI | Yes | `uv tool install "streamtex[cli]" -U` |
| Claude Code | Recommended | [claude.ai/claude-code](https://claude.ai/claude-code) |
| Cursor | Alternative | [cursor.com](https://cursor.com) |

---

## Setup (5 minutes)

### Step 1 — Create a workspace and clone repos

```bash
mkdir my-workspace && cd my-workspace
stx workspace init .        # default: standard preset (docs + claude)
stx workspace update         # clones repos, syncs deps, installs commands globally
```

> After cloning, shared commands (like `/stx-guide`) are copied to `~/.claude/commands/`
> and available globally — even outside any project.

### Step 2 — Create a project and install a Claude profile

```bash
stx project new my-project
cd projects/my-project
stx claude install project .
```

This creates a `.claude/` directory with commands, skills, agents,
and references tailored to your workflow.

### Step 3 — Open in Claude Code or Cursor

```bash
claude          # Open Claude Code in this directory
# or
cursor .        # Open Cursor in this directory
```

You now have access to all slash commands and agents.

---

## Your First Project (Zero Code)

### 1. Describe your project

In Claude Code or Cursor, type:

```
/project:project-init
```

Then describe what you want in natural language:

> "Create a Docker introduction course with 10 slides, dark theme,
> table of contents, page navigation, and a banner with the course title"

### 2. Review the proposed structure

The **Project Architect** agent analyzes your description and proposes:

- List of blocks (slides) with names and content descriptions
- `book.py` structure (pagination, TOC, banner configuration)
- Color palette and style system
- Enabled features

**Nothing is generated until you approve.**

### 3. Generated files

After confirmation, the agent creates:

```
my-project/
├── .streamlit/config.toml       # Theme configuration
├── blocks/
│   ├── __init__.py              # Block registry
│   ├── bck_01_title.py          # Title slide
│   ├── bck_02_overview.py       # Course overview
│   ├── ...                      # Content slides
│   └── bck_10_conclusion.py     # Conclusion
├── custom/
│   └── styles.py                # Project styles and colors
└── book.py                      # Entry point with st_book()
```

### 4. Run and preview

```bash
uv sync
uv run streamlit run book.py
```

Your project opens in the browser, ready to use.

---

## Workflow Reference

### Pathway 1 — Create a presentation from scratch

```
/project:project-init          → Describe your project
/designer:slide-new            → Add or refine individual slides
/designer:slide-audit          → Check design rule compliance
/designer:slide-fix            → Auto-fix violations
```

### Pathway 2 — Convert Google Docs to StreamTeX

```
/migration:html-migrate        → Convert one HTML file
/migration:html-convert-batch  → Convert all HTML files in a directory
/migration:conversion-audit    → Verify conversion quality
```

### Pathway 3 — Customize an existing project

```
/project:project-customize     → Describe changes in natural language
```

Example: *"Switch to light theme, add green accent color, enable TOC sidebar"*

The agent proposes a diff preview, then applies changes safely.

### Pathway 4 — Generate a course from a CSV plan

```
/project:course-generate       → Generate book.py from blocks.csv
```

Prepare a `blocks.csv` file listing block names and order,
then let the agent generate the full `book.py` configuration.

---

## Command Reference

### Project Commands (5)

| Command | What it does |
|---------|-------------|
| `/project:project-init` | Create a complete project from a natural-language description. The Project Architect agent proposes structure, blocks, colors, and features — generates all files after your approval. |
| `/project:project-customize` | Modify theme, colors, typography, navigation, or features of an existing project. Reads current configuration, proposes a diff preview, applies changes safely without deleting content. |
| `/project:course-generate` | Generate `book.py` from a `blocks.csv` file listing block names and order. |
| `/project:collection-new` | Create a multi-project collection hub with TOML configuration. |
| `/project:project-upgrade` | Upgrade project boilerplate files to the latest template structure. |

### Designer Commands (7)

| Command | What it does |
|---------|-------------|
| `/designer:slide-new` | Create a new slide following visual design rules. Enforces ~45-char lines, 32pt body text, proper structure (explanation, code, demo, details). |
| `/designer:block-new` | Create a content block with automatic blueprint matching. Matches your description against 10 block templates and generates appropriate structure. |
| `/designer:slide-audit` | Validate a slide against design rules. Checks line lengths, font sizes, imports, structure, TOC entries. Reports errors and warnings with line numbers. |
| `/designer:slide-fix` | Auto-fix all design violations found by audit. Breaks long lines, adds `show_code()`, corrects font sizes, fixes spacing. |
| `/designer:style-audit` | Check styles for consistency. Detects raw HTML/CSS, hardcoded colors, duplicate styles, non-English names, dark mode issues. |
| `/designer:style-refactor` | Extract repeated style patterns into `BlockStyles` or `custom/styles.py`. Optimizes naming and composition. |
| `/designer:block-preview` | Validate block structure, image assets, style references, and TOC entries without running the app. |

### Migration Commands (5)

| Command | What it does |
|---------|-------------|
| `/migration:html-migrate` | Convert HTML content (e.g., Google Docs export) to a StreamTeX block. Analyzes colors, layout, and formatting — generates clean block with styles. |
| `/migration:html-convert-batch` | Batch convert all HTML files in a directory. Supports `--all`, `--filter`, `--dry-run`, `--force`, `--limit`. |
| `/migration:html-convert-block` | Convert a single saved HTML block with detailed color mapping and style consolidation. |
| `/migration:html-export` | Configure HTML export in `book.py` and audit widgets for export compatibility. |
| `/migration:conversion-audit` | Verify a converted block for color fidelity, proper components, and no residual raw HTML/CSS. |

### Developer Commands (3)

| Command | What it does |
|---------|-------------|
| `/developer:test-run` | Run the test suite with `pytest`. Analyzes failures and reports pass/fail counts. |
| `/developer:lint` | Run `ruff` linter. Auto-fixes where possible, reports remaining manual issues. |
| `/developer:deploy` | Deploy to Docker, Hugging Face Spaces, or GCP. Runs pre-deployment checks (tests, lint, requirements, git status). |

### Presentation-Only Commands (3)

*Available with the `presentation` profile only.*

| Command | What it does |
|---------|-------------|
| `/designer:presentation-audit` | Check slide for live projection compliance: font sizes (48pt+ body), keyword length (5-7 words), contrast, spacing. |
| `/designer:presentation-fix` | Auto-fix font sizes, text length, contrast, and visual anchor issues for live projection. |
| `/designer:survey-convert` | Convert survey screenshots (e.g., Stack Overflow Developer Survey) into code-generated presentation blocks. |

---

## Agent Reference

StreamTeX includes 4 specialized AI agents that work autonomously within their domain:

### Project Architect

- **Role**: Design project structure from natural language descriptions
- **Principles**: One block = one idea, max 15 blocks, logical ordering (intro, concepts, demos, synthesis, conclusion)
- **Output**: Proposed plan with block list, features, color palette — requires your confirmation
- **Trigger**: Activated automatically by `/project:project-init`

### Slide Designer

- **Role**: Create visually polished, pedagogically structured slides
- **Principles**: ~45-char lines, 32pt body text, canonical structure (explanation, code, demo, details)
- **Anti-patterns detected**: String concatenation, missing `show_code()`, code without demo, unclear error boxes
- **Trigger**: Activated by `/designer:slide-new`

### Slide Reviewer

- **Role**: Review and validate completed slides
- **Checks**: Structure compliance, visual quality, pedagogical flow, text formatting
- **Output**: Checklist with pass/fail for each criterion
- **Trigger**: Available as a follow-up after slide creation

### Presentation Designer

- **Role**: Specialist for live projection at 10-20m distance
- **Principles**: Keywords only (5-7 words per bullet, 3 bullets max), 48pt+ body, 96pt+ titles, high contrast, visual-first
- **Overrides**: Base design rules with larger fonts and stricter text limits
- **Trigger**: Activated by presentation profile commands
- **Profile**: Requires `presentation` profile

---

## Profile Reference

StreamTeX provides 4 installable AI profiles via
[streamtex-claude](https://github.com/nicolasguelfi/streamtex-claude).

### `project` (recommended for most users)

- **Audience**: Content creators, teachers, presenters
- **Commands**: 19 (designer + migration + project + developer)
- **Agents**: Project Architect, Slide Designer, Slide Reviewer
- **Skills**: Block blueprints, visual design rules, style conventions, quick reference
- **Install**: `stx claude install project ./my-project`

### `presentation` (extends project)

- **Audience**: Live presenters (amphitheater, conference)
- **Adds**: 3 commands + 1 agent + 2 skills on top of `project`
- **Key difference**: Enforces large fonts (48pt+), keyword-only bullets, high contrast for 10-20m distance
- **Install**: `stx claude install presentation ./my-project`

### `documentation` (manual authoring)

- **Audience**: Technical writers, manual authors
- **Commands**: 10 (designer + project + developer)
- **Agents**: Slide Designer, Slide Reviewer
- **Focus**: Multi-manual coordination, course generation
- **Install**: `stx claude install documentation ./my-project`

### `library` (core development)

- **Audience**: StreamTeX library contributors
- **Commands**: 3 (test, lint, deploy)
- **Skills**: Architecture reference, testing patterns
- **Install**: `stx claude install library ./streamtex`

---

## Block Blueprint Catalog

When you create blocks with `/designer:block-new` or `/project:project-init`,
the agent matches your description against these 12 templates:

| # | Blueprint | Use case |
|:-:|-----------|----------|
| 1 | **Title** (`bck_title`) | Course or project title with author and subtitle |
| 2 | **Section Header** (`bck_section`) | Section divider with number and description |
| 3 | **Content** (`bck_content`) | Title + bullet points — the most common pattern |
| 4 | **Comparison** (`bck_comparison`) | Two-column layout for X vs Y comparisons |
| 5 | **Image + Text** (`bck_image_text`) | Image alongside explanatory text |
| 6 | **Code Demo** (`bck_code_demo`) | Code snippet with output or live result |
| 7 | **Timeline** (`bck_timeline`) | Numbered steps or workflow progression |
| 8 | **Quote** (`bck_quote`) | Highlighted citation or key message |
| 9 | **Gallery** (`bck_gallery`) | Grid of images or visual elements |
| 10 | **Conclusion** (`bck_conclusion`) | Synthesis of key takeaways |
| 11 | **AI Image + Text** (`bck_ai_image`) | AI-generated image alongside text (requires `streamtex[ai]`) |
| 12 | **Interactive Image Lab** (`bck_ai_lab`) | Widget for live AI image generation in the browser |

You don't need to know these names — just describe what you want, and the
agent selects the best template automatically.

---

## AI Image Generation

StreamTeX can generate images from text prompts using external AI providers.
Images are cached on disk — same parameters produce the same file, no API cost
on Streamlit reruns.

### Installation

```bash
uv add "streamtex[ai]"           # All 3 providers
uv add "streamtex[ai-openai]"    # OpenAI GPT-Image only
uv add "streamtex[ai-google]"    # Google Imagen 4 only
uv add "streamtex[ai-fal]"       # fal.ai Stable Diffusion only
```

### Configuration

Add to your `book.py`:

```python
from streamtex import set_ai_image_config, AIImageConfig

set_ai_image_config(AIImageConfig(
    provider="openai",           # "openai" | "google" | "fal"
    default_size="1024x1024",
    output_dir="static/images/ai",
    auto_generate=False,         # True = generate immediately if not cached
))
```

### API Keys

Set in your `.env` file (or as Render env vars for deployment):

```bash
STX_OPENAI_API_KEY=sk-...
STX_GOOGLE_AI_KEY=AIza...
STX_FAL_KEY=fal-...
```

### Usage in Blocks

```python
# Declarative — generate and display
st_ai_image("A minimalist illustration of cloud architecture")

# With provider/size override
st_ai_image("A futuristic dashboard", provider="google", size="1024x1024")

# Interactive widget — user types prompt in the browser
st_ai_image_widget(default_prompt="A modern diagram")

# Programmatic — save to file, then display
from streamtex import generate_image
path = generate_image("Illustration of AI concepts", provider="openai")
st_image(uri=path, width="100%")
```

### Supported Providers

| Provider | Model | Strengths |
|----------|-------|-----------|
| **OpenAI** | GPT-Image (gpt-image-1) | High quality, prompt interpretation with `revised_prompt` feedback |
| **Google** | Imagen 4 (imagen-4.0-generate-001) | Photorealistic output, strong text-in-image rendering |
| **fal.ai** | Stable Diffusion v3.5 Large | Open-source, fast generation, customizable parameters |

### Manual vs Auto Mode

- **Manual** (`auto_generate=False`, default): Shows a placeholder with a **Generate** button. No API call until you click.
- **Auto** (`auto_generate=True`): Generates immediately if not cached. Use for batch generation or scripted workflows.

---

## Tips and Best Practices

### Iterating with AI

- Start with `/project:project-init` for the overall structure
- Use `/designer:slide-new` to refine individual slides
- Run `/designer:slide-audit` periodically to catch design issues
- Use `/project:project-customize` to adjust theme and navigation at any time

### Combining commands

Commands can be chained in a natural conversation:

> "Create a new slide about Docker volumes with a code example"
> → agent uses `/designer:slide-new` + blueprint #6 (code demo)

> "Audit all my slides for design compliance"
> → agent runs `/designer:slide-audit` on each block file

### When to switch to code

AI commands handle most content creation. Switch to Python when you need:

- Custom interactive widgets (forms, state management)
- Complex data visualizations with live data sources
- Integration with external APIs (Google Sheets, databases)
- Custom rendering logic not covered by standard blocks

---

## FAQ

### Do I need to know Python?

**No.** The AI profiles provide commands and agents that generate all Python code
for you. You describe what you want in natural language, review the proposals,
and the AI builds it.

### Which AI assistant should I use?

**Claude Code** is recommended — it has native support for slash commands and
the agent system. **Cursor** also works well with the same `.claude/` configuration.

### Can I mix AI-generated and hand-written blocks?

**Yes.** AI-generated blocks are standard Python files. You can edit them manually,
add custom logic, or create new blocks by hand alongside AI-generated ones.

### How do I update my AI profile?

Update everything at once from the workspace root:

```bash
cd streamtex-dev/
stx workspace update         # pulls repos, syncs deps, updates all profiles
```

For a single project:
```bash
stx claude diff .           # See what changed
stx claude update .         # Update profile from source
stx claude update . --force # Override local CLAUDE.md changes
```

### Can I create my own commands?

**Yes.** Add markdown files to `.claude/commands/` following the existing format.
Commands are simple markdown files with instructions for the AI assistant.

### How do I deploy my project?

```bash
/developer:deploy
```

The deploy command supports Docker, Hugging Face Spaces, and GCP targets.
It runs pre-flight checks (tests, linting, requirements) before deploying.

### How does Render auto-deploy work?

Render services are automatically redeployed on push to `main` via a GitHub Actions
workflow (`.github/workflows/render-deploy.yml`). The workflow uses **smart path-based
filtering** — only services whose files actually changed are redeployed:

- Changes in `manuals/stx_manual_intro/**` → deploy `streamtex-intro` only
- Changes in shared files (`Dockerfile`, `pyproject.toml`, `shared-blocks/`, `.github/`, `scripts/`) → deploy **ALL** services
- Manual trigger (`workflow_dispatch`) → deploy **ALL** services

The mapping between services and folders is extracted automatically from the `FOLDER`
env var in `render.yaml`.

**Setup (one-time per repo):**
```bash
gh secret set RENDER_API_KEY -R nicolasguelfi/<repo> --body "<your-render-api-key>"
```

**Manual trigger (deploys all services):**
```bash
gh workflow run render-deploy.yml -R nicolasguelfi/<repo>
```

> **Note:** Render's built-in GitHub App auto-deploy can silently stop after consecutive
> build failures. The GitHub Actions workflow bypasses this limitation entirely.

### How do I sync env vars to Render after changing render.yaml?

```bash
stx deploy env-sync              # Sync all services
stx deploy env-sync --dry-run    # Preview changes without applying
stx deploy env-sync --service streamtex-intro  # Sync one service
```

This reads your `render.yaml` env vars and pushes them to live Render services via the API. Requires `render login` (stores API key in `~/.render/cli.yaml`).
