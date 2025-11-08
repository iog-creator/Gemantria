<!-- Handoff updated: 2025-11-07T20:01:49.979238 -->
# NEXT_STEPS v6.2.3 (Operational Status - Phases Complete)

## Status
✅ **All Core Phases Complete** - Pipeline operational with unified envelope
- Phase 0: Governance v6.2.3 ✅
- Phase 1: Data Layer (DB foundation) ✅
- Phase 2: Pipeline Core (LangGraph) ✅
- Phase 3: Exports & Badges ✅
- Phase 5: UI Polish ✅
- Phase 8: Temporal Analytics Suite ✅
- Phase 9: Graph Latest ✅
- Phase 10: Correlation Visualization ✅
- Phase 11: Unified Envelope ✅

## Current Operational Focus

### Phase 11+ — Production Operations
**Branch:** `feat/p11-unified-envelope` (current)
**Scope:** Unified envelope operations, COMPASS validation, UI integration, production hardening
**Status:** 🔄 **Active** - Branch diverged, needs reconciliation

## Development Workflow (v6.2.3)

### Per-PR Process
1. **Branch:** Use existing draft PR branches above
2. **Work:** Make changes, commit with conventional format
3. **Test:** `make [area].smoke` + `ruff format --check . && ruff check .`
4. **PR:** Mark ready, ensure policy-gate + build-pr pass
5. **Merge:** Bot-mediated squash merge when conditions met

### Quality Gates (Active)
- **policy-gate:** Conventional Commits + signed commit verification
- **build-pr:** CI checks with hermetic behavior
- **human approval:** Required for merge
- **bot mediation:** Mergify handles merge when conditions met

## Current Operator Pick
**P1-DB**: Implement migrations + `make db.migrate` + CI empty-DB tolerance.
5) `feature/pr-002-bible-ro`               (core data)

For each branch `<B>` do the following block; paste evidence after each:

#### 1.x) Prepare `<B>`
- [ ] Create a short-lived integration branch: `integrate/<B>`
```
git fetch origin
git checkout -b integrate/<B> origin/<B>
git rebase origin/main
```
If conflicts: resolve them **strictly** keeping governance files aligned with main; re-run rebase until clean.

- [ ] Local sanity (paste decisive tails):
```
make rules.numbering.check
make share.check
make ops.next
```
(Data/exports gates may require DB; CI will enforce. Do not skip the above three.)

#### 1.y) Open PR for `<B>`
- [ ] Open PR: head=`integrate/<B>` → base=`main`
Title: `integrate(<B>): rebase on main; pass policy gates`
Body includes:
- What the branch adds (one paragraph)
- List of conflicts resolved (files) or state "no conflicts"
- Confirmation that governance files were kept as on `main` (workflow names/order, CODEOWNERS, RULES_INDEX.md)
- Required checks list (must match our policy)

- [ ] Confirm required checks appear on the PR:
- Rules numbering check
- Install psycopg (v3)
- Confirm DSN secret present
- Data completeness gate (Rule 037)
- Exports smoke (Rule 038)
- Share consistency check (no drift)
- NEXT_STEPS check

- [ ] When CI is green, **Squash & Merge** the PR.
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
- **What it adds**: PR template and Cursor instruction loop blurb in AGENTS.md; adds NEXT_STEPS template
- **Conflicts**: No conflicts
- **Governance alignment**: Kept main's versions of duplicate PR templates
- **Required checks**: All policy checks visible on PR
- **CI Status**: Passed - merged with title `integrate(feature/ops-pr-template): rebase on main; pass policy gates`

### feature/infra-guards-001 Integration Evidence
- **Branch created**: `integrate/feature/infra-guards-001` from local `feature/infra-guards-001`
- **Rebase**: Successfully rebased with conflicts resolved by keeping main versions for governance files
- **Local sanity tails**:
  - `[rules.numbering.check] OK`
  - `[share.check] OK — share mirror is clean`
  - `[ops.next] NEXT_STEPS clear`
- **PR opened**: [integrate/feature/infra-guards-001 → main](https://github.com/iog-creator/Gemantria/pull/11)
- **What it adds**: Code quality improvements (import organization, linting fixes) in book_readiness.py, run_book.py, verify_data_completeness.py
- **Special handling**: Deduped governance files per integration playbook - reset .github/, Makefile, AGENTS.md to main versions (overlapping changes moved to policy-guards-002)
- **Governance alignment**: Governance files reset to main versions as source of truth
- **Required checks**: All policy checks visible on PR
- **CI Status**: Pending (will merge when green)

### 1.4) feature/pr-003-batch-semantics - PR OPEN
- [x] **Branch created**: `integrate/feature/pr-003-batch-semantics` from `origin/feature/pr-003-batch-semantics`
- [x] **Rebase**: Successfully rebased with conflicts resolved by keeping main versions for governance files
- [x] **Local sanity tails**:
  - `[rules.numbering.check] OK`
  - `[share.check] OK — share mirror is clean`
  - `[ops.next] NEXT_STEPS clear`
- [x] **PR opened**: [integrate/feature/pr-003-batch-semantics → main](https://github.com/iog-creator/Gemantria/pull/14)
- [x] **What it adds**: Batch processing with size enforcement and deterministic semantics
- [x] **Special handling**: Batch config consolidated to single canonical source (`src/graph/batch_processor.py#DEFAULT_BATCH_SIZE = 50` with `BATCH_SIZE` env override, documented in AGENTS.md)
- [x] **Governance alignment**: Governance files reset to main versions as source of truth
- [x] **Required checks**: All policy checks visible on PR
- [x] **CI Status**: Pending (will merge when green)

## Evidence tails

### Docs Index Creation (PR #13)
- **Branch created**: `feature/docs-index-005`
- **Files added**: `docs/INDEX.md` (comprehensive navigation index), one-line link in `README.md`
- **Content**: Links to RULES_INDEX, AGENTS, CI workflow, CODEOWNERS, SHARE_MANIFEST, SSOT schemas, latest exports, make targets
- **PR opened**: [feature/docs-index-005 → main](https://github.com/iog-creator/Gemantria/pull/13)
- **Purpose**: Single jump page for repo navigation without attachments
- **CI Status**: Pending (docs-only changes, policy gates still enforced)

### 1.3) feature/pr-004-postgres-checkpointer - PR OPEN
- [x] **Branch created**: `integrate/feature/pr-004-postgres-checkpointer` from `origin/feature/pr-004-postgres-checkpointer`
- [x] **Rebase**: Successfully rebased with conflicts resolved by keeping main versions for governance files and branch versions for postgres checkpointer implementation
- [x] **Local sanity tails**:
  - `[rules.numbering.check] OK`
  - `[share.check] OK — share mirror is clean`
  - `[ops.next] NEXT_STEPS clear`
- [x] **PR opened**: [integrate/feature/pr-004-postgres-checkpointer → main](https://github.com/iog-creator/Gemantria/pull/12)
- [x] **What it adds**: LangGraph-compatible Postgres checkpointer with BaseCheckpointSaver interface, JSONB storage, and transactional upsert semantics
- [x] **Special handling**: Verified no gate regressions; migration `002_create_checkpointer.sql` documented (creates checkpointer_state and checkpointer_writes tables)
- [x] **Governance alignment**: Governance files reset to main versions; postgres implementation preserved
- [x] **Required checks**: All policy checks visible on PR
- [x] **CI Status**: Pending (will merge when green)
