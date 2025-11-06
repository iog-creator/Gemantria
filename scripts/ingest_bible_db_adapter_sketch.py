#!/usr/bin/env python3
"""
Minimal probe: show how we would map bible_db views → canonical SSOT noun/enrichment shapes.

This is a sketch demonstrating the adapter pattern for consuming bible_db views
into our SSOT noun/enrichment boundaries.
"""

import json
import sys
from typing import Dict, Any


def noun_from_morph(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map bible_db.v_morph_tokens row → SSOT noun shape.

    This adapter normalizes bible_db morphology data into our canonical
    noun structure with gematria, sources, and analysis metadata.
    """
    # Extract surface form (Hebrew text)
    surface = row.get("surface", "").strip()

    # Determine class from POS and context
    pos = row.get("pos", "OTHER")
    morph = row.get("morph", "")

    # Classify: nouns are primary, but we can infer person/place from context
    noun_class = "thing"  # default
    if pos == "NOUN":
        # Could enhance with proper_names lookup or theological_term
        if row.get("theological_term"):
            # Could be person/place/other based on theological_term value
            noun_class = "thing"  # would need proper_names join to determine

    # Build source reference
    osis_ref = row.get("osis_ref", "")
    source_ref = {
        "name": "bible_db.v_morph_tokens",
        "ref": osis_ref,
        "verse_id": row.get("verse_id"),
        "token_id": row.get("token_id"),
    }

    return {
        "surface": surface,
        "letters": None,  # Would compute from surface via Hebrew normalization
        "gematria_value": None,  # Would compute via gematria calculation
        "class": noun_class,
        "analysis": {
            "lemma": row.get("lemma"),
            "pos": pos,
            "morph": morph,
            "strongs_id": row.get("strongs_id"),
            "transliteration": row.get("transliteration"),
            "gloss": row.get("gloss"),
            "definition": row.get("definition"),
            "theological_term": row.get("theological_term"),
        },
        "sources": [source_ref],
    }


def enrichment_from_entry(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map bible_db.hebrew_entries + v_morph_tokens → enrichment block.

    Adds lexical and theological context to nouns.
    """
    return {
        "theology": {
            "themes": [],  # Would extract from theological_term or definition
            "cross_refs": [],  # Would need cross-reference lookup
            "notes": [
                row.get("definition", ""),
                row.get("usage", ""),
            ],
        },
        "lexical": {
            "strongs_id": row.get("strongs_id"),
            "transliteration": row.get("transliteration"),
            "gloss": row.get("gloss"),
        },
    }


if __name__ == "__main__":
    # Example usage (would connect to DB in real implementation)
    example_row = {
        "token_id": 3336975,
        "verse_id": 42358,
        "osis_ref": "Gen.1.1",
        "book": "Gen",
        "chapter": 1,
        "verse": 1,
        "surface": "אֱלֹהִ֑ים",
        "word_position": 3,
        "lemma": "God",
        "strongs_id": "H0430",
        "morph": "HNcmpa",
        "pos": "NOUN",
        "transliteration": "elohim",
        "gloss": "God",
        "theological_term": None,
        "definition": "God, gods",
        "usage": None,
    }

    noun = noun_from_morph(example_row)
    print(json.dumps(noun, indent=2, ensure_ascii=False))
    print("\nOK - mapping sketch ready", file=sys.stderr)
