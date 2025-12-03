# KB Document Registry (KB-Reg:M1)

## Purpose

The KB document registry tracks knowledge-base documents (AGENTS.md, SSOT docs, rules, runbooks, ADRs, etc.) with structured metadata including:

- **id/handle**: Unique identifier for the document
- **title**: Human-readable title
- **path/URI**: File path relative to repo root or absolute URI
- **type**: Document type (agents_md, ssot, rule, runbook, adr, changelog, readme, other)
- **tags**: Tags for categorization
- **owning_subsystem**: Owning subsystem (pmagent, docs, rules, scripts, etc.)
- **provenance**: Provenance metadata (source, last_updated, checksum, etc.)

## SSOT & Persistence

- **Registry file**: `share/kb_registry.json` (JSON format)
- **CI/Hermetic**: Registry is read-only in CI; writes are only allowed in local/dev environments
- **Schema version**: 1.0 (versioned for forward compatibility)

## Usage

### CLI Commands

```bash
# List all registered documents
pmagent kb registry list

# Show details for a specific document
pmagent kb registry show <doc_id>

# Validate registry (check file existence, duplicates)
pmagent kb registry validate
```

### Python API

```python
from pmagent.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    load_registry,
    save_registry,
    validate_registry,
)

# Load registry
registry = load_registry()

# Create and add document
doc = KBDocument(
    id="agents-md-root",
    title="Root AGENTS.md",
    path="AGENTS.md",
    type="agents_md",
    tags=["governance", "root"],
    owning_subsystem="root",
    provenance={"source": "manual"},
)
registry.add_document(doc)

# Save registry (only in local/dev, not CI)
save_registry(registry, allow_ci_write=False)

# Validate registry
validation = validate_registry(registry)
if not validation["valid"]:
    print("Errors:", validation["errors"])
```

## Integration

- **pm.snapshot**: Registry is included in system snapshots (KB-Reg:M2) — advisory-only, non-gating
- **AgentPM planning**: Registry provides `query_registry()` helper for document discovery and planning (KB-Reg:M2)
- **Share manifest**: Registry complements share manifest by providing document metadata

## KB-Reg:M2 — Snapshot & Planning Integration (Implemented)

### Snapshot Integration

The KB registry is integrated into `pm.snapshot` via `pmagent.status.snapshot.get_system_snapshot()`:

- **Advisory-only**: KB registry summary does not affect `overall_ok` (non-gating)
- **Read-only in CI**: Registry is read-only in CI environments (per Rule-044)
- **Summary fields**: `available`, `total`, `valid`, `errors_count`, `warnings_count`
- **Graceful handling**: Returns empty registry summary if file is missing (hermetic behavior)

### Planning Helper

The `query_registry()` function provides a read-only filter interface for planning agents:

```python
from pmagent.kb.registry import load_registry, query_registry

registry = load_registry()

# Query by type
ssot_docs = query_registry(registry, type="ssot")

# Query by owning subsystem
pmagent_docs = query_registry(registry, owning_subsystem="pmagent")

# Query by tags (document must have all specified tags)
governance_docs = query_registry(registry, tags=["governance", "root"])

# Combined filters
results = query_registry(registry, type="agents_md", owning_subsystem="pmagent", tags=["governance"])
```

This helper is intended for future AgentPM planning flows (no CLI yet).

## KB-Reg:M3a — Seeded Registry (Implemented)

The KB registry has been seeded with core SSOT documents, runbooks, and AGENTS.md files:

- **SSOT Documents**: `docs/SSOT/MASTER_PLAN.md`, `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md`
- **Key ADRs**: `ADR-065-postgres-ssot.md`, `ADR-066-lm-studio-control-plane-integration.md`, `ADR-032-bibledb-as-SSOT-roadmap.md`
- **Runbooks**: `docs/runbooks/PM_SNAPSHOT_CURRENT.md`
- **AGENTS.md files**: Root `AGENTS.md`, `pmagent/AGENTS.md`, `webui/graph/AGENTS.md`

**Seeding Script**: `scripts/kb/seed_registry.py` — Populates `share/kb_registry.json` with initial document entries. Respects CI write guards (Rule-044) — only runs in local/dev environments.

**CLI Commands**:
- `pmagent kb registry list` — List all registered documents
- `pmagent kb registry by-subsystem --owning-subsystem <subsystem>` — Filter by owning subsystem
- `pmagent kb registry by-tag --tag <tag>` — Filter by tag
- `pmagent kb registry show <doc_id>` — Show details for a specific document
- `pmagent kb registry validate` — Validate registry entries

