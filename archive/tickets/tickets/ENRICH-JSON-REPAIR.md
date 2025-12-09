# ENRICH-JSON-REPAIR
Issue: LLM occasionally returns malformed JSON (backslashes / trailing commas).
Observed: lines from logs/enrichment*.log with 'noun_enrichment_failed'.
Action: strengthen json_sanitize.safe_json_loads() with:
- trailing comma removal
- control-char escape
- array-of-objects coercion
Attachments: paste failing payload samples here.
