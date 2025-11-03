# AGENTS.md - Graph Visualization WebUI

## Directory Purpose

The `webui/graph/` directory contains a React-based interactive visualization application for exploring semantic concept networks. Built with modern web technologies for real-time graph exploration and analysis.

## Architecture

### Tech Stack

- **React 18**: Component-based UI framework
- **Vite**: Fast development server and build tool
- **Visx**: D3-powered visualization library for graphs
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling

### Key Components

#### `GraphView.tsx` - Main Visualization Component

**Purpose**: Interactive force-directed graph visualization
**Features**:

- D3 force simulation for natural graph layout
- Cluster-based node coloring
- Size-coded nodes by degree centrality
- Interactive node selection and hover effects
- Zoom and pan controls
- Real-time data loading from JSON exports

#### `NodeDetails.tsx` - Information Panel

**Purpose**: Display detailed metrics for selected nodes
**Features**:

- Node ID and label display
- Centrality measures (degree, betweenness, eigenvector)
- Cluster membership
- Formatted numerical display

#### `GraphStats.tsx` - Statistics Dashboard

**Purpose**: Display high-level network statistics and metrics
**Features**:

- Real-time stats cards (nodes, edges, clusters)
- Centrality averages (degree, betweenness, eigenvector)
- Cluster metrics (density, diversity) from backend analysis
- Responsive grid layout with loading states

#### `MetaPanel.tsx` - Performance & Metadata Display (P11 Sprint 2)

**Purpose**: Show envelope metadata and performance indicators
**Features**:

- Load time performance badge (green <200ms, yellow <500ms, red ≥500ms)
- Color-coded visual indicator with hover tooltip
- Real-time fetch from `/var/ui/perf.json`
- Graceful fallback for missing performance data
- Metadata display with JSON formatting

#### `MetricsDashboard.tsx` - Development Metrics Visualization (P11 Sprint 2)

**Purpose**: Developer-focused metrics trends and analytics
**Features**:

- D3-powered line charts for historical metrics
- SVG export functionality for sharing
- Real-time data loading from `/var/ui/metrics.jsonl`
- Configurable chart dimensions and styling
- Error handling for missing metrics data

#### `GraphDashboard.tsx` - Main Page Layout

**Purpose**: Orchestrate the complete visualization experience
**Features**:

- Responsive grid layout
- Error handling and loading states
- Metadata display (node/edge counts)
- Integration with data loading hooks
- Performance badge integration (MetaPanel)
- Dual views toggle (user badges + dev metrics dashboard)
- WebGL escalation modal for large datasets (>50k nodes or >3s TTI)
- Automatic performance monitoring and optimization recommendations

#### `GraphPreview.tsx` - Large Dataset Preview (Phase 2.2)

**Purpose**: Lightweight preview component for datasets >10k nodes
**Features**:

- Summary statistics grid (nodes, edges, clusters, temporal patterns, forecasts, correlations)
- Lazy pagination for node chunks (1000 nodes per page)
- Performance estimates (memory usage, estimated TTI)
- Progressive enhancement (summary → details toggle)
- Export summary functionality (stub for future implementation)

#### `usePerformance.ts` - Performance Monitoring Hook (Phase 2.3)

**Purpose**: Track and analyze rendering performance for optimization decisions
**Features**:

- Time-to-Interactive (TTI) measurement
- FPS monitoring during interactions
- Memory usage tracking (optional, privacy-respecting)
- DOM node counting for complexity assessment
- Automated performance recommendations (WebGL, virtualization, simplification)
- Configurable thresholds for different performance metrics

#### `DebugPanel.tsx` - Performance Debug Panel (Phase 4)

**Purpose**: Detailed performance debugging interface with comprehensive metrics display
**Features**:

- Tabbed interface (Core Metrics, Recommendations, Graph Stats)
- Real-time performance indicators with status colors and icons
- Detailed recommendations with actionable steps
- Graph rendering statistics (visible/total nodes, zoom level, culling efficiency)
- ARIA-compliant with keyboard navigation and screen reader support
- Modal overlay with backdrop dismissal

**Integration**: Accessible via PerformanceBadge clicks in GraphDashboard header

#### `PerformanceBadge.tsx` - Performance Status Indicator (Phase 4)

**Purpose**: Visual performance status badge with click-to-debug functionality
**Features**:

- Color-coded status (green=good, yellow=warning, red=error)
- Summary metrics display (TTI, FPS, memory, issue count)
- Hover tooltips with detailed status messages
- Click handler to open DebugPanel
- Configurable size and detail level
- Trend indicators for performance changes

