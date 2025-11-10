#!/usr/bin/env python3
"""Sync Always-Apply triad from database to documentation files."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
from glob import glob
from pathlib import Path

# ---- Config / Env ----------------------------------------------------------------
STRICT = os.getenv("STRICT_ALWAYS_APPLY", "0") == "1"  # fail on drift
DSN = os.getenv("ATLAS_DSN") or os.getenv("GEMATRIA_DSN")  # read-only DSN
FILES = [
    "AGENTS.md",
    "RULES_INDEX.md",
    "README.md",
    "README_FULL.md",
    "docs/**/*.md",
    "share/**/*.md",
]

pat_block = re.compile(r"(?is)^[^\n]*Always[ -]Apply[^\n]*$\n(?:.*?\n)*?(?=^#|^\S|\Z)", re.M)
pat_ruleline = re.compile(r"^(?P<prefix>\s*[-*]\s*)(?P<rule>Rule-(?P<num>\d{3}))(?P<rest>.*)$", re.M)
# Optional sentinel comment we maintain inside the block (or immediately after its title line)
pat_sentinel = re.compile(r"<!--\s*alwaysapply\.sentinel:\s*([0-9,\s]+)\s*source=([a-z_]+)\s*-->", re.I)
# Also match old format: <!-- guard.alwaysapply sentinel: ... -->
pat_sentinel_old = re.compile(r"<!--\s*guard\.alwaysapply\s+sentinel:\s*[0-9,\s]+\s*-->", re.I)

SENTINEL_FMT = "<!-- alwaysapply.sentinel: {triad} source={source} -->"


def redact_dsn(dsn: str | None) -> dict:
    """Redact DSN for evidence output."""
    if not dsn:
        return {"present": False}
    try:
        u = urllib.parse.urlsplit(dsn)
        q = dict(urllib.parse.parse_qsl(u.query))
        return {
            "present": True,
            "scheme": u.scheme,
            "host": u.hostname,
            "port": u.port,
            "dbname": (u.path or "/").lstrip("/"),
            "sslmode": q.get("sslmode"),
            "redacted": True,
        }
    except Exception:
        return {"present": True, "redacted": True}


def _connect(dsn: str):
    """Connect to database using psycopg 3 (preferred) or psycopg2 (fallback only)."""
    try:
        import psycopg  # type: ignore

        return psycopg.connect(dsn, autocommit=True, connect_timeout=5)
    except ImportError:
        # Fallback to psycopg2 only if psycopg 3 is unavailable
        import psycopg2  # type: ignore

        return psycopg2.connect(dsn, connect_timeout=5)


def fetch_triad_from_db(dsn: str) -> tuple[list[str], str]:
    """
    Try a few sources, newest-first:
      1) ops_ssot_always_apply(view/table): SELECT rule_id WHERE active=true
      2) governance_policy(key='always_apply_rules'): JSON or CSV list
      3) ai_interactions(event='policy_update'): payload->always_apply_rules
    Return (rules, source_tag)
    """
    conn = _connect(dsn)
    cur = conn.cursor()
    # 1) ops_ssot_always_apply
    try:
        cur.execute(
            """
            select rule_id from ops_ssot_always_apply
            where coalesce(active,true) = true
            order by rule_id
        """
        )
        rows = [r[0] for r in cur.fetchall()]
        if rows:
            return [f"{int(x):03d}" for x in rows], "ops_ssot_always_apply"
    except Exception:
        pass
    # 2) governance_policy
    try:
        cur.execute(
            """
            select value from governance_policy
            where key in ('always_apply_rules','ALWAYS_APPLY_RULES')
            order by updated_at desc nulls last, created_at desc nulls last
            limit 1
        """
        )
        row = cur.fetchone()
        if row and row[0]:
            raw = str(row[0]).strip()
            rules: list[str] = []
            if raw.startswith("["):
                import json as _json

                rules = [f"{int(x):03d}" for x in _json.loads(raw)]
            else:
                rules = [f"{int(x):03d}" for x in re.split(r"[,\s]+", raw) if x]
            if rules:
                return rules, "governance_policy"
    except Exception:
        pass
    # 3) ai_interactions latest policy_update
    try:
        cur.execute(
            """
            select payload
            from ai_interactions
            where event in ('policy_update','governance_update')
            order by ts desc
            limit 1
        """
        )
        row = cur.fetchone()
        if row and row[0]:
            import json as _json

            payload = row[0] if isinstance(row[0], dict) else _json.loads(row[0])
            rules = payload.get("always_apply_rules") or payload.get("ALWAYS_APPLY_RULES")
            if rules:
                return [f"{int(x):03d}" for x in rules], "ai_interactions"
    except Exception:
        pass
    return [], "none"


def _ensure_sentinel(text: str, triad: list[str], source: str) -> str:
    """Ensure sentinel comment is present in the block (only one)."""
    sentinel = SENTINEL_FMT.format(triad=",".join(triad), source=source)
    # Remove all existing sentinels (old and new format)
    text = pat_sentinel.sub("", text)
    text = pat_sentinel_old.sub("", text)
    # Inject after the first line of the block (title line) to keep list formatting tidy
    lines = text.splitlines()
    if not lines:
        return text
    # Find first non-empty line after title
    insert_idx = 1
    for i, line in enumerate(lines[1:], 1):
        if line.strip():
            insert_idx = i
            break
    return "\n".join([*lines[:insert_idx], sentinel, *lines[insert_idx:]])


def rewrite_block_keep_descriptions(block: str, triad: list[str], source: str) -> tuple[str, bool]:
    """Replace the set of Rule-### lines inside the block with the triad,
    preserving descriptions for rules that already exist."""
    existing = {}

    def _store(m):
        existing[m.group("num")] = m.group(0)
        return m.group(0)

    _ = pat_ruleline.sub(_store, block)  # populate existing
    # Choose a prefix to keep list style consistent
    m0 = pat_ruleline.search(block)
    prefix = m0.group("prefix") if m0 else "- "
    # Build new lines in triad order, keeping known descriptions
    new_lines = []
    for r in triad:
        line = existing.get(r)
        if line:
            new_lines.append(line)
        else:
            new_lines.append(f"{prefix}Rule-{r}")
    # Remove all rule lines and sentinels, then insert our set once
    stripped = pat_ruleline.sub("", block)
    stripped = pat_sentinel.sub("", stripped)
    stripped = pat_sentinel_old.sub("", stripped)
    # Place new rule lines after the first heading line within the block
    parts = stripped.splitlines()
    # Insert right after the opening line (title of the block)
    if parts:
        # Find first non-empty line after title
        insert_idx = 1
        for i, line in enumerate(parts[1:], 1):
            if line.strip() and not line.strip().startswith("*"):
                insert_idx = i
                break
        parts = [*parts[:insert_idx], *new_lines, *parts[insert_idx:]]
    out = "\n".join([p for p in parts if p.strip() != ""])
    # Did we change anything?
    changed = set(existing.keys()) != set(triad) or any(r not in existing for r in triad)
    out = _ensure_sentinel(out, triad, source)
    return out + ("\n" if not out.endswith("\n") else ""), changed


def scan_and_optionally_write(triad: list[str], source: str, write: bool) -> dict:
    """Scan files for Always-Apply blocks and optionally rewrite them."""
    results = []
    changed_any = False
    for g in FILES:
        for path in glob(g, recursive=True):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            blocks = list(pat_block.finditer(text))
            if not blocks:
                continue
            new_text = text
            file_changed = False
            for m in reversed(blocks):  # reverse to keep offsets stable
                block = m.group(0)
                new_block, changed = rewrite_block_keep_descriptions(block, triad, source)
                if changed:
                    file_changed = True
                    start, end = m.span()
                    new_text = new_text[:start] + new_block + new_text[end:]
            if write and file_changed:
                Path(path).write_text(new_text, encoding="utf-8")
            if file_changed:
                changed_any = True
            results.append({"path": path, "blocks": len(blocks), "changed": file_changed})
    return {"changed_any": changed_any, "files": results}


def main() -> int:
    """Main entry point."""
    out = {
        "clock": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "STRICT" if STRICT else "HINT",
        "dsn": redact_dsn(DSN),
        "triad": [],
        "source": "",
        "ok": False,
        "note": "",
        "write": os.getenv("WRITE", "0") == "1",
        "results": {},
    }
    if not DSN:
        out["note"] = "DSN missing; using fallback triad"
        triad, source = (["050", "051", "052"], "fallback-default")
    else:
        try:
            triad, source = fetch_triad_from_db(DSN)
        except Exception as e:
            out["note"] = f"connect/query error: {e}; using fallback triad"
            triad, source = (["050", "051", "052"], "fallback-default")
    # Fallback to 050/051/052 if DB has nothing
    if not triad:
        triad, source = (["050", "051", "052"], "fallback-default")
    out["triad"], out["source"] = triad, source
    # Scan and optionally write
    out["results"] = scan_and_optionally_write(triad, source, write=out["write"])
    out["ok"] = True
    _write(out)
    return 0


def _write(payload: dict):
    """Write evidence JSON to file."""
    p = Path("evidence/guard_alwaysapply_dbmirror.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    sys.exit(main())
