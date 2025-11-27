import os

import pytest

from agentpm.modules.gematria.utils.collect_nouns_db import collect_nouns_for_book

pytestmark = pytest.mark.requires_bible_db


def _has_bible() -> bool:
    return bool(os.getenv("BIBLE_DB_DSN"))


def test_collect_nouns_genesis_smoke():
    if not _has_bible():
        pytest.skip("BIBLE_DB_DSN not set; skipping bible_db integration test")
    nouns = collect_nouns_for_book("Genesis")
    assert isinstance(nouns, list) and len(nouns) > 0
    sample = nouns[0]
    for k in ("hebrew", "name", "primary_verse", "freq", "book"):
        assert k in sample
