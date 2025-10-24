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

#### `GraphDashboard.tsx` - Main Page Layout

**Purpose**: Orchestrate the complete visualization experience
**Features**:

- Responsive grid layout
- Error handling and loading states
- Metadata display (node/edge counts)
- Integration with data loading hooks

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
