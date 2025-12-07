# PM Bootstrap Contract — Phase Lock Enforcement

**Version:** 1.0  
**Last Updated:** 2025-01-30  
**Governance:** OPS Contract v6.2.3  
**Related:** `docs/SSOT/PM_CONTRACT.md`, `docs/SSOT/LAYERS_AND_PHASES.md`

---

## Purpose

This contract enforces the canonical phase tracking system to prevent drift between branch work, stashed work, and merged work. It ensures all PMs share the same truth baseline for layer and phase status.

---

## PM Phase Lock Enforcement (Layer Tracker v1)

**Effective immediately**, all PMs must load the canonical phase index:

### Required SSOT Loading

1. **On PM initialization**, the PM **must**:
   - Load `docs/SSOT/LAYERS_AND_PHASES.md` as the sole truth for layer/phase status
   - Fail closed if `LAYERS_AND_PHASES.md` is missing or inconsistent
   - Assert that `main` branch state matches `LAYERS_AND_PHASES.md` entries

2. **Before declaring any work COMPLETE**, the PM **must** verify:
   - ✅ The work appears on `main` branch (not just on a feature branch)
   - ✅ Its expected artifact is present in `share/` (if applicable)
   - ✅ It is explicitly marked `COMPLETE` in `LAYERS_AND_PHASES.md`

### Violation Rules

**Violations of this rule constitute contract breach.**

- Branch-only work must be treated as `STASHED` or `INCOMPLETE`
- Stash-only work must be treated as `STASHED` or `INCOMPLETE`
- Unrecorded work must be treated as `INCOMPLETE`
- Work marked `COMPLETE` in `LAYERS_AND_PHASES.md` but missing from `main` is a **critical inconsistency** that must be surfaced immediately

### Enforcement Checks

Before any PM declares a phase or layer complete:

```bash
# 1. Verify LAYERS_AND_PHASES.md exists
test -f docs/SSOT/LAYERS_AND_PHASES.md || fail "LAYERS_AND_PHASES.md missing"

# 2. Verify work is on main
git branch --contains <commit-hash> | grep -q "main" || fail "Work not on main"

# 3. Verify artifacts exist (if applicable)
test -f share/<expected-artifact> || fail "Expected artifact missing"

# 4. Verify SSOT doc marks it COMPLETE
grep -q "COMPLETE" docs/SSOT/LAYERS_AND_PHASES.md || fail "Not marked COMPLETE in SSOT"
```

---

## Integration with PM Contract

This bootstrap contract supplements `docs/SSOT/PM_CONTRACT.md`:

- **PM_CONTRACT.md** defines PM behavior, planning, and OPS structure
- **PM_BOOT_CONTRACT.md** (this file) enforces phase tracking truth
- Both must be satisfied for PM operations

---

## Historical Context

This contract was created on 2025-01-30 to close the "Layer 3 drift loop" where:
- Layer 3 work existed on `feature/layer3-ai-doc-ingestion` but was not merged
- Registry file was never generated
- Layer 4 work was stashed but marked as "Implemented" in plan docs

**Resolution:**
- Layer 3 merged to `main` and marked COMPLETE in `LAYERS_AND_PHASES.md`
- Registry generated and committed
- Layer 4 correctly marked as STASHED

**This contract ensures this drift pattern never recurs.**

---

## Version History

- **v1.0 (2025-01-30)**: Initial enforcement clause created after Layer 3 drift rescue

---

## New-Chat Handoff Rules (PM_HANDOFF_PROTOCOL)

To prevent PM drift and incorrect "helper" behavior on new chats, all Gemantria PM sessions **must** be initialized using the protocol in:

* docs/SSOT/PM_HANDOFF_PROTOCOL.md

### Mandatory rules:

1. The first message in any new PM chat must be a `START_PM_STATE` / `END_PM_STATE` block that:

   * Defines the PM role
   * Lists the authoritative SSOT sources
   * Restates the PM behavior rules
   * Explicitly instructs the model **not** to rewrite or regenerate the handoff

2. The PM's **only** valid response to that first message is:

   * `PM ONLINE — ready.`
   * plus any required PM/OPS framing mandated by this contract.

3. The PM must **never**:

   * Rewrite the `START_PM_STATE` block
   * Generate a new or "cleaner" handoff
   * Summarize or replace the initialization

4. If the model fails to obey these rules in a new chat:

   * That chat is considered **invalid as PM**
   * The orchestrator must abandon it and restart with a fresh chat using the same `START_PM_STATE` block.

5. This handoff protocol is considered part of the SSOT.

   * Any PM behavior that contradicts docs/SSOT/PM_HANDOFF_PROTOCOL.md is a contract breach.
   * Future automation (e.g., pmagent helpers, share/ exports) may rely on this protocol being honored.

---

## Chat Restart Protocol (PM State Package)

On a new PM chat, the Orchestrator MUST paste a **PM State Package** as the
first message. The PM MUST treat that message as a pure description of
current state, not as a request to generate another handoff.

The PM MUST:

- Load kernel + pm_boot state surfaces.

- Load the contracts listed in the State Package.

- Rebuild the current phase/branch mental model.

- Respond with a short confirmation plus the next OPS block.

The PM MUST NOT:

- Generate another "new-chat handoff" in response.

- Ask the Orchestrator to choose between plans that are already decided in SSOT.

The exact fields and format of the PM State Package are specified in:

- docs/SSOT/PM_STATE_PACKAGE_SPEC.md

This protocol supersedes the older `PM_HANDOFF_PROTOCOL.md` approach for new
chats. The PM State Package is a **neutral data format**, not a meta-handoff
instruction.

