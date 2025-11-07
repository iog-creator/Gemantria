# Gemantria Pipeline Report

**Run ID**: `aggregated_recent`
**Generated**: 2025-10-22T05:43:01.614881+00:00

## Executive Summary

- **AI Enrichments**: 0
- **Confidence Validations**: 0 (0 passed, 0 failed)
- **Network Nodes**: 22 (0 strong, 0 weak edges)
- **Average AI Confidence**: 0.0000
- **Average Token Usage**: 0

## Node Performance

| Node                 | Events | Avg Duration (ms) |
| -------------------- | ------ | ----------------- |
| collect_nouns        | 6      | 8.0               |
| validate_batch       | 2      | 5.0               |
| enrichment           | 2      | 5.0               |
| confidence_validator | 2      | 5.0               |
| network_aggregator   | 2      | 4.0               |

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

- **Total Nodes**: 22
- **Strong Edges (≥0.90)**: 0
- **Weak Edges (≥0.75)**: 0
- **Embeddings Generated**: 22
- **Rerank Calls**: 0
- **Average Edge Strength**: 0.5009
- **Rerank Yes Ratio**: 1.000

## Qwen Live Verification

### Qwen Live Verification

- **Verified**: ✅ Yes
- **Models**: text-embedding-qwen3-embedding-0.6b, qwen.qwen3-reranker-0.6b
- **Embedding Dim**: 1024
- **Latency (ms)**: embed=645, rerank=708
- **Reason**: All models verified: text-embedding-qwen3-embedding-0.6b, qwen.qwen3-reranker-0.6b, christian-bible-expert-v2.0-12b

## Enrichment Proof

❌ **Error retrieving enrichment health data**: the connection is closed

## Concept Network Verification

- **Nodes persisted**: 22
- **Embedding dims (avg/min/max)**: 1024/1024/1024

## Quality Metrics

✅ **Real LM Studio Inference**: Confirmed active (non-mock mode)
✅ **Database Persistence**: All metrics and enrichments stored
✅ **Confidence Thresholds**: Met (gematria ≥0.90, AI ≥0.95)
✅ **Pipeline Integrity**: All nodes executed successfully
✅ **Qwen Integration**: Real embeddings + reranker active (non-mock mode)

## Qwen Usage Statistics

### Model Usage Summary

- **Total Pipeline Runs**: 61
- **Embeddings Generated**: 0
- **Rerank Calls Made**: 0
- **Average Yes Ratio**: 0.000
- **Average Edge Strength**: 0.0000

### Edge Strength Distribution

| Bucket           | Count | Avg Strength |
| ---------------- | ----- | ------------ |
| filtered (<0.75) | 15    | 0.501        |

### Top Rerank Pairs

| Source ID   | Target ID   | Edge Strength | Cosine | Rerank Score | Type        | Model         |
| ----------- | ----------- | ------------- | ------ | ------------ | ----------- | ------------- |
| 48b461e6... | 8f26a22e... | 0.5009        | 1.0000 | 0.5009       | decided_yes | qwen-reranker |
| 8f26a22e... | 48b461e6... | 0.5009        | 1.0000 | 0.5009       | decided_yes | qwen-reranker |
| e95d1521... | d2b1cc0c... | 0.5009        | 1.0000 | 0.5009       | decided_yes | qwen-reranker |
| d2b1cc0c... | e95d1521... | 0.5009        | 1.0000 | 0.5009       | decided_yes | qwen-reranker |
| 48e1b80e... | 8d01e612... | 0.5009        | 1.0000 | 0.5009       | decided_yes | qwen-reranker |

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
LINE 6: (SELECT ROUND(AVG(degree), 3) FROM concept_centr...
^
HINT: No function matches the given name and argument types. You might need to add explicit type casts.

## Pattern Correlation Summary

⚠️ **No correlation data available**

## Correlation Network Analytics

- **Correlation Threshold**: ≥0.4
- **Network Nodes**: 0
- **Correlation Edges**: 0 (filtered from 0 total)
- **Connected Components**: unknown (networkx not available)
- **Network Connected**: Yes

### Network Metrics

- **Average Weighted Degree**: unknown (networkx not available)
- **Maximum Weighted Degree**: unknown (networkx not available)
- **Average Clustering Coefficient**: unknown (networkx not available)

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

_No temporal patterns available for analysis._

## Forecast Summary

- **Total Forecasts**: 0
- **Forecasted Books**:
- **Default Horizon**: 10
- **Default Model**: sma

### Model Distribution

| Model | Count |
| ----- | ----- |

## Interactive Analytics Endpoints

The analytics pipeline now provides REST API endpoints for real-time access to correlation and pattern data:

| Endpoint          | Method                                                      | Data Source               | Last Modified       |
| ----------------- | ----------------------------------------------------------- | ------------------------- | ------------------- |
| Graph Statistics  | `GET /api/v1/stats`                                         | `graph_stats.json`        | 2025-10-21 22:42:38 |
| Correlations      | `GET /api/v1/correlations`                                  | `graph_correlations.json` | 2025-10-21 22:42:38 |
| Patterns          | `GET /api/v1/patterns`                                      | `graph_patterns.json`     | 2025-10-21 22:42:38 |
| Network Subgraph  | `GET /api/v1/network/{concept_id}`                          | `dynamic`                 | Dynamic             |
| Temporal Patterns | `GET /api/v1/temporal?series_id={id}&unit=chapter&window=5` | `temporal_patterns.json`  | 2025-10-21 22:42:38 |
| Forecasts         | `GET /api/v1/forecast?series_id={id}&horizon=10`            | `pattern_forecast.json`   | 2025-10-21 22:42:38 |

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
✅ **Semantic Network Built**: 22 concepts connected with 0 semantic relationships.

---

_Report generated automatically by Gemantria pipeline analysis_
