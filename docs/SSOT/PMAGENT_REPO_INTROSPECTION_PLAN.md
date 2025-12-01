# PMAGENT Repo Introspection Subsystem — SSOT Planning Document

**Status:** Planning (v0.2)  
**Canonical Path:** `docs/SSOT/PMAGENT_REPO_INTROSPECTION_PLAN.md`  
**Owner:** PM  

---

## 1. Mission

Provide a deterministic, DMS-backed, governance-enforced system for:

- Scanning the repository
- Reconciling repo files with the DMS and Layer 4 code ingestion
- Generating semantic inventories
- Identifying integration islands (e.g., `webui/`, `ui/`, `genai-toolbox/`)
- Identifying quarantine candidates (e.g., `archive/`, `logs/`)
- Formalizing repo hygiene and feature-reunion workflows

This subsystem must:

- Be reproducible (via `pmagent`)
- Be grounded in DMS + Layer 4 data
- Integrate with existing pmagent capabilities
- Feed the Feature Reunion Backlog and planning lanes
- Plug into the Reality Green posture

No code is implemented by this doc; it defines the target behavior.

---

## 2. Command Suite (v1)

### 2.1 `pmagent repo semantic-inventory`

Generates a DMS/Layer-4–aligned semantic inventory of the repository.

**Inputs:**

- Live repo file listing (from `find` or equivalent)
- DMS doc registry (control.doc_registry)
- Layer 4 code fragment classifications (`code_fragments_classified`)
- `.cursorignore` posture

**Outputs:**

- `evidence/repo/repo_semantic_inventory.json`
- `evidence/repo/semantic_inventory_filtered.json`

**Guarantees:**

- Read-only with respect to repo and DMS
- Fails if DMS is unavailable
- Fails if `.cursorignore` hides governed paths (via guards)

---

### 2.2 `pmagent repo reunion-plan`

Produces an integration + quarantine plan using the semantic inventory.

**Inputs:**

- `evidence/repo/semantic_inventory_filtered.json`
- DMS posture (control.* tables)
- Feature Reunion Backlog (`docs/SSOT/FEATURE_REUNION_BACKLOG.md`)

**Outputs:**

- `evidence/repo/repo_reunion_plan.json`
- Optional export: `share/exports/repo/reunion_plan.json`

**Guarantees:**

- Read-only
- Uses SSOT policy (Repo Deprecation Policy + Feature Reunion Backlog)
- No file moves

---

### 2.3 `pmagent repo quarantine-candidates`

Extracts quarantinable file paths ("quarantine island") from the reunion plan.

**Inputs:**

- `evidence/repo/repo_reunion_plan.json`

**Outputs:**

- `evidence/repo/repo_quarantine_candidates.json`
- Optional export: `share/exports/repo/quarantine_candidates.json`

**Used for:**

- Hygiene PR dry-runs
- Future automated PR generation

---

### 2.4 `pmagent repo classify --update` (Phase 2 / write-back)

Transition from read-only planning to active governance.

**Inputs:**

- `evidence/repo/repo_semantic_inventory.json`
- `evidence/repo/repo_reunion_plan.json`
- DMS connection (STRICT)

**Effects:**

- Writes classification data to DMS extensions (e.g., repo classification tables)
- Updates Feature Reunion Backlog entries (e.g., via a generated patch)
- Optionally updates planning_lane_status

**Constraints:**

- Requires `STRICT_MODE=STRICT`
- Must be disabled in HINT mode
- Must be covered by tests and CI before enabling

---

### 2.5 `pmagent repo guard-check`

Runs repo-related governance guards:

- `.cursorignore` visibility
- DMS/share sync posture
- Semantic inventory sanity (e.g., untracked source file thresholds)
- Quarantine policy enforcement for `archive/` + `logs/`

**Outputs:**

- `evidence/repo/guard_cursorignore.json`
- `evidence/repo/guard_dms_sync.json`
- `evidence/repo/guard_quarantine.json`

Modes:

- HINT: emit warnings, exit 0
- STRICT: fail closed on violations

---

### 2.6 Integration with Existing pmagent / Layer 4 Capabilities

This subsystem must not duplicate existing behavior; it should extend it.

- `pmagent kb`:
  - `repo semantic-inventory` consumes DMS-backed registry data also used by `pmagent kb` flows.
  - `repo classify --update` may extend behaviors currently implemented in `classify_fragments.py`.

