# Phase 13, Step 3 - Pre-Flight Verification

**Status:** Ready for DDL Execution  
**Branch:** feat/phase13-vector-unify  
**Risk Level:** 🔴 CRITICAL (Destructive Operation)

---

## Current State

### Database Status
- **Table:** `bible.verses`
- **Current Dimension:** 768-D (verified via pg_column_size = 3076 bytes)
- **Total Verses:** 116,566
- **Embedded Verses:** 116,566 (100%)
- **Database:** ✅ Running
- **LM Studio:** ✅ Running (BGE-M3 available)

### Scripts Ready
- ✅ `scripts/ops/phase13_ddl_migration_1024.sql` (DDL migration)
- ✅ `scripts/ops/reembed_verses_bge_1024.py` (re-embedding script)

---

## Execution Plan

### Step 1: DDL Migration (⚠️ DESTRUCTIVE)

**Command:**
```bash
psql -d bible_db -f scripts/ops/phase13_ddl_migration_1024.sql
```

**Impact:**
- Alters `bible.verses.embedding` from `vector(768)` to `vector(1024)`
- **NULLs ALL 116,566 embeddings** (requires full re-embedding)
- Drops existing HNSW index, creates new 1024-D index
- Estimated downtime: 5-10 minutes

**Rollback Plan:**
- Requires full backup restoration
- **CRITICAL:** Backup bible_db BEFORE executing

### Step 2: Full Re-embedding

**Command:**
```bash
python scripts/ops/reembed_verses_bge_1024.py --batch-size 500
```

**Resource Estimates:**
- **Time:** ~2-4 hours (116,566 verses × ~0.12s/verse)
- **Memory:** 8GB+ VRAM (BGE-M3 model)
- **Processing:** 500 verses/batch (233 batches total)
- **Resumable:** Yes (`--resume` flag for interrupted runs)

**Progress Monitoring:**
```sql
-- Check progress
SELECT 
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as embedded,
    COUNT(*) FILTER (WHERE embedding IS NULL) as pending
FROM bible.verses;
```

---

## Pre-Flight Checklist

### ⚠️ CRITICAL - Before DDL Execution

- [ ] **Full backup of bible_db completed**
- [ ] **Backup verified and tested (can restore)**
- [ ] **bible_db in maintenance mode** (no other processes accessing)
- [ ] **User approval obtained** for destructive operation
- [ ] **Resource availability confirmed** (8GB+ VRAM, 4-hour window)

### ✅ Pre-Conditions Met

- [x] On correct branch (feat/phase13-vector-unify)
- [x] DB services running
- [x] LM Studio running (BGE-M3 available)
- [x] DDL script created and verified
- [x] Re-embedding script created and tested (--help works)
- [x] Current dimension confirmed (768-D)

---

## Decision Point

**🛑 STOP - User Approval Required**

This is a **high-risk, irreversible operation**. Proceeding will:

1. NULL all 116,566 verse embeddings
2. Require 2-4 hours of re-processing
3. Block vector search functionality until complete

**Recommendation:** 
- Execute backup FIRST
- Run DDL migration during maintenance window
- Monitor re-embedding progress
- Verify vector search after completion

**Next Command (DO NOT RUN WITHOUT APPROVAL):**
```bash
# Step 1: Backup (REQUIRED)
pg_dump -d bible_db -F c -f /tmp/bible_db_backup_$(date +%Y%m%d_%H%M%S).dump

# Step 2: Execute DDL (DESTRUCTIVE)
psql -d bible_db -f scripts/ops/phase13_ddl_migration_1024.sql

# Step 3: Re-embed (LONG-RUNNING)
python scripts/ops/reembed_verses_bge_1024.py --batch-size 500
```

---

## Verification Steps (Post-Migration)

1. **Schema Verification:**
   ```sql
   SELECT atttypmod - 4 as dimension
   FROM pg_attribute
   WHERE attrelid = 'bible.verses'::regclass AND attname = 'embedding';
   -- Expected: 1024
   ```

2. **Embedding Count:**
   ```sql
   SELECT COUNT(*) FROM bible.verses WHERE embedding IS NOT NULL;
   -- Expected: 116,566
   ```

3. **Vector Search Test:**
   ```python
   from agentpm.biblescholar.vector_adapter import VectorAdapter
   adapter = VectorAdapter()
   results = adapter.search("love", top_k=5)
   assert len(results) > 0
   assert all(len(r.embedding) == 1024 for r in results)
   ```

---

## Abort Conditions

Abort execution if:
- ❌ Backup fails or cannot be verified
- ❌ BGE-M3 model not available
- ❌ Insufficient VRAM (< 8GB)
- ❌ Time window < 4 hours
- ❌ Other critical processes running on bible_db

---

**Status:** ⏸️ AWAITING USER APPROVAL
