#!/usr/bin/env python3
"""
Release Notes Enforcer: Block releases without proper models + evidence documentation.

Ensures release notes include models_used and evidence hashes for auditability.
"""

import json
import glob
import sys


def die(msg):
    """Fail with descriptive message."""
    print(f"RELEASE_NOTES_BLOCK: {msg}")
    sys.exit(1)


def main():
    """Main enforcer validation."""
    notes_files = sorted(glob.glob("share/release/notes/*.json")) or []

    if not notes_files:
        die("no release notes JSON found in share/release/notes/")

    notes = json.load(open(notes_files[-1]))

    # Must include models_used
    if not notes.get("models_used"):
        die("models_used missing in release notes")

    # Must include evidence with hashes
    ev = notes.get("evidence", [])
    if not ev or not all("sha256_12" in x for x in ev):
        die("evidence hashes missing")

    print("RELEASE_NOTES_OK")


if __name__ == "__main__":
    main()
