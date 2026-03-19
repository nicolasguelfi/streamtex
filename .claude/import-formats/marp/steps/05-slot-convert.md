# Step 5 — Convert Slots (Instructor Notes)

> **Profile-aware:** Read the active profile from `.claude/import-formats/marp/profiles/{profile}.md`
> to determine how slots are handled.

Skip this step if `--no-slots` is specified.

## Profile-Specific Behavior

### slides profile

- **Default:** Skip entirely (`--no-slots` implied)
- **If forced:** Extract only slide-compatible content:
  - Core Content section → key bullets
  - Learning Objectives → omitted
  - Context / References → omitted
  - Speaker notes → Python comments

### document profile

- **Default:** Fully integrate all slot content
- **Parse** slot sections:

| Slot Section | StreamTeX Component |
|---|---|
| Learning Objectives | `show_explanation()` at top of block |
| Context / Why | `show_explanation()` after title |
| Core Content | Main block body (full text, lists, images) |
| Hands-On / Checkpoint | `show_details()` with activity instructions |
| Key Takeaways | Styled `st_list()` at end of block |
| References | `show_details()` with links |

### document profile template

```python
def build():
    st_write(bs.headline, "Topic Title", toc_lvl="1")

    # From slot: Learning Objectives
    show_explanation("""\
        By the end of this session, you will be able to:
        - Objective 1
        - Objective 2
    """)

    st_space("v", 2)

    # From slot: Core Content (main body)
    st_write(bs.headline, "Key Concept", toc_lvl="+1")
    st_write(bs.body, "Full explanation from the slot...")
    with st_list(l_style=bs.body, li_style=bs.body) as l:
        with l.item(): st_write(bs.body, "Detailed point 1")
        with l.item(): st_write(bs.body, "Detailed point 2")

    # From slot: Hands-On
    show_details("""\
        **Activity:** Follow these steps...
        1. Step one
        2. Step two
    """)

    # From slot: References
    show_details("""\
        **References:**
        - [Link 1](https://...)
        - [Link 2](https://...)
    """)
```

## Rules

- Apply the same Zero Residual Markdown rules as step 4
- Slot content in `show_explanation()` and `show_details()` uses Markdown
  (these helpers render via `st_markdown()` internally — this is allowed)
- Main body content (`st_write()`, `st_list()`) must use native `stx.*` components
