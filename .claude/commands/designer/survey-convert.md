Convert a Stack Overflow Developer Survey screenshot into a code-generated StreamTeX presentation block.

The screenshot is the **source reference only** — the output is pure Python code that reproduces the chart. Zero static image dependency.

## Before Converting

Read these files (mandatory):
1. `.claude/designer/ros_designer_default/skills/survey-chart-conversion.md` — conversion schema and template
2. `.claude/designer/ros_designer_default/skills/presentation-design-rules.md` — presentation rules
3. Target project's `CLAUDE.md` — **contains project paths** (blocks dir, book.py)
4. Target project's `custom/styles.py` — palette and containers

## Arguments

`$ARGUMENTS` — Syntax: `[OPTIONS] [SOURCE]`

- **`SOURCE`** (optional) — a file or directory path:
  - **A single image path**: Convert that one image
  - **A directory path**: Use that directory as source instead of the default
  - **Omitted**: default to the project's `temp/` directory (from CLAUDE.md "Project Paths")

- **Options**:
  - **`--all`**: Convert ALL images in the source directory (batch mode)
  - **`--list`**: List all images in the source directory (no conversion)

### Examples

```
/designer:survey-convert                                      # interactive — list temp/ images, ask which
/designer:survey-convert --all                                # batch — convert all images in temp/
/designer:survey-convert --list                               # list images in temp/ without converting
/designer:survey-convert projects/AI4SE/temp/Screenshot.png   # convert one specific image
/designer:survey-convert --all /path/to/other/folder          # batch from a custom folder
```

## Path Resolution

1. If a **source directory or file** is given explicitly in `$ARGUMENTS`, use it.
2. Otherwise, read the target project's `CLAUDE.md` → "Project Paths" table → `temp/` row.
3. Output paths (`blocks/`) always come from the project's CLAUDE.md.

## Conversion Workflow (single image)

### Step 1 — Read the image
Read the screenshot file. Zoom in mentally on each element to extract all data.

### Step 2 — Extract chart data
From the **right panel** of the screenshot, read every bar:
- **Label**: exact text to the left of each bar
- **Value**: percentage number to the right of each bar
- Read **top to bottom**, in the exact order shown
- Store as `SURVEY_DATA = [{"label": "...", "value": N.N}, ...]`

### Step 3 — Extract metadata
From the **left panel**, extract:
- **Title**: The bold heading
- **Description**: The paragraph text (will be distilled into keywords)
- **Question**: The text in the gray question box
- **Active tab**: Which tab is highlighted (e.g. "Professional Developers")
- **Response count and percent**: Bottom-right of chart area

### Step 4 — Distill keywords
Convert the description paragraph into 2–3 keyword stats:
- Numbers first: percentages, rankings, trends
- Max 5–7 words per keyword
- Max 3 keywords total

### Step 5 — Choose naming
- Block file: `bck_survey_<topic_slug>.py`
- Verify no naming collision with existing blocks

### Step 6 — Generate block
Use the template from `survey-chart-conversion.md` skill.
Fill in ALL fields:
- `SURVEY_TITLE`, `SURVEY_KEYWORDS`, `SURVEY_SOURCE`, `SURVEY_QUESTION`
- `SURVEY_DATA` — every bar from the chart
- `RESPONSE_COUNT`, `RESPONSE_PERCENT`

The block includes `_render_bars()` which generates the bar chart in code via `st.html()`.

### Step 7 — Register block
Add to the block list in `book.py`.

## Batch Mode (`--all`)

When converting all images:
1. Read all images in the source directory
2. For each image, extract the title and propose a slug
3. Show the full conversion plan as a table:
   ```
   | # | Image file | Title | Proposed slug | Block file |
   ```
4. Ask user to confirm before proceeding
5. Convert all images sequentially
6. Register all blocks in `book.py`
7. Report summary: N blocks created

## Output

After conversion, show:
```
## Converted: <title>

- Block: `blocks/bck_survey_<topic>.py`
- Bars: N data points extracted
- Keywords: <list>
- Source: <source line>
- Registered in: book.py ✓
```
