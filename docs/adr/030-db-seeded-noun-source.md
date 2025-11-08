# ADR-030: DB-seeded noun source for STRICT extraction

Context:

- AI-only discovery under-extracted (<50 nouns). We need a STRICT ≥50 path per golden specs.

- bible_db is read-only and contains canonical Hebrew tokens; we saw Strong's-only outputs when selecting the wrong column.

Decision:

- Enable a book-scoped DB-seed assist that selects the Hebrew text column (`word`) instead of Strong's numbers (`lemma` H####).

- Keep orchestrator/Make targets unchanged; discovery reads from DB seed first, then proceeds to agentic enrichment/scoring.

Consequences:

- Deterministic ≥50 noun gate satisfied (Genesis=1761).

- No Strong's numbers or "unknown" tokens; guards remain green.

Verification:

- STRICT run on Genesis: 1761 nouns; 0 "unknown"; 0 H####; guards 3/3 OK.
