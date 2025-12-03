# GEMINI.md — Gemini Agent Framework Map

This document provides a map of the Gemantria Agent Framework, synthesized from `AGENTS.md` and the project's governance rules. It serves as the primary integration point for Gemini agents to understand their role, constraints, and workflows within the Gemantria project.

## Core Mission & Priorities

(Source: `AGENTS.md`)

- **Mission**: Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.
- **Priorities**:
    1.  **Correctness**: **Code gematria > bible_db > LLM (LLM = metadata only)**.
    2.  **Determinism**: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.
    3.  **Safety**: **bible_db is READ-ONLY**; parameterized SQL only; **fail-closed if <50 nouns** (ALLOW_PARTIAL=1 is explicit).

## Rule 070: Gotchas Check (Mandatory)

**Gemini Persona**: You are opinionated. You do not allow the orchestrator to make stupid errors. You MUST perform a "Gotchas Check" at the beginning and end of every workflow.

### 1. Pre-Work Gotchas Check (Beginning)
**Before starting any work**, ask: "What are the potential gotchas, edge cases, design inconsistencies, integration issues, or hidden dependencies?"

**Required Actions**:
1.  **Search for known issues**: TODOs, FIXMEs, known bugs.
2.  **Review dependencies**: What depends on this? What does this depend on?
3.  **Check integration points**: How does this fit with existing systems?
4.  **Document findings**: List them in your response.

### 2. Post-Work Gotchas Check (End)
**After completing work**, ask: "What gotchas did I introduce or miss?"

**Required Actions**:
1.  **Review changes**: Did I break assumptions?
2.  **Verify integration**: Do connections still work?
3.  **Check for regressions**: Any breaking changes?
4.  **Document gaps**: TODOs left behind, known limitations.

## Agent Development Protocol

### 1. Create Agent Logic
- Create new Python files in appropriate directories (e.g., `agentpm/modules/`).
- **Instrumentation**: Use OTel decorators (`@span_llm`, `@span_tool`) for observability.

### 2. Define in `AGENTS.md`
- Update the local `AGENTS.md` in the directory where you are working.
- If a new directory is created, create a new `AGENTS.md`.
- **Sync**: Run `make agents.md.sync` to ensure documentation is not stale.

### 3. Integrate & Test
- **Small Green PRs**: Branch -> Test -> Code -> Lint/Test -> Commit -> Push -> PR.
- **Gates**: `ruff format`, `ruff check`, `make book.smoke`, `make reality.green`.
- **Coverage**: Aim for ≥98% test coverage.

## Key Protocols & Contracts

- **Database Access**:
    - **Strictly use centralized loaders**: `scripts.config.env` or `agentpm.db.loader`.
    - **NEVER** use `os.getenv("GEMATRIA_DSN")` directly.
    - **Bible DB** is strictly READ-ONLY.
- **PM DMS Integration (Rule-053)**:
    - Query **Postgres DMS** BEFORE file searching.
    - Use `pmagent kb registry` and `control.mcp_tool_catalog`.
- **Orchestrator Output**:
    - Filter `dump_bash_state: command not found` noise from subprocess outputs.

## Agent Index (Key Subsystems)

The following `AGENTS.md` files define specific subsystem contracts:

- **Root Framework**: [`AGENTS.md`](./AGENTS.md)
- **AgentPM (Control Plane)**: [`agentpm/AGENTS.md`](./agentpm/AGENTS.md)
- **BibleScholar**: [`agentpm/biblescholar/AGENTS.md`](./agentpm/biblescholar/AGENTS.md)
- **Knowledge Base**: [`agentpm/kb/AGENTS.md`](./agentpm/kb/AGENTS.md)
- **Planning**: [`agentpm/plan/AGENTS.md`](./agentpm/plan/AGENTS.md)
- **Reality Check**: [`agentpm/reality/AGENTS.md`](./agentpm/reality/AGENTS.md)
- **DB Layer**: [`agentpm/db/AGENTS.md`](./agentpm/db/AGENTS.md)
- **LM Layer**: [`agentpm/lm/AGENTS.md`](./agentpm/lm/AGENTS.md)

*Note: This list is not exhaustive. Always check for a local `AGENTS.md` in your working directory.*
