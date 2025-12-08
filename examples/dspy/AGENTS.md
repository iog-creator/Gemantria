# examples/dspy AGENTS.md — DSPy Training Data Directory

## Directory Purpose

Training data for DSPy reasoning programs powering pmagent OA (Phase 28+).

---

## DSPy Pipeline Stages & Example Types

Per the DSPy research doc and OA architecture, OA is a **pipeline of modules**:

```
interpret_request → load_context → plan_tools → call_lms → post_process
```

Each stage needs different training data:

### Stage 1: Signature Examples (Envelope→Result)
**Current focus.** Input/output pairs for the 4 reasoning programs.

| File | Count | Programs |
|------|-------|----------|
| `dspy_synthetic_examples_1.jsonl` | 6 | SafeOPSDecision |
| `dspy_synthetic_examples_2.jsonl` | 41 | All 4 programs |
| `dspy_synthetic_examples_3.jsonl` | 8 | Edge cases (all programs) |

### Stage 2: Evaluation Examples (TODO)
For `dspy.BootstrapFewShot` optimizer. Same structure + quality labels:
- Decision correctness score
- Rationale clarity score  
- Required guards present (bool)

### Stage 3: Few-Shot Seeds (TODO)
Hand-curated "golden" examples (2-3 per program) for initial prompting before compilation.

### Stage 4: Module-Level Data (TODO)
Per the OA research, we need examples for individual DSPy modules:
- `interpret_request`: user_msg → intent
- `load_governed_context`: intent → facts (kernel+DMS+hints)
- `plan_and_act`: intent,facts → draft_response,actions
- `finalize_response`: draft → assistant_message

---

## Reasoning Programs

| Program | Purpose | Current Examples |
|---------|---------|------------------|
| SafeOPSDecision | Go/no-go for OPS work | ✅ 20+ |
| OPSBlockGenerator | Draft executable OPS blocks | ✅ 10+ |
| GuardFailureInterpreter | Diagnose + remediate guard failures | ✅ 12+ |
| PhaseTransitionValidator | Validate phase transitions | ✅ 10+ |

---

## Contracts

1. **JSONL Format**: One JSON object per line
2. **envelope_id**: Unique UUID per example
3. **JSON Literals Only**: `true`/`false`/`null` (not Python)
4. **DMS Tracking**: Run `make housekeeping` after adding files

---

## Related Docs (DMS-Tracked)

- `docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md` — Program signatures
- `docs/SSOT/oa/OA_REASONING_BRIDGE.md` — Envelope/Result schemas
- `docs/Building a Robust and Reliable Agentic AI System with DSPy.pdf` — Architecture guide
