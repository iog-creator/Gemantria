#!/usr/bin/env python3
from __future__ import annotations

import json

from openai import OpenAI

from scripts.config.env import openai_cfg


def main() -> int:
    cfg = openai_cfg()
    # Log client config for evidence (no secrets)
    snap = {
        "base_url": cfg["base_url"],
        "embed_model": cfg["embed_model"],
        "api_key_len": len(cfg["api_key"] or ""),
    }
    print(json.dumps({"client_cfg": snap}))
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    out = client.embeddings.create(model=cfg["embed_model"], input=["hello from gemantria"])
    print(json.dumps({"dims": len(out.data[0].embedding)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
