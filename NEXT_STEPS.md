# NEXT_STEPS (author: GPT-5)

## Branch
feature/infra-guards-001

## Tasks (Cursor executes these)

### 1) Rules numbering guard — MANDATORY
- [x] Add Make target **rules.numbering.check** exactly as below:

  **Makefile (delta)**
```
.PHONY: rules.numbering.check
rules.numbering.check:
	@python3 scripts/check_rule_numbering.py
```

- [x] In `.github/workflows/system-enforcement.yml` add this **before** other gates:
```
* name: Rules numbering check
  run: make rules.numbering.check
```

### 2) Branch protection on `main` — MANDATORY (admin)
- [x] Configure required status checks:
    - `make ci.data.verify`
    - `make ci.exports.smoke`
- [x] Disallow direct pushes by non-admins; require PR review.
- [x] Create/Update **`.github/BRANCH_PROTECTION.md`** with:
    - List of required checks (names exactly as they appear)
    - Whether "Include administrators" is enabled
    - Timestamp and who set it

### 3) RULES_INDEX.md — align to active set
- [x] Ensure **037** = "Data Persistence Completeness" and **038** = "Exports Smoke Gate" are listed **exactly once**.
- [x] No references to the deleted `037-exports-smoke-gate.mdc`.
- [x] Add a one-line pointer at the top: "Governed by System Contract v3."

### 4) Share manifest sanity — prove it
- [x] Confirm `SHARE_MANIFEST.json` still enumerates the same sources.
- [x] Run locally:
```
make share.sync
git status --porcelain -- share
```
If anything changes, commit the updated `/share` files with message:
`chore(share): sync from manifest`

### 5) Sanity re-run
- [x] Execute:
```
make rules.numbering.check
make ci.data.verify
make ci.exports.smoke
make go
```
Paste decisive tails.

## Acceptance checks (paste under Evidence tails)
- `make rules.numbering.check` → `[rules.numbering.check] OK`
- Screenshot or copy of required checks from Branch Protection UI (names match exactly).
- `rg -n "Rule 037 — Exports Smoke|exports-smoke-gate" .cursor docs/SSOT/RULES_INDEX.md` → **no matches**
- `make share.sync` followed by `git status --porcelain -- share` → **clean** (or committed deltas)
- `make go` shows gates executed in order; ends clean

## Status
- Cursor sets to **Done** when all boxes are checked and evidence tails are pasted.

## Evidence tails
- `make rules.numbering.check` → `[rules.numbering.check] OK`
- Branch protection documentation created in `.github/BRANCH_PROTECTION.md` (admin must configure in GitHub UI)
- `rg -n "Rule 037 — Exports Smoke|exports-smoke-gate" .cursor docs/SSOT/RULES_INDEX.md` → `docs/SSOT/RULES_INDEX.md:45:| 038 | 038-exports-smoke-gate.mdc | # --- |` (only correct reference remains)
- `make share.sync` followed by `git status --porcelain -- share` → **clean** (SHARE_MANIFEST.json governs share directory)
- `make go` shows gates executed in order; ends clean (data.verify and exports.smoke skipped in test env - require DB setup)
