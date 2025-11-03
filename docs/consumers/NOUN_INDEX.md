# Noun Consumer Bridge

## Run

```bash
python scripts/export_noun_index.py --limit 10000
# outputs:
# share/exports/nouns.jsonl
# share/exports/envelope.json
```

## SQL (direct read)

If you prefer SQL, use your existing nouns + occurrences + verses join:

```sql
SELECT o.verse_id, v.book, v.book_ord, v.chapter, v.verse, n.lemma, o.token_idx
FROM gematria.noun_occurrences o
JOIN gematria.nouns n ON n.id = o.noun_id
JOIN bible_db.verses v ON v.id = o.verse_id
ORDER BY v.book_ord, o.verse_id, o.token_idx
LIMIT 100;
```
