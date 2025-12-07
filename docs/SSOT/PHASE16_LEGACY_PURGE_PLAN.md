# Phase 16: Legacy Purge Plan

**Status:** PLANNING  
**Owner:** PM + Cursor (OPS Mode)  
**Governance:** Gemantria OPS v6.2.3 (Rules 050, 051, 052 active)

---

## 1. Objective

Remove legacy artifacts that:
- Are not registered in the KB/DMS registry
- Are not referenced by SSOT documentation
- Are not active code paths in the current system
- Are not essential infrastructure or configuration

This ensures:
- Clean semantic search (no stale embeddings)
- Reduced cognitive overhead for agents
- Clear separation between SSOT and legacy content
- Deterministic governance surface

---

## 2. Scope

### In Scope
- Documentation files (`*.md`) not in KB registry
- Code files not actively used or imported
- Deprecated scripts and utilities
- Stale experimental notebooks and scratch files
- Database reconciliation (registry + embeddings)

### Out of Scope
- Bible database (`bible.db`) - READ-ONLY, never touched
- Active SSOT documentation (registered in DMS)
- Current production code paths
- Essential infrastructure and configuration files

---

## 3. Allowed Surface Policy (What Survives)

### 3.1 KEEP

The following categories are explicitly preserved:

- **SSOT Documentation**: All docs registered in `control.doc_registry` with `enabled=true`
- **Active Code**: All Python modules imported by current agents and scripts
- **Tests**: All test files under `tests/` and `pmagent/*/tests/`
- **Guards**: All governance guards under `scripts/guards/`
- **Exports**: Current export artifacts and schemas

#### 3.1.0 AGENTS Docs Are Always KEEP

AGENTS.md variants that are registered in the KB/DMS registry with:
- `is_ssot=true`, and
- `enabled=true`

are explicitly and unconditionally classified as **KEEP**.

These documents define the project's agent framework and are required for governance, orchestration, and tool routing.

---

### 3.1.1 Infra / Config Whitelist (Always KEEP)

The following files are essential infrastructure and **must always be kept**, even if not present in the KB registry:

- `pyproject.toml`
- `Makefile`
- `README.md`, `README_FULL.md`
- `RULES_INDEX.md`
- `CHANGELOG.md`, `RELEASES.md`
- `.github/workflows/*.yml` (CI workflows)
- `pytest.ini`
- `pre-commit-config.yaml`
- Any required config file (`*.cfg`, `*.toml`, `*.yaml`, `*.yml`)

These files define the operational structure of the repository and cannot be classified as legacy.

---

### 3.1.2 Runbooks Policy

Runbooks are kept if:
- `is_ssot=true`
- `enabled=true`
- `dominant_importance ∈ {core, high}`

Older or superseded runbooks should:
- Be marked `enabled=false` in the registry
- Optionally moved to `archive/runbooks/`

This avoids drift between old procedures and current operational reality.

---

### 3.1.3 Notebook / Scratch / Experiment Cleanup

Files under the following directories are **DELETE/ARCHIVE candidates by default**:

- `notebooks/`
- `scratch/`
- `experiments/`
- `tmp/`

These may only be kept if explicitly registered in the KB registry with `enabled=true`.

---

### 3.2 MOVE (Archive)

#### Default Rule for Unregistered Docs

Any `*.md` file located under:
- `docs/`
- `docs/SSOT/`

that:
1. does **not** appear in the KB/DMS registry, **and**
2. is **not referenced** by any KEEP file

is classified as **MOVE** or **DELETE** by default.

This ensures the documentation surface stays tightly aligned with the registry and prevents drift.

#### Archive Candidates

Candidates for archival (move to `archive/` directory):

- Documentation superseded by newer SSOT docs
- Old implementation plans (pre-Phase 10)
- Deprecated agent modules with historical value
- Old test vectors replaced by newer versions

---

### 3.3 DELETE

Hard delete candidates:

- Generated artifacts that can be regenerated
- Duplicate documentation
- Empty or placeholder files
- Build artifacts accidentally committed

---

## 4. Embedding Scope Policy

### 4.1 Current Embeddings

Only docs registered in `control.doc_registry` with `enabled=true` should have embeddings.

### 4.2 Cleanup Actions

- Remove embeddings for deleted docs
- Remove embeddings for docs marked `enabled=false`
- Preserve embeddings for archived docs (optional, based on policy)

### 4.3 Re-embedding

After purge, if `enabled=true` docs lack embeddings:
- Run `make housekeeping` to regenerate embeddings
- Verify via `pmagent kb registry --enabled` that all active docs have embeddings

---

### 4.3.1 Registry-Driven Embedding Source of Truth

Embedding pipelines **MUST**:
- Select documents exclusively via the KB/DMS registry
- Never embed files discovered by filesystem globbing
- Fail **loudly** if a file lacks a registry row

Any document without a registry row is **not eligible for embedding** under any circumstance.

---

### 4.4 DB Reconciliation After Cleanup

After filesystem cleanup, the DMS must be reconciled:

1. Identify registry rows whose `path` no longer exists.
2. Mark such rows `enabled=false` or delete them if policy allows.
3. Remove:
   - Dead embeddings
   - Dead document fragments
   - Dead sync-state entries
4. Write evidence to:
   - `share/PHASE16_DB_RECON_REPORT.json`

