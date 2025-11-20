# AGENTS.md

## Directory Purpose

The `agentpm/plan/` directory contains planning workflows powered by the KB registry. These helpers provide deterministic, read-only planning surfaces for PM/AgentPM workflows.

## AgentPM-Next:M1 — Registry-Powered Planning Flows

**Purpose:** Provide a thin, deterministic planning surface that interprets KB registry status and hints to produce prioritized documentation worklists.

**Implementation:**
- **Helper**: `agentpm.plan.kb.build_kb_doc_worklist()` — Builds prioritized worklist from KB registry status and hints
- **CLI**: `pmagent plan kb` — Returns prioritized documentation worklist with suggested actions
- **Worklist structure**: Items grouped by subsystem, ordered by severity (missing > stale > out_of_sync > low_coverage > info)
- **Hermetic**: No writes, no LM calls; purely interprets existing KB signals

**Usage:**
```bash
# Get worklist in JSON format
pmagent plan kb --json-only

# Get worklist with human-readable output
pmagent plan kb
```

**Worklist Item Structure:**
- `id`: Document ID or subsystem identifier
- `title`: Human-readable title
- `subsystem`: Owning subsystem (e.g., "docs", "agentpm", "webui")
- `type`: Document type (e.g., "ssot", "adr", "runbook")
- `severity`: Priority level ("missing", "stale", "out_of_sync", "low_coverage", "info")
- `reason`: Explanation of why this item is in the worklist
- `suggested_action`: Recommended action to address the issue

**Integration:**
- Uses `agentpm.status.snapshot.get_kb_status_view()` and `get_kb_hints()` for KB data
- Uses `agentpm.kb.registry.load_registry()` for document details
- Processes freshness data from KB-Reg:M6 freshness analysis
- Processes hints from KB-Reg:M4 hint generation
