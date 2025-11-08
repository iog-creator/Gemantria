# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
sync_share.py — standard share sync entrypoint.

Delegates to update_share.py to refresh the flat share/ folder
based on share/SHARE_MANIFEST.json.
"""

from update_share import main

if __name__ == "__main__":
    main()
