# DSPy Training Examples for pmagent

This directory contains synthetic training examples for DSPy programs that will power the pmagent reasoning layer in Phase 28.

## Structure

- `dspy_synthetic_examples.jsonl` — 6 envelope/result pairs (original SafeOPSDecision examples)
- `dspy_synthetic_examples_2.jsonl` — 40 envelope/result pairs (all 4 program types)

**Format**: JSONL (one JSON object per line), compatible with DSPy's data loading.

## Reasoning Programs

| Program | Purpose |
|---------|---------|
| **SafeOPSDecision** | Determine if an OPS operation is safe to execute |
| **OPSBlockGenerator** | Generate valid OPS command blocks |
| **GuardFailureInterpreter** | Analyze guard failures and suggest remediation |
| **PhaseTransitionValidator** | Verify phase transition criteria are met |

## Example Schema

Each example follows the `ReasoningEnvelope → ReasoningResult` contract from `docs/SSOT/oa/OA_REASONING_BRIDGE.md`:

```json
{
  "envelope": {
    "envelope_id": "uuid",
    "program_id": "SafeOPSDecision",
    "goal": "...",
    "kernel_state_ref": { ... },
    "oa_context": { ... },
    "tools_allowed": ["oa.kernel_status", "oa.guard.run"]
  },
  "result": {
    "status": "OK|DEGRADED|BLOCKED|FAILED",
    "decision": { ... },
    "rationale": "Chain-of-thought explanation",
    "tool_calls": [ ... ],
    "diagnostics": [ ... ]
  }
}
```

## Usage

These examples will be used with `dspy.BootstrapFewShot` to train pmagent reasoning programs.

## Related Documents

- [OA_REASONING_BRIDGE.md](../../docs/SSOT/oa/OA_REASONING_BRIDGE.md) — Schema definitions
- [OA_API_CONTRACT.md](../../docs/SSOT/oa/OA_API_CONTRACT.md) — Tool specifications
