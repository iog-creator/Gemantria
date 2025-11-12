# PLAN-081 — Orchestrator Dashboard Polish (Atlas Tile + Browser-Verified Badge)

**Context.** v0.0.3 is finalized with browser verification screenshots and RO MCP guard proofs. This plan adds **orchestrator-first** dashboard elements to provide immediate clarity on proofs and status without backend changes.

## Objectives

- **Atlas Tile:** Add "MCP RO Proof" tile showing endpoint count + last tagproof timestamp.
- **Browser-Verified Badge:** Add visual badge linking to the two browser verification screenshots (`browser_verified_index.png`, `browser_verified_mcp_catalog_view.png`).
- **Visual Tone:** Keep clean, "semi-technical orchestrator" aesthetic; no backend changes.

## Deliverables

- **Atlas Dashboard Component:**
  - New tile component: `webui/graph/components/MCPROProofTile.tsx` (or equivalent)
  - Displays: endpoint count from `mcp.v_catalog`, last tagproof time from `share/releases/*/tagproof/tag_run.view.final.json`
  - Links to tagproof artifacts when available

- **Browser Verification Badge:**
  - Badge component: `webui/graph/components/BrowserVerifiedBadge.tsx` (or equivalent)
  - Links to `share/releases/v0.0.3/webproof/browser_verified_*.png`
  - Visual indicator (checkmark icon + "Browser-Verified" text)

- **Integration:**
  - Add both components to main orchestrator dashboard view
  - Ensure responsive layout and accessibility

## Acceptance Criteria

- Atlas tile displays endpoint count (≥3 expected) and last tagproof timestamp.
- Browser-Verified badge is visible and links to both screenshots.
- Visual design matches "semi-technical orchestrator" tone (clean, informative, not cluttered).
- No backend changes; all data sourced from existing artifacts/JSON files.
- `ruff` green (if TypeScript/React linting configured).
- Browser verification: tile and badge render correctly (visual check).

## Out-of-Scope

- Backend API changes or new endpoints.
- Database schema modifications.
- CI/CD workflow changes.
- Tool Bus or guard implementation changes.

## Plan-of-Record (one PR)

- **PR: ui/orchestrator-dashboard-polish**

  - Add MCP RO Proof tile component.
  - Add Browser-Verified badge component.
  - Integrate into main dashboard view.
  - Update component documentation if needed.

  - Evidence bundle: ruff tail, visual screenshots of updated dashboard, component file list.

