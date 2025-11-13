#!/usr/bin/env python3
"""
Control-plane MCP catalog export.

Reuses the existing mcp_catalog_stub.py to query control.mcp_tool_catalog
and exports the result to share/atlas/control_plane/mcp_catalog.json
for Atlas integration.

Uses centralized DSN loader (via stub script).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STUB_SCRIPT = REPO_ROOT / "scripts" / "db" / "mcp_catalog_stub.py"
STUB_JSON = REPO_ROOT / "evidence" / "mcp_catalog_stub.json"
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
OUT_PATH = OUT_DIR / "mcp_catalog.json"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def run_stub() -> None:
    """Best-effort: run the existing MCP catalog stub script.

    The stub is responsible for querying control.mcp_tool_catalog with the
    centralized DSN loader. This script then reshapes/relocates its JSON for
    control-plane Atlas exports.
    """
    if STUB_SCRIPT.exists():
        # We intentionally do not fail on non-zero exit; DB-off behavior is
        # handled by the stub itself and by our fallback below.
        subprocess.run(
            [sys.executable, str(STUB_SCRIPT)],
            check=False,
            cwd=REPO_ROOT,
        )


def build_db_off(error_msg: str) -> dict:
    """DB-off tolerant payload when the stub is missing or malformed."""
    return {
        "schema": "control",
        "generated_at": now_iso(),
        "ok": False,
        "connection_ok": False,
        "tools": [],
        "error": error_msg,
    }


def load_stub_payload() -> dict | None:
    if not STUB_JSON.exists():
        return None
    try:
        raw = STUB_JSON.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {"__error__": f"failed to read stub JSON: {exc}"}
    if not isinstance(data, dict):
        return {"__error__": "stub JSON is not an object"}
    return data


def normalize_payload(data: dict) -> dict:
    """Ensure the payload has the required control-plane keys."""
    data.setdefault("schema", "control")
    data.setdefault("generated_at", now_iso())
    data.setdefault("ok", False)
    data.setdefault("connection_ok", False)
    data.setdefault("tools", [])
    data.setdefault("error", None)
    return data


def main() -> int:
    """Generate control-plane MCP catalog export."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Run stub to refresh evidence/mcp_catalog_stub.json (best-effort).
    run_stub()

    # 2) Try to load the stub JSON.
    stub_data = load_stub_payload()
    if stub_data is None:
        payload = build_db_off("mcp_catalog_stub.json not found")
    elif "__error__" in stub_data:
        payload = build_db_off(stub_data["__error__"])
    else:
        payload = normalize_payload(stub_data)

    # 3) Write the control-plane export JSON for Atlas.
    OUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    print(f"[control_mcp_catalog_export] Wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
