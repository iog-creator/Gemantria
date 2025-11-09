#!/usr/bin/env python3

from __future__ import annotations

import json, os, re, sys, pathlib, datetime, zoneinfo

ROOT = pathlib.Path(__file__).resolve().parents[2]

EXPORTS = ROOT / "exports"

FILES = ["graph_latest.scored.json", "ai_nouns.json", "graph_stats.json", "graph_patterns.json"]

RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$")


def is_tag_ctx() -> bool:
    return (
        os.getenv("GITHUB_REF_TYPE", "").lower() == "tag"
        or os.getenv("GITHUB_REF", "").startswith("refs/tags/")
        or os.getenv("STRICT_TAG_CONTEXT") == "1"
    )


def find_generated_at(obj):
    # prefer top-level 'generated_at'; fall back to obj.get('meta',{}).get('generated_at')

    if isinstance(obj, dict):
        if "generated_at" in obj:
            return obj["generated_at"]

        meta = obj.get("meta") or obj.get("metadata")

        if isinstance(meta, dict) and "generated_at" in meta:
            return meta["generated_at"]

    return None


def main() -> int:
    strict = is_tag_ctx() or os.getenv("STRICT_EXPORTS_RFC3339") == "1"

    verdict = {
        "schema": "guard.exports-rfc3339.v1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "strict": bool(strict),
        "files": {},
        "ok": False,
    }

    errors, hints = [], []

    for name in FILES:
        p = EXPORTS / name

        status = {"exists": p.exists(), "has_generated_at": False, "rfc3339_ok": False, "error": None}

        if not p.exists():
            msg = f"missing: exports/{name}"

            (errors if strict else hints).append(msg)

            verdict["files"][name] = status

            continue

        try:
            obj = json.loads(p.read_text())

            ts = find_generated_at(obj)

            status["has_generated_at"] = ts is not None

            if ts is None:
                msg = f"{name}: missing generated_at"

                (errors if strict else hints).append(msg)

            else:
                ok = bool(RFC3339.match(ts))

                status["rfc3339_ok"] = ok

                if not ok:
                    (errors if strict else hints).append(f"{name}: generated_at not RFC3339 (fast-lane)")

        except Exception as e:
            status["error"] = f"json:{type(e).__name__}"

            (errors if strict else hints).append(f"{name}: unreadable JSON: {e}")

        verdict["files"][name] = status

    for h in hints:
        print("HINT: exports.rfc3339:", h, file=sys.stderr)

    verdict["ok"] = not errors

    # always write verdict

    out = ROOT / "evidence" / "exports_rfc3339.verdict.json"

    out.parent.mkdir(parents=True, exist_ok=True)

    out.write_text(json.dumps(verdict, ensure_ascii=False))

    print(f"HINT: exports.rfc3339: wrote verdict -> {out}", file=sys.stderr)

    if errors:
        for e in errors:
            print("ERROR: exports.rfc3339:", e, file=sys.stderr)

        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
