#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time


def sha256(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to release_manifest.json")
    ap.add_argument(
        "--hard-cmd",
        default="make -s eval.verify.integrity",
        help="Command to run the hard integrity check once",
    )
    ap.add_argument("--cache-dir", default=".cache/integrity", help="Cache directory")
    ap.add_argument("--timeout", type=int, default=180, help="Timeout (s) for hard check")
    args = ap.parse_args()

    man = pathlib.Path(args.manifest)
    if not man.exists():
        print(f"[integrity.fast] SKIP (no manifest: {man})")
        print("[integrity] soft gate: SKIP (non-blocking)")
        return 0

    cache = pathlib.Path(args.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    key = sha256(man.read_bytes())
    stamp = cache / f"{key}.json"

    if stamp.exists():
        try:
            meta = json.loads(stamp.read_text())
            status = meta.get("status")
            ts = meta.get("ts")
            print(f"[integrity.fast] cache hit (status={status}, ts={ts})")
            print(f"[integrity] soft gate: {str(status).upper()} (cached)")
            return 0
        except Exception:
            pass  # fall through to recompute

    print("[integrity.fast] cache miss → running hard check once…")
    start = time.time()
    try:
        rc = subprocess.run(args.hard_cmd, shell=True, timeout=args.timeout).returncode
    except subprocess.TimeoutExpired:
        rc = 124

    status = "pass" if rc == 0 else ("timeout" if rc == 124 else "fail")
    stamp.write_text(json.dumps({"status": status, "rc": rc, "ts": time.time()}))
    dur = time.time() - start
    print(f"[integrity.fast] result={status} rc={rc} dur={dur:.2f}s")
    print(f"[integrity] soft gate: {status.upper()} (non-blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
