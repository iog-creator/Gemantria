import json
import time
from pathlib import Path
from datetime import datetime

# Default log path
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "retrieval.jsonl"


def log_retrieval(lane: str, model: str, query: str, context: str = "unknown") -> None:
    """
    Log a retrieval event to the TV log file.

    Args:
        lane: The retrieval profile/lane used (e.g., "DEFAULT", "BIBLE")
        model: The embedding model used
        query: The query text (will be truncated if too long)
        context: Where this retrieval happened (e.g., "docs_search", "bible_rag")
    """
    try:
        # Ensure log directory exists
        if not LOG_DIR.exists():
            LOG_DIR.mkdir(parents=True, exist_ok=True)

        entry = {
            "ts": time.time(),
            "dt": datetime.now().isoformat(),
            "lane": lane,
            "model": model,
            "context": context,
            "query": query[:200],  # Truncate for sanity
        }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception as e:
        # Fail silently to not break the app
        print(f"WARNING: failed to log retrieval event: {e}")
