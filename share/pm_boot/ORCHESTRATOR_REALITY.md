# Orchestrator Reality: Roles & Wiring

**Version**: 1.0  
**Purpose**: Define who does what in the Gemantria orchestration stack  
**Audience**: Orchestrator (you), OA, Cursor, and anyone confused about the architecture

---

## The Problem This Solves

**Before Phase 26**: Cursor sometimes acted like it had never met this project, even though we had AGENTS.md, EXECUTION_CONTRACT, DMS, and governance rules.

**Why**: The backend machinery exists, but enforcement wasn't hardened. Each new Cursor session could start "cold" and guess instead of following the mandatory boot sequence.

**This doc**: Clarifies exactly who does what, so we can stop the confusion.

---

## Core Roles

### 1. LM Studio (Inference Provider)

**What it is**: Local model server running Granite, BGE, and other models via OpenAI-compatible API.

**What it does**:
- Runs inference (embeddings, chat, reranking)
- Provides responses to prompts
- **That's it. LM Studio doesn't call tools, doesn't run commands, doesn't manage state.**

**What it does NOT do**:
- ❌ Call pmagent commands
- ❌ Execute shell commands
- ❌ Manage the kernel envelope
- ❌ Have "tools" or "tool belt"

**Interface**: HTTP API at `http://127.0.0.1:9994/v1` (or Ollama equivalent)

---

### 2. Orchestrator Assistant (OA)

**What it is**: The thinking layer that helps the human orchestrator understand project state and decide what to do next.

**What it does**:
- Reads kernel state via tools (calls `pmagent handoff boot-pm --json`)
- Uses LM Studio for inference to interpret/explain state
- Proposes concrete tasks for Cursor to execute
- Refuses forward work when kernel mode is DEGRADED
- Acts as advisor/interpreter, **never executes commands directly**

**What it does NOT do**:
- ❌ Run shell commands
- ❌ Edit files
- ❌ Execute migrations
- ❌ Make DB queries

**Tools OA should have**:
1. `get_kernel_status()` → calls `pmagent handoff status-handoff --json`
2. `get_pm_boot_envelope()` → calls `pmagent handoff boot-pm --json`
3. `read_share_surface(path)` → reads files from `share/`
4. `query_dms_hints(scope)` → queries `control.hint_registry`

**Boot sequence**:
1. Session starts
2. OA calls `get_pm_boot_envelope()`
3. OA explains kernel state to orchestrator
4. OA proposes next action based on mode (NORMAL vs DEGRADED)

**Spec**: `docs/SSOT/PHASE26_OA_BOOT_SPEC.md`

---

### 3. Cursor (Executor / OPS Agent)

**What it is**: The hands that run commands, edit files, and apply changes. That's me.

**What I do**:
- Execute shell commands
- Edit code files
- Run migrations
- Execute tests
- Follow EXECUTION_CONTRACT, DMS_QUERY_PROTOCOL, and governance rules

