import os
import pathlib
import subprocess
import sys

ENVELOPE = os.environ.get("ENVELOPE", "share/exports/envelope.json")
MIN_NODES = int(os.environ.get("MIN_NODES", "1"))
MIN_EDGES = int(os.environ.get("MIN_EDGES", "0"))
ALLOW_EMPTY = os.environ.get("ALLOW_EMPTY") == "1"


def test_envelope_min_counts():
    p = pathlib.Path(ENVELOPE)
    if not p.exists():
        import pytest

        pytest.skip(f"envelope not found at {ENVELOPE}")
    cmd = [
        sys.executable,
        "scripts/acceptance/check_envelope.py",
        ENVELOPE,
        "--min-nodes",
        str(MIN_NODES),
        "--min-edges",
        str(MIN_EDGES),
    ]
    if ALLOW_EMPTY:
        cmd.append("--allow-empty")
    subprocess.check_call(cmd)
