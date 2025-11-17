#!/usr/bin/env python3
"""
Tests for Bible Scholar HTML page.

Phase-9A: Verifies /bible page renders correctly and contains required elements.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.services.api_server import app  # noqa: E402

client = TestClient(app)


def test_bible_page_returns_200():
    """Test that /bible returns 200 OK."""
    response = client.get("/bible")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_bible_page_contains_title():
    """Test that /bible contains 'Bible Scholar' title."""
    response = client.get("/bible")
    assert "Bible Scholar" in response.text
    assert "Passage & Commentary" in response.text


def test_bible_page_contains_input_form():
    """Test that /bible contains input field and submit button."""
    response = client.get("/bible")
    assert 'id="reference"' in response.text
    assert 'id="use-lm"' in response.text
    assert 'type="submit"' in response.text
    assert "Lookup Passage" in response.text


def test_bible_page_contains_api_reference():
    """Test that /bible JavaScript references /api/bible/passage."""
    response = client.get("/bible")
    assert "/api/bible/passage" in response.text


def test_bible_page_contains_results_area():
    """Test that /bible contains results display elements."""
    response = client.get("/bible")
    assert 'id="results"' in response.text
    assert 'id="passage-text"' in response.text
    assert 'id="commentary-text"' in response.text


def test_bible_page_contains_tailwind():
    """Test that /bible includes Tailwind CSS."""
    response = client.get("/bible")
    assert "tailwindcss.com" in response.text
