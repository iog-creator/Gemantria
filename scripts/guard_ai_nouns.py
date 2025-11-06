import json, sys, pathlib, re

from jsonschema import validate, Draft202012Validator, exceptions as je

BAD = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F]")


def scrub(x):
    if isinstance(x, str):
        return BAD.sub("", x)
    if isinstance(x, list):
        return [scrub(v) for v in x]
    if isinstance(x, dict):
        return {k: scrub(v) for k, v in x.items()}
    return x


root = pathlib.Path(".")

payload = json.loads(root.joinpath("exports/ai_nouns.json").read_text())

schema = json.loads(root.joinpath("docs/SSOT/SSOT_ai-nouns.v1.schema.json").read_text())

payload = scrub(payload)

Draft202012Validator.check_schema(schema)

try:
    validate(payload, schema)
except je.ValidationError as e:
    print("FAIL_SCHEMA:", e.message)
    sys.exit(2)

# invariants: no empty surface; letters join to surface length (best-effort; Hebrew combining marks tolerated)
bad = [n for n in payload["nodes"] if not n["surface"] or len(n["letters"]) < 1]
if bad:
    print("FAIL_INVARIANT: empty surface or zero letters:", len(bad))
    sys.exit(2)

print("AI_NOUNS_GUARD_OK")
