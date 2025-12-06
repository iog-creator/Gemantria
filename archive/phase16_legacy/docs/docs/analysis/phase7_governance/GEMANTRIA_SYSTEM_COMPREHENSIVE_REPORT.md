# Gemantria System — Comprehensive Implementation Report
## Phase-7 Governance Reconstruction Context

> **Generated**: 2025-11-16  
> **Branch**: feat/phase7.governance.rebuild.20251116-085215  
> **Purpose**: Single authoritative document for GPT to understand what exists and complete Phase-7 governance reconstruction
> **Scope**: Full system audit showing existing infrastructure vs what needs to be done

---

# EXECUTIVE SUMMARY

The Gemantria system is a **mature, production-ready gematria analysis pipeline** with:

- ✅ **Core Pipeline (Phases 0-5)**: 100% complete and operational
- ✅ **Phase-7F/7G**: Local LM architecture, status introspection, UI/TVs complete  
- ⚠️ **Phase-6**: 60% complete (knowledge/LM wiring partial)
- 🚧 **Phase-7 Governance**: Infrastructure exists, needs DB-backed SSOT migration

**CRITICAL INSIGHT FOR GPT**: 

**What you're asking for ALREADY EXISTS** — the Phase-7 governance reconstruction is about **integrating existing pieces**, not building from scratch.

**Gap**: Rules live only in `.cursor/rules/*.mdc` (69 files). Need to:
1. Add 3 DB tables to store rule definitions
2. Write 1 ingestion script to populate those tables
3. Write 1 guard script to validate sync
4. Run once + verify

**Estimated Effort**: 1 PR, 4-6 hours of focused work

---

# 1. EXISTING INFRASTRUCTURE (WHAT'S ALREADY BUILT)

## 1.1 Control-Plane Schema (Migration 040 — COMPLETE ✅)

**Location**: `migrations/040_control_plane_schema.sql`

**Tables Implemented**:
- `control.tool_catalog` — Tool registry with rings, IO schemas, enable flags
- `control.capability_rule` — Capability rules with allowlist/denylist/budgets  
- `control.doc_fragment` — Document fragments for proof-of-rewrite (PoR)
- `control.capability_session` — Capability sessions with task_id tracking
- `control.agent_run` — Agent runs with violations, evidence URIs, quarantine flags

**Materialized Views** (Compliance):
- `control.mv_compliance_7d` — 7-day compliance window
- `control.mv_compliance_30d` — 30-day compliance window
- Functions: `control.refresh_compliance(window TEXT)`

**Verification**:
```bash
pmagent control tables  # Shows all control-plane tables
pmagent control schema  # Shows DDL for control-plane
```

**Status**: ✅ **COMPLETE** — Schema is deployed and operational (verified via `pmagent control` commands)

---

## 1.2 AI Tracking Tables (Migrations 015 & 016 — COMPLETE ✅)

**Location**: 
- `migrations/015_create_governance_tracking.sql`
- `migrations/016_create_ai_learning_tracking.sql`

**Tables Implemented**:
- `public.ai_interactions` — AI-user interactions, tool usage, context tracking
- `public.governance_artifacts` — Artifact tracking (rules, agents, hints, metadata)
- `public.hint_emissions` — Hint emissions during runtime  
- `public.governance_compliance_log` — Compliance check history
- `public.tool_usage_analytics` — Tool performance and effectiveness
- `public.code_generation_events` — Code generation outcomes
- `public.user_feedback` — User satisfaction tracking

**Functions Implemented**:
- `update_governance_artifact()` — Upsert governance artifacts
- `log_hint_emission()` — Log hint emissions
- `check_governance_freshness()` — Check if governance is stale

**3-Role DB Contract** (OPS v6.2.3):
- **Extraction DB**: `GEMATRIA_DSN` → database `gematria`  
- **SSOT DB**: `BIBLE_DB_DSN` → database `bible_db` (read-only)  
- **AI Tracking**: Lives in `gematria` DB, `public` schema; `AI_AUTOMATION_DSN` **must equal** `GEMATRIA_DSN`

**Guards**:
- `guard.ai.tracking` — Validates tables in `public.ai_interactions`, `public.governance_artifacts`
- `guard.rules.alwaysapply.dbmirror` — Validates Always-Apply Triad (Rules 050/051/052)

**Status**: ✅ **COMPLETE** — Schema is deployed and operational

---

## 1.3 MCP Knowledge Catalog (RFC-078, Migration 078 — COMPLETE ✅)

**Location**: 
- `db/sql/078_mcp_knowledge.sql`
- `migrations/041_control_mcp_catalog_view.sql`

**Schema Implemented**:
- `mcp.tools` — Tool catalog with desc, tags, cost_est, visibility
- `mcp.endpoints` — HTTP/tool endpoints (path, method, auth, notes)
- `mcp.logs` — Optional logs (RW in dev; OMIT in STRICT RO lanes)
- `mcp.v_catalog` — Read-only view (tag-proof friendly)

**Guards**: 
- `guard_mcp_catalog_strict.py` — Validates schema, counts, "no write verbs" invariant
- `guard.mcp.db.ro` — STRICT RO proof for tags (requires `STRICT_DB_PROBE=1`)

**Exports**:
- `share/atlas/control_plane/mcp_catalog.json`
- `share/atlas/control_plane/capability_rules.json`
- `share/atlas/control_plane/agent_runs_7d.json`

**Makefile Targets**:
```bash
make mcp.catalog.export       # Export MCP catalog
make mcp.catalog.validate     # Validate MCP catalog structure
make guard.mcp.catalog.strict # Validate catalog (STRICT mode)
```

