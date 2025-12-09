# 🔥🔥🔥 LOUD HINTS REGISTRY 🔥🔥🔥

**Purpose:** Comprehensive registry of all LOUD HINT emissions throughout the Gemantria system, connecting each hint to its relevant MDC rule and agent file. All functions and files now include proper metadata references in docstrings and comments.

**Why LOUD HINTS:** Many AIs won't pick up subtle hints. LOUD HINTS use triple fire emojis and explicit rule references to ensure visibility.

---

## 🔗 Rule-026 (System Enforcement Bridge)

**Related File:** `.cursor/rules/026-system-enforcement-bridge.mdc`
**Agent Context:** `scripts/rules_guard.py`
**Hint Locations:**
- `scripts/rules_guard.py:main()` - "Pre-commit + CI + Branch Protection"
- `scripts/hint.sh` - Enhanced with LOUD formatting

---

## 🔗 Rule-027 (Docs Sync Gate)

**Related File:** `.cursor/rules/027-docs-sync-gate.mdc`
**Agent Context:** `scripts/rules_guard.py`
**Hint Locations:**
- `scripts/rules_guard.py:main()` - "Require docs/ADR/SSOT updates for code changes"

---

## 🔗 Rule-038 (Exports Smoke Gate)

**Related File:** `.cursor/rules/038-exports-smoke-gate.mdc`
**Agent Context:** `Makefile:ci.exports.smoke`
**Hint Locations:**
- `Makefile:ci.exports.smoke` - "Fail-Fast Guard for Export Readiness"

---

## 🔗 Rule-039 (Cursor Execution Contract)

**Related File:** `.cursor/rules/039-gpt5-contract-v5-2.mdc`
**Agent Context:** `AGENTS.md Pipeline Execution`
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Drive, Don't Ask"

---

## 🔗 Rule-043 (CI DB Bootstrap & Empty-Data Handling)

**Related File:** `.cursor/rules/043-ci-db-bootstrap-and-empty-data-handling.mdc`
**Agent Context:** `scripts/ci/ensure_db_then_migrate.sh`
**Hint Locations:**
- `scripts/ci/ensure_db_then_migrate.sh` - "Any workflow that queries DB must create DB + run all migrations first"

---

## 🔗 Rule-046 (Hermetic CI Fallbacks)

**Related File:** `.cursor/rules/046-hermetic-ci-fallbacks.mdc`
**Agent Context:** `src/services/AGENTS.md`
**Hint Locations:**
- `src/services/lmstudio_client.py:assert_qwen_live()` - "No outbound inference in CI; use deterministic mocks"

---

## 🔗 Rule-050 (OPS Contract v6.2.3)

**Related File:** `.cursor/rules/050-ops-contract.mdc`
**Agent Context:** `AGENTS.md OPS Contract`
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Evidence-First Protocol"
- `Makefile:pipeline.e2e` - "Evidence-First Protocol"
- `Makefile:eval.graph.calibrate.adv` - "Hermetic Test Bundle"
- `Makefile:ci.exports.smoke` - "Hermetic Test Bundle"

---

## 🔗 Rule-051 (Cursor Insight & Handoff)

**Related File:** `.cursor/rules/051-cursor-insight.mdc`
**Agent Context:** `AGENTS.md Cursor Execution Profile`
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Baseline Evidence Required"
- `Makefile:pipeline.e2e` - "Baseline Evidence Required"
- `Makefile:eval.graph.calibrate.adv` - "Baseline Evidence Required"
- `Makefile:ci.exports.smoke` - "Baseline Evidence Required"

---

## 🔗 Rule-052 (Tool Priority & Context Guidance)

**Related File:** `.cursor/rules/052-tool-priority.mdc`
**Agent Context:** `AGENTS.md Tool Priority`
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Local+GH → Codex → Gemini/MCP"

---

## 🔗 Rule-053 (Idempotent Baseline)

**Related File:** `.cursor/rules/053-idempotent-baseline.mdc`
**Agent Context:** `AGENTS.md Baseline Evidence`
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Cache Baseline Evidence 60m"
- `Makefile:pipeline.e2e` - "Cache Baseline Evidence 60m"

---

## 🔗 Rule-058 (Auto-Housekeeping Post-Change)

**Related File:** `.cursor/rules/058-auto-housekeeping.mdc`
**Agent Context:** `scripts/rules_guard.py`
**Hint Locations:**
- `scripts/rules_guard.py:main()` - "Run rules_audit.py/share.sync/forest regen"

