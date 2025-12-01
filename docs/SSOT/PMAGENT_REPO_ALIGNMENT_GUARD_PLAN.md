# PMAGENT Repo Alignment Guard — SSOT Planning Document

**Status:** Planning (v0.1)  
**Canonical Path:** `docs/SSOT/PMAGENT_REPO_ALIGNMENT_GUARD_PLAN.md`  
**Owner:** PM  

---

## 1. Mission

The Repo Alignment Guard enforces **plan vs implementation consistency**.

It compares:

1. **Plan Layer**  
   - Expected code paths/modules defined in  
     `docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md`

2. **Reality Layer**  
   - Actual code paths from:  
     - `evidence/repo/repo_semantic_inventory.json`  
     - `evidence/repo/repo_reunion_plan.json`

3. **Alignment Layer**  
   - This guard reconciles the two and produces drift evidence.

This subsystem eliminates "silent drift" such as Layer-4 code landing in  
`scripts/code_ingest/` instead of `scripts/governance/` as originally planned.

No code is implemented by this doc; it defines target behavior.

---

## 2. Inputs

### 2.1 Plan Inputs
- `docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md`  
  Extracts:
  - expected code paths
  - expected module names
  - expected integration points

### 2.2 Reality Inputs
- `evidence/repo/repo_semantic_inventory.json`
- `evidence/repo/repo_reunion_plan.json`

Extracts:
- actual code paths
- integration islands
- quarantine islands

### 2.3 Optional
- Additional plan docs (future phases)

---

## 3. Outputs

### 3.1 Evidence File
`evidence/repo/guard_layer4_alignment.json`

### 3.2 Schema (conceptual)
- `expected_paths` (array of strings)
- `actual_paths` (array of strings)
- `missing_expected_paths` (array of strings)
- `unexpected_locations` (array of strings)
- `integration_island_for_layer4` (string)
- `status` ("pass" | "fail")
- `recommended_backlog_updates` (array of strings)

Schema will be formalized separately.

---

## 4. Guard Behavior

### HINT Mode
- Emits warnings only
- Never blocks execution
- Used in `make reality.green`

### STRICT Mode
- Fails closed if:
  - any expected path is missing
  - any unexpected implementation path exists
  - any unresolved mismatch remains

Used in CI, tag lanes, and manual strict checks.

---

## 5. Detection Logic

### 5.1 Extract Expected Code Paths
Parse `LAYER4_CODE_INGESTION_PLAN.md` for:

- Required modules
- Required scripts
- Required functions
- Required locations (e.g., `scripts/governance/*.py`)

### 5.2 Extract Actual Code Paths
From semantic inventory:

- All repo paths
- Classification tags
- Integration islands

### 5.3 Compare Expected vs Actual
Produce deltas:

- `missing_expected_paths`
- `unexpected_locations`
- whether Layer-4 implementation lives in:
  - expected locations  
  - integration island  
  - quarantinable areas

### 5.4 Emit Evidence
Create full JSON output showing exact mismatches.

---

## 6. Integration with Repo Introspection Subsystem

This guard is an extension of:

- `pmagent repo semantic-inventory`
- `pmagent repo reunion-plan`

It requires those commands to run first.

---

## 7. Execution Workflow

### Step 1 — Generate plan layer
No CLI; plan comes from SSOT.

### Step 2 — Generate reality layer
```bash
pmagent repo semantic-inventory
pmagent repo reunion-plan
```

### Step 3 — Run alignment guard
```bash
make guard.repo.alignment
```

### Expected outputs:
- `evidence/repo/guard_layer4_alignment.json`

---

## 8. Make Targets (planned)

- `guard.repo.alignment`  
  Runs only this guard  
  (STRICT/HINT depending on environment)

- `guard.repo.all`  
  Includes alignment guard

---

## 9. Test Vectors (TVs)

- **TV-REPO-07**  
  Plan expects X, repo contains X → PASS

- **TV-REPO-08**  
  Plan expects X, repo contains Y → FAIL

- **TV-REPO-09**  
  Plan expects files under scripts/governance, reality under scripts/code_ingest → FAIL  
  (Layer 4 canonical test)

- **TV-REPO-10**  
  Plan changed but not applied → FAIL

---

## 10. Future Extensions

- Multi-layer plan alignment (Layers 3–6)
- Cross-language alignment (Python+TS)
- Integration with planning_lane_status
- Dashboard visualization in Atlas
