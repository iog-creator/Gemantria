from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any

_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class _UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "ts": int(time.time() * 1000),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra_json") and isinstance(record.extra_json, dict):
            payload.update(record.extra_json)
        return json.dumps(payload, ensure_ascii=False, cls=_UUIDEncoder)


def get_logger(name: str = "gemantria") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(_LEVEL)
    h = logging.StreamHandler(stream=sys.stdout)
    h.setFormatter(_JsonFormatter())
    logger.addHandler(h)
    logger.propagate = False
    return logger


def log_json(logger: logging.Logger, level: int, msg: str, **extra: Any) -> None:
    logger.log(level, msg, extra={"extra_json": extra})
