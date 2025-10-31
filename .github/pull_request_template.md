## Title
<!-- concise, imperative; include PR code (e.g., 024c), scope keyword -->

## Summary
<!-- what & why in 2–4 lines -->

## References (REQUIRED)
- **Rules cited:** <!-- e.g., 039-execution-contract; 040-ci-triage; 041-pr-merge-policy -->
- **Agents referenced:** <!-- e.g., AGENTS.md#orchestrator; AGENTS.md#cursor -->
- **Docs touched:** <!-- list relative paths -->
- **SSOT links:** <!-- RULES_INDEX.md anchors; AGENTS.md anchors; SSOT_MASTER_PLAN.md sections -->

## Scope (files only)
<!-- exact list; no others -->

## Acceptance
- [ ] `make -s ops.verify` → `[ops.verify] OK`
- [ ] If Makefile edited: `make -s targets.check.dupes` → OK
- [ ] No governance/workflow drift
- [ ] CI green

## Emitted Hints (REQUIRED)
- List the key runtime HINT lines your changes will emit (e.g., `HINT: verify: database bootstrap OK`) so CI logs are clear for both Cursor and reviewers.

## Evidence tails
<!-- paste decisive tails or failing tails -->