**What I do NOT do**:
- ❌ Decide strategy (that's OA or PM)
- ❌ Infer project state (I read kernel instead)
- ❌ Ignore governance rules

**Mandatory boot sequence (what I MUST do)**:
1. Before any destructive operation:
   - Call `pmagent handoff status-handoff --json`
   - Check kernel mode (NORMAL vs DEGRADED)
   - If DEGRADED: refuse normal work, ask for remediation scope
2. Before DB queries:
   - Run DB preflight check (`scripts/ops/preflight_db_check.py`)
3. Before any phase work:
   - Read `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json`
   - Verify current phase matches kernel

**Spec**: `docs/SSOT/PHASE26_OPS_BOOT_SPEC.md`, `docs/SSOT/EXECUTION_CONTRACT.md`

---

### 4. Orchestrator Console (UI)

**What it is**: The dashboard that shows kernel state, health, and next actions.

**What it does**:
- Displays kernel status (phase, branch, mode)
- Shows failing guards and remediation docs
- Lists next actions from boot envelope
- Auto-refreshes by calling pmagent commands

**What it does NOT do**:
- ❌ Execute commands
- ❌ Make decisions
- ❌ Require manual shell work from orchestrator

**Data sources**:
- `pmagent handoff status-handoff --json`
- `pmagent handoff boot-pm --json`
- `share/REALITY_GREEN_SUMMARY.json`
- `share/handoff/PM_KERNEL.json`

**Status**: Designed but not fully implemented (Console V2 scaffolding exists)

---

### 5. PM (Project Manager / Planning Agent)

**What it is**: Strategic decision-maker for phase planning and work prioritization.

**What it does**:
- Chooses next work items from MASTER_PLAN
- Defines phase boundaries
- Reviews and approves designs
- Issues 4-block instructions (Goal, Commands, Evidence, Next Gate)

**What it does NOT do**:
- ❌ Execute commands (delegates to Cursor)
- ❌ Write code (reviews Cursor's output)

**Interface**: Human orchestrator talks to PM, PM talks to Cursor

---

## The Correct Information Flow

### Normal Work Flow (Mode: NORMAL)

```
Orchestrator
    ↓ (talks to)
PM Agent
    ↓ (issues 4-block instructions)
Cursor
    ↓ (reads kernel first)
pmagent handoff status-handoff --json
    ↓ (gets envelope)
Kernel (PM_KERNEL.json + PM_BOOTSTRAP_STATE.json)
    ↓ (if NORMAL)
Cursor executes work
    ↓ (updates)
Share surfaces + DB
    ↓ (observed by)
OA (explains state back to orchestrator)
```

### Degraded Mode Flow (Mode: DEGRADED)

```
Cursor
    ↓ (reads kernel)
pmagent handoff status-handoff --json
    ↓ (returns)
{"degraded": true, "health": {"reality_green": false, "failed_checks": [...]}}
    ↓ (Cursor refuses normal work)
Cursor reports to PM: "Kernel says DEGRADED, need remediation scope"
    ↓
PM defines remediation scope
    ↓
Cursor executes ONLY remediation commands
```

---

## What "LM Studio Does Most of Cursor's Job" Actually Means

**The Goal**: Small local model (via LM Studio) handles most of Cursor's thinking.

**How it works**:
1. **OA uses LM Studio** to reason about kernel state
2. **OA proposes concrete actions** based on boot envelope
3. **Cursor executes** what OA proposes (not what Cursor guesses)

**What this is NOT**:
- ❌ LM Studio calling pmagent directly
- ❌ LM Studio running shell commands
- ❌ LM Studio "having tools"

**What this IS**:
- ✅ OA (as orchestration layer) calls pmagent
- ✅ OA uses LM Studio for inference/reasoning
- ✅ Cursor follows OA's instructions instead of guessing

---

## Why Cursor Still Gets Confused (And How We Fix It)

### Current State (Partial Enforcement)

**Problem**: Cursor CAN start a task without:
- Reading kernel
- Running `pmagent handoff status-handoff`
- Checking DB preflight
- Respecting Phase 26 specs

**Result**: Cursor sometimes acts like ordinary repo, not Gemantria with strict governance.

### What's Missing

1. **Mandatory boot checklist**:
   - No hardened "run this first before any work" enforcement
   - Boot sequence is documented but not automatic

2. **OA integration**:
   - OA doesn't yet have tool access to pmagent
   - OA can't auto-read kernel on session start

3. **Console integration**:
   - Console V2 exists but doesn't auto-call pmagent
   - Orchestrator still has to run commands manually

### The Fix (Next Work)

**Short term**:
1. Update Cursor's EXECUTION_CONTRACT to make boot sequence **non-optional**
2. Add pre-commit hook that runs `pmagent handoff status-handoff`
3. Make `make reality.green` check kernel health

**Medium term**:
1. Wire OA tools to call pmagent automatically
2. Update OA system prompt to **always** start with kernel envelope
3. Wire Console V2 to display kernel state automatically

**Long term**:
1. Pre-commit hooks enforce kernel preflight
2. Cursor wrapper commands that auto-run boot checks
3. Full "fail-closed" enforcement: can't start work without kernel check

---

## Decision Tree: Who Does What?

**Need inference / reasoning?** → LM Studio (via OA)

**Need to understand project state?** → OA (calls pmagent, reads kernel)

**Need to execute commands?** → Cursor (follows OA/PM instructions)

**Need to see status?** → Console (auto-displays kernel state)

**Need to plan work?** → PM (chooses from MASTER_PLAN)

**Need kernel data?** → pmagent commands (single source of truth)

---

## Related Documentation

- **Kernel Spec**: `docs/SSOT/PHASE26_HANDOFF_KERNEL.md`
- **OA Behavior**: `docs/SSOT/PHASE26_OA_BOOT_SPEC.md`
- **Cursor/OPS Behavior**: `docs/SSOT/PHASE26_OPS_BOOT_SPEC.md`
- **pmagent Boot Commands**: `docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md`
- **Execution Contract**: `docs/SSOT/EXECUTION_CONTRACT.md`
- **DMS Query Protocol**: `docs/SSOT/DMS_QUERY_PROTOCOL.md`

---

## TL;DR

- **LM Studio**: Inference only, no tools
- **OA**: Reasoner + tool user, calls pmagent, uses LM Studio for thinking
- **Cursor**: Executor, follows contracts, runs commands
- **Console**: UI, shows kernel state automatically
- **PM**: Strategist, plans work, instructs Cursor

**The problem**: Backend exists, enforcement doesn't. Cursor can still skip boot checks.

**The fix**: Make kernel boot checks **mandatory** via contracts, hooks, and OA/Console integration.
