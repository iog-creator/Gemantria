# PM Handoff Protocol — Canonical SSOT

## 1. Purpose

This document defines the **official boot protocol** for any new PM chat instance in Gemantria.

Phase 24 introduced deterministic machine surfaces:

- `share/PM_BOOTSTRAP_STATE.json`
- `share/HANDOFF_KERNEL.json`

These two files **replace all prior “human handoff” instructions**.  
A new PM instance must **derive the entire system state from these surfaces**, not from memory, past chats, or assumptions.

This protocol ensures:

- No “drift” between chats
- No dependency on previous conversation history
- Reproducible initialization for PM, OA, and Cursor


---

## 2. Minimal Boot Surfaces

A new PM instance **must read these surfaces first**, *before reading any other file*:

1. **`share/HANDOFF_KERNEL.json`**  
   - Contains:  
     - `current_phase`  
     - `last_completed_phase`  
     - `branch`  
     - Full health block from `reality.green`  
     - Kernel-level metadata and references to other surfaces

2. **`share/PM_BOOTSTRAP_STATE.json`**  
   - Contains:  
     - Discovered phases  
     - Phase index surfaces  
     - PM-facing metadata  
     - Structural repo information

3. (Conditional) **`share/REALITY_GREEN_SUMMARY.json`**  
   - A detailed breakdown of checks  
   - Only required if kernel reports degraded health


---

## 3. New PM Chat Boot Sequence

Follow these steps *in order*.  
This sequence is deterministic and mandatory.

### **Step 1 — Load HANDOFF_KERNEL.json**

Extract:

- `current_phase`  
- `branch`  
- `health.reality_green`  
- `health.checks`  
- `required_surfaces`  

If `reality_green == false`, the system is in **degraded mode** and PM must follow the failure path (see Section 4).

---

### **Step 2 — Load PM_BOOTSTRAP_STATE.json**

Confirm:

- `meta.current_phase` matches kernel’s `current_phase`
- Surfaces listed in `phases` map exist
- No contradictions with kernel metadata

---

### **Step 3 — Validate Minimal Consistency**

A new PM instance must verify:

- Kernel and Bootstrap **agree on the phase**
- Kernel health is not contradictory  
  (e.g., cannot claim green while backup missing)
- All `required_surfaces` exist on disk

If inconsistent → go to Failure Mode.

---

### **Step 4 — Load Phase Docs On Demand**

PM should NOT preload the entire SSOT.  
Instead:

- Only load `docs/SSOT/PHASENN_INDEX.md` when needed.
- For active phase work, load the relevant `PHASENN_*` docs dynamically.

This keeps new PM initialization lightweight and deterministic.

---

### **Step 5 — Engage with Cursor / OA**

All PM → Cursor → OA interactions must follow these rules:

1. **Always reference the Kernel’s `current_phase` when issuing instructions.**  
2. **Never assume a phase. Derive it from the Kernel.**
3. **When Cursor proposes actions, require that they pass strict guards** unless explicitly waived.
4. **Do not let Cursor / OA continue if kernel says `reality_green = false`.**

---

## 4. Failure Modes & Escalation Rules

If **any** of these are true:

- Kernel: `health.reality_green = false`
- Kernel: key check is false (DMS, Share Sync, Bootstrap Consistency, Backup)
- Bootstrap and SSOT phases mismatch
- Required surfaces missing
- Guard mismatch detected

Then the PM must:

### **Step 1 — Load REALITY_GREEN_SUMMARY.json**

Identify exactly which guard failed.

### **Step 2 — Prohibit further operations**

No phase work, no destructive ops, no share regeneration.

### **Step 3 — Delegate to Cursor with explicit remediation scope**

Example:

> “Cursor, fix DMS → share alignment only.  
> No other changes permitted.”

### **Step 4 — Require a re-run of `make reality.green`**

Only when green again may the PM continue.

---

## 5. Formal Guarantees

This protocol ensures that:

- PM startup is reproducible  
- Kernel and Bootstrap act as the canonical “seed” surfaces  
- No new chat will ever inherit inconsistent state  
- All PM behavior can be verified by guards and automated checks

This document is SSOT and overrides prior instructions.

#### Hints & Enforcement (Phase 26+)

The behaviors described in this protocol are not advisory. They are enforced via DMS hints:

- `pm.boot.kernel_first` — PM boot behavior.
- `oa.boot.kernel_first` — OA boot behavior.
- `ops.preflight.kernel_health` — OPS preflight behavior.

Any deviation from this protocol that violates these hints must be treated as a guard failure and resolved before continuing phase work.
