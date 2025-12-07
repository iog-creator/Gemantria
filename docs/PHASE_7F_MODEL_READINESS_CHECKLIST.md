# Phase-7F: Model Readiness Checklist

**Status**: 🚧 IN PROGRESS  
**Gate**: All four slots must be 100% ready, configured, and tested before Phase-8

## Overview

This phase ensures all four critical model slots are fully operational via Ollama (slots 1-3) and properly wired (slot 4) before proceeding to Phase-8 (DSPy + LoRA).

**Critical Rule**: **No LM Studio on the critical path.** All production model calls must go through Ollama (slots 1-3) or dedicated theology provider (slot 4).

---

## The Four Slots

### 1. LOCAL_AGENT_MODEL → Granite via Ollama ✅

**Target**: `granite4:tiny-h` via Ollama

**Configuration**:
```env
INFERENCE_PROVIDER=ollama
LOCAL_AGENT_MODEL=granite4:tiny-h
```

**Status**: ✅ **VERIFIED**
- Model installed: `granite4:tiny-h`
- Auto-discovery: Working
- Chat test: Passing (`chat(model_slot="local_agent")` returns valid responses)

**Tests**:
- [x] `get_lm_model_config()` returns `provider="ollama"` and `local_agent_model="granite4:tiny-h"`
- [x] `pmagent health lm` reports provider=ollama and Granite=OK
- [x] `chat(model_slot="local_agent", "Say: GRANITE-READY")` returns response containing "GRANITE-READY"

---

### 2. EMBEDDING_MODEL → BGE-M3 via Ollama 🚧

**Target**: BGE-M3 embedding model via Ollama

**Configuration**:
```env
EMBEDDING_MODEL=bge-m3:latest  # or alternative Ollama name
```

**Status**: 🚧 **IN PROGRESS**
- Current: `text-embedding-bge-m3` (LM Studio name)
- Need: Verify Ollama model name for BGE-M3
- Need: Update auto-discovery normalization
- Need: Test embedding calls via Ollama

**Ollama Model Names** (to verify):
- `bge-m3` (if available)
- `bge-large-en-v1.5` (alternative)
- `bge-base-en-v1.5` (alternative)
- Fallback: Use Granite embeddings if BGE-M3 not available

**Tests**:
- [ ] `get_lm_model_config()` returns `embedding_model="bge-m3:latest"` (or verified Ollama name)
- [ ] Auto-discovery checks and pulls BGE-M3 model
- [ ] `embed(["a", "b"], model_slot="embedding")` returns:
  - `ok=True`
  - batch size = 2
  - embedding dimension > 0
- [ ] Optional: Tiny retrieval test to verify embeddings flow into RAG pipeline

**Implementation Tasks**:
- [ ] Research actual Ollama model name for BGE-M3
- [ ] Update `_normalize_model_name()` in `ollama_discovery.py` to handle BGE-M3
- [ ] Update `.env` and `env_example.txt` with correct Ollama model name
- [ ] Add BGE-M3 to auto-discovery required models list
- [ ] Create embedding smoke test

---

### 3. RERANKER_MODEL → BGE Reranker via Ollama 🚧

**Target**: BGE reranker model via Ollama

**Configuration**:
```env
RERANKER_MODEL=bge-reranker-v2-m3:latest  # or alternative Ollama name
```

**Status**: 🚧 **IN PROGRESS**
- Current: Using bi-encoder fallback (cosine similarity)
- Need: Verify Ollama model name for BGE reranker
- Need: Implement `rerank()` helper in Ollama adapter
- Need: Test reranker calls via Ollama

**Ollama Model Names** (to verify):
- `bge-reranker-v2-m3` (if available)
- `bge-reranker-base` (alternative)
- Fallback: Document if not available, use bi-encoder temporarily

**Tests**:
- [ ] `get_lm_model_config()` returns `reranker_model="bge-reranker-v2-m3:latest"` (or verified Ollama name)
- [ ] Auto-discovery checks and pulls BGE reranker model
- [ ] `rerank(query, docs, model_slot="reranker")` returns:
  - Scores for each document
  - Scores sorted (highest relevance first)
  - Scores in [0.0, 1.0] range

**Test Case**:
```python
query = "Who parted the Red Sea?"
docs = ["About Moses...", "About David...", "About Paul..."]
scores = rerank(query, docs, model_slot="reranker")
# Verify: scores[0] > scores[1] > scores[2] (Moses should rank highest)
```

**Implementation Tasks**:
- [ ] Research actual Ollama model name for BGE reranker
- [ ] Add `rerank()` function to `pmagent/adapters/ollama.py`
- [ ] Update `_normalize_model_name()` to handle BGE reranker
- [ ] Update `.env` and `env_example.txt` with correct Ollama model name
- [ ] Add BGE reranker to auto-discovery required models list
- [ ] Create reranker smoke test
- [ ] Update `src/rerank/blender.py` to use Ollama reranker (remove fallback)

