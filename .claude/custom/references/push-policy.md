# Push policy (NG decision, board audit1, 2026-10-03)

- **Never push** to any StreamTeX repository without first asking NG explicitly, in a dedicated question, and getting
  his answer for that specific push.
- The question must state: repository, branch, commits, which workflows the push triggers, and whether it **publishes**.
- On `streamtex`, a push to `main` that changes `version` in `pyproject.toml` **publishes to PyPI** through
  `.github/workflows/auto-tag.yml`; there is no approval gate and cancelling the run does not stop a publication
  already done (0.7.40 was published that way on 2026-10-03).
- Local commits on branches are fine. Never change the streamtex version without NG's explicit line.
