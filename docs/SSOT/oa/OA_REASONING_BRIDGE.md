# OA Reasoning Bridge Spec (Phase 27.F)

## 1. Overview and Purpose

This document defines the **Reasoning Bridge** — the architectural layer connecting the Orchestrator Assistant (OA) runtime to future DSPy reasoning programs (Phase 28).

**Scope (Phase 27.F):**
- Defines the **data contracts** (schemas) for exchanging state and results.
- Establishes the **interface** for invoking reasoning.
- Provides **scaffolding** implementation in `pmagent.oa.reasoning_bridge`.
- **Constraint:** No DSPy imports or runtime logic are present in this phase.

The bridge ensures that OA remains the **sovereign state manager** while delegating complex cognitive tasks to DSPy programs.

---

## 2. Reasoning Envelope Schema

The **Reasoning Envelope** is the immutable input payload provided to every DSPy program. It grants the program a "read-only view" of the universe at a specific moment.

### Schema: `ReasoningEnvelope`

| Field | Type | Description |
|-------|------|-------------|
| `envelope_id` | `str` (UUID) | Unique ID for this reasoning session. |
| `timestamp` | `str` (ISO8601) | Time of envelope creation. |
| `program_id` | `str` (Enum) | The DSPy program being invoked (e.g., `SafeOPSDecision`). |
| `goal` | `str` | The high-level objective or question driving this reasoning step. |
| `kernel_state_ref` | `KernelStateRef` | Pointers to authoritative kernel surfaces. |
| `oa_context` | `dict` | Usage context (from `share/oa/CONTEXT.json`). |
| `tools_allowed` | `list[str]` | Whitelist of `oa.*` tool IDs this program may use (see `OA_TOOLS_REGISTRY.md`). |

### Schema: `KernelStateRef`

A unified view of the kernel state, derived from standard SSOT surfaces.

| Field | Type | Source Surface |
|-------|------|----------------|
| `mode` | `str` | `kernel_status()` from `HANDOFF_KERNEL.json` |
| `bootstrap` | `dict` | `PM_BOOTSTRAP_STATE.json` |
| `ssot_index` | `dict` | `SSOT_SURFACE_V17.json` |
| `reality_summary` | `dict` | `REALITY_GREEN_SUMMARY.json` |
| `oa_state` | `dict` | `share/orchestrator_assistant/STATE.json` |

---

## 3. Reasoning Result Schema

The **Reasoning Result** is the structured output returned by a DSPy program. OA consumes this result to take concrete actions (e.g., executing a command, updating state, or escalating).

### Schema: `ReasoningResult`

| Field | Type | Description |
|-------|------|-------------|
| `envelope_id` | `str` (UUID) | ID of the input envelope. |
| `program_id` | `str` | The program that produced this result. |
| `status` | `str` (Enum) | `OK`, `DEGRADED`, `BLOCKED`, `FAILED`. |
| `decision` | `dict` | Program-specific payload (see below). |
| `rationale` | `str` | Chain-of-thought or explanation for the decision. |
| `tool_calls` | `list[dict]` | Log of `oa.*` tools invoked during reasoning. |
| `diagnostics` | `list[OADiagnostic]` | Diagnostic events detected (see `OA_DIAGNOSTICS_CATALOG.md`). |

---

## 4. Program-Specific Payloads

Each DSPy program (defined in `PHASE27_D_DSPY_REASONING_OUTLINE.md`) returns a specific structure in the `decision` field.

### 4.1 SafeOPSDecision
* **Goal:** Determine if it is safe to proceed with an OPS operation.
* **Decision Payload:** `SafeOPSDecisionResult`
  - `allowed_action`: `str` ("PROCEED", "ABORT", "WARN")
  - `safety_check_summary`: `str`

### 4.2 OPSBlockGenerator
* **Goal:** Generate a valid OPS block (atomic sequence of commands).
* **Decision Payload:** `OPSBlockGeneratorResult`
  - `ops_block`: `list[str]` (commands)
  - `complexity_score`: `int` (1-10)
  - `risk_analysis`: `str`

### 4.3 GuardFailureInterpreter
* **Goal:** Analyze why a guard failed and suggest remediation.
* **Decision Payload:** `GuardFailureInterpreterResult`
  - `root_cause`: `str`
  - `remediation_plan`: `str` (commands or manual fix)
  - `is_transient`: `bool`

### 4.4 PhaseTransitionValidator
* **Goal:** Verify if criteria for moving to the next phase are met.
* **Decision Payload:** `PhaseTransitionValidatorResult`
  - `transition_status`: `str` ("READY", "NOT_READY")
  - `missing_criteria`: `list[str]`

---

## 5. Constraints & Safety (Bridge Layer)

1. **Tool Mediation:**
   - Reasoning programs MUST NOT call shell commands directly.
   - They MUST only use `pmagent.oa.tools` wrappers exposed via `tools_allowed`.

2. **Read-Only Envelopes:**
   - The inputs (kernel state, context) are immutable copies. Reasoning cannot mutate the input objects to affect the system state directly.

3. **No Side Effects in Design:**
   - The bridge implementation in Phase 27.F is **scaffolding only**.
   - `run_reasoning_program()` acts as a NO-OP or mocks a response.
   - No external API calls (LLM) or heavy compute are permitted in 27.F.

4. **Kernel Health Check:**
   - If `reality_green` is `false` in the envelope, the bridge should Enforce **Diagnostic Mode** (only `GuardFailureInterpreter` allowed, others blocked) — *To be implemented in runtime logic Phase 28.*

---

## 6. Phase 28 Handoff

In **Phase 28**, we will:
1. Import `dspy`.
2. Implement the `run_reasoning_program` function to actually drive the DSPy signatures defined in `PHASE27_D_DSPY_REASONING_OUTLINE.md`.
3. Connect the `ReasoningEnvelope` to the DSPy `dspy.Example` or `dspy.Prediction` inputs.
4. Serialize DSPy outputs into the `ReasoningResult` schema.