**Status**: ✅ **COMPLETE** — Schema is deployed, exports working, guards operational

---

## 1.4 Compliance Exports (Phase-3C — COMPLETE ✅)

**Location**: 
- `agentpm/control_plane/exports.py`
- `scripts/db/control_compliance_exports.py`

**Exports Implemented**:
- `share/atlas/control_plane/compliance.head.json` — Overall compliance summary
- `share/atlas/control_plane/top_violations_7d.json` — Top violations (7-day window)
- `share/atlas/control_plane/top_violations_30d.json` — Top violations (30-day window)

**Guards**:
- `guard_control_compliance_exports.py` — Validates export structure and presence

**Functions**:
- `export_compliance_head()` — Export HEAD summary from both windows
- `export_top_violations(window)` — Export top violations for 7d/30d
- `write_compliance_exports(output_dir, strict_mode)` — Write all exports with HINT/STRICT posture

**Hermetic Behavior** (Rule-046):
- All exports tolerate `db_off` mode
- Return structured JSON with `ok`, `mode`, `reason` fields
- No crashes when DB unavailable

**Makefile Targets**:
```bash
make atlas.control.exports    # Export compliance data
make guard.control.compliance # Validate compliance exports
```

**Status**: ✅ **COMPLETE** — Exports working, hermetic fallbacks implemented

---

## 1.5 PMAgent Control Commands (Phase-3B — COMPLETE ✅)

**Location**: `pmagent/cli.py`, `scripts/control/*.py`

**Commands Implemented**:
- `pmagent control status` — DB status + table row counts
- `pmagent control tables` — Schema-qualified table list with row counts
- `pmagent control schema` — DDL introspection for control-plane tables
- `pmagent control pipeline-status` — Recent pipeline runs summary
- `pmagent control summary` — Aggregated control-plane posture

**Hermetic Behavior** (Rule-046):
- All commands tolerate `db_off` mode (driver missing / connection failed)
- Return structured JSON with `ok`, `mode`, `reason` fields
- No crashes when DB unavailable

**Example Outputs**:
```json
{
  "ok": false,
  "mode": "db_off",
  "reason": "connection_failed: could not connect to server",
  "tables": []
}
```

**Runbooks**:
- `docs/runbooks/CONTROL_STATUS.md` — Command usage guide
- `docs/runbooks/CONTROL_SCHEMA.md` — Schema introspection guide
- `docs/runbooks/CONTROL_TABLES.md` — Table inventory guide
- `docs/runbooks/CONTROL_PIPELINE_STATUS.md` — Pipeline status guide

**Status**: ✅ **COMPLETE** — All commands implemented and tested

---

## 1.6 DSN Centralization (SSOT — COMPLETE ✅)

**Location**: `scripts/config/env.py` (canonical SSOT)

**Loaders Implemented**:
```python
# RW DSN (write-enabled)
def get_rw_dsn():
    # GEMATRIA_DSN → RW_DSN → AI_AUTOMATION_DSN → ATLAS_DSN_RW → ATLAS_DSN
    pass

# RO DSN (read-only)
def get_ro_dsn():
    # GEMATRIA_RO_DSN | ATLAS_DSN_RO (peers) → ATLAS_DSN → (fallback) RW
    pass

# Bible DB DSN (read-only)
def get_bible_db_dsn():
    # BIBLE_DB_DSN → BIBLE_RO_DSN → RO_DSN → ATLAS_DSN_RO → ATLAS_DSN
    pass
```

**DSN Precedence** (documented in AGENTS.md):
- **RW DSN**: `GEMATRIA_DSN` → `RW_DSN` → `AI_AUTOMATION_DSN` → `ATLAS_DSN_RW` → `ATLAS_DSN`
- **RO DSN**: `GEMATRIA_RO_DSN` | `ATLAS_DSN_RO` (peers) → `ATLAS_DSN` → (fallback to RW)
- **Bible DB DSN**: `BIBLE_RO_DSN` → `RO_DSN` → `ATLAS_DSN_RO` → `ATLAS_DSN` (also checks `BIBLE_DB_DSN` directly)

**Contract**:
- ❌ **FORBIDDEN**: `os.getenv("GEMATRIA_DSN")` direct access
- ✅ **REQUIRED**: Always use centralized loaders from `scripts.config.env`

**Guard**:
- `guard_dsn_centralized.sh` — Validates no direct `os.getenv()` calls
- `make guard.dsn.centralized` — HINT mode
- `make guard.dsn.centralized.strict` — STRICT mode (fail-closed)

**Makefile Target**:
```bash
make dsns.echo  # Print redacted DSNs (never prints secrets)
```

**Status**: ✅ **COMPLETE** — Centralized loaders operational, contract enforced

---

## 1.7 Guards System (60+ Guards — COMPLETE ✅)

**Location**: `scripts/guards/`

**Key Guards Implemented**:

### Governance Guards:
- `guard_ai_tracking_contract.py` — AI tracking in gematria DB (Rule-064)
- `guard_alwaysapply_dbmirror.py` — Always-Apply Triad DB mirror (Rules 050/051/052)
- `guard_control_compliance_exports.py` — Compliance export structure
- `guard_control_knowledge_mcp_exports.py` — MCP knowledge exports
- `guard_docs_consistency.py` — Doc consistency patterns
- `guard_db_health.py` — DB health posture (ready/db_off/partial)
- `guard_lm_health.py` — LM Studio health posture (lm_ready/lm_off)

### Schema Guards:
- `guard_exports_json.py` — Export JSON structure validation
- `guard_exports_rfc3339.py` — RFC3339 timestamp validation
- `guard_schema_smoke.py` — Schema smoke tests
- `guard_schema_contract.py` — Schema contract enforcement

