"""

Unified bring-up system for DB + LM Studio (server + GUI).



Steps:

  1. Detect DB environment (systemd, docker, brew) based on project history.

  2. Start DB using the detected or configured mechanism.

  3. Detect LM Studio resolver configuration.

  4. Start LM Studio server using the 'lms' CLI.

  5. Attempt GUI launch if available (based on prior LM Studio Updater logic).

  6. Load all configured models (THEOLOGY, MATH, EMBEDDING, RERANKER, LM_EMBED_MODEL).

  7. Verify all endpoints.

  8. Emit runtime manifest to share/runtime/system_bringup.manifest.json.



This script is designed to be invoked via:

  pmagent bringup full

  make system.start

"""

import json
import os
import subprocess
import sys
from pathlib import Path


import scripts.ai.lmstudio_resolver as lmstudio_resolver

import requests


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def detect_db():
    # Attempt to determine DB startup style

    # systemd
    if (
        Path("/usr/lib/systemd/system/postgresql.service").exists()
        or Path("/lib/systemd/system/postgresql.service").exists()
    ):
        return ("systemd", ["sudo", "systemctl", "start", "postgresql"])

    # brew

    brew_path = Path("/opt/homebrew/bin/brew")

    if brew_path.exists():
        return ("brew", ["brew", "services", "start", "postgresql"])

    # docker compose

    if Path("docker-compose.yml").exists():
        return ("docker", ["docker", "compose", "up", "-d", "db"])

    return ("unknown", None)


def start_db():
    mode, cmd = detect_db()

    if cmd:
        proc = run(cmd)

        return {"mode": mode, "stdout": proc.stdout, "stderr": proc.stderr, "ok": proc.returncode == 0}

    return {"mode": "unknown", "ok": False, "reason": "no_db_start_command_detected"}


def start_lmstudio_server(port):
    proc = run(["lms", "server", "start", "--port", str(port)])

    return {"stdout": proc.stdout, "stderr": proc.stderr, "ok": proc.returncode == 0}


def load_model(model):
    base = lmstudio_resolver.base_url()

    ping_url = f"{base}/chat/completions"

    # Try loading via LMS CLI:

    run(["lms", "load", model])

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": f"Health check for {model}"}],
        "max_tokens": 16,
        "temperature": 0.0,
    }

    try:
        r = requests.post(ping_url, json=payload, timeout=10)

        r.raise_for_status()

        return {"model": model, "ok": True, "response": r.text}

    except Exception as e:
        return {"model": model, "ok": False, "error": str(e)}


def start_gui_if_available():
    # From LM Studio Updater attachment logic:

    # On macOS: open -a LM\ Studio

    # On Linux: try `lmstudio` or AppImage

    for cmd in [
        ["open", "-a", "LM Studio"],
        ["lmstudio"],
        ["./LM_Studio.AppImage"],
    ]:
        try:
            proc = run(cmd)

            if proc.returncode == 0:
                return {"attempted": cmd, "ok": True}

        except Exception:
            continue

    return {"ok": False, "reason": "gui_not_found"}


def main():
    manifest = {}

    manifest["db_start"] = start_db()

    manifest["gui"] = start_gui_if_available()

    base_url = lmstudio_resolver.base_url()

    manifest["lm_endpoint"] = {"base_url": base_url}

    # LM Studio port is inside the resolver; extract it:

    port = int(base_url.rsplit(":", 1)[-1].replace("/v1", ""))

    manifest["lm_server"] = start_lmstudio_server(port)

    models = []

    for env_var in [
        "THEOLOGY_MODEL",
        "MATH_MODEL",
        "EMBEDDING_MODEL",
        "LM_EMBED_MODEL",
        "RERANKER_MODEL",
    ]:
        m = os.getenv(env_var)

        if m:
            models.append(load_model(m))

    manifest["models"] = models

    out_path = Path("share/runtime")

    out_path.mkdir(parents=True, exist_ok=True)

    Path("share/runtime/system_bringup.manifest.json").write_text(json.dumps(manifest, indent=2))

    print(json.dumps(manifest, indent=2))

    # Exit non-zero if ANY model or LM server or DB failed:

    if not manifest["db_start"].get("ok"):
        sys.exit(1)

    if not manifest["lm_server"].get("ok"):
        sys.exit(1)

    if any(not m.get("ok") for m in models):
        sys.exit(1)


if __name__ == "__main__":
    main()
