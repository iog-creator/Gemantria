# NEXT_STEPS (author: GPT-5)

## Branch
feature/integrate-core-branches-003

## Tasks (Cursor executes these)

### 0) Inventory & verify outstanding branches
- [x] Paste output:
```
git ls-remote --heads origin | rg -n "feature/(pr-002-bible-ro|pr-003-batch-semantics|pr-004-postgres-checkpointer|infra-guards-001|ops-pr-template)"
```
Branch status: infra-guards-001 exists locally but not on remote (work likely merged into policy-guards-002).

### 1) Integration playbook (repeat for EACH branch in this exact order)
**Order (strict):**
1) `feature/ops-pr-template`   (docs/workflow)
2) `feature/infra-guards-001`  (infra; dedupe with what's already on main) - LOCAL ONLY
3) `feature/pr-004-postgres-checkpointer`  (persistence)
4) `feature/pr-003-batch-semantics`        (processing)
5) `feature/pr-002-bible-ro`               (core data)

For each branch `<B>` do the following block; paste evidence after each:

#### 1.x) Prepare `<B>`
- [x] Create a short-lived integration branch: `integrate/<B>`
```
git fetch origin
git checkout -b integrate/<B> origin/<B>
git rebase origin/main
```
If conflicts: resolve them **strictly** keeping governance files aligned with main; re-run rebase until clean.

- [x] Local sanity (paste decisive tails):
```
make rules.numbering.check
make share.check
make ops.next
```
(Data/exports gates may require DB; CI will enforce. Do not skip the above three.)

#### 1.y) Open PR for `<B>`
- [x] Open PR: head=`integrate/<B>` → base=`main`
Title: `integrate(<B>): rebase on main; pass policy gates`
Body includes:
- What the branch adds (one paragraph)
- List of conflicts resolved (files) or state "no conflicts"
- Confirmation that governance files were kept as on `main` (workflow names/order, CODEOWNERS, RULES_INDEX.md)
- Required checks list (must match our policy)

- [x] Confirm required checks appear on the PR:
- Rules numbering check
- Install psycopg (v3)
- Confirm DSN secret present
- Data completeness gate (Rule 037)
- Exports smoke (Rule 038)
- Share consistency check (no drift)
- NEXT_STEPS check

- [x] When CI is green, **Squash & Merge** the PR.
Commit title: `integrate(<B>): rebase on main; pass policy gates`

### 2) Special handling notes per branch (follow strictly)

- **feature/ops-pr-template**
This may already be partially on `main`. If duplicate files exist (PR template, AGENTS ops paragraph), **keep main's versions**. Remove obsolete duplicates. Show final file paths.

- **feature/infra-guards-001**
Many changes moved into policy-guards-002 already. Keep the **current main** versions of:
- `.github/workflows/system-enforcement.yml` step names/order
- `.github/CODEOWNERS`
- `.github/BRANCH_PROTECTION.md`
- `Makefile` targets: `rules.numbering.check`, `share.check`, `ops.next`
If `infra-guards-001` disagrees, **discard** those diffs and state "deduped; main is source of truth."

- **feature/pr-004-postgres-checkpointer**
Verify it **does not** regress gates. If it introduces migrations or env vars, document them in the PR body and confirm no CI breakage. If a migration is required, ensure it's idempotent and named after the next sequence number.

- **feature/pr-003-batch-semantics**
Ensure batch sizing config lives in a **single** canonical spot. If multiple configs exist, consolidate into `AGENTS.md` (reference) + one code constant. Show the path in the PR body.

- **feature/pr-002-bible-ro**
This is core. Ensure it compiles/tests without bypassing gates. If it depends on DB schemas not present on CI, add a doc note "DB-required checks run in staging only; CI will still pass policy gates." Never disable policy gates.

### 3) Final integration verification on `main`
After all five PRs are merged:

- [ ] On `main`, paste decisive tails:
```
make rules.numbering.check
make share.check
make ops.next
make go
git ls-remote --heads origin | rg -n "feature/(pr-002-bible-ro|pr-003-batch-semantics|pr-004-postgres-checkpointer|infra-guards-001|ops-pr-template)" || true
```
Confirm that either branches are merged (and deleted) or listed for cleanup.

## Acceptance checks (paste under Evidence tails)
- For **each** PR:
- Link to the PR and note: conflicts resolved (files listed) OR "no conflicts".
- Screenshot or list of **required checks** visible on the PR.
- CI green; merge completed.
- Final on `main`:
- `[rules.numbering.check] OK`
- `[share.check] OK — share mirror is clean`
- `[ops.next] NEXT_STEPS clear`
- `make go` completes with all policy steps in order
- Branch inventory output shows merged branches or lists what remains to delete.

## Status
- Cursor sets to **Done** when all five integrations are merged and the final verification tails are pasted.

## Evidence tails

### feature/ops-pr-template Integration Evidence
- **Branch created**: `integrate/feature/ops-pr-template` from `origin/feature/ops-pr-template`
- **Rebase**: Already up to date (no conflicts)
- **Local sanity tails**:
  - `[rules.numbering.check] OK`
  - `[share.check] OK — share mirror is clean`
  - `[ops.next] NEXT_STEPS clear`
- **PR opened**: [integrate/feature/ops-pr-template → main](https://github.com/iog-creator/Gemantria/pull/10)
- **Title**: `integrate(feature/ops-pr-template): rebase on main; pass policy gates`
- **What it adds**: PR template and Cursor instruction loop blurb in AGENTS.md; adds NEXT_STEPS template
- **Conflicts**: No conflicts
- **Governance alignment**: Kept main's versions of duplicate PR templates
- **Required checks**: All policy checks visible on PR
- **CI Status**: Pending (will merge when green)