### DSN Guards:
- `guard_dsn_centralized.sh` — DSN centralization enforcement

### Rules Guards:
- `rules_guard.py` — Rules numbering, status, and structure validation

**Posture Modes**:
- **HINT mode**: Tolerant, warns only (default on PRs)
- **STRICT mode**: Fail-closed (tags, releases)

**Makefile Targets**:
```bash
make guards.all              # Run all guards (HINT mode)
make guards.strict           # Run all guards (STRICT mode)
make guard.dsn.centralized   # DSN centralization (HINT)
make guard.db.health         # DB health (HINT)
make guard.lm.health         # LM health (HINT)
```

**Status**: ✅ **COMPLETE** — Guard system operational, 60+ guards implemented

---

## 1.8 Phase-7F/7G Implementation (COMPLETE ✅)

**Phase-7F Features** ✅:
- Per-slot provider configuration (local_agent, embedding, reranker, theology)
- Provider routing via env vars (`INFERENCE_PROVIDER`, `*_PROVIDER`)
- Provider enable/disable flags (`OLLAMA_ENABLED`, `LM_STUDIO_ENABLED`)
- Default models:
  - `granite4:tiny-h` (local_agent)
  - `granite-embedding:278m` (embedding)
  - `bge-reranker-v2-m3:latest` (reranker)
  - `Christian-Bible-Expert-v2.0-12B` (theology)

**Phase-7G Features** ✅:
- `pmagent lm.status` command — LM provider/model introspection
- System status UI: `/api/status/system`, `/status` page
- TVs: `TV-LM-HEALTH-01`, `TV-DB-HEALTH-01`
- Status explanation: `pmagent status.explain` + `/api/status/explain`
- LM insights: `/api/lm/indicator` + `/lm-insights` page
- System dashboard: `/dashboard`
- DB health graph: `/api/db/health_timeline` + `/db-insights`
- BibleScholar UI: `/api/bible/passage` + `/bible`

**Documentation**:
- `docs/PHASE_7F_SUMMARY.md` — Phase-7F summary
- `docs/PHASE_7F_IMPLEMENTATION_SUMMARY.md` — Implementation details
- `docs/PHASE_7F_MODEL_READINESS_CHECKLIST.md` — Model readiness checklist
- `docs/runbooks/OLLAMA_ALTERNATIVE.md` — Ollama provider setup
- `docs/runbooks/LM_STUDIO_SETUP.md` — LM Studio setup

**Status**: ✅ **COMPLETE** — All Phase-7F/7G features implemented and tested

---

## 1.9 Share Directory Sync (Rule-030 — COMPLETE ✅)

**Location**: `scripts/update_share.py`, `scripts/sync_share.py`

**Manifest**: `docs/SSOT/SHARE_MANIFEST.json` (40 items max, currently 32 items)

**Sync Mechanism**:
- Reads manifest for file list and destinations
- Change detection via SHA-256 content comparison
- Preview generation for large exports (>4KB → head_json)
- Flat layout (all files in `share/`, no subdirectories)

**Makefile Target**:
```bash
make share.sync           # Sync all manifest items to share/
make share.manifest.verify # Verify manifest is within limits
make share.check          # Check share/ is clean and current
```

**Housekeeping Integration** (Rule-058):
- `make housekeeping` runs `share.sync` first
- All doc/governance changes trigger automatic sync

**Manifest Items** (excerpt):
- `AGENTS.md` → `share/AGENTS.md`
- `CHANGELOG.md` → `share/CHANGELOG.md`
- `Makefile` → `share/Makefile`
- `docs/SSOT/MASTER_PLAN.md` → `share/MASTER_PLAN.md`
- `docs/SSOT/GPT_REFERENCE_GUIDE.md` → `share/GPT_REFERENCE_GUIDE.md`
- `docs/runbooks/LM_STUDIO_SETUP.md` → `share/LM_STUDIO_SETUP.md`
- `docs/runbooks/DB_HEALTH.md` → `share/DB_HEALTH.md`
- `env_example.txt` → `share/env_example.txt`

**Status**: ✅ **COMPLETE** — Share sync operational, DB tracking optional

---

## 1.10 Housekeeping System (Rule-058 — COMPLETE ✅)

**Location**: `Makefile` (target: `housekeeping`)

**Components**:
```makefile
housekeeping: share.sync adr.housekeeping governance.housekeeping \
              governance.docs.hints docs.hints docs.masterref.populate \
              handoff.update
    # 1. Share sync (Rule-030)
    # 2. ADR housekeeping (format validation)
    # 3. Governance housekeeping (DB + compliance + docs)
    # 4. Governance docs hints (Rule-026 + Rule-065)
    # 5. Document hints (Rule-050 + Rule-061)
    # 6. Master reference population
    # 7. Handoff update
    # 8. Create missing AGENTS.md files (Rule-017, Rule-058)
    # 9. Auto-update AGENTS.md based on code changes
    # 10. Auto-update CHANGELOG.md based on commits
    # 11. Validate AGENTS.md
    # 12. Rules audit
    # 13. Forest generation
    # 14. PM snapshot generation
```

**Scripts**:
- `scripts/sync_share.py` — Share directory sync
- `scripts/governance_housekeeping.py` — Governance updates
- `scripts/governance_docs_hints.py` — Hint emission for doc changes
- `scripts/create_agents_md.py` — Create missing AGENTS.md files
- `scripts/auto_update_agents_md.py` — Auto-update AGENTS.md
- `scripts/auto_update_changelog.py` — Auto-update CHANGELOG.md
- `scripts/validate_agents_md.py` — Validate AGENTS.md structure
- `scripts/rules_audit.py` — Rules numbering/status validation
- `scripts/generate_forest.py` — Generate forest overview
- `scripts/pm_snapshot.py` — Generate PM snapshot

