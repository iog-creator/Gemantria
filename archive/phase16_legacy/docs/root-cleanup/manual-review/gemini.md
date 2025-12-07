# Gemini Agent Framework Map

This document provides a map of the Gemantria Agent Framework, synthesized from `AGENTS.md`, `docs/SSOT/AGENTS.md`, and `agents/example_enrich.py`.

## Core Mission & Priorities

- **Mission:** Build a deterministic, resumable LangGraph pipeline for verified gematria data and visualizations.
- **Priorities:**
    1.  **Correctness:** Code gematria > `bible_db` > LLM (metadata only).
    2.  **Determinism:** Content-hash identity, `uuidv7`, fixed seeds.
    3.  **Safety:** `bible_db` is read-only, parameterized SQL, fail-closed design.

## Agent Development Protocol

### 1. **Create Agent Logic:**
- Create a new Python file in the `/agents` directory (e.g., `agents/my_new_agent.py`).
- Implement the core logic of your agent.
- **Instrumentation:** Use the provided OTel decorators to instrument your agent for observability. Wrap LLM calls with `@span_llm` and tool/database calls with `@span_tool`, as demonstrated in `agents/example_enrich.py`.

### 2. **Define Agent in `AGENTS.md`:**
- Open the root `AGENTS.md` file.
- Add a new entry for your agent, detailing its purpose, models used, and its role in the pipeline.
- If your agent introduces new data schemas or contracts, create corresponding documents in `docs/SSOT/` and link them.

### 3. **Integrate into the Pipeline:**
- Add a `make` target in the `Makefile` for your agent (e.g., `make my_agent.run`).
- If part of the main data processing flow, add it to the LangGraph pipeline defined in `src/graph/graph.py`.
- Ensure your agent's operation is idempotent and resumable.

### 4. **Testing:**
- Write unit and integration tests for your agent in the `/tests` directory.
- Ensure tests cover both success and failure cases.
- Mock external services like databases and LLMs for hermetic testing.
- Aim for >= 98% test coverage.

### 5. **Documentation & Governance:**
- If your agent's logic changes, you **must** update the corresponding `AGENTS.md` file.
- Run `make agents.md.sync` to ensure documentation is not stale.

## Key Protocols & Contracts

- **Database Access:**
    - All database connections must use the centralized loaders in `scripts.config.env` or `src.gemantria.dsn`.
    - Direct `os.getenv()` for DSNs is forbidden.
    - The `bible_db` is strictly read-only.
- **Workflow:**
    - Follow the "small green PRs" model: branch, test-first, code, lint/test, commit, push, PR.
    - All code must be formatted with `ruff format` and linted with `ruff check`.
- **SSOT (Single Source of Truth):**
    - The `docs/SSOT/` directory contains all canonical schemas and API contracts.
    - All data exports must be validated against these schemas.
- **Observability:**
    - Agent operations are traced using OpenTelemetry.
    - Spans are written to `evidence/otel.spans.jsonl`.

## Example Agent (`example_enrich.py`)

This agent demonstrates the basic pattern for an enrichment agent:
- It takes a noun as input.
- It calls an LLM to get an "insight" (`call_llm`). This function is wrapped with `@span_llm`.
- It looks up the gematria value (`lookup_gematria`). This function is wrapped with `@span_tool`.
- It returns a dictionary containing the original text, the gematria value, and the LLM output.

This map should serve as a guide for understanding and extending the agentic capabilities of this repository.
