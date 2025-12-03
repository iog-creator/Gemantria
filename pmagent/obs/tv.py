import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Re-use log path from logger
from pmagent.obs.logger import LOG_FILE


def watch_tv(follow: bool = True, lines: int = 20) -> None:
    """
    Watch the retrieval log like a TV.

    Args:
        follow: If True, tail the file forever.
        lines: Number of initial lines to show.
    """
    print(f"📺  AgentPM TV - Watching {LOG_FILE}...")
    print(f"Waiting for retrieval events... (Ctrl+C to exit)")
    print("-" * 60)

    if not LOG_FILE.exists():
        print(f"(Log file {LOG_FILE} does not exist yet. Waiting for events...)")
        # Create it so we can tail it
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.touch()

    # Read last N lines
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            # Simple tail implementation
            all_lines = f.readlines()
            last_n = all_lines[-lines:]
            for line in last_n:
                _print_entry(line)

            if not follow:
                return

            # Tail
            f.seek(0, 2)  # Go to end
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                _print_entry(line)

    except KeyboardInterrupt:
        print("\n👋 TV turned off.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error watching TV: {e}")
        sys.exit(1)


def _print_entry(json_line: str) -> None:
    try:
        if not json_line.strip():
            return
        data = json.loads(json_line)

        # Format: [HH:MM:SS] [LANE] (Context) Query...
        dt = datetime.fromisoformat(data.get("dt", ""))
        ts_str = dt.strftime("%H:%M:%S")
        lane = data.get("lane", "???")
        context = data.get("context", "unknown")
        query = data.get("query", "")
        model = data.get("model", "")

        # Colorize if possible (simple ANSI)
        # Lane colors: DEFAULT=Green, BIBLE=Blue, LEGACY=Yellow
        lane_color = "\033[92m"  # Green
        if lane == "BIBLE":
            lane_color = "\033[94m"  # Blue
        elif lane == "LEGACY":
            lane_color = "\033[93m"  # Yellow
        reset = "\033[0m"

        print(f"\033[90m[{ts_str}]\033[0m {lane_color}[{lane}]\033[0m ({context}) {query}")
        print(f"           \033[90m↳ Model: {model}\033[0m")

    except Exception:
        # Fallback for bad lines
        print(json_line.strip())
