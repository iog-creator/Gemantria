# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

import json
import re


def coerce_json_one_line(text: str) -> str:
    """Best-effort cleanup of LLM output to valid single-line JSON.

    - Strips markdown code fences
    - Removes control characters except tab/newline
    - Trims to last closing brace
    """
    s = text or ""
    # strip code fences
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.MULTILINE)
    # remove control chars (keep tab/newline)
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)
    # trim to last '}' if present (avoid trailing chatter)
    last = s.rfind("}")
    if last != -1:
        s = s[: last + 1]
    return s.strip()


def parse_llm_json(text: str) -> dict:
    """Parse LLM JSON with repair attempts.

    Tries full parse, then extracts top-level object if needed.
    """
    s1 = coerce_json_one_line(text)
    try:
        return json.loads(s1)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", s1)
        if m:
            return json.loads(coerce_json_one_line(m.group(0)))
        raise