---

## 🔗 Rule-011 (Production Safety)

**Related File:** `.cursor/rules/011-production-safety.mdc`
**Agent Context:** `src/services/AGENTS.md`
**Hint Locations:**
- `src/services/lmstudio_client.py:assert_qwen_live()` - "Qwen Live Gate Required"

---

## 📋 Agent File Hints Registry

### AGENTS.md Pipeline Execution
**Related Rules:** Rule-039, Rule-050, Rule-051, Rule-052, Rule-053
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "LangGraph orchestration with Qwen health gate"

### src/graph/AGENTS.md
**Related Rules:** Rule-050, Rule-051
**Hint Locations:**
- `src/graph/graph.py:run_pipeline()` - "Pipeline state management and batch processing"

### src/services/AGENTS.md
**Related Rules:** Rule-011, Rule-046
**Hint Locations:**
- `src/services/lmstudio_client.py:assert_qwen_live()` - "Qwen Live Gate: Must call assert_qwen_live() before network aggregation"

### scripts/AGENTS.md
**Related Rules:** Rule-050, Rule-051
**Hint Locations:**
- `Makefile:eval.graph.calibrate.adv` - "calibrate_advanced.py - Advanced Edge Strength Calibration"

### scripts/rules_guard.py
**Related Rules:** Rule-026, Rule-027, Rule-058
**Hint Locations:**
- `scripts/rules_guard.py:main()` - "System-level enforcement so rules aren't just words"

### scripts/ci/ensure_db_then_migrate.sh
**Related Rules:** Rule-043
**Hint Locations:**
- `scripts/ci/ensure_db_then_migrate.sh` - "Database bootstrap script for CI"

---

## 🎯 Hint Emission Pattern

**Format:** `🔥🔥🔥 LOUD HINT: [Rule/File Reference] - [Instruction/Hint] 🔥🔥🔥`

**Purpose:** Triple fire emojis ensure visibility even for AIs that filter out standard hints.

**Placement:** Critical entry points, validation gates, and safety checks.

**Connection:** Every hint explicitly references the MDC rule and agent file that governs that behavior.

---

## 🛠️ **AUTOMATED GOVERNANCE TRACKING**

**New Database-Backed System (Rule-058 Auto-Housekeeping):**

### Governance Artifacts Database
- **`governance_artifacts`** table tracks all rules, agent files, and metadata references
- **`hint_emissions`** table logs all runtime LOUD HINT emissions
- **`governance_compliance_log`** table maintains compliance history
- Automatic checksum validation prevents tampering

### Automated Maintenance Scripts
- **`scripts/governance_tracker.py`** - Database population and compliance validation
- **`scripts/governance_housekeeping.py`** - Integrated housekeeping workflow
- **`make governance.housekeeping`** - Makefile integration
- **`make housekeeping`** - Complete workflow including governance

### Rules Guard Integration
- **Critical Check 7**: LOUD HINTS governance validation
- Validates hint.sh emissions, metadata backing, and documentation completeness
- Fails-closed if governance system is compromised

### Migration System
- **`migrations/015_create_governance_tracking.sql`** - Database schema
- Functions for artifact updates and compliance logging
- Automated freshness checking (>24h warnings)

---

## 📋 **METADATA BACKING**

**All files now include proper governance metadata:**

### Function Docstrings
- **Related Rules:** List of MDC rule numbers that govern the function
- **Related Agents:** Specific agent file references for behavior guidance
- **Implementation notes:** Which rules are implemented and how

### File Headers
- **Rule references:** Which MDC rules apply to the entire file
- **Agent references:** Which agent files define the file's purpose
- **Purpose statements:** Clear governance linkage

### Makefile Targets
- **Rule comments:** Above each target explaining governance requirements
- **Agent comments:** Linking to specific agent file sections
- **LOUD HINTS:** Runtime emission of governance requirements

### Script Headers
- **Rule attribution:** Which MDC rules the script enforces
- **Agent linkage:** Which agent files define script behavior
- **Purpose governance:** Clear rule-based purpose statements

---

## 🔍 Verification Checklist

- [ ] All Rule-039+ hints emitted at pipeline start
- [ ] Rule-050/051 hints in hermetic test bundle targets
- [ ] Rule-026 hints in system enforcement gates
- [ ] Rule-043 hints in CI database operations
- [ ] Rule-011 hints in Qwen health checks
- [ ] All hints use LOUD formatting (🔥🔥🔥)
- [ ] All hints connect to specific MDC rules and agent files
