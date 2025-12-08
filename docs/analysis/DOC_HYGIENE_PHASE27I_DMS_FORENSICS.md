# Phase 27.I — DMS Forensics (Batch 4B)

Read-only inspection of `control.doc_registry` and related tables.
No writes performed in this batch.


## doc_registry schema

- `doc_id` :: uuid
- `logical_name` :: text
- `role` :: text
- `repo_path` :: text
- `share_path` :: text
- `is_ssot` :: boolean
- `enabled` :: boolean
- `created_at` :: timestamp with time zone
- `updated_at` :: timestamp with time zone

## doc_registry counts

- Total rows: **1176**

By extension:
- `*.py`: 779
- `*.md`: 388
- `*.pdf`: 9

## Enabled flag distribution

- enabled=True: 1176

## Importance distribution

- Column `importance` does not exist in doc_registry (confirmed missing).

## Sample doc_registry rows (markdown)

- `agentpm/adapters/AGENTS.md` — enabled=True, importance=None
- `agentpm/AGENTS.md` — enabled=True, importance=None
- `agentpm/ai_docs/AGENTS.md` — enabled=True, importance=None
- `agentpm/atlas/AGENTS.md` — enabled=True, importance=None
- `agentpm/biblescholar/AGENTS.md` — enabled=True, importance=None
- `agentpm/biblescholar/tests/AGENTS.md` — enabled=True, importance=None
- `agentpm/bus/AGENTS.md` — enabled=True, importance=None
- `agentpm/control_plane/AGENTS.md` — enabled=True, importance=None
- `agentpm/control_widgets/AGENTS.md` — enabled=True, importance=None
- `agentpm/db/AGENTS.md` — enabled=True, importance=None
- `agentpm/dms/AGENTS.md` — enabled=True, importance=None
- `agentpm/docs/AGENTS.md` — enabled=True, importance=None
- `agentpm/exports/AGENTS.md` — enabled=True, importance=None
- `agentpm/extractors/AGENTS.md` — enabled=True, importance=None
- `agentpm/gatekeeper/AGENTS.md` — enabled=True, importance=None
- `agentpm/governance/AGENTS.md` — enabled=True, importance=None
- `agentpm/graph/AGENTS.md` — enabled=True, importance=None
- `agentpm/guard/AGENTS.md` — enabled=True, importance=None
- `agentpm/guarded/AGENTS.md` — enabled=True, importance=None
- `agentpm/handoff/AGENTS.md` — enabled=True, importance=None
- `agentpm/hints/AGENTS.md` — enabled=True, importance=None
- `agentpm/kb/AGENTS.md` — enabled=True, importance=None
- `agentpm/knowledge/AGENTS.md` — enabled=True, importance=None
- `agentpm/lm/AGENTS.md` — enabled=True, importance=None
- `agentpm/lm_widgets/AGENTS.md` — enabled=True, importance=None
