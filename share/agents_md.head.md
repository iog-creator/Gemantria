# agents_md.head

**Generated**: 2025-11-30T02:21:28.250189+00:00
**Source**: `agents_md.head.json`

---

- **schema**: `file_head.v1`
- **generated_at**: `2025-11-30T02:21:17.357903+00:00`
- **file_path**: `/home/mccoy/Projects/Gemantria.v2/AGENTS.md`
- **exists**: `true`
- **line_count**: `1672`
- **head_lines**:
  1. `# AGENTS.md — Gemantria Agent Framework`
  2. `<!-- alwaysapply.sentinel: 050,051,052 source=ai_interactions -->`
  3. ``
  4. ```
> \*\*Always-Apply Triad\*\*: We operate under \*\*Rule-050 (LOUD FAIL)\*\*, \*\*Rule-051 (CI gating)\*\*, and \*\*Rule-052 (tool-priority)\*\*. The guards ensure this 050/051/052 triad is present in docs and mirrored in DB checks.
```

  5. ``
  6. `## Directory Purpose`
  7. ``
  8. ```
The root `AGENTS.md` serves as the primary agent framework documentation for the Gemantria repository, defining mission, priorities, environment, workflows, and governance for all agentic operations across the codebase.
```

  9. ``
  10. `## Mission`
  11. ```
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.
```

  12. ``
  13. `## Priorities`
  14. `1) Correctness: \*\*Code gematria > bible_db > LLM (LLM = metadata only)\*\*.`
  15. `2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.`
  16. ```
3) Safety: \*\*bible_db is READ-ONLY\*\*; parameterized SQL only; \*\*fail-closed if <50 nouns\*\* (ALLOW_PARTIAL=1 is explicit).
```

  17. ``
  18. `## pmagent Status`
  19. ``
  20. ```
See `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` for current vs intended state of pmagent commands and capabilities.
```

  21. ``
  22. ```
See `docs/SSOT/PMAGENT_REALITY_CHECK_DESIGN.md` for reality.check implementation design and validation schema.
```

  23. ``
  24. `## PM DMS Integration (Rule-053) ⭐ NEW`
  25. ``
  26. `\*\*Phase 9.1\*\*: PM must query \*\*Postgres DMS (control plane)\*\* BEFORE file searching.`
  27. ``
  28. `\*\*DMS-First Workflow\*\*:`
  29. `1. \*\*Documentation\*\*: `pmagent kb registry by-subsystem --owning-subsystem=<project>``
  30. `2. \*\*Tool Catalog\*\*: `SELECT \* FROM control.mcp_tool_catalog WHERE tags @> '{<project>}'``
  31. `3. \*\*Project Status\*\*: `pmagent status kb` and `pmagent plan kb list``
  32. `4. \*\*File Search\*\* (LAST RESORT): Only if content not in DMS`
  33. ``
  34. `\*\*Feature Registration\*\*:`
  35. `- After building new tool/module: Create MCP envelope → `make mcp.ingest` → Update KB registry`
  36. `- PM learns capabilities automatically through DMS registration`
  37. `- \*\*Goal\*\*: PM and project develop together`
  38. ``
  39. ```
See `.cursor/rules/053-pm-dms-integration.mdc` and `docs/SSOT/PM_CONTRACT.md` Section 2.6 for full workflow.
```

  40. ``
  41. `## Environment`
  42. `- venv: `python -m venv .venv && source .venv/bin/activate``
  43. `- install: `make deps``
  44. `- Databases:`
  45. `  - `BIBLE_DB_DSN` — read-only Bible database (RO adapter denies writes pre-connection)`
  46. `  - `GEMATRIA_DSN` — read/write application database`
  47. `- \*\*DSN Access\*\*: All DSN access must go through centralized loaders:`
  48. `  - \*\*Preferred\*\*: `scripts.config.env` (`get_rw_dsn()`, `get_ro_dsn()`, `get_bible_db_dsn()`)`
  49. `  - \*\*Legacy\*\*: `src.gemantria.dsn` (`dsn_rw()`, `dsn_ro()`, `dsn_atlas()`)`
  50. `  - Never use `os.getenv("GEMATRIA_DSN")` directly - enforced by `guard.dsn.centralized``
  51. ``
  52. `### 3-Role DB Contract (OPS v6.2.3)`
  53. `\*\*Extraction DB\*\*: `GEMATRIA_DSN` → database `gematria`  `
  54. `\*\*SSOT DB\*\*: `BIBLE_DB_DSN` → database `bible_db` (read-only)  `
  55. ```
\*\*AI Tracking\*\*: \*\*lives in `gematria` DB\*\*, `public` schema; `AI_AUTOMATION_DSN` \*\*must equal\*\* `GEMATRIA_DSN`.  
```

  56. ```
Guards: `guard.rules.alwaysapply.dbmirror` (triad), `guard.ai.tracking` (tables `public.ai_interactions`, `public.governance_artifacts`).  
```

  57. `CI posture: HINT on PRs; STRICT on tags behind `vars.STRICT_DB_MIRROR_CI == '1'`.`
  58. `- Batch & overrides:`
  59. `  - `BATCH_SIZE=50` (default noun batch size)`
  60. `  - `ALLOW_PARTIAL=0\|1` (if 1, manifest must capture reason)`
  61. `  - `PARTIAL_REASON=<string>` (required when ALLOW_PARTIAL=1)`
  62. `- Checkpointer: `CHECKPOINTER=postgres\|memory` (default: memory for CI/dev)`
  63. `- LLM: Local inference providers (LM Studio or Ollama) when enabled; confidence is metadata only.`
  64. ```
  - \*\*Inference Providers\*\* (Phase-7E): Supports both LM Studio and Ollama via `INFERENCE_PROVIDER`:
```

  65. ```
    - `lmstudio`: OpenAI-compatible API (`OPENAI_BASE_URL`) - \*\*Granite models available in LM Studio\*\*
```

  66. ```
    - `ollama`: Native HTTP API (`OLLAMA_BASE_URL`) - \*\*Granite models also available via Ollama\*\*
```

  67. ```
  - \*\*Setup\*\*: See `docs/runbooks/LM_STUDIO_SETUP.md` for LM Studio setup or `docs/runbooks/OLLAMA_ALTERNATIVE.md` for Ollama
```

  68. ```
  - \*\*Quick Start (LM Studio)\*\*: Set `INFERENCE_PROVIDER=lmstudio`, `LM_STUDIO_ENABLED=1`, `OPENAI_BASE_URL=http://127.0.0.1:9994/v1`
