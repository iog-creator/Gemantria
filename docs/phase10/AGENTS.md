# AGENTS.md - Phase 10 Directory

## Directory Purpose

The `docs/phase10/` directory contains documentation for Phase 10 UI development, dashboard planning, and visualization interfaces. This directory documents the user interface architecture, component structure, and development workflows for the Gemantria web UI.

## Key Documents

### Phase 10 Documentation

- **STRUCTURE.md** - Phase-10 UI Structure Plan
  - Documents proposed UI layout and component organization
  - Defines hermetic policy (no Node/npm in CI, local dev only)
  - Specifies directory structure (`ui/public/`, `ui/src/app/`, etc.)
  - Provides local dev steps and CI stance
  - Outlines next development slices (P10-B, P10-C, P10-D)

- **DASHBOARD_PLAN.md** - Dashboard Development Plan
  - Documents dashboard architecture and component design
  - Specifies visualization requirements and data sources
  - Defines integration points with backend exports

- **UI_SPEC.md** - UI Specification Document
  - Detailed UI component specifications
  - Interaction patterns and user workflows
  - Visual design guidelines and accessibility requirements

## Documentation Standards

### UI Documentation Format

All Phase 10 documentation should include:

1. **Architecture** - UI structure and component organization
2. **Hermetic Policy** - CI restrictions (no Node/npm in CI)
3. **Local Dev** - Development setup and workflow procedures
4. **Component Specs** - Detailed component documentation
5. **Integration** - Backend data integration and envelope loading

### Hermetic CI Policy

- **No Node/npm in CI**: All UI work is local dev only
- **UI directory**: All UI work lives under `ui/` directory
- **Make targets**: `ui.dev.help` prints local instructions and HINTs in CI
- **No CI jobs**: No Node jobs added to CI workflows

## Development Guidelines

### Creating Phase 10 Documentation

1. **Document structure**: Specify UI directory layout and component organization
2. **Hermetic compliance**: Document CI restrictions and local-only workflows
3. **Dev procedures**: Provide step-by-step local development setup
4. **Component specs**: Document component APIs and integration points
5. **Next steps**: Outline development slices and priorities

### UI Development Standards

- **TypeScript**: Use TypeScript for type safety
- **Component structure**: Follow React/Next.js best practices
- **Envelope loading**: Load data from `/tmp/p9-ingest-envelope.json` or `share/exports/`
- **Local-only**: All UI development is local, not in CI

## Related Documentation

### UI Development

- **ui/README_UI.md**: UI development setup and instructions
- **docs/atlas/**: Atlas visualization documentation
- **Rule 056**: UI Generation Standard (Gemini 2.5 Pro primary, Claude Sonnet 4 fallback)

### Backend Integration

- **docs/consumers/**: Data consumer interfaces and export formats
- **scripts/extract/extract_all.py**: Unified envelope extraction
- **make ui.extract.all**: Extract envelope for UI consumption

## Integration with Governance

### Rule 056 - UI Generation Standard

Phase 10 documentation supports UI generation standards:

- **Model routing**: Documents Gemini 2.5 Pro (primary) and Claude Sonnet 4 (fallback)
- **Component structure**: Specifies React 18+, Next.js, Tailwind CSS
- **QA gates**: Documents frontend lint/test requirements

### Rule 046 - Hermetic CI Fallbacks

Phase 10 enforces hermetic CI policy:

- **No Node in CI**: UI work is local dev only
- **Make targets**: `ui.dev.help` provides local instructions
- **CI hints**: CI emits HINTs for UI development guidance

### Rule 067 - Atlas Webproof

Phase 10 UI supports browser-verified UI requirements:

- **Visual verification**: Procedures for browser-based UI verification
- **Screenshot procedures**: How to capture and verify visual evidence
- **Backlink validation**: Procedures for verifying webproof backlinks

## Maintenance Notes

- **Keep current**: Update Phase 10 docs when UI architecture changes
- **Test procedures**: Verify all local dev steps work as documented
- **Component updates**: Document new components and their integration
- **CI compliance**: Ensure UI development remains CI-hermetic
