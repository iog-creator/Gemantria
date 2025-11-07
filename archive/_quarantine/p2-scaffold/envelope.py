from __future__ import annotations

from dataclasses import dataclass, asdict

from typing import Any, Dict

import json

import os

import sys

import time

import uuid

import hashlib

import random


def _seed_from_env() -> int:
    s = os.getenv("PIPELINE_SEED", "42")

    try:
        return int(s)

    except ValueError:
        return 42


RANDOM_SEED = _seed_from_env()

random.seed(RANDOM_SEED)


def deterministic_uuid(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

    # uuidv4-compatible formatting based on hash

    return str(uuid.UUID(h[0:32]))


@dataclass
class Envelope:
    run_id: str

    stage: str

    ok: bool

    items: int = 0

    meta: Dict[str, Any] = None

    hint: str | None = None

    ts: float = time.time()

    def to_json(self) -> str:
        d = asdict(self)

        return json.dumps(d, sort_keys=True, ensure_ascii=False)


def emit(stage: str, ok: bool, items: int = 0, **meta: Any) -> None:
    run_id = os.getenv("RUN_ID") or deterministic_uuid(str(RANDOM_SEED), stage, str(time.time()))

    hint = f"HINT[pipeline.seed]: {RANDOM_SEED}"

    env = Envelope(run_id=run_id, stage=stage, ok=ok, items=items, meta=meta, hint=hint)

    sys.stdout.write(env.to_json() + "\n")

    sys.stdout.flush()
