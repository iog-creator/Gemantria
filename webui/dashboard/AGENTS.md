# AGENTS.md - Dashboard WebUI Directory

## Directory Purpose

The `webui/dashboard/` directory contains React components for the advanced analytics dashboard. This provides interactive visualization of temporal patterns, forecasting, and complex analytics beyond the basic graph viewer.

## Key Components

### `TemporalExplorer.tsx` - Phase 8 Temporal Pattern Explorer

**Purpose**: Interactive exploration of time-series patterns across biblical texts
**Features**:

- **Time Series Visualization**: Line charts showing concept frequency over verse/chapter indices
- **Rolling Window Analysis**: Interactive controls for window size and unit selection
- **Change Point Detection**: Visual indicators for statistically significant pattern shifts
- **Series Statistics**: Display of volatility metrics and pattern characteristics
  **Requirements**:
- Real-time API data fetching from `/api/v1/temporal`
- Responsive design for mobile and desktop viewing
- Loading states and error handling
- TypeScript interfaces for data validation

### `ForecastPanel.tsx` - Phase 8 Predictive Forecasting

**Purpose**: Display and compare predictive forecasts for temporal patterns
**Features**:

- **Forecast Visualization**: Combined historical + predicted value charts
- **Model Comparison**: Side-by-side display of different forecasting algorithms
- **Confidence Intervals**: Uncertainty bands around forecast predictions
- **Performance Metrics**: RMSE and MAE display for forecast accuracy
  **Requirements**:
- Real-time API data fetching from `/api/v1/forecast`
- Interactive horizon and series selection
- TypeScript interfaces matching API response schemas
- Responsive grid layout with proper error boundaries

### `MetricsPanel.tsx` - Advanced Analytics Dashboard

**Purpose**: Comprehensive display of pipeline and network metrics
**Features**:

- **KPI Cards**: Key performance indicators with sparkline charts
- **Network Statistics**: Advanced graph topology metrics
- **Performance Trends**: Historical performance data visualization
- **Health Indicators**: System and service health status
  **Requirements**:
- Integration with `/api/v1/stats` and `/api/v1/correlations`
- Real-time data updates with appropriate caching
- Responsive card-based layout
- Comprehensive error handling and loading states

### `PatternExplorer.tsx` - Cross-Book Pattern Visualization

**Purpose**: Interactive exploration of correlation patterns across biblical books
**Features**:

- **Chord Diagrams**: Multi-book relationship visualization
- **Heatmap Views**: Correlation strength matrices
- **Filtering Controls**: Metric-based filtering (support, lift, confidence)
- **Tooltip Details**: Shared concept lists and statistical significance
  **Requirements**:
- API integration with `/api/v1/patterns`
- D3-powered interactive visualizations
- Responsive design for large datasets
- TypeScript type safety throughout

## Architecture

### Tech Stack

- **React 18**: Component-based UI framework with hooks
- **TypeScript**: Type-safe development and API contracts
- **Vite**: Fast development server and optimized builds
- **Tailwind CSS**: Utility-first responsive styling
- **Recharts/D3**: Data visualization libraries

### Data Flow

1. **API Integration**: Components fetch data from FastAPI endpoints
2. **State Management**: Local component state with loading/error handling
3. **Data Processing**: Client-side data transformation and filtering
4. **Visualization**: Render visualizations with interactive controls
5. **User Interaction**: Event handling and state updates

### Component Patterns

- **Hook-based**: Custom hooks for data fetching and state management
- **Error Boundaries**: Graceful error handling and user feedback
- **Loading States**: Skeleton screens and progress indicators
- **Responsive Design**: Mobile-first approach with breakpoint handling

## API Integration

### Endpoint Contracts

| Component        | Endpoint           | Data Structure                  |
| ---------------- | ------------------ | ------------------------------- |
| TemporalExplorer | `/api/v1/temporal` | TemporalPattern[] with metadata |
| ForecastPanel    | `/api/v1/forecast` | Forecast[] with intervals       |
| MetricsPanel     | `/api/v1/stats`    | Network statistics object       |
| PatternExplorer  | `/api/v1/patterns` | Pattern correlations array      |

### Error Handling

- **Network Errors**: Retry logic with exponential backoff
- **Data Errors**: Validation against TypeScript interfaces
- **Timeout Handling**: Appropriate loading states and user feedback
- **Fallback Data**: Graceful degradation when APIs unavailable

## Performance Considerations

### Rendering Optimization

- **Virtual Scrolling**: Handle large datasets efficiently
- **Memoization**: Prevent unnecessary re-renders
- **Lazy Loading**: Component and data loading optimization
- **Bundle Splitting**: Code splitting for faster initial loads

### Data Management

- **Caching Strategy**: Appropriate cache headers and client-side caching
- **Pagination**: Efficient handling of large result sets
- **Incremental Updates**: Real-time data updates without full refreshes
- **Memory Management**: Cleanup of event listeners and subscriptions

## Testing Strategy

### Component Testing

- **Unit Tests**: Individual component logic and rendering
- **Integration Tests**: API integration and data flow
- **Visual Tests**: Screenshot comparisons for UI consistency
- **Accessibility Tests**: Keyboard navigation and screen reader support

### End-to-End Testing

- **User Journeys**: Complete workflows from data loading to interaction
- **Performance Tests**: Rendering performance with large datasets
- **Cross-browser**: Compatibility across supported browsers

## Accessibility

### Keyboard Navigation

- **Tab Order**: Logical focus management through interactive elements
- **Enter/Space**: Activation of interactive controls
- **Arrow Keys**: Navigation within data visualizations
- **Escape**: Close modals and return to main content

### Screen Reader Support

- **ARIA Labels**: Semantic labeling of interactive elements
- **Live Regions**: Announcement of dynamic content changes
- **High Contrast**: Sufficient color contrast ratios
- **Semantic HTML**: Proper heading hierarchy and landmark roles

## Deployment

### Build Process

- **Vite Optimization**: Tree shaking and code splitting
- **Asset Optimization**: Image and font optimization
- **Bundle Analysis**: Size monitoring and optimization
- **CDN Integration**: Static asset delivery optimization

### Integration Options

- **Standalone**: Serve as static files from any web server
- **Embedded**: Integration into larger applications
- **Micro-frontend**: Independent deployment with shared routing
- **Docker**: Containerized deployment with nginx

## Housekeeping (Rule 058)

After ANY code changes in this directory, run comprehensive housekeeping:

```bash
# Rule 058 mandatory housekeeping checklist
python3 scripts/rules_audit.py
make share.sync
python3 scripts/generate_forest.py
ruff format --check . && ruff check .
# Check if ADR needed/updated (Rule 029)
PYTHONPATH=. python3 -m pytest tests/ -v --tb=short
# Verify docs updated (AGENTS.md, SSOT, README)
```

**DO NOT SKIP ANY STEP.** See [Rule 058](../../.cursor/rules/058-auto-housekeeping.mdc) for complete checklist.


## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Graph Viewer**: [../graph/AGENTS.md](../graph/AGENTS.md) - Basic visualization
- **API Server**: [../../src/services/AGENTS.md](../../src/services/AGENTS.md) - Backend integration
- **Rules**: [.cursor/rules/033-visualization-api-validation.mdc](../../.cursor/rules/033-visualization-api-validation.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - API response schemas
