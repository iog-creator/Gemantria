#!/usr/bin/env python3
import json
import os
import pathlib
import re
import time


def redact(d: str) -> str:
    return re.sub(r"//[^@]*@", "//<REDACTED>@", d) if d else d


# Write/refresh chip JSON
chip = {
    "strict": os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON"),
    "checkpointer": os.environ.get("CHECKPOINTER", ""),
    "dsn": redact(os.environ.get("GEMATRIA_DSN", "")),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}

adir = pathlib.Path("share/atlas")
adir.mkdir(parents=True, exist_ok=True)
(adir / "db_proof_chip.json").write_text(json.dumps(chip, indent=2))

# Ensure Atlas index has a marker attribute or comment
idx = adir / "index.html"
if idx.exists():
    text = idx.read_text(errors="ignore")
else:
    text = "<!doctype html><html><head><meta charset='utf-8'></head><body><div id='app'></div></body></html>"

if "data-db-strict=" not in text and "db-proof-chip" not in text:
    text = text.replace("<div id='app'", "<div id='app' data-db-strict='true'><!-- db-proof-chip -->")

idx.write_text(text)

print(json.dumps({"index_html": str(idx), "marker": True}))
