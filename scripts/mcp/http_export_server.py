#!/usr/bin/env python3
"""
Dev-only tiny HTTP server to regenerate docs/atlas/data/mcp_catalog.json.

Behavior (offline-safe):
- POST /export  -> tries to run the existing exporter script (psql/DSN aware); on success writes JSON and returns 200.
- If DSN/psql missing, exporter writes the stub; we still return 200 with a note.
- GET  /health  -> 200 {"ok": true}

Never used in CI; for local convenience only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "scripts" / "mcp" / "export_catalog_json.py"
OUT = ROOT / "docs" / "atlas" / "data" / "mcp_catalog.json"


class H(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.strip("/") == "health":
            self._json(200, {"ok": True})
        else:
            self._json(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if self.path.strip("/") == "export":
            try:
                if not EXPORTER.exists():
                    self._json(500, {"ok": False, "error": "exporter_missing"})
                    return
                # Run exporter as a subprocess to keep PYTHONPATH simple.
                proc = subprocess.run([sys.executable, str(EXPORTER)], cwd=str(ROOT), capture_output=True, text=True)
                ok = proc.returncode == 0 and OUT.exists()
                self._json(
                    200 if ok else 500,
                    {
                        "ok": ok,
                        "returncode": proc.returncode,
                        "stdout": proc.stdout[-300:],
                        "stderr": proc.stderr[-300:],
                        "out_exists": OUT.exists(),
                    },
                )
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        else:
            self._json(404, {"ok": False, "error": "not_found"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8777"))
    print(f"[atlas-live] export server on http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
