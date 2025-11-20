#!/usr/bin/env python3
"""
Tests for KB-aware status explanation (KB-Reg:M5)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.status.explain import explain_system_status, _add_kb_documentation_section


def test_explain_includes_documentation_section():
    """Test that explain_system_status includes documentation section."""
    explanation = explain_system_status(use_lm=False)

    assert "documentation" in explanation
    assert isinstance(explanation["documentation"], dict)
    assert "available" in explanation["documentation"]
    assert "total" in explanation["documentation"]
    assert "by_subsystem" in explanation["documentation"]
    assert "by_type" in explanation["documentation"]
    assert "hints" in explanation["documentation"]
    assert "key_docs" in explanation["documentation"]


def test_add_kb_documentation_section_adds_section():
    """Test that _add_kb_documentation_section adds documentation to explanation."""
    explanation = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "Everything is working.",
    }

    enhanced = _add_kb_documentation_section(explanation)

    assert "documentation" in enhanced
    assert isinstance(enhanced["documentation"], dict)
    assert "available" in enhanced["documentation"]
    assert "total" in enhanced["documentation"]
    assert "by_subsystem" in enhanced["documentation"]
    assert "by_type" in enhanced["documentation"]
    assert "hints" in enhanced["documentation"]
    assert "key_docs" in enhanced["documentation"]
    # Original fields preserved
    assert enhanced["level"] == "OK"
    assert enhanced["headline"] == "All systems nominal"
    assert enhanced["details"] == "Everything is working."


def test_add_kb_documentation_section_handles_missing_registry():
    """Test that _add_kb_documentation_section handles missing registry gracefully."""
    explanation = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "Everything is working.",
    }

    # Should not raise even if registry is missing
    enhanced = _add_kb_documentation_section(explanation)

    assert "documentation" in enhanced
    # Should have empty/fallback structure
    assert enhanced["documentation"]["available"] is False or enhanced["documentation"]["available"] is True
    assert isinstance(enhanced["documentation"]["total"], int)