This ensures the semantic pipeline and governance queries reflect the cleaned repo.

---

## 5. Implementation Steps (Phase 16 Work)

### Phase 16.1: Audit Current State

#### Mandatory Pre-Check: `make reality.green STRICT`

Before running any classification, inventory, or purge work, Cursor **must**:

```bash
make reality.green STRICT
```

The output must be recorded into:
- `share/PHASE16_AUDIT_SNAPSHOT.json`

No purge or classification steps may begin unless this check passes cleanly.

#### Audit Steps

1. Run `pmagent kb registry --all` to snapshot current registry
2. Run `pmagent repo introspect` to identify active code paths
3. Export current embeddings count
4. Git status check - ensure clean working tree

**Evidence:** `share/PHASE16_AUDIT_SNAPSHOT.json`

---

### Phase 16.2: Classify Files

For each file in repo:

1. Check if in KB registry with `enabled=true` → **KEEP**
2. Check if in infra whitelist → **KEEP**
3. Check if active import path → **KEEP**
4. Check if referenced by SSOT docs → **KEEP**
5. Otherwise → candidate for **MOVE** or **DELETE**

**Evidence:** `share/PHASE16_CLASSIFICATION_REPORT.json`

---

### Phase 16.3: Execute Purge

1. Create feature branch: `feat/phase16-legacy-purge`
2. Execute MOVE operations (to `archive/`)
3. Execute DELETE operations
4. Update `.gitignore` if needed
5. Commit with message: `Phase 16: Legacy purge (KEEP=N, MOVE=M, DELETE=D)`

**Evidence:** Git commit hash + diff summary

#### Execution Notes (2025-12-03)

**Status:** ✅ COMPLETE

**Actual Results:**
- **Deleted:** 2,654 files from `archive/` (legacy evidence, reports, cleanup artifacts)
- **Moved:** 281 files to `archive/phase16_legacy/` (preserved for safekeeping)
- **Untouched:** 5,237 files (KEEP: 61 SSOT docs + UNCLASSIFIED: 5,176 files)

**Execution Details:**
- Timestamp: `2025-12-03T23:42:14.108308Z`
- Commit: `phase16: execute legacy purge (archive only)`
- Audit Log: `share/PHASE16_PURGE_EXECUTION_LOG.json`

**Safety Verification:**
- ✅ All deletions restricted to `archive/` and `logs/` directories
- ✅ No SSOT docs touched
- ✅ No active code paths (`pmagent/`, `scripts/`, `webui/`, `src/`, `tests/`) affected
- ✅ All moved files preserved in `archive/phase16_legacy/` with original structure

**Policy Applied:**
- DELETE: Files classified as DELETE + in `archive/` directory
- MOVE: Files classified as MOVE + in `{archive, logs}` directories  
- KEEP/UNCLASSIFIED: Completely untouched

---

### Phase 16.4: DB Reconciliation

**Status:** ✅ COMPLETE

1. Run DB reconciliation script (per section 4.4)
2. Mark stale registry entries `enabled=false`
3. Remove dead embeddings
4. Generate reconciliation report

**Evidence:** `share/PHASE16_DB_RECON_REPORT.json`

#### Reconciliation Results (2025-12-04)

**Analysis:**
- Reviewed all KB/DMS registry entries against purge log
- Checked 2,654 deleted files + 281 moved files
- **Result:** ✅ Zero registry entries referenced purged files

**Actions Taken:**
- Registry updates: 0 (not needed)
- Embedding cleanups: 0 (not needed)
- Hint regenerations: 0 (not needed)

**Conclusion:**
All purged files were legacy artifacts outside the governance surface. The KB/DMS registry was already clean and required no reconciliation.





---

### Phase 16.5: Verification

1. Run `make reality.green` - must pass
2. Run `pmagent kb registry --enabled` - verify all paths exist
3. Run `make housekeeping` - verify no errors
4. Review purge summary metrics

**Evidence:** All make targets pass + summary JSON

---

## 6. Purge Summary & Metrics Requirement

Upon completing the legacy purge, the system must generate:

`share/PHASE16_LEGACY_PURGE_SUMMARY.json`

Containing:
- Count of KEEP files
- Count of MOVE files
- Count of DELETE/ARCHIVE files
- Registry entries disabled or removed
- Embeddings count before and after purge
- Git commit hash
- Timestamp of purge

This summary acts as a human-visible assurance that the cleanup executed correctly and that no excessive deletion occurred.

---

## 7. Rollback Plan

If verification fails:

1. `git reset --hard origin/main` (discard branch)
2. Restore DB snapshot if reconciliation corrupted state
3. Re-run audit to understand failure
4. File incident report in `docs/incidents/`

---

## 8. Success Criteria

- [ ] `make reality.green` passes
- [ ] All `enabled=true` docs exist on filesystem
- [ ] No dead embeddings in DB
- [ ] Purge summary shows reasonable metrics (not 0, not 90% deleted)
- [ ] PM review approves the changes

---

## 9. Next Steps After Phase 16

Once legacy purge is complete and verified:

1. Unblock Phase 4 correlation work
2. Proceed to Phase 8/10 temporal analytics
3. Begin Phase 15 Wave-2 RAG improvements

---

**End of Phase 16 Legacy Purge Plan**
