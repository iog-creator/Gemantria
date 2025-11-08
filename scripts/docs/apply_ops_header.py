# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
from pathlib import Path

HEADER = """# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source=\"fallback_fast_lane\")

"""

changed = 0

for f in list(Path("scripts").rglob("*.py")) + list(Path("src").rglob("*.py")):
    t = f.read_text(encoding="utf-8", errors="ignore")
    if "OPS meta:" not in t.splitlines()[:5]:
        f.write_text(HEADER + t, encoding="utf-8")
        changed += 1

print(f"applied_header_to={changed}")
