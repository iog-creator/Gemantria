#!/usr/bin/env python3
"""
KB Document Registry Model & Persistence (KB-Reg:M1)

Registry for tracking KB documents (AGENTS.md, SSOT docs, rules, etc.) with
metadata including id/handle, title, path/URI, type, tags, owning subsystem,
and provenance.

SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
CI/Hermetic: Registry is read-only in CI; writes are only allowed in local/dev environments.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Standard registry path (relative to repo root)
REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "share" / "kb_registry.json"


class KBDocument(BaseModel):
    """KB Document Registry Entry.

    Represents a single document in the knowledge base registry.
    """

    id: str = Field(..., description="Unique identifier/handle for the document")
    title: str = Field(..., description="Human-readable title")
    path: str = Field(..., description="File path relative to repo root or absolute URI")
    type: str = Field(
        ...,
        description="Document type (e.g., 'agents_md', 'ssot', 'rule', 'runbook', 'adr')",
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    owning_subsystem: str = Field(
        ...,
        description="Owning subsystem (e.g., 'agentpm', 'docs', 'rules', 'scripts')",
    )
    provenance: dict[str, Any] = Field(
        default_factory=dict,
        description="Provenance metadata (source, last_updated, checksum, etc.)",
    )
    registered_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO timestamp when document was registered",
    )
    # Freshness tracking fields (KB-Reg:M6)
    last_seen_mtime: float | None = Field(
        default=None,
        description="File modification time (Unix timestamp) when last checked",
    )
    last_refreshed_at: str | None = Field(
        default=None,
        description="ISO timestamp when registry entry was last refreshed",
    )
    min_refresh_interval_days: int | None = Field(
        default=None,
        description="Minimum refresh interval in days (per doc type or doc-specific override)",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID is non-empty and suitable as a handle."""
        if not v or not v.strip():
            raise ValueError("ID must be non-empty")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate document type is recognized."""
        valid_types = {
            "agents_md",
            "ssot",
            "rule",
            "runbook",
            "adr",
            "changelog",
            "readme",
            "other",
        }
        if v not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KBDocument:
        """Create from dictionary."""
        return cls(**data)


class KBDocumentRegistry(BaseModel):
    """KB Document Registry Container.

    Holds all registered KB documents with metadata.
    """

    version: str = Field(default="1.0", description="Registry schema version")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO timestamp when registry was generated",
    )
    documents: list[KBDocument] = Field(default_factory=list, description="List of registered documents")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "documents": [doc.to_dict() for doc in self.documents],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KBDocumentRegistry:
        """Create from dictionary."""
        documents = [KBDocument.from_dict(doc) for doc in data.get("documents", [])]
        return cls(
            version=data.get("version", "1.0"),
            generated_at=data.get("generated_at", datetime.now(UTC).isoformat()),
            documents=documents,
        )

    def get_by_id(self, doc_id: str) -> KBDocument | None:
        """Get document by ID."""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def get_by_path(self, path: str) -> KBDocument | None:
        """Get document by path."""
        for doc in self.documents:
            if doc.path == path:
                return doc
        return None

    def add_document(self, document: KBDocument) -> bool:
        """Add document to registry (returns False if ID already exists)."""
        if self.get_by_id(document.id):
            return False
        self.documents.append(document)
        return True

    def remove_document(self, doc_id: str) -> bool:
        """Remove document from registry (returns False if not found)."""
        for i, doc in enumerate(self.documents):
            if doc.id == doc_id:
                self.documents.pop(i)
                return True
        return False


def load_registry(registry_path: Path | None = None) -> KBDocumentRegistry:
    """Load KB registry from JSON file.

    Args:
        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)

    Returns:
        KBDocumentRegistry instance

    Raises:
        FileNotFoundError: If registry file doesn't exist
        ValueError: If registry file is invalid JSON or schema
    """
    if registry_path is None:
        registry_path = REGISTRY_PATH

    if not registry_path.exists():
        # Return empty registry if file doesn't exist (hermetic behavior)
        return KBDocumentRegistry()

    try:
        content = registry_path.read_text()
        data = json.loads(content)
        return KBDocumentRegistry.from_dict(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in registry file: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to load registry: {e}") from e


def save_registry(
    registry: KBDocumentRegistry, registry_path: Path | None = None, allow_ci_write: bool = False
) -> None:
    """Save KB registry to JSON file.

    Args:
        registry: KBDocumentRegistry instance to save
        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)
        allow_ci_write: If True, allow writes in CI (default: False, read-only in CI)

    Raises:
        RuntimeError: If attempting to write in CI without allow_ci_write=True
        OSError: If file write fails
    """
    if registry_path is None:
        registry_path = REGISTRY_PATH

    # CI/Hermetic: Read-only in CI unless explicitly allowed
    if os.getenv("CI") == "true" and not allow_ci_write:
        raise RuntimeError(
            "Registry writes are disabled in CI (read-only). Set allow_ci_write=True to override (not recommended)."
        )

    # Update generated_at timestamp
    registry.generated_at = datetime.now(UTC).isoformat()

    # Ensure directory exists
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON with indentation
    try:
        content = json.dumps(registry.to_dict(), indent=2)
        registry_path.write_text(content + "\n")
    except Exception as e:
        raise OSError(f"Failed to write registry file: {e}") from e


def validate_registry(registry: KBDocumentRegistry, repo_root: Path | None = None) -> dict[str, Any]:
    """Validate registry entries (check file existence, duplicates, etc.).

    Args:
        registry: KBDocumentRegistry instance to validate
        repo_root: Repository root path (defaults to parent of agentpm/)

    Returns:
        Validation result dict with keys:
        - valid: bool
        - errors: list[str]
        - warnings: list[str]
        - stats: dict with counts
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    errors: list[str] = []
    warnings: list[str] = []
    stats = {
        "total": len(registry.documents),
        "valid_paths": 0,
        "missing_paths": 0,
        "duplicate_ids": 0,
        "duplicate_paths": 0,
    }

    # Check for duplicate IDs
    seen_ids: set[str] = set()
    for doc in registry.documents:
        if doc.id in seen_ids:
            errors.append(f"Duplicate ID: {doc.id}")
            stats["duplicate_ids"] += 1
        seen_ids.add(doc.id)

    # Check for duplicate paths
    seen_paths: set[str] = set()
    for doc in registry.documents:
        if doc.path in seen_paths:
            warnings.append(f"Duplicate path: {doc.path} (ID: {doc.id})")
            stats["duplicate_paths"] += 1
        seen_paths.add(doc.path)

    # Check file existence
    for doc in registry.documents:
        # Skip URI paths (assume external)
        if doc.path.startswith(("http://", "https://", "file://")):
            stats["valid_paths"] += 1
            continue

        # Check relative to repo root
        doc_path = repo_root / doc.path
        if doc_path.exists():
            stats["valid_paths"] += 1
        else:
            errors.append(f"Missing file: {doc.path} (ID: {doc.id})")
            stats["missing_paths"] += 1

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }


