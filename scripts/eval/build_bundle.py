#!/usr/bin/env python3
import pathlib
import tarfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_BUNDLES_DIR = ROOT / "share" / "eval" / "bundles"
DEFAULT_EVAL_DIR = ROOT / "share" / "eval"
BUNDLES_DIR = ROOT / os.environ.get("EVAL_BUNDLES_DIR", str(DEFAULT_BUNDLES_DIR.relative_to(ROOT)))
EVAL_DIR = ROOT / os.environ.get("EVAL_DIR", str(DEFAULT_EVAL_DIR.relative_to(ROOT)))


def main():
    print("[eval.bundle] starting")

    # Create bundles directory
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)

    # Create timestamped bundle name
    timestamp = int(time.time())
    bundle_name = f"eval_bundle_{timestamp}.tar.gz"
    bundle_path = BUNDLES_DIR / bundle_name

    # Create tar.gz bundle
    with tarfile.open(bundle_path, "w:gz") as tar:
        # Add key eval files (not entire directories)
        if EVAL_DIR.exists():
            # Add report files
            for pattern in ["*.json", "*.md", "*.html"]:
                for item in EVAL_DIR.glob(pattern):
                    if item.is_file() and item.stat().st_size < 1024*1024:  # Skip files > 1MB
                        tar.add(item, arcname=f"eval/{item.name}")

        # Add exports directory (just JSON files, not entire subdirs)
        exports_dir = ROOT / "exports"
        if exports_dir.exists():
            for item in exports_dir.glob("*.json"):
                if item.is_file() and item.stat().st_size < 1024*1024:  # Skip files > 1MB
                    tar.add(item, arcname=f"exports/{item.name}")

        # Add eval config files
        eval_config_dir = ROOT / "eval"
        if eval_config_dir.exists():
            for item in eval_config_dir.glob("*.yml"):
                if item.is_file():
                    tar.add(item, arcname=f"config/{item.name}")

    print(f"[eval.bundle] created {bundle_path}")
    print(f"[eval.bundle] bundle size: {bundle_path.stat().st_size} bytes")
    print("[eval.bundle] OK")


if __name__ == "__main__":
    main()
