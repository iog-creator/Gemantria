# ADR-032: bible_db as Single Source of Truth (Roadmap)

Status: Proposed (Major) | Owner: PM | Scope: DB schema + pipeline + exports

Decision: Adopt bible_db schema as SSOT across nodes/edges; all derived data must join on bible_db IDs.

Non-goals (now): immediate cut-over. Current pipeline remains the production path.

Milestones: M1 data model PRD, M2 compat views, M3 staged cut-over, M4 UI switch.

Risks: consumer breakage; mitigated by back-compat views and dual-exports during transition.