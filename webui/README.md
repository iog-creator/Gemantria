# WebUI Directory

## Overview

The `webui/` directory contains React-based web user interfaces for exploring and visualizing gematria data. This includes interactive graph visualizations, dashboards, and temporal pattern analysis tools.

## Directory Structure

### `graph/` - Main Graph Visualization Application

- **Purpose**: Interactive semantic concept network visualization
- **Tech Stack**: React 18, Vite, Visx, TypeScript, Tailwind CSS
- **Features**: Force-directed graph layout, centrality metrics, cluster analysis, temporal patterns, forecasting
- **Entry Point**: `npm run dev` (localhost:5173)

### `dashboard/` - Dashboard Components

- **Purpose**: Reusable dashboard components for metrics and analytics
- **Components**: ForecastPanel, MetricsPanel, PatternExplorer, TemporalExplorer
- **Integration**: Shared components for graph visualization and analysis

## Development Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd webui/graph
npm install

cd ../dashboard
npm install
```

### Development Servers

```bash
# Graph visualization (main app)
cd webui/graph
npm run dev

# Dashboard components (if separate dev server needed)
cd webui/dashboard
npm run dev
```

## Build Process

### Production Builds

```bash
# Graph visualization
cd webui/graph
npm run build

# Dashboard components
cd webui/dashboard
npm run build
```

### Integration with Pipeline

```bash
# Generate fresh data for visualizations
make exports.graph

# Launch main visualization
make webui
```

## Architecture

### Data Flow

1. **Data Sources**: JSON exports from `scripts/export_stats.py` and `scripts/export_graph.py`
2. **API Endpoints**: REST API for dynamic data (`/api/v1/temporal`, `/api/v1/forecast`)
3. **Visualization**: React components render interactive charts and graphs
4. **State Management**: React hooks manage loading states and user interactions

### Component Hierarchy

```
App
├── GraphDashboard
│   ├── GraphView (main visualization)
│   ├── GraphStats (metrics cards)
│   ├── NodeDetails (selected node info)
│   └── TemporalExplorer (Phase 8)
└── ForecastPanel (Phase 8)
```

## Features

### Graph Visualization (`graph/`)

- **Interactive Exploration**: Force-directed layout with zoom/pan
- **Node Metrics**: Degree, betweenness, eigenvector centrality
- **Cluster Analysis**: Community detection and coloring
- **Temporal Patterns**: Time-series analysis across biblical texts
- **Forecasting**: Predictive modeling with uncertainty bands

### Dashboard Components (`dashboard/`)

- **Metrics Panels**: Statistical summaries and KPIs
- **Pattern Exploration**: Interactive data analysis tools
- **Temporal Analysis**: Time-series visualization components
- **Forecast Displays**: Prediction intervals and model comparison

## Testing

### Unit Tests

```bash
cd webui/graph
npm test

cd webui/dashboard
npm test
```

### Integration Tests

```bash
# Full pipeline integration
make test.integration
```

### Visual Regression Tests

```bash
# Screenshot comparison tests
npm run test:visual
```

## Deployment

### Standalone Deployment

```bash
# Build and serve static files
npm run build
npm run preview
```

### Temporal Export Integration

The UI includes download links for temporal analysis exports (`temporal_strip.csv` and `temporal_summary.md`). To enable these downloads:

1. **Generate exports** (from project root):
   ```bash
   make ui.temporal.summary OUTDIR=ui/out
   ```

2. **Copy to public directory** (before build):
   ```bash
   # Ensure ui/out/ files are in the web server's public path
   cp ui/out/temporal_strip.csv webui/graph/public/ui/out/
   cp ui/out/temporal_summary.md webui/graph/public/ui/out/

   # Or create symlinks for development
   mkdir -p webui/graph/public/ui/out
   ln -sf ../../../../ui/out/temporal_strip.csv webui/graph/public/ui/out/
   ln -sf ../../../../ui/out/temporal_summary.md webui/graph/public/ui/out/
   ```

3. **Version exports** (recommended for production):
   ```bash
   # Tag exports with commit hash for cache busting
   COMMIT=$(git rev-parse --short HEAD)
   cp ui/out/temporal_strip.csv "webui/graph/public/ui/out/temporal_strip_${COMMIT}.csv"
   cp ui/out/temporal_summary.md "webui/graph/public/ui/out/temporal_summary_${COMMIT}.md"

   # Update component to use versioned paths
   ```

> **Note**: Download links are always visible but will fail gracefully if files don't exist. Keep exports local-only; do not commit to repository.

### Integration Options

- **Static Hosting**: Deploy built files to any web server
- **Embedded**: Integrate components into larger applications
- **Docker**: Containerized deployment with nginx

## Performance Considerations

### Bundle Optimization

- **Code Splitting**: Lazy loading of components
- **Tree Shaking**: Remove unused dependencies
- **Compression**: Gzip/brotli compression for assets

### Runtime Performance

- **Virtual Scrolling**: Handle large datasets efficiently
- **WebGL Rendering**: Hardware-accelerated graphics for graphs
- **Progressive Loading**: Incremental data loading for better UX

## Browser Support

### Supported Browsers

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Fallbacks

- **Canvas Rendering**: Fallback for older browsers without WebGL
- **Simplified Layouts**: Graceful degradation for limited devices

## Accessibility

### WCAG Compliance

- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Readers**: ARIA labels and semantic HTML
- **High Contrast**: Sufficient color contrast ratios
- **Focus Management**: Clear focus indicators and logical tab order

## Development Guidelines

### Component Development

- **TypeScript**: Strict typing for all components
- **Testing**: Unit tests for all components
- **Storybook**: Component documentation and testing
- **Linting**: ESLint and Prettier for code quality

### Data Handling

- **Type Safety**: Strong typing for API responses
- **Error Handling**: Graceful error states and fallbacks
- **Loading States**: Proper loading indicators and skeletons

### Styling

- **Tailwind CSS**: Utility-first styling approach
- **Responsive Design**: Mobile-first responsive layouts
- **Dark Mode**: Support for light/dark theme switching

## Related Documentation

- **Parent**: [../README.md](../README.md) - Project overview
- **Graph Visualization**: [graph/README.md](graph/README.md) - Detailed graph app docs
- **Dashboard Components**: [dashboard/AGENTS.md](dashboard/AGENTS.md) - Component specifications
- **API Integration**: [../share/AGENTS.md](../share/AGENTS.md) - API endpoint documentation

## Contributing

### Code Standards

- Follow existing TypeScript and React patterns
- Maintain component composition and reusability
- Ensure accessibility compliance
- Add tests for new functionality

### Review Process

- Code review required for all changes
- Visual regression tests must pass
- Accessibility audit for UI changes
- Performance impact assessment for rendering changes