**Mandatory Run** (Rule-058):
- After ANY docs/scripts/rules changes
- Before requesting review
- Failure to run = CI failure

**Status**: ✅ **COMPLETE** — Full housekeeping pipeline operational

---

## 1.11 Cursor Rules System (69 Rules — COMPLETE ✅)

**Location**: `.cursor/rules/` (69 .mdc files + README)

**Rules Structure**:
- **000-068**: Contiguous numbering (no gaps except reserved 047/048)
- **Always-Apply Triad**: Rule-050 (OPS), Rule-051 (CI gating), Rule-052 (tool priority)
- **Status types**: `active`, `deprecated`, `reserved`

**Key Rules**:
- `000-ssot-index.mdc` — SSOT index (deprecated)
- `050-ops-contract.mdc` — OPS contract v6.2.3 (Always-Apply)
- `051-cursor-insight.mdc` — CI gating and handoff (Always-Apply)
- `052-tool-priority.mdc` — Tool priority and context (Always-Apply)
- `058-auto-housekeeping.mdc` — Mandatory housekeeping (Always-Apply)
- `062-environment-validation.mdc` — Venv validation (Always-Apply)
- `063-git-safety.mdc` — Git safety (Always-Apply)

**Rules Inventory** (in AGENTS.md):
```markdown
| # | Title |
|---:|-------|
| 000 | # 000-ssot-index (AlwaysApply) |
| 001 | # --- (db-safety) |
...
| 068 | # --- (gpt-docs-sync) |
```

**Validation**:
- `scripts/rules_audit.py` — Validates numbering, status, structure
- `make rules.audit` — Run rules audit

**Status**: ✅ **COMPLETE** — 69 rules implemented, contiguous numbering verified

---

## 1.12 AGENTS.md Governance (Rule-006 — COMPLETE ✅)

**Root AGENTS.md**: Canonical agent framework documentation

**Scoped AGENTS.md Files**:
- `scripts/AGENTS.md` — Scripts directory documentation
- `agentpm/AGENTS.md` — AgentPM package documentation
- `src/AGENTS.md` — Source code documentation
- (Others created as needed via `scripts/create_agents_md.py`)

**Content Requirements** (Rule-006):
- Directory purpose statement
- API contracts and function signatures
- Behavior documentation for key functions/classes
- Integration points and dependencies

**Auto-Generation**:
- `scripts/create_agents_md.py` — Create missing AGENTS.md files
- `scripts/auto_update_agents_md.py` — Auto-update based on code changes
- `scripts/validate_agents_md.py` — Validate structure and completeness

**Makefile Targets**:
```bash
make agents.md.sync       # Check for stale AGENTS.md files
make agents.md.validate   # Validate AGENTS.md structure
```

**Housekeeping Integration**:
- `make housekeeping` automatically creates missing AGENTS.md files
- Validation runs as part of housekeeping

**Status**: ✅ **COMPLETE** — AGENTS.md governance operational

---

# 2. WHAT'S MISSING (GOVERNANCE SSOT MIGRATION)

## 2.1 Problem Statement

**Current State**:
- ✅ Postgres control-plane schema exists
- ✅ AI tracking tables exist
- ✅ MCP catalog exists
- ✅ Compliance exports exist
- ✅ Guards exist
- ❌ **Rules definitions NOT in DB** — live only in `.cursor/rules/*.mdc`
- ❌ **No DB-driven governance** — `.cursor/rules` is de facto SSOT

**Target State**:
- ✅ Postgres becomes SSOT for governance
- ✅ Rules defined in DB (`control.rule_definition`)
- ✅ `.cursor/rules/*.mdc` generated FROM DB (or sync validated)
- ✅ Guards validate DB SSOT
- ✅ CI lanes enforce SSOT consistency

**Gap Analysis**:

| Component | Exists? | Status |
|-----------|---------|--------|
| Control-plane schema | ✅ | Complete |
| AI tracking tables | ✅ | Complete |
| MCP catalog | ✅ | Complete |
| Compliance exports | ✅ | Complete |
| Rules in `.cursor/rules/` | ✅ | Complete (69 files) |
| **Rules in DB** | ❌ | **Missing** |
| **Ingestion script** | ❌ | **Missing** |
| **DB SSOT guard** | ❌ | **Missing** |

---

## 2.2 What Needs to Be Built (Minimal Scope)

### 2.2.1 New DB Tables (Migration 0XX)

**File**: `migrations/042_governance_rules_ssot.sql`

**Tables to Create**:

#### A. `control.rule_definition`

```sql
CREATE TABLE control.rule_definition (
    rule_id TEXT PRIMARY KEY,           -- "000", "001", ..., "068"
    name TEXT NOT NULL,                 -- "ssot-index", "db-safety", etc.
    status TEXT NOT NULL,               -- "active", "deprecated", "reserved"
    description TEXT,
    severity TEXT NOT NULL,             -- "HINT", "STRICT"
    always_apply BOOLEAN NOT NULL DEFAULT FALSE,
    docs_path TEXT,                     -- ".cursor/rules/000-ssot-index.mdc"
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE control.rule_definition IS 
'Rule definitions SSOT - canonical source for governance rules';

COMMENT ON COLUMN control.rule_definition.rule_id IS 
'Rule identifier (000-068), contiguous numbering enforced';

COMMENT ON COLUMN control.rule_definition.always_apply IS 
'If true, this rule is part of the Always-Apply set (e.g., 050/051/052)';
```

#### B. `control.rule_source`

