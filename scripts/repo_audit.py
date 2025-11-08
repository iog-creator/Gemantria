# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
issues = []


def exists(p):
    return (ROOT / p).exists()


def read(p):
    try:
        return (ROOT / p).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def add(sev, msg):
    issues.append((sev, msg))


# 1) SSOT presence
for f in [
    "share/RULES_INDEX.md",
    "AGENTS.md",
    "share/SHARE_MANIFEST.json",
    "share/SSOT_MASTER_PLAN.md",
]:
    if not exists(f):
        add("ERR", f"Missing {f}")

# 2) Schemas present
schemas = [p for p in ROOT.rglob("*schema*.json")]
if not schemas:
    add("ERR", "No *schema*.json files found")

# 3) Rules integrity (index alignment)
rules_dir = ROOT / ".cursor" / "rules"
idx = read("share/RULES_INDEX.md") or read("docs/SSOT/RULES_INDEX.md") or ""
active_list = set()
# Accept either an "## Active" list or a table row: | num | file | title |
for line in idx.splitlines():
    s = line.strip()
    m_list = re.match(r"-\s+([0-9a-zA-Z\-_\.]+)", s)
    if m_list:
        active_list.add(m_list.group(1))
        continue
    if s.startswith("|") and s.count("|") >= 3:
        parts = [p.strip() for p in s.split("|")]
        if len(parts) >= 3 and parts[2].endswith(".mdc"):
            active_list.add(parts[2])
if rules_dir.exists():
    files = {p.name for p in rules_dir.glob("*.mdc")}
    unknown = sorted(files - active_list)
    if unknown:
        add("WARN", f"Rules not listed in RULES_INDEX.md: {', '.join(unknown)}")
else:
    add("ERR", ".cursor/rules missing")

# 4) Agents contract minimal fields present
agents = read("AGENTS.md")
if ("models.verify" not in agents) or ("LM_STUDIO_HOST" not in agents):
    add(
        "WARN",
        "AGENTS.md missing quick commands for models.verify or LM_STUDIO_HOST reference",
    )

# 5) SHARE manifest basic sanity
try:
    manifest = json.loads(read("share/SHARE_MANIFEST.json") or "{}")
    items = manifest.get("items", [])
    if not items:
        add("WARN", "SHARE_MANIFEST.json: items list is empty")
except Exception as e:
    add("ERR", f"Invalid SHARE_MANIFEST.json: {e}")

# 6) Quick grep for TODO/FIXME in src/ and docs/
hits = []
for p in list(ROOT.rglob("src/**/*.py")) + list(ROOT.rglob("docs/**/*.md")):
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "TODO" in t or "FIXME" in t:
            hits.append(str(p.relative_to(ROOT)))
    except Exception:
        pass
if hits:
    add(
        "INFO",
        f"TODO/FIXME present in: {', '.join(hits[:20])}{'…' if len(hits) > 20 else ''}",
    )

# 7) Env/model knobs present
envp = read(".env")
for key in [
    "ANSWERER_USE_ALT",
    "ANSWERER_MODEL_PRIMARY",
    "ANSWERER_MODEL_ALT",
    "EMBED_URL",
    "LM_STUDIO_HOST",
    "EMBEDDING_MODEL",
    "EMBED_BATCH_MAX",
    "CANDIDATE_POLICY",
]:
    if key not in envp:
        add("WARN", f".env missing {key}")

# 8) JSON adapters (psycopg3) guard
code_uses_json = any(
    "from psycopg.types.json import Json" in read(str(p.relative_to(ROOT))) for p in ROOT.rglob("**/*.py")
)
if not code_uses_json:
    add("WARN", "No psycopg Json adapter import found; ensure JSONB inserts adapt dicts")

# 9) Output
sev_rank = {"ERR": 0, "WARN": 1, "INFO": 2}
issues.sort(key=lambda x: sev_rank.get(x[0], 9))
print("== repo_audit ==")
for sev, msg in issues:
    print(f"{sev}: {msg}")
print("== repo_audit summary ==")
error_count = sum(1 for s, _ in issues if s == "ERR")
warn_count = sum(1 for s, _ in issues if s == "WARN")
info_count = sum(1 for s, _ in issues if s == "INFO")
print(f"errors={error_count}, warnings={warn_count}, info={info_count}")
sys.exit(1 if any(s == "ERR" for s, _ in issues) else 0)
