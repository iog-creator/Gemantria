#!/usr/bin/env python3
"""Verify AI tracking export has RFC3339 timestamp and valid structure"""

import json
import re
import sys
from pathlib import Path

p = Path("exports/ai_tracking.json")
if not p.exists():
    print("[analytics.ai.verify] missing exports/ai_tracking.json", file=sys.stderr)
    sys.exit(2)

doc = json.loads(p.read_text(encoding="utf-8"))
ts = doc.get("generated_at", "")
ok_ts = bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$", ts))
totals = doc.get("totals", {})
sessions = totals.get("sessions", 0)
calls = totals.get("calls", 0)

print(
    f"[analytics.ai.verify] generated_at RFC3339: {'OK' if ok_ts else 'FAIL'}; sessions={sessions} calls={calls}"
)
sys.exit(0 if ok_ts else 3)
