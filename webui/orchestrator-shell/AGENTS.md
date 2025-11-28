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

<!-- Add coding standards and patterns specific to this directory here -->

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
