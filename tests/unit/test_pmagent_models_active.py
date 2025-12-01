#!/usr/bin/env python3
"""Tests for pmagent models active command (config-only; no LM calls)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pmagent.cli import app


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@patch("pmagent.cli.get_lm_model_config")
@patch("pmagent.cli.get_retrieval_lane_models")
def test_models_active_default_profile(mock_retrieval, mock_config, runner):
    """Test models active with DEFAULT profile (Granite stack)."""
    mock_retrieval.return_value = {
        "profile": "DEFAULT",
        "embedding_model": "granite-embedding:278m",
        "reranker_model": "granite4:tiny-h",
        "granite_active": True,
    }
    mock_config.return_value = {
        "local_agent_model": "granite4:tiny-h",
        "bible_embedding_model": None,
    }

    result = runner.invoke(app, ["models", "active"])

    assert result.exit_code == 0
    assert "ACTIVE RETRIEVAL PROFILE: DEFAULT" in result.stdout
    assert "EMBEDDING_MODEL:          granite-embedding:278m" in result.stdout
    assert "RERANKER_MODEL:           granite4:tiny-h" in result.stdout
    assert "LOCAL_AGENT_MODEL:        granite4:tiny-h" in result.stdout
    assert "BIBLE_EMBEDDING_MODEL" not in result.stdout


@patch("pmagent.cli.get_lm_model_config")
@patch("pmagent.cli.get_retrieval_lane_models")
def test_models_active_granite_profile(mock_retrieval, mock_config, runner):
    """Test models active with GRANITE profile."""
    mock_retrieval.return_value = {
        "profile": "GRANITE",
        "embedding_model": "ibm-granite/granite-embedding-english-r2",
        "reranker_model": "ibm-granite/granite-embedding-reranker-english-r2",
        "granite_active": True,
    }
    mock_config.return_value = {
        "local_agent_model": "ibm-granite/granite-4.0-h-tiny-GGUF",
        "bible_embedding_model": None,
    }

    result = runner.invoke(app, ["models", "active"])

    assert result.exit_code == 0
    assert "ACTIVE RETRIEVAL PROFILE: GRANITE" in result.stdout
    assert "EMBEDDING_MODEL:          ibm-granite/granite-embedding-english-r2" in result.stdout
    assert (
        "RERANKER_MODEL:           ibm-granite/granite-embedding-reranker-english-r2"
        in result.stdout
    )
    assert "LOCAL_AGENT_MODEL:        ibm-granite/granite-4.0-h-tiny-GGUF" in result.stdout


@patch("pmagent.cli.get_lm_model_config")
@patch("pmagent.cli.get_retrieval_lane_models")
def test_models_active_with_bible_embedding(mock_retrieval, mock_config, runner):
    """Test models active when BIBLE_EMBEDDING_MODEL is configured."""
    mock_retrieval.return_value = {
        "profile": "DEFAULT",
        "embedding_model": "granite-embedding:278m",
        "reranker_model": "granite4:tiny-h",
        "granite_active": True,
    }
    mock_config.return_value = {
        "local_agent_model": "granite4:tiny-h",
        "bible_embedding_model": "bge-m3:latest",
    }

    result = runner.invoke(app, ["models", "active"])

    assert result.exit_code == 0
    assert "ACTIVE RETRIEVAL PROFILE: DEFAULT" in result.stdout
    assert "BIBLE_EMBEDDING_MODEL:    bge-m3:latest" in result.stdout
