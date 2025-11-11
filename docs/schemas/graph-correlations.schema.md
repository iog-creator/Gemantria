# Graph Correlations Export Schema

Schema for validating pattern correlation exports from the semantic network

## Schema Definition

**File**: `graph-correlations.schema.json`

**JSON Schema Version**: https://json-schema.org/draft/2020-12/schema

## Properties

### `correlations`
**Required**
**Type**: `array`
**Description**: Array of correlation records between concepts, clusters, or patterns

**Items**:
- Type: `object`
- Properties:
  - `source`: Source concept identifier (content_hash or concept_id)
  - `target`: Target concept identifier (content_hash or concept_id)
  - `correlation`: Pearson correlation coefficient (-1 to 1)
  - `p_value`: Statistical significance p-value (0 to 1)
  - `metric`: Type of correlation analysis performed
  - `cluster_source`: Cluster ID of the source concept, null if unclustered
  - `cluster_target`: Cluster ID of the target concept, null if unclustered
  - `confidence`: Optional confidence score for the correlation
  - `sample_size`: Number of data points used in correlation calculation
  - `cooccurrence_score`: Text co-occurrence frequency score (0-1)

### `metadata`
**Required**
**Type**: `object`

**Properties**:

### `total_correlations`
**Type**: `integer`
**Description**: Total number of correlations found

### `significant_correlations`
**Type**: `integer`
**Description**: Number of correlations with p_value < 0.05

### `correlation_methods`
**Type**: `array`
**Description**: Types of correlation analysis performed

**Items**:
- Type: `string`

### `generated_at`
**Type**: `string`
**Description**: Timestamp when correlations were calculated

### `run_id`
**Type**: `string`
**Description**: Pipeline run ID that generated these correlations
