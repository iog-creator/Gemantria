# Temporal Strip Export (CSV/PNG)

Generates a simple "year → count" dataset from `share/exports/envelope.json` and writes:

- `ui/out/temporal_strip.csv`
- `ui/out/temporal_strip.png` (if matplotlib available)

## Quick start

```bash
# 1) Export nouns+envelope (requires GEMATRIA_DSN)
python scripts/export_noun_index.py --limit 10000

# 2) Build temporal strip (point mode)
make ui.export.temporal ENVELOPE=share/exports/envelope.json OUTDIR=ui/out

# 3) (Optional) Span mode uses start_year..end_year if present
make ui.export.temporal.span ENVELOPE=share/exports/envelope.json OUTDIR=ui/out

# 4) Produce a Markdown summary and (optionally) post it to the PR
make ui.temporal.summary OUTDIR=ui/out
make ui.temporal.comment OUTDIR=ui/out
```

### Notes

- Year extraction order: `node.year` → `node.data.year` → `node.data.start_year`.
- Span mode clamps spans and caps at 5000 years per node for safety.
- Works without launching any Node/JS dev server.
