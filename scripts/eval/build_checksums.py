# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import glob
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "share" / "eval" / "checksums.csv"


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    print("[eval.checksums] starting")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(glob.glob(str(ROOT / "exports" / "graph_*.json")))
    lines = ["sha256,bytes,file"]
    for f in files:
        p = pathlib.Path(f)
        lines.append(f"{_sha256(p)},{p.stat().st_size},exports/{p.name}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.checksums] wrote {OUT.relative_to(ROOT)}")
    print("[eval.checksums] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
