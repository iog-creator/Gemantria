#!/usr/bin/env python3
"""
Tests for Document Q&A Module

E2E Pipeline (Reality Check #1): Tests for answer_doc_question() function.
"""

from __future__ import annotations

from unittest.mock import patch


from agentpm.knowledge.qa_docs import answer_doc_question


def test_happy_path(monkeypatch):
    """Test happy path: mock LM + DB returns answer + sources."""
    # Mock retrieval to return sections
    mock_sections = [
        {
            "id": "section-1",
            "source_id": "source-1",
            "section_title": "Phase-6P",
            "body": "Phase-6P delivers BibleScholar Reference Answer Slice using bible_db, Gematria, similarity, and guarded LM calls.",
            "order_index": 1,
            "source_path": "docs/SSOT/MASTER_PLAN.md",
            "source_title": "MASTER PLAN",
        }
    ]

    def mock_retrieve(query: str, limit: int = 5):
        return mock_sections

    # Mock guarded_lm_call to return success
    mock_lm_result = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [
                {"message": {"content": "Phase-6P delivers BibleScholar Reference Answer Slice."}}
            ],
            "usage": {"total_tokens": 100},
            "model": "test-model",
        },
        "call_site": "knowledge.qa_docs.answer_doc_question",
    }

    with patch("agentpm.knowledge.qa_docs.retrieve_doc_sections", side_effect=mock_retrieve):
        with patch("agentpm.knowledge.qa_docs.guarded_lm_call", return_value=mock_lm_result):
            result = answer_doc_question("What does Phase-6P deliver?")

    assert result["ok"] is True
    assert result["answer"] == "Phase-6P delivers BibleScholar Reference Answer Slice."
    assert result["sources"] == ["section-1"]
    assert result["mode"] == "lm_on"
    assert result["lm_meta"] is not None
    assert result["lm_meta"]["model"] == "test-model"


def test_db_off(monkeypatch):
    """Test db_off scenario: DB unreachable → LM still called with empty context."""

    # Mock retrieval to return empty list (DB unavailable)
    def mock_retrieve(query: str, limit: int = 5):
        return []

    # Mock guarded_lm_call to return success (LM still works)
    mock_lm_result = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [
                {
                    "message": {
                        "content": "I don't have relevant documentation to answer this question."
                    }
                }
            ],
            "usage": {"total_tokens": 50},
            "model": "test-model",
        },
        "call_site": "knowledge.qa_docs.answer_doc_question",
    }

    with patch("agentpm.knowledge.qa_docs.retrieve_doc_sections", side_effect=mock_retrieve):
        with patch("agentpm.knowledge.qa_docs.guarded_lm_call", return_value=mock_lm_result):
            result = answer_doc_question("What does Phase-6P deliver?")

    assert result["ok"] is True
    assert result["sources"] == []
    assert result["mode"] == "db_off"  # No sections found
    assert "documentation" in result["answer"].lower()


def test_no_results(monkeypatch):
    """Test no_results: query not found → LM called with empty context."""

    # Mock retrieval to return empty list (no matches)
    def mock_retrieve(query: str, limit: int = 5):
        return []

    # Mock guarded_lm_call to return success
    mock_lm_result = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [{"message": {"content": "No relevant documentation found."}}],
            "usage": {"total_tokens": 30},
            "model": "test-model",
        },
        "call_site": "knowledge.qa_docs.answer_doc_question",
    }

    with patch("agentpm.knowledge.qa_docs.retrieve_doc_sections", side_effect=mock_retrieve):
        with patch("agentpm.knowledge.qa_docs.guarded_lm_call", return_value=mock_lm_result):
            result = answer_doc_question("What is the meaning of life?")

    assert result["ok"] is True
    assert result["sources"] == []
    assert result["mode"] == "db_off"


def test_budget_exceeded(monkeypatch):
    """Test budget_exceeded: guarded_lm_call budget error handled."""
    # Mock retrieval to return sections
    mock_sections = [
        {
            "id": "section-1",
            "source_id": "source-1",
            "section_title": "Test Section",
            "body": "Test content",
            "order_index": 1,
            "source_path": "test.md",
            "source_title": "Test",
        }
    ]

    def mock_retrieve(query: str, limit: int = 5):
        return mock_sections

    # Mock guarded_lm_call to return budget_exceeded
    mock_lm_result = {
        "ok": False,
        "mode": "budget_exceeded",
        "reason": "Budget exceeded",
        "response": None,
        "call_site": "knowledge.qa_docs.answer_doc_question",
    }

    with patch("agentpm.knowledge.qa_docs.retrieve_doc_sections", side_effect=mock_retrieve):
        with patch("agentpm.knowledge.qa_docs.guarded_lm_call", return_value=mock_lm_result):
            result = answer_doc_question("What does Phase-6P deliver?")

    assert result["ok"] is False
    assert result["answer"] is None
    assert result["sources"] == ["section-1"]  # Sections still retrieved
    assert result["mode"] == "budget_exceeded"


def test_lm_off(monkeypatch):
    """Test lm_off: LM Studio disabled → returns appropriate mode."""
    # Mock retrieval to return sections
    mock_sections = [
        {
            "id": "section-1",
            "source_id": "source-1",
            "section_title": "Test Section",
            "body": "Test content",
            "order_index": 1,
            "source_path": "test.md",
            "source_title": "Test",
        }
    ]

    def mock_retrieve(query: str, limit: int = 5):
        return mock_sections

    # Mock guarded_lm_call to return lm_off
    mock_lm_result = {
        "ok": False,
        "mode": "lm_off",
        "reason": "lm_studio_disabled",
        "response": None,
        "call_site": "knowledge.qa_docs.answer_doc_question",
    }

    with patch("agentpm.knowledge.qa_docs.retrieve_doc_sections", side_effect=mock_retrieve):
        with patch("agentpm.knowledge.qa_docs.guarded_lm_call", return_value=mock_lm_result):
            result = answer_doc_question("What does Phase-6P deliver?")

    assert result["ok"] is False
    assert result["answer"] is None
    assert result["sources"] == ["section-1"]
    assert result["mode"] == "lm_off"
