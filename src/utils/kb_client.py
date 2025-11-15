"""
Knowledge Slice client for BibleScholar.

Consumes kb_docs.head.json exported by Gemantria (see KB_WIDGETS.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List
import json
import os


@dataclass
class KBDoc:
    id: str
    title: str
    section: str | None
    slug: str
    tags: List[str]
    preview: str


DEFAULT_KB_EXPORT_PATH_ENV = "KB_DOCS_EXPORT_PATH"
# Default to Gemantria export location, fallback to static/exports for BibleScholar
DEFAULT_KB_EXPORT_RELATIVE = "share/atlas/control_plane/kb_docs.head.json"


def _resolve_export_path(path: str | None = None) -> Path:
    if path:
        return Path(path)
    env = os.getenv(DEFAULT_KB_EXPORT_PATH_ENV)
    if env:
        return Path(env)
    return Path(DEFAULT_KB_EXPORT_RELATIVE)


def _safe_get_docs(payload: Any) -> Iterable[dict]:
    if not isinstance(payload, dict):
        return []
    docs = payload.get("docs")
    if not isinstance(docs, list):
        return []
    return [d for d in docs if isinstance(d, dict)]


def _parse_doc(raw: dict) -> KBDoc | None:
    try:
        doc_id = str(raw.get("id") or "")
        title = (raw.get("title") or "").strip()
        slug = (raw.get("slug") or "").strip()
        if not doc_id or not title or not slug:
            return None

        section = raw.get("section")
        if section is not None:
            section = str(section).strip() or None

        tags_raw = raw.get("tags") or []
        tags: List[str] = []
        if isinstance(tags_raw, list):
            for t in tags_raw:
                if isinstance(t, str):
                    t = t.strip()
                    if t:
                        tags.append(t)

        preview = (raw.get("preview") or "").strip()
        if not preview:
            preview = ""

        return KBDoc(
            id=doc_id,
            title=title,
            section=section,
            slug=slug,
            tags=tags,
            preview=preview,
        )
    except Exception:
        return None


def load_kb_docs(path: str | None = None) -> List[KBDoc]:
    """
    Load KB docs from kb_docs.head.json.

    Offline-safe:
    - Missing file / unreadable JSON -> []
    - db_off: true or ok: false -> []
    """
    export_path = _resolve_export_path(path)
    if not export_path.exists():
        return []

    try:
        data = json.loads(export_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(data, dict):
        if data.get("db_off") is True or data.get("ok") is False:
            return []

    docs: List[KBDoc] = []
    for raw in _safe_get_docs(data):
        doc = _parse_doc(raw)
        if doc is not None:
            docs.append(doc)
    return docs


def knowledge_panel_context(path: str | None = None) -> dict:
    """
    Jinja-friendly context for the Knowledge panel.
    """
    docs = load_kb_docs(path)
    return {
        "kb_docs": docs,
        "kb_has_docs": bool(docs),
    }
