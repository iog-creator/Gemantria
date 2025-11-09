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

## Visual QA (Cursor Browser) — REQUIRED (HINT)
- [ ] I ran `npm run dev` in `/ui` and opened the app with Cursor's **Browser** tool
- [ ] I navigated to the **Cross-References** page and verified:
  - Chips render (first 5 + "+N more")
  - Hover styles apply
  - Clicking a chip opens the **Side Panel**; close works
  - Search filters by Hebrew/gematria
- [ ] I added screenshots in a PR comment titled **"Cursor Browser QA — XRef Visualization"**

> Runbook: `docs/runbooks/CURSOR_BROWSER_QA.md`

## Acceptance (governance v6.2.3)
- [ ] ruff format/check green (SSOT)
- [ ] `make ops.verify` passes (Rule-054 duplicate guard)
- [ ] Smokes relevant to this area green
- [ ] No new knobs or duplicate scaffolds

## Emitted Hints (REQUIRED)
- List the key runtime HINT lines your changes will emit (e.g., `HINT: verify: database bootstrap OK`) so CI logs are clear for both Cursor and reviewers.

## Evidence (paste outputs)
Run locally and paste these four lines (from `make evidence.bundle`):

- `OK: canonical repo layout present.`
- `OK: enrichment details preserved on N nodes.`
- `OK: crossrefs extracted for X/Y verse-mentioning nouns.`
- One `jq` JSON line showing `confidence` plus two OSIS refs.

Also confirm: **UI build finished without TS errors**.
