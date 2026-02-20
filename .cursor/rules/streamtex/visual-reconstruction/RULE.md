---
alwaysApply: false
---

# StreamTeX Visual Reconstruction Workflow

## 0. Strict Compliance (Read First)
**CRITICAL:** You are reconstructing a visual design using **StreamTeX Primitives**, NOT raw HTML/CSS.
- Adhere to `.cursor/rules/streamtex/development/RULE.md`.
- **Do not** write `st.markdown("<div style...>")` to replicate the look. You must find the correct `sx` function and `Style` combination.

## 1. Context
This workflow applies when the user provides one or more screenshots/images to recreate as a StreamTeX block.

## 2. Visual Audit Strategy
Before coding, analyze the images to distinguish between structure, layout, colors, text, UI components and assets:

### A. Layout & Grid Detection
- **Horizontal Split:** If elements are side-by-side, use `stx.st_grid()`.
    - *Estimate Ratios:* 1/3 Image + 2/3 Text = `stx.st_grid(cols="1fr 2fr", …)`.
- **Inline Elements:** If blocks sit side-by-side in a single line, use `stx.st_span(...)`.
- **Stacked Elements:** Default behavior `st_block()`.
- **Vertical Rhythm:** Identify the main sections (Hero, Content, Footer).

### B. Typography & Hierarchy
- Map visual sizes to styles (e.g., `s.huge` (80pt), `s.Large` (48pt), `s.medium` (16pt), `s.small` (8pt), etc.)
- **Color Extraction:** Match colors to `s.project.colors.*` or define new generic colors.
  - *Constraint:* Ensure colors are dark-mode friendly (check contrast).
  - *Consistency:* For default vs. intentional color logic, near-black/near-white, and link styling, align with `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`.
- **Bold & Italic:** Scrutinize the image for weight (Bold) and slant (Italic). Apply `s.bold` / `s.italic` accordingly.

### C. Spacing & Alignment
- **Vertical Spacing:** Use `stx.st_space("v", size=...)` to match the exact vertical gaps seen in the screenshot.
- **Padding:** If text isn't touching the container edge, add `s.container.paddings.*`.
- **Centering:** If text is centered, use `s.center_txt`.

### D. Color & Theme Logic
- **Explicit vs. Implicit:**
    - If the background is White/Black and text is Black/White, assume this is **Theme Dependent**. Do NOT hardcode colors.
    - If the background is a specific color (e.g., "Card Beige"), then explicitly style it.
- **Contrast:** Ensure any hardcoded colors remain visible in both Light and Dark modes.

### E. Content Classification (Text vs. Image)
**Take extra caution to distinguish between styled text and embedded images (logos/graphics).**
- **Analysis:** Compare the element's style to the rest of the page. If an element differs significantly in font face, framing, background, or complexity from the standard body/header text, it is likely an **Image/Logo**.
- **Consistency Check:** If you have multiple screenshots, check if the element remains identical while other text changes. This often confirms it is an image asset.
- **Decision:**
    - If **Image/Logo**: Treat it as an asset (see Section 3.A).
    - If **Text**: You MUST implement it using `stx.st_write`.

## 3. Implementation Rules

### A. Asset Handling & Naming
If the screenshot contains images, illustrations, or icons and logos (identified in 2.E), you MUST use `stx.st_image` with the following URI naming convention:
- **Format:** `[current_block_filename_no_ext]_image_[00index].png`
- **Example:** If creating `bck_agent_building_workflow_summary_002.py`, the first image is:
  `uri="bck_agent_building_workflow_summary_002_image_001.png"`
- **Note:** Do not use placeholder names like "placeholder.png" or "image1.jpg". Use the strict schema derived from the block's filename.
- **Description:** Add a comment describing the required asset.

### B. Multiple Image Inputs
- If provided with multiple screenshots (e.g., a scrolling capture split into parts), you must create a **single block** that includes ALL elements from ALL images in their correct sequence.
- Do not create separate blocks unless explicitly asked. Merge the visual flow into one continuous `build()` function.

### C. Text Layout & Coloring
- **Line Breaks:** Use `stx.st_br()` to force line breaks exactly where they appear in the image to preserve the visual shape of the text.
- **Multi-Colored Text:** You must replicate text coloring with high precision.
    - *Example:* If "Artificial Intelligence" is Blue but "A" and "I" are Red.
    - **Implementation:** Do NOT simplify this to a single color. Use a `stx.st_write` call with multiple `(style, txt)` tuples as its parameters (one for "A", one for "rtificial", etc.) or appropriate StreamTeX composition tools to achieve the exact visual result.

### D. Iterative Styling
- Define `BlockStyles` first.
- Reuse generic styles (e.g., `card_container`) for repeating elements.

## 4. Reconstruction Checklist
- [ ] Did I correctly identify Logos vs. Text (Section 2.E)?
- [ ] Are multi-colored text elements replicated faithfully (Section 3.C)?
- [ ] Did I map all intentional colors (text, background, border) and document any dropped colors?
- [ ] Is the layout built with `st_grid`/`st_block` (not raw HTML)?
- [ ] Are image URIs named correctly (e.g., `..._image_001.png`)?
- [ ] Does the block contain the full sequence from all provided screenshots?
- [ ] Is vertical spacing respected using `st_space`?
- [ ] Are line breaks (`st_br`) used to match the text flow?
- [ ] Are generic styles defined in `BlockStyles`?
- [ ] Is the code free of inline CSS strings?