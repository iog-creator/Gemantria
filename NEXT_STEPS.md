# NEXT_STEPS (author: GPT-5)

## Branch
feature/phase8-kickoff-001

## Tasks (Cursor executes these)

### 1) Add Phase-8 plan (docs only)
- [ ] Create `docs/PHASE8_PLAN.md` with the exact content below:

# Gemantria — Phase-8 Plan (Scope & Milestones)

> Source of truth for Phase-8 goals; no CI/gate changes. Use alongside `docs/INDEX.md`.

## Objectives (P0)
- Reliable end-to-end graph updates with checkpointing (now in main).
- Deterministic batch semantics (single DEFAULT_BATCH_SIZE + env override).
- Bible DB strict read-only consumption (no writes to scripture tables).
- Governance continuity: Rule-037/038 gates, share no-drift, NEXT_STEPS.

## Deliverables (P0 → P1)
- P0: Evaluation harness skeleton (local smoke only), dataset notes, success metrics grid.
- P1: Automated eval report artifacts in `/share` (future PR; not part of this commit).

## Success Metrics (initial)
- Export integrity: 100% Rule-038 pass
- Join/coverage sanity: 100% Rule-037 pass
- Eval smoke: 100% tasks reach "OK" (non-flaky)
- Latency budget: TBD after real run; target p95 export step ≤ N sec

## Workstream Anchors
- Checkpointer usage patterns, Batch processor invariants, RO Bible node integration, Export smoke expansions (future), Reranker hygiene.

### 2) Add local eval smoke target (no CI wiring)
- [ ] Create `scripts/eval/run_eval.py` with exact content:

#!/usr/bin/env python3
import sys
def main():
    print("[eval.smoke] starting")
    # placeholder – add real eval tasks in a future PR
    print("[eval.smoke] OK")
    return 0
if __name__ == "__main__":
    sys.exit(main())

- [ ] Modify `Makefile` to add **local-only** targets (do NOT change the `go` recipe ordering; do NOT add CI steps):

.PHONY: eval.smoke ci.eval.smoke

eval.smoke:
@python3 scripts/eval/run_eval.py

# Intentionally same as local for now; not wired into CI

ci.eval.smoke:
@python3 scripts/eval/run_eval.py

### 3) AGENTS note (docs-only; keep governance intact)
- [ ] Append under "Operations → Evaluation" in `AGENTS.md`:

* **Phase-8 local eval**: `make eval.smoke` runs a non-CI smoke to validate the eval harness. Do not wire into CI or `make go` until stabilized. Governance gates (037/038, share no-drift, NEXT_STEPS) remain unchanged.

### 4) Open PR
- [ ] Head: `feature/phase8-kickoff-001` → Base: `main`
- [ ] Title: `docs/eval: add Phase-8 plan and local eval.smoke (no CI changes)`
- [ ] Body states:
  - No changes to CI workflow order, gate set, or `make go`.
  - Adds `docs/PHASE8_PLAN.md`, local eval smoke target and script, AGENTS note.

### 5) Evidence tails (paste in PR)
- [ ] Show the first lines of the plan:

git show HEAD:docs/PHASE8_PLAN.md | sed -n '1,40p'

- [ ] Prove make targets exist and run:

rg -n "eval\.smoke" Makefile
make eval.smoke

Expected output contains:
- `[eval.smoke] starting`
- `[eval.smoke] OK`

### 6) Merge
- [ ] **Squash & Merge** with title:

docs/eval: add Phase-8 plan and local eval.smoke (no CI changes)

## Acceptance checks (Cursor pastes under Evidence tails)
- `docs/PHASE8_PLAN.md` content snippet
- `Makefile` diff lines showing `eval.smoke` and `ci.eval.smoke`
- `make eval.smoke` tails show `[eval.smoke] OK`
- PR merged with exact title

## Status
- Cursor sets to **Done** when merged and evidence is pasted.
