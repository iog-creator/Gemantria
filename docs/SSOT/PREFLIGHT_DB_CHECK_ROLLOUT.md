# Pre-Flight DB Check Rollout Plan

## Problem Summary

Agents query DMS without checking DB availability first, leading to:
- Assumptions that `db_off` is acceptable
- Violations of Rule 050 (Evidence-First Protocol)
- Confusing error messages

## Solution Implemented

✅ **Core Infrastructure**:
- `scripts/ops/preflight_db_check.py` - Mandatory pre-flight check
- `scripts/ops/query_dms_phase_status.py` - Reference implementation
- `docs/SSOT/DMS_QUERY_PROTOCOL.md` - Documentation

## Rollout Strategy

### Phase 1: Critical DMS Query Scripts (High Priority)

These scripts query `control.*` tables and should fail-fast if DB is offline:

**Governance & DMS Management**:
- [ ] `scripts/governance/check_dms_work_needed.py` (queries control.doc_fragment, control.doc_registry)
- [ ] `scripts/governance/ingest_doc_content.py` (queries control.doc_registry, control.doc_version)
- [ ] `scripts/governance/seed_hint_registry.py` (inserts into control.hint_registry)
- [ ] `scripts/db/control_mcp_catalog_export.py` (queries control.mcp_tool_catalog)
- [ ] `scripts/db/control_mvs_snapshot.py` (queries control schema)
- [ ] `scripts/db/export_dms_tables.py` (exports control.doc_registry, control.doc_version)

**Share Sync & Bootstrap**:
- [ ] `scripts/sync_share.py` (queries control.doc_registry)
- [ ] `scripts/pm/generate_pm_bootstrap_state.py` (likely queries control.*)

**Document Management & Hints**:
- [ ] `scripts/document_management_hints.py` (queries multiple control.* tables)
- [ ] `scripts/governance_tracker.py` (queries check_governance_freshness, governance_artifacts, hint_emissions)

### Phase 2: Data Export Scripts (Medium Priority)

These query main schema (`concept_network`, `concept_relations`, etc.):

- [ ] `scripts/exports_smoke.py`
- [ ] `scripts/export_noun_index.py`
- [ ] `scripts/analyze_metrics.py`
- [ ] `scripts/verify_data_completeness.py`
- [ ] `scripts/exports/export_graph_core.py`
- [ ] `scripts/export_jsonld.py`
- [ ] `scripts/atlas/atlas_proof_dsn.py`

### Phase 3: Tool-Specific Scripts (Lower Priority)

These are domain-specific and may have different DB posture requirements:

- [ ] `scripts/atlas/gen_filter_apply.py`
- [ ] Other atlas/visualization scripts
- [ ] Other export utilities

## Implementation Pattern

All scripts querying DMS should use this pattern:

```python
#!/usr/bin/env python3
"""Script description."""

import subprocess
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# ✅ PRE-FLIGHT DB CHECK (MANDATORY for DMS queries)
preflight_script = REPO / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run(
    [sys.executable, str(preflight_script), "--mode", "strict"],
    capture_output=True
)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

# Now safe to import and use DB modules
from scripts.config.env import get_rw_dsn
import psycopg
```

## Enforcement

### Makefile Integration

Add pre-flight checks to key targets:

```makefile
share.sync:
    @python scripts/ops/preflight_db_check.py --mode strict
    @python scripts/sync_share.py

housekeeping:
    @python scripts/ops/preflight_db_check.py --mode strict
    # ... rest of housekeeping

mcp.ingest:
    @python scripts/ops/preflight_db_check.py --mode strict
    # ... rest of mcp.ingest
```

### Guard Integration

Update `scripts/guards/guard_reality_green.py` to check if pre-flight pattern is used in DMS query scripts.

## Next Steps

1. **Immediate**: Add pre-flight to Phase 1 scripts (highest impact)
2. **Short-term**: Add pre-flight to Phase 2 scripts
3. **Medium-term**: Add Makefile integration
4. **Long-term**: Create guard to detect DMS queries without pre-flight

## Success Criteria

- ✅ No more assumptions about `db_off` mode
- ✅ Clear error messages when DB is required but offline
- ✅ Evidence-first protocol (Rule 050) enforced automatically
- ✅ Reduced troubleshooting time

## Related

- `docs/SSOT/DMS_QUERY_PROTOCOL.md` - Full protocol documentation
- `docs/hints/HINT-DB-002-postgres-not-running.md` - DB offline fix
- `.cursor/rules/050-ops-contract.mdc` - Evidence-First Protocol
- `docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md` - DSN requirements
