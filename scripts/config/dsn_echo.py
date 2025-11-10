#!/usr/bin/env python3
from __future__ import annotations

import argparse

from scripts.config.env import get_ro_dsn, get_rw_dsn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ro", action="store_true")
    ap.add_argument("--rw", action="store_true")
    a = ap.parse_args()
    if a.rw:
        print(get_rw_dsn() or "")
    else:
        print(get_ro_dsn() or "")
