# REALITY_GREEN_SUMMARY

**Generated**: 2025-12-08T16:47:35.208830+00:00
**Source**: `REALITY_GREEN_SUMMARY.json`

---

- **reality_green**: `true`
- **checks**:
  1. Item:
    - **name**: `DB Health`
    - **passed**: `true`
    - **message**: `DB is reachable and healthy`
    - **details**:
      - **output**: `OK: DB reachable and base tables present.`
  2. Item:
    - **name**: `Control-Plane Health`
    - **passed**: `true`
    - **message**: `Control plane is healthy`
    - **details**:
      - **output**:

```
HINT: MV refresh failed: field name must not be null
CONTEXT:  SQL statement "REFRESH MATERIALIZED VIEW control.mv_compliance_30d"
PL/pgSQL function control.refresh_compliance(text) line 6 at SQL statement
```

  3. Item:
    - **name**: `AGENTS.md Sync`
    - **passed**: `true`
    - **message**: `All AGENTS.md files are in sync`
    - **details**:
      - **output**: ``
  4. Item:
    - **name**: `Share Sync & Exports`
    - **passed**: `true`
    - **message**: `All required exports present`
    - **details**:
  5. Item:
    - **name**: `Ledger Verification`
    - **passed**: `true`
    - **message**: `All 9 tracked artifacts are current`
    - **details**:
      - **summary**:
        - **ok**: `true`
        - **total**: `9`
        - **current**: `9`
        - **stale**:
        - **missing**:
        - **results**:
          1. Item:
            - **name**: `AGENTS.md`
            - **source_of_truth**: `root`
            - **status**: `current`
            - **ledger_hash**: `f6fee1d9b4bac96c...`
            - **current_hash**: `f6fee1d9b4bac96c...`
          2. Item:
            - **name**: `MASTER_PLAN.md`
            - **source_of_truth**: `docs/SSOT`
            - **status**: `current`
            - **ledger_hash**: `7267134e5e14bb7d...`
            - **current_hash**: `7267134e5e14bb7d...`
          3. Item:
            - **name**: `DB_HEALTH.md`
            - **source_of_truth**: `docs/runbooks`
            - **status**: `current`
            - **ledger_hash**: `7b351351aaaf7321...`
            - **current_hash**: `7b351351aaaf7321...`
          4. Item:
            - **name**: `PM_SNAPSHOT_CURRENT.md`
            - **source_of_truth**: `docs/runbooks`
            - **status**: `current`
            - **ledger_hash**: `6c51be1d31e4250e...`
            - **current_hash**: `6c51be1d31e4250e...`
          5. Item:
            - **name**: `RULES_INDEX.md`
            - **source_of_truth**: `root`
            - **status**: `current`
            - **ledger_hash**: `df01a6ca8e43a79b...`
            - **current_hash**: `df01a6ca8e43a79b...`
          6. Item:
            - **name**: `system_health.json`
            - **source_of_truth**: `share/atlas/control_plane`
            - **status**: `current`
            - **ledger_hash**: `9c634ea5601204f4...`
            - **current_hash**: `9c634ea5601204f4...`
          7. Item:
            - **name**: `lm_indicator.json`
            - **source_of_truth**: `share/atlas/control_plane`
            - **status**: `current`
            - **ledger_hash**: `0c8d7f9de6b933f5...`
            - **current_hash**: `0c8d7f9de6b933f5...`
          8. Item:
            - **name**: `canonical.json`
            - **source_of_truth**: `share/exports/docs-control`
            - **status**: `current`
            - **ledger_hash**: `c7ca48f2888fb60a...`
            - **current_hash**: `c7ca48f2888fb60a...`
          9. Item:
            - **name**: `summary.json`
            - **source_of_truth**: `share/exports/docs-control`
            - **status**: `current`
            - **ledger_hash**: `fd4f7625bcefe9fb...`
            - **current_hash**: `fd4f7625bcefe9fb...`
  6. Item:
    - **name**: `Ketiv-Primary Policy`
    - **passed**: `true`
    - **message**: `Ketiv-primary policy enforced (gematria uses written form per ADR-002)`
    - **details**:
      - **output**:

