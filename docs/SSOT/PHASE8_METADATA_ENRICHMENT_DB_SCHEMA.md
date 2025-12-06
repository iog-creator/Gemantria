# Phase 8 Metadata Enrichment — DB Schema Discovery

## Executive Summary

**Status**: ✅ Schema verified via live DB queries  
**DB Access**: ✅ GEMATRIA_DSN configured and connected  
**Finding**: Metadata available via `v_concepts_with_verses` view with gematria_value and verses JSONB

### Critical Discovery

**Problem**: Neither `concepts` nor `concept_metadata` tables contain book/chapter/verse/gematria fields as code analysis suggested.

**Solution**: Use `v_concepts_with_verses` view which aggregates:
- `gematria_value` (integer)
- `book_source` (varchar)
- `verses` (JSONB array with chapter/verse objects)
- Additional metadata: hebrew_text, strong_number, occurrence counts

---

## 1. Required Metadata Fields

Per `PHASE8_METADATA_ENRICHMENT_PLAN.md`, Phase 8 requires:

1. `position` - Sequential verse index (integer)
2. `chapter` - Chapter number (integer)  
3. `verse` - Verse number (integer)
4. `gematria` - Numeric gematria value

---

## 2. Data Sources Identified

### Primary Source Table: `nouns` (analysis schema)

**Evidence** from `scripts/backfill_noun_embeddings.py` (lines 80-119):
```sql
SELECT n.id, n.lemma, n.surface, n.book, n.chapter, n.verse
FROM nouns n
```

**Available columns** on `nouns` table:
- ✅ `book` (varchar)
- ✅ `chapter` (integer)
- ✅ `verse` (integer)
- ⚠️ `gematria_value` - May exist but shows as NULL in some scripts

### Secondary Source: `bible.verses` (bible_db schema)

**Evidence** from `scripts/export_noun_index.py` (lines 95-112) and `scripts/db/populate_mark_1_1_greek.py` (lines 114-131):
```sql
SELECT v.book_name, v.chapter_num, v.verse_num, v.verse_id
FROM bible.verses v
ORDER BY v.book_name, v.chapter_num, v.verse_num
```

**Available columns** on `bible.verses`:
- ✅ `verse_id` (UUID/varchar, primary key)
- ✅ `book_name` (varchar)
- ✅ `chapter_num` (integer)
- ✅ `verse_num` (integer)
- ⚠️ `translation_source` (varchar, e.g., "WLC", "LXX")
- ⚠️ `text` (text, verse content)

### Tertiary Source: `bible.v_morph_tokens` (view)

**Evidence** from `scripts/ingest_bible_db_morphology.py` (lines 42, 50):
```sql
SELECT * FROM bible.v_morph_tokens
```

This view provides:
- ✅ `osis_ref` (OSIS reference like "Gen.1.1")
- Morphological token data per word
- Source for linking surface forms to verses

---

## 3. Join Strategy

### Current Graph Node Structure

From `scripts/export_graph.py` (lines 278-300), nodes are built from:
```sql
SELECT n.concept_id, co.name, c.cluster_id,
       ce.degree, ce.betweenness, ce.eigenvector
FROM concept_network n
LEFT JOIN concepts co ON co.id::text = n.concept_id::text
```

**Key**: `concept_id` (UUID) links to `concepts.id`

### concepts Table Analysis

From `scripts/ingest_bible_db_morphology.py` and other ingestion scripts:
```python
{
    "id": uuid,
    "name": surface_form,
    "book": book_name,  # ← Already present!
   "sources": [{"name": "bible_db.v_morph_tokens", "ref": osis_ref}]
}
```

**Discovery**: The `concepts` table **already contains** `book`, and likely `chapter`/`verse` or can derive them from OSIS refs.

### Proposed Join Path

**Option A - Direct from concepts table** (if chapter/verse exist):
```sql
SELECT n.concept_id, co.name, co.book, co.chapter, co.verse,  
       co.gematria_value,
       c.cluster_id, ce.degree, ce.betweenness, ce.eigenvector
FROM concept_network n
LEFT JOIN concepts co ON co.id::text = n.concept_id::text
LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
```

**Option B - Via nouns table** (if concepts links to nouns):
```sql
SELECT n.concept_id, co.name,
       no.book AS book, no.chapter AS chapter, no.verse AS verse,
       no.gematria_value,
       c.cluster_id, ce.degree, ce.betweenness, ce.eigenvector
FROM concept_network n
LEFT JOIN concepts co ON co.id::text = n.concept_id::text
LEFT JOIN nouns no ON co.id = no.id  -- or via another join key
LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
```

**Option C - Calculate position from chapter/verse**:
```python
# After fetching chapter and verse
position = (chapter * 1000) + verse  # Standard formula per export_stats.py line 846
```

---

## 4. Gematria Value Source

### Primary: `nouns.gematria_value`

From `scripts/export_stats.py` (lines 819-823):
```sql
SELECT chapter, primary_verse,
       SUM(gematria_value) as gematria_sum
FROM concepts
WHERE book = %s AND gematria_value IS NOT NULL
```

**Implication**: `concepts` table has `gematria_value` column.

