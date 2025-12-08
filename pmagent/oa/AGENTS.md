# pmagent/oa — Orchestrator Assistant Module

## Directory Purpose

This module provides the **Orchestrator Assistant (OA) runtime** —
a read-only kernel consumer that normalizes kernel surfaces for Console v2 and future DSPy reasoning programs.

## Key Components

### state.py
- Builds and writes kernel-aligned OA state snapshots
- Reads: `PM_BOOTSTRAP_STATE.json`, `SSOT_SURFACE_V17.json`, `REALITY_GREEN_SUMMARY.json`
- Writes: `share/orchestrator_assistant/STATE.json`
- Exposes `oa_tools` section for DSPy program tool discovery

### tools.py (Phase 27.E Batch 3)
- Thin, typed wrappers for pmagent commands OA is allowed to invoke
- All functions are **read-only** (no git, DB, or surface writes)
- Tools correspond 1:1 with entries in `docs/SSOT/oa/OA_TOOLS_REGISTRY.md`
- **No DSPy imports** — pure Python for decoupling

### dspy_signatures.py (Phase 28)
- DSPy Signature classes for 4 reasoning programs
- Optional dspy import — falls back gracefully if not installed
- `create_module(program_id)` factory for DSPy Modules
- Training data: `examples/dspy/*.jsonl`

### reasoning_bridge.py (Phase 27.F + 28)
- Types: `ReasoningEnvelope`, `ReasoningResult`, `KernelStateRef`
- `build_envelope()` — creates immutable input for DSPy programs
- `run_reasoning_program()` — executes DSPy signature with envelope

## OA Tools Interface

| Tool ID | Function | Purpose |
|---------|----------|---------|
| `oa.kernel_status` | `kernel_status()` | Get kernel mode, health, interpretation |
| `oa.reality_check` | `reality_check()` | Get normalized reality check results |
| `oa.guard.run` | `run_guard(name)` | Run a specific guard script |
| `oa.bootstrap_state` | `get_bootstrap_state()` | Load PM_BOOTSTRAP_STATE.json |
| `oa.ssot_surface` | `get_ssot_surface()` | Load SSOT_SURFACE_V17.json |
| `oa.reality_summary` | `get_reality_summary()` | Load REALITY_GREEN_SUMMARY.json |
| `oa.handoff_kernel` | `get_handoff_kernel()` | Load HANDOFF_KERNEL.json |

## Safety Constraints

- OA is **read-only** — never modifies kernel surfaces directly
- OA does not run arbitrary shell commands
- All tool invocations go via `pmagent.oa.tools` wrappers
- DSPy programs (Phase 28) will consume these tools as their execution substrate

## Related Documents

- `docs/SSOT/oa/OA_TOOLS_REGISTRY.md` — Complete tool specifications
- `docs/SSOT/oa/OA_API_CONTRACT.md` — OA entrypoints and I/O
- `docs/SSOT/oa/OA_DATA_MODEL.md` — Schema definitions
- `docs/SSOT/PHASE27_B_OA_RUNTIME.md` — Boot sequence spec
- `docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md` — DSPy program signatures
