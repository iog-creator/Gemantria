"""Tests for control-plane widget adapters."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agentpm.control_widgets.adapter import (
    load_biblescholar_reference_widget_props,
    load_graph_compliance_widget_props,
)

REPO = Path(__file__).resolve().parents[3]


def test_load_graph_compliance_widget_props_healthy():
    """Test loading graph compliance widget props with healthy data."""
    with TemporaryDirectory() as tmpdir:
        compliance_file = Path(tmpdir) / "graph_compliance.json"
        compliance_data = {
            "schema": "graph_compliance_v1",
            "generated_at": "2025-11-21T10:00:00Z",
            "ok": True,
            "connection_ok": True,
            "total_runs_with_violations": 0,
            "metrics": {
                "by_tool": {},
                "by_node": {},
                "by_pattern": {},
                "by_batch": {},
            },
            "window_days": 30,
        }
        compliance_file.write_text(json.dumps(compliance_data), encoding="utf-8")

        # Temporarily patch the path
        import agentpm.control_widgets.adapter as adapter_module

        original_path = adapter_module.GRAPH_COMPLIANCE_PATH
        adapter_module.GRAPH_COMPLIANCE_PATH = compliance_file

        try:
            props = load_graph_compliance_widget_props()
            assert props["status"] == "ok"
            assert props["label"] == "Graph compliance: No violations"
            assert props["color"] == "green"
            assert props["icon"] == "status-healthy"
            assert props["metrics"]["totalRunsWithViolations"] == 0
            assert props["metrics"]["windowDays"] == 30
        finally:
            adapter_module.GRAPH_COMPLIANCE_PATH = original_path


def test_load_graph_compliance_widget_props_degraded():
    """Test loading graph compliance widget props with violations."""
    with TemporaryDirectory() as tmpdir:
        compliance_file = Path(tmpdir) / "graph_compliance.json"
        compliance_data = {
            "schema": "graph_compliance_v1",
            "generated_at": "2025-11-21T10:00:00Z",
            "ok": True,
            "connection_ok": True,
            "total_runs_with_violations": 5,
            "metrics": {
                "by_tool": {"tool1": 3, "tool2": 2},
                "by_node": {"node1": 2},
                "by_pattern": {},
                "by_batch": {},
            },
            "window_days": 30,
        }
        compliance_file.write_text(json.dumps(compliance_data), encoding="utf-8")

        import agentpm.control_widgets.adapter as adapter_module

        original_path = adapter_module.GRAPH_COMPLIANCE_PATH
        adapter_module.GRAPH_COMPLIANCE_PATH = compliance_file

        try:
            props = load_graph_compliance_widget_props()
            assert props["status"] == "degraded"
            assert "5 violation(s)" in props["label"]
            assert props["color"] == "yellow"
            assert props["icon"] == "status-warning"
            assert props["metrics"]["totalRunsWithViolations"] == 5
            assert props["metrics"]["byTool"]["tool1"] == 3
        finally:
            adapter_module.GRAPH_COMPLIANCE_PATH = original_path


def test_load_graph_compliance_widget_props_missing_file():
    """Test loading graph compliance widget props when file is missing."""
    import agentpm.control_widgets.adapter as adapter_module

    original_path = adapter_module.GRAPH_COMPLIANCE_PATH
    adapter_module.GRAPH_COMPLIANCE_PATH = Path("/nonexistent/file.json")

    try:
        props = load_graph_compliance_widget_props()
        assert props["status"] == "unknown"
        assert "offline-safe mode" in props["label"]
        assert props["color"] == "grey"
    finally:
        adapter_module.GRAPH_COMPLIANCE_PATH = original_path


def test_load_biblescholar_reference_widget_props_active():
    """Test loading BibleScholar reference widget props with active data."""
    with TemporaryDirectory() as tmpdir:
        reference_file = Path(tmpdir) / "biblescholar_reference.json"
        reference_data = {
            "schema": "biblescholar_reference_v1",
            "generated_at": "2025-11-21T10:00:00Z",
            "ok": True,
            "connection_ok": True,
            "questions": [],
            "summary": {
                "total_questions": 10,
                "by_mode": {"lm_studio": 8, "fallback": 2},
                "by_verse_ref": {"John 3:16": 3, "Genesis 1:1": 2},
            },
            "window_days": 30,
        }
        reference_file.write_text(json.dumps(reference_data), encoding="utf-8")

        import agentpm.control_widgets.adapter as adapter_module

        original_path = adapter_module.BIBLESCHOLAR_REFERENCE_PATH
        adapter_module.BIBLESCHOLAR_REFERENCE_PATH = reference_file

        try:
            props = load_biblescholar_reference_widget_props()
            assert props["status"] == "active"
            assert "10 question(s)" in props["label"]
            assert props["color"] == "green"
            assert props["icon"] == "status-active"
            assert props["metrics"]["totalQuestions"] == 10
            assert props["metrics"]["byMode"]["lm_studio"] == 8
        finally:
            adapter_module.BIBLESCHOLAR_REFERENCE_PATH = original_path


def test_load_biblescholar_reference_widget_props_empty():
    """Test loading BibleScholar reference widget props with empty data."""
    with TemporaryDirectory() as tmpdir:
        reference_file = Path(tmpdir) / "biblescholar_reference.json"
        reference_data = {
            "schema": "biblescholar_reference_v1",
            "generated_at": "2025-11-21T10:00:00Z",
            "ok": True,
            "connection_ok": True,
            "questions": [],
            "summary": {
                "total_questions": 0,
                "by_mode": {},
                "by_verse_ref": {},
            },
            "window_days": 30,
        }
        reference_file.write_text(json.dumps(reference_data), encoding="utf-8")

        import agentpm.control_widgets.adapter as adapter_module

        original_path = adapter_module.BIBLESCHOLAR_REFERENCE_PATH
        adapter_module.BIBLESCHOLAR_REFERENCE_PATH = reference_file

        try:
            props = load_biblescholar_reference_widget_props()
            assert props["status"] == "empty"
            assert "No questions yet" in props["label"]
            assert props["color"] == "grey"
            assert props["icon"] == "status-empty"
            assert props["metrics"]["totalQuestions"] == 0
        finally:
            adapter_module.BIBLESCHOLAR_REFERENCE_PATH = original_path


def test_load_biblescholar_reference_widget_props_missing_file():
    """Test loading BibleScholar reference widget props when file is missing."""
    import agentpm.control_widgets.adapter as adapter_module

    original_path = adapter_module.BIBLESCHOLAR_REFERENCE_PATH
    adapter_module.BIBLESCHOLAR_REFERENCE_PATH = Path("/nonexistent/file.json")

    try:
        props = load_biblescholar_reference_widget_props()
        assert props["status"] == "unknown"
        assert "offline-safe mode" in props["label"]
        assert props["color"] == "grey"
    finally:
        adapter_module.BIBLESCHOLAR_REFERENCE_PATH = original_path
