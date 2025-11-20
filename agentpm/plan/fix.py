#!/usr/bin/env python3
"""
KB Document Fix Actions (AgentPM-Next:M2)

Consumes worklist from build_kb_doc_worklist() and produces/executes doc fixes.
Default dry-run mode; --apply requires explicit opt-in.
"""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from agentpm.kb.registry import (
    KBDocumentRegistry,
    load_registry,
    save_registry,
    REGISTRY_PATH,
    REPO_ROOT,
)

# Approved paths for writes (safety check)
APPROVED_PATHS = [
    "docs/",
    "AGENTS.md",
    "rules/docs/",
]


class FixAction:
    """Represents a single fix action."""

    def __init__(
        self,
        id: str,
        subsystem: str,
        severity: str,
        action_type: str,
        description: str,
        doc_path: str | None = None,
        suggested_edits: str | None = None,
        notes: list[str] | None = None,
    ):
        self.id = id
        self.subsystem = subsystem
        self.severity = severity
        self.action_type = action_type
        self.description = description
        self.doc_path = doc_path
        self.suggested_edits = suggested_edits
        self.notes = notes or []
        self.applied = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "subsystem": self.subsystem,
            "severity": self.severity,
            "doc_path": self.doc_path,
            "action_type": self.action_type,
            "description": self.description,
            "suggested_edits": self.suggested_edits,
            "applied": self.applied,
            "notes": self.notes,
        }


def _is_approved_path(path: str) -> bool:
    """Check if path is in approved write locations."""
    path_str = str(path)
    # Check if path starts with any approved prefix
    for approved in APPROVED_PATHS:
        if path_str.startswith(approved) or path_str == approved:
            return True
    # Check if it's an AGENTS.md file anywhere
    if path_str.endswith("AGENTS.md"):
        return True
    return False


def build_fix_actions(
    worklist: dict[str, Any],
    filters: dict[str, Any] | None = None,
    registry_path: Path | None = None,
) -> list[FixAction]:
    """Convert worklist items to fix action objects.

    Args:
        worklist: Worklist from build_kb_doc_worklist()
        filters: Optional filters dict with keys: subsystem, min_severity, limit
        registry_path: Optional path to registry file (for loading doc details)

    Returns:
        List of FixAction objects
    """
    if filters is None:
        filters = {}

    actions: list[FixAction] = []
    items = worklist.get("items", [])

    # Apply filters
    subsystem_filter = filters.get("subsystem")
    min_severity = filters.get("min_severity")
    limit = filters.get("limit", 50)

    # Severity order for min_severity filter
    severity_order = {
        "missing": 0,
        "stale": 1,
        "out_of_sync": 2,
        "low_coverage": 3,
        "info": 4,
    }

    filtered_items = []
    for item in items:
        # Filter by subsystem
        if subsystem_filter and item.get("subsystem") != subsystem_filter:
            continue

        # Filter by min_severity
        if min_severity:
            item_severity = item.get("severity", "info")
            min_severity_level = severity_order.get(min_severity, 99)
            item_severity_level = severity_order.get(item_severity, 99)
            if item_severity_level > min_severity_level:
                continue

        filtered_items.append(item)

    # Apply limit
    filtered_items = filtered_items[:limit]

    # Load registry for doc details if needed
    registry: KBDocumentRegistry | None = None
    if registry_path or any(item.get("severity") in ["missing", "stale", "out_of_sync"] for item in filtered_items):
        try:
            actual_registry_path = registry_path if registry_path else REGISTRY_PATH
            registry = load_registry(actual_registry_path)
        except Exception:
            # Can't load registry, continue without it
            pass

    # Convert items to actions
    for item in filtered_items:
        item_id = item.get("id", "unknown")
        severity = item.get("severity", "info")
        subsystem = item.get("subsystem", "unknown")

        # Get doc_path from registry
        doc_path = None
        if registry:
            doc = registry.get_by_id(item_id)
            if doc:
                doc_path = doc.path

        # Determine action type based on severity
        if severity == "missing":
            action_type = "create_stub_doc"
            description = item.get("suggested_action", f"Create stub document for {item.get('title', item_id)}")
        elif severity == "stale":
            action_type = "mark_stale_and_suggest_update"
            description = item.get(
                "suggested_action", f"Mark stale and suggest update for {item.get('title', item_id)}"
            )
        elif severity == "out_of_sync":
            action_type = "sync_metadata"
            description = item.get("suggested_action", f"Sync metadata for {item.get('title', item_id)}")
        elif severity == "low_coverage":
            action_type = "propose_new_docs"
            description = item.get("suggested_action", f"Propose new docs for {subsystem} subsystem")
        else:
            action_type = "no_op"
            description = item.get("suggested_action", f"Advisory note for {item.get('title', item_id)}")

        action = FixAction(
            id=item_id,
            subsystem=subsystem,
            severity=severity,
            action_type=action_type,
            description=description,
            doc_path=doc_path,
        )
        actions.append(action)

    return actions


