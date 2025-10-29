#!/usr/bin/env python3
import json
import pathlib
import shutil
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_SNAPSHOT_DIR = ROOT / "share" / "eval" / "snapshot"
ENV_SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR")
SNAPSHOT_DIR = (ROOT / ENV_SNAPSHOT_DIR) if ENV_SNAPSHOT_DIR else DEFAULT_SNAPSHOT_DIR


def main():
    print("[eval.snapshot] starting")

    # Ensure snapshot directory exists
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Create a basic snapshot with current timestamp
    snapshot_info = {
        "timestamp": int(time.time()),
        "type": "eval_snapshot",
        "version": "phase8"
    }

    # Write snapshot info
    snapshot_file = SNAPSHOT_DIR / "snapshot.json"
    snapshot_file.write_text(json.dumps(snapshot_info, indent=2), encoding="utf-8")

    # Copy current eval outputs to snapshot
    eval_dir = ROOT / "share" / "eval"
    if eval_dir.exists():
        for item in eval_dir.glob("*.json"):
            if item.is_file():
                shutil.copy2(item, SNAPSHOT_DIR / f"snapshot_{item.name}")

    print(f"[eval.snapshot] wrote snapshot to {SNAPSHOT_DIR}")
    print("[eval.snapshot] OK")


if __name__ == "__main__":
    main()
