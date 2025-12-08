# GEMINI.md — Gemini Agent Framework Map

This document provides a map of the Gemantria Agent Framework, synthesized from `AGENTS.md` and the project's governance rules. It serves as the primary integration point for Gemini agents to understand their role, constraints, and workflows within the Gemantria project.

---

## ⚠️ MANDATORY CONVERSATION BOOT SEQUENCE (Rule 080)

**YOU MUST EXECUTE THIS SEQUENCE AT THE START OF EVERY CONVERSATION BEFORE ANY OTHER WORK.**

Failure to follow this sequence has caused repeated governance violations and system fragility. This is non-negotiable.

### Step 1: Kernel Health Check
```bash
make ops.kernel.check
```
**If this fails**: STOP. Enter NO-OP mode. Report failure to user.

### Step 2: Check System Mode
```bash
cat share/handoff/PM_KERNEL.json | jq '{mode, current_phase, branch}'
```
- If `mode == "DEGRADED"`: Only PM-approved remediation work allowed
- If `mode == "NORMAL"`: Proceed to Step 3

### Step 3: Verify Reality Green
```bash
make reality.green
```
**If any checks fail**: Report failures before proceeding. Do NOT assume passes.

### Step 4: Query DMS Before File Search (Rule 051/053/069)
Before searching files with grep/find, FIRST query the DMS:
```bash
# List all registered KB docs
pmagent kb registry list

# Filter by tag (e.g., dspy, governance, phase27)
pmagent kb registry by-tag --tag "dspy"

# Filter by subsystem (e.g., oa, pmagent, kernel)
pmagent kb registry by-subsystem --subsystem "oa"
```
The DMS (Document Management System) knows what docs exist and their importance.

### Step 5: Check Local AGENTS.md
If working in a specific directory, read its `AGENTS.md` first:
```bash
cat <working_directory>/AGENTS.md
```

### Boot Confirmation
After completing steps 1-3, state in your response:
> **Boot complete**: Kernel mode=`<mode>`, phase=`<phase>`, reality.green=`<pass/fail count>`

---

> [!CAUTION]
> **You do NOT have persistent codebase embeddings.** You must actively read docs and query DMS each session. Do not assume knowledge from previous conversations carries over.

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
- Create new Python files in appropriate directories (e.g., `pmagent/modules/`).
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
    - **Strictly use centralized loaders**: `scripts.config.env` or `pmagent.db.loader`.
    - **NEVER** use `os.getenv("GEMATRIA_DSN")` directly.
    - **Bible DB** is strictly READ-ONLY.
- **PM DMS Integration (Rule-053)**:
    - Query **Postgres DMS** BEFORE file searching.
    - Use `pmagent kb registry` and `control.mcp_tool_catalog`.
- **Orchestrator Output**:
    - Filter `dump_bash_state: command not found` noise from subprocess outputs.

## Artifact & Walkthrough Protocol (Rule 071)

**MANDATORY**: All phase completion walkthroughs and implementation evidence MUST be saved to the codebase, not just to the Gemini artifact directory.

### Walkthrough Location
- **Path**: `docs/SSOT/PHASE{XX}_IMPLEMENTATION_EVIDENCE.md`
- **Example**: `docs/SSOT/PHASE27BC_IMPLEMENTATION_EVIDENCE.md`
- **Pattern**: Follow existing phase docs in `docs/SSOT/PHASE*`

### Required Content
1. **Status & Branch**: Current state and git branch
2. **Commits**: Table of relevant commits with descriptions
3. **Changes Made**: New files, modified files, organized by component
4. **Health Evidence**: `reality.green` output, guard results
5. **Verification Commands**: How to reproduce/verify the work

### Workflow
1. Create walkthrough in artifact directory during work
2. **ALWAYS** copy final walkthrough to `docs/SSOT/PHASE{XX}_IMPLEMENTATION_EVIDENCE.md`
3. Commit the evidence file to the codebase
4. This ensures PM and future agents can access the evidence

## OPS Output Format (Rule 050)

**All OPS responses must follow the 4-block format:**

1. **Goal** — Single sentence stating the objective
2. **Commands** — Runnable shell commands (no prose between)
3. **Evidence to return** — What outputs to expect
4. **Next gate** — What happens after seeing evidence

**Local Gates Are Primary (Rule 050 §5.5):**
- Never say "waiting for CI" — local gates are the truth
- Run these before any push: `ruff format --check . && ruff check . && make book.smoke && make reality.green`
- CI is informational only, not blocking

---

## Agent Index (Key Subsystems)

The following `AGENTS.md` files define specific subsystem contracts:

- **Root Framework**: [`AGENTS.md`](./AGENTS.md)
- **AgentPM (Control Plane)**: [`pmagent/AGENTS.md`](./pmagent/AGENTS.md)
- **BibleScholar**: [`pmagent/biblescholar/AGENTS.md`](./pmagent/biblescholar/AGENTS.md)
- **Knowledge Base**: [`pmagent/kb/AGENTS.md`](./pmagent/kb/AGENTS.md)
- **Planning**: [`pmagent/plan/AGENTS.md`](./pmagent/plan/AGENTS.md)
- **Reality Check**: [`pmagent/reality/AGENTS.md`](./pmagent/reality/AGENTS.md)
- **DB Layer**: [`pmagent/db/AGENTS.md`](./pmagent/db/AGENTS.md)
- **LM Layer**: [`pmagent/lm/AGENTS.md`](./pmagent/lm/AGENTS.md)

*Note: This list is not exhaustive. Always check for a local `AGENTS.md` in your working directory.*
