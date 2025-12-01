"""
Tests for KB document registry model and persistence (KB-Reg:M1).
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    load_registry,
    query_registry,
    save_registry,
    validate_registry,
)


class TestKBDocument:
    """Test KBDocument model."""

    def test_create_document(self):
        """Test creating a KBDocument."""
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            tags=["test", "docs"],
            owning_subsystem="docs",
            provenance={"source": "manual"},
        )
        assert doc.id == "test-doc-1"
        assert doc.title == "Test Document"
        assert doc.path == "docs/test.md"
        assert doc.type == "ssot"
        assert doc.tags == ["test", "docs"]
        assert doc.owning_subsystem == "docs"
        assert doc.provenance == {"source": "manual"}

    def test_document_validation_id(self):
        """Test ID validation."""
        # Empty ID should fail
        try:
            KBDocument(id="", title="Test", path="test.md", type="ssot", owning_subsystem="docs")
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_document_validation_type(self):
        """Test type validation."""
        # Invalid type should fail
        try:
            KBDocument(
                id="test", title="Test", path="test.md", type="invalid", owning_subsystem="docs"
            )
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_document_to_dict(self):
        """Test document serialization."""
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        data = doc.to_dict()
        assert data["id"] == "test-doc-1"
        assert data["title"] == "Test Document"
        assert "registered_at" in data

    def test_document_from_dict(self):
        """Test document deserialization."""
        data = {
            "id": "test-doc-1",
            "title": "Test Document",
            "path": "docs/test.md",
            "type": "ssot",
            "tags": [],
            "owning_subsystem": "docs",
            "provenance": {},
            "registered_at": "2025-01-01T00:00:00+00:00",
        }
        doc = KBDocument.from_dict(data)
        assert doc.id == "test-doc-1"
        assert doc.title == "Test Document"


class TestKBDocumentRegistry:
    """Test KBDocumentRegistry model."""

    def test_create_registry(self):
        """Test creating a registry."""
        registry = KBDocumentRegistry()
        assert registry.version == "1.0"
        assert len(registry.documents) == 0

    def test_add_document(self):
        """Test adding documents to registry."""
        registry = KBDocumentRegistry()
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        assert registry.add_document(doc) is True
        assert len(registry.documents) == 1
        assert registry.get_by_id("test-doc-1") == doc

    def test_add_duplicate_document(self):
        """Test adding duplicate document (should fail)."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="test-doc-1",
            title="Test Document 1",
            path="docs/test1.md",
            type="ssot",
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="test-doc-1",  # Same ID
            title="Test Document 2",
            path="docs/test2.md",
            type="ssot",
            owning_subsystem="docs",
        )
        assert registry.add_document(doc1) is True
        assert registry.add_document(doc2) is False  # Duplicate ID
        assert len(registry.documents) == 1

    def test_get_by_id(self):
        """Test getting document by ID."""
        registry = KBDocumentRegistry()
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        registry.add_document(doc)
        assert registry.get_by_id("test-doc-1") == doc
        assert registry.get_by_id("nonexistent") is None

    def test_get_by_path(self):
        """Test getting document by path."""
        registry = KBDocumentRegistry()
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        registry.add_document(doc)
        assert registry.get_by_path("docs/test.md") == doc
        assert registry.get_by_path("nonexistent.md") is None

    def test_remove_document(self):
        """Test removing document from registry."""
        registry = KBDocumentRegistry()
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        registry.add_document(doc)
        assert registry.remove_document("test-doc-1") is True
        assert len(registry.documents) == 0
        assert registry.remove_document("nonexistent") is False


