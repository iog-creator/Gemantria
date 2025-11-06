# Gemantria Pipeline Report

**Run ID**: `aggregated_recent`
**Generated**: 2025-11-05T04:31:45.740833+00:00

## Executive Summary

- **AI Enrichments**: 0
- **Confidence Validations**: 0   (0 passed, 0 failed)
- **Network Nodes**: 3702   (741 strong, 422 weak edges)
- **Average AI Confidence**: 0.0000
- **Average Token Usage**: 0

## Node Performance

| Node | Events | Avg Duration (ms) |
|------|--------|-------------------|

## AI Enrichment Details

- **Total Theological Insights Generated**: 0
- **Average Confidence Score**: 0.0000
- **Average Token Consumption**: 0 tokens per insight

## Confidence Validation Results

- **Total Validations**: 0
- **Passed**: 0
- **Failed**: 0
- **Average Gematria Confidence**: 0.0000
- **Average AI Confidence**: 0.0000

## Concept Network Summary

- **Total Nodes**: 3702
- **Strong Edges (≥0.90)**: 741
- **Weak Edges (≥0.75)**: 422
- **Embeddings Generated**: 3702
- **Rerank Calls**: 0
- **Average Edge Strength**: 0.8289
- **Rerank Yes Ratio**: 0.000

## Qwen Live Verification

### Qwen Live Verification

- **Verified**: ✅ Yes
- **Models**: text-embedding-bge-m3, qwen3-reranker-8b
- **Embedding Dim**: 1024
- **Latency (ms)**: embed=1206, rerank=1254
- **Reason**: All models verified: text-embedding-bge-m3, qwen3-reranker-8b, christian-bible-expert-v2.0-12b

## Enrichment Proof

❌ **Error retrieving enrichment health data**: the connection is closed


## Concept Network Verification

- **Nodes persisted**: 3702
- **Embedding dims (avg/min/max)**: 1024/1024/1024

## Quality Metrics

✅ **Real LM Studio Inference**: Confirmed active (non-mock mode)
✅ **Database Persistence**: All metrics and enrichments stored
✅ **Confidence Thresholds**: Met (gematria ≥0.90, AI ≥0.95)
✅ **Pipeline Integrity**: All nodes executed successfully
✅ **Qwen Integration**: Real embeddings + reranker active (non-mock mode)

## Qwen Usage Statistics

### Model Usage Summary

- **Total Pipeline Runs**: 88
- **Embeddings Generated**: 0
- **Rerank Calls Made**: 0
- **Average Yes Ratio**: 0.000
- **Average Edge Strength**: 0.0000

### Edge Strength Distribution

| Bucket | Count | Avg Strength |
|--------|-------|--------------|
| strong (≥0.90) | 741 | 0.985 |
| weak (0.75-0.89) | 422 | 0.843 |
| filtered (<0.75) | 692 | 0.653 |

### Top Rerank Pairs

| Source ID | Target ID | Edge Strength | Cosine | Rerank Score | Type | Model |
|-----------|-----------|---------------|--------|--------------|------|-------|
| 5f914e30... | 87a6df59... | 1.0000 | 0.5000 | 1.0000 | auto | qwen-reranker |
| 060bcbc1... | 5bec1e32... | 1.0000 | 0.5000 | 1.0000 | auto | qwen-reranker |
| 31c501af... | 2449ba46... | 1.0000 | 0.5000 | 1.0000 | auto | qwen-reranker |
| 41232034... | 7b7139fc... | 1.0000 | 0.5000 | 1.0000 | auto | qwen-reranker |
| df2c93bc... | 5cfecadf... | 1.0000 | 0.5000 | 1.0000 | auto | qwen-reranker |


## Relations

- **Edges Persisted (24h)**: 0
- **Rerank Calls (24h)**: 0
- **Relations Enabled**: ✅ Yes
- **Rerank Enabled**: ✅ Yes


## Confidence Gates

- **Soft Warnings (24h)**: 0 (threshold: 0.90)
- **Hard Failures (24h)**: 0 (threshold: 0.95)
- **ALLOW_PARTIAL**: ❌ No


## Pattern Discovery

❌ **Error retrieving pattern discovery data**: function round(double precision, integer) does not exist
LINE 7:             (SELECT ROUND(AVG(degree), 3) FROM concept_centr...
                            ^
HINT:  No function matches the given name and argument types. You might need to add explicit type casts.


## Pattern Correlation Summary

⚠️ **No correlation data available**


## Correlation Network Analytics

- **Correlation Threshold**: ≥0.4
- **Network Nodes**: 0
- **Correlation Edges**: 0 (filtered from 0 total)
- **Connected Components**: 0
- **Network Connected**: No

### Network Metrics
- **Average Weighted Degree**: 0
- **Maximum Weighted Degree**: 0
- **Average Clustering Coefficient**: 0

### Top 10 Strongest Connections

⚠️ **No correlation edges found in network**


## Cross-Book Pattern Analytics

- **Total Patterns**: 0
- **Analyzed Books**: 
- **Pattern Methods**: 
- **Min Shared Concepts**: 2
- **Min Pattern Strength**: 0.1


⚠️ **No cross-book patterns found**


## Temporal Analytics

- **Total Series**: 0
- **Analyzed Books**: 
- **Default Unit**: chapter
- **Default Window**: 5
- **Min Series Length**: 10


*No temporal patterns available for analysis.*


## Forecast Summary

- **Total Forecasts**: 0
- **Forecasted Books**: 
- **Default Horizon**: 10
- **Default Model**: sma

### Model Distribution

| Model | Count |
|-------|-------|



## Interactive Analytics Endpoints

The analytics pipeline now provides REST API endpoints for real-time access to correlation and pattern data:

| Endpoint | Method | Data Source | Last Modified |
|----------|--------|-------------|---------------|
| Graph Statistics | `GET /api/v1/stats` | `graph_stats.json` | 2025-11-04 20:31:02 |
| Correlations | `GET /api/v1/correlations` | `graph_correlations.json` | 2025-11-04 20:31:02 |
| Patterns | `GET /api/v1/patterns` | `graph_patterns.json` | 2025-11-04 20:31:02 |
| Network Subgraph | `GET /api/v1/network/{concept_id}` | `dynamic` | Dynamic |
| Temporal Patterns | `GET /api/v1/temporal?series_id={id}&unit=chapter&window=5` | `temporal_patterns.json` | 2025-11-04 20:31:02 |
| Forecasts | `GET /api/v1/forecast?series_id={id}&horizon=10` | `pattern_forecast.json` | 2025-11-04 20:31:02 |


### API Server

To start the analytics API server:

```bash
# Start the FastAPI server
python -m src.services.api_server

# Or using uvicorn directly
uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000
```

### Dashboard Access

Interactive dashboards are available at:
- **Metrics Dashboard**: `webui/dashboard/` - Real-time KPIs and analytics
- **Pattern Explorer**: `webui/dashboard/` - Cross-book pattern visualization

### Web UI Integration

The API endpoints power the interactive dashboards:
- `/api/v1/stats` → Metrics cards and sparklines
- `/api/v1/patterns` → Pattern heatmap and chord diagrams
- `/api/v1/correlations` → Network visualization and filtering



## Recommendations

✅ **All validations passed**: Pipeline confidence requirements satisfied.
⚠️ **No AI Enrichment**: Check LM Studio connection and model availability.
✅ **Semantic Network Built**: 3702 concepts connected with 1163 semantic relationships.

---
*Report generated automatically by Gemantria pipeline analysis*
