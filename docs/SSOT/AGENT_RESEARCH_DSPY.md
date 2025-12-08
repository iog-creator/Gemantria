# DSPy Agent Design Research Summary

## Source

Based on "Building a Robust and Reliable Agentic AI System with DSPy.pdf"

---

## Core Architecture

OA as DSPy pipeline with explicit module contracts:

```
interpret_request → load_context → plan_tools → call_lms → post_process
```

### Module Responsibilities

| Module | Input | Output |
|--------|-------|--------|
| `interpret_request` | user_msg, context | intent |
| `load_governed_context` | intent | facts (kernel+DMS+hints) |
| `plan_and_act` | intent, facts | draft_response, actions |
| `finalize_response` | draft_response, actions | assistant_message |

---

## Model Stack

Per research, recommended configuration:

| Role | Model | Notes |
|------|-------|-------|
| General reasoning | Granite 3.0 (MoE) | Low latency |
| Code/numeric | Nemotron 8-15B | GPU optimized |
| Theology | Christian-Bible-Expert-v2.0-12B | Existing slot |
| Teacher/evaluator | Grok | Via OpenRouter |

---

## DSPy Pipeline Stages

### Stage 1: Signatures
- `dspy.Signature` classes for each reasoning program
- Input/output contracts per OA_REASONING_BRIDGE.md

### Stage 2: Modules
- `dspy.Module` wrapping `dspy.ChainOfThought`
- Tool-use modules with schema validation

### Stage 3: Optimization
- `dspy.BootstrapFewShot` with teacher (Grok)
- Metric functions for automated tuning

---

## Integration Points

- **Training data**: `examples/dspy/*.jsonl` (55 examples)
- **Runtime bridge**: `pmagent/oa/reasoning_bridge.py`
- **Tools**: `pmagent/oa/tools.py` (7 read-only wrappers)

---

## Related SSOT Docs

- [PHASE27_D_DSPY_REASONING_OUTLINE](./PHASE27_D_DSPY_REASONING_OUTLINE.md)
- [OA_REASONING_BRIDGE](./oa/OA_REASONING_BRIDGE.md)
- [OA_API_CONTRACT](./oa/OA_API_CONTRACT.md)
