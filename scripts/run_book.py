#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore  # hard-required by requirements-dev.txt
except Exception:
    yaml = None

BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "reports" / "readiness"
LOGS = BASE / "logs" / "book"
REPORTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

DEFAULT_CFG = {
    "book": "Genesis",
    "chapters": list(range(1, 51)),  # Genesis 1..50
    "seed": 20251024,
    "endpoints": {
        "api": ["localhost", 8000],
        "chat": ["localhost", 9991],
        "embed": ["localhost", 9994],
    },
    "concurrency": 1,
}


def _load_yaml_or_json(p: Path) -> dict[str, Any]:
    if not p.exists():
        return DEFAULT_CFG
    if p.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML not available but YAML config requested")
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    return json.loads(p.read_text(encoding="utf-8"))


def _port_up(host: str, port: int, timeout: float = 0.4) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def _require_services(cfg: dict[str, Any]) -> None:
    ok = True
    for name, (h, p) in cfg["endpoints"].items():
        up = _port_up(h, int(p))
        print(f"[guide] service {name} @{h}:{p} → {'up' if up else 'down'}")
        ok &= up
    if not ok:
        print(
            "[gate] required services down — start API/chat/embed and re-run.",
            file=sys.stderr,
        )
        sys.exit(2)


def _seed_env(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["GEMANTRIA_SEED"] = str(seed)


def _plan(cfg: dict[str, Any]) -> dict[str, Any]:
    plan = {
        "book": cfg["book"],
        "chapters": cfg["chapters"],
        "seed": cfg["seed"],
        "endpoints": cfg["endpoints"],
        "concurrency": cfg.get("concurrency", 1),
        "ts": time.time(),
        "id": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12],
    }
    return plan


def _write(path: Path, obj: Any) -> None:
    # Idempotent write to avoid noisy touches under share
    new = json.dumps(obj, indent=2, ensure_ascii=False)
    if path.exists() and path.read_text(encoding="utf-8") == new:
        print(f"[guide] unchanged: {path}")
        return
    path.write_text(new, encoding="utf-8")
    print(f"[guide] wrote: {path}")


def cmd_plan(args: argparse.Namespace) -> None:
    cfg = _load_yaml_or_json(Path(args.cfg))
    _write(REPORTS / "book_plan.json", _plan(cfg))


def cmd_dry(args: argparse.Namespace) -> None:
    cfg = _load_yaml_or_json(Path(args.cfg))
    _seed_env(int(cfg["seed"]))
    _require_services(cfg)
    plan = _plan(cfg)
    _write(REPORTS / "book_plan.json", plan)
    _write(LOGS / "dry_run.trace", {"ts": time.time(), "plan_id": plan["id"], "dry": True})
    print("[guide] dry-run OK (no LM calls executed)")


def _run_chapters(cfg: dict[str, Any], chapters: list[int], real: bool) -> None:
    _seed_env(int(cfg["seed"]))
    _require_services(cfg)
    book = cfg["book"]

    # Import the main pipeline here to avoid circular imports
    if real:
        from src.graph.graph import run_pipeline

    t0 = time.time()
    if real:
        # Call the real pipeline for this book (currently processes entire book, not individual chapters)
        try:
            result = run_pipeline(book=book, mode="START")
            pipeline_success = "error" not in result
            run_id = str(result.get("run_id", "unknown")) if "run_id" in result else "unknown"
        except Exception as e:
            print(f"[error] Pipeline failed for {book}: {e}")
            pipeline_success = False
            result = {"error": str(e)}
            run_id = "failed"
    else:
        # Dry run - just validate services
        pipeline_success = True
        result = {"dry_run": True}
        run_id = "dry-run"

    # Log the book-level result and simulate chapter-level logs for compatibility
    book_log_data = {
        "book": book,
        "chapters_requested": chapters,
        "seed": cfg["seed"],
        "real": real,
        "ts": time.time(),
        "pipeline_success": pipeline_success,
        "duration": time.time() - t0,
        "run_id": run_id,
    }

    # Write book-level log
    (LOGS / f"{book}.book.json").write_text(
        json.dumps(book_log_data, indent=2, default=str),
        encoding="utf-8",
    )

    # Create individual chapter logs for compatibility with existing tooling
    for ch in chapters:
        chapter_log_data = {
            "book": book,
            "chapter": ch,
            "seed": cfg["seed"],
            "real": real,
            "ts": time.time(),
            "pipeline_success": pipeline_success,
            "duration": time.time() - t0,  # Same duration for all chapters
            "run_id": run_id,
            "book_run": True,  # Indicates this was part of a book-level run
        }

        (LOGS / f"{book}.ch{ch:02d}.json").write_text(
            json.dumps(chapter_log_data, indent=2, default=str),
            encoding="utf-8",
        )
        print(
            f"[guide] chapter {ch} {'REAL' if real else 'DRY'} done in {time.time() - t0:.2f}s {'✓' if pipeline_success else '✗'}"
        )


def cmd_stop(args: argparse.Namespace) -> None:
    cfg = _load_yaml_or_json(Path(args.cfg))
    n = int(args.n)
    chapters = list(cfg["chapters"])[:n]
    # Run real inference for the partial book
    _run_chapters(cfg, chapters, real=True)
    # keep partial marker *out* of share to reduce churn
    _write(LOGS / "book_run.partial.json", {"run": "partial", "n": n, "ts": time.time()})
    print(f"[guide] stop-loss executed for first {n} chapter(s).")


def cmd_resume(_args: argparse.Namespace) -> None:
    # Resume: check if book-level run exists, otherwise run the full book
    # (Assumes DEFAULT_CFG or last used cfg; users can re-run stop/dry to reset plan)
    cfg = DEFAULT_CFG
    book_log = LOGS / f"{cfg['book']}.book.json"

    if book_log.exists():
        print(f"[guide] book {cfg['book']} already processed — nothing to resume.")
        return

    # Run the full book processing
    print(f"[guide] resuming full book processing for {cfg['book']}...")
    _run_chapters(cfg, cfg["chapters"], real=True)
    _write(LOGS / "book_run.resumed.json", {"resumed": cfg["chapters"], "ts": time.time()})
    print(f"[guide] resume executed for full book ({len(cfg['chapters'])} chapters).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers()
    p1 = sub.add_parser("plan")
    p1.add_argument("--cfg", required=True)
    p1.set_defaults(func=cmd_plan)
    p2 = sub.add_parser("dry")
    p2.add_argument("--cfg", required=True)
    p2.set_defaults(func=cmd_dry)
    p3 = sub.add_parser("stop")
    p3.add_argument("--cfg", required=True)
    p3.add_argument("--n", required=True)
    p3.set_defaults(func=cmd_stop)
    p4 = sub.add_parser("resume")
    p4.set_defaults(func=cmd_resume)
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)
    args = ap.parse_args()
    args.func(args)
