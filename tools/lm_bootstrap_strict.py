import json
import os
import subprocess
import sys

CANDIDATES = [
    os.getenv("LM_CLI", ""),
    "lms",
    "/Applications/LM Studio.app/Contents/Resources/bin/lms",
    os.path.expanduser("~/.local/share/LM Studio/resources/bin/lms"),
    "/usr/local/bin/lms",
    "/usr/bin/lms",
]
CANDIDATES = [p for p in CANDIDATES if p]


def is_executable(path: str) -> bool:
    try:
        return os.path.isfile(path) and os.access(path, os.X_OK)
    except Exception:
        return False


def which(cmd: str) -> str | None:
    try:
        out = subprocess.check_output(["which", cmd], text=True).strip()
        return out if out else None
    except Exception:
        return None


def find_cli() -> str | None:
    envp = os.getenv("LM_CLI")
    if envp and is_executable(envp):
        return envp
    w = which("lms")
    if w and is_executable(w):
        return w
    for c in CANDIDATES:
        if is_executable(c):
            return c
    return None


def main() -> None:
    cli = find_cli()
    if not cli:
        print(
            "[FAIL] LM Studio CLI 'lms' not found. Install or symlink the binary; no UI fallback allowed.",
            file=sys.stderr,
        )
        sys.exit(1)
    # Emit a tiny JSON to be parsed by callers
    print(json.dumps({"mode": "cli", "cli": cli}))
    sys.exit(0)


if __name__ == "__main__":
    main()
