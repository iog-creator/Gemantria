# PM Quick Start Guide

**Purpose**: Rapidly orient PM agents to project state when starting a new session.

## Immediate Context Check (30 seconds)

### 1. Current Phase
```bash
head -n 20 NEXT_STEPS.md
```
Look for: Phase number, completion status

### 2. System Health
```bash
pmagent health db --json-only
```
Look for: `"ok": true`

### 3. Next Work Items
```bash
pmagent plan next --limit 3
```
Look for: Unchecked items in NEXT_STEPS

### 4. Recent Changes
```bash
ls -lt evidence/pmagent/*.json | head -n 3
```
Look for: Recent capability sessions

## Project Structure (60 seconds)

### Key Directories
- `docs/SSOT/` - Single source of truth documents
- `docs/plans/` - Phase-specific plans
- `share/` - Shared documentation for context
- `migrations/` - Database schema changes
- `scripts/` - Automation scripts
- `src/services/` - API server and services

### Essential Documents
1. **MASTER_PLAN.md** - Overall roadmap (`docs/SSOT/`)
2. **NEXT_STEPS.md** - Work queue (root)
3. **AGENTS.md** - Agent workflows (root)
4. **PM_CONTRACT.md** - PM responsibilities (`docs/SSOT/`)
5. **PROJECT_STATUS.md** - Current state (`share/`)

## Critical Context (90 seconds)

### What is Gemantria?
Biblical text analysis system using:
- Graph-based semantic networks
- Pattern mining algorithms
- Multi-source biblical data
- REST API for frontend

### Current State (Phase 12)
- **Pattern Mining**: Implemented (Louvain, Cliques, Motifs)
- **Database**: PostgreSQL with pattern tables
- **API**: `/api/v1/patterns` endpoint active
- **Export**: Pattern JSON generation working

### Architecture
- **Backend**: Python (FastAPI, NetworkX, psycopg2)
- **Database**: PostgreSQL with JSONB
- **Frontend**: React/TypeScript (separate UI)
- **Exports**: JSON files in `exports/`

## DMS First Workflow (Rule 053)

Before any file search, query DMS:

### 1. Documentation
```bash
pmagent kb registry by-subsystem --owning-subsystem=<project>
```

### 2. Tool Catalog
```sql
SELECT * FROM control.mcp_tool_catalog WHERE tags @> '{<project>}'
```

### 3. Project Status
```bash
pmagent status kb
pmagent plan kb list
```

### 4. File Search (LAST RESORT)
Only if content not in DMS

## Common PM Tasks

### Start New Phase
1. Check MASTER_PLAN for next phase
2. Create phase plan in `docs/plans/`
3. Update NEXT_STEPS.md
4. Register in AGENTS.md
5. Run `make housekeeping`

### Update Progress
1. Mark items complete in NEXT_STEPS.md
2. Run governance sync: `make housekeeping`
3. Update phase status if complete

### Check System Health
```bash
pmagent bringup full  # Start services
pmagent health db     # Check database
pmagent status kb     # Check docs
```

### Generate Status Report
```bash
pmagent plan next     # Current work
pmagent status explain # System summary
```

## Phase 12 Specific Knowledge

### What Was Completed
- Database schema: `migrations/052_phase12_patterns.sql`
- Mining engine: `scripts/mining/find_patterns.py`
- API endpoint: `/api/v1/patterns`
- Export pipeline: `scripts/exports/export_patterns.py`

### Pattern Types
1. Louvain Communities (clustering)
2. Maximal Cliques (complete subgraphs)
3. Triangle Motifs (3-cycles)

### Key Metrics
- 9 patterns discovered (test data)
- 3 pattern types supported
- 2 database tables created
- 1 API endpoint added

## Emergency Context Recovery

If completely lost:
1. Read `share/PROJECT_STATUS.md` (this takes 2 minutes)
2. Read `NEXT_STEPS.md` (current work queue)
3. Run `pmagent plan next` (DMS query)
4. Read phase plan: `docs/plans/PHASE_*` for current phase
5. Check `AGENTS.md` for workflows

## References

- **Full Status**: `share/PROJECT_STATUS.md`
- **Phase 12**: `share/plans/PHASE_12_SUMMARY.md`
- **Master Plan**: `docs/SSOT/MASTER_PLAN.md`
- **Governance**: `AGENTS.md`
- **DMS Docs**: `pmagent kb registry list`

