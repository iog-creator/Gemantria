# Orchestrator UI Shell — SSOT Contract (v1)

## 1. Purpose

The Orchestrator UI Shell is the **unified frame** for all operator-facing tools
in Gemantria (and future BibleScholar). It:

- gives the orchestrator a **single console** to see system posture,
- wraps existing panels (Doc Control Panel, Graph, Temporal, Forecast, Atlas),
- remains **hermetic** (works with DB/LM offline, using only static exports),
- never shows raw stack traces or low-level errors.

This document is the **single source of truth** for the Shell's layout and
behavior. WebUI code MUST implement this contract.

**Related vision**: The overarching UX and interaction model for the orchestrator dashboard is described in `docs/SSOT/Orchestrator Dashboard - Vision.md`. This Shell contract implements that vision for the current release.

---

## 2. Layout Overview

The Shell has three persistent regions:

1. **Top Header (Status Bar)** — shows high-level system posture.
2. **Left Rail (Orchestrator Tools)** — icon-based navigation.
3. **Main Canvas** — the active workspace ("score") for the selected tool.

The Shell frame is always present; individual panels (Docs, Graph, etc.) render
inside the Main Canvas.

---

## 3. Top Header — Status Tiles

### 3.1 Tiles

The header shows at least three tiles:

- **DB** — database posture
- **LM** — language model posture
- **System** — aggregate posture

Each tile has:

- `label` — short text ("DB", "LM", "System")
- `status` — one of `"healthy" | "degraded" | "offline" | "partial" | "unknown"`
- `reason` (optional) — short machine-readable reason (e.g. `"db_off"`)
- `updatedAt` (optional) — RFC3339 timestamp if available
- `detailsLink` (optional) — link to a deeper status page

### 3.2 Data Sources (read-only, static)

Tiles are driven by **static JSON exports only**:

- **DB tile** — DB health JSON / snapshot (guard_db_health output)
  - `mode=ready`     → `status="healthy"`
  - `mode=partial`   → `status="degraded"`
  - `mode=db_off`    → `status="offline"`
- **LM tile** — `share/atlas/control_plane/lm_indicator.json`
  - Map `lm_indicator.status` directly (`"healthy" | "degraded" | "offline"`).
- **System tile** — system health JSON (system_health aggregate export)
  - Map overall `ok`/component modes into one of the standard statuses.

The Shell MUST NOT make direct network calls to DB or LM endpoints. It only
reads these JSONs via HTTP from the static export directory.

**Reality Green Requirements**: For a "green" system state (validated by `make reality.green`), the following exports MUST be present:
- `share/atlas/control_plane/system_health.json` (required for System tile)
- `share/atlas/control_plane/lm_indicator.json` (required for LM tile)
- `share/exports/docs-control/summary.json` (required for Docs panel)
- WebUI public exports (mirrors of share exports in `webui/graph/public/exports/control-plane/`)

### 3.3 Error Handling

If a JSON export is:

- **Missing** — show `status="unknown"` and a friendly message:
  - "No recent health export found. Run the corresponding guard/smoke."
- **Invalid JSON** — show `status="degraded"` and:
  - "Export appears malformed. Check guard evidence / logs."
- **Empty but valid** — show `status="unknown"` with:
  - "No data yet. Run the pipeline to generate data."

The header MUST NEVER crash the app. All parsing errors are caught and turned
into human-readable status.

---

## 4. Left Rail — Orchestrator Tools

The left rail is a vertical icon bar with one entry per orchestrator tool.

### 4.1 Initial Tool Set

Initial contract tools:

- `docs`     — Docs / Archive (Doc Control Panel)
- `models`   — LM / Models posture (LM indicator + LM dashboard)
- `db`       — DB / Control Plane posture
- `graph`    — Graph / Temporal / Forecast dashboards
- `inputs`   — Attachments / inputs (future)
- `insights` — Guarded tool calls / compliance (future)

Each tool item has:

- `id` — stable string (`"docs"`, `"models"`, etc.)
- `icon` — visual icon (implementation detail, but MUST have aria-label)
- `label` — tooltip + screen reader text
- `route` — SPA route (e.g., `"/docs"`, `"/graph"`)

### 4.2 Behavior

