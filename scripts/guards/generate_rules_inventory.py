#!/usr/bin/env python3
"""Generate RULES_INVENTORY table in AGENTS.md from .cursor/rules/*.mdc files."""
from pathlib import Path
import re

rules_dir = Path(".cursor/rules")
rows = []

for fp in sorted(rules_dir.glob("*.mdc")):
    name = fp.name
    m = re.match(r"^(\d{3})[-_](.*)\.mdc$", name)
    rid = m.group(1) if m else name.split(".")[0]
    text = fp.read_text(encoding="utf-8", errors="ignore")

    # title = first markdown H1 or fallback to file stub
    mt = re.search(r"(?m)^\s*#\s+(.+?)\s*$", text)
    title = mt.group(1).strip() if mt else (m.group(2).replace("-", " ") if m else name)

    # Check alwaysApply flag
    ma = re.search(r"(?im)^\s*alwaysApply\s*:\s*(true|false)\s*$", text)
    always = (ma.group(1).lower() == "true") if ma else False
    status = "Always-Apply" if always else "Default-Apply"

    rows.append((int(rid) if rid.isdigit() else 999, rid, title, name, status))

rows.sort(key=lambda r: r[0])

table = [
    "| ID | File | Title | Status |",
    "|---:|:-----|:------|:-------|",
]
for _, rid, title, name, status in rows:
    table.append(f"| {rid} | `{name}` | {title} | **{status}** |")

block = "\n".join(table) + "\n"

agents = Path("AGENTS.md")
doc = agents.read_text(encoding="utf-8", errors="ignore")
begin = "<!-- RULES_INVENTORY:BEGIN -->"
end = "<!-- RULES_INVENTORY:END -->"

if begin in doc and end in doc:
    new = re.sub(
        rf"{re.escape(begin)}.*?{re.escape(end)}",
        f"{begin}\n{block}{end}",
        doc,
        flags=re.S,
    )
else:
    new = doc.rstrip() + f"\n\n{begin}\n{block}{end}\n"

agents.write_text(new, encoding="utf-8")

# summary to stdout
triad_true = [r for r in rows if r[4] == "Always-Apply"]
print(
    f"inventory_rows={len(rows)} always_apply_ids={[r[1] for r in triad_true]}"
)

