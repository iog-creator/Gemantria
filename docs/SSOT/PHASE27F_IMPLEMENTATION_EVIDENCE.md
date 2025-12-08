# Phase 27.F Implementation Evidence: OA↔DSPy Bridge Scaffolding

## Status

✅ **COMPLETE** — Scaffolding and design only. No DSPy runtime.

- **Bridge Spec**: `docs/SSOT/oa/OA_REASONING_BRIDGE.md`
- **Scaffolding**: `pmagent/oa/reasoning_bridge.py`
- **Contract Updated**: `docs/SSOT/oa/OA_API_CONTRACT.md`
- **State Metadata**: In `share/orchestrator_assistant/STATE.json` (`reasoning_bridge` key)

## Summary

Phase 27.F established the architectural bridge for future DSPy reasoning programs (Phase 28). We defined the "Reasoning Envelope" (read-only input) and "Reasoning Result" (structured output) schemas.

**Key Deliverables:**

1.  **Reasoning Envelope**: A unified view of the kernel state (`bootstrap`, `ssot`, `reality`, `oa_state`) plus context and tool whitelist.
2.  **Scaffolding Module**: A `TypedDict`-based Python module defining the data structures. Functions are stubs.
3.  **Coherence Guard**: `scripts/guards/guard_oa_reasoning_bridge.py` ensures the SSOT doc, code definitions, and OA state metadata remain in sync.

## Schemas

### Envelope (Abstract)
```python
class ReasoningEnvelope(TypedDict):
    program_id: str
    goal: str
    kernel_state_ref: KernelStateRef
    oa_context: dict
    tools_allowed: List[str]
```

### Supported Programs (Design)
1.  **SafeOPSDecision**: GO/NO-GO for operations.
2.  **OPSBlockGenerator**: Drafts command sequences.
3.  **GuardFailureInterpreter**: Analyzes failures and suggests fixes.
4.  **PhaseTransitionValidator**: Checks phase exit criteria.

## Safety & Constraints
- **No DSPy Imports**: The scaffold module uses only standard library types.
- **Read-Only**: The bridge does not mutate kernel state.
- **Tool Mediation**: Programs must use `oa.*` tools via the `pmagent.oa.tools` wrapper (implemented in 27.E).

## Verification
- `make reality.green` passes (18/18).
- `guard_oa_reasoning_bridge.py` passes.
- OA state contains `reasoning_bridge` metadata.
