#!/usr/bin/env python3
"""
CLI tests for `pmagent report kb` (AgentPM-Next:M3).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path


def _write_registry(tmp_path: Path) -> Path:
    """Create a minimal kb_registry.json with a couple of docs."""
    registry = {
        "version": "1.0",
        "documents": [
            {
                "id": "doc-fresh",
                "title": "Fresh Doc",
                "path": "docs/fresh.md",
                "type": "ssot",
                "owning_subsystem": "docs",
                "min_refresh_interval_days": 30,
                "last_seen_mtime": None,
            },
            {
                "id": "doc-missing",
                "title": "Missing Doc",
                "path": "docs/missing.md",
                "type": "ssot",
                "owning_subsystem": "docs",
                "min_refresh_interval_days": 30,
                "last_seen_mtime": None,
            },
        ],
    }
    registry_path = tmp_path / "kb_registry.json"
    registry_path.write_text(json.dumps(registry))

    # Create fresh.md file so only one doc is missing
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "fresh.md").write_text("# Fresh\n")

    return registry_path


def _write_manifest(tmp_path: Path, now: datetime) -> Path:
    """Create a minimal plan_kb_fix manifest with some applied actions."""
    manifests_dir = tmp_path / "evidence" / "plan_kb_fix"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifests_dir / "run-test.json"
    payload = {
        "mode": "apply",
        "filters": {},
        "source": {
            "worklist_items": 1,
            "generated_at": now.isoformat(),
        },
        "actions": [],
        "summary": {
            "total_actions": 1,
            "actions_applied": 3,
            "actions_skipped": 0,
            "files_created": [],
            "files_modified": [],
            "errors": [],
        },
    }
    manifest_path.write_text(json.dumps(payload))
    return manifest_path


def test_report_kb_json_only_with_registry_and_manifest(tmp_path, monkeypatch):
    """Helper compute_kb_doc_health_metrics should emit metrics with registry + manifest."""
    from agentpm.status.kb_metrics import compute_kb_doc_health_metrics
    from agentpm.kb.registry import save_registry, KBDocumentRegistry, KBDocument

    # Build a small registry in tmp_path
    registry = KBDocumentRegistry()
    doc_fresh = KBDocument(
        id="doc-fresh",
        title="Fresh Doc",
        path="docs/fresh.md",
        type="ssot",
        owning_subsystem="docs",
    )
    doc_missing = KBDocument(
        id="doc-missing",
        title="Missing Doc",
        path="docs/missing.md",
        type="ssot",
        owning_subsystem="docs",
    )
    registry.add_document(doc_fresh)
    registry.add_document(doc_missing)

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "fresh.md").write_text("# Fresh\n")

    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    now = datetime.now(UTC)
    manifests_dir = tmp_path / "evidence" / "plan_kb_fix"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    _ = _write_manifest(tmp_path, now)

    report = compute_kb_doc_health_metrics(
        registry_path=registry_path,
        manifests_dir=manifests_dir,
        now=now,
    )

    assert report["available"] is True
    metrics = report["metrics"]

    assert "kb_fresh_ratio" in metrics
    assert "kb_missing_count" in metrics
    assert "kb_stale_count_by_subsystem" in metrics
    assert "kb_fixes_applied_last_7d" in metrics
    assert metrics["kb_fixes_applied_last_7d"] == 3


def test_report_kb_handles_missing_registry(tmp_path, monkeypatch):
    """CLI `pmagent report kb --json-only` should succeed and emit JSON."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "report", "kb", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout.strip()
    data = json.loads(output)

    assert "available" in data
    assert "metrics" in data
