#!/usr/bin/env python3
"""
Tests for BibleScholar passage service.

Phase-9A: Verifies passage lookup and commentary generation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentpm.biblescholar.bible_db_adapter import VerseRecord  # noqa: E402
from agentpm.biblescholar.passage import (  # noqa: E402
    fetch_passage_dict,
    generate_commentary,
    get_passage_and_commentary,
)


def test_fetch_passage_dict_valid_reference():
    """Test fetch_passage_dict with valid reference."""
    with patch("agentpm.biblescholar.passage.fetch_passage") as mock_fetch:
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="John",
            chapter_num=3,
            verse_num=16,
            text="For God so loved the world...",
            translation_source="KJV",
        )
        mock_fetch.return_value = [mock_verse]

        result = fetch_passage_dict("John 3:16")

        assert result["reference"] == "John 3:16"
        assert len(result["verses"]) == 1
        assert result["verses"][0]["book"] == "John"
        assert result["verses"][0]["chapter"] == 3
        assert result["verses"][0]["verse"] == 16
        assert "For God so loved" in result["verses"][0]["text"]
        assert len(result["errors"]) == 0


def test_fetch_passage_dict_invalid_reference():
    """Test fetch_passage_dict with invalid reference."""
    with patch("agentpm.biblescholar.passage.fetch_passage") as mock_fetch:
        mock_fetch.return_value = []

        result = fetch_passage_dict("Invalid 99:99")

        assert result["reference"] == "Invalid 99:99"
        assert len(result["verses"]) == 0
        assert len(result["errors"]) > 0
        assert "No verses found" in result["errors"][0]


def test_fetch_passage_dict_empty_reference():
    """Test fetch_passage_dict with empty reference."""
    result = fetch_passage_dict("")

    assert result["reference"] == ""
    assert len(result["verses"]) == 0
    assert len(result["errors"]) > 0
    assert "cannot be empty" in result["errors"][0]


def test_generate_commentary_with_lm():
    """Test generate_commentary when LM is available."""
    passage = {
        "reference": "John 3:16",
        "verses": [
            {"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world..."}
        ],
    }

    with patch("agentpm.biblescholar.passage.theology_chat") as mock_chat:
        mock_chat.return_value = "This passage speaks of God's love for humanity..."

        result = generate_commentary(passage, use_lm=True)

        assert result["source"] == "lm_theology"
        assert "God's love" in result["text"]
        mock_chat.assert_called_once()


def test_generate_commentary_without_lm():
    """Test generate_commentary when use_lm=False."""
    passage = {
        "reference": "John 3:16",
        "verses": [{"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved..."}],
    }

    result = generate_commentary(passage, use_lm=False)

    assert result["source"] == "fallback"
    assert "disabled" in result["text"].lower()


def test_generate_commentary_lm_unavailable():
    """Test generate_commentary when LM raises exception."""
    passage = {
        "reference": "John 3:16",
        "verses": [{"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved..."}],
    }

    with patch("agentpm.biblescholar.passage.theology_chat") as mock_chat:
        mock_chat.side_effect = RuntimeError("LM unavailable")

        result = generate_commentary(passage, use_lm=True)

        assert result["source"] == "fallback"
        assert "unavailable" in result["text"].lower()


def test_generate_commentary_empty_passage():
    """Test generate_commentary with empty passage."""
    passage = {"reference": "John 3:16", "verses": []}

    result = generate_commentary(passage, use_lm=True)

    assert result["source"] == "fallback"
    assert "No passage text" in result["text"]


def test_get_passage_and_commentary_success():
    """Test get_passage_and_commentary with successful lookup and commentary."""
    with (
        patch("agentpm.biblescholar.passage.fetch_passage") as mock_fetch,
        patch("agentpm.biblescholar.passage.theology_chat") as mock_chat,
    ):
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="John",
            chapter_num=3,
            verse_num=16,
            text="For God so loved the world...",
            translation_source="KJV",
        )
        mock_fetch.return_value = [mock_verse]
        mock_chat.return_value = "This passage speaks of God's love..."

        result = get_passage_and_commentary("John 3:16", use_lm=True)

        assert result["reference"] == "John 3:16"
        assert len(result["verses"]) == 1
        assert result["commentary"]["source"] == "lm_theology"
        assert "errors" in result
        assert isinstance(result["errors"], list)


def test_get_passage_and_commentary_no_lm():
    """Test get_passage_and_commentary with use_lm=False."""
    with patch("agentpm.biblescholar.passage.fetch_passage") as mock_fetch:
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="John",
            chapter_num=3,
            verse_num=16,
            text="For God so loved the world...",
            translation_source="KJV",
        )
        mock_fetch.return_value = [mock_verse]

        result = get_passage_and_commentary("John 3:16", use_lm=False)

        assert result["reference"] == "John 3:16"
        assert len(result["verses"]) == 1
        assert result["commentary"]["source"] == "fallback"


def test_get_passage_and_commentary_always_returns_dict():
    """Test that get_passage_and_commentary always returns expected dict structure."""
    with patch("agentpm.biblescholar.passage.fetch_passage") as mock_fetch:
        mock_fetch.return_value = []

        result = get_passage_and_commentary("Invalid 99:99", use_lm=True)

        # Should always return dict with these keys
        assert "reference" in result
        assert "verses" in result
        assert "commentary" in result
        assert "errors" in result
        assert isinstance(result["verses"], list)
        assert isinstance(result["errors"], list)
        assert "source" in result["commentary"]
        assert "text" in result["commentary"]
