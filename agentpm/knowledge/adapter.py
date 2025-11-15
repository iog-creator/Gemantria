"""
Knowledge Base Widget adapter for downstream apps (StoryMaker, BibleScholar).

Transforms the canonical `kb_docs.head.json` export into a simple, typed interface
for downstream apps. Hermetic (file-only, no DB calls) and fail-closed (offline-safe
defaults when file is missing or invalid).

See `docs/SSOT/PHASE_6_PLAN.md` (6C) for the KB export schema.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, TypedDict

KB_DOCS_PATH = Path("share/atlas/control_plane/kb_docs.head.json")


class KBDocWidgetProps(TypedDict):
    """Widget props for a single KB document (read-only, file-based)."""

    id: str
    title: str
    section: str
    slug: str
    tags: List[str]
    preview: str
    created_at: str


class KBWidgetProps(TypedDict):
    """Widget props matching KB contract for downstream apps."""

    docs: List[KBDocWidgetProps]
    db_off: bool
    ok: bool
    error: str | None
    generated_at: str
    source: Dict[str, str]


@dataclass
class RawKBDoc:
    """Raw KB document data parsed from JSON file."""

    id: str
    title: str
    section: str
    slug: str
    tags: list[str]
    preview: str
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawKBDoc:
        """Parse raw KB doc from dict with safe defaults."""
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            section=str(data.get("section", "general")),
            slug=str(data.get("slug", "")),
            tags=list(data.get("tags", [])) if isinstance(data.get("tags"), list) else [],
            preview=str(data.get("preview", "")),
            created_at=str(data.get("created_at", "1970-01-01T00:00:00Z")),
        )


@dataclass
class RawKBExport:
    """Raw KB export data parsed from JSON file."""

    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    docs: list[RawKBDoc]
    db_off: bool
    error: str | None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawKBExport:
        """Parse raw KB export from dict with safe defaults."""
        docs_list = data.get("docs", [])
        if not isinstance(docs_list, list):
            docs_list = []

        parsed_docs = []
        for doc_data in docs_list:
            if isinstance(doc_data, dict):
                parsed_docs.append(RawKBDoc.from_dict(doc_data))

        return cls(
            schema=str(data.get("schema", "knowledge")),
            generated_at=str(data.get("generated_at", "1970-01-01T00:00:00Z")),
            ok=bool(data.get("ok", False)),
            connection_ok=bool(data.get("connection_ok", False)),
            docs=parsed_docs,
            db_off=bool(data.get("db_off", True)),
            error=_to_optional_str(data.get("error")),
        )


# Offline-safe default widget props
OFFLINE_SAFE_DEFAULT: KBWidgetProps = {
    "docs": [],
    "db_off": True,
    "ok": False,
    "error": "KB export file unavailable (offline-safe mode)",
    "generated_at": "1970-01-01T00:00:00Z",
    "source": {"path": str(KB_DOCS_PATH)},
}


def _to_optional_str(value: Any) -> str | None:
    """Convert value to str or None."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return str(value)


def load_kb_docs_widget_props() -> KBWidgetProps:
    """
    Load KB documents widget props from kb_docs.head.json.

    Returns widget props matching the KB contract for downstream apps.
    Hermetic (file-only, no DB calls) and fail-closed (offline-safe defaults).

    Returns:
        KBWidgetProps: Widget props with docs list, db_off status, and metadata.
    """
    # Check if file exists
    if not KB_DOCS_PATH.exists():
        return OFFLINE_SAFE_DEFAULT

    # Try to load and parse JSON
    try:
        content = KB_DOCS_PATH.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, json.JSONDecodeError) as exc:
        # File read or JSON parse error - return offline-safe default
        return {
            "docs": [],
            "db_off": True,
            "ok": False,
            "error": f"Failed to load KB export: {exc!s}",
            "generated_at": "1970-01-01T00:00:00Z",
            "source": {"path": str(KB_DOCS_PATH)},
        }

    # Parse raw export
    try:
        raw_export = RawKBExport.from_dict(data)
    except Exception as exc:  # noqa: BLE001
        # Parse error - return offline-safe default
        return {
            "docs": [],
            "db_off": True,
            "ok": False,
            "error": f"Failed to parse KB export: {exc!s}",
            "generated_at": "1970-01-01T00:00:00Z",
            "source": {"path": str(KB_DOCS_PATH)},
        }

    # Convert raw docs to widget props
    docs_props: List[KBDocWidgetProps] = []
    for raw_doc in raw_export.docs:
        docs_props.append(
            {
                "id": raw_doc.id,
                "title": raw_doc.title,
                "section": raw_doc.section,
                "slug": raw_doc.slug,
                "tags": raw_doc.tags,
                "preview": raw_doc.preview,
                "created_at": raw_doc.created_at,
            }
        )

    # Return widget props
    return {
        "docs": docs_props,
        "db_off": raw_export.db_off,
        "ok": raw_export.ok,
        "error": raw_export.error,
        "generated_at": raw_export.generated_at,
        "source": {"path": str(KB_DOCS_PATH)},
    }