**Registry Fields**:
- `id`: Unique identifier/handle
- `title`: Human-readable title
- `path`: File path relative to repo root
- `type`: Document type (ssot, adr, runbook, agents_md, etc.)
- `tags`: Tags for categorization
- `owning_subsystem`: Owning subsystem (docs, pmagent, webui, root, etc.)
- `provenance`: Provenance metadata (source, category, etc.)
- `registered_at`: ISO timestamp when document was registered

## KB-Reg:M3b — KB Status Surface & Planning View (Implemented)

The KB registry provides a PM-focused status view via `pmagent status kb`:

**Command**: `pmagent status kb [--json-only]`

**Output Structure**:
```json
{
  "available": true,
  "total": 9,
  "by_subsystem": {
    "docs": 3,
    "root": 4,
    "pmagent": 1,
    "webui": 1
  },
  "by_type": {
    "ssot": 2,
    "adr": 3,
    "runbook": 1,
    "agents_md": 3
  },
  "missing_files": [],
  "notes": []
}
```

**Use Cases**:
- **PM Planning**: "What docs do we have?" — Quick overview of document coverage
- **Coverage Gaps**: "What's missing?" — `missing_files` list shows validation issues
- **Subsystem Analysis**: "What docs belong to each subsystem?" — `by_subsystem` breakdown
- **Type Analysis**: "What types of docs do we have?" — `by_type` breakdown

**Integration**:
- `pmagent status kb` is the primary KB status view for PM/AgentPM planning
- `pmagent kb registry summary` provides the same view (wrapper for convenience)
- Both commands use `pmagent.status.snapshot.get_kb_status_view()` helper

## KB-Reg:M4 — Registry-Driven Hints (Implemented)

KB registry health is surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`:

**Hints Generator**: `pmagent.status.snapshot.get_kb_hints()` — Generates structured hints from KB registry status

**Hint Types**:
- `KB_REGISTRY_UNAVAILABLE` (INFO): Registry file not found
- `KB_MISSING_DOCS` (WARN): Registry references missing files
- `KB_LOW_COVERAGE_SUBSYSTEM` (INFO): Subsystem has low document coverage (<3 docs)
- `KB_VALIDATION_ISSUES` (WARN): Registry validation errors/warnings
- `KB_EMPTY_REGISTRY` (INFO): Registry exists but contains no documents

**Integration**:
- **pm.snapshot**: KB hints included in `evidence/pm_snapshot/snapshot.json` and rendered in `share/pm.snapshot.md` under "KB Hints (Advisory)" section
- **reality-check**: KB hints included in `kb_hints` field of verdict (advisory-only, never affects `overall_ok`)
- **Advisory-only**: KB hints are metadata only; they do not affect system health gates

**Example Hints**:
```json
[
  {
    "level": "INFO",
    "code": "KB_LOW_COVERAGE_SUBSYSTEM",
    "message": "Subsystem 'webui' has low document coverage (1 doc(s))",
    "subsystem": "webui",
    "have": 1
  },
  {
    "level": "WARN",
    "code": "KB_MISSING_DOCS",
    "message": "KB registry references 2 missing file(s)",
    "missing_count": 2,
    "missing_files": ["docs/missing1.md", "docs/missing2.md"]
  }
]
```

## KB-Reg:M5 — PostgreSQL Query Optimization (Implemented)

The KB registry builder (`scripts/kb/build_kb_registry.py`) has been optimized for PostgreSQL performance:

### JSONB Query Optimization

**Problem**: Queries were using inefficient `meta::text <> '{}'::text` which cannot use GIN indexes effectively.

**Solution**: Replaced with PostgreSQL-native JSONB containment operator `@>`:
- `f.meta @> '{"kb_candidate": true}'::jsonb` (uses GIN index directly)
- `f.meta @> '{"kb_candidate": true, "importance": "core"}'::jsonb` (compound queries)

**Performance Impact**: 2-5x faster queries on large datasets, better GIN index utilization.

**Files Modified**:
- `scripts/kb/build_kb_registry.py` (3 query locations optimized)
- `scripts/governance/classify_fragments.py` (1 query location optimized)

**Documentation**:
- **Reference**: `docs/SSOT/POSTGRES_OPTIMIZATION_REVIEW.md` (comprehensive optimization guide)
- **Priority**: `docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md` (actionable decision guide)
- **Summary**: `docs/SSOT/POSTGRES_OPTIMIZATION_SUMMARY.md` (this work summary)

**Status**: ✅ **COMPLETE** — Critical optimization implemented, additional optimizations documented for future use.

## Related Rules

- **Rule-044**: Share Manifest Contract (registry follows similar patterns)
- **Rule-037**: Data Persistence Completeness (registry is a persistent artifact)
- **Rule-030**: Share Sync (registry lives in share/ directory)

