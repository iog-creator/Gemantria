"""Tests for scripts/governance/ingest_doc_embeddings.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scripts.governance import ingest_doc_embeddings as mod


def test_get_embedding_model_from_config() -> None:
    """Test that get_embedding_model retrieves model from config."""
    with patch("scripts.governance.ingest_doc_embeddings.get_lm_model_config") as mock_config:
        mock_config.return_value = {"embedding_model": "bge-m3:latest"}
        model = mod.get_embedding_model()
        assert model == "bge-m3:latest"


def test_get_embedding_model_override() -> None:
    """Test that model_name override works."""
    model = mod.get_embedding_model("custom-model")
    assert model == "custom-model"


def test_get_embedding_model_missing() -> None:
    """Test that missing model raises RuntimeError."""
    with patch("scripts.governance.ingest_doc_embeddings.get_lm_model_config") as mock_config:
        mock_config.return_value = {}
        with pytest.raises(RuntimeError, match="No EMBEDDING_MODEL configured"):
            mod.get_embedding_model()


def test_embed_fragments_dry_run() -> None:
    """Test that dry-run returns mock embeddings."""
    fragments = [
        {"fragment_id": "f1", "content": "test content 1"},
        {"fragment_id": "f2", "content": "test content 2"},
    ]
    result = mod.embed_fragments(fragments, "bge-m3:latest", dry_run=True)
    assert len(result) == 2
    assert result[0]["fragment_id"] == "f1"
    assert len(result[0]["embedding"]) == 1024
    assert all(x == 0.0 for x in result[0]["embedding"])


def test_embed_fragments_real() -> None:
    """Test that real embeddings are generated."""
    fragments = [
        {"fragment_id": "f1", "content": "test content"},
    ]
    with patch("scripts.governance.ingest_doc_embeddings.lm_studio") as mock_lm:
        mock_lm.embed.return_value = [[0.1] * 1024]
        result = mod.embed_fragments(fragments, "bge-m3:latest", dry_run=False)
        assert len(result) == 1
        assert result[0]["fragment_id"] == "f1"
        assert len(result[0]["embedding"]) == 1024
        assert result[0]["embedding"][0] == 0.1


def test_embed_fragments_dimension_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that non-1024 dimension triggers warning."""
    fragments = [{"fragment_id": "f1", "content": "test"}]
    with patch("scripts.governance.ingest_doc_embeddings.lm_studio") as mock_lm:
        mock_lm.embed.return_value = [[0.1] * 512]  # Wrong dimension
        # Should not raise, just warn
        result = mod.embed_fragments(fragments, "bge-m3:latest", dry_run=False)
        assert len(result) == 1


def test_store_embeddings_dry_run() -> None:
    """Test that dry-run doesn't write to DB."""
    mock_conn = MagicMock()
    embeddings = [
        {"fragment_id": "f1", "embedding": [0.1] * 1024},
    ]
    count = mod.store_embeddings(mock_conn, embeddings, "bge-m3:latest", dry_run=True)
    assert count == 1
    mock_conn.execute.assert_not_called()


def test_store_embeddings_real() -> None:
    """Test that real embeddings are stored."""
    mock_conn = MagicMock()
    embeddings = [
        {"fragment_id": "f1", "embedding": [0.1, 0.2, 0.3]},
    ]
    count = mod.store_embeddings(mock_conn, embeddings, "bge-m3:latest", dry_run=False)
    assert count == 1
    assert mock_conn.execute.call_count == 1
    mock_conn.commit.assert_called_once()


def test_ingest_embeddings_db_off() -> None:
    """Test that DB-off is handled gracefully."""
    with patch("scripts.governance.ingest_doc_embeddings.get_control_engine") as mock_engine:
        mock_engine.side_effect = RuntimeError("DB unavailable")
        result = mod.ingest_embeddings(dry_run=True)
        assert "error" in result
        assert "DB connection failed" in result["error"]


def test_ingest_embeddings_no_model() -> None:
    """Test that missing model is handled gracefully."""
    with patch("scripts.governance.ingest_doc_embeddings.get_embedding_model") as mock_model:
        mock_model.side_effect = RuntimeError("No EMBEDDING_MODEL configured")
        result = mod.ingest_embeddings(dry_run=True)
        assert "error" in result
        assert "No EMBEDDING_MODEL" in result["error"]
