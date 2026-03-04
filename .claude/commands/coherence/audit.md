Audit the StreamTeX ecosystem for cross-component coherence issues.

Arguments: $ARGUMENTS (optional scope: all | library | docs | profiles | blocks — default: all)

## Steps

1. **Locate workspace root**: Find the nearest parent directory containing `stx.toml`.
   The workspace root contains: `streamtex/`, `streamtex-docs/`, `streamtex-claude/`, `projects/`.

2. **Load rules**: Read `.claude/developer/skills/coherence-checks.md`.

3. **Determine scope** from arguments:
   - `all` (default) — Run all 8 check categories
   - `library` — Checks 1 + 2 only (API coverage, cheatsheet sync)
   - `docs` — Checks 3 + 6 only (cross-manual consistency, block structure)
   - `profiles` — Checks 4 + 8 (profile file sync, stx-guide sync)
   - `blocks` — Checks 3 + 6 + 7 (block patterns, structure, template freshness)

4. **Execute checks** for the selected scope. For each check:
   - Read the specified source files
   - Compare against the expected state defined in coherence-checks.md
   - Record findings with severity (ERROR / WARNING / INFO)

5. **Report findings** in the output format below.

## Output Format

```
## Coherence Audit — [scope]

### Summary
| Category | Status | Issues |
|----------|--------|--------|
| API Coverage | ⚠ 3 warnings | |
| Cheatsheet Sync | ✓ OK | |
| ... | | |

### ERRORS (N) — must fix
- [Category] File:Line — Description → Suggested fix

### WARNINGS (N) — should fix
- [Category] File:Line — Description → Suggested fix

### INFO (N) — for awareness
- [Category] Description
```