```sql
CREATE TABLE control.rule_source (
    id SERIAL PRIMARY KEY,
    rule_id TEXT NOT NULL REFERENCES control.rule_definition(rule_id),
    source_type TEXT NOT NULL,          -- "cursor_rules", "rules_index", "agents_md"
    path TEXT NOT NULL,
    content_hash TEXT NOT NULL,         -- SHA-256
    content TEXT,                       -- Full .mdc content (optional)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rule_source_rule_id ON control.rule_source(rule_id);
CREATE INDEX idx_rule_source_type ON control.rule_source(source_type);

COMMENT ON TABLE control.rule_source IS 
'Rule source tracking - maps DB rules to .cursor/rules/*.mdc files';
```

#### C. `control.guard_definition`

```sql
CREATE TABLE control.guard_definition (
    guard_id TEXT PRIMARY KEY,          -- "guard_db_health", etc.
    name TEXT NOT NULL,
    description TEXT,
    rule_ids TEXT[] NOT NULL,           -- Rules this guard enforces
    strict_default BOOLEAN NOT NULL DEFAULT FALSE,
    script_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_guard_rule_ids ON control.guard_definition USING GIN(rule_ids);

COMMENT ON TABLE control.guard_definition IS 
'Guard definitions - maps guards to rules they enforce';
```

**Migration Verification**:
```bash
psql $GEMATRIA_DSN -c "SELECT COUNT(*) FROM control.rule_definition;"
# Expected: 0 (empty until ingestion)

psql $GEMATRIA_DSN -c "SELECT COUNT(*) FROM control.rule_source;"
# Expected: 0 (empty until ingestion)
```

---

### 2.2.2 Ingestion Script

**File**: `scripts/governance/ingest_rules_to_db.py`

**Purpose**: Parse `.cursor/rules/*.mdc` and `RULES_INDEX.md` → populate DB

**Algorithm**:

```python
#!/usr/bin/env python3
"""
ingest_rules_to_db.py — Ingest .cursor/rules/*.mdc → control.rule_definition
"""

import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
import psycopg

from scripts.config.env import get_rw_dsn

ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = ROOT / ".cursor" / "rules"
RULES_INDEX = ROOT / "RULES_INDEX.md"

def parse_rule_file(path: Path) -> dict:
    """
    Parse a .cursor/rules/NNN-name.mdc file.
    Extract:
    - rule_id (from filename)
    - name (from filename or content)
    - status (from content: "DEPRECATED", "reserved", or "active")
    - description (from first header)
    - severity (from content: "STRICT" or "HINT")
    - always_apply (from content: "AlwaysApply" or "Always-Apply")
    - content_hash (SHA-256)
    """
    content = path.read_text()
    
    # Extract rule_id from filename: "NNN-name.mdc"
    match = re.match(r"(\d{3})-(.+)\.mdc", path.name)
    if not match:
        return None
    
    rule_id = match.group(1)
    name_slug = match.group(2)
    
    # Parse content
    status = "active"
    if "DEPRECATED" in content or "deprecated" in content.lower():
        status = "deprecated"
    elif "reserved" in content.lower():
        status = "reserved"
    
    # Extract description (first header line starting with #)
    description = None
    for line in content.split("\n"):
        if line.startswith("# "):
            description = line[2:].strip()
            break
    
    # Determine severity
    severity = "HINT"
    if "STRICT" in content or "strict" in content:
        severity = "STRICT"
    
    # Determine always_apply
    always_apply = False
    if "AlwaysApply" in content or "Always-Apply" in content:
        always_apply = True
    
    # Compute content hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    return {
        "rule_id": rule_id,
        "name": name_slug,
        "status": status,
        "description": description,
        "severity": severity,
        "always_apply": always_apply,
        "docs_path": str(path.relative_to(ROOT)),
        "content_hash": content_hash,
        "content": content
    }

def ingest_rules():
    """Ingest all rules from .cursor/rules/ → DB"""
    dsn = get_rw_dsn()
    if not dsn:
        print("ERROR: No RW DSN available")
        return 1
    
    rules = []
    for mdc_file in sorted(RULES_DIR.glob("*.mdc")):
        if mdc_file.name == "README.md":
            continue
        if mdc_file.suffix == ".tmp":
            continue
        
        rule_data = parse_rule_file(mdc_file)
        if rule_data:
            rules.append(rule_data)
    
    print(f"Parsed {len(rules)} rules from .cursor/rules/")
    
    # Connect to DB and ingest
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Upsert into control.rule_definition
            for rule in rules:
                cur.execute(
                    """
                    INSERT INTO control.rule_definition 
                        (rule_id, name, status, description, severity, always_apply, docs_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (rule_id) 
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        status = EXCLUDED.status,
                        description = EXCLUDED.description,
                        severity = EXCLUDED.severity,
                        always_apply = EXCLUDED.always_apply,
                        docs_path = EXCLUDED.docs_path,
                        updated_at = NOW()
                    """,
                    (
                        rule["rule_id"],
                        rule["name"],
                        rule["status"],
                        rule["description"],
                        rule["severity"],
                        rule["always_apply"],
                        rule["docs_path"]
                    )
                )
                
                # Insert into control.rule_source
                cur.execute(
                    """
                    INSERT INTO control.rule_source
                        (rule_id, source_type, path, content_hash, content)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        rule["rule_id"],
                        "cursor_rules",
                        rule["docs_path"],
                        rule["content_hash"],
                        rule["content"]
                    )
                )
            
            conn.commit()
    
    print(f"✅ Ingested {len(rules)} rules into control.rule_definition")
    return 0

if __name__ == "__main__":
    exit(ingest_rules())
```

