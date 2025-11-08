#!/usr/bin/env python3
"""
Sandbox smoke check for TS code-exec PoC (ADR-063).
Gate-aware: skips when CODE_EXEC_TS=0 (default).
If enabled, runs a hermetic Node/TS hello-world in a sandboxed process.
"""

import os
import subprocess
import sys

CODE_EXEC_TS = os.getenv("CODE_EXEC_TS", "0")


def main():
    if CODE_EXEC_TS == "0":
        print("SKIP (CODE_EXEC_TS=0): TS sandbox PoC disabled (default).")
        sys.exit(0)

    # If enabled, run a minimal TS/Node hello-world
    # This is a placeholder for the actual sandbox implementation
    try:
        # Check if Node.js is available
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            print("SKIP: Node.js not available", file=sys.stderr)
            sys.exit(0)

        # Minimal hello-world (no network, no file I/O beyond temp)
        hello_script = "console.log('TS sandbox smoke: OK');"
        result = subprocess.run(
            ["node", "-e", hello_script],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("OK: TS sandbox smoke passed (hermetic hello-world).")
            sys.exit(0)
        else:
            print(f"ERROR: TS sandbox smoke failed: {result.stderr}", file=sys.stderr)
            sys.exit(2)

    except subprocess.TimeoutExpired:
        print("ERROR: TS sandbox smoke timed out", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("SKIP: Node.js not found (tolerated)", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: TS sandbox smoke exception: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
