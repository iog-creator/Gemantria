#!/usr/bin/env python3

import os, json

req = ["BIBLE_DSN", "GEMATRIA_DSN"]

present = {k: bool(os.getenv(k)) for k in req}

print(
    json.dumps(
        {"stage": "ingest.env.check", "required": req, "present": present, "hermetic": True},
        ensure_ascii=False,
    )
)

# Always exit 0 in CI (hermetic policy)
