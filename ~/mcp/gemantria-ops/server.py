#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import subprocess, shlex, os, pathlib

mcp = FastMCP("gemantria-ops")
ROOT = pathlib.Path(os.getenv("GEMANTRIA_ROOT",".")).resolve()

def _run(cmd: str) -> dict:
    p = subprocess.run(shlex.split(cmd), cwd=str(ROOT),
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "cwd": str(ROOT), "returncode": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr}

@mcp.tool()  # one-command pipeline
def make_go() -> dict: "Run lint/format → smart strict/soft → audits → share"; return _run("make go")

@mcp.tool()
def mini_go() -> dict: "Run real mini + metrics"; return _run("make mini.go")

@mcp.tool()
def readiness_verify() -> dict: "Schema + thresholds (hard)"; return _run("make readiness.verify")

@mcp.tool()
def book_plan() -> dict: "Plan chapters (no inference)"; return _run("make book.plan")

@mcp.tool()
def book_dry() -> dict: "Validate services/env (no LM calls)"; return _run("make book.dry")

@mcp.tool()
def book_stop(n: int = 1) -> dict: "Stop-loss N chapters (gated)"; return _run(f"make book.stop N={n}")

@mcp.tool()
def book_resume() -> dict: "Resume deterministic run"; return _run("make book.resume")

@mcp.tool()
def book_stats() -> dict: "Summarize chapter timings/RCs"; return _run("make book.stats")

@mcp.tool()
def book_go() -> dict:
    "Full run (gated by readiness PASS)"
    pre = _run("make readiness.verify")
    return pre if pre["returncode"] else _run("make book.go")

@mcp.tool()
def share_sync() -> dict: "Mirror minimal artifacts"; return _run("make share.sync")

@mcp.tool()
def rules_audit_all() -> dict: "Run all audits"; return _run("make rules.navigator.check rules.audit repo.audit docs.audit")

if __name__ == "__main__":
    mcp.run(transport="stdio")