**Integration**: Embedded in GraphDashboard header next to dataset statistics

#### `MetricsDashboard.tsx` - Performance Analytics Dashboard (Phase 4)

**Purpose**: Development-focused performance trends and historical analytics
**Features**:

- Time-range selection (1min, 5min, 15min) for historical data
- Real-time sparkline charts for key metrics
- Trend analysis with percentage changes vs previous periods
- Performance recommendations with priority levels
- Graph rendering metrics integration
- Data export functionality (JSON/CSV)
- Auto-refresh toggle for continuous monitoring

**Integration**: Standalone page accessible via routing, receives graph metrics from parent components

#### `TemporalExplorer.tsx` - Phase 8 Temporal Pattern Visualization (NEW)

**Purpose**: Interactive exploration of time-series patterns across biblical texts
**Features**:

- Time series line charts with rolling window overlays
- Change point indicators for detected transitions
- Interactive filtering by series, unit (verse/chapter), and window size
- Series statistics display (volatility, length, metadata)
- Responsive design with loading and error states
- Real-time API data fetching from `/api/v1/temporal`

#### `ForecastPanel.tsx` - Phase 8 Predictive Forecasting (NEW)

**Purpose**: Display and compare predictive forecasts for temporal patterns
**Features**:

- Historical + forecast line charts with uncertainty bands
- Model performance metrics (RMSE, MAE) display
- Interactive series selection and horizon adjustment
- Prediction intervals with configurable confidence levels
- Comparative analysis across different forecasting models
- Real-time API data fetching from `/api/v1/forecast`

### Data Flow

1. **Data Loading**: `useGraphData` hook fetches from `/exports/graph_latest.json`
2. **Stats Loading**: `useGraphStats` hook fetches from `/exports/graph_stats.json`
3. **Graph Rendering**: Visx components render force-directed layout
4. **User Interaction**: Node clicks update selection state
5. **Details Display**: Selected node metrics shown in sidebar

## Metrics Hooks

### `useGraphStats.ts` - Statistics Data Hook

**Purpose**: Load and provide network statistics for dashboard cards
**Data Sources**:

- Primary: `/exports/graph_stats.json` (static file from `scripts/export_stats.py`)
- Fallback: `/exports/graph_latest.json` (graph data with basic counts)
- Backup: `/api/stats` (on-demand API endpoint if implemented)
  **Features**:
- Automatic data fetching on component mount
- Graceful fallback handling for missing data sources
- TypeScript interfaces for type safety
- Loading state management

### Statistics Display

**Cards**: nodes, edges, clusters, avg_degree, avg_cluster_density, avg_cluster_diversity
**Formatting**: Proper number formatting with decimal precision
**Layout**: Responsive 2-column grid with shadow styling

#### GraphStats.tsx & useGraphStats.ts

Implements PR-017 metrics visualization.
**Verification Rules:** 016 (contract sync), 021 (stats proof), 022 (viz contract sync).
**Testing:** `npm run test:ci` runs `__tests__/GraphStats.test.tsx`.
**Data Flow:** export_stats.py → graph_stats.json → useGraphStats → GraphStats.tsx → GraphDashboard.tsx.

## Performance Monitoring & Large Dataset Handling

### Viewport Culling (Phase 2.1)

**Purpose**: Optimize rendering performance for large graphs (>10k nodes)
**Implementation**:

- Automatic detection of large datasets (>10k nodes triggers optimizations)
- Viewport-based filtering of nodes and edges to visible area
- Label hiding for non-selected/hovered nodes in large mode
- Zoom and pan controls with mouse wheel and drag interactions
- Performance overlay showing visible node count and WebGL recommendations

**Performance Gains**:
- 100k nodes: ~5-10% visible nodes rendered (90%+ reduction)
- TTI maintained under 500ms threshold
- Memory usage reduced through selective rendering

### Performance Profiling Hook (usePerformance.ts)

**Metrics Tracked**:
- **TTI (Time to Interactive)**: End-to-end load time measurement
- **FPS**: Frames per second during user interactions
- **Memory Usage**: Optional heap size monitoring (privacy-respecting)
- **DOM Nodes**: Rendered element count for complexity assessment
- **Render Time**: Individual component render duration

**Recommendations Engine**:
- **WebGL Escalation**: Triggered at >3s TTI or >50k nodes
- **Virtualization**: Memory usage exceeds 200MB threshold
- **Simplification**: DOM node count >10k suggests optimization

