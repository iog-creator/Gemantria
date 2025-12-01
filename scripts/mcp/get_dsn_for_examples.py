#!/usr/bin/env python3
from __future__ import annotations

import os


def main():
    try:
        from scripts.config import env as _env

        ro = getattr(_env, "dsn_ro", lambda: None)()
        rw = getattr(_env, "dsn_rw", lambda: None)()
        print(ro or rw or "")
        return
    except Exception:
        pass

    print(os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO") or os.getenv("GEMATRIA_RW_DSN") or "")


if __name__ == "__main__":
    main()
