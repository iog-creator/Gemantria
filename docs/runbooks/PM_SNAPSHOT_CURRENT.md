# PM Snapshot — Current State (auto-maintained)

## 1. Reality Gate

- **reality.green**: GREEN

- **DB**: Online and healthy (Option C enforced — DB-down is a hard failure).

- **Control Plane**: Healthy.

- **AGENTS.md**: All in sync.

- **Share / Exports**: All required exports present and synced.

- **System State Ledger**: All tracked artifacts are current.

This snapshot is only valid when `make reality.green` is GREEN.

## 2. Active Branch / Workstream

- **Branch**: feat/webui.docs-control.20251119

- **Focus**:
  - Doc Control Panel (DM-001/DM-002) — implemented and wired into Shell.
  - Orchestrator UI Shell v1 — header, left rail, main canvas, overview, docs, graph, temporal, forecast, models, DB.
  - System State Ledger (migration 050) — live and populated.
  - reality.green truth gate — live and green.

## 3. Key Guarantees (when reality.green is GREEN)

- DB is reachable and healthy (Option C).
- Control-plane tables exist and are consistent.
- AGENTS.md files are fresh and reflect the code.
- SSOT docs (MASTER_PLAN, DB_HEALTH, RULES_INDEX) match ledger hashes.
- Core exports (system_health, lm_indicator, docs-control exports) exist and are current.
- WebUI Orchestrator Shell files are present and wired.

## 4. Next Likely PM Tasks (when a new PM chat starts)

- Use this snapshot + the top of MASTER_PLAN.md to decide:
  - Next Shell slice (e.g. Insights panel, Autopilot wiring, compliance views), or
  - Next governance/ledger extension (e.g. adding more artifacts or dashboards).

Any PM agent must **not** declare new work "done" without:

- `make reality.green` == GREEN

- Updating this snapshot if the high-level state changes.
