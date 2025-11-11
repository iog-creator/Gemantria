# Temporal Pattern Analytics Schema

JSON schema for temporal pattern analysis across biblical texts using rolling window computations

## Schema Definition

**File**: `temporal-patterns.schema.json`

**JSON Schema Version**: https://json-schema.org/draft/2020-12/schema

## Properties

### `temporal_patterns`
**Required**
**Type**: `array`
**Description**: Array of temporal pattern records for concepts/clusters over time

**Items**:
- Type: `object`
- Properties:
  - `series_id`: Identifier for the concept or cluster (concept_id or cluster_id)
  - `unit`: Time unit for analysis (verse or chapter index)
  - `window`: Rolling window size for temporal analysis
  - `start_index`: Starting index in the biblical text
  - `end_index`: Ending index in the biblical text
  - `metric`: Type of metric being tracked over time
  - `values`: Array of computed values for each window position
  - `method`: Computation method used for the rolling window
  - `book`: Biblical book this series belongs to
  - `zscore_values`: Z-score normalized values for anomaly detection
  - `change_points`: Indices where significant changes occur in the series
  - `seasonality`: Detected seasonal pattern (e.g., 'weekly', 'monthly')
  - `metadata`: Additional metadata about the temporal analysis

### `metadata`
**Required**
**Type**: `object`

**Properties**:

### `generated_at`
**Type**: `string`
**Description**: Timestamp when analysis was generated

### `analysis_parameters`
**Type**: `object`

**Properties**:

### `default_unit`
**Type**: `string`
**Allowed values**: verse, chapter

### `default_window`
**Type**: `integer`

### `min_series_length`
**Type**: `integer`

### `total_series`
**Type**: `integer`
**Description**: Total number of temporal series analyzed

### `books_analyzed`
**Type**: `array`
**Description**: List of biblical books included in analysis

**Items**:
- Type: `string`