---

### 4. THEOLOGY_MODEL → Existing Christian LLM 🚧

**Target**: `christian-bible-expert-v2.0-12b` (existing model, keep as-is)

**Configuration**:
```env
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
THEOLOGY_PROVIDER=<provider_name>  # ollama, lmstudio, or dedicated
```

**Status**: 🚧 **IN PROGRESS**
- Current: Uses LM Studio (needs to be removed from critical path)
- Need: Determine if theology model can run in Ollama
- Need: If not, create dedicated theology adapter (separate from LM Studio)
- Need: Ensure theology calls don't depend on LM Studio

**Options**:
1. **Option A**: If theology model available in Ollama → use Ollama adapter
2. **Option B**: If theology model requires separate provider → create dedicated theology adapter
3. **Option C**: Keep theology model on LM Studio but make it non-blocking (optional)

**Tests**:
- [ ] `get_lm_model_config()` returns `theology_model="christian-bible-expert-v2.0-12b"`
- [ ] `chat(model_slot="theology", "Summarize John 3:16 in one sentence.")` returns:
  - Theologically sound response
  - Clearly from Christian model (not Granite)
  - No LM Studio dependency (if Option A or B)

**Implementation Tasks**:
- [ ] Check if `christian-bible-expert-v2.0-12b` is available in Ollama
- [ ] If not available, create dedicated theology adapter
- [ ] Update `pmagent/adapters/lm_studio.py` to route theology calls correctly
- [ ] Ensure theology calls don't block on LM Studio availability
- [ ] Create theology smoke test
- [ ] Document theology provider choice

---

## Pipeline-Level Test (All Four Slots Together)

**Status**: 🚧 **NOT STARTED**

**Test Scenario**: Mini end-to-end pipeline using all four slots

**Steps**:
1. User question: "Who parted the Red Sea?"
2. System:
   - Uses **BGE-M3 embeddings** (slot 2) to search corpus
   - Uses **BGE reranker** (slot 3) to order passages
   - Feeds top passages and question into:
     - **Granite** (slot 1) for ops/agent reasoning (optional)
     - **Christian LLM** (slot 4) for final theological answer
3. Verification:
   - [ ] All three Ollama models were hit (Granite, BGE-M3, BGE reranker)
   - [ ] Christian LLM was used for final answer
   - [ ] No LM Studio calls at all (except optional theology if not in Ollama)

**Implementation Tasks**:
- [ ] Create `tests/integration/test_model_readiness_pipeline.py`
- [ ] Implement mini RAG pipeline test
- [ ] Verify all four slots are called
- [ ] Verify no LM Studio calls (except optional theology)

---

## Implementation Plan

### Phase 7F.1: Embedding Model (BGE-M3)
1. Research Ollama model name for BGE-M3
2. Update auto-discovery normalization
3. Update configuration files
4. Test embedding calls

### Phase 7F.2: Reranker Model (BGE Reranker)
1. Research Ollama model name for BGE reranker
2. Implement `rerank()` in Ollama adapter
3. Update auto-discovery
4. Test reranker calls
5. Update `blender.py` to use Ollama reranker

### Phase 7F.3: Theology Model
1. Check if theology model available in Ollama
2. Create/update theology adapter
3. Ensure no LM Studio dependency
4. Test theology calls

### Phase 7F.4: End-to-End Pipeline Test
1. Create integration test
2. Verify all four slots
3. Verify no LM Studio calls
4. Document results

---

## Acceptance Criteria

**All of the following must be TRUE before Phase-8:**

- [ ] Slot 1 (LOCAL_AGENT_MODEL): ✅ Verified and passing
- [ ] Slot 2 (EMBEDDING_MODEL): ✅ Configured, tested, passing
- [ ] Slot 3 (RERANKER_MODEL): ✅ Configured, tested, passing
- [ ] Slot 4 (THEOLOGY_MODEL): ✅ Configured, tested, passing
- [ ] Pipeline test: ✅ All four slots used, no LM Studio calls

**Gate**: If any slot fails, **STOP** and fix before proceeding.

---

## Notes

- **Model Availability**: Some models may not be available in Ollama. Document alternatives and fallbacks.
- **Theology Provider**: If theology model can't run in Ollama, create dedicated adapter (not LM Studio).
- **LM Studio Removal**: Ensure LM Studio is completely removed from critical path (except optional theology if needed).

---

## Related Files

- `pmagent/adapters/ollama.py` - Ollama adapter (needs `rerank()`)
- `scripts/ollama_discovery.py` - Auto-discovery (needs BGE model normalization)
- `scripts/config/env.py` - Configuration loader (already supports all slots)
- `src/rerank/blender.py` - Reranker integration (needs Ollama reranker)
- `scripts/guards/guard_lm_health.py` - Health checks (already integrated)

---

**Last Updated**: 2025-11-16  
**Next Review**: After each slot completion

