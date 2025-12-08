# DSPy Training Examples for pmagent

Training data for DSPy reasoning programs (Phase 28+).

## Files

| File | Examples | Coverage |
|------|----------|----------|
| `dspy_synthetic_examples_1.jsonl` | 6 | SafeOPSDecision baseline |
| `dspy_synthetic_examples_2.jsonl` | 41 | All 4 programs |
| `dspy_synthetic_examples_3.jsonl` | 8 | Edge cases (all programs) |

**Total: 55 examples** in JSONL format (one JSON object per line).

## Reasoning Programs

1. **SafeOPSDecision** — Go/no-go for OPS work
2. **OPSBlockGenerator** — Drafts OPS blocks from PM goals
3. **GuardFailureInterpreter** — Diagnoses + remediates guard failures
4. **PhaseTransitionValidator** — Validates phase transitions

## DSPy Pipeline (per OA research)

```
interpret_request → load_context → plan_tools → call_lms → post_process
```

See `AGENTS.md` for full pipeline documentation and TODO items.

## Usage

These examples will be used with `dspy.BootstrapFewShot` to train pmagent reasoning programs.

## Related Documents

- [OA_REASONING_BRIDGE.md](../../docs/SSOT/oa/OA_REASONING_BRIDGE.md) — Schema definitions
- [OA_API_CONTRACT.md](../../docs/SSOT/oa/OA_API_CONTRACT.md) — Tool specifications
