# GPT Reference Guide - Gemantria Project Files

This guide explains the curated files available for GPT analysis of the Gemantria project. **Note**: For GPT PM context rebuild, see `docs/handoff/GPT_PM_CONTEXT_REBUILD.md` which consolidates project overview, history, and operational context.

## Core Project Documentation

**AGENTS.md** - Agent framework and operational contracts. Defines how automated agents work, their responsibilities, and governance rules.

**GEMATRIA_MASTER_REFERENCE.md** - Complete project master reference (1,183 lines). Contains all project details, architecture, agent contracts, rules, schemas, and operational procedures.

**MASTER_PLAN.md** - High-level project roadmap and goals. Strategic vision and phase planning.

**RULES_INDEX.md** - Complete index of all project rules. Governance framework with 61+ numbered rules for compliance.

## Configuration & Setup

**env_example.txt** - Environment variable template. Shows all required configuration variables.

**pyproject.toml** - Python project configuration. Dependencies, build settings, and tool configurations.

**pytest.ini** - Test configuration. How tests are run and configured.

**Makefile** - Build and automation targets. All available `make` commands for development, testing, and deployment.

## Schemas & Data Structures

**ai-nouns.schema.json** - Schema for AI-generated noun data. Defines structure of enriched concept data.

**graph.schema.json** - Schema for semantic network data. Defines node/edge structure for concept graphs.

**graph-patterns.schema.json** - Schema for graph pattern analysis. Community detection and centrality metrics.

**graph-stats.schema.json** - Schema for graph statistics. Network health and performance metrics.

**graph_stats.head.json** - Sample graph statistics data. Real example of graph analysis output.

## Documentation

**README.md** - Project overview and quick start. Basic introduction and setup instructions.

**README_FULL.md** - Comprehensive project documentation. Detailed guides and references.

**CHANGELOG.md** - Version history and changes. What changed in each release.

**RELEASES.md** - Release notes and deployment info. Version-specific release information.

## Development Workflow

**pull_request_template.md** - PR template requirements. What must be included in pull requests.

**pre-commit-config.yaml** - Code quality hooks. Automated checks that run before commits.

**SHARE_MANIFEST.json** - File sharing configuration. Defines which files are shared and how.

## Usage Guidelines for GPT

1. **Start with GEMATRIA_MASTER_REFERENCE.md** for complete project understanding
2. **Reference AGENTS.md** for operational procedures and agent contracts
3. **Check RULES_INDEX.md** for governance compliance requirements
4. **Use schemas** to understand data structures and validation rules
5. **Review Makefile** for available automation commands
6. **Check env_example.txt** for configuration requirements

## File Limits

This curated set of files stays within GPT's 22-file upload limit while providing comprehensive project understanding. The GPT PM Context Rebuild document (`docs/handoff/GPT_PM_CONTEXT_REBUILD.md`) consolidates several files (README, README_FULL, GEMATRIA_MASTER_REFERENCE) to reduce redundancy.

## GPT System Prompt Requirements

**Role Clarification:**
- **GPT = Project Manager (PM)**: Plans, decides, and provides instructions. Does NOT execute commands.
- **Cursor = Executor**: Reads GPT's instructions and runs the actual commands/tool calls.
- **Human = Orchestrator**: Coordinates the work, learns as we go, and needs clear explanations of what's happening and why.

**Session Initialization (MANDATORY):**
```bash
cd /home/mccoy/Projects/Gemantria.v2
source activate_venv.sh
make ssot.verify
```

**Validation Checklist:**
- ✅ Virtual environment active (.venv)
- ✅ Environment variables loaded
- ✅ Governance docs present (AGENTS.md, RULES_INDEX.md, GEMATRIA_MASTER_REFERENCE.md)
- ✅ Quality SSOT verified (ruff checks pass)
- ✅ Database accessible (PostgreSQL gematria and bible_db) - **Note**: Scripts handle DB unavailability gracefully (hermetic behavior per Rule 046)
- ✅ Share folder curated (files under 22-file GPT limit, see SHARE_MANIFEST.json for current count)

