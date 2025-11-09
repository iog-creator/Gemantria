#!/usr/bin/env python3

from __future__ import annotations

import json, pathlib, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
V1 = ROOT / "tests" / "truth" / "extraction_accuracy.v1.json"
V2 = ROOT / "tests" / "truth" / "extraction_accuracy.v2.json"


def key(c):
    s = f"{c.get('surface', '')}|{c.get('letters', '')}|{c.get('gematria', '')}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    data = json.loads(V1.read_text())
    cases = sorted(data.get("cases", []), key=key)
    assert len(cases) >= 25, "Need ≥25 cases in v1 before promoting to v2"
    out = {
        "version": "v2",
        "source": data.get("source", "fixtures"),
        "schema": "extraction_accuracy.v2",
        "cases": [
            {
                "id": i + 1,
                "surface": c.get("surface"),
                "letters": c.get("letters"),
                "gematria": c.get("gematria"),
                "ref": c.get("ref"),
            }
            for i, c in enumerate(cases)
        ],
    }
    V2.parent.mkdir(parents=True, exist_ok=True)
    V2.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"OK: promoted truth to v2 ({len(out['cases'])} cases) → {V2}")


if __name__ == "__main__":
    main()
