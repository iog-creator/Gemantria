# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import glob
import hashlib
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "share" / "eval"
JSON_OUT = OUTDIR / "provenance.json"
MD_OUT = OUTDIR / "provenance.md"


def _git(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(["git", *cmd], cwd=ROOT).decode("utf-8").strip()
    except Exception:
        return None


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    print("[eval.provenance] starting")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    manifest = ROOT / "eval" / "manifest.yml"
    thresholds = ROOT / "eval" / "thresholds.yml"
    latest = ROOT / "exports" / "graph_latest.json"
    cand = sorted(glob.glob(str(ROOT / "exports" / "graph_*.json")))
    exports = [pathlib.Path(c) for c in cand]

    repo = {
        "git_head": _git(["rev-parse", "HEAD"]),
        "git_branch": _git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "ts_unix": int(time.time()),
    }

    man_ver = None
    if manifest.exists():
        for line in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("version:"):
                man_ver = line.split(":", 1)[1].strip()
                break

    thr_ver = None
    if thresholds.exists():
        for line in thresholds.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("version:"):
                thr_ver = line.split(":", 1)[1].strip()
                break

    latest_info = None
    if latest.exists():
        latest_info = {
            "path": str(latest.relative_to(ROOT)),
            "size_bytes": latest.stat().st_size,
            "sha256": _sha256(latest),
        }

    total_size = sum(p.stat().st_size for p in exports) if exports else 0
    exports_data = {
        "count": len(exports),
        "total_size_bytes": total_size,
        "latest": latest_info,
    }
    prov = {
        "repo": repo,
        "manifest_version": man_ver,
        "thresholds_version": thr_ver,
        "exports": exports_data,
    }

    JSON_OUT.write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# Gemantria Eval Provenance")
    lines.append("")
    lines.append(f"*git:* `{repo['git_head']}`  •  *branch:* `{repo['git_branch']}`")
    lines.append(f"*manifest_version:* {man_ver}  •  *thresholds_version:* {thr_ver}")
    lines.append(f"*exports:* count={exports_data['count']}  •  total_size_bytes={exports_data['total_size_bytes']}")
    if latest_info:
        lines.append(f"*latest:* `{latest_info['path']}`  •  sha256={latest_info['sha256']}")
    lines.append("")
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[eval.provenance] wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"[eval.provenance] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.provenance] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
