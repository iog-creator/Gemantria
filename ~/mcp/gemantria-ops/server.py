#!/usr/bin/env python3
import os
import pathlib
import shlex
import subprocess
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gemantria-ops")
ROOT = pathlib.Path(os.getenv("GEMANTRIA_ROOT", ".")).resolve()

# Add scripts directory to path for monitor_pipeline import
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _run(cmd: str) -> dict:
    p = subprocess.run(
        shlex.split(cmd),
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    return {
        "cmd": cmd,
        "cwd": str(ROOT),
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


@mcp.tool()  # one-command pipeline
def make_go() -> dict:
    "Run lint/format → audits → share"
    return _run("make go")


@mcp.tool()
def mini_go() -> dict:
    "Run real mini + metrics"
    return _run("make mini.go")


@mcp.tool()
def readiness_verify() -> dict:
    "Schema + thresholds (hard)"
    return _run("make readiness.verify")


@mcp.tool()
def book_plan() -> dict:
    "Plan chapters (no inference)"
    return _run("make book.plan")


@mcp.tool()
def book_dry() -> dict:
    "Validate services/env (no LM calls)"
    return _run("make book.dry")


@mcp.tool()
def book_stop(n: int = 1) -> dict:
    "Stop-loss N chapters (gated)"
    return _run(f"make book.stop N={n}")


@mcp.tool()
def book_resume() -> dict:
    "Resume deterministic run"
    return _run("make book.resume")


@mcp.tool()
def book_stats() -> dict:
    "Summarize chapter timings/RCs"
    return _run("make book.stats")


@mcp.tool()
def book_go() -> dict:
    "Full run (gated by readiness PASS)"
    pre = _run("make readiness.verify")
    return pre if pre["returncode"] else _run("make book.go")


@mcp.tool()
def share_sync() -> dict:
    "Mirror minimal artifacts"
    return _run("make share.sync")


@mcp.tool()
def rules_audit_all() -> dict:
    "Run all audits"
    return _run("make rules.navigator.check rules.audit repo.audit docs.audit")


@mcp.tool()
def monitor_pipeline(pid: int | None = None, json_output: bool = False) -> dict:
    """Monitor pipeline status and wait for completion.
    
    Args:
        pid: Optional process ID to monitor (auto-detected if None)
        json_output: If True, return JSON format; otherwise return formatted text
    
    Returns:
        dict with pipeline status, metrics, GPU stats, and process info
    """
    try:
        # Import monitor_pipeline module
        from monitor_pipeline import monitor_once
        
        # Run single monitoring cycle
        status = monitor_once(pid)
        
        if json_output:
            # Return as JSON-serializable dict
            return {
                "status": "success",
                "data": {
                    "stage_status": status.get("stage_status", {}),
                    "metrics": status.get("metrics", {}),
                    "process_stats": status.get("process_stats", {}),
                    "gpu_stats": status.get("gpu_stats", {}),
                    "errors": status.get("errors", []),
                    "timestamp": status.get("timestamp"),
                }
            }
        else:
            # Return formatted text output
            from monitor_pipeline import format_status_report
            formatted = format_status_report(
                status["stage_status"],
                status["metrics"],
                status["process_stats"],
                status["gpu_stats"],
                status["errors"],
            )
            return {
                "status": "success",
                "output": formatted,
                "data": status,
            }
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Failed to import monitor_pipeline: {e}",
            "hint": "Make sure scripts/monitor_pipeline.py exists and dependencies are installed",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@mcp.tool()
def wait_for_pipeline_completion(pid: int | None = None, check_interval: int = 10, max_wait: int = 3600) -> dict:
    """Wait for pipeline to complete, checking periodically.
    
    Args:
        pid: Optional process ID to monitor (auto-detected if None)
        check_interval: Seconds between checks (default: 10)
        max_wait: Maximum seconds to wait (default: 3600 = 1 hour)
    
    Returns:
        dict with final status and whether pipeline completed
    """
    import time
    
    try:
        from monitor_pipeline import monitor_once
        start_time = time.time()
        checks = 0
        
        while time.time() - start_time < max_wait:
            checks += 1
            status = monitor_once(pid)
            
            # Check if enrichment is complete
            stage_status = status.get("stage_status", {})
            enrichment = stage_status.get("enrichment", {})
            
            if enrichment.get("status") == "COMPLETE":
                return {
                    "status": "success",
                    "completed": True,
                    "checks": checks,
                    "elapsed_seconds": int(time.time() - start_time),
                    "final_status": status,
                }
            
            # Check if process is still running
            process_stats = status.get("process_stats", {})
            if process_stats.get("runtime") == "finished" and not pid:
                return {
                    "status": "success",
                    "completed": True,
                    "checks": checks,
                    "elapsed_seconds": int(time.time() - start_time),
                    "final_status": status,
                }
            
            time.sleep(check_interval)
        
        # Timeout reached
        return {
            "status": "timeout",
            "completed": False,
            "checks": checks,
            "elapsed_seconds": int(time.time() - start_time),
            "final_status": monitor_once(pid),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
