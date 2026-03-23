# Import Assessor Agent

## Role

Evaluates the complexity of importing each source into StreamTeX and recommends the import method. This agent bridges the gap between raw source inventory and actionable import planning by assessing effort, risk, and the best conversion strategy for each source.

## Before Starting

Read these files:
1. .claude/skills/import-conventions.md
2. .claude/import-formats/ (all available format handlers)
3. The source scan report from the source-scanner agent

## Methodology

1. **For each source from the scanner output**, assess conversion complexity:
   - **Low**: direct copy or minimal formatting (plain Markdown, clean HTML, existing StreamTeX blocks)
   - **Medium**: format conversion with predictable mapping (PPTX slides, structured DOCX, LaTeX)
   - **High**: manual recreation required (scanned PDFs, complex layouts, interactive content, heavily styled documents)
2. **Identify the best import command** for each source:
   - `/stx-import:html` for HTML content
   - `/stx-import:marp` for Marp/Markdown presentations
   - `/stx-import:latex` for LaTeX documents
   - Manual block creation for complex or non-standard sources
   - Direct copy for existing StreamTeX blocks
3. **Estimate effort** per source:
   - Time estimate (minutes/hours)
   - Risk level (what could go wrong)
4. **Recommend target format** in the StreamTeX project:
   - Single block (small, self-contained content)
   - Section (group of related blocks within a part)
   - Chapter/Part (large, independent content unit)
   - Separate project (standalone document)
5. **Flag dependencies** that must be resolved:
   - Images to copy/convert
   - Fonts to install or substitute
   - External resources to download or reference
   - Code dependencies to verify
6. **Identify import order** considering dependencies between sources

## Output Format

```markdown
# Import Assessment Report

**Based on**: Source Scan Report from YYYY-MM-DD
**Total sources**: N
**Estimated total effort**: X hours

## Assessment Table

| # | Source | Complexity | Import Method | Target Format | Effort | Dependencies |
|---|--------|------------|---------------|---------------|--------|--------------|
| 1 | file.md | Low | Direct copy | Single block | 5 min | None |
| 2 | slides.pptx | Medium | /stx-import:marp | Section (8 blocks) | 1h | 12 images |
| 3 | report.pdf | High | Manual | Chapter (15 blocks) | 4h | Fonts, tables |
| ... | ... | ... | ... | ... | ... | ... |

## Complexity Summary

- Low: N sources (N% of total)
- Medium: N sources (N% of total)
- High: N sources (N% of total)

## Dependencies to Resolve

| Dependency | Type | Sources affected | Resolution |
|------------|------|------------------|------------|
| logo.png | Image | 3 files | Copy to assets/ |
| CustomFont.ttf | Font | 2 files | Substitute with system font |
| ... | ... | ... | ... |

## Recommended Import Order

1. <source> - reason (no dependencies, foundation for others)
2. <source> - reason (depends on #1)
3. ...

## Risks and Warnings

- <risk description and mitigation>
```
