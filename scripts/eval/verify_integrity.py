#!/usr/bin/env python3
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
MANIFEST = EVAL / "release_manifest.json"
REPORT = EVAL / "integrity_report.txt"


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print("[integrity] manifest missing:", MANIFEST.relative_to(ROOT))
        return 2
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = data.get("artifacts", [])
    bad = 0
    lines = []
    for a in artifacts:
        path = a.get("path")
        exp_sha = a.get("sha256")
        exp_sz = a.get("size")
        if not path or path in ("release_manifest.json", "integrity_report.txt"):
            continue
        fp = EVAL / path
        if not fp.exists():
            lines.append(f"MISSING\t{path}")
            bad += 1
            continue
        try:
            sz = fp.stat().st_size
            sh = sha256(fp)
        except Exception as e:
            lines.append(f"ERROR\t{path}\t{e}")
            bad += 1
            continue
        ok_sz = (exp_sz is None) or (sz == exp_sz)
        ok_sh = (exp_sha is None) or (sh == exp_sha)
        if ok_sz and ok_sh:
            lines.append(f"OK\t{path}")
        else:
            lines.append(
                f"MISMATCH\t{path}\tgot_size={sz}\texp_size={exp_sz}\tgot_sha256={sh}\texp_sha256={exp_sha}"
            )
            bad += 1
    header = f"[integrity] checked={len(artifacts)} mismatches={bad}"
    print(header)
    REPORT.write_text(header + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
