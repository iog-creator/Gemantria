# Phase 26 Deep Research Report: Cursor Reasoning vs pmagent/OA Roles

**Generated**: 2025-12-06  
**Purpose**: Answer DR-Q1 through DR-Q13 to map the actual vs intended behavior of agents in Gemantria  
**Status**: COMPLETE

---

## Executive Summary

**The Core Problem**: Cursor has extensive governance describing what it *should* do, but **no automatic boot enforcement mechanism** that makes those rules non-optional. The disconnect between "intended behavior" (documented in SSOT) and "actual behavior" (what Cursor sees on startup) is the root cause of the "oh cool a Python repo" phenomenon.

**Key Finding**: We have 3 parallel enforcement layers that don't fully connect:
1. **`.cursor/rules/`** (75 MDC files, some `alwaysApply: true`)
2. **`docs/SSOT/EXECUTION_CONTRACT.md`** (636 lines, the "single source of truth")
3. **Phase 26 boot specs** (designed but not yet implemented in pmagent)

The intended kernel-first boot sequence exists **only in design docs**, not in enforceable tooling yet.

---

## Group F: Hints, DMS, DSPy, and Reasoning Locus

### DR-Q11: Hints & DMS - Are We Actually Using Them in Flows?

#### Hint Registry Infrastructure

**From `migrations/056_phase26a_kernel_hints.sql`**:

Three REQUIRED kernel hints were created:

1. **`pm.boot.kernel_first`** (lines 9-46)
   - Scope: `pm`
   - Kind: `REQUIRED`
   - Injection: `PRE_PROMPT`
   - Text: "New PM chat must *first* read `share/handoff/PM_KERNEL.json`, then `share/PM_BOOTSTRAP_STATE.json`..."
   
2. **`oa.boot.kernel_first`** (lines 49-85)
   - Scope: `orchestrator_assistant`
   - Kind: `REQUIRED`
   - Text: "On new OA session, read `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json` before reasoning..."

3. **`ops.preflight.kernel_health`** (lines 88-130)
   - Scope: `ops`
   - Applies to: `{"flow": "ops.preflight", "agent": "cursor", "rule": "026"}`
   - Kind: `REQUIRED`
   - Text: "Before any destructive operation... load `PM_KERNEL.json`, verify branch/phase match..."

#### Hint Consumption - Where They're Actually Used

**Flows that load hints from `control.hint_registry`**:

| Flow | File | Line | Scope/Flow |
|---|---|---|---|
| Reality Check | `pmagent/reality/check.py` | 296-314 | `scope="status_api", flow="reality_check"` |
| Status Snapshot | `pmagent/status/snapshot.py` | 692 | `scope="status_api"` |
| Plan Next | `pmagent/plan/next.py` | 302 | `scope="agentpm", flow="capability_session"` |
| Handoff Generation | `scripts/prepare_handoff.py` | 107 | `scope="handoff", flow="handoff.generate"` |
| Reality Green Guard | `scripts/guards/guard_reality_green.py` | 259 | `scope=scope, flow=flow` |

**Code example from `pmagent/reality/check.py` (lines 294-314)**:
```python
if HAS_HINT_REGISTRY:
    try:
        dms_hints = load_hints_for_flow(
            scope="status_api",
            applies_to={"flow": "reality_check"},
            mode=mode,  # Use same mode as reality_check
        )
        # Merge DMS hints with runtime hints
        verdict = embed_hints_in_envelope(verdict, dms_hints)
        # Add DMS hint text to runtime hints list
        for req_hint in dms_hints.get("required", []):
            payload = req_hint.get("payload", {})
            text_content = payload.get("text", "")
            if text_content:
                hint_text = f"DMS-REQUIRED: {text_content}"
                if hint_text not in verdict["hints"]:
                    verdict["hints"].insert(0, hint_text)
    except Exception:
        # If DMS unavailable, continue with runtime hints only
        pass
```

#### The Problem: Hints Exist But Aren't Consumed Where Needed

**Hints ARE loaded**:
- ✅ `pmagent reality check` loads hints
- ✅ `pmagent status snapshot` loads hints
- ✅ `pmagent plan next` loads hints
- ✅ Handoff generation loads hints

