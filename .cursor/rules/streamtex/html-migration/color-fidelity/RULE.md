---
alwaysApply: true
---

# StreamTeX HTML Migration: Color Fidelity (No Missed Colors)

When migrating HTML exports (e.g., Google Docs) into StreamTeX blocks, **do not simplify away intentional colors**.

## 1. Color Audit (MANDATORY)

Before writing the block code, perform a **structured color audit** of the HTML:

### A. Scan All Color-Bearing Properties

Enumerate explicit colors for each of these CSS properties:

- **`color`** (text)
- **`background-color`**
- **`border-color`** (and borders with shorthand that include color)
- **`text-decoration-color`** (if present)

Include colors that appear **only on individual list items / spans** (common in Google Docs exports). Ignore "noise" class names (`c1`, `c12`) but **do not ignore their computed colors**.

### B. Process Aid: Hex Code List

List every hex/rgb value found in the source (e.g., via search for `#` or `rgb(`). For each value, either:

- Map it to a StreamTeX style and document the mapping, or
- Explicitly classify it as "default/theme—intentionally not migrated" and document why.

### C. Default vs. Intentional

- **Default / theme colors** (do NOT hardcode): exact `#000000`, `#ffffff`, `rgb(0,0,0)`, `rgb(255,255,255)`, or `inherit` that reflects the page theme.
- **Near-black / near-white** (e.g., `#111111`, `#222222`, `#fafafa`): if used **consistently** for a specific role (title, caption, card background), treat as **intentional** and preserve.
- **Intentional colors** (MUST preserve): any other non-default hex/rgb (e.g., `#274e13`, `#783f04`, `#1155cc`, `#ff0000`).
- **Neutral grays** (`#666`, `#888`, etc.): if used for a one-off minor detail, may be approximated or ignored; if used repeatedly for headings or UI elements, **must be migrated**.

### D. Links with Non-Default Colors

If an `<a>` element uses a **non-default blue** or any branded color, you **must** create a named style (e.g., `bs.link_style`) using explicit `s.project.colors.*` and apply it. Do not leave links unstyled when the HTML uses a distinct brand/accent color.

## 2. Mapping Rule (MANDATORY)

For every intentional color found:

- Create a **named style** for it and apply it wherever it appears.
  - Prefer project-level palette: `s.project.colors.<name>` when it's likely reused across blocks.
  - Otherwise define a local `BlockStyles` style: `bs.<semantic_name> = Style("color: #xxxxxx;")` or equivalent.
- **Never collapse differently-colored items** into one style, even if they share font size/weight/alignment.
  - Instead: make a base style (size/weight/alignment) and **add** the color style per item.

## 3. Consolidation Without Losing Color

When consolidating classes (e.g., merging `c3`, `c6`):

- **Before merging**, check whether **any** of them introduces a non-default color.
- If yes, that color **must** be preserved in the consolidated style (or factored as a separate color-only style).
- **Colors must not be approximated away.** Either map exactly to an existing palette color or introduce a new one. Do not drop colors to "simplify."

## 4. Color-Mapping Summary (MANDATORY)

In the `BlockStyles` class, add a brief **color-mapping summary** comment that documents:

- Which HTML colors were migrated and under what names (e.g., `.c18` → `#1155cc` → `s.project.colors.denim_blue`).
- Which colors were **intentionally dropped** and why (e.g., "default body black—theme-controlled").

## 5. Dropped Colors Log

If you intentionally do NOT migrate a color, add a short note in the block comments:

- Which color (hex or class) was skipped.
- Why (e.g., "default body black," "single-use decoration," "irrelevant to content").

## 6. Color Sanity Check (MANDATORY)

Before finishing the migration:

1. Pick 3–5 visually important elements (title, primary links, callouts, highlights).
2. Verify that their colors in the StreamTeX output match the intent of the original HTML (same hue family and emphasis).
3. Ensure no intentional color was accidentally omitted during consolidation.

## 7. Implementation Checklist (MUST PASS)

- [ ] I enumerated every non-default color from `color`, `background-color`, `border-color`, and `text-decoration-color`.
- [ ] I listed every **non-default** text color used in the HTML.
- [ ] I listed every **non-default** background/border color used in the HTML.
- [ ] Each intentional color has a corresponding StreamTeX style and is applied to all matching elements.
- [ ] Per-item list bullet text colors (if any) are preserved.
- [ ] I did not hardcode black/white when it should be theme-controlled.
- [ ] I added a color-mapping summary in `BlockStyles` and a dropped-colors log where applicable.
- [ ] I performed the color sanity check on key elements.
