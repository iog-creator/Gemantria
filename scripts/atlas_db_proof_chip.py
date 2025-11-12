#!/usr/bin/env python3
import json
import os
import pathlib
import re
import time


def redact(d):
    return re.sub(r"//[^@]*@", "//<REDACTED>@", d) if d else d


chip = {
    "strict": os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON"),
    "checkpointer": os.environ.get("CHECKPOINTER", ""),
    "dsn": redact(os.environ.get("GEMATRIA_DSN", "")),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}

p = pathlib.Path("share/atlas")
p.mkdir(parents=True, exist_ok=True)
(p / "db_proof_chip.json").write_text(json.dumps(chip, indent=2))

print(json.dumps(chip))
