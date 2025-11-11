#!/usr/bin/env python3
import json, os, sys, subprocess

def is_tag_build():
    if os.getenv("GITHUB_REF_TYPE") == "tag":
        return True
    try:
        out = subprocess.run(
            ["git","describe","--exact-match","--tags"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False
        )
        return out.returncode == 0 and out.stdout.strip() != ""
    except Exception:
        return False

strict = os.getenv("STRICT_GUARDS","0") in ("1","true","TRUE") or is_tag_build()
ok = True
notes = []
try:
    import jsonschema  # type: ignore
    have = True
except Exception:
    have = False
    notes.append("jsonschema not importable")

if strict and not have:
    ok = False

print(json.dumps({"guard":"jsonschema.import","strict":strict,"ok":ok,"have_jsonschema":have,"notes":notes}, indent=2))
sys.exit(0 if ok else 1)
