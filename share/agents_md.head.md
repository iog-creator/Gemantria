# agents_md.head

**Generated**: 2025-12-07T19:20:06.089351+00:00
**Source**: `agents_md.head.json`

---

- **schema**: `file_head.v1`
- **generated_at**: `2025-12-07T19:19:53.394910+00:00`
- **file_path**: `/home/mccoy/Projects/Gemantria.v2/AGENTS.md`
- **exists**: `true`
- **line_count**: `1774`
- **head_lines**:
  1. `# AGENTS.md — Gemantria Agent Framework`
  2. `<!-- alwaysapply.sentinel: 050,051,052 source=ai_interactions -->`
  3. ``
  4. `> \*\*AGENT REGISTRY ROLE: CANONICAL_GLOBAL\*\*  `
  5. ```
> Source of truth for the Gemantria agent roster (IDs, roles, subsystems, tools, workflows, governance).  
```

  6. ```
> Derived views: `pmagent/kb/AGENTS.md` (PM-focused), `pmagent/tests/\*/AGENTS.md` (test-specific), other subsystem-specific summaries.  
```

  7. `> Last reviewed: 2025-12-03`
  8. ``
  9. ```
> \*\*Always-Apply Triad\*\*: We operate under \*\*Rule-050 (LOUD FAIL)\*\*, \*\*Rule-051 (CI gating)\*\*, and \*\*Rule-052 (tool-priority)\*\*. The guards ensure this 050/051/052 triad is present in docs and mirrored in DB checks.
```

  10. ``
  11. `## Doc Strategy & DMS Hierarchy (Gemantria-Specific)`
  12. ``
  13. `\*\*Architecture Clarification:\*\*`
  14. ``
  15. `pmagent is the governance and control-plane engine for the Gemantria project.`
  16. `All documentation lifecycle, classification, metadata, and structural enforcement`
  17. `are handled by pmagent's control-plane DMS (`control.doc_registry`).`
  18. `Gemantria is the domain project being governed, not the system performing`
  19. `the governance. AGENTS.md surfaces define the agent-facing worldview of both`
  20. `Gemantria and pmagent; the DMS records that worldview in structured form.`
  21. ``
  22. `In Gemantria, documentation and metadata are layered. The hierarchy for truth is:`
  23. ``
  24. `1. \*\*Orchestrator (human)\*\* — ultimate source of product and governance intent.`
  25. ``
  26. `2. \*\*Contracts & SSOT docs\*\* (`docs/SSOT/\*\*`, PHASE index docs, OPS/PM contracts).`
  27. ``
  28. ```
3. \*\*AGENTS surfaces\*\* (`AGENTS.md` at root and subsystem levels) — canonical map of agents, tools, and doc surfaces.
```

  29. ``
  30. ```
4. \*\*pmagent control-plane DMS\*\* (`control.doc_registry` in Postgres) — structured inventory and lifecycle metadata for docs (paths, importance, tags, owner_component, enabled/archived), which must reflect (not override) the above.
```

  31. ``
  32. `5. \*\*Filesystem layout\*\* — implementation detail that must be kept in sync with the registry.`
  33. ``
  34. `\*\*AGENTS.md is privileged:\*\*`
  35. ``
  36. ```
- Root `AGENTS.md` is the \*\*global agent registry\*\* (`CANONICAL_GLOBAL`) and must never be archived or demoted.
```

  37. ``
  38. `- Subsystem-level `AGENTS.md` files are local views that inherit from this global registry.`
  39. ``
  40. ```
- Any automated doc lifecycle (archive/cleanup/moves) must treat `AGENTS.md` as \*\*core SSOT\*\*, not as regular documentation.
```

  41. ``
  42. `\*\*pmagent control-plane DMS responsibilities:\*\*`
  43. ``
  44. ```
- Tracks \*\*which docs exist\*\*, where they live (`repo_path`), their lifecycle (`enabled`, archive path), and their metadata (`importance`, `tags`, `owner_component`).
```

  45. ``
  46. `- Must not propose or apply moves that contradict the AGENTS contract (e.g., archiving `AGENTS.md`).`
  47. ``
  48. ```
- Housekeeping scripts (`scripts/governance/ingest_docs_to_db.py` and related) populate the pmagent control-plane DMS with `importance`, `tags`, and `owner_component` but \*\*never downgrade AGENTS docs\*\*.
```

  49. ``
  50. ```
In short: \*\*AGENTS.md defines the world; the pmagent control-plane DMS records and enforces that definition.\*\*
```

  51. ``
  52. `## Canonical Agents Table (Draft from KB Registry)`
  53. ``
  54. ```
The following table was generated from \*\*share/AGENTS_REGISTRY_SNAPSHOT.json\*\* to reflect the currently registered agents in the pmagent control-plane DMS.
```

  55. ``
  56. `<!-- BEGIN: AUTO-GENERATED AGENTS TABLE -->`
  57. `\| Agent ID \| Path \| Subsystem \| Tags \|`
  58. `\|----------\|------\|-----------\|------\|`
  59. `\| agents::agentpm/kb/agents.md \| agentpm/kb/AGENTS.md \| ops \| ssot, agent_framework \|`
  60. ```
\| agents::agentpm/knowledge/agents.md \| agentpm/knowledge/AGENTS.md \| ops \| ssot, agent_framework \|
```

  61. `\| agents::agentpm/metrics/agents.md \| agentpm/metrics/AGENTS.md \| ops \| ssot, agent_framework \|`
  62. `\| agents::agentpm/rpc/agents.md \| agentpm/rpc/AGENTS.md \| ops \| ssot, agent_framework \|`
  63. ```
\| agents::agentpm/tests/kb/agents.md \| agentpm/tests/kb/AGENTS.md \| general \| ssot, agent_framework \|
```

  64. ```
\| agents::agentpm/tests/status/agents.md \| agentpm/tests/status/AGENTS.md \| ops \| ssot, agent_framework \|
```

  65. `\| agents::docs/audits/agents.md \| docs/audits/AGENTS.md \| ops \| ssot, agent_framework \|`
  66. ```
\| agents::src/gemantria.egg-info/agents.md \| src/gemantria.egg-info/AGENTS.md \| gematria \| ssot, agent_framework \|
```

  67. `<!-- END: AUTO-GENERATED AGENTS TABLE -->`
  68. ``
  69. `## Directory Purpose`
  70. ``
  71. ```
The root `AGENTS.md` serves as the primary agent framework documentation for the Gemantria repository, defining mission, priorities, environment, workflows, and governance for all agentic operations across the codebase.
```

  72. ``
  73. `## Mission`
  74. ```
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.
```

  75. ``
  76. `## Priorities`
  77. `1) Correctness: \*\*Code gematria > bible_db > LLM (LLM = metadata only)\*\*.`
  78. `2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.`
  79. ```
3) Safety: \*\*bible_db is READ-ONLY\*\*; parameterized SQL only; \*\*fail-closed if <50 nouns\*\* (ALLOW_PARTIAL=1 is explicit).
```

  80. `- \*\*pmagent control-plane DMS Lifecycle Policy\*\*:`
  81. ```
    - \*\*Exclusive SSOT\*\*: `control.doc_registry` (pmagent control-plane DMS) is the ONLY authority for document existence and status.
```

  82. ```
    - \*\*Lifecycle\*\*: `importance` and `enabled` columns determine if a doc is Core, Helpful, or Archived.
```

  83. `    - \*\*Pathing\*\*: Filesystem locations must reflect pmagent control-plane DMS `repo_path`.`
  84. ``
  85. `## pmagent Status`
  86. ``
  87. ```
See `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` for current vs intended state of pmagent commands and capabilities.
```

  88. ``
  89. ```
See `docs/SSOT/PMAGENT_REALITY_CHECK_DESIGN.md` for reality.check implementation design and validation schema.
```

  90. ``
  91. `## PM DMS Integration (Rule-053) ⭐ NEW`
  92. ``
  93. ```
\*\*Phase 9.1\*\*: PM must query \*\*pmagent control-plane DMS (Postgres `control.doc_registry`)\*\* BEFORE file searching.
```

  94. ``
  95. `\*\*DMS-First Workflow\*\*:`
  96. `1. \*\*Documentation\*\*: `pmagent kb registry by-subsystem --owning-subsystem=<project>``
  97. `2. \*\*Tool Catalog\*\*: `SELECT \* FROM control.mcp_tool_catalog WHERE tags @> '{<project>}'``
  98. `3. \*\*Project Status\*\*: `pmagent status kb` and `pmagent plan kb list``
  99. `4. \*\*File Search\*\* (LAST RESORT): Only if content not in DMS`
  100. ``
- **head_line_count**: `100`
- **error**: `null`
