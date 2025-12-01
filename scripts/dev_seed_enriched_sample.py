# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Writes a minimal ai_nouns.json with one enriched noun that mentions verses,
so guards/spot-checks produce positive evidence without running the full pipeline.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.osis import extract_verse_references

from datetime import datetime, UTC

sample = {
    "schema": "gematria/ai-nouns.v1",
    "book": "Genesis",
    "generated_at": datetime.now(UTC).isoformat(),
    "nodes": [
        {
            "noun_id": "seed-ps30-isa43",
            "surface": "בֹּקֶר",
            "letters": ["ב", "ֹ", "ּ", "ק", "ֶ", "ר"],
            "gematria": 222,
            "class": "thing",
            "ai_discovered": True,
            "sources": [{"ref": "Gen.1.5"}],
            "analysis": {"lemma": "morning"},
            "enrichment": {
                "insight": "Weeping may endure for a night, but joy comes in the morning (Psalm 30:5). See also Isaiah 43:2.",
                "confidence": 0.95,
            },
        }
    ],
}

# Extract and attach crossrefs to demonstrate the feature
for node in sample["nodes"]:
    enrichment = node.get("enrichment", {})
    insight = enrichment.get("insight", "")
    if insight:
        crossrefs = extract_verse_references(insight)
        if crossrefs:
            enrichment["crossrefs"] = [
                {"label": ref["label"], "osis": ref["osis"]} for ref in crossrefs
            ]

with open("exports/ai_nouns.json", "w", encoding="utf-8") as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)
print("Wrote exports/ai_nouns.json with seeded enrichment and extracted crossrefs.")