- Layer 4 ingestion:
  - `repo semantic-inventory` and `reunion-plan` assume that Layer 4 is complete and up to date
    (code discovery, fragmentation, embedding, and export).

- Reality-check / DMS posture:
  - Repo introspection commands must align with what `reality-check` reports about DMS state.

Future work will make these relationships explicit in implementation (e.g., calling shared helper modules).

---

## 3. JSON Schemas & File Locations (v1)

### 3.1 Canonical Locations

Schemas (planning-level; files to be created when implemented):

- `schemas/repo_semantic_inventory.schema.json`
- `schemas/repo_reunion_plan.schema.json`
- `schemas/repo_quarantine_candidates.schema.json`

Evidence outputs:

- `evidence/repo/repo_semantic_inventory.json`
- `evidence/repo/semantic_inventory_filtered.json`
- `evidence/repo/repo_reunion_plan.json`
- `evidence/repo/repo_quarantine_candidates.json`

Share exports (if/when needed):

- `share/exports/repo/semantic_inventory.json`
- `share/exports/repo/reunion_plan.json`
- `share/exports/repo/quarantine_candidates.json`

Atlas/control-plane exports (future):

- `share/atlas/control_plane/repo_semantic_inventory.json`
- `share/atlas/control_plane/repo_reunion_plan.json`

---

### 3.2 `repo_semantic_inventory` Schema (conceptual)

Canonical ID: `gemantria://v1/repo_semantic_inventory`  
Schema file: `schemas/repo_semantic_inventory.schema.json`

High-level structure:

- `summary` (object)
  - `total_repo_files` (integer)
  - `dms_tracked_files` (integer)
  - `layer4_tracked_files` (integer)
  - `core_files_count` (integer)
  - `untracked_files_count_raw` (integer)
  - `untracked_source_files_count_filtered` (integer)
- `core_files` (array of strings: repo paths)
- `untracked_source_files` (array of strings: repo paths)
- `ignored_files_count` (integer)

Schema must be a proper JSON Schema draft (e.g., draft-07) and validated by existing schema guards.

---

### 3.3 `repo_reunion_plan` Schema (conceptual)

Canonical ID: `gemantria://v1/repo_reunion_plan`  
Schema file: `schemas/repo_reunion_plan.schema.json`

High-level structure:

- `summary` (object) mirroring `repo_semantic_inventory` summary
- `dir_labels` (object) keyed by top-level directory
  - each value has:
    - `label` (string: `integration_candidate`, `quarantine_candidate`, `investigate`, `external`)
    - `untracked_source_count` (integer)
- `files` (object)
  - `integration_candidates` (array of strings)
  - `quarantine_candidates` (array of strings)
  - `external` (array of strings)
  - `investigate` (array of strings)
- `notes` (array of strings)

---

### 3.4 `repo_quarantine_candidates` Schema (conceptual)

Canonical ID: `gemantria://v1/repo_quarantine_candidates`  
Schema file: `schemas/repo_quarantine_candidates.schema.json`

High-level structure:

- `quarantine_candidates` (array of strings: repo paths)

---

## 4. Output Locations & Conventions

- Evidence files (`evidence/repo/*`) are for PM/OPS and CI.
- Share exports (`share/exports/repo/*`) are for UI, dashboards, or external tooling.
- Atlas/control-plane exports (`share/atlas/control_plane/*`) are for observability dashboards.
- All paths must respect existing naming conventions and schema governance (including schema naming guards).

---

## 5. Governance Integration

### 5.1 Rules 050 / 051 / 052

- All repo introspection commands operate under these rules:
  - Evidence-first
  - DMS-first
  - Fail-closed on governance violations in STRICT mode

### 5.2 Reality Green Integration

- `make reality.green` MUST run `make guard.repo.all` in HINT mode:
  - Ensures repo introspection is at least checked on the happy path.
- CI/tag pipelines MUST run `STRICT_MODE=STRICT make guard.repo.all`:
  - Ensures no quarantinable files sneak back into live areas.
  - Ensures `.cursorignore` remains valid.
  - Ensures DMS/share posture is consistent.

---

## 6. Guard Specifications

### 6.1 Guard Scripts (planned names)

