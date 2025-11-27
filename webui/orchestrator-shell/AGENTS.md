# AGENTS.md - webui/orchestrator-shell Directory

## Directory Purpose

The `webui/orchestrator-shell/` directory contains orchestrator-shell components for the Gematria analysis pipeline.

## Key Components

- **OrchestratorShell.tsx**: Main shell component that provides the layout (header, left rail, main canvas)
- **OrchestratorOverview.tsx**: Overview dashboard showing system signals, MCP RO proof status, and autopilot intent log
- **MCPROProofTile.tsx**: Tile component displaying MCP read-only proof status (E21-E24 proofs, endpoint count, last updated timestamp)
- **BrowserVerifiedBadge.tsx**: Badge component displaying browser verification status (verified pages, screenshot count, link to screenshots)
- **Header.tsx**: Header component with system status indicators
- **LeftRail.tsx**: Navigation rail for switching between different panels
- **MainCanvas.tsx**: Main content area that renders the active panel based on selection

## API Contracts

<!-- Add function/class signatures and contracts here -->

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

### Critical Patterns (Locked Down)

#### SVG Icon Sizing
**ALL SVG icons in SearchBar and other components MUST include explicit inline size constraints:**
```tsx
<svg className="h-5 w-5 text-gray-400" style={{ width: '20px', height: '20px', flexShrink: 0 }}>
```
**Why:** Without explicit pixel constraints, SVGs can scale to viewport width (e.g., 1679px), creating "giant Q" visual bugs.

#### Live Search Default
**All search tabs (SearchTab, SemanticSearchTab, CrossLanguageTab) MUST default to live mode:**
```tsx
const [liveMode, setLiveMode] = useState(true); // NOT false
```
**Rationale:** Users expect live data by default. Static mode is a fallback.

#### API Endpoint Contracts
**Frontend API calls MUST match backend router signatures:**
- Check `src/services/routers/biblescholar.py` for exact parameter names
- Search endpoint: `GET /api/bible/search?q=...&limit=20&translation=KJV` (NOT POST with body)
- Semantic endpoint: `GET /api/bible/semantic?q=...&limit=20` (parameter is `q`, not `query`)
- Map response structures to match backend DTOs exactly

#### Browser Verification
**MANDATORY for all UI changes:**
- Use `browser_take_screenshot` to verify visual state
- Use `browser_evaluate` to check element sizes and positions
- Verify no console errors with `browser_console_messages`
- Do not claim fixes are complete without visual verification

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
