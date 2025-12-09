# Bible DB Read-Only Ingestion

**Source**: `bible.v_morph_tokens` (view)  
**Output**: `exports/ai_nouns.db_morph.json` (schema: `gemantria/ai-nouns.v1`)

## Run

```bash
make db.ingest.morph
make guards.all
make pipeline.from_db
```

## Envelope fields

- `nodes[].surface` (Hebrew token)
- `nodes[].class` — `person | thing | other` (POS-based)
- `nodes[].analysis` — `{lemma, pos, morph, strongs_id, transliteration, gloss, definition}`
- `nodes[].sources[]` — `{"name":"bible_db.v_morph_tokens","ref":"OSIS"}`

## Notes

- Read-only; relies on canonical view `bible.v_morph_tokens`
- Orchestrator accepts file input via `--nouns-json`

