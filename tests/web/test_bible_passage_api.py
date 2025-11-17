#!/usr/bin/env python3
"""
Tests for Bible passage API endpoint.

Phase-9A: Verifies /api/bible/passage endpoint returns correct JSON shape.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.services.api_server import app  # noqa: E402

client = TestClient(app)


def test_bible_passage_api_valid_reference():
    """Test /api/bible/passage with valid reference."""
    mock_result = {
        "reference": "John 3:16",
        "verses": [{"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world..."}],
        "commentary": {"source": "lm_theology", "text": "This passage speaks of God's love..."},
        "errors": [],
    }

    with patch("agentpm.biblescholar.passage.get_passage_and_commentary") as mock_get:
        mock_get.return_value = mock_result

        response = client.get("/api/bible/passage?reference=John%203:16&use_lm=true")

        assert response.status_code == 200
        data = response.json()
        assert data["reference"] == "John 3:16"
        assert len(data["verses"]) == 1
        assert data["commentary"]["source"] == "lm_theology"
        assert "errors" in data


def test_bible_passage_api_invalid_reference():
    """Test /api/bible/passage with invalid reference."""
    mock_result = {
        "reference": "Invalid 99:99",
        "verses": [],
        "commentary": {"source": "fallback", "text": "No passage text available."},
        "errors": ["No verses found for reference: Invalid 99:99"],
    }

    with patch("agentpm.biblescholar.passage.get_passage_and_commentary") as mock_get:
        mock_get.return_value = mock_result

        response = client.get("/api/bible/passage?reference=Invalid%2099:99")

        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) > 0
        assert len(data["verses"]) == 0


def test_bible_passage_api_lm_disabled():
    """Test /api/bible/passage with use_lm=false."""
    mock_result = {
        "reference": "John 3:16",
        "verses": [{"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world..."}],
        "commentary": {"source": "fallback", "text": "Theology model commentary is disabled."},
        "errors": [],
    }

    with patch("agentpm.biblescholar.passage.get_passage_and_commentary") as mock_get:
        mock_get.return_value = mock_result

        response = client.get("/api/bible/passage?reference=John%203:16&use_lm=false")

        assert response.status_code == 200
        data = response.json()
        assert data["commentary"]["source"] == "fallback"


def test_bible_passage_api_missing_reference():
    """Test /api/bible/passage without reference parameter."""
    response = client.get("/api/bible/passage")

    assert response.status_code == 422  # Validation error


def test_bible_passage_api_unexpected_error():
    """Test /api/bible/passage when service raises unexpected exception."""
    with patch("agentpm.biblescholar.passage.get_passage_and_commentary") as mock_get:
        mock_get.side_effect = Exception("Unexpected error")

        response = client.get("/api/bible/passage?reference=John%203:16")

        assert response.status_code == 500
        data = response.json()
        assert "errors" in data
        assert "Unexpected error" in data["errors"][0]