def query_registry(
    registry: KBDocumentRegistry,
    *,
    type: str | None = None,
    owning_subsystem: str | None = None,
    tags: list[str] | None = None,
) -> list[KBDocument]:
    """Query registry with filters (read-only, for planning agents).

    Args:
        registry: KBDocumentRegistry instance to query
        type: Filter by document type (optional)
        owning_subsystem: Filter by owning subsystem (optional)
        tags: Filter by tags (document must have all specified tags) (optional)

    Returns:
        List of KBDocument instances matching the filters
    """
    results = registry.documents

    # Filter by type
    if type is not None:
        results = [doc for doc in results if doc.type == type]

    # Filter by owning_subsystem
    if owning_subsystem is not None:
        results = [doc for doc in results if doc.owning_subsystem == owning_subsystem]

    # Filter by tags (document must have all specified tags)
    if tags is not None:
        tag_set = set(tags)
        results = [doc for doc in results if tag_set.issubset(set(doc.tags))]

    return results


# Default refresh intervals (days) per document type (KB-Reg:M6)
DEFAULT_REFRESH_INTERVALS: dict[str, int] = {
    "ssot": 30,  # SSOT docs should be refreshed monthly
    "adr": 90,  # ADRs are more stable, quarterly refresh
    "agents_md": 14,  # AGENTS.md files should be kept current, bi-weekly
    "runbook": 60,  # Runbooks are stable but should be checked bimonthly
    "rule": 90,  # Rules are stable, quarterly refresh
    "changelog": 7,  # Changelogs should be updated frequently
    "readme": 30,  # README files monthly
    "other": 60,  # Other docs bimonthly
}