**Response Protocol (Two-Part Format):**
1. **Code Box for Cursor** (instructions Cursor will execute):
   - **Goal** — One sentence describing objective
   - **Commands** — Exact shell commands, top to bottom (for Cursor to execute)
   - **Evidence to return** — Which outputs Cursor should show
   - **Next gate** — What happens once evidence returned
2. **Tutor Notes** (outside the box, for the human orchestrator):
   - **Educational and explanatory**: Teach what's happening, not just summarize
   - **Define acronyms and terms**: Don't assume knowledge (e.g., "DSN = Database connection string")
   - **Explain WHY, not just WHAT**: Help the orchestrator understand the reasoning
   - **Plain English**: Avoid jargon; if you must use technical terms, explain them
   - **Help them learn**: The orchestrator knows enough to break things; guide them safely

**Tool Priority (for Cursor to use):**
1. local+gh (git, make, gh pr)
2. codex (if available, else "Codex disabled (401)")
3. gemini/mcp (for long docs)

## Hermetic Behavior (DB/Service Availability)

**Rule 046**: Hermetic CI Fallbacks - Scripts must handle missing/unavailable databases gracefully:
- DB-dependent operations check availability first
- Emit HINTs (not errors) when DB unavailable
- Housekeeping passes even when DB unavailable
- Per AGENTS.md: "If DB/services down → 'correct hermetic behavior.'"

**Example**: `governance_tracker.py` checks DB availability, emits HINTs, and returns success when DB unavailable, allowing `make housekeeping` to pass.

## LM Studio & Local Model Configuration

This system uses LM Studio as the default inference provider (`INFERENCE_PROVIDER=lmstudio`). The following environment variables control how local models are selected:

- **`INFERENCE_PROVIDER`** – Inference provider selector (default: `lmstudio`)
- **`OPENAI_BASE_URL`** – Base URL for LM Studio's OpenAI-compatible API (default: `http://127.0.0.1:9994/v1`)
- **`EMBEDDING_MODEL`** – General embedding model (e.g., `text-embedding-bge-m3`)  
- **`THEOLOGY_MODEL`** – Christian/theology reasoning model (e.g., `christian-bible-expert-v2.0-12b`)  
- **`LOCAL_AGENT_MODEL`** – Local agent/workflow model (e.g., `qwen/qwen3-8b`)
- **`MATH_MODEL`** – Optional math-heavy model for numeric verification
- **`RERANKER_MODEL`** – Optional reranker model for post-processing
- **`AUTO_START_MCP_SSE`** – Auto-start MCP SSE server during bring-up (default: `0`)

All LM configuration is centralized in `scripts/config/env.py` via `get_lm_model_config()`.

**Legacy Support (Deprecated):**
- `LM_EMBED_MODEL` → Use `EMBEDDING_MODEL` instead (will be removed in Phase-8)
- `QWEN_RERANKER_MODEL` → Use `RERANKER_MODEL` instead (will be removed in Phase-8)

### LM Studio Model Discovery

Use the discovery helper to list available LM Studio models and validate configuration:

```bash
python -m scripts.lm_models_ls
```

This command calls the LM Studio `/v1/models` endpoint (via `OPENAI_BASE_URL`) and verifies that `EMBEDDING_MODEL`, `THEOLOGY_MODEL`, `LOCAL_AGENT_MODEL`, and `RERANKER_MODEL` exist.

### OPS Command Ledger (v0)

Successful OPS command bundles can be recorded in the OPS Command Ledger:

- File: `share/ops_command_ledger.jsonl`
- Helper: `scripts/ops_ledger.append_entry()`

Future phases may mine this ledger for reusable command sequences.

## Governance Reference

**ADR-058**: GPT System Prompt Requirements as Operational Governance - Establishes GPT system prompt requirements as part of the operational governance framework.

**Rule 046**: Hermetic CI Fallbacks - Defines graceful handling of unavailable services/databases.
