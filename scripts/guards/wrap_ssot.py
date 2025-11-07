#!/usr/bin/env python3

import json, sys, datetime, pathlib

from typing import Any, Dict


def iso_now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def write_json(p: str, obj: Dict[str, Any]) -> None:
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(p: str) -> Dict[str, Any]:
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def wrap_ai_nouns(src: str, dst: str, book: str):
    data = load_json(src)
    out = {
        "schema": "gematria/ai-nouns.v1",
        "book": book,
        "generated_at": iso_now(),
        "nodes": data.get("nodes") or data.get("items") or [],
    }
    write_json(dst, out)


def wrap_graph(src: str, dst: str, book: str):
    data = load_json(src)
    data.setdefault("schema", "gematria/graph.v1")
    data.setdefault("book", book)
    data.setdefault("generated_at", iso_now())
    write_json(dst, data)


def main():
    """
    usage:
      wrap_ssot.py ai-nouns <src> <dst> <book>
      wrap_ssot.py graph    <src> <dst> <book>
    """
    kind = sys.argv[1]
    if kind == "ai-nouns":
        _, _, src, dst, book = sys.argv
        wrap_ai_nouns(src, dst, book)
    elif kind == "graph":
        _, _, src, dst, book = sys.argv
        wrap_graph(src, dst, book)
    else:
        print("unknown kind", kind)
        sys.exit(2)


if __name__ == "__main__":
    main()
