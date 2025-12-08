# Phase 27.G Walkthrough — Kernel Coherence II

## Summary

Fixed critical fragment duplication bug and achieved kernel coherence with **18/18 reality.green checks passing**.

## Changes Made

### 1. Fixed Fragment Duplication Bug
**File**: [ingest_doc_content.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/governance/ingest_doc_content.py#L297-306)

```diff
-# Delete existing fragments for this (doc_id, version_id)
-DELETE FROM control.doc_fragment
-WHERE doc_id = :doc_id AND version_id = :version_id
+# Delete ALL existing fragments for this doc_id (not just current version)
+DELETE FROM control.doc_fragment
+WHERE doc_id = :doc_id
```

**Root cause**: Each housekeeping run created new `version_id`s, but old fragments from previous versions were never deleted. Over ~10 runs, this accumulated **430,305 fragments** instead of the expected ~46k.

### 2. Added Embedding Progress Reporting
**File**: [ingest_doc_embeddings.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/governance/ingest_doc_embeddings.py#L152-196)

- Added `[PROGRESS]` output during embedding generation
- Shows rate, ETA, and percentage completion

### 3. Batched LM Studio Embedding Requests
**File**: [lm_studio.py](file:///home/mccoy/Projects/Gemantria.v2/pmagent/adapters/lm_studio.py#L315-328)

Changed from 1 HTTP request per text to batched array input:
```python
# Before: for text in text_list: requests.post(...)
# After: requests.post(url, json={"input": text_list, ...})
```

### 4. Updated DIRECTORY_DUPLICATION_MAP Status
**File**: [DIRECTORY_DUPLICATION_MAP.md](file:///home/mccoy/Projects/Gemantria.v2/docs/SSOT/DIRECTORY_DUPLICATION_MAP.md)

Added explicit "IMPORTANT: No file moves have been performed yet. This is planning only."

### 5. Moved Stray Root Files
- `PM_HANDOFF_PROTOCOL.md` → `docs/SSOT/`
- `SHARE_FOLDER_ANALYSIS.md` → `docs/SSOT/`

## Verification Results

### Database State After Fix
| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| Total fragments | 430,305 | 46,570 |
| Total embeddings | 269,800 | 46,570 |
| Unembedded gap | 160,505 | 0 |

### Reality Green Output
```
✅ REALITY GREEN: All checks passed - system is ready
📊 STATUS: 18/18 checks passed
```

### Performance
- Classification: 46,570 fragments in 6.1s (7,617/s)
- Embeddings: 46,570 fragments in ~7.7 min (100/s via LM Studio)

## Embedding Rate Investigation

Tested batch sizes 32 vs 256 — both resulted in ~100/s. The bottleneck is **LM Studio's BGE-M3 model processing**, not HTTP overhead or batch size. Potential optimization requires LM Studio GUI settings (evalBatchSize, Flash Attention).
