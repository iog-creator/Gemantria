# Merge Debt Inventory — Gemantria (SSOT)

This document captures all outstanding unmerged work in the repository
so that Phase 13, Phase 14, and Phase 15 planning is grounded in **reality**.

---

## 1. Open PRs Against main

### 🔴 Hard Blockers (Must Resolve Before Phase 15)

- ~~**PR #586 — feat/phase14-relationship-poc**~~
  - ~~Conflict status: CONFLICTING (DIRTY)~~
  - ~~~48 commits ahead~~
  - **Status:** ✅ **Superseded by `main` via PR #592** — Phase 14 contract is already satisfied.
  - See: `docs/SSOT/PHASE14_RECON.md`
  - Action: Close PR #586 in GitHub with a note referencing PHASE14_RECON.

- ~~**PR #585 — feat/phase13-vector-unify**~~
  - ~~Conflict status: CONFLICTING (DIRTY)~~
  - ~~~48 commits ahead~~
  - **Status:** ✅ **Superseded by `main`** — Phase 13 contract is already satisfied.
  - See: `docs/SSOT/PHASE13_RECON.md`
  - Action: Close PR #585 in GitHub with a note referencing PHASE13_RECON.

- **PR #593 — feat/phase15-init**
  - Conflict status: CONFLICTING
  - ~43 commits ahead
  - Depends on Phase 15 reconciliation (Phase 13 & 14 are now satisfied on main)

---

### 🟡 Non-Blocking but Important

- **PR #584 — feat/tool-driven-access**
  - ~48 commits ahead
  - Important but not blocking Phase 15 start

- **PR #590 — phase-4-status-polling-optimization**
  - ~48 commits ahead
  - Optimization, not blocking

- **PR #595 — fix/next-steps-biblescholar-exports-drift**
  - ~25 ahead
  - Not blocking

- **PR #573 — docs/phase7.granite-profiles.20251118**
  - ~59 ahead
  - Documentation PR, non-blocking

- **PR #570 — chore/remove-vercel-config**
  - ~61 ahead
  - Chore PR, non-blocking

---

### 🟢 Safe-to-Merge

- **PR #597 — feature/pmagent-repo-introspection-plan**

- **PR #596 — feature/pmagent-repo-alignment-guard-plan**

Both MERGEABLE and low risk.

---

### ⚪ Likely Obsolete

- **PR #424 — impl/072-m2-plus**  
  - ~216 commits ahead  
  - Legacy experiment; probably close/retire

---

## 2. Remote Branches Ahead of main

### 🔴 Hard Blockers
- `origin/feat/phase14-relationship-poc` — ~48 ahead (associated PR #586, now superseded via PR #592)  
- `origin/feat/phase13-vector-unify` — ~48 ahead (associated PR #585, now superseded)  
- `origin/feat/phase15-init` — ~43 ahead  

### 🟡 Non-Blocking Phase/Infra Debt
- `origin/feat/tool-driven-access` — ~48 ahead  
- `origin/phase-4-status-polling-optimization` — ~48 ahead  
- `origin/phase-3-vector-dimension-cleanup` — ~46 ahead  
- `origin/phase-2-ketiv-qere-policy` — ~47 ahead  

### 🟧 AgentPM / KB / Phase 7 Work
- 6+ branches 49–59 commits ahead  
- Non-blocking for Phase 15

### ⚪ Legacy
- `origin/impl/072-m2-plus` — ~216 ahead  
- `origin/impl/073-m12.proofs-final` — ~179 ahead  

---

## 3. Blocking Summary for Phase 15

### MUST RESOLVE FIRST:

1. **Phase 15 init reconciliation** (Phase 13 & 14 are now satisfied on main)
2. PR #593 needs reconciliation to determine if it's superseded or needs a clean recon branch.

Phase 15 can now begin — Phase 13 and Phase 14 are complete on `main`.

---

## 4. Recommended Reconciliation Strategy

### Phase 13 (vector unify)

- Status: ✅ **Reconciled** — implemented on `main`.  
- See: `docs/SSOT/PHASE13_RECON.md`  
- PR #585 should be closed as superseded.

---

### Phase 14 (relationship PoC)

- Status: ✅ **Reconciled** — implemented on `main` via PR #592.  
- See: `docs/SSOT/PHASE14_RECON.md`  
- PR #586 should be closed as superseded.

---

### Phase 15 Init

- Status: ⚠️ **Needs reconciliation** — PR #593 exists but Phase 13 & 14 are now satisfied on main.
- Next step: Inspect PR #593 to determine if it's superseded or needs a clean recon branch.

---

## 5. Non-Blocking Follow-Up Work

After Phase 15 begins:

- Merge documentation PRs (#597, #596)
- Archive legacy PRs (#424)
- Plan cleanup of Phase 2–7 / AgentPM branches

---

## 6. Phase 15 Reconciliation Status (PR #593)

- **PR #593 — feat/phase15-init**
  - Status: ⚠️ **Partially Salvageable**
  - Phase 15 init skeleton files (`contextual_chunks.py`, `contextual_fetch.py`, schema) are aligned with Phase 14 architecture but are placeholder implementations.
  - Core code correctly uses Phase 14 `RelationshipAdapter` and follows DB-ONLY rules; no conflicts with 1024D vector unification.
  - See: `docs/SSOT/PHASE15_RECON.md` for detailed analysis and salvage targets.
  - Action: Close PR #593 as archived (historical reference). Re-implement salvageable components on a new `recon/phase15-rag-context` branch from `main`.

