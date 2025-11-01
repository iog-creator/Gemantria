#!/usr/bin/env python3

"""

Gemantria CLI (reuse-first, Phase-6)

Thin Typer wrapper that proxies to existing Make targets and scripts.

No new logic; no network; hermetic-friendly.

"""

from __future__ import annotations

import subprocess, os, sys

import typer


app = typer.Typer(add_completion=False, no_args_is_help=True)


def _run(cmd: str) -> int:
    return subprocess.call(cmd, shell=True, env=os.environ.copy())


@app.command(help="Show active thresholds and key envs.")
def env():
    print("EDGE_STRONG=", os.getenv("EDGE_STRONG", "0.90"))

    print("EDGE_WEAK=", os.getenv("EDGE_WEAK", "0.75"))

    print("CANDIDATE_POLICY=", os.getenv("CANDIDATE_POLICY", "cache"))


@app.command(help="Run governance gates (ruff + rules_guard).")
def verify():
    sys.exit(_run("make -s ops.verify"))


@app.command(help="DB migrations (tolerates empty/missing DB if CI helper used).")
def db_migrate():
    sys.exit(_run("make -s db.migrate || make -s ci.db.tolerate.empty"))


@app.command(help="Pipeline smoke (reuse-first; hermetic).")
def pipeline():
    sys.exit(_run("make -s ci.pipeline.smoke"))


@app.command(help="Exports + badges (reuse-first; empty-DB tolerant).")
def exports():
    code = _run("make -s ci.exports.smoke && make -s ci.exports.validate && make -s ci.badges")

    sys.exit(code)


@app.command(help="Web UI smoke (adapter + existing viewer build if present).")
def webui():
    sys.exit(_run("make -s ci.webui.smoke"))


@app.command(help="Quality/reranker smoke (reuse-first).")
def quality():
    sys.exit(_run("make -s ci.quality.smoke && make -s quality.show.thresholds"))


@app.command(help="5-minute local quick-start (hermetic).")
def quickstart():
    cmds = [
        "ruff format --check . && ruff check .",
        "make -s ops.verify",
        "make -s ci.pipeline.smoke",
        "make -s ci.exports.smoke",
        "make -s ci.webui.smoke",
        "make -s ci.quality.smoke",
    ]

    for c in cmds:
        print("[quickstart]>", c)

        rc = _run(c)

        if rc != 0:
            print(f"[quickstart] step failed rc={rc}")

            sys.exit(rc)

    print("[quickstart] complete ✅")


if __name__ == "__main__":
    app()
