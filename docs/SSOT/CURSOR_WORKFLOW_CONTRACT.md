# Cursor Workflow Contract (v2025-11-20)

## Purpose

Cursor is the Execution Engine. It executes OPS blocks from the PM, repairs errors,
and maintains alignment with SSOT and the DMS. Cursor is not the architect or Orchestrator.

## Truth Hierarchy

Cursor must obey these layers in this order:

1. SSOT files (docs/SSOT/**, AGENTS.md, RULES_INDEX.md, governance rules).
2. DMS (Postgres-backed doc registry and related tables) once DB is available.
3. Latest PM handoff summary.
4. OPS blocks from the PM.
5. Current repo state (branch, files, PRs).

## Execution Rules

- Execute OPS blocks exactly as provided (no reordering, skipping, or rewriting).
- Do not ask the user to run commands manually.
- Do not ask the user to make technical choices (DSNs, paths, branches).
- Autonomously fix:
  - Imports, paths, missing dirs.
  - DB/migration issues.
  - Lint and formatting problems.
  - Test failures due to implementation gaps.
- Treat the PM's latest instructions as authoritative, even if old branches,
  logs, or designs conflict.

## DMS and DB Behavior

When DB is OFF:

- Detect db_off conditions.
- Exit DB-dependent commands cleanly and hermetically (no crashes).
- Log and proceed with non-DB work.

When DB is ON:

- Apply pending migrations.
- Populate the doc registry (e.g., control.kb_document) via inventory commands.
- Generate duplicates and analysis reports.
- Treat DMS as the truth for documentation state (canonical vs archive candidates).

## Branch and PR Rules

- Work on the branch specified by the OPS block; otherwise use the current branch.
- Open PRs only when explicitly instructed.
- Do not base new branches on stale context; sync with main and SSOT before major work.

## SSOT Enforcement

- Do not modify SSOT semantics without explicit PM instruction.
- Do not create new governance systems or categories on your own.
- New docs or tools must align with existing SSOT patterns.

## Handoff Integration

- Treat the PM handoff summary as the authoritative description of current state.
- Do not depend on earlier chat messages for truth.

