---
alwaysApply: true
---

# StreamTeX HTML Migration Workflow

## 0. Strict Compliance (Read First)
**CRITICAL:** This workflow guides the *analysis* of HTML inputs. The *code generation* phase MUST strictly follow `.cursor/rules/streamtex/development/RULE.md`.
- **Inherit all rules:** No raw HTML strings, use `sx` functions, strict imports.
- **Inherit Styling:** Use generic style names (English) and dark-mode friendly colors as defined in the Core Guidelines.
- **Color Fidelity:** You MUST also follow `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md` for all color handling.

## 1. Context
This workflow applies when the user provides raw, cluttered HTML (e.g., Google Docs export) to convert into a StreamTeX block.

If the target project has an `input/` folder containing source HTML files, use those as context for the migration. Place source HTML in `<project>/input/` and migrated blocks in `<project>/blocks/`.

Before implementing a new migration, you SHOULD:
- Read the target project's `book.py` to see how blocks are wired.
- Look at existing blocks in the project for style conventions and helper patterns already in use.

## 2. Analysis Phase (Internal Monologue)
1.  **Filter Noise:** Ignore non-descriptive class names (`c1`, `c12`). Look at the *computed* styles (e.g., bold, centered, blue) of those classes.
2.  **Identify Defaults:**
    - Is the text or grid backgrounds just black/white? **Do not** apply a color style (allow Light/Dark mode).
    - Is the link underlined? That is default behavior; do not add extra decoration styles or set `no_link_decor=True` (keep it as the default `False`).
3.  **Detect Formatting:**
    - Identify **Bold** (`font-weight: 700`) and *Italic* (`font-style: italic`) usage. Map these to `s.bold` and `s.italic`.
4.  **Identify Containers:**
    - Tables used for alignment or data (e.g. `<table>`) -> Map to `sx.st_grid()`.
    - Manual bullet points -> Map to `sx.st_list()`.
5.  **Style Consolidation:**
    - Identify repeating patterns (e.g., "11pt Arial Black").
    - Create **ONE** generic style in `BlockStyles` (e.g., `s.text.header_standard`) instead of copying `c1`, `c2`, `c3`.
    - **Preserve colors:** Before merging classes, ensure no non-default color is dropped. See color-fidelity RULE for the consolidation rule.
6.  **Identify Colors:**
    - Is every color used in the html defined and used in the block?
    - Is every part of the page colored the appropriate way?
    - Double check every div and html class to make sure.
    - Follow the guidelines outlined in `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md` to achieve faithful reconstruction of the color styles.
7.  **Color Sanity Check (before finishing):**
    - Compare key colored elements (titles, links, callouts, highlights) between the original HTML and the migrated block.
    - Confirm their color intent is preserved (same hue family and emphasis).

## 3. Implementation Steps

### A. Asset Handling & Naming (CRITICAL)
If the HTML contains images (`<img>` tags), you MUST rename them using the project standard:
- **Format:** `[current_block_filename_no_ext]_image_[00index].[extension]`
- **Example:** `bck_session_intro_01_image_001.png`
- **Action:** Replace the original `src` (often a Googleusercontent URL) with this local URI in `sx.st_image(uri=...)`.
- **Destination:** If the images are provided (present inside the workspace), copy them into the project's `static/images` folder and rename them.

### B. Structure & Layout
1.  **Setup:** Create file with Mandatory Imports from `.cursor/rules/streamtex/development/RULE.md`.
2.  **Styles:** Define consolidated `BlockStyles` class.
    - *Constraint:* Do not use IDs for style differentiation if definitions are identical.
3.  **Structure:** Write `build()`.
    - Use `sx.st_block()` for stacked blocks.
    - Use `sx.st_write(style, (sub_style, txt), txt, ...)` for inline text of different styles.
    - Use `sx.st_span()` for other inline elements.

### B.1 Inline vs Block Layout (CRITICAL)
**StreamTeX containers stack children vertically by default.** Multiple `st_write()` calls inside a list item or cell will render **on top of each other**, not side by side.

When the HTML has **multiple sibling inline elements** (e.g. `<li><span>Pricing</span><span> ??</span></li>` or `<p><a>link</a> text</a></p>`):

- **WRONG:** Multiple `st_write` calls — they stack vertically:
  ```python
  with lst.item():
      st_write(bs.link_style, "Pricing", link=URL)
      st_write(s.bold, " ??")   # Renders BELOW, not beside
  ```
- **CORRECT:** One `st_write` with tuple arguments — content flows inline:
  ```python
  with lst.item():
      st_write(s.Large, (bs.link_style, "Pricing", URL), (s.bold, " ??"))
  ```

