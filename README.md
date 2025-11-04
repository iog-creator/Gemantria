# Gemantria Envelope Viewer

A local-only React + Next.js dashboard for visualizing Phase-9 ingestion envelopes.

## Features

- **File Picker + Drag-Drop**: Load envelope JSON files without network
- **React Flow Graph**: Pan, zoom, and explore node/edge graph
- **Temporal Strip**: Visualize metadata and snapshot timing
- **Metrics Panel**: View node/edge counts and graph density
- **Smart Filtering**: Filter by label, node type, relation type, and edge weight
- **Export**: Save filtered data as JSON (local)
- **Type-Safe**: Full TypeScript support with Envelope schema

## Setup

### Prerequisites
- Node.js 18+
- `/tmp/p9-ingest-envelope.json` (built via `make ingest.local.envelope`)

### Local Development

\`\`\`bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open http://localhost:3000
\`\`\`

## Loading Envelope

### Option 1: File Picker (Recommended)
1. Click "Upload Envelope" button
2. Select your `p9-ingest-envelope.json` file
3. Or drag-drop the file onto the upload area

### Option 2: Dev HTTP (Automatic)
1. Copy envelope to `public/envelope.json`
2. App loads automatically on startup

## Architecture

\`\`\`
src/
  components/          # UI components
  lib/
    types.ts          # Envelope schema
    providers.ts      # File/HTTP adapters
    events.ts         # Event bus
  app/
    page.tsx          # Main dashboard
\`\`\`

## Performance

- Supports ~5k nodes / ~20k edges smoothly
- Circular layout with React Flow
- Client-side filtering (100ms budget)
- No network or database dependencies

## Events

The app emits:
- `envelopeLoaded`: When envelope is loaded
- `filterChanged`: When filters update
- `selectionChanged`: When graph selection changes

## Notes

- Local-only: No CI integration, no Node in CI
- Hermetic: All data processing in-browser
- gitignore: `ui/out/` (export directory)
