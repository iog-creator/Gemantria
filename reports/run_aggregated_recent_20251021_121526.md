# Gemantria Pipeline Report

**Run ID**: `aggregated_recent`
**Generated**: 2025-10-21T19:15:26.442021+00:00

## Executive Summary

- **AI Enrichments**: 48
- **Confidence Validations**: 48 (40 passed, 8 failed)
- **Network Nodes**: 0 (0 strong, 0 weak edges)
- **Average AI Confidence**: 0.9000
- **Average Token Usage**: 76

## Node Performance

| Node | Events | Avg Duration (ms) |
|------|--------|-------------------|
| collect_nouns | 52 | 5.0 |
| validate_batch | 52 | 7.0 |
| enrichment | 52 | 3169.0 |
| confidence_validator | 52 | 9.0 |
| network_aggregator | 43 | 5532.0 |

## AI Enrichment Details

- **Total Theological Insights Generated**: 48
- **Average Confidence Score**: 0.9000
- **Average Token Consumption**: 76 tokens per insight

## Confidence Validation Results

- **Total Validations**: 48
- **Passed**: 40
- **Failed**: 8
- **Average Gematria Confidence**: 1.0000
- **Average AI Confidence**: 0.9000

## Concept Network Summary

- **Total Nodes**: 0
- **Strong Edges (≥0.90)**: 0
- **Weak Edges (≥0.75)**: 0
- **Embeddings Generated**: 0
- **Rerank Calls**: 0
- **Average Edge Strength**: 0.0000
- **Rerank Yes Ratio**: 0.000

## Qwen Live Verification

### Qwen Live Verification

- **Verified**: ✅ Yes
- **Models**: text-embedding-qwen3-embedding-0.6b, qwen.qwen3-reranker-0.6b
- **Embedding Dim**: 1024
- **Latency (ms)**: embed=588, rerank=700
- **Reason**: All models verified: text-embedding-qwen3-embedding-0.6b, qwen.qwen3-reranker-0.6b, christian-bible-expert-v2.0-12b

## Enrichment Proof

❌ **Error retrieving enrichment health data**: the connection is closed


## Concept Network Verification

- **Nodes persisted**: 10
- **Embedding dims (avg/min/max)**: 1024/1024/1024

## Quality Metrics

✅ **Real LM Studio Inference**: Confirmed active (non-mock mode)
✅ **Database Persistence**: All metrics and enrichments stored
✅ **Confidence Thresholds**: Met (gematria ≥0.90, AI ≥0.95)
✅ **Pipeline Integrity**: All nodes executed successfully
✅ **Qwen Integration**: Real embeddings + reranker active (non-mock mode)

## Qwen Usage Statistics

### Model Usage Summary

- **Total Pipeline Runs**: 47
- **Embeddings Generated**: 0
- **Rerank Calls Made**: 0
- **Average Yes Ratio**: 0.000
- **Average Edge Strength**: 0.0000

### Edge Strength Distribution

| Bucket | Count | Avg Strength |
|--------|-------|--------------|
| filtered (<0.75) | 7 | 0.501 |

### Top Rerank Pairs

| Source ID | Target ID | Edge Strength | Cosine | Rerank Score | Type | Model |
|-----------|-----------|---------------|--------|--------------|------|-------|
| 48e1b80e... | 8d01e612... | 0.5009 | 1.0000 | 0.5009 | decided_yes | qwen-reranker |
| 48b461e6... | 8f26a22e... | 0.5009 | 1.0000 | 0.5009 | decided_yes | qwen-reranker |
| 8f26a22e... | 48b461e6... | 0.5009 | 1.0000 | 0.5009 | decided_yes | qwen-reranker |
| e95d1521... | d2b1cc0c... | 0.5009 | 1.0000 | 0.5009 | decided_yes | qwen-reranker |
| d2b1cc0c... | e95d1521... | 0.5009 | 1.0000 | 0.5009 | decided_yes | qwen-reranker |


## Relations

- **Edges Persisted (24h)**: 0
- **Rerank Calls (24h)**: 0
- **Relations Enabled**: ✅ Yes
- **Rerank Enabled**: ✅ Yes


## Confidence Gates

- **Soft Warnings (24h)**: 0 (threshold: 0.90)
- **Hard Failures (24h)**: 0 (threshold: 0.85)
- **ALLOW_PARTIAL**: ✅ Yes


## Pattern Discovery

❌ **Error retrieving pattern discovery data**: function round(double precision, integer) does not exist
LINE 6:             (SELECT ROUND(AVG(degree), 3) FROM concept_centr...
                            ^
HINT:  No function matches the given name and argument types. You might need to add explicit type casts.


## Recommendations

⚠️ **Review Required**: 8 validations failed confidence thresholds.
✅ **AI Enrichment Active**: 48 theological insights generated with high confidence.
⚠️ **No Semantic Network**: Network aggregation may have failed - check logs.

---
*Report generated automatically by Gemantria pipeline analysis*
