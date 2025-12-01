# Handoff — Rule 051 (Cursor Insight & Handoff)
Generated: 2025-12-01T09:54:55.069399

## Goal
Continue work from previous chat session with full context and baseline evidence.

## Required Hints

- **docs.dms_only**: DMS-only, no fallback. share/ is derived from control.doc_registry only.
- **share.dms_only**: share/ sync is DMS-only. No manifest fallback.
  Commands:
    - `make share.sync`
- **governance.fail_closed**: Governance scripts must fail-closed on errors. No silent fallbacks.

## Baseline Evidence

### 1. Repository Information
```bash
git rev-parse --show-toplevel
```
**Output:** `/home/mccoy/Projects/Gemantria.v2`

```bash
git rev-parse --abbrev-ref HEAD
```
**Output:** `main`

```bash
git status -sb
```
**Output:**
```
## main...origin/main
 M pmagent/cli.py
 M scripts/control/control_status.py
?? pmagent/handoff/
?? scripts/triage_pmagent_dms_master.py
?? scripts/verify_pmagent_dms_master.py
?? share/kb_registry.json
?? share/runtime/
```

### 2. Hermetic Test Bundle

```bash
ruff format --check . && ruff check .
```
*Run and paste output*

```bash
make book.smoke
```
*Run and paste output*

```bash
make ci.exports.smoke
```
*Run and paste output*

## Next Steps

1. Run the commands above and paste their outputs
2. Review git status and PR state (if applicable)
3. Continue with the next task

---

*Source: AGENTS.md + RULES_INDEX.md + .cursor/rules/050 + .cursor/rules/051*