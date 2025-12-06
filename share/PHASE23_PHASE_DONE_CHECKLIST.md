# Phase 23.3 — Phase-DONE Checklist

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Ensure hints, envelopes, AGENTS.md sync, CI/hooks, and operator documentation are
integral parts of the workflow for every new phase — not afterthoughts.

---

## Detection Strategy

We do **not** auto-detect new tools from git diffs.

Instead, each phase that introduces new tools/surfaces must explicitly list them in its
phase docs (e.g., `share/PHASENN_INDEX.md` under "New Tools" / "New Surfaces").

The guard uses those docs as its input.

---

## Hint Scope (What Requires a Hint)

A hint is **required** when a tool / script / command is:

1. Directly invoked by operators (CLI, `make`, or documented workflows), or
2. Intended to be called by pmagent/tiny models via envelopes, or
3. Part of governance / health / stress harness.

Internal helpers and private modules do **not** require hints.

---

## Checklist for New Tools

- [ ] Relevant AGENTS.md updated
- [ ] Hint exists (DMS registry or docs/hints/)
- [ ] Envelope integration (if tool-callable by AI)
- [ ] CI/Make target exists
- [ ] Operator snippet in phase docs

## Checklist for New Surfaces

- [ ] JSON/MD file exists under share/
- [ ] VIEW_MODEL.json updated
- [ ] check_console_v2.py validates path
- [ ] Hint explains where surface fits

## Checklist for Stress Scenarios

- [ ] Scenario documented under share/PHASENN_*
- [ ] Reversible (can restore to healthy state)
- [ ] Hint describes failure pattern

---

## Enforcement Posture (Phase 23)

- `scripts/guards/guard_phase_done.py` supports `--mode HINT|STRICT`
- During Phase 23: **HINT mode only** (warns but doesn't block)
- STRICT mode deferred to future governance phase

## Guard Command

```bash
make PHASE=23 MODE=HINT phase.done.check
```
