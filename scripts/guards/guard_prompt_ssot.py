#!/usr/bin/env python3
"""Guard to enforce GPT System Prompt SSOT structure."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path("GPT_SYSTEM_PROMPT.md")
SSOT = Path("docs/SSOT/GPT_SYSTEM_PROMPT.md")
STRICT = os.getenv("STRICT_PROMPT_SSOT", "0") == "1"


def sha(p: Path) -> str:
    """Compute short SHA256 hash of file."""
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def main() -> int:
    """Check SSOT structure and required sections."""
    report = {"ok": False, "exists": {}, "sections": {}, "hashes": {}, "note": ""}
    report["exists"]["root"] = ROOT.exists()
    report["exists"]["ssot"] = SSOT.exists()
    if not (ROOT.exists() and SSOT.exists()):
        report["note"] = "missing root or SSOT file"
        print(json.dumps(report, indent=2))
        return 2 if STRICT else 0

    txt = SSOT.read_text(encoding="utf-8", errors="ignore")
    has_box = re.search(r"```text\s*\[SYSTEM PROMPT", txt) is not None
    has_tutor = re.search(r"^##\s*Tutor notes", txt, flags=re.M) is not None
    report["sections"] = {"system_box": has_box, "tutor_notes": has_tutor}

    report["hashes"]["root"] = sha(ROOT)
    report["hashes"]["ssot"] = sha(SSOT)
    # Root is a pointer; don't require content match—just presence of SSOT + sections
    ok = report["exists"]["root"] and report["exists"]["ssot"] and has_box and has_tutor
    report["ok"] = ok
    print(json.dumps(report, indent=2))
    if not ok and STRICT:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