```
✅ Ketiv-primary guard: PASS (4399/4399 nodes)

```

  7. Item:
    - **name**: `DMS Hint Registry`
    - **passed**: `true`
    - **message**: `DMS hint registry accessible with 4 REQUIRED hints across 2 flow(s)`
    - **details**:
      - **total_hints**: `4`
      - **flows_with_hints**: `2`
  8. Item:
    - **name**: `Repo Alignment (Layer 4)`
    - **passed**: `true`
    - **message**: `Plan vs implementation drift detected (HINT mode: warnings only)`
    - **details**:
      - **output**:

```
Layer 4 Alignment Guard: FAIL
  Expected paths: 7
  Actual paths: 4
  Missing: 0
  Integration islands: 2
\nViolations detected:
  - Found 2 files in scripts/code_ingest/ (plan expected scripts/governance/)
  - Update LAYER4_CODE_INGESTION_PLAN.md or migrate code to planned locations
\nEvidence: evidence/repo/guard_layer4_alignment.json
\n⚠️  HINT MODE: Warnings only (exit 0)

```

      - **note**: `Run with --strict to enforce`
  9. Item:
    - **name**: `DMS Alignment`
    - **passed**: `true`
    - **message**: `pmagent control-plane DMS and Share are aligned`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "dms_share_alignment": "OK",
  "missing_in_share": [],
  "missing_in_dms": [],
  "extra_in_share": []
}
```

  10. Item:
    - **name**: `DMS Metadata`
    - **passed**: `true`
    - **message**: `pmagent control-plane DMS metadata sane (low_enabled=0)`
    - **details**:
      - **distribution**:
        - **critical**: `144`
        - **high**: `262`
        - **medium**: `56`
        - **unknown**: `783`
  11. Item:
    - **name**: `AGENTS–DMS Contract`
    - **passed**: `true`
    - **message**: `All AGENTS.md rows satisfy pmagent control-plane DMS contract`
    - **details**:
      - **rows**: `116`
  12. Item:
    - **name**: `Bootstrap Consistency`
    - **passed**: `true`
    - **message**: `Bootstrap state matches SSOT`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "bootstrap_current_phase": "24",
  "ssot_current_phase": "24",
  "mismatches": []
}
```

  13. Item:
    - **name**: `Root Surface`
    - **passed**: `true`
    - **message**: `No unexpected files in repository root`
    - **details**:
      - **output**: `[root-surface] OK: no unexpected files in repo root`
  14. Item:
    - **name**: `Share Sync Policy`
    - **passed**: `true`
    - **message**: `No unknown or unsafe share/ docs in managed namespaces`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "missing_in_share": [
    "PM_HANDOFF_PROTOCOL.md",
    "SHARE_FOLDER_ANALYSIS.md"
  ],
  "extra_in_share": [],
  "missing_in_dms": []
}
```

  15. Item:
    - **name**: `Backup System`
    - **passed**: `true`
    - **message**: `Recent backup exists and rotation logic is sane`
    - **details**:
  16. Item:
    - **name**: `WebUI Shell Sanity`
    - **passed**: `true`
    - **message**: `WebUI shell files present`
    - **details**:
  17. Item:
    - **name**: `OA State`
    - **passed**: `true`
    - **message**: `OA state is consistent with kernel surfaces`
    - **details**:
      - **output**:

```
✅ OA State Guard: PASS
   OA state is consistent with kernel surfaces

JSON: {"ok": true, "mode": "STRICT", "mismatches": [], "missing_surfaces": []}
```

  18. Item:
    - **name**: `Handoff Kernel`
    - **passed**: `true`
    - **message**: `Handoff kernel is consistent with bootstrap/SSOT/reality.green`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "mismatches": []
}
```

- **timestamp**: `2025-12-08T16:34:47Z`
