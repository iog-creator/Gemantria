import os, sys, json, urllib.request

# Load environment variables from .env.local if it exists
if os.path.exists(".env.local"):
    with open(".env.local") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value


BASE = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:9994/v1")

REQUIRED = ["THEOLOGY_MODEL", "EMBEDDING_MODEL", "RERANKER_MODEL", "MATH_MODEL"]

MISSING = [k for k in REQUIRED if not os.environ.get(k)]

if MISSING:
    sys.stderr.write(f"[MCP:FATAL] Missing env keys: {MISSING}. Align with docs/MODEL_MANIFEST.md.\n")

    sys.exit(2)


def reachable(url: str, timeout=3) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200

    except Exception:
        return False


if not reachable(f"{BASE}/models"):
    sys.stderr.write(f"[MCP:FATAL] LM Studio not reachable at {BASE}. Run: make lm.health  && open the GUI/CLI.\n")

    sys.exit(3)


# Minimal JSON-RPC-style placeholder so your editor/tooling doesn't hang

# This is intentionally simple; your real MCP may use stdio sockets.

sys.stdout.write(
    json.dumps({"mcp": "ok", "provider": "lmstudio", "base_url": BASE, "models": "see make lm.models", "env_ok": True})
    + "\n"
)

sys.stdout.flush()