def create_stub_doc(doc_path: Path, metadata: dict[str, Any]) -> None:
    """Create a minimal stub document file.

    Args:
        doc_path: Path where stub should be created
        metadata: Document metadata (title, owning_subsystem, tags, etc.)
    """
    # Ensure parent directory exists
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    # Build front-matter
    title = metadata.get("title", doc_path.stem)
    subsystem = metadata.get("owning_subsystem", "unknown")
    tags = metadata.get("tags", [])
    doc_type = metadata.get("type", "other")

    # Create minimal stub content
    content = f"""# {title}

**Status:** Stub (created by AgentPM-Next:M2 doc-fix)

**Subsystem:** {subsystem}
**Type:** {doc_type}
**Tags:** {", ".join(tags) if tags else "none"}

---

TODO: Flesh out this document.

This stub was automatically created by `pmagent plan kb fix` to address missing documentation.
Please add proper content following the subsystem's documentation standards.

"""

    doc_path.write_text(content)


def mark_stale_note(doc_path: Path, note: str | None = None) -> None:
    """Append a staleness marker to a document.

    Args:
        doc_path: Path to document
        note: Optional note text (if None, uses template)
    """
    if not doc_path.exists():
        return

    # Read existing content
    existing = doc_path.read_text()

    # Check if staleness note already exists (idempotence)
    if "<!-- STALENESS NOTE" in existing:
        # Update existing note
        lines = existing.split("\n")
        new_lines = []
        in_stale_note = False
        for line in lines:
            if "<!-- STALENESS NOTE" in line:
                in_stale_note = True
                # Skip until end marker
                continue
            if in_stale_note and "-->" in line:
                in_stale_note = False
                # Add updated note
                timestamp = datetime.now(UTC).isoformat()
                note_text = note or "Document may be stale per KB freshness rules. Please review and update if needed."
                new_lines.append(f"<!-- STALENESS NOTE (updated {timestamp}) -->")
                new_lines.append(f"**Note:** {note_text}")
                new_lines.append("<!-- END STALENESS NOTE -->")
                continue
            if not in_stale_note:
                new_lines.append(line)
        doc_path.write_text("\n".join(new_lines))
    else:
        # Append new note
        timestamp = datetime.now(UTC).isoformat()
        note_text = note or "Document may be stale per KB freshness rules. Please review and update if needed."
        stale_section = f"""

---

<!-- STALENESS NOTE (added {timestamp}) -->
**Note:** {note_text}
<!-- END STALENESS NOTE -->
"""
        doc_path.write_text(existing + stale_section)


