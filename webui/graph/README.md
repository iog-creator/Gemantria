# Graph Visualization WebUI

React-based interactive graph visualization for Gemantria semantic networks.

## Overview

This web application provides:
- **Interactive graph visualization** of semantic concept networks
- **Force-directed layouts** with cluster coloring
- **Node exploration** with detailed centrality metrics
- **Real-time data loading** from exported JSON files
- **Responsive design** for large network exploration

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Visx** for graph visualization and D3 integration
- **Tailwind CSS** for styling
- **React Router** for navigation

## Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
cd webui/graph
npm install
```

### Development Server
```bash
npm run dev
# Opens http://localhost:5173
```

### Build for Production
```bash
npm run build
npm run preview  # Test production build
```

## Data Sources

The visualization loads data from `exports/graph_latest.json` which contains:
- **Nodes**: Concepts with positions, labels, and metadata
- **Edges**: Semantic relationships with strength scores
- **Clusters**: Community detection results
- **Centrality metrics**: Degree, betweenness, eigenvector centrality

## Key Components

### GraphView (`src/components/GraphView.tsx`)
Main graph visualization component using Visx force-directed layout.

### NodeDetails (`src/components/NodeDetails.tsx`)
Detailed node information panel with centrality metrics and concept details.

### GraphDashboard (`src/pages/GraphDashboard.tsx`)
Main dashboard page integrating all components.

## Data Flow

```
Pipeline → exports/graph_latest.json → GraphDashboard → GraphView → NodeDetails
```

## Features

- **Zoom & Pan**: Mouse wheel and drag navigation
- **Node Selection**: Click nodes for detailed information
- **Cluster Coloring**: Automatic color assignment by community
- **Responsive Layout**: Adapts to window size changes
- **Search/Filter**: Future feature for large networks

## Deployment

### Local Development
```bash
make webui  # Launches development server
```

### Production Build
```bash
npm run build
# Deploy dist/ folder to web server
```

## API Integration

Data is loaded via:
- `src/hooks/useGraphData.ts` - Graph data fetching hook
- Static JSON files in `exports/` directory
- Future: Real-time API endpoints

## Performance Considerations

- **Large networks**: May require virtualization for 1000+ nodes
- **Browser limits**: Chrome handles up to ~10k nodes well
- **Memory usage**: Force-directed layouts are computationally intensive

## Related Documentation

- [Pipeline Exports](../scripts/README.md#export_graphpy)
- [Graph Analysis](../scripts/README.md#analyze_graphpy)
- [WebUI Integration](../AGENTS.md#webui-visualization)
