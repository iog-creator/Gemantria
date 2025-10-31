#!/usr/bin/env python3
import pathlib
import tarfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLES_DIR = ROOT / "share" / "eval" / "bundles"
EVAL_DIR = ROOT / "share" / "eval"
EXPORTS_DIR = ROOT / "exports"
EVAL_CONFIG_DIR = ROOT / "eval"


def main() -> int:
    print("[eval.bundle] starting")

    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)

    # Generate timestamp
    ts = time.strftime("%Y%m%d%H%M%S")
    bundle_name = f"eval_bundle_{ts}.tar.gz"
    bundle_path = BUNDLES_DIR / bundle_name

    # Files to include
    files_to_bundle = []

    # Add share/eval/* artifacts
    if EVAL_DIR.exists():
        for item in EVAL_DIR.glob("*"):
            if item.is_file():
                files_to_bundle.append((item, f"share/eval/{item.name}"))

    # Add exports (if present)
    export_files = ["graph_latest.json", "graph_sanitized.json", "graph_repaired.json"]
    for export_file in export_files:
        export_path = EXPORTS_DIR / export_file
        if export_path.exists():
            files_to_bundle.append((export_path, f"exports/{export_file}"))

    # Add eval config files
    config_files = ["manifest.yml", "thresholds.yml"]
    for config_file in config_files:
        config_path = EVAL_CONFIG_DIR / config_file
        if config_path.exists():
            files_to_bundle.append((config_path, f"eval/{config_file}"))

    # Add snapshot files (if present)
    snapshot_dir = EVAL_DIR / "snapshot"
    if snapshot_dir.exists():
        for item in snapshot_dir.glob("*"):
            if item.is_file():
                files_to_bundle.append((item, f"share/eval/snapshot/{item.name}"))

    # Create the tar.gz bundle
    with tarfile.open(bundle_path, "w:gz") as tar:
        for src_path, arc_name in files_to_bundle:
            tar.add(src_path, arcname=arc_name)

    print(f"[eval.bundle] created {bundle_path.relative_to(ROOT)}")
    print(f"[eval.bundle] included {len(files_to_bundle)} files")
    print("[eval.bundle] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