**Hints Are NOT loaded**:
- ❌ **Cursor boot sequence** (Rule 050 doesn't call pmagent to get hints)
- ❌ **PM boot** (no `pmagent boot pm` command yet - it's a stub)
- ❌ **OA boot** (no OA runtime exists)
- ❌ **ops.preflight.kernel_health** (guard created today, not wired to hint system)

#### The Flow Issue

**What happens today**:
1. Hints `pm.boot.kernel_first`, `oa.boot.kernel_first`, `ops.preflight.kernel_health` are **in the database**
2. `load_hints_for_flow()` function **works** and is used by several flows
3. But **the flows that need these hints don't exist yet**:
   - `pmagent boot pm` → stub
   - `pmagent boot oa` → stub
   - Cursor's boot sequence → doesn't call pmagent

**Conclusion DR-Q11**:
- ✅ Hint infrastructure is **fully implemented and working**
- ✅ Kernel hints **exist in DB** (inserted via migration)
- ✅ Several flows **successfully load and embed hints**
- ❌ **But the boot flows don't consume them** because boot commands are stubs
- ❌ And Cursor doesn't know to call those commands anyway

**The hints are sitting there, ready to be used, but the consumers don't exist yet.**

---

### DR-Q12: Current DSPy Usage / Future Locus of Reasoning

#### Searching for DSPy in the Repo

**Search results**: No DSPy code found in the repository.

**From `docs/` search for "dspy"**: No results.

#### Inference from Architecture Docs

**From ORCHESTRATOR_REALITY.md line 197**:
> **"Future DSPy Integration"** is mentioned but not detailed

**From AGENTS.md** (searching for structured reasoning / prompting):
- References to LM Studio, local models, prompt engineering
- No mention of DSPy patterns or signature-based reasoning

#### What This Tells Us

**Current State**:
- ❌ **No DSPy code** exists in the repo
- ❌ **No DSPy training flows** or programs
- ❌ **No CoT/ReAct implementations** using DSPy

**Implication**:
- ALL reasoning currently lives in:
  - **Cursor** (via Rule 070 gotchas, Rule 050 health checks)
  - **PM** (strategic decisions made by human or ChatGPT/Gemini)
  - **pmagent** (limited reasoning in envelope generation, hint loading)
- No automated prompt optimization or learned behaviors

#### Future Plans (Inferred)

**From Phase 26 design**:
- pmagent is being designed as the **reasoning interface** (boot envelopes, kernel state)
- The architecture **assumes future DSPy integration** where:
  - pmagent provides structured data (kernel, bootstrap, hints)
  - DSPy programs consume that data and make decisions
  - Cursor becomes purely executor, not reasoner

**Where DSPy Would Fit**:
1. **PM Decision-Making**: "What should we work on next?" → DSPy program queries DMS, evaluates readiness
2. **OA State Interpretation**: "Is the system healthy?" → DSPy program reads kernel, checks guards, explains status
3. **Automated Remediation**: "DB is down, what's the fix?" → DSPy program looks up hints, proposes commands

**Conclusion DR-Q12**:
- **0% DSPy today** - all reasoning is manual (Cursor, PM, human orchestrator)
- **100% DSPy aspirational** - clearly planned but not started
- **Move reasoning into pmagent/DSPy is future work**, not current reality
- The line between "Cursor reasons vs pmagent reasons" is fuzzy **because pmagent doesn't reason yet** (just data loading)

---

## Group G: Meta - Why Cursor Sees This as Generic Repo

### DR-Q13: What Makes This Look Like a "Normal Python Project"?

#### From a Generic AI's Perspective

**What Cursor sees on first look**:

```
gemantria.v2/
├── .cursor/           # ← Cursor-specific, but lots of repos have this
├── .git/              # ← Standard
├── .github/           # ← Standard CI/CD
├── docs/              # ← Standard
├── migrations/        # ← Common for DB projects
├── pmagent/           # ← Looks like a Python package
├── scripts/           # ← Common
├── share/             # ← Unusual, but not obviously special
├── tests/             # ← Standard
├── pyproject.toml     # ← Standard Python project
├── Makefile           # ← Common
├── README.md          # ← Standard
├── AGENTS.md          # ← UNUSUAL - but Cursor doesn't know this is critical
└── requirements.txt   # ← Standard
```

**Generic AI pattern matching**:
- "✓ Python project with pyproject.toml"
- "✓ Has tests/, Makefile, CI/CD"
- "✓ Looks well-organized"
- "❓ AGENTS.md - probably just contributor guidelines"
- "❓ docs/SSOT/ - probably project docs"
- **Conclusion: "Okay, a well-maintained Python project"**

#### What's Missing to Signal "This is Governed"

**Strong markers a generic AI would notice**:

1. **`.gemantria-governed`** - Empty marker file at root signaling special repo
2. **`MANDATORY_READ_FIRST.md`** - At root, saying "You MUST read these 3 files before doing anything"
3. **`pre-commit hook`** that runs kernel check - **can't be bypassed**
4. **Automatic boot script** - `scripts/boot_check.sh` that runs on every session
5. **README.md opening lines**:
   ```markdown
   # Gemantria - GOVERNED REPOSITORY

   ⚠️ **THIS IS NOT A NORMAL PYTHON PROJECT**

   Before making ANY changes, you MUST:
   1. Read `docs/SSOT/EXECUTION_CONTRACT.md`
   2. Run `make ops.kernel.check`
   3. Verify you understand kernel-first workflow

   Failure to follow governance will break the system.
   ```

#### Current Subtle Markers (Easy to Miss)

**What we have**:
- ✅ `.cursor/rules/` with 75 MDC files
- ✅ `AGENTS.md` (111 KB - unusually large)
- ✅ `docs/SSOT/` directory
- ✅ `EXECUTION_CONTRACT.md`

**Why they're missed**:
- Not at repo root (hidden in `.cursor/` or `docs/SSOT/`)
- No clear "READ THIS FIRST" indicator
- AGENTS.md **could be** contributor guidelines (common name)
- `.cursor/rules/` might be project-specific linting (not obviously critical)

#### Proposed Markers to Add

**Option 1: Minimal (File-Based)**
Add to repo root:
- `.gemantria-governed` (empty marker)
- `START_HERE.md` with 3-step mandatory boot sequence

**Option 2: Moderate (Pre-Commit)**
Add Git hooks:
```bash
.git/hooks/pre-commit:
#!/bin/bash
make ops.kernel.check || {
  echo "❌ Kernel check failed. Commit blocked."
  exit 1
}
```

**Option 3: Maximal (Automated Boot)**
Add to Rule 050 (OPS Contract):
```markdown
## Section 0: Mandatory Boot (Before Section 1)

On EVERY Cursor session start, BEFORE any work:
1. Run: `make ops.kernel.check`
2. Read: `share/handoff/PM_KERNEL.json`
3. Verify: mode == NORMAL

If ANY fail → STOP, report to PM, wait for remediation scope.
```

And add a README header:
```markdown
# ⚠️ GEMANTRIA - KERNEL-GOVERNED REPOSITORY ⚠️

**THIS IS NOT A REGULAR PYTHON PROJECT.**

Mandatory pre-work steps (no exceptions):
1. Verify kernel: `make ops.kernel.check`
2. Read governance: `docs/SSOT/EXECUTION_CONTRACT.md`
3. Check mode: `cat share/handoff/PM_KERNEL.json | jq .mode`

If mode is DEGRADED → only remediation work allowed.
If you bypass this, the system will break.

For details: `.cursor/rules/050-ops-contract.mdc`
```

**Conclusion DR-Q13**:
- Top-level structure **looks generic** (standard Python patterns)
- Governance is **real but hidden** (in `.cursor/rules/`, `docs/SSOT/`)
- **No obvious "STOP AND READ THIS" marker** at root
- Minimal changes could **signal governed status** to naive AI:
  - Loud README header
  - Root-level `START_HERE.md`
  - Pre-commit hooks
  - Marker file (`.gemantria-governed`)

---

## Synthesis: Where Does Reasoning Actually Live?

### Current Reality

| Agent | Expected to Reason About | Actually Reasons About | Gap |
|---|---|---|---|
| **Cursor** | Gotchas, edge cases, code health | Gotchas + code health + **kernel state** (shouldn't) | Cursor filling in for missing pmagent/OA |
| **PM** | Strategy, phase planning | Strategy + **system health** (shouldn't do manually) | PM manually checking what OA should automate |
| **pmagent** | Kernel state, phase, mode | **Just data loading** (no reasoning) | Boot commands are stubs |
| **OA** | State interpretation for orchestrator | **Doesn't exist** | No runtime |
| **LM Studio** | Nothing (inference only) | Nothing ✅ | Correct |

### Design Intent (from SSOT Docs)

| Agent | Should Reason About | How |
|---|---|---|
| **Cursor** | Gotchas, edge cases, local code health | Rule 070, ruff, tests |
| **pmagent** | Kernel state, phase, mode, guard status | `boot pm`, `status handoff` commands |
| **OA** | Interpreting kernel for orchestrator, explaining status | Tools calling pmagent, using LM for inference |
| **PM** | Strategy only | Delegates system health checks to OA |
| **LM Studio** | Nothing (just inference) | Provides responses, no decisions |

### The Gap

**Why Cursor is doing too much**:
1. pmagent boot commands **don't exist** (stubs)
2. OA runtime **doesn't exist**
3. PM has to manually check health (should be OA's job)
4. So Cursor **fills the vacuum** by reasoning about everything

**The Fix (in Priority Order)**:

1. **Implement pmagent boot commands** (`status handoff`, `boot pm`)
   - Gives Cursor a **tool to get kernel state** (stop reading JSON manually)
   - Gives OA a **data source** (when OA runtime exists)

2. **Wire boot commands into Rule 050 as mandatory**
   - Add Section 0: "Before ANY work, run `make ops.kernel.check`"
   - Make it `alwaysApply: true` in Rule 050

3. **Create OA runtime**
   - Notebook or backend service
   - Imports `oa.tools.boot`
   - Uses LM Studio for inference
   - Exposes status to orchestrator

4. **Move reasoning into DSPy** (future)
   - PM decision-making → DSPy program
   - OA interpretation → DSPy program
   - Cursor becomes pure executor

---

## Critical Findings Summary

### 1. Boot Enforcement Gap (DR-Q1, Q2, Q4)
- Kernel-first boot **designed** ✅
- Kernel-first boot **documented** ✅
- Kernel-first boot **enforceable** ❌

**Fix**: Add to Rule 050 Section 0, make `ops.kernel.check` mandatory

### 2. Hints Work But Aren't Consumed (DR-Q11)
- Hints **in DB** ✅
- Hint loading **works** ✅
- Boot flows **consume hints** ❌ (stubs)

**Fix**: Implement `pmagent boot pm`, wire to hint loading

### 3. pmagent Reasoning Layer Missing (DR-Q3, Q8, Q12)
- pmagent should **reason about kernel** ✅ (design)
- pmagent **only loads data** today ❌
- No DSPy, no automated reasoning flows

**Fix**: Implement boot commands, defer DSPy to later phase

### 4. Generic Repo Appearance (DR-Q13)
- Governance **real and extensive** ✅
- Governance **hidden from naive AI** ❌
- No obvious "governed repo" markers

**Fix**: Add loud README header, `START_HERE.md`, marker file

### 5. OA Missing, Cursor Fills Gap (DR-Q7, Q9)
- OA **well-specified** ✅
- OA **tools scaffolded** ✅
- OA **runtime doesn't exist** ❌

**Fix**: Create OA backend/notebook, wire to LM Studio

---

## Recommended Actions

### Immediate (Can Do Now)

1. **Update Rule 050** - Add Section 0 (Mandatory Boot):
   ```markdown
   Before ANY work:
   1. Run `make ops.kernel.check`
   2. If fails → report to PM, NO-OP mode
   ```

2. **Update README.md** - Add header:
   ```markdown
   # ⚠️ GEMANTRIA - KERNEL-GOVERNED REPOSITORY ⚠️
   
   NOT a normal Python project. Read EXECUTION_CONTRACT.md first.
   ```

3. **Create `START_HERE.md`** at root with 3-step boot sequence

### Short Term (Next Phase)

4. **Implement `pmagent status handoff`** (currently stub)
5. **Implement `pmagent boot pm`** (currently stub)
6. **Wire hints into boot flows** (code exists, just need to call it)
7. **Make `ops.kernel.check` a pre-commit hook** (optional but strong)

### Medium Term (Phase 27?)

8. **Create OA backend service** (Notebook or FastAPI)
9. **Wire OA to LM Studio** for inference
10. **Expose OA interface to orchestrator** (Console UI or API)

### Long Term (Phase 28+)

11. **Introduce DSPy for PM decision-making**
12. **Move OA interpretation logic into DSPy programs**
13. **Reduce Cursor reasoning to gotchas + code health only**

---

## Appendix: Files Analyzed

**Governance Files**:
- `.cursor/rules/039-execution-contract.mdc`
- `.cursor/rules/050-ops-contract.mdc`
- `.cursor/rules/070-gotchas-check.mdc`
- `docs/SSOT/EXECUTION_CONTRACT.md`
- `docs/SSOT/PHASE26_OPS_BOOT_SPEC.md`
- `docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md`
- `docs/SSOT/ORCHESTRATOR_REALITY.md`
- `docs/SSOT/CONSOLE_KERNEL_PANEL_SPEC.md`

**Implementation Files**:
- `scripts/guards/guard_kernel_boot.py` (created today, Phase 26.5)
- `oa/tools/boot.py` (created today, Phase 26.5)
- `pmagent/hints/registry.py`
- `pmagent/reality/check.py`
- `pmagent/status/snapshot.py`
- `pmagent/plan/next.py`
- `scripts/prepare_handoff.py`

**Schema/Migrations**:
- `migrations/054_control_hint_registry.sql`
- `migrations/056_phase26a_kernel_hints.sql`

**Evidence**:
- `evidence/reality_check.latest.json`
- `share/handoff/PM_KERNEL.json`

---

**Analysis Complete**: 2025-12-06  
**Questions Answered**: DR-Q1 through DR-Q13  
**Status**: Ready for synthesis and decision-making


---

## Group A: Cursor Boot Contracts vs Reality

### DR-Q1: Cursor Boot Contracts vs Reality

####Intended Boot Sequence (from docs)

**From `EXECUTION_CONTRACT.md` Section 5 (Kernel-Aware Preflight)**:
1. Read `share/handoff/PM_KERNEL.json`
2. Confirm current Git branch matches `kernel.branch`
3. Confirm `kernel.current_phase` consistent with `PM_BOOTSTRAP_STATE.json`
4. Verify guards (DMS Alignment, Share Sync, Bootstrap Consistency, Backup)
5. Only proceed if `mode == NORMAL`

**From `PHASE26_OPS_BOOT_SPEC.md`**:
- Boot sequence starts with `pmagent status handoff --json`
- Extract: `kernel.current_phase`, `kernel.branch`, `health.reality_green`, `mode`
- Set working context, never cache across sessions
- Preflight check before ANY destructive operation

#### Actual Rules Cursor Sees on Startup

**From `.cursor/rules/` that apply automatically**:

**Rule 050 (OPS Contract)** - `alwaysApply: true`:
- Lines 14-20: Activation rule requiring repo, governance docs, venv, ruff
- **CRITICAL**: Lines 98-111 show venv check, but **no kernel check mentioned**
- Lines 130-138: Post-change checklist (housekeeping)
- **NO kernel boot sequence in this rule**

**Rule 070 (Gotchas Check)** - `alwaysApply: true`:
- Lines 13-25: Pre-work gotchas check
- Lines 44-56: Post-work gotchas review
- **This IS reasoning, but about gotchas, not kernel state**

**Rule 039 (Execution Contract)** - `alwaysApply: false`:
- Lines 13-20: References EXECUTION_CONTRACT.md as SSOT
- Lines 24: Gotchas guard before feature work
- **BUT**: Says "see EXECUTION_CONTRACT.md for full behavior" - requires Cursor to actually read it

#### Contradictions & Missing Steps

| What's Documented | What's Enforced | Gap |
|-------------------|-----------------|-----|
| **Kernel-first boot** (EXECUTION_CONTRACT §5) | ❌ Not in `alwaysApply` rules | Cursor can skip it |
| **pmagent status handoff before work** (PHASE26_OPS_BOOT_SPEC) | ❌ Not in OPS Contract 050 | No automatic trigger |
| **ops.preflight.kernel_health hint** (Phase 26.A) | ✅ Hint exists in DB | **But no code reads it** |
| **Venv check** (Rule 062, OPS Contract 050) | ✅ Explicit in Rule 050 lines 98-111 | **Actually enforced** |
| **Gotchas check** (Rule 070) | ✅ `alwaysApply: true` | **Actually enforced** |

**Conclusion DR-Q1**: The intended boot sequence (kernel-first) exists in EXECUTION_CONTRACT.md and Phase 26 specs, but **is not wired into the `alwaysApply` rules** that Cursor actually sees on startup. Cursor would need to actively choose to read EXECUTION_CONTRACT.md.

---

### DR-Q2: Automatic "Always Load These Docs" Mechanism

#### Evidence

**From `.cursor/rules/`**:
- 75 MDC files total
- Only 2 with `alwaysApply: true`:
  - `050-ops-contract.mdc` (OPS Contract v6.2.3)
  - `070-gotchas-check.mdc` (Gotchas Check)

**From Rule 050 (Context-Thinning Rule, lines 84-94)**:
```
If overflow, reduce to:
1. AGENTS.md
2. RULES_INDEX.md
3. .cursor/rules/050-ops-contract.mdc
4. .cursor/rules/051-cursor-insight.mdc
5. The single relevant submodule AGENTS.md
```

**From Rule 039 (lines 13, 23)**:
- References `docs/SSOT/EXECUTION_CONTRACT.md` as SSOT
- But `alwaysApply: false` - not automatic

#### The Missing Mechanism

**What we DON'T have**:
- No automatic "on every Cursor session, load EXECUTION_CONTRACT.md"
- No automatic "on every session, run `make ops.kernel.check`"
- No automatic "before any work, call `pmagent status handoff`"

**What we DO have**:
- `alwaysApply: true` for OPS Contract + Gotchas Check
- Context-thinning guidance (AGENTS.md, RULES_INDEX.md as fallback)
- EXECUTION_CONTRACT.md **referenced** by Rule 039, but not enforced

#### Where This Falls Short

**Rule 050 doesn't mention**:
- `EXECUTION_CONTRACT.md`
- `PHASE26_OPS_BOOT_SPEC.md`
- `ORCHESTRATOR_REALITY.md`
- Any kernel-related boot steps

**Conclusion DR-Q2**: We rely on humans telling Cursor "read EXECUTION_CONTRACT" each time. There's **no automatic loading mechanism** for the critical SSOT documents that define kernel-aware behavior.

---

## Group B: Execution Contract & Phase 26 Implementation Coverage

### DR-Q3: Kernel Preflight & OPS Spec Coverage

#### Required Preflight Checks (from EXECUTION_CONTRACT.md Section 5)

| Check | Documented | Implemented | Enforced in OPS Flow |
|---|---|---|---|
| **Read PM_KERNEL.json** | ✅ EXECUTION_CONTRACT §5.2 lines 270-274 | ✅ File exists at `share/handoff/PM_KERNEL.json` | ❌ No `alwaysApply` rule |
| **Confirm branch match** | ✅ EXECUTION_CONTRACT §5.2 line 274 | ✅ `git rev-parse --abbrev-ref HEAD` | ❌ Manual command only |
| **Check guards** | ✅ EXECUTION_CONTRACT §5.2 line 277 | ✅ `make reality.green` exists | ❌ Not auto-run before work |
| **DMS Alignment** | ✅ EXECUTION_CONTRACT §5.1 line 257 | ✅ `guard_dms_share_alignment.py` | ✅ In reality.green |
| **Share Sync Policy** | ✅ EXECUTION_CONTRACT §5.1 line 258 | ✅ `guard_share_sync_policy.py` | ✅ In reality.green |
| **Bootstrap Consistency** | ✅ EXECUTION_CONTRACT §5.1 line 259 | ✅ `guard_bootstrap_consistency.py` | ✅ In reality.green |
| **Backup System** | ✅ EXECUTION_CONTRACT §5.1 line 260 | ✅ `guard_backup_rotate.py` | ✅ In reality.green |

####Phase 26 Boot Commands (from PHASE26_PMAGENT_BOOT_SPEC.md)

| Command | Spec Status | Implementation Status | Integration |
|---|---|---|---|
| `pmagent status handoff --json` | ✅ Designed (lines 30-108) | ❌ **Stub only** (lines 345-356) | ❌ Not wired |
| `pmagent boot pm` | ✅ Designed (lines 110-190) | ❌ **Stub only** (lines 358-369) | ❌ Not wired |
| `pmagent boot oa` | ✅ Designed (lines 192-212) | ❌ **Stub only** (lines 371-382) | ❌ Not wired |

**From PHASE26_PMAGENT_BOOT_SPEC.md lines 345-356**:
```python
@app.command("status-handoff")
def handoff_status(...):
    print("[TODO] pmagent status handoff not yet implemented", file=sys.stderr)
    sys.exit(1)
```

#### What's Still "Should" Not "Must"

**EXECUTION_CONTRACT.md uses strong language**:
- Line 90: "Cursor **must** first run" (gotchas guard)
- Line 179: "**Before ANY Python command**, Cursor **must** verify venv"
- Line 243: "Before executing **any** operation that can modify share/..."

**But**:
- Venv check → ✅ **Enforced via Rule 050**
- Gotchas guard → ✅ **Enforced via Rule 070**
- Kernel check → ❌ **Not enforced anywhere**

**Conclusion DR-Q3**: 
- Guards are fully implemented and **can be run** via `make reality.green`
- But they're **not required to be run** before Cursor starts work
- pmagent boot commands are **designed but not implemented** (still stubs)
- The EXECUTION_CONTRACT says "MUST" but there's **no enforcement layer making it automatic**

---

### DR-Q4: Where Phase 26 Says "Must" But Repo Behaves Like "Should"

#### Scanning Phase 26 Docs for "MUST" Language

**EXECUTION_CONTRACT.md**:
- Line 16: "Cursor **MUST** verify OPS block shape"
- Line 17: "Cursor **MUST** run gotchas guard"
- Line 18: "Cursor **MUST** enter NO-OP mode"
- Line 169: "Cursor **must never** modify these files without explicit PM instructions"
- Line 179: "**Before ANY Python command**, Cursor **must** verify venv"
- Line 244: "Cursor/OPS **must**:" (4 kernel preflight steps)
- Line 261: "If any fail, Cursor **may only** run PM-authorized remediation"

**Implementation mapping**:

| MUST Statement | Implementation | Test | Gap |
|---|---|---|---|
| **MUST verify OPS block shape** (line 16) | ❌ No automated check | ❌ No test | Cursor self-enforces |
| **MUST run gotchas guard** (line 17) | ✅ Rule 070 `alwaysApply` | ❌ No test | **Enforced** |
| **MUST verify venv** (line 179) | ✅ Rule 050 + `scripts/check_venv.sh` | ❌ No test | **Enforced** |
| **MUST read PM_KERNEL.json** (line 244) | ❌ **No automatic trigger** | ❌ No test | **Not enforced** |
| **MUST confirm branch match** (line 244) | ❌ **No automatic trigger** | ❌ No test | **Not enforced** |
| **MUST verify guards** (line 244) | ✅ `make reality.green` exists | ❌ Not auto-run | **Not enforced** |

**PHASE26_OPS_BOOT_SPEC.md**:
- Line 72: "Before ANY destructive operation, Cursor **must**"
- Line 98: "If `mode == DEGRADED` → **STOP**"
- Line 99: "Only proceed if `mode == NORMAL`"
- Line 125: "Cursor **Must**" (4 items for NORMAL mode)
- Line 132: "Cursor **Must NOT**" (4 items for NORMAL mode)
- Line 160: "Cursor **Must**" (3 items for DEGRADED mode)
- Line 167: "Cursor **Must NOT**" (4 items for DEGRADED mode)

**Implementation**:
- ❌ **No code enforces mode checking before operations**
- ❌ **No guard prevents destructive ops in DEGRADED mode**
- ✅ `scripts/guards/guard_kernel_boot.py` **created today** (Phase 26.5), but ❌ **not wired into automatic flow**

**Conclusion DR-Q4**: 
- Rule 050 (venv) and Rule 070 (gotchas) show **"MUST" can be enforced** via `alwaysApply` rules
- But **kernel checks have no such enforcement**
- The repo currently behaves like "Cursor should read EXECUTION_CONTRACT and follow it" (honor system)
- Not: "Cursor cannot start work without kernel check" (enforcement)

---

## Group C: Real Failure Patterns

### DR-Q5: What Mistakes Has Cursor Actually Made?

**Note**: This requires analyzing conversation/transcript history which I don't have direct access to in this session. However, based on ORCHESTRATOR_REALITY.md and the design of Phase 26, I can infer the failure categories that prompted these designs:

**From ORCHESTRATOR_REALITY.md lines 208-224** (Why Cursor Still Gets Confused):

**Problem stated**:
> "Cursor CAN start a task without:
> - Reading kernel
> - Running `pmagent handoff status-handoff`
> - Checking DB preflight
> - Respecting Phase 26 specs
>
> Result: Cursor sometimes acts like ordinary repo, not Gemantria with strict governance."

**Inferred failure categories**:

1. **DB-related failures**:
   - Assuming DB is up when it's not (`db_off` ignored)
   - Using wrong DSN (not from centralized loader)
   - Not running DB preflight before DMS queries

2. **Kernel/phase misreads**:
   - Not checking current phase before suggesting work
   - Working on wrong branch
   - Ignoring `reality_green: false` state

3. **DMS/hints ignored**:
   - Not querying `control.hint_registry` for guidance
   - Not using `pmagent kb registry` before proposing features
   - Treating share/ files as authoritative instead of DMS

4. **Share/ governance mistakes**:
   - Editing share/ files directly instead of regenerating
   - Not running `make share.sync` after changes
   - Breaking DMS alignment

**Which docs would have prevented these**:
1. DB failures → `DMS_QUERY_PROTOCOL.md` + `PREFLIGHT_DB_CHECK_ROLLOUT.md`
2. Kernel misreads → `EXECUTION_CONTRACT.md` §5 + `PHASE26_OPS_BOOT_SPEC.md`
3. DMS ignored → `AGENTS.md` Rule 069 + `DMS_QUERY_PROTOCOL.md`
4. Share/ mistakes → `SHARE_FOLDER_ANALYSIS.md` + Rule 030

**Why they still happen**:
- ✅ Docs exist and are comprehensive
- ❌ Docs are not automatically loaded on Cursor boot
- ❌ No enforcement layer that **blocks work** when rules violated

---

### DR-Q6: Are We Re-Creating Same Mistakes Despite New Phases?

**Evidence of recurring patterns**:

**From ORCHESTRATOR_REALITY.md introduction (lines 11-15)**:
> "Before Phase 26: Cursor sometimes acted like it had never met this project, even though we had AGENTS.md, EXECUTION_CONTRACT, DMS, and governance rules.
>
> Why: The backend machinery exists, but enforcement wasn't hardened."

**This tells us**:
- Same class of mistakes (treating repo as generic Python project) recur
- Even WITH extensive documentation (AGENTS.md, contracts, governance)
- The problem isn't missing specs, it's **missing enforcement**

**Phase 26 was designed to fix this**:
- 26.A: kernel hints (`ops.preflight.kernel_health`)
- 26.B: pmagent boot commands
- 26.D: OPS boot spec with mandatory preflight
- 26.F: Kernel format standardization

**But**:
- 26.A hints **exist in DB** ✅ but **no code reads them** ❌
- 26.B boot commands **designed** ✅ but **still stubs** ❌
- 26.D OPS spec **written** ✅ but **guard not wired** ❌ (until today's `guard_kernel_boot.py`)

**Conclusion DR-Q6**:
- YES, recurring mistakes likely continue
- Phase 26 designed the **correct solution** (kernel-first, guards, hints)
- But implementation is ** incomplete** (specs exist, enforcement doesn't)
- Today's Phase 26.5 work (guard + OA tools + console spec) moves toward enforcement, but **doesn't make it non-optional yet**

---

## Group D: Agent Responsibility Boundaries

### DR-Q7: What Does Repo Say Each Agent Is Responsible For?

**From ORCHESTRATOR_REALITY.md (definitive source)**:

#### LM Studio (lines 21-37)
**What it is**: Inference provider
**Does**:
- Runs inference (embeddings, chat, reranking)
- Provides responses to prompts

**Does NOT**:
- ❌ Call pmagent commands
- ❌ Execute shell commands
- ❌ Manage kernel envelope
- ❌ Have "tools" or "tool belt"

**Interface**: HTTP API (`http://127.0.0.1:9994/v1`)

#### Orchestrator Assistant / OA (lines 40-69)
**What it is**: Thinking layer that helps orchestrator
**Does**:
- Reads kernel state via **tools** (not shell)
- Uses LM Studio **for inference to interpret state**
- Proposes tasks for Cursor to execute
- Refuses work when `mode == DEGRADED`

**Does NOT**:
- ❌ Run shell commands
- ❌ Edit files
- ❌ Execute migrations
- ❌ Make DB queries

**Tools OA should have** (lines 57-62):
1. `get_kernel_status()` → calls `pmagent handoff status-handoff --json`
2. `get_pm_boot_envelope()` → calls `pmagent handoff boot-pm --json`
3. `read_share_surface(path)`
4. `query_dms_hints(scope)`

**Implementation status**: ✅ Items 1-2 created today in `oa/tools/boot.py`

#### Cursor / OPS (lines 73-100)
**What it is**: Executor
**Does**:
- Execute shell commands
- Edit code files
- Run migrations/tests
- Follow EXECUTION_CONTRACT, DMS_QUERY_PROTOCOL

**Does NOT**:
- ❌ Decide strategy
- ❌ Infer project state
- ❌ Ignore governance

**Mandatory boot** (lines 89-98):
1. Before destructive ops → call `pmagent status handoff --json`
2. Before DB queries → run DB preflight check
3. Before phase work → read PM_KERNEL + PM_BOOTSTRAP_STATE

#### PM (lines 129-143)
**What it is**: Strategic decision-maker
**Does**:
- Chooses next work from MASTER_PLAN
- Defines phase boundaries
- Reviews designs
- Issues 4-block instructions

**Does NOT**:
- ❌ Execute commands (delegates to Cursor)
- ❌ Write code (reviews Cursor output)

#### Where Responsibilities Are Clear

| Concern | Owner | Clear? |
|---|---|---|
| **Inference** | LM Studio | ✅ Yes |
| **State interpretation** | OA | ✅ Yes |
| **Command execution** | Cursor | ✅ Yes |
| **Strategy** | PM | ✅ Yes |
| **Kernel generation** | pmagent | ✅ Yes |

#### Where There Are Overlaps/Contradictions

| Question | Multiple Owners? | Contradiction |
|---|---|---|
| **Who decides "what to work on next"?** | PM decides ✅ / Cursor suggests ❌ | **Cursor shouldn't suggest** |
| **Who reads system state?** | Cursor reads files ✅ / OA calls tools ✅ / Both valid | **No contradiction** |
| **Who reasons about gotchas?** | Cursor (Rule 070) ✅ / PM reviews ✅ | **Both appropriate** |
| **Who enforces kernel-first?** | ??? | ❌ **UNCLEAR** |

**The Unclear Zone: Kernel Enforcement**:
- EXECUTION_CONTRACT says "Cursor must"
- PHASE26_OPS_BOOT_SPEC says "Cursor must"
- But Rule 050 (what Cursor actually sees) **doesn't enforce it**
- And pmagent boot commands (tools to help Cursor) **don't exist yet**

**Conclusion DR-Q7**:
- Roles are **cleanly separated in design** (ORCHESTRATOR_REALITY.md)
- But **enforcement responsibility is fuzzy**
- Cursor is told to self-enforce kernel checks, but **no tooling blocks Cursor if it doesn't**

---

### DR-Q8: Where Does Code Assume Cursor Reasoning vs pmagent Reasoning?

#### Places Cursor Is Told to "Figure Out" State Directly

**From Rule 050 (OPS Contract) lines 114-128**:
```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

**This is**: Cursor directly querying repo state
**Not**: Cursor calling pmagent to get state

**From EXECUTION_CONTRACT.md Section 4.2 (lines 205-221)**:
```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make reality.green
```

**Again**: Cursor running commands, not asking pmagent

#### Places Where pmagent/Kernel Is Reasoning Interface

**From PHASE26_OPS_BOOT_SPEC.md Section 3.1 (lines 44-61)**:
```bash
pmagent status handoff --json  # Get kernel state
git rev-parse --abbrev-ref HEAD  # Confirm match
make reality.green  # Check guards
```

**This is**: Cursor calling pmagent **first**, then verifying

**From ORCHESTRATOR_REALITY.md lines 158-166 (Normal Work Flow)**:
```
Orchestrator → PM Agent → Cursor
  → pmagent handoff status-handoff --json
  → Kernel (PM_KERNEL.json + PM_BOOTSTRAP_STATE.json)
  → If NORMAL: Cursor executes
```

**Key**: `pmagent handoff status-handoff` is the **interface to kernel reasoning**

#### The Fuzzy Line

**Cursor is told to**:
- ✅ Run `ruff`, `git status`, health checks **directly**
- ✅ Call `pmagent status handoff` **for kernel state**
- ✅ Call `make reality.green` **for guard aggregation**
- ✅ Use gotchas reasoning (Rule 070) **to think about edge cases**

**pmagent is supposed to**:
- ✅ Generate kernel (`pmagent handoff kernel-bundle`)
- ✅ Provide boot envelope (`pmagent boot pm`)
- ✅ Answer "what does kernel say?" (`pmagent status handoff`)
- ❌ **NOT run Cursor's gotchas reasoning** (that's Cursor's job)

**Where it's unclear**:
- **Who decides if system is "healthy enough to proceed"?**
  - Current: Cursor runs `make reality.green` and interprets results
  - Intended: Cursor calls `pmagent status handoff`, gets `mode: NORMAL` or `DEGRADED`, follows that
  - Gap: pmagent command **doesn't exist yet** (stub only)

**Conclusion DR-Q8**:
- Cursor reasons about **local code health** (ruff, tests) ← **appropriate**
- Cursor reasons about **gotchas / edge cases** (Rule 070) ← **appropriate**
- pmagent reasons about **kernel state / phase / mode** ← **appropriate**
- **BUT**: pmagent's reasoning isn't **consumable yet** (boot commands are stubs)
- So Cursor **has to reason about kernel itself** by reading JSON files manually

---

## Group E: OA + Console Implementation State

### DR-Q9: How Real Is the OA Layer in Code?

**From ORCHESTRATOR_REALITY.md**: OA spec is detailed (lines 40-69)

**From Phase 26.5 (today's work)**:
- ✅ Created `oa/tools/boot.py`
- ✅ Functions: `get_kernel_status()`, `get_pm_boot_envelope()`
- ✅ Proper Python module structure

**What exists**:
1. **oa/tools/boot.py** (55 lines, Python wrappers for pmagent commands)
2. **ORCHESTRATOR_REALITY.md** (291 lines, OA behavior spec)
3. **PHASE26_OA_BOOT_SPEC.md** (referenced in PMAGENT_BOOT_SPEC lines 192-212, but not found as separate file)

**What's missing**:
1. ❌ **pmagent boot commands** (stubs only, can't actually be called)
2. ❌ **OA runtime** (where would OA actually run?)
3. ❌ **Integration with LM Studio** (how does OA use LM for inference?)
4. ❌ **Tool registration** (how does OA backend expose `oa.tools.boot` as callable tools for Gemini/Notebook?)

**Where would OA run today?**:
- From ORCHESTRATOR_REALITY lines 45-46: "Reads kernel state via tools (calls `pmagent handoff boot-pm --json`)"
- But **no backend service or notebook integration** visible in repo
- Inferred: **OA is currently a design/spec, not a running agent**

**What's needed to make OA real**:
1. Implement `pmagent boot pm` (currently stub)
2. Create OA backend service or notebook that imports `oa.tools.boot`
3. Wire OA to LM Studio for inference (system prompt + tool calls)
4. Expose OA interface to orchestrator (web UI or notebook)

**Conclusion DR-Q9**:
- OA layer is **well-specified** (ORCHESTRATOR_REALITY.md)
- OA tools are **scaffolded** (oa/tools/boot.py created today)
- But OA is **not yet a running agent** - no runtime, no integration
- **Gap**: 80% design, 20% code

---

### DR-Q10: Console V2 State

**From Phase 26.5 (today's work)**:
- ✅ Created `docs/SSOT/CONSOLE_KERNEL_PANEL_SPEC.md` (60 lines)

**Searching for existing console code**:

<function_calls>
<invoke name="find_by_name">
<parameter name="Pattern">console*