def analyze_freshness(
    registry: KBDocumentRegistry, repo_root: Path | None = None, now: datetime | None = None
) -> dict[str, Any]:
    """Analyze document freshness (stale/missing/out-of-sync) (KB-Reg:M6).

    Args:
        registry: KBDocumentRegistry instance to analyze
        repo_root: Repository root path (defaults to parent of agentpm/)
        now: Current datetime for comparison (defaults to now)

    Returns:
        Dictionary with freshness analysis:
        {
            "stale_docs": list[dict] - docs that haven't been refreshed in too long,
            "missing_docs": list[dict] - docs that don't exist on filesystem,
            "out_of_sync_docs": list[dict] - docs where file mtime > last_seen_mtime,
            "summary": {
                "total": int,
                "stale_count": int,
                "missing_count": int,
                "out_of_sync_count": int,
                "fresh_count": int
            }
        }
    """
    if repo_root is None:
        repo_root = REPO_ROOT
    if now is None:
        now = datetime.now(UTC)

    stale_docs: list[dict[str, Any]] = []
    missing_docs: list[dict[str, Any]] = []
    out_of_sync_docs: list[dict[str, Any]] = []
    fresh_count = 0

    for doc in registry.documents:
        # Skip URI paths (assume external, can't check freshness)
        if doc.path.startswith(("http://", "https://", "file://")):
            fresh_count += 1
            continue

        # Check if file exists
        doc_path = repo_root / doc.path
        if not doc_path.exists():
            missing_docs.append(
                {
                    "id": doc.id,
                    "path": doc.path,
                    "title": doc.title,
                    "type": doc.type,
                }
            )
            continue

        # Get file modification time
        try:
            file_mtime = doc_path.stat().st_mtime
        except OSError:
            # Can't read file stats, skip freshness check
            continue

        # Determine refresh interval (doc-specific override, or type default, or 60 days)
        refresh_interval_days = doc.min_refresh_interval_days
        if refresh_interval_days is None:
            refresh_interval_days = DEFAULT_REFRESH_INTERVALS.get(doc.type, 60)

        # Check if out of sync (file was modified after last_seen_mtime)
        if doc.last_seen_mtime is not None and file_mtime > doc.last_seen_mtime:
            out_of_sync_docs.append(
                {
                    "id": doc.id,
                    "path": doc.path,
                    "title": doc.title,
                    "type": doc.type,
                    "file_mtime": file_mtime,
                    "last_seen_mtime": doc.last_seen_mtime,
                    "age_days": (now.timestamp() - file_mtime) / 86400,
                }
            )
            continue

        # Check if stale (last_refreshed_at is too old or missing)
        is_stale = False
        if doc.last_refreshed_at:
            try:
                last_refreshed = datetime.fromisoformat(doc.last_refreshed_at.replace("Z", "+00:00"))
                if last_refreshed.tzinfo is None:
                    last_refreshed = last_refreshed.replace(tzinfo=UTC)
                age_days = (now - last_refreshed).total_seconds() / 86400
                if age_days > refresh_interval_days:
                    is_stale = True
            except (ValueError, AttributeError):
                # Invalid timestamp, treat as stale
                is_stale = True
        else:
            # Never refreshed, check if file is older than refresh interval
            file_age_days = (now.timestamp() - file_mtime) / 86400
            if file_age_days > refresh_interval_days:
                is_stale = True

        if is_stale:
            stale_docs.append(
                {
                    "id": doc.id,
                    "path": doc.path,
                    "title": doc.title,
                    "type": doc.type,
                    "last_refreshed_at": doc.last_refreshed_at,
                    "refresh_interval_days": refresh_interval_days,
                }
            )
        else:
            fresh_count += 1

    return {
        "stale_docs": stale_docs,
        "missing_docs": missing_docs,
        "out_of_sync_docs": out_of_sync_docs,
        "summary": {
            "total": len(registry.documents),
            "stale_count": len(stale_docs),
            "missing_count": len(missing_docs),
            "out_of_sync_count": len(out_of_sync_docs),
            "fresh_count": fresh_count,
        },
    }
