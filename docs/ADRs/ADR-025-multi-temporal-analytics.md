# ADR-025: Multi-Temporal Analytics & Predictive Patterns

## Status

Accepted

## Context

As the Gemantria project advances through Phases 5-7 (correlation and pattern analytics), we now have rich static datasets but lack temporal awareness. Biblical texts have natural sequential structure (verses, chapters, books) that could reveal important patterns over time. Understanding how concepts evolve, cluster, or correlate across sequential indices provides deeper insight into textual dynamics.

Traditional correlation analysis treats all relationships as static and contemporaneous. Phase 8 introduces time-aware analytics to track how relationships change, predict future patterns, and identify temporal anomalies or trends in the biblical text.

The current export system produces comprehensive but time-agnostic analytics. We need temporal extensions that maintain the existing deterministic, schema-validated approach while adding sequence-aware computations.

## Decision

Implement comprehensive temporal analytics with the following components:

### 1. Temporal Pattern Analysis

- **Rolling Window Computations**: Apply rolling means/sums over sequential indices
- **Time Units**: Support verse-level and chapter-level temporal analysis
- **Change Point Detection**: Identify significant shifts in temporal patterns
- **Series Metadata**: Track series length, volatility, and statistical properties

### 2. Predictive Forecasting

- **Statistical Models**: Implement Naive, Simple Moving Average, and ARIMA forecasting
- **Prediction Intervals**: Provide uncertainty quantification for forecasts
- **Performance Metrics**: Track RMSE and MAE for model evaluation
- **Horizon Flexibility**: Configurable forecast lengths (default 10 steps)

### 3. Schema-Validated Exports

- **Temporal Patterns Schema**: Structured validation for rolling window results
- **Forecast Schema**: Comprehensive validation for prediction outputs
- **Metadata Tracking**: Analysis parameters, performance metrics, and data quality indicators

### 4. Interactive Exploration

- **Temporal Pattern Explorer**: Visual interface for time series analysis with filtering
- **Forecast Dashboard**: Interactive forecast visualization with model comparison
- **Real-time Filtering**: API-driven exploration of temporal relationships

## Rationale

### Why Temporal Analytics?

1. **Enhanced Understanding**: Biblical texts have inherent sequential structure that static analysis misses
2. **Pattern Discovery**: Temporal patterns can reveal narrative arcs, thematic development, and structural motifs
3. **Predictive Insights**: Forecasting enables hypothesis testing about textual evolution
4. **Anomaly Detection**: Change point analysis identifies significant textual transitions

### Why This Approach?

1. **Incremental Extension**: Builds on existing correlation/pattern infrastructure
2. **Schema-First**: Maintains validation integrity with new JSON schemas
3. **API-Driven**: Enables interactive exploration without data duplication
4. **Performance Conscious**: Efficient algorithms suitable for large biblical datasets

### Design Principles

1. **Deterministic**: Same inputs produce identical temporal analyses
2. **Composable**: Temporal features integrate with existing analytics pipeline
3. **Scalable**: Rolling window algorithms work efficiently with large sequences
4. **Discoverable**: Clear API contracts and interactive exploration interfaces

## Alternatives Considered

### Alternative 1: Time Series Database Integration

**Rejected**: Would introduce external dependencies and complexity beyond current PostgreSQL setup

**Rationale**: Current pgvector integration already handles embeddings efficiently. Adding temporal databases would increase operational complexity without proportional benefit.

### Alternative 2: Complex ML Models Only

**Rejected**: Starting with complex models (LSTM, Prophet) would be overkill for initial temporal exploration

**Rationale**: Statistical forecasting provides interpretable baseline. Complex models can be added later if needed for specific use cases.

### Alternative 3: Real-time Streaming Analytics

**Rejected**: Biblical text analysis doesn't require real-time processing

**Rationale**: Batch processing aligns with existing pipeline architecture and provides deterministic, reproducible results.

## Consequences

### Positive Outcomes

1. **Enhanced Analytics**: Users can explore how biblical concepts evolve over narrative time
2. **Predictive Capabilities**: Enable hypothesis testing about textual development patterns
3. **Interactive Discovery**: Web UI enables exploration of temporal relationships
4. **Extensible Framework**: Foundation for more advanced temporal analysis techniques

### Negative Outcomes

1. **Increased Complexity**: Additional schemas, APIs, and UI components to maintain
2. **Performance Overhead**: Rolling window computations add to export processing time
3. **Learning Curve**: Users need to understand temporal analysis concepts
4. **Data Volume**: Additional JSON exports increase storage and transfer requirements

### Mitigation Strategies

1. **Incremental Adoption**: Temporal features are optional and don't break existing workflows
2. **Efficient Algorithms**: Rolling window implementations are computationally efficient
3. **Clear Documentation**: Comprehensive guides for temporal analysis concepts
4. **Optional Processing**: Users can disable temporal exports if not needed

## Implementation Requirements

### Core Components

1. **Temporal Analysis Engine** (`scripts/export_stats.py`)

   - Rolling window computation functions
   - Change point detection algorithms
   - Series statistical analysis

2. **Forecasting Engine** (`scripts/export_stats.py`)

   - Statistical model implementations
   - Prediction interval calculations
   - Performance metric computation

3. **API Endpoints** (`src/services/api_server.py`)

   - Temporal pattern filtering and retrieval
   - Forecast data access with parameters

4. **Interactive Components** (`webui/dashboard/`)
   - Time series visualization with controls
   - Forecast display with uncertainty intervals

### Data Contracts

1. **Temporal Patterns Schema** (`docs/SSOT/temporal-patterns.schema.json`)

   - Rolling window result validation
   - Series metadata structure
   - Change point data format

2. **Forecast Schema** (`docs/SSOT/pattern-forecast.schema.json`)
   - Prediction result validation
   - Performance metric structure
   - Uncertainty quantification format

### Quality Assurance

1. **Schema Validation**: All exports validated against JSON schemas
2. **Performance Testing**: Rolling window algorithms benchmarked for efficiency
3. **API Testing**: Endpoint functionality verified with various filter combinations
4. **UI Testing**: Interactive components tested across different temporal datasets

## Related ADRs

- **ADR-018**: Pattern Correlation Engine (foundation for temporal analysis)
- **ADR-021**: Stats Proof (metrics validation framework)
- **ADR-022**: Visualization Contract Sync (UI data contract patterns)
- **ADR-023**: API + Dashboard (interactive exploration framework)

## Notes

### Future Enhancements

1. **Advanced Forecasting**: LSTM, Prophet, or other ML models for complex patterns
2. **Multi-scale Analysis**: Cross-book temporal relationships
3. **Seasonal Decomposition**: Identify cyclical patterns in biblical narratives
4. **Real-time Updates**: Streaming temporal analysis for dynamic datasets

### Integration Points

1. **Existing Pipeline**: Seamlessly integrates with current export workflow
2. **Web UI**: Extends existing dashboard architecture
3. **API Framework**: Follows established REST API patterns
4. **Schema System**: Uses existing JSON Schema validation infrastructure

### Performance Considerations

1. **Memory Usage**: Rolling window computations are memory-efficient
2. **Processing Time**: Additional exports add ~30-50% to total processing time
3. **Storage Impact**: Two additional JSON files (~10-20% increase in export size)
4. **API Performance**: Efficient filtering and pagination for large temporal datasets
