# Template: course

StreamTeX pedagogical course with structured chapters.

## Defaults

| Setting | Value |
|---------|-------|
| Type | presentation |
| Audience | screen (upgrade to auditorium if user specifies projection) |
| Theme | dark |
| Pagination | yes |
| TOC | `NumberingMode.SIDEBAR_ONLY`, `sidebar_max_level=2`, `search=True` |
| Sidebar | `initial_sidebar_state="expanded"` |
| Banner | `BannerConfig.full()` |
| Marker | `MarkerConfig(auto_marker_on_toc=1, show_nav_ui=True)` |
| Body font | `s.large` (32pt) — screen / `s.Large` (48pt) — auditorium |
| Title font | `s.huge` (80pt) |
| Max blocks | 15 (otherwise suggest splitting into collection) |

## Pedagogical structure

A course follows a strict pedagogical progression:

### Phase 1: Context (1-2 blocks)
- **Title block** (Blueprint 1): Course name, instructor, date
- **Objectives block** (Blueprint 3): Learning objectives as bullet points

### Phase 2: Core content (N blocks)
Each chapter follows the pattern:
- **Section header** (Blueprint 2): Chapter title and overview
- **Concept explanation** (Blueprint 3): Key concepts with bullets
- **Illustration** (Blueprint 5 or 11): Diagram or AI-generated visual
- **Practical demo** (Blueprint 6): Code examples with output
- **Exercise / quiz** (Blueprint 3): Practice questions or key points

### Phase 3: Synthesis (1-2 blocks)
- **Summary** (Blueprint 10): Key takeaways from all chapters
- **Next steps** (Blueprint 3): References, further reading, assignments

## Blueprint mapping

| Chapter element | Blueprint | Notes |
|----------------|-----------|-------|
| Course title | 1 — Title | First slide |
| Learning objectives | 3 — Text Content | Bullet list |
| Chapter header | 2 — Section Header | "Chapter N: Title" |
| Concept explanation | 3 — Text Content | Key points |
| Visual illustration | 5 — Image + Text | Diagram + explanation |
| Code demonstration | 6 — Code + Result | Live code example |
| Comparison | 4 — Two-Column Comparison | "Approach A vs B" |
| Process/workflow | 7 — Timeline | Step-by-step |
| Key takeaway | 8 — Quote | Important message |
| Chapter summary | 10 — Conclusion | End-of-chapter recap |
| Course conclusion | 10 — Conclusion | Final takeaways |

## Typical course structure (6 chapters)

```
 1.  bck_title              Blueprint 1   Course title
 2.  bck_objectives         Blueprint 3   Learning objectives
 3.  bck_ch1_header         Blueprint 2   Chapter 1: Introduction
 4.  bck_ch1_content        Blueprint 3   Chapter 1 content
 5.  bck_ch1_demo           Blueprint 6   Chapter 1 demo
 6.  bck_ch2_header         Blueprint 2   Chapter 2: ...
 7.  bck_ch2_content        Blueprint 3   Chapter 2 content
 8.  bck_ch2_comparison     Blueprint 4   Chapter 2 comparison
 ...
13.  bck_ch6_content        Blueprint 3   Chapter 6 content
14.  bck_summary            Blueprint 10  Course summary
15.  bck_next_steps         Blueprint 3   References & assignments
```

## Reference files

- `.claude/designer/agents/project-architect.md` — architecture agent for planning
- `.claude/designer/skills/block-blueprints.md` — all available blueprints
