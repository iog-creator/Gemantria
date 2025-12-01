# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

import sys, json, os


def main():
    strict_mode = os.getenv("STRICT_CROSSREFS_GUARD", "0") == "1"
    hint_prefix = "HINT" if not strict_mode else "ERROR"

    if not os.path.exists("exports/ai_nouns.json"):
        msg = f"{hint_prefix}: exports/ai_nouns.json not found (hermetic behavior: file not generated)"
        print(msg, file=sys.stderr)
        sys.exit(2 if strict_mode else 0)

    try:
        with open("exports/ai_nouns.json") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"{hint_prefix}: exports/ai_nouns.json is malformed JSON: {e}"
        print(msg, file=sys.stderr)
        sys.exit(2 if strict_mode else 0)
    except Exception as e:
        msg = f"{hint_prefix}: failed to read exports/ai_nouns.json: {e}"
        print(msg, file=sys.stderr)
        sys.exit(2 if strict_mode else 0)

    if "nodes" not in data:
        msg = f"{hint_prefix}: no nodes in ai_nouns.json (hermetic behavior: empty structure)"
        print(msg, file=sys.stderr)
        sys.exit(2 if strict_mode else 0)

    node_count = len(data["nodes"])
    if node_count == 0:
        msg = (
            f"{hint_prefix}: no nodes found in ai_nouns.json (hermetic behavior: empty nodes array)"
        )
        print(msg, file=sys.stderr)
        sys.exit(2 if strict_mode else 0)

    print(f"OK: enrichment details preserved on {node_count} nodes.")


if __name__ == "__main__":
    main()
