# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import pathlib
import subprocess
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "share" / "eval" / "snapshot"
MANIFEST = ROOT / "eval" / "manifest.yml"
THRESHOLDS = ROOT / "eval" / "thresholds.yml"


def _git(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(["git", *cmd], cwd=ROOT).decode("utf-8").strip()
    except Exception:
        return None


def _load_yaml(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    print("[eval.snapshot] starting")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Load source files
    if not MANIFEST.exists():
        print("[eval.snapshot] FAIL no eval/manifest.yml")
        return 2
    if not THRESHOLDS.exists():
        print("[eval.snapshot] FAIL no eval/thresholds.yml")
        return 2

    manifest_data = _load_yaml(MANIFEST)
    thresholds_data = _load_yaml(THRESHOLDS)

    # Write snapshot files
    manifest_snapshot = SNAPSHOT_DIR / "manifest.snapshot.yml"
    thresholds_snapshot = SNAPSHOT_DIR / "thresholds.snapshot.yml"

    with manifest_snapshot.open("w", encoding="utf-8") as f:
        yaml.safe_dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    with thresholds_snapshot.open("w", encoding="utf-8") as f:
        yaml.safe_dump(thresholds_data, f, default_flow_style=False, sort_keys=False)

    # Create provenance snapshot
    provenance = {
        "git_head": _git(["rev-parse", "HEAD"]),
        "git_branch": _git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "timestamp_unix": int(time.time()),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "manifest_version": manifest_data.get("version"),
        "thresholds_version": thresholds_data.get("version"),
    }

    provenance_snapshot = SNAPSHOT_DIR / "provenance.snapshot.json"
    import json  # noqa: E402

    provenance_snapshot.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")

    print(f"[eval.snapshot] wrote {manifest_snapshot.relative_to(ROOT)}")
    print(f"[eval.snapshot] wrote {thresholds_snapshot.relative_to(ROOT)}")
    print(f"[eval.snapshot] wrote {provenance_snapshot.relative_to(ROOT)}")
    print("[eval.snapshot] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
