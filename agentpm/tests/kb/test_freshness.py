"""
Tests for KB document freshness analysis (KB-Reg:M6).
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    analyze_freshness,
)


class TestAnalyzeFreshness:
    """Test freshness analysis functionality."""

    def test_analyze_freshness_stale_docs(self):
        """Test detecting stale documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create a file that exists
            doc_path = repo_root / "docs" / "test.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test Document")

            # Create document with old last_refreshed_at (beyond refresh interval)
            old_date = (datetime.now(UTC) - timedelta(days=60)).isoformat()
            doc = KBDocument(
                id="stale-doc",
                title="Stale Document",
                path="docs/test.md",
                type="ssot",  # 30 day refresh interval
                owning_subsystem="docs",
                last_refreshed_at=old_date,
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            assert result["summary"]["stale_count"] == 1
            assert len(result["stale_docs"]) == 1
            assert result["stale_docs"][0]["id"] == "stale-doc"

    def test_analyze_freshness_fresh_docs(self):
        """Test that fresh documents are not flagged as stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create a file that exists
            doc_path = repo_root / "docs" / "test.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test Document")

            # Create document with recent last_refreshed_at
            recent_date = (datetime.now(UTC) - timedelta(days=5)).isoformat()
            doc = KBDocument(
                id="fresh-doc",
                title="Fresh Document",
                path="docs/test.md",
                type="ssot",  # 30 day refresh interval
                owning_subsystem="docs",
                last_refreshed_at=recent_date,
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            assert result["summary"]["stale_count"] == 0
            assert result["summary"]["fresh_count"] == 1
            assert len(result["stale_docs"]) == 0

    def test_analyze_freshness_missing_docs(self):
        """Test detecting missing documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create document pointing to non-existent file
            doc = KBDocument(
                id="missing-doc",
                title="Missing Document",
                path="docs/missing.md",
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            assert result["summary"]["missing_count"] == 1
            assert len(result["missing_docs"]) == 1
            assert result["missing_docs"][0]["id"] == "missing-doc"

    def test_analyze_freshness_out_of_sync_docs(self):
        """Test detecting out-of-sync documents (file modified after last_seen_mtime)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create a file
            doc_path = repo_root / "docs" / "test.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test Document")
            initial_mtime = doc_path.stat().st_mtime

            # Wait a bit and modify the file
            time.sleep(1.1)
            doc_path.write_text("# Test Document Updated")

            # Create document with old last_seen_mtime (before file modification)
            doc = KBDocument(
                id="out-of-sync-doc",
                title="Out of Sync Document",
                path="docs/test.md",
                type="ssot",
                owning_subsystem="docs",
                last_seen_mtime=initial_mtime,  # Older than current file mtime
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            assert result["summary"]["out_of_sync_count"] == 1
            assert len(result["out_of_sync_docs"]) == 1
            assert result["out_of_sync_docs"][0]["id"] == "out-of-sync-doc"
            assert (
                result["out_of_sync_docs"][0]["file_mtime"]
                > result["out_of_sync_docs"][0]["last_seen_mtime"]
            )

    def test_analyze_freshness_custom_refresh_interval(self):
        """Test that custom refresh intervals override defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create a file
            doc_path = repo_root / "docs" / "test.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test Document")

            # Create document with custom refresh interval (7 days) and old refresh date (10 days ago)
            old_date = (datetime.now(UTC) - timedelta(days=10)).isoformat()
            doc = KBDocument(
                id="custom-interval-doc",
                title="Custom Interval Document",
                path="docs/test.md",
                type="ssot",  # Default would be 30 days
                owning_subsystem="docs",
                last_refreshed_at=old_date,
                min_refresh_interval_days=7,  # Custom: 7 days
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            # Should be stale because 10 days > 7 days (custom interval)
            assert result["summary"]["stale_count"] == 1
            assert result["stale_docs"][0]["refresh_interval_days"] == 7

    def test_analyze_freshness_uri_paths_skipped(self):
        """Test that URI paths (http/https/file://) are skipped in freshness analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create document with URI path
            doc = KBDocument(
                id="uri-doc",
                title="URI Document",
                path="https://example.com/doc.md",
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            # URI paths should be counted as fresh (skipped)
            assert result["summary"]["fresh_count"] == 1
            assert result["summary"]["stale_count"] == 0
            assert result["summary"]["missing_count"] == 0

    def test_analyze_freshness_no_refresh_date_uses_file_age(self):
        """Test that documents without last_refreshed_at use file age for staleness check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create an old file (beyond refresh interval)
            doc_path = repo_root / "docs" / "old.md"
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Old Document")
            # Set file mtime to 60 days ago
            old_timestamp = (datetime.now(UTC) - timedelta(days=60)).timestamp()
            os.utime(doc_path, (old_timestamp, old_timestamp))

            # Create document without last_refreshed_at
            doc = KBDocument(
                id="no-refresh-date-doc",
                title="No Refresh Date Document",
                path="docs/old.md",
                type="ssot",  # 30 day refresh interval
                owning_subsystem="docs",
                # No last_refreshed_at
            )
            registry.add_document(doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            # Should be stale because file is 60 days old > 30 day interval
            assert result["summary"]["stale_count"] == 1

    def test_analyze_freshness_summary_counts(self):
        """Test that summary counts are accurate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            registry = KBDocumentRegistry()

            # Create various documents
            # Fresh doc
            fresh_path = repo_root / "docs" / "fresh.md"
            fresh_path.parent.mkdir(parents=True, exist_ok=True)
            fresh_path.write_text("# Fresh")
            fresh_doc = KBDocument(
                id="fresh",
                title="Fresh",
                path="docs/fresh.md",
                type="ssot",
                owning_subsystem="docs",
                last_refreshed_at=(datetime.now(UTC) - timedelta(days=5)).isoformat(),
            )
            registry.add_document(fresh_doc)

            # Stale doc
            stale_path = repo_root / "docs" / "stale.md"
            stale_path.parent.mkdir(parents=True, exist_ok=True)
            stale_path.write_text("# Stale")
            stale_doc = KBDocument(
                id="stale",
                title="Stale",
                path="docs/stale.md",
                type="ssot",
                owning_subsystem="docs",
                last_refreshed_at=(datetime.now(UTC) - timedelta(days=60)).isoformat(),
            )
            registry.add_document(stale_doc)

            # Missing doc
            missing_doc = KBDocument(
                id="missing",
                title="Missing",
                path="docs/missing.md",
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(missing_doc)

            # Analyze freshness
            result = analyze_freshness(registry, repo_root=repo_root)

            summary = result["summary"]
            assert summary["total"] == 3
            assert summary["fresh_count"] == 1
            assert summary["stale_count"] == 1
            assert summary["missing_count"] == 1
            assert summary["out_of_sync_count"] == 0
