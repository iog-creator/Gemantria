import os

import pytest

from src.graph.nodes.validation import validate_noun

pytestmark = pytest.mark.skipif(
    not os.getenv("BIBLE_DB_DSN"),
    reason="BIBLE_DB_DSN not set; skipping DB-backed integration test",
)


def test_validate_noun_shape_when_db_present():
    out = validate_noun("אדם")
    assert set(out.keys()) == {"surface", "normalized", "gematria", "db", "llm"}
    db = out["db"]
    assert set(db.keys()) == {
        "present_in_bible_db",
        "strong_number",
        "lemma_frequency",
        "verse_context",
    }
    assert isinstance(db["present_in_bible_db"], bool)
    # If present, fields should be populated with expected types
    if db["present_in_bible_db"]:
        assert db["strong_number"] is not None
        assert isinstance(db["lemma_frequency"], int)
        assert isinstance(db["verse_context"], list)
