# Graph SSOT



## Schema Definition

**File**: `SSOT_graph.v1.schema.json`


## Properties

### `schema`
**Required**
**Type**: `any`

### `book`
**Required**
**Type**: `string`

### `generated_at`
**Required**
**Type**: `string`

### `nodes`
**Required**
**Type**: `array`

**Items**:
- Type: `object`
- Properties:
  - `id`: 
  - `lemma`: 
  - `surface`: 
  - `book`: 

### `edges`
**Required**
**Type**: `array`

**Items**:
- Type: `object`
- Properties:
  - `src`: 
  - `dst`: 
  - `type`: 
  - `weight`: 
  - `cosine`: 
  - `rerank_score`: 
  - `class`: 
  - `analysis`: 
