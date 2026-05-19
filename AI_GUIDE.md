# StreamTeX AI Guide

[![Best on Chrome](https://img.shields.io/badge/Best%20on-Chrome-4285F4?logo=googlechrome&logoColor=white)](https://www.google.com/chrome/)

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
stx install                  # default: standard preset (docs + claude)
stx update                   # clones repos, syncs deps, installs commands globally
```

> **Developer shortcut:** if you've registered a local source with
> `stx dev register streamtex /path/...`, add `--dev` to any
> `stx install --project NAME` to auto-link the dev source into the
> new project's venv (skips the manual `stx dev link streamtex` step).

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
/stx-block:init
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
stx run
```

Your project opens in the browser, ready to use.

---

## Workflow Reference

### Pathway 1 — Create a presentation from scratch

```
/stx-block:init                    → Describe your project
/stx-block:slide-new               → Add or refine individual slides
/stx-block:audit --target <name>   → Check design rule compliance
/stx-block:fix --target <name>     → Auto-fix violations
```

### Pathway 2 — Convert Google Docs to StreamTeX

```
/stx-import:html                   → Convert one HTML file
/stx-import:html-batch             → Convert all HTML files in a directory
/stx-import:html-audit             → Verify conversion quality
```

### Pathway 3 — Customize an existing project

```
/stx-block:customize               → Describe changes in natural language
/stx-block:update                  → Incremental adjustments (theme, nav, content)
```

Example: *"Switch to light theme, add green accent color, enable TOC sidebar"*

The agent proposes a diff preview, then applies changes safely.

### Pathway 4 — Generate a course from a CSV plan

```
/stx-block:course-generate         → Generate book.py from blocks.csv
```

Prepare a `blocks.csv` file listing block names and order,
then let the agent generate the full `book.py` configuration.

### Pathway 5 — Compound document engineering (CE cycle)

```
/stx-ce:collect <sources/>         → Inventory and classify source material
/stx-ce:assess                     → Auto-detect import / improve / create pathway
/stx-ce:plan                       → Plan production (or --interactive)
/stx-ce:produce                    → Execute plan (orchestrates stx-block + stx-import)
/stx-ce:review                     → Multi-perspective review (audience, pedagogy, etc.)
/stx-ce:fix                        → Auto-fix review findings
/stx-ce:compound                   → Capitalize learnings as solutions
/stx-ce:integrate                  → Route solutions to lib issues / skill updates
```

Or run the full cycle autonomously with `/stx-ce:go "<description>"`.

---

## Command Reference

### Project Lifecycle — `stx-block` (15 commands)

The `stx-block` namespace covers the entire project lifecycle, from creation to
audit/fix loops. Most users only need `init`, `update`, `audit`, and `fix` —
the rest are specialized variations.

| Command | What it does |
|---------|-------------|
| `/stx-block:init` | Create a complete project from a natural-language description. The Project Architect agent proposes structure, blocks, colors, and features — generates all files after your approval. Templates: `project` (default), `presentation`, `collection`, `course`. |
| `/stx-block:update` | Add content, customize theme, migrate HTML, export — covers all post-creation modifications. Sub-flags: `--upgrade`, `--migrate`, `--export`. |
| `/stx-block:audit` | Validate quality (structure, styles, design rules, presentation compliance). Use `--all` or `--target <name>`. Replaces the legacy `slide-audit`/`style-audit`. |
| `/stx-block:fix` | Auto-fix violations found by audit. Use `--all` or `--target <name>`. Replaces the legacy `slide-fix`. |
| `/stx-block:tool <name>` | Run specialized tools (e.g. `survey-convert`). |
| `/stx-block:slide-new` | Create a new slide following visual design rules. Enforces ~45-char lines, 32pt body text, canonical structure. |
| `/stx-block:new` | Create a new content block with automatic blueprint matching against 10 block templates. |
| `/stx-block:preview` | Validate block structure, image assets, style references, and TOC entries without running the app. |
| `/stx-block:style-refactor` | Extract repeated style patterns into `BlockStyles` or `custom/styles.py`. Optimizes naming and composition. |
| `/stx-block:customize` | Modify theme, colors, typography, navigation, or features of an existing project. Reads current configuration, proposes a diff preview. |
| `/stx-block:upgrade` | Upgrade project boilerplate files to the latest template structure. |
| `/stx-block:collection-new` | Create a multi-project collection hub with TOML configuration. |
| `/stx-block:course-generate` | Generate `book.py` from a `blocks.csv` file listing block names and order. |
| `/stx-block:test` | Run the test suite with `pytest` (via `uv run`). Analyzes failures and reports pass/fail counts. |
| `/stx-block:lint` | Run `ruff` linter. Auto-fixes where possible, reports remaining manual issues. |

### Compound Document Engineering — `stx-ce` (13 commands)

A structured methodology for document production. Phases: `COLLECT → ASSESS →
PLAN → PRODUCE → REVIEW → FIX → COMPOUND → INTEGRATE`. CE artifacts live in
`docs/`. See `.claude/references/ce_cheatsheet_en.md` for the full reference.

| Command | Phase |
|---------|-------|
| `/stx-ce:collect <sources/>` | Inventory + classify source material |
| `/stx-ce:assess` | Auto-detect pathway (import / improve / create) |
| `/stx-ce:plan` | Plan production (auto or `--interactive`) |
| `/stx-ce:produce` | Execute plan (orchestrates stx-block + stx-import) |
| `/stx-ce:review` | Multi-perspective review (5 axes) |
| `/stx-ce:fix` | Correct review findings + verify |
| `/stx-ce:compound` | Capitalize learnings as solutions |
| `/stx-ce:integrate` | Route solutions to lib issues / skill updates / custom rules |
| `/stx-ce:go "<description>"` | Full autonomous cycle with 4 validation gates |
| `/stx-ce:status` | Show CE cycle status |
| `/stx-ce:task` | Ad-hoc task with lifecycle reconciliation |
| `/stx-ce:continue` | Resume work with context briefing |
| `/stx-ce:pause` | Save session checkpoint before pausing |

### Import — `stx-import` (6 commands, shared)

| Command | What it does |
|---------|-------------|
| `/stx-import:html` | Convert HTML content (Google Docs export) to a StreamTeX block. |
| `/stx-import:html-batch` | Batch convert all HTML files in a directory. Supports `--all`, `--filter`, `--dry-run`, `--force`, `--limit`. |
| `/stx-import:html-block` | Convert a single saved HTML block with detailed color mapping. |
| `/stx-import:html-audit` | Audit conversion quality (color fidelity, components, no raw HTML). |
| `/stx-import:marp` | Import a Marp project into StreamTeX. |
| `/stx-import:marp-analyze` | Analyze a Marp project before import. |
| `/stx-import:latex` | Import LaTeX documents into StreamTeX. |

### Presentation overlay — `stx-presentation` (3 commands)

*Available with the `presentation` profile only — extends `project`.*

| Command | What it does |
|---------|-------------|
| `/stx-presentation:presentation-audit` | Check slide for live projection compliance: font sizes (48pt+ body), keyword length (5-7 words), contrast, spacing. |
| `/stx-presentation:presentation-fix` | Auto-fix font sizes, text length, contrast, and visual anchor issues for live projection. |
| `/stx-presentation:survey-convert` | Convert survey screenshots (e.g., Stack Overflow Developer Survey) into code-generated presentation blocks. |

### Deploy — `stx-deploy` (shared)

`/stx-deploy:preflight`, `/stx-deploy:provision`, `/stx-deploy:setup`,
`/stx-deploy:secure`, `/stx-deploy:install-coolify`, `/stx-deploy:configure-domain`,
`/stx-deploy:deploy`, `/stx-deploy:deploy-batch`, `/stx-deploy:update`,
`/stx-deploy:scale`, `/stx-deploy:setup-loadbalancer`, `/stx-deploy:status`,
`/stx-deploy:go` — full Hetzner/Coolify deployment pipeline.

### Issues — `stx-issue` (6 commands, shared)

`/stx-issue:bug`, `/stx-issue:feature`, `/stx-issue:question`, `/stx-issue:docs`,
`/stx-issue:comment`, `/stx-issue:list` — create and manage GitHub issues with
auto-collected environment metadata.

### Patterns — `stx-pattern` (5 commands, shared)

`/stx-pattern:list`, `/stx-pattern:show`, `/stx-pattern:new`,
`/stx-pattern:reindex`, `/stx-pattern:validate` — manage the reusable design
patterns catalog (see Section 4i in stx-guide).

---

## Agent Reference

StreamTeX includes 4 specialized AI agents that work autonomously within their domain:

### Project Architect

- **Role**: Design project structure from natural language descriptions
- **Principles**: One block = one idea, max 15 blocks, logical ordering (intro, concepts, demos, synthesis, conclusion)
- **Output**: Proposed plan with block list, features, color palette — requires your confirmation
- **Trigger**: Activated automatically by `/stx-block:init`

### Slide Designer

- **Role**: Create visually polished, pedagogically structured slides
- **Principles**: ~45-char lines, 32pt body text, canonical structure (explanation, code, demo, details)
- **Anti-patterns detected**: String concatenation, missing `show_code()`, code without demo, unclear error boxes
- **Trigger**: Activated by `/stx-block:slide-new`

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
- **Commands**: 28 (15 stx-block + 13 stx-ce) plus shared groups (stx-issue, stx-import, stx-export, stx-deploy, stx-pattern)
- **Agents**: 21 (3 designer + 18 ce specialists)
- **Skills**: 21 (8 designer + 13 ce)
- **Install**: `stx claude install project ./my-project`

### `presentation` (extends project)

- **Audience**: Live presenters (amphitheater, conference)
- **Adds**: 3 stx-presentation commands + 1 agent + 3 skills on top of `project`
- **Key difference**: Enforces large fonts (48pt+), keyword-only bullets, high contrast for 10-20m distance
- **Install**: `stx claude install presentation ./my-project`

### `documentation` (manual authoring)

- **Audience**: Technical writers, manual authors
- **Inherits** `project`. Adds shared `stx-coherence` and `stx-pattern` command groups for cross-manual coherence audits and pattern management.
- **Focus**: Multi-manual coordination, course generation, ecosystem-wide audits
- **Install**: `stx claude install documentation ./my-project`

### `library` (core development)

- **Audience**: StreamTeX library contributors
- **Inherits** `project`. Adds shared `stx-coherence` for ecosystem-wide audits.
- **Skills**: Architecture reference, testing patterns
- **Install**: `stx claude install library ./streamtex`

---

## Block Blueprint Catalog

When you create blocks with `/stx-block:new` or `/stx-block:init`,
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

Set in your `.env` file (or as Coolify env vars for deployment):

```bash
STX_OPENAI_API_KEY=sk-...
STX_GOOGLE_AI_KEY=AIza...
STX_FAL_KEY=fal-...
```

### Usage in Blocks

Since streamtex 0.7.x, AI image rendering goes through `st_image()`
with `prompt=` + `editable=True` (one unified API for local / URL /
AI-generated images).

```python
# Declarative AI image — generate and display
st_image(prompt="A minimalist illustration of cloud architecture",
         editable=True, name="cloud_arch")

# With provider / size override
st_image(prompt="A futuristic dashboard", editable=True, name="dashboard",
         provider="google", ai_size="1024x1024")

# Interactive editing — same call; clicking the image opens the editor
# panel (Prompt / AI / Edit / History tabs, with save action).
st_image(prompt="A modern diagram", editable=True, name="diagram")

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

- Start with `/stx-block:init` for the overall structure
- Use `/stx-block:slide-new` to refine individual slides
- Run `/stx-block:audit --all` periodically to catch design issues
- Use `/stx-block:customize` (or `/stx-block:update`) to adjust theme and navigation at any time

### Combining commands

Commands can be chained in a natural conversation:

> "Create a new slide about Docker volumes with a code example"
> → agent uses `/stx-block:slide-new` + blueprint #6 (code demo)

> "Audit all my slides for design compliance"
> → agent runs `/stx-block:audit --all`

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
stx update                   # pulls repos, syncs deps, updates all profiles
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
/stx-deploy:preflight
/stx-deploy:deploy
```

The `stx-deploy` command group drives the full Hetzner/Coolify deployment pipeline (preflight, provision, secure, install-coolify, configure-domain, deploy, scale, status). For local Docker testing, use `stx deploy docker .` from the CLI directly.

### How does Hetzner/Coolify auto-deploy work?

Coolify applications are automatically redeployed on push to `main`
via a GitHub Actions workflow
(`.github/workflows/hetzner-deploy.yml`). The workflow uses
**smart path-based filtering** — only services whose files actually
changed are redeployed:

- Changes in `manuals/stx_manual_intro/**` → deploy `docs-intro` only
- Changes in shared files (`Dockerfile`, `pyproject.toml`, `shared-blocks/`, `.github/`, `scripts/`) → deploy **ALL** services (batched ≤ 4 to avoid server hang)
- Manual trigger (`workflow_dispatch`) → deploy **ALL** services

The mapping between services and folders lives in
`.stx-deploy.json` at the workspace root.

**Setup (one-time per repo):**
```bash
gh secret set COOLIFY_API_TOKEN -R nicolasguelfi/<repo> --body "<your-coolify-token>"
```

**Manual trigger (deploys all services):**
```bash
gh workflow run hetzner-deploy.yml -R nicolasguelfi/<repo>
```

### How do I manage env vars on Coolify?

Env vars are managed per application in the Coolify dashboard
(https://coolify.streamtex.org). There is **no committed file** that
mirrors them — by design, to avoid leaking secrets through git.

For the runtime selector (which manual to serve), set `FOLDER` per
application in the Coolify env-vars panel.