**Makefile Target**:
```makefile
.PHONY: governance.ingest.rules
governance.ingest.rules:
	@echo ">> Ingesting rules from .cursor/rules/ → DB"
	@PYTHONPATH=. python3 scripts/governance/ingest_rules_to_db.py
	@echo "Rules ingestion complete"
```

---

### 2.2.3 Validation Guard

**File**: `scripts/guards/guard_rules_db_ssot.py`

**Purpose**: Validate that DB SSOT matches `.cursor/rules`

**Algorithm**:

```python
#!/usr/bin/env python3
"""
guard_rules_db_ssot.py — Validate DB rules SSOT matches .cursor/rules/*.mdc
"""

import hashlib
import json
import sys
from pathlib import Path
import psycopg

from scripts.config.env import get_ro_dsn

ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = ROOT / ".cursor" / "rules"

def main():
    """
    Validate DB SSOT:
    1. Query control.rule_definition for all rules
    2. For each rule, check .cursor/rules/NNN-name.mdc exists
    3. Compute content_hash and compare with DB
    4. Emit HINT/FAIL based on STRICT_RULES_DB_SSOT env var
    """
    dsn = get_ro_dsn()
    if not dsn:
        print(json.dumps({
            "ok": True,
            "mode": "db_off",
            "reason": "No RO DSN available; DB unavailable (hermetic behavior)"
        }))
        return 0
    
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT rule_id, name, status, docs_path, always_apply
                    FROM control.rule_definition
                    ORDER BY rule_id
                    """
                )
                db_rules = cur.fetchall()
    except Exception as e:
        print(json.dumps({
            "ok": True,
            "mode": "db_off",
            "reason": f"DB query failed: {e}"
        }))
        return 0
    
    issues = []
    
    for rule_id, name, status, docs_path, always_apply in db_rules:
        rule_file = ROOT / docs_path if docs_path else RULES_DIR / f"{rule_id}-{name}.mdc"
        
        if not rule_file.exists():
            issues.append({
                "rule_id": rule_id,
                "issue": "file_missing",
                "expected_path": str(rule_file.relative_to(ROOT))
            })
            continue
        
        # Compute content hash
        content = rule_file.read_text()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Query DB for expected hash
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT content_hash FROM control.rule_source
                    WHERE rule_id = %s AND source_type = 'cursor_rules'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (rule_id,)
                )
                row = cur.fetchone()
                if not row:
                    issues.append({
                        "rule_id": rule_id,
                        "issue": "no_source_record",
                        "path": str(rule_file.relative_to(ROOT))
                    })
                    continue
                
                db_hash = row[0]
                if content_hash != db_hash:
                    issues.append({
                        "rule_id": rule_id,
                        "issue": "hash_mismatch",
                        "path": str(rule_file.relative_to(ROOT)),
                        "db_hash": db_hash,
                        "file_hash": content_hash
                    })
    
    # Determine posture
    strict_mode = os.getenv("STRICT_RULES_DB_SSOT") == "1"
    
    if issues:
        result = {
            "ok": not strict_mode,
            "mode": "STRICT" if strict_mode else "HINT",
            "issues": issues,
            "count": len(issues)
        }
        print(json.dumps(result, indent=2))
        return 1 if strict_mode else 0
    else:
        result = {
            "ok": True,
            "mode": "STRICT" if strict_mode else "HINT",
            "message": "All rules in sync between DB and .cursor/rules/",
            "rule_count": len(db_rules)
        }
        print(json.dumps(result, indent=2))
        return 0

if __name__ == "__main__":
    exit(main())
```

**Makefile Targets**:
```makefile
.PHONY: guard.rules.db.ssot guard.rules.db.ssot.strict
guard.rules.db.ssot:
	@mkdir -p evidence
	@python3 scripts/guards/guard_rules_db_ssot.py | tee evidence/guard_rules_db_ssot.json
	@cat evidence/guard_rules_db_ssot.json

guard.rules.db.ssot.strict:
	@mkdir -p evidence
	@STRICT_RULES_DB_SSOT=1 python3 scripts/guards/guard_rules_db_ssot.py | tee evidence/guard_rules_db_ssot.json
	@cat evidence/guard_rules_db_ssot.json
	@jq -e '.ok == true' evidence/guard_rules_db_ssot.json
```

---

### 2.2.4 Documentation

**File**: `docs/runbooks/GOVERNANCE_DB_SSOT.md`