Rule: **One logical line of mixed-style text = one `st_write` call** with `(style, "text")` or `(style, "text", link_url)` tuples for each styled segment.

### B.2 Link and Font Size (CRITICAL)
Links default to 12pt. When the HTML shows links at a larger size (e.g. 42pt, 48pt), **include the font size in the link style** so links visually match surrounding text:

- **WRONG:** `link_style = s.project.colors.denim_blue + s.text.decors.underline_text` — links stay 12pt.
- **CORRECT:** `link_style = s.project.colors.denim_blue + s.text.decors.underline_text + s.Large` — links match 48pt context.

**Key patterns to follow:**
- Raw HTML table layout -> `sx.st_grid` with `cell_styles` (use `s.container.layouts.vertical_center_layout` for vertical centering) and `sx.st_block` for cell content.
- Repeated inline link sequences -> abstract into a small helper function that constructs arguments for a `st_write()` call.
- **Inline mixed-style text** -> one `st_write` with tuples: e.g. `st_write(bs.italic_bold, "(", (bs.link_style, "Link", URL), ") surrounding text...")` — link and surrounding text flow inline.

### C. Content Extraction
1.  **Text:** Extract clean text. Replace `<br>` with `sx.st_br()`.
2.  **Lists:** Convert `<ul>/<ol>` or manual bullets to `sx.st_list()`.

When unsure how to represent a particular HTML construct, look for the closest equivalent in existing blocks within the project or in `documentation/manuals/sx_manual_intro/blocks/`.

## 4. Migration Checklist
- [ ] Did I remove all raw HTML strings?
- [ ] Did I replace "c1/c2" classes with semantic names?
- [ ] Did I rename all image assets to `..._image_001.[ext]`?
- [ ] Did I use `sx.st_list` instead of hardcoded bullets?
- [ ] **Inline content:** For HTML with multiple sibling spans (e.g. `<span>X</span><span>Y</span>`), did I use one `st_write` with tuple args instead of multiple `st_write` calls?
- [ ] **Font size:** Do the styles include the appropriate font size when HTML shows text at non-default (e.g. 42pt) size?
- [ ] Did I use `sx.st_br()` for line breaks to match the layout?
- [ ] Did I use `sx.st_grid()` with `cell_styles` containing `s.container.layouts.vertical_center_layout` to match `<table>` layouts?
- [ ] Did I remove hardcoded black/white colors to support Dark Mode?
- [ ] Did I correctly apply `s.bold` and `s.italic` where needed?
- [ ] Did I map all non-default **text colors** to composed styles?
- [ ] Did I map all non-default **background/border colors** (cards, callouts, highlights)?
- [ ] Did I add a color-mapping summary and dropped-colors log in `BlockStyles`?
- [ ] Did I pass the color sanity check (visual parity of key elements)?
- [ ] Did I reuse or learn from patterns found in existing project blocks or `documentation/manuals/sx_manual_intro/blocks/`?

## 5. Second-Pass Verification & Refinement (MANDATORY)

After you have a complete first version of the migrated block (imports, `BlockStyles`, and `build()` implemented), you MUST perform a **second pass** before considering the task done:

1. **Re-read the Source HTML Carefully**
   - Walk through the original HTML **top-to-bottom**.
   - For each meaningful element (headings, paragraphs, lists, tables, callouts, links, images):
     - Confirm there is a corresponding structure in the StreamTeX block.
     - Confirm its styling (bold/italic, alignment, color, background, borders) is represented.
   - If any element or style is missing or approximated too loosely, **update the block code**, not just comments.

2. **Re-read the Migration Rules**
   - Re-skim this file and `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`.
   - Check explicitly that:
     - No intentional color from the HTML was dropped during consolidation.
     - Default/theme-dependent colors (pure black/white) are not hardcoded.
     - Tables, lists, and line breaks are mapped to `sx.st_grid`, `sx.st_list`, and `sx.st_br` where appropriate.

3. **Refine the Block Implementation**
   - Adjust `BlockStyles` and `build()` to fix any mismatches found during the re-read.
   - Prefer **improving existing structures** (styles, helper functions, grids) over adding ad-hoc one-off code.
   - Keep the code aligned with patterns already established in the project.

4. **Second-Pass Checklist**
- [ ] I re-read the full source HTML after the first implementation.
- [ ] I re-read the html-migration and color-fidelity rules after the first implementation.
- [ ] I checked: no multi-span inline content wrongly split into multiple `st_write` calls (should be one `st_write` with tuples).
- [ ] I checked: styles include font size when HTML shows text larger than 12pt.
- [ ] I updated the block code (styles and layout) based on discrepancies found in the second pass.
- [ ] I verified that every visually meaningful element in the HTML has a faithful counterpart in the block.
