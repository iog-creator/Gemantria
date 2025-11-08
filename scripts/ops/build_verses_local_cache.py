from __future__ import annotations
import json
import pathlib

SRC = pathlib.Path("ui/derived/xrefs_index.v1.json")
DST = pathlib.Path("ui/out/verses.local.json")
SAMPLE = {
    "Genesis:1:1": "In the beginning God created the heaven and the earth.",
    "Romans:1:20": "For the invisible things of him from the creation of the world are clearly seen...",
}


def main() -> int:
    if not SRC.exists():
        DST.write_text(json.dumps(SAMPLE, ensure_ascii=False, indent=2))
        print(f"Wrote {DST} (sample only)")
        return 0
    data = json.loads(SRC.read_text())
    out = dict(SAMPLE)
    for n in data.get("nodes", []):
        for xr in n.get("xrefs") or []:
            key = f"{xr['book']}:{xr['chapter']}:{xr['verse']}"
            out.setdefault(key, "")  # placeholder if unknown
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {DST} with {len(out)} verses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