**Content**:
```markdown
# Governance DB SSOT Runbook

## Overview

Governance rules are now stored in Postgres (`control.rule_definition`) as the single source of truth (SSOT).

## Tables

- `control.rule_definition` — Rule metadata (id, name, status, severity, always_apply)
- `control.rule_source` — Rule sources (path, content_hash, full content)
- `control.guard_definition` — Guard-to-rule mappings

## Operations

### Ingest Rules to DB

```bash
make governance.ingest.rules
```

This parses `.cursor/rules/*.mdc` files and populates the DB.

### Validate DB SSOT

```bash
# HINT mode (warns only)
make guard.rules.db.ssot

# STRICT mode (fail-closed)
make guard.rules.db.ssot.strict
```

### Query Rules from DB

```sql
-- List all rules
SELECT rule_id, name, status, severity, always_apply
FROM control.rule_definition
ORDER BY rule_id;

-- Always-Apply Triad
SELECT rule_id, name FROM control.rule_definition
WHERE always_apply = true;

-- Active rules only
SELECT rule_id, name FROM control.rule_definition
WHERE status = 'active';
```

## CI Integration

- **PR CI**: Runs `guard.rules.db.ssot` (HINT mode)
- **Tag CI**: Runs `guard.rules.db.ssot.strict` (STRICT mode)

## Hermetic Behavior

- Ingestion script requires `GEMATRIA_DSN` (write-enabled)
- Guard script tolerates `db_off` mode (returns `ok: true` when DB unavailable)
```

---

## 2.3 Transition Plan

### Phase 1: Implementation (1 PR)

**Tasks**:
1. ✅ Create migration `042_governance_rules_ssot.sql` with 3 tables
2. ✅ Implement `scripts/governance/ingest_rules_to_db.py`
3. ✅ Implement `scripts/guards/guard_rules_db_ssot.py`
4. ✅ Add Makefile targets (`governance.ingest.rules`, `guard.rules.db.ssot`)
5. ✅ Write runbook `docs/runbooks/GOVERNANCE_DB_SSOT.md`
6. ✅ Update AGENTS.md with DB SSOT references

**Verification**:
```bash
# 1. Apply migration
psql $GEMATRIA_DSN -f migrations/042_governance_rules_ssot.sql

# 2. Run ingestion
make governance.ingest.rules

# 3. Verify DB contains rules
psql $GEMATRIA_DSN -c "SELECT COUNT(*) FROM control.rule_definition;"
# Expected: 69 (or current rule count)

# 4. Run guard
make guard.rules.db.ssot
# Expected: ok: true, no issues

# 5. Housekeeping
make housekeeping
```

---

### Phase 2: CI Integration

**Tasks**:
1. Add `guard.rules.db.ssot` to PR CI workflow (HINT mode)
2. Add `guard.rules.db.ssot.strict` to tag CI workflow (STRICT mode)
3. Update `.github/workflows/ci.yml` with new guard

**Verification**:
```yaml
# .github/workflows/ci.yml
- name: Validate Rules DB SSOT
  run: make guard.rules.db.ssot
```

---

# 3. KEY INSIGHTS FOR GPT

## 3.1 What Already Works

1. ✅ **Control-Plane Schema** — Tables exist, migrations applied
2. ✅ **AI Tracking** — Tables exist, functions work
3. ✅ **MCP Catalog** — Tables exist, exports work
4. ✅ **Compliance Exports** — JSON exports working
5. ✅ **PMAgent Commands** — All control commands implemented
6. ✅ **DSN Centralization** — Loaders operational
7. ✅ **Guards System** — 60+ guards operational
8. ✅ **Phase-7F/7G** — Local LM + UI complete
9. ✅ **Share Sync** — Manifest-driven sync working
10. ✅ **Housekeeping** — Full pipeline operational
11. ✅ **Cursor Rules** — 69 rules in `.cursor/rules/`
12. ✅ **AGENTS.md Governance** — Auto-generation working

## 3.2 What's the Gap

1. ❌ **No rules in DB** — Rules live only in `.cursor/rules/*.mdc`
2. ❌ **No ingestion script** — No way to populate `control.rule_definition`
3. ❌ **No DB SSOT guard** — No validation of DB vs `.cursor/rules`

## 3.3 What Needs to Be Done (ONE PR)

**Scope**: Add DB-backed governance SSOT

**Files to Create**:
1. `migrations/042_governance_rules_ssot.sql` — 3 new tables
2. `scripts/governance/ingest_rules_to_db.py` — Ingestion script
3. `scripts/guards/guard_rules_db_ssot.py` — Validation guard
4. `docs/runbooks/GOVERNANCE_DB_SSOT.md` — Operations runbook

**Files to Modify**:
1. `Makefile` — Add 3 new targets
2. `AGENTS.md` — Add DB SSOT references

**Estimated Effort**: 1 PR, 4-6 hours of focused work

**Verification Steps**:
```bash
# 1. Apply migration
psql $GEMATRIA_DSN -f migrations/042_governance_rules_ssot.sql

# 2. Ingest rules
make governance.ingest.rules

# 3. Verify count
psql $GEMATRIA_DSN -c "SELECT COUNT(*) FROM control.rule_definition;"

# 4. Run guard
make guard.rules.db.ssot

# 5. Housekeeping
make housekeeping

# 6. PR smoke
make book.smoke && make ci.exports.smoke && make guards.all
```

---

# 4. REFERENCE FILES (Templates for GPT)

## 4.1 Existing Migrations (Templates)

- `migrations/040_control_plane_schema.sql` — Control-plane schema template
- `migrations/015_create_governance_tracking.sql` — Governance tracking template
- `migrations/041_control_mcp_catalog_view.sql` — MCP catalog template

**Pattern to Follow**:
```sql
-- Migration NNN: Description
-- Author: GPT-5
-- Date: 2025-11-16

BEGIN;

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS control;

-- Create tables
CREATE TABLE control.table_name (...);

-- Create indexes
CREATE INDEX idx_name ON control.table_name(...);

-- Create comments
COMMENT ON TABLE control.table_name IS 'Description';

COMMIT;
```

---

## 4.2 Existing Guards (Templates)

- `scripts/guards/guard_ai_tracking_contract.py` — DB contract validation template
- `scripts/guards/guard_control_compliance_exports.py` — Export validation template
- `scripts/guards/guard_db_health.py` — DB health check template

**Pattern to Follow**:
```python
#!/usr/bin/env python3
"""
guard_name.py — Guard description
"""

import json
import os
import sys
import psycopg

from scripts.config.env import get_ro_dsn

def main():
    # 1. Get RO DSN (hermetic behavior)
    dsn = get_ro_dsn()
    if not dsn:
        print(json.dumps({
            "ok": True,
            "mode": "db_off",
            "reason": "No RO DSN available"
        }))
        return 0
    
    # 2. Connect and validate
    try:
        with psycopg.connect(dsn) as conn:
            # ... validation logic ...
            pass
    except Exception as e:
        # Hermetic: tolerate DB failures
        print(json.dumps({
            "ok": True,
            "mode": "db_off",
            "reason": f"DB error: {e}"
        }))
        return 0
    
    # 3. Check STRICT mode
    strict_mode = os.getenv("STRICT_GUARD_NAME") == "1"
    
    # 4. Return result
    result = {
        "ok": True,  # or False if issues found
        "mode": "STRICT" if strict_mode else "HINT",
        # ... other fields ...
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    exit(main())
```

---

## 4.3 Existing Loaders (Templates)

- `scripts/config/env.py` — DSN loaders template
- `agentpm/db/loader.py` — SQLAlchemy engines template

**DSN Loader Pattern**:
```python
from scripts.config.env import get_rw_dsn, get_ro_dsn

# Write-enabled DSN
rw_dsn = get_rw_dsn()

# Read-only DSN
ro_dsn = get_ro_dsn()
```

---

## 4.4 Existing Runbooks (Templates)

- `docs/runbooks/CONTROL_STATUS.md` — Command usage template
- `docs/runbooks/MCP_KNOWLEDGE_DB.md` — DB usage template
- `docs/runbooks/DB_HEALTH.md` — Health check template

**Runbook Pattern**:
```markdown
# Feature Name Runbook

## Overview

Brief description of feature.

## Commands

### Command 1

```bash
make target.name
```

Description of what this does.

## Verification

Steps to verify the feature works.

## Troubleshooting

Common issues and solutions.
```

---

# 5. CONCLUSION

The Gemantria system has **all the infrastructure needed** for Phase-7 governance reconstruction. The missing piece is **populating the DB with rules** and **validating the sync**.

**GPT does NOT need to**:
- ❌ Build control-plane schema (exists)
- ❌ Build AI tracking tables (exists)
- ❌ Build PMAgent commands (exists)
- ❌ Build guards system (exists)
- ❌ Build share sync (exists)
- ❌ Build housekeeping (exists)

**GPT ONLY needs to**:
- ✅ Add 3 new tables for rule definitions (migration 042)
- ✅ Write ingestion script (parse `.cursor/rules/*.mdc` → DB)
- ✅ Write guard script (validate DB matches `.cursor/rules`)
- ✅ Add 3 Makefile targets
- ✅ Write 1 runbook
- ✅ Update AGENTS.md
- ✅ Run once + verify
- ✅ Open PR

**This is integration work, not greenfield development.**

---

# 6. APPENDIX: File Inventory

## Control-Plane Files (Existing)

```
migrations/040_control_plane_schema.sql          ✅
migrations/015_create_governance_tracking.sql    ✅
migrations/016_create_ai_learning_tracking.sql   ✅
migrations/041_control_mcp_catalog_view.sql      ✅

scripts/config/env.py                            ✅
agentpm/db/loader.py                            ✅

agentpm/control_plane/exports.py                 ✅
scripts/db/control_compliance_exports.py         ✅
scripts/db/control_lm_metrics_export.py          ✅

scripts/guards/guard_ai_tracking_contract.py     ✅
scripts/guards/guard_alwaysapply_dbmirror.py     ✅
scripts/guards/guard_control_compliance_exports.py ✅
scripts/guards/guard_db_health.py                ✅
scripts/guards/guard_lm_health.py                ✅

pmagent/cli.py                                   ✅
scripts/control/*.py                             ✅

docs/runbooks/CONTROL_STATUS.md                  ✅
docs/runbooks/CONTROL_SCHEMA.md                  ✅
docs/runbooks/CONTROL_TABLES.md                  ✅
docs/runbooks/MCP_KNOWLEDGE_DB.md                ✅
```

## Governance Files (To Create)

```
migrations/042_governance_rules_ssot.sql         ❌ (needs creation)
scripts/governance/ingest_rules_to_db.py         ❌ (needs creation)
scripts/guards/guard_rules_db_ssot.py            ❌ (needs creation)
docs/runbooks/GOVERNANCE_DB_SSOT.md              ❌ (needs creation)
```

## Governance Files (Existing)

```
.cursor/rules/000-ssot-index.mdc                 ✅ (69 total)
AGENTS.md                                        ✅
RULES_INDEX.md                                   ✅

scripts/update_share.py                          ✅
scripts/sync_share.py                            ✅
scripts/governance_housekeeping.py               ✅
scripts/governance_docs_hints.py                 ✅
scripts/rules_audit.py                           ✅
scripts/create_agents_md.py                      ✅
scripts/auto_update_agents_md.py                 ✅
scripts/validate_agents_md.py                    ✅
scripts/generate_forest.py                       ✅
scripts/pm_snapshot.py                           ✅

docs/SSOT/SHARE_MANIFEST.json                    ✅
docs/SSOT/MASTER_PLAN.md                         ✅
docs/SSOT/GPT_REFERENCE_GUIDE.md                 ✅
```

---

**END OF COMPREHENSIVE SYSTEM REPORT**

---

**Usage Instructions for GPT**:

1. Read this entire report carefully
2. Understand that 95% of what you need already exists
3. Focus ONLY on the 4 files to create (section 2.2)
4. Use existing templates from section 4 as patterns
5. Verify using commands in section 2.3
6. Open ONE PR with all changes

**DO NOT**:
- Rebuild existing infrastructure
- Create new guard patterns (use templates)
- Invent new DSN loaders (use `scripts.config.env`)
- Create new migration patterns (follow existing ones)

**DO**:
- Follow existing patterns exactly
- Test locally before opening PR
- Run `make housekeeping` after all changes
- Include verification steps in PR description

