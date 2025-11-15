from pathlib import Path
import json

from src.utils.kb_client import KBDoc, load_kb_docs, knowledge_panel_context


def _write_kb(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "kb_docs.head.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_load_kb_docs_happy_path(tmp_path):
    path = _write_kb(
        tmp_path,
        {
            "ok": True,
            "db_off": False,
            "docs": [
                {
                    "id": "1",
                    "title": "Getting Started",
                    "section": "Intro",
                    "slug": "getting-started",
                    "tags": ["start", "intro"],
                    "preview": "How to begin.",
                }
            ],
        },
    )
    docs = load_kb_docs(str(path))
    assert len(docs) == 1
    doc = docs[0]
    assert isinstance(doc, KBDoc)
    assert doc.title == "Getting Started"
    assert doc.section == "Intro"
    assert "start" in doc.tags


def test_load_kb_docs_db_off_returns_empty(tmp_path):
    path = _write_kb(
        tmp_path,
        {
            "ok": False,
            "db_off": True,
            "docs": [],
        },
    )
    docs = load_kb_docs(str(path))
    assert docs == []


def test_load_kb_docs_malformed_json_returns_empty(tmp_path):
    p = tmp_path / "kb_docs.head.json"
    p.write_text("{not-json}", encoding="utf-8")
    docs = load_kb_docs(str(p))
    assert docs == []


def test_load_kb_docs_ignores_invalid_docs(tmp_path):
    path = _write_kb(
        tmp_path,
        {
            "ok": True,
            "db_off": False,
            "docs": [
                {"id": "1", "title": "Has slug", "slug": "ok"},
                {"title": "Missing id", "slug": "bad"},
            ],
        },
    )
    docs = load_kb_docs(str(path))
    assert len(docs) == 1
    assert docs[0].id == "1"


def test_knowledge_panel_context_keys(tmp_path):
    path = _write_kb(
        tmp_path,
        {
            "ok": True,
            "db_off": False,
            "docs": [
                {
                    "id": "1",
                    "title": "Doc",
                    "section": None,
                    "slug": "doc",
                    "tags": [],
                    "preview": "",
                }
            ],
        },
    )
    ctx = knowledge_panel_context(str(path))
    assert "kb_docs" in ctx
    assert "kb_has_docs" in ctx
    assert ctx["kb_has_docs"] is True
    assert len(ctx["kb_docs"]) == 1