- Clicking a rail item sets the active tool and updates the Main Canvas.
- The rail never shows raw errors; the worst state is disabled / inactive
  icons with explanatory tooltips.

---

## 5. Main Canvas — Panels

The Main Canvas hosts one panel at a time. Panels MUST respect hermetic /
WHEN–THEN behavior:

> **WHEN** backend X is online and exports are present, **THEN** the panel
> activates. Otherwise it shows a curated message.

### 5.1 Default Landing Panel — "Orchestrator Overview"

The default view when opening the Shell:

- Re-displays header tiles in a larger layout (DB, LM, System).
- Shows a **"Recent Signals"** list summarizing key facts (e.g., LM success
  rate, DB mode).
- Shows large buttons / cards linking to:
  - Doc Control Panel
  - Graph / Temporal / Forecast
  - LM Status page (Atlas LM status HTML)
- Uses only static exports (lm_indicator, system health, exported stats, etc.).

### 5.2 Docs Panel (Doc Control Panel)

The existing Doc Control Panel UI is embedded inside the Shell. The Shell:

- provides the header + rail framing,
- puts the Doc Control Panel component inside the Main Canvas,
- does not change internal Doc Control Panel behavior.

The Doc Control Panel continues to read its `/exports/docs-control/*.json`
files as defined in its own contract.

### 5.3 Graph / Temporal / Forecast Panel

This panel consumes:

- `exports/graph_latest.json` for graph topology
- `exports/temporal_patterns.json`
- `exports/pattern_forecast.json`

It may show:

- graph stats cards (node/edge counts, clusters),
- temporal trend cards,
- forecast summary cards,
- navigation to deeper dedicated dashboards.

If any of these files are missing, the panel shows a friendly message and hints
to run exports, rather than throwing.

### 5.4 Models Panel (LM)

This panel consumes:

- `share/atlas/control_plane/lm_indicator.json`
- `lm_usage_7d.json`
- `lm_health_7d.json`
- `lm_insights_7d.json`

It shows:

- a single sentence status ("LM is offline / healthy / degraded"),
- simple metrics (total calls, success rate, error rate),
- links to LM-specific dashboards (HTML/Atlas pages) when available.

### 5.5 Future Panels

Future tools (e.g., insights, inputs, full compliance dashboards) MUST:

- consume their data via static exports,
- follow the same error-handling and WHEN–THEN rules,
- integrate into the same Shell frame.

---

## 6. Data Contract — Static JSON Only

The Shell MUST:

- fetch data only from static JSON/HTML assets generated by scripts / guards,
- never issue direct DB queries or LM API calls from the browser,
- treat all backend integration as **conditional**.

If a required JSON file is absent, the Shell MUST:

- display a clear, friendly explanation,
- suggest which command to run (e.g., `make ci.exports.smoke`,
  `make atlas.lm.indicator`),
- remain fully interactive in other sections.

---

## 7. WHEN / THEN Offline Behavior

For every backend-dependent panel, the UI MUST:

- Explicitly show "When backend X is online, this panel will activate"
  when data is missing or stale.
- Avoid technical jargon like "psycopg.OperationalError" in the UI.

Examples:

- DB off → "Database appears offline. When Postgres is available and DB
  health passes, this panel will show live graph/DB stats."
- LM off → "LM Studio appears offline or unreachable. When LM is healthy,
  you'll see model usage and health metrics here."

---

## 8. Autopilot Stub (Future)

The Shell reserves space on the Overview panel for an **Orchestrator Autopilot
Input**:

- A single text box where the operator can describe an intent
  (e.g., "Show me what's going on with my models and docs.").
- In v1, this is **local-only**:
  - Text is stored in client state or local storage,
  - No backend calls are made,
  - It acts as a "scratchpad of orchestrator intents".

Future versions may wire this into controlled agents / pmagent commands, but
this document requires that v1 have **no side effects** beyond local state.

---

## 9. Testing Requirements

- Shell must render without DB or LM (purely hermetic) using:
  - existing smoke exports,
  - or stubbed static JSON files.
- Any missing JSON must result in a rendered, informative UI, not a crash.
- Navigation between tools must work without full-page reloads.
- Accessibility: icons require `aria-label` and tooltips; tiles and buttons
  must be keyboard reachable.

