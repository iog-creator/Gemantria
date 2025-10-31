# Quality Dashboard (Nightly)

**What we track (nightly, non-blocking):**
- **Typing (MyPy):** error count (`mypy_history` artifact, JSONL)
- **Lint (Ruff):** issue count (`ruff_history` artifact, JSONL)
- **Coverage:** percent (`coverage_history` artifact, JSONL)

**Where to see results:**
- Actions → *typing-nightly*, download: `mypy_full_report`, `mypy_history`
- Actions → *lint-nightly*, download: `ruff_full_report`, `ruff_history`
- Actions → *coverage-nightly*, download: `coverage_report`, `coverage_history`

**Badges:**
If `ALLOW_BADGE_COMMITS=true`:
- Rendered in README from `share/eval/badges/*.svg`
Else:
- Grab `quality_badges` artifact from the *quality-badges* workflow.

**Threshold warnings (optional):**
- Set repo variables:
  - `TYPING_WARN_MAX` (int), `LINT_WARN_MAX` (int), `COVERAGE_WARN_MIN` (float)
- Nightlies will emit **HINT: … WARN:** lines when exceeded (jobs still succeed).

**Governance note:** Nightlies are **observability only** — they never block PRs.