def sync_metadata(registry: KBDocumentRegistry, doc_id: str, repo_root: Path | None = None) -> None:
    """Fix registry/FS metadata drift.

    Args:
        registry: KBDocumentRegistry instance
        doc_id: Document ID to sync
        repo_root: Repository root path
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    doc = registry.get_by_id(doc_id)
    if not doc:
        return

    # Check if file exists and update last_seen_mtime
    doc_path = repo_root / doc.path
    if doc_path.exists():
        mtime = doc_path.stat().st_mtime
        doc.last_seen_mtime = mtime
        # Update last_refreshed_at if file was modified
        if doc.last_seen_mtime != mtime:
            doc.last_refreshed_at = datetime.now(UTC).isoformat()


def apply_actions(
    actions: list[FixAction],
    dry_run: bool = True,
    repo_root: Path | None = None,
    registry_path: Path | None = None,
    allow_stubs_for_low_coverage: bool = False,
) -> dict[str, Any]:
    """Execute fix actions (or simulate in dry-run).

    Args:
        actions: List of FixAction objects to execute
        dry_run: If True, simulate actions without writing (default: True)
        repo_root: Repository root path
        registry_path: Optional path to registry file (for syncing metadata)
        allow_stubs_for_low_coverage: If True, allow creating stubs for low_coverage items

    Returns:
        Dictionary with execution results:
        {
            "mode": "dry-run" | "apply",
            "actions_applied": int,
            "actions_skipped": int,
            "files_created": list[str],
            "files_modified": list[str],
            "errors": list[str]
        }
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    result: dict[str, Any] = {
        "mode": "dry-run" if dry_run else "apply",
        "actions_applied": 0,
        "actions_skipped": 0,
        "files_created": [],
        "files_modified": [],
        "errors": [],
    }

    registry: KBDocumentRegistry | None = None
    if registry_path or any(action.action_type == "sync_metadata" for action in actions):
        try:
            actual_registry_path = registry_path if registry_path else REGISTRY_PATH
            registry = load_registry(actual_registry_path)
        except Exception as e:
            result["errors"].append(f"Failed to load registry: {e}")

    for action in actions:
        try:
            if action.action_type == "no_op":
                result["actions_skipped"] += 1
                continue

            if action.action_type == "propose_new_docs" and not allow_stubs_for_low_coverage:
                result["actions_skipped"] += 1
                continue

            if not action.doc_path:
                result["actions_skipped"] += 1
                action.notes.append("No doc_path available")
                continue

            doc_path = repo_root / action.doc_path

            # Safety check: only write to approved paths
            if not _is_approved_path(action.doc_path):
                result["actions_skipped"] += 1
                action.notes.append(f"Path not in approved write locations: {action.doc_path}")
                result["errors"].append(f"Skipped {action.id}: path not approved")
                continue

            if dry_run:
                # Simulate action
                if action.action_type == "create_stub_doc":
                    result["files_created"].append(str(action.doc_path))
                elif action.action_type in ["mark_stale_and_suggest_update", "sync_metadata"]:
                    if doc_path.exists():
                        result["files_modified"].append(str(action.doc_path))
                result["actions_applied"] += 1
            else:
                # Execute action
                if action.action_type == "create_stub_doc":
                    if not doc_path.exists():
                        # Get metadata from registry if available
                        metadata: dict[str, Any] = {"title": action.description, "owning_subsystem": action.subsystem}
                        if registry:
                            doc = registry.get_by_id(action.id)
                            if doc:
                                metadata = {
                                    "title": doc.title,
                                    "owning_subsystem": doc.owning_subsystem,
                                    "tags": doc.tags,
                                    "type": doc.type,
                                }
                        create_stub_doc(doc_path, metadata)
                        result["files_created"].append(str(action.doc_path))
                        action.applied = True
                        result["actions_applied"] += 1
                    else:
                        result["actions_skipped"] += 1
                        action.notes.append("File already exists")

                elif action.action_type == "mark_stale_and_suggest_update":
                    if doc_path.exists():
                        mark_stale_note(doc_path, action.suggested_edits)
                        result["files_modified"].append(str(action.doc_path))
                        action.applied = True
                        result["actions_applied"] += 1
                    else:
                        result["actions_skipped"] += 1
                        action.notes.append("File does not exist")

                elif action.action_type == "sync_metadata":
                    if registry and action.id:
                        sync_metadata(registry, action.id, repo_root)
                        # Save registry if modified
                        try:
                            save_registry(registry, registry_path, allow_ci_write=False)
                            action.applied = True
                            result["actions_applied"] += 1
                        except Exception as e:
                            result["errors"].append(f"Failed to save registry: {e}")
                            action.notes.append(f"Registry save failed: {e}")

        except Exception as e:
            result["errors"].append(f"Error processing {action.id}: {e}")
            action.notes.append(f"Error: {e}")

    return result