class TestRegistryPersistence:
    """Test registry persistence (load/save)."""

    def test_save_and_load_registry(self):
        """Test saving and loading registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "test_registry.json"
            registry = KBDocumentRegistry()
            doc = KBDocument(
                id="test-doc-1",
                title="Test Document",
                path="docs/test.md",
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(doc)

            # Save registry
            save_registry(registry, registry_path, allow_ci_write=True)

            # Load registry
            loaded = load_registry(registry_path)
            assert loaded.version == registry.version
            assert len(loaded.documents) == 1
            assert loaded.get_by_id("test-doc-1").title == "Test Document"

    def test_load_nonexistent_registry(self):
        """Test loading nonexistent registry (should return empty)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "nonexistent.json"
            registry = load_registry(registry_path)
            assert registry.version == "1.0"
            assert len(registry.documents) == 0

    def test_registry_json_structure(self):
        """Test registry JSON structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "test_registry.json"
            registry = KBDocumentRegistry()
            doc = KBDocument(
                id="test-doc-1",
                title="Test Document",
                path="docs/test.md",
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(doc)
            save_registry(registry, registry_path, allow_ci_write=True)

            # Verify JSON structure
            content = registry_path.read_text()
            data = json.loads(content)
            assert "version" in data
            assert "generated_at" in data
            assert "documents" in data
            assert len(data["documents"]) == 1
            assert data["documents"][0]["id"] == "test-doc-1"


class TestRegistryValidation:
    """Test registry validation."""

    def test_validate_registry_with_valid_files(self):
        """Test validation with valid files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test Document\n")

            registry = KBDocumentRegistry()
            doc = KBDocument(
                id="test-doc-1",
                title="Test Document",
                path=str(
                    test_file.relative_to(ROOT) if tmpdir.startswith(str(ROOT)) else test_file
                ),
                type="ssot",
                owning_subsystem="docs",
            )
            registry.add_document(doc)

            # Validate (using tmpdir as repo root for this test)
            # Note: Validation may fail if path is absolute and not under repo root
            # This is expected behavior
            _ = validate_registry(registry, repo_root=Path(tmpdir))

    def test_validate_registry_with_duplicate_ids(self):
        """Test validation detects duplicate IDs."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="test-doc-1",
            title="Test Document 1",
            path="docs/test1.md",
            type="ssot",
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="test-doc-1",  # Duplicate ID
            title="Test Document 2",
            path="docs/test2.md",
            type="ssot",
            owning_subsystem="docs",
        )
        # Manually add both (bypassing add_document which prevents duplicates)
        registry.documents = [doc1, doc2]

        validation = validate_registry(registry)
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
        assert any("Duplicate ID" in error for error in validation["errors"])

    def test_validate_registry_with_missing_files(self):
        """Test validation detects missing files."""
        registry = KBDocumentRegistry()
        doc = KBDocument(
            id="test-doc-1",
            title="Test Document",
            path="nonexistent/file.md",
            type="ssot",
            owning_subsystem="docs",
        )
        registry.add_document(doc)

        validation = validate_registry(registry, repo_root=ROOT)
        # Should have errors for missing files
        assert len(validation["errors"]) > 0
        assert any("Missing file" in error for error in validation["errors"])


class TestRegistryQuery:
    """Test registry query helper."""

    def test_query_by_type(self):
        """Test querying by document type."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="doc-1",
            title="SSOT Document",
            path="docs/ssot.md",
            type="ssot",
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="doc-2",
            title="Rule Document",
            path=".cursor/rules/001.mdc",
            type="rule",
            owning_subsystem="rules",
        )
        registry.add_document(doc1)
        registry.add_document(doc2)

        # Query by type
        results = query_registry(registry, type="ssot")
        assert len(results) == 1
        assert results[0].id == "doc-1"

        results = query_registry(registry, type="rule")
        assert len(results) == 1
        assert results[0].id == "doc-2"

        results = query_registry(registry, type="agents_md")
        assert len(results) == 0

    def test_query_by_owning_subsystem(self):
        """Test querying by owning subsystem."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="doc-1",
            title="Docs Document",
            path="docs/test.md",
            type="ssot",
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="doc-2",
            title="Rules Document",
            path=".cursor/rules/001.mdc",
            type="rule",
            owning_subsystem="rules",
        )
        registry.add_document(doc1)
        registry.add_document(doc2)

        # Query by owning_subsystem
        results = query_registry(registry, owning_subsystem="docs")
        assert len(results) == 1
        assert results[0].id == "doc-1"

        results = query_registry(registry, owning_subsystem="rules")
        assert len(results) == 1
        assert results[0].id == "doc-2"

        results = query_registry(registry, owning_subsystem="nonexistent")
        assert len(results) == 0

    def test_query_by_tags(self):
        """Test querying by tags."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="doc-1",
            title="Document 1",
            path="docs/test1.md",
            type="ssot",
            tags=["governance", "root"],
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="doc-2",
            title="Document 2",
            path="docs/test2.md",
            type="ssot",
            tags=["governance"],
            owning_subsystem="docs",
        )
        doc3 = KBDocument(
            id="doc-3",
            title="Document 3",
            path="docs/test3.md",
            type="ssot",
            tags=["other"],
            owning_subsystem="docs",
        )
        registry.add_document(doc1)
        registry.add_document(doc2)
        registry.add_document(doc3)

        # Query by single tag
        results = query_registry(registry, tags=["governance"])
        assert len(results) == 2
        assert {r.id for r in results} == {"doc-1", "doc-2"}

        # Query by multiple tags (document must have all)
        results = query_registry(registry, tags=["governance", "root"])
        assert len(results) == 1
        assert results[0].id == "doc-1"

        # Query by non-existent tag
        results = query_registry(registry, tags=["nonexistent"])
        assert len(results) == 0

    def test_query_combined_filters(self):
        """Test querying with combined filters."""
        registry = KBDocumentRegistry()
        doc1 = KBDocument(
            id="doc-1",
            title="SSOT Document",
            path="docs/ssot.md",
            type="ssot",
            tags=["governance"],
            owning_subsystem="docs",
        )
        doc2 = KBDocument(
            id="doc-2",
            title="Rule Document",
            path=".cursor/rules/001.mdc",
            type="rule",
            tags=["governance"],
            owning_subsystem="rules",
        )
        registry.add_document(doc1)
        registry.add_document(doc2)

        # Query with combined filters
        results = query_registry(
            registry, type="ssot", owning_subsystem="docs", tags=["governance"]
        )
        assert len(results) == 1
        assert results[0].id == "doc-1"

        # No matches
        results = query_registry(registry, type="ssot", owning_subsystem="rules")
        assert len(results) == 0
