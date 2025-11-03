<!-- 18696d49-fecc-43af-92d3-1b4282095ee9 bc9ed394-3720-4f9e-b30c-660c9975f6d8 -->
# UI Enhancement & Data Pipeline Improvement Plan

## Phase 1: Unified Data Extraction Pipeline

### 1.1 Create Unified Extract Script

**File**: `scripts/extract/extract_all.py`

- Merge graph_latest.json, temporal patterns, forecasting data, and correlations
- Generate unified envelope format with integrated attributes
- Support configurable dataset sizes (100, 1k, 10k, 100k+ nodes)
- Add validation against unified schema

### 1.2 Update Makefile Targets

**File**: `Makefile`

- Add `ui.extract.all` target with SIZE and OUTDIR parameters
- Wire into existing export chain

### 1.3 Document Plan Extension

**File**: `docs/PHASE11_PLAN.md` (if exists) or create new planning doc

- Record Sprint 1 extension decisions: unified pipe, minimalist UI, virtual rendering, dual metrics

## Phase 2: Large Dataset Rendering Optimization

### 2.1 Implement Virtual Scrolling for Graph

**File**: `webui/graph/src/components/GraphView.tsx`

- Add threshold detection (>10k nodes triggers chunked mode)
- Implement viewport-based rendering (only visible nodes)
- Add summary node for large datasets showing total count
- Optimize d3-force simulation for chunked data (reduce iterations)

### 2.2 Create Graph Preview Component

**File**: `webui/graph/src/components/GraphPreview.tsx` (new)

- Lightweight preview for large datasets
- Lazy loading strategy with pagination
- Summary statistics overlay
- Progressive enhancement from summary to detail

### 2.3 Add Performance Profiling

**File**: `webui/graph/src/hooks/usePerformance.ts` (new)

- Track render times, frame rates, memory usage
- Automatic optimization recommendations
- Export performance logs to metrics pipeline

## Phase 3: UI Beautification (Minimalist Modern)

### 3.1 Design System Implementation

**File**: `webui/graph/src/styles/theme.ts` (new)

- Color palette: soft blues (#4A90E2), grays (#F8F9FA), accent gold (#FFB84D)
- Typography: Inter or system font stack
- Spacing: 8px grid system
- Shadows: subtle elevation (0-3 levels)

### 3.2 Enhance Dashboard Layout

**File**: `webui/graph/src/pages/GraphDashboard.tsx`

- Replace gray background with gradient (light blue to white)
- Redesign stat cards with icons and subtle shadows
- Add smooth transitions (200ms ease-in-out)
- Implement responsive breakpoints (mobile-first)

### 3.3 Improve Graph Visualization

**File**: `webui/graph/src/components/GraphView.tsx`

- Better color palette for clusters (pastel with good contrast)
- Animated node interactions (scale on hover, pulse on select)
- Edge opacity based on strength (subtle to prominent)
- Add mini-map navigator for large graphs

### 3.4 Node Details Panel Redesign

**File**: `webui/graph/src/components/NodeDetails.tsx`

- Card-based layout with sections
- Add temporal timeline visualization if data available
- Display correlation heatmap for connected nodes
- Add copy-to-clipboard for node data

## Phase 4: Performance Monitoring Integration

### 4.1 Developer Debug Panel

**File**: `webui/graph/src/components/DebugPanel.tsx` (new)

- Collapsible panel (bottom-right, toggle with Ctrl+Shift+D)
- Real-time FPS counter, memory usage, render times
- Dataset size and optimization status
- Export diagnostics as JSON

### 4.2 User-Facing Performance Badges

**File**: `webui/graph/src/components/PerformanceBadge.tsx` (new)

- Small indicator showing load time (green <100ms, yellow <500ms, red >500ms)
- Dataset size badge with optimization status
- Integration with acceptance metrics (perf.json)

### 4.3 Metrics Dashboard Page

**File**: `webui/graph/src/pages/MetricsDashboard.tsx` (new)

- Historical trend charts from metrics.jsonl
- Performance comparison across runs
- Quality indicators (edge strength distribution)
- Export download links (temporal_strip.csv, summary.md)

## Phase 5: Data Management Improvements

### 5.1 Client-Side Caching

**File**: `webui/graph/src/utils/cache.ts` (new)

- IndexedDB storage for large envelopes
- Cache invalidation strategy (version-based)
- Background refresh with stale-while-revalidate

### 5.2 Enhanced Error Handling

**File**: `webui/graph/src/hooks/useGraphData.ts`

- Retry logic with exponential backoff
- Partial data loading (progressive enhancement)
- User-friendly error messages with recovery suggestions

### 5.3 Data Export Features

**File**: `webui/graph/src/components/ExportPanel.tsx` (new)

- Export current view as PNG/SVG
- Download filtered dataset as JSON
- Generate shareable URLs with view state

## Implementation Order

1. Phase 1 (Data Pipeline) - Foundation for testing
2. Phase 2 (Large Dataset) - Critical performance work
3. Phase 3 (UI Beauty) - Visual improvements
4. Phase 4 (Monitoring) - Observability
5. Phase 5 (Data Management) - Polish and reliability

## Testing Strategy

- Create synthetic datasets: 100, 1k, 10k, 100k nodes
- Run acceptance suite after each phase
- Visual regression testing for UI changes
- Performance benchmarks: render time <100ms (10k nodes), <500ms (100k nodes)
- Accessibility audit with updated components

## Success Metrics

- Load time improvement: >50% faster for 10k+ node graphs
- UI satisfaction: modern, clean, professional aesthetic
- Performance visibility: real-time metrics accessible to users
- Data reliability: unified extraction with validation

### To-dos

- [ ] Create scripts/extract/extract_all.py with unified data pipeline stub
- [ ] Add ui.extract.all target to Makefile
- [ ] Implement chunked/virtual rendering in GraphView.tsx for >10k nodes
- [ ] Create GraphPreview.tsx component for large dataset summary
- [ ] Create theme.ts with minimalist modern design tokens
- [ ] Redesign GraphDashboard.tsx with gradients, shadows, smooth transitions
- [ ] Improve GraphView.tsx colors, animations, mini-map
- [ ] Enhance NodeDetails.tsx with timeline and correlation viz
- [ ] Create DebugPanel.tsx with real-time performance metrics
- [ ] Create PerformanceBadge.tsx for user-facing indicators
- [ ] Create MetricsDashboard.tsx page with historical trends
- [ ] Implement IndexedDB caching in utils/cache.ts
- [ ] Enhance useGraphData.ts with retry logic and better errors
- [ ] Create ExportPanel.tsx for PNG/SVG/JSON exports