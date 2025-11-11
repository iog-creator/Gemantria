# Cross-Text Pattern Correlation Schema

JSON schema for cross-text pattern correlation analysis across multiple biblical books

## Schema Definition

**File**: `graph-patterns.schema.json`

**JSON Schema Version**: https://json-schema.org/draft/2020-12/schema

## Properties

### `patterns`
**Required**
**Type**: `array`
**Description**: Array of cross-text pattern correlation records

**Items**:
- Type: `object`
- Properties:
  - `book_source`: Source biblical book (e.g., 'Genesis', 'Exodus')
  - `book_target`: Target biblical book (e.g., 'Exodus', 'Leviticus')
  - `shared_concepts`: List of concept IDs that appear in both books
  - `pattern_strength`: Overall strength of the pattern relationship (0.0 to 1.0)
  - `metric`: Pattern correlation metric used (e.g., 'jaccard', 'cosine', 'lift')
  - `support`: Support metric: proportion of total concepts involved in pattern
  - `lift`: Lift metric: ratio of observed to expected co-occurrence
  - `confidence`: Confidence metric: conditional probability of pattern occurrence
  - `p_value`: Statistical significance p-value

### `metadata`
**Required**
**Type**: `object`
**Description**: Metadata about the pattern analysis

**Properties**:

### `total_patterns`
**Type**: `integer`
**Description**: Total number of cross-text patterns identified

### `analyzed_books`
**Type**: `array`
**Description**: List of books that were analyzed for patterns

**Items**:
- Type: `string`

### `pattern_methods`
**Type**: `array`
**Description**: List of pattern analysis methods used

**Items**:
- Type: `string`

### `generated_at`
**Type**: `string`
**Description**: Timestamp when analysis was performed

### `run_id`
**Type**: `string`
**Description**: Pipeline run ID that generated this analysis

### `analysis_parameters`
**Type**: `object`
**Description**: Parameters used for pattern analysis

**Properties**:

### `min_shared_concepts`
**Type**: `integer`
**Description**: Minimum number of shared concepts to consider a pattern
**Default**: `2`

### `min_pattern_strength`
**Type**: `number`
**Description**: Minimum pattern strength threshold
**Default**: `0.1`