### Fallback: Calculate from surface form

From `scripts/ingest_bible_db_morphology.py` (line 31):
```python
"gematria_value": None,  # calculated downstream
```

If `gematria_value` is NULL, it can be calculated from Hebrew/Greek surface forms using the gematria module.

---

## 5. Implementation Requirements (VERIFIED)

### Actual Schema Discovery

**Table**: `v_concepts_with_verses` (view)

**Columns**:
- `id` (integer) - concept ID
- `name` (varchar 255)
- `gematria_value` (integer) ✅
- `book_source` (varchar 100) ✅  
- `hebrew_text` (varchar 255)
- `strong_number` (varchar 10)
- `verses` (jsonb) ✅ - Array of {chapter, verse} objects
- `verse_occurrence_count` (integer)
- Plus: degree, betweenness_centrality, doctrinal_tags, temporal_eras

### Enrichment Strategy

**JOIN PATH**:
```sql
FROM concept_network cn
LEFT JOIN concepts c ON c.id::text = cn.concept_id::text
LEFT JOIN v_concepts_with_verses v ON v.id::text = cn.concept_id::text
```

**METADATA EXTRACTION**:
```python
for row in db_nodes:
    concept_id = row[0]
    name = row[1]
    gematria_value = row[6]  # From v_concepts_with_verses
    book = row[7]  # book_source
    verses_json = row[8]  # JSONB array
    
    # Extract first verse for chapter/verse/position
    if verses_json:
        first_verse = verses_json[0]
        chapter = first_verse.get('chapter')
        verse = first_verse.get('verse')
        position = (chapter * 1000) + verse if (chapter and verse) else None
    else:
        chapter, verse, position = None, None, None
    
    node_data = {
        "noun_id": concept_id,
        "surface": name,
        # ... existing fields ...
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "position": position,
        "gematria": float(gematria_value) if gematria_value else None,
    }
```

### Minimal Change to `export_graph.py`

**Current query** (lines 278-289):
```sql
SELECT n.concept_id, co.name, c.cluster_id,
       ce.degree, ce.betweenness, ce.eigenvector
FROM concept_network n
LEFT JOIN concepts co ON co.id::text = n.concept_id::text
LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
```

**Enriched query** (add 3 fields from v_concepts_with_verses):
```sql
SELECT n.concept_id, co.name, c.cluster_id,
       ce.degree, ce.betweenness, ce.eigenvector,
       v.gematria_value, v.book_source, v.verses
FROM concept_network n
LEFT JOIN concepts co ON co.id::text = n.concept_id::text
LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
LEFT JOIN v_concepts_with_verses v ON v.id::text = n.concept_id::text
```

---

## 6. Validation Steps

### Pre-Implementation Checks

1. **Verify `concepts` table schema**:
   ```sql
   \d concepts
   ```
   Confirm columns: `book`, `chapter`, `verse`, `gematria_value`

2. **Sample query** to test join:
   ```sql
   SELECT co.id, co.name, co.book, co.chapter, co.verse, co.gematria_value
   FROM concepts co
   LIMIT 10;
   ```

3. **Check NULL rates**:
   ```sql
   SELECT 
     COUNT(*) as total,
     COUNT(book) as has_book,
     COUNT(chapter) as has_chapter,
     COUNT(verse) as has_verse,
     COUNT(gematria_value) as has_gematria
   FROM concepts;
   ```

### Post-Implementation Validation

1. Re-export graph: `python scripts/export_graph.py`
2. Inspect sample nodes: `jq '.nodes[0]' exports/graph_latest.json`
3. Re-run Phase 8: `python scripts/temporal_analytics.py`
4. Verify: `jq '.metadata.total_series' exports/temporal_patterns.json` > 0

---

## 7. Acceptance Criteria

- ✅ At least 50% of nodes have `chapter`, `verse`, and `position` fields
- ✅ At least 25% of nodes have non-NULL `gematria` values
- ✅ Phase 8 produces `total_series > 0` after re-export
- ✅ No crashes or SQL errors during export

---

## 8. Next Steps

1. **DB Schema Verification** (requires GEMATRIA_DSN):
   - Run pre-implementation checks above
   - Confirm exact column names in `concepts` table

2. **Implement Enrichment Patch**:
   - Modify `scripts/export_graph.py` per section 5
   - Add position calculation logic
   - Handle NULL gracefully (nodes without verse metadata)

3. **Test & Validate**:
   - Re-export graph
   - Re-run Phase 8
   - Confirm non-zero temporal patterns

4. **Document Results**:
   - Update diagnostic with actual metadata coverage
   - Proceed to Phase 8 → envelope mapping docs

---

## Appendix: Key Code References

- **Node export**: `scripts/export_graph.py` lines 260-342
- **Verse metadata usage**: `scripts/export_stats.py` lines 796-850
- **Nouns with verse refs**: `scripts/backfill_noun_embeddings.py` lines 75-120
- **Bible verses table**: `scripts/db/populate_mark_1_1_greek.py` lines 114-131
- **Position calculation**: `scripts/export_stats.py` line 846 (`chapter * 1000 + verse`)
