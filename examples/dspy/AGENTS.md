# examples/dspy AGENTS.md — DSPy Training Examples Directory

## Directory Purpose

This directory contains training data for DSPy reasoning programs that power pmagent in Phase 28+.

---

## Data Types Required

Per the DSPy pipeline, we need **three categories** of training data:

### 1. Signature Examples (Input/Output Pairs)
**Used by:** `dspy.Signature`, `dspy.ChainOfThought`, `dspy.Predict`

Format: JSONL with `{"envelope": {...}, "result": {...}}`

Current files:
- `dspy_synthetic_examples.jsonl` — 6 SafeOPSDecision examples
- `dspy_synthetic_examples_2.jsonl` — 40 examples across all 4 program types

### 2. Metric Functions (Validation Data)
**Used by:** `dspy.BootstrapFewShot` optimizer

These examples need explicit quality labels for the optimizer to bootstrap:
- Correct decision (GO/NO_GO/CONDITIONAL)
- Rationale quality score (0.0-1.0)
- Required guards present

**TODO:** Add `dspy_evaluation_examples.jsonl` with quality labels

### 3. Few-Shot Seed Examples (High-Quality Curated)
**Used by:** Initial prompting before compilation

These are hand-curated, high-quality examples that demonstrate ideal outputs:
- 2-3 examples per reasoning program
- Carefully written rationales
- Cover edge cases

**TODO:** Add `dspy_seed_examples.jsonl` with curated seeds

---

## Program-Specific Data

| Program | Current Examples | Status |
|---------|-----------------|--------|
| SafeOPSDecision | 10+ | ✅ Good coverage |
| OPSBlockGenerator | 10+ | ✅ Good coverage |
| GuardFailureInterpreter | 10+ | ✅ Good coverage |
| PhaseTransitionValidator | 10+ | ✅ Good coverage |

---

## Contracts

1. **JSONL Format Required**: One JSON object per line for DSPy compatibility
2. **envelope_id Must Be Unique**: Used to match envelope/result pairs
3. **No Python Literals**: Use `true`/`false`/`null`, not `True`/`False`/`None`
4. **Compact JSON**: Use `separators=(',', ':')` for disk efficiency

---

## Related Documents

- [PHASE27_D_DSPY_REASONING_OUTLINE](../../docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md) — Program signatures
- [OA_REASONING_BRIDGE](../../docs/SSOT/oa/OA_REASONING_BRIDGE.md) — Envelope/Result schemas
- [OA_API_CONTRACT](../../docs/SSOT/oa/OA_API_CONTRACT.md) — Tool specifications

---

## Maintenance

- **DMS Integration**: Files here are tracked by DMS after commit
- **Validation**: Run `python -c "import json; [json.loads(l) for l in open('<file>')]"` to validate JSONL
- **Updates**: Add examples as real scenarios emerge from PM/Cursor work