- `scripts/guards/guard_repo_cursorignore.py`
  - Verifies `.cursorignore` does not hide governed paths (e.g., `share/**`).
  - Output: `evidence/repo/guard_cursorignore.json`.

- `scripts/guards/guard_repo_dms_sync.py`
  - Verifies DMS/share sync posture (e.g., `doc_registry` vs share manifests/exports).
  - Output: `evidence/repo/guard_dms_sync.json`.

- `scripts/guards/guard_repo_quarantine.py`
  - Verifies that known quarantine islands (`archive/`, `logs/`) are either:
    - properly quarantined (moved), or
    - explicitly allowed with SSOT exceptions.
  - Output: `evidence/repo/guard_quarantine.json`.

### 6.2 Make Targets

Planned:

- `guard.repo.all` — run all repo-related guards
- `guard.repo.cursorignore`
- `guard.repo.dms.sync`
- `guard.repo.quarantine`

### 6.3 Modes

- HINT mode:
  - Guards emit warnings and exit 0.
  - Used in local dev and reality.green.
- STRICT mode:
  - Guards fail on violations (non-zero exit).
  - Used in tag builds and enforced CI lanes.

---

## 7. Execution Workflow

### 7.1 Phase 1 — Read-Only Introspection

Typical sequence:

```bash
# Step 1: Generate semantic inventory
pmagent repo semantic-inventory \
  > share/exports/repo/semantic_inventory.json

# Step 2: Generate reunion plan
pmagent repo reunion-plan \
  > share/exports/repo/reunion_plan.json

# Step 3: Extract quarantine candidates
pmagent repo quarantine-candidates \
  > share/exports/repo/quarantine_candidates.json

# Step 4: Run repo-related guards
make guard.repo.all
```

### 7.2 Phase 2 — Write-Back (Future)

```bash
# Requires STRICT_MODE=STRICT
STRICT_MODE=STRICT pmagent repo classify --update

# Verify DMS updates / registry posture
pmagent kb registry list --owning-subsystem=<project>
```

Dependencies:

- Layer 4 ingestion complete and green.
- DMS online and reachable.
- Schema files present and validated.
- `.cursorignore` valid and enforced via guards.

---

## 8. Feature Reunion Backlog Integration

This subsystem must interoperate with:

- `docs/SSOT/FEATURE_REUNION_BACKLOG.md`
- Repo Deprecation Policy SSOT

Specifically:

- `repo_reunion_plan.json` provides machine-readable data to:
  - Populate or update Feature Reunion Backlog entries.
  - Identify integration islands (e.g., `webui/`, `ui/`, `genai-toolbox/`).
  - Identify quarantine islands (e.g., `archive/`, `logs/`).

A future extension may include:

- A `pmagent repo reunion-plan --update-backlog` mode that generates a proposed patch for `FEATURE_REUNION_BACKLOG.md` rather than editing it directly.

---

## 9. Test Vectors

Test vectors for this subsystem should follow existing TV conventions.

Planned TVs:

- **TV-REPO-01**: Semantic inventory on a clean repo
  - Expectation: `untracked_source_files_count_filtered == 0`.

- **TV-REPO-02**: Semantic inventory with synthetic orphan files
  - Expectation: `untracked_source_files_count_filtered > 0`.

- **TV-REPO-03**: Reunion plan on a repo with `webui/`, `ui/`, `genai-toolbox/`
  - Expectation: these dirs labeled `integration_candidate`.

- **TV-REPO-04**: Reunion plan on a repo with `archive/` and `logs/`
  - Expectation: these dirs labeled `quarantine_candidate` and files listed accordingly.

- **TV-REPO-05**: Guard check with valid `.cursorignore`
  - Expectation: `guard_repo_cursorignore` passes in STRICT mode.

- **TV-REPO-06**: Guard check with `.cursorignore` hiding `share/**`
  - Expectation: `guard_repo_cursorignore` fails in STRICT mode and emits clear evidence.

Additional TVs can be added as the implementation matures.

---

## 10. Future Extensions

Potential future enhancements:

- Atlas dashboards for repo health and reunion progress
- Historical snapshots of repo classifications in DMS
- Automated hygiene PR generators based on `repo_quarantine_candidates.json`
- Integration island status pages in the Web UI
- Integration with Phase 15 API Gateway and later phases