```

  69. ```
  - \*\*Quick Start (Ollama)\*\*: Set `INFERENCE_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://127.0.0.1:11434`, then `ollama pull ibm/granite4.0-preview:tiny`
```

  70. `  - \*\*Health Check\*\*: `pmagent health lm` verifies inference provider availability`
  71. `  - \*\*Default Models (Phase-7F)\*\*: `
  72. `    - \*\*Default stack\*\*: Granite embedding + Granite reranker + Granite local agent.`
  73. `      - `LOCAL_AGENT_MODEL=granite4:tiny-h` (Ollama)`
  74. `      - `EMBEDDING_MODEL=granite-embedding:278m` (Granite)`
  75. `      - `RERANKER_MODEL=granite4:tiny-h` (Granite)`
  76. `    - \*\*Bible lane\*\*: BGE embedding + theology model; BGE is not the general default.`
  77. ```
      - `BIBLE_EMBEDDING_MODEL=bge-m3:latest` (Ollama: `qllama/bge-m3`) - for Bible/multilingual tasks only
```

  78. `    - \*\*Qwen reranker\*\*: fallback only, not the primary reranker.`
  79. `    - `THEOLOGY_MODEL=Christian-Bible-Expert-v2.0-12B` (via theology adapter)`
  80. ```
  - \*\*Retrieval Profile (Phase-7C)\*\*: `RETRIEVAL_PROFILE=DEFAULT` (default) uses Granite stack. Setting `RETRIEVAL_PROFILE=GRANITE` or `BIBLE` switches retrieval embeddings/rerankers accordingly. Granite IDs are resolved via `GRANITE_EMBEDDING_MODEL`, `GRANITE_RERANKER_MODEL`, and `GRANITE_LOCAL_AGENT_MODEL`. Misconfigured Granite profiles emit a `HINT` and fall back to DEFAULT for hermetic runs.
```

  81. ```
  - \*\*Planning Lane (Gemini CLI + Codex)\*\*: pmagent exposes a \*\*planning slot\*\* for backend planning, coding refactors, and math-heavy reasoning. This lane is intentionally \*\*non-theology\*\* and never substitutes for gematria/theology slots.
```

  82. ```
    - Configure via `PLANNING_PROVIDER` (`gemini`, `codex`, `lmstudio`, `ollama`) and `PLANNING_MODEL`. Optional toggles: `GEMINI_ENABLED`, `CODEX_ENABLED`, `GEMINI_CLI_PATH`, `CODEX_CLI_PATH`.
```

  83. ```
    - pmagent calls CLI adapters (`agentpm/adapters/gemini_cli.py`, `agentpm/adapters/codex_cli.py`) with structured prompts, logs runs through `agentpm.runtime.lm_logging`, and records outcomes in `control.agent_run`.
```

  84. ```
    - If the selected CLI is unavailable, pmagent fails closed with `mode="lm_off"` and optionally falls back to the Granite local_agent slot—never to theology.
```

  85. ```
    - Multi-agent planning is permitted: pmagent may spin up multiple planning calls (Gemini/Codex instances) for decomposition tasks, each tracked with its own agent_run row. Context windows are large, but prompts must still cite SSOT docs; no theology, scripture exegesis, or gematria scoring is delegated to these tools.
```

  86. ```
    - Planning lane usage is opt-in per operator; CI remains hermetic (planning CLIs disabled unless explicitly allowed).
```

  87. ```
    - \*\*Runbooks\*\*: See `docs/runbooks/GEMINI_CLI.md` and `docs/runbooks/CODEX_CLI.md` for setup and usage details.
```

  88. ``
  89. `### LM Status Command`
  90. ``
  91. `- Command: `pmagent lm.status``
  92. `- Purpose: Show current LM configuration and local service health:`
  93. `  - Per-slot provider and model (local_agent, embedding, reranker, theology)`
  94. `  - Ollama health (local only)`
  95. `  - LM Studio/theology_lmstudio health (local only)`
  96. `- Notes:`
  97. `  - No LangChain/LangGraph; this is a thin status/introspection layer.`
  98. `  - All checks use localhost URLs (127.0.0.1); no internet calls.`
  99. ``
  100. `### System Status UI & TVs`
- **head_line_count**: `100`
- **error**: `null`
