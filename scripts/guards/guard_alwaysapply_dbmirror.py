#!/usr/bin/env python3
"""Mirror Always-Apply triad from automation Postgres before reading files."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List

TRIAD = {"050", "051", "052"}
DSN_ENV_VARS: List[str] = ["AI_AUTOMATION_DSN", "GEMATRIA_DSN"]


def main() -> int:
    dsn = next((os.getenv(var) for var in DSN_ENV_VARS if os.getenv(var)), None)
    result: dict[str, object] = {
        "source": "db",
        "dsn_env": next((var for var in DSN_ENV_VARS if os.getenv(var)), "missing"),
        "triad": None,
        "ok": True,
        "note": "",
    }

    if not dsn:
        result["note"] = "DSN missing; skipping DB mirror (HINT)."
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    probe = [
        "psql",
        dsn,
        "-At",
        "-c",
        "SELECT triad FROM ai_policy_view LIMIT 1;",
    ]

    try:
        output = subprocess.check_output(probe, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as exc:  # pragma: no cover - runtime guard
        result["note"] = f"DB mirror unavailable ({exc.returncode}); HINT only."
        result["ok"] = False
        print(json.dumps(result, indent=2, sort_keys=True))
        if os.getenv("STRICT_DB_MIRROR") == "1":
            return 1
        return 0

    triad = [item.strip() for item in output.split(",") if item.strip()]
    result["triad"] = triad or None

    if set(triad) == TRIAD:
        result["note"] = "DB triad matches."
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    result["note"] = "DB triad mismatch."
    result["ok"] = False
    print(json.dumps(result, indent=2, sort_keys=True))
    if os.getenv("STRICT_DB_MIRROR") == "1":
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
