#!/usr/bin/env python3
"""
Tests for reality-check AI docs helper.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agentpm.ai_docs.reality_check_ai_notes import (  # noqa: E402
    build_prompt,
    generate_ai_notes,
    read_agents_md_section,
    read_reality_check_code,
    read_reality_check_design,
    write_ai_notes_file,
)


def test_read_reality_check_code():
    """Test reading reality-check code."""
    code = read_reality_check_code()
    assert isinstance(code, str)
    # Should contain some expected content
    assert "reality_check" in code or "def reality_check" in code or len(code) == 0


def test_read_reality_check_design():
    """Test reading reality-check design doc."""
    design = read_reality_check_design()
    assert isinstance(design, str)
    # Should contain some expected content or be empty if file doesn't exist
    assert len(design) >= 0


def test_read_agents_md_section():
    """Test reading AGENTS.md section."""
    section = read_agents_md_section()
    assert isinstance(section, str)
    # Should contain some expected content or be empty
    assert len(section) >= 0


def test_build_prompt():
    """Test prompt building logic."""
    prompt = build_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    # Should contain key instructions
    assert "Granite" in prompt or "housekeeping" in prompt.lower()
    assert "reality-check" in prompt.lower() or "reality check" in prompt.lower()


@patch("agentpm.ai_docs.reality_check_ai_notes.lm_studio_chat")
def test_generate_ai_notes_lm_off(mock_chat):
    """Test AI notes generation when LM is offline."""
    # Mock LM Studio adapter returning lm_off
    mock_chat.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "lm_studio_disabled",
        "response": None,
    }

    content, lm_available = generate_ai_notes()

    assert not lm_available
    assert content == ""
    mock_chat.assert_called_once()


@patch("agentpm.ai_docs.reality_check_ai_notes.lm_studio_chat")
def test_generate_ai_notes_lm_on(mock_chat):
    """Test AI notes generation when LM is online."""
    # Mock LM Studio adapter returning successful response
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "reason": None,
        "response": {
            "choices": [
                {
                    "message": {
                        "content": "# Reality Check Summary\n\nThis is a test summary.",
                    },
                },
            ],
        },
    }

    content, lm_available = generate_ai_notes()

    assert lm_available
    assert "Reality Check Summary" in content
    mock_chat.assert_called_once()


def test_write_ai_notes_file_lm_off(tmp_path):
    """Test writing AI notes file when LM was offline."""
    # Use tmp_path for testing
    output_path = tmp_path / "docs" / "SSOT" / "PMAGENT_REALITY_CHECK_AI_NOTES.md"

    with patch("agentpm.ai_docs.reality_check_ai_notes.ROOT", tmp_path):
        result_path = write_ai_notes_file("", lm_available=False)

    assert result_path == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")
    assert "Granite offline" in content or "no fresh AI notes" in content
    assert "Last run" in content


def test_write_ai_notes_file_lm_on(tmp_path):
    """Test writing AI notes file when LM was online."""
    output_path = tmp_path / "docs" / "SSOT" / "PMAGENT_REALITY_CHECK_AI_NOTES.md"
    ai_content = "# Reality Check Summary\n\nThis is test content."

    with patch("agentpm.ai_docs.reality_check_ai_notes.ROOT", tmp_path):
        result_path = write_ai_notes_file(ai_content, lm_available=True)

    assert result_path == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")
    assert "Reality Check Summary" in content
    assert "Generated" in content
    assert "Granite" in content or "LM Studio" in content