**Integration**: Wired into GraphView and GraphDashboard for real-time monitoring

### WebGL Escalation Modal

**Trigger Conditions**:
- Dataset size >50k nodes
- TTI >3s with >10k nodes
- Performance hook recommends WebGL

**Features**:
- Modal dialog with performance metrics display
- User choice between WebGL acceleration or continued SVG rendering
- Escalation tracking via `/var/ui/escalation.json`
- Graceful fallback for missing WebGL support

**Data Flow**: Performance monitoring → recommendations → modal → escalation.json → renderer switch

## Development Workflow

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev        # localhost:5173 with hot reload

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

### Integration with Pipeline

```bash
# Generate fresh data
make exports.graph

# Launch visualization
make webui

# Browser opens automatically at localhost:5173
```

## Configuration

### Vite Configuration

- **Development Server**: Port 5173 with hot reload
- **Proxy Setup**: Routes `/exports/*` to backend server
- **Build Output**: Optimized production bundle

### Data Source

- **Primary Source**: `/exports/graph_latest.json`
- **Fallback**: Error handling for missing data
- **Refresh**: Manual page reload for updated data

## Performance Considerations

### Large Graph Handling

- **Force Simulation**: Configured for graphs up to 10,000 nodes
- **Rendering Optimization**: Efficient DOM updates
- **Memory Management**: Garbage collection for large datasets

### Browser Compatibility

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+
- **WebGL Fallback**: Canvas-based rendering for older browsers

## Features

### Interactive Features

- **Node Selection**: Click nodes to view detailed metrics
- **Hover Effects**: Visual feedback on node hover
- **Zoom Controls**: Mouse wheel and touch gestures
- **Pan Controls**: Drag to navigate large graphs

### Visual Encoding

- **Node Size**: Proportional to degree centrality
- **Node Color**: Categorical coloring by cluster membership
- **Edge Width**: Proportional to relationship strength
- **Edge Opacity**: Visual strength indication

### Data Display

- **Node Metrics**: Degree, betweenness, eigenvector centrality
- **Graph Statistics**: Total nodes, edges, clusters
- **Export Timestamp**: Data freshness indicator

## Deployment

### Development Deployment

```bash
# Local development
npm run dev
```

### Production Build

```bash
# Create optimized build
npm run build

# Serve static files
npm run preview
```

### Integration Options

- **Standalone**: Serve as static files from any web server
- **Embedded**: Integrate into larger applications
- **Docker**: Containerized deployment option

## Testing Strategy

### Component Testing

- **Unit Tests**: Individual component behavior
- **Integration Tests**: Data loading and rendering
- **Visual Tests**: Screenshot comparisons

### Performance Testing

- **Load Testing**: Large graph rendering performance
- **Memory Testing**: Memory usage with big datasets
- **Responsiveness**: Frame rate and interaction latency

## Accessibility

### Keyboard Navigation

- **Tab Navigation**: Accessible focus management
- **Enter/Space**: Activate node selection
- **Arrow Keys**: Navigate between nodes

### Screen Reader Support

- **ARIA Labels**: Semantic HTML structure
- **Live Regions**: Dynamic content announcements
- **High Contrast**: Sufficient color contrast ratios

## Related ADRs

| Component/Function   | Related ADRs                                      |
| -------------------- | ------------------------------------------------- |
| GraphView.tsx        | ADR-023 (Visualization API Spec)                  |
| GraphStats.tsx       | ADR-016 (Metrics Contract), ADR-017 (Stats Proof) |
| TemporalExplorer.tsx | ADR-023 (Visualization API Spec)                  |
| ForecastPanel.tsx    | ADR-023 (Visualization API Spec)                  |
| useGraphStats.ts     | ADR-016 (Metrics Contract)                        |

## Future Enhancements

### Planned Features

- **Search/Filter**: Node search and filtering capabilities
- **Multiple Layouts**: Alternative graph layout algorithms
- **Export Options**: Save visualizations as images
- **Animation**: Smooth transitions between states

### Performance Optimizations

- **WebGL Rendering**: Hardware-accelerated graphics
- **Virtual Scrolling**: Handle extremely large graphs
- **Progressive Loading**: Load graph data incrementally

### Advanced Analytics

- **Path Finding**: Shortest path visualization
- **Subgraph Extraction**: Focus on specific node neighborhoods
- **Temporal Analysis**: Show graph evolution over time
