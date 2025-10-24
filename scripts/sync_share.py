#!/usr/bin/env python3
"""
sync_share.py — standard share sync entrypoint.

Delegates to update_share.py to refresh the flat share/ folder
based on share/SHARE_MANIFEST.json.
"""

from update_share import main

if __name__ == "__main__":
    main()
