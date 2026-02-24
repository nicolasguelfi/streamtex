# Presentation Design Rules — `ros_designer_default`

> **Relationship to base rules**: This file **extends** `visual-design-rules.md` (shared skills).
> Where a rule here conflicts with the base, **this file wins**.
> Base rules still apply for anything not overridden here.

These rules target **live presentations** projected at 10–20 m distance.
They optimize for instant readability and visual impact.

---

## Rule 1 — Keywords Only

**No sentences on slides.** Each bullet is a keyword phrase.

| Constraint | Limit |
|---|---|
| Words per bullet | 5–7 max |
| Bullets per section | 3 max |

### WRONG
```python
st_write(bs.body, "84% of respondents are using or planning to use AI tools "
    "in their development process, an increase over last year.")
```

### CORRECT
```python
st_write(bs.body, "84% use or plan AI tools")
st_write(bs.body, "51% daily usage among pros")
st_write(bs.body, "+8% vs 2023")
```

---

## Rule 2 — Font Size for Distance

Audience at 10–20 m needs large text, but sizes must stay **proportional**
so that the full slide fits on one screen.

| Element | Size | StreamTeX style | Notes |
|---|---|---|---|
| Course title | 96pt | `s.Huge` / `s.project.titles.course_title` | Title slide only |
| Section titles | 80pt | `s.huge` / project section title | Page headings |
| Subtitles | 48pt bold | `s.Large + s.bold` | |
| Body text | 48pt | `s.Large` | Main readable content |
| Attribution/source | 32pt | `s.large` | Footers, sources |
| Caption/footer | 32pt | `s.large` | |

> **Giant (128pt) and GIANT (196pt) are exceptional** — use only for
> single-word decorative elements (e.g. a number, an icon label).
> Never use them for multi-word titles: they overflow the viewport.

> **Override**: base `visual-design-rules.md` uses `s.large` (32pt) for body.
> In presentation mode, body is `s.Large` (48pt) minimum.

### WRONG
```python
st_write(s.large, "Key takeaway")       # 32pt — too small at distance
st_write(s.medium, "Source: Survey 2024") # 16pt — invisible
```

### CORRECT
```python
st_write(s.Large, "Key takeaway")        # 48pt — readable at distance
st_write(s.large, "Source: Survey 2024")  # 32pt — acceptable for attribution
```

---

## Rule 3 — Visual First

Prefer symbols, icons, and images over text. A chart or diagram replaces a paragraph.

### WRONG
```python
st_write(bs.body, "The adoption rate increased significantly over the past year")
```

### CORRECT
```python
st_write(bs.body, "Adoption rate: 76% → 84%")
# or better: show a chart
```

---

## Rule 4 — One Idea Per Section

Each section conveys **one concept**. If you need to explain two things, use two sections (or two slides).

---

## Rule 5 — High Contrast

Never use `muted` or `subtle` colors on body text. Reserve them for attribution only.

| Color usage | Allowed elements |
|---|---|
| `s.project.colors.primary` | Titles, emphasis |
| `s.project.colors.accent` | Subtitles, highlights |
| `s.project.colors.muted` | Source lines, footers ONLY |
| `s.project.colors.subtle` | NEVER on readable content |

### WRONG
```python
st_write(s.project.colors.muted + s.Large, "Important takeaway")
```

### CORRECT
```python
st_write(s.project.colors.accent + s.Large + s.bold, "Important takeaway")
```

---

## Rule 6 — Generous Spacing

Presentation slides need breathing room.

| Between | Spacing |
|---|---|
| Major sections | `st_space(size=4)` |
| Sub-sections | `st_space(size=3)` |
| Elements within a section | `st_space(size=2)` |

> **Override**: base rules use `st_space("v", 2)` between sections.
> Presentations use `st_space(size=4)` between major sections.

---

## Rule 7 — No Helper Boxes

Presentation slides do NOT use `show_explanation()`, `show_details()`, `show_code()`.
These are for pedagogical/tutorial slides, not live presentations.

Use direct `st_write()` calls instead.

### WRONG
```python
show_explanation("Key findings from the survey")
```

### CORRECT
```python
st_write(bs.body, "Key findings from the survey")
```

---

## Rule 8 — Image Sizing

Images must be large enough to see from the back of the room.

| Constraint | Minimum |
|---|---|
| Image width | 400px |
| Preferred width | 600px+ |
| Logo (decorative) | 160px acceptable |

---

## Rule 9 — Simplified Block Structure

Presentation blocks use a reduced set of style roles:

```python
class BlockStyles:
    heading = ...    # Section title (Huge 96pt or huge 80pt — never Giant)
    sub = ...        # Subtitle (Large + bold)
    body = ...       # Body text (Large) — the main content style
    body_accent = ...  # Accented body (Large + accent color)
    caption = ...    # Attribution/source (large, muted)
```

No `explanation`, `details`, `code_example` — those belong to tutorial slides.
