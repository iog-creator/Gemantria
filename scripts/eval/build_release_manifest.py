#!/usr/bin/env python3
import csv, hashlib, json, os, pathlib, time
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUTJ = EVAL / "release_manifest.json"

def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    print("[eval.release_manifest] starting")
    artifacts: List[Dict] = []
    for base in [
        EVAL,
        EVAL / "badges",
        EVAL / "bundles",
    ]:
        if not base.exists():
            continue
        for dirpath, _, filenames in os.walk(base):
            for fn in filenames:
                p = pathlib.Path(dirpath) / fn
                rel = p.relative_to(EVAL)
                try:
                    size = p.stat().st_size
                    sha = _sha256(p)
                except Exception:
                    size = None; sha = None
                artifacts.append({"path": str(rel), "size": size, "sha256": sha})

    OUTJ.write_text(json.dumps({
        "generated_at": int(time.time()),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[eval.release_manifest] wrote {OUTJ.relative_to(ROOT)}")
    print("[eval.release_manifest] OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
