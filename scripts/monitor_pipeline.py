#!/usr/bin/env python3
"""
Comprehensive Pipeline Monitor with Interactive Menu

Monitors all pipeline stages:
- collect_nouns: Noun extraction from Bible database
- validate_batch: Batch size and quality gates
- enrichment: AI-powered theological analysis
- confidence_validator: Quality threshold enforcement
- network_aggregator: Semantic embeddings and relationships
- schema_validator: JSON schema validation
- analysis_runner: Graph analysis and export

Orchestrator operations:
- pipeline: Main pipeline execution
- analysis: Graph analysis and exports
- full: Complete workflow (pipeline → analysis → exports)

Features:
- Real-time ETA calculations for all stages
- Last run timestamp tracking
- Error detection and extraction
- Interactive menu with quick actions
"""

import json
import os
import select
import shutil
import subprocess
import sys
import termios
import time
import tty
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Status colors
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"

    # Bright variants
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_MAGENTA = "\033[95m"

    # Background colors
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"


# Log file locations
LOG_DIR = Path("logs")
ORCHESTRATOR_LOG = Path("/tmp/orchestrator_venv.log")  # Background process log
PIPELINE_LOG = LOG_DIR / "pipeline_orchestrator.log"
GRAPH_LOG = LOG_DIR / "graph.log"


def get_gpu_stats() -> Dict[str, str | None]:
    """Get GPU utilization, memory, and temperature."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(", ")
            if len(parts) >= 4:
                return {
                    "utilization": parts[0].strip() + "%",
                    "memory": f"{parts[1].strip()}MB / {parts[2].strip()}MB",
                    "temperature": parts[3].strip() + "°C",
                }
    except Exception:
        pass
    return {"utilization": None, "memory": None, "temperature": None}


def get_process_stats(pid: int | None = None) -> Dict[str, Any]:
    """Get process runtime and CPU usage."""
    if not pid:
        # Try to find orchestrator process
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python.*pipeline_orchestrator.py.*full.*Genesis"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split()[0])
        except Exception:
            pass

    if not pid:
        return {"runtime": "finished", "cpu_usage": "N/A", "memory_usage": "N/A", "pid": None}

    try:
        # Get detailed stats including RSS (Resident Set Size) in KB
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "etime,pcpu,pmem,rss"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("\n")[-1].split()
            if len(parts) >= 4:
                rss_kb = int(parts[3])
                rss_mb = rss_kb / 1024.0
                rss_gb = rss_mb / 1024.0

                # Format memory nicely
                if rss_gb >= 1.0:
                    memory_str = f"{rss_gb:.2f} GB"
                elif rss_mb >= 1.0:
                    memory_str = f"{rss_mb:.1f} MB"
                else:
                    memory_str = f"{rss_kb} KB"

                # Get CPU usage: lifetime average from ps and current snapshot from top
                cpu_lifetime = float(parts[1])
                cpu_current = None

                try:
                    # Get current CPU usage from top (real-time snapshot)
                    top_result = subprocess.run(
                        ["top", "-b", "-n", "1", "-p", str(pid)],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    if top_result.returncode == 0:
                        lines = top_result.stdout.strip().split("\n")
                        # Find the header line to determine column positions
                        header_line = None
                        for line in lines:
                            if "%CPU" in line:
                                header_line = line
                                break

                        # Find the data line for our PID
                        for line in lines:
                            if str(pid) in line and "PID" not in line and "%CPU" not in line:
                                fields = line.split()
                                if header_line:
                                    # Find %CPU column index from header
                                    header_fields = header_line.split()
                                    try:
                                        cpu_idx = header_fields.index("%CPU")
                                        if cpu_idx < len(fields):
                                            cpu_current = float(fields[cpu_idx])
                                            break
                                    except (ValueError, IndexError):
                                        pass
                                else:
                                    # Fallback: %CPU is typically 8th field (index 8)
                                    if len(fields) >= 9:
                                        try:
                                            cpu_current = float(fields[8])
                                            break
                                        except (ValueError, IndexError):
                                            pass
                except Exception:
                    pass

                # Format CPU string - show both if available
                if cpu_current is not None:
                    cpu_str = f"{cpu_current:.1f}% (now), {cpu_lifetime:.1f}% (avg)"
                else:
                    cpu_str = f"{cpu_lifetime:.1f}%"

                return {
                    "runtime": parts[0],
                    "cpu_usage": cpu_str,
                    "memory_usage": memory_str,
                    "memory_usage_mb": rss_mb,
                    "pid": pid,
                }
    except Exception:
        pass

    return {"runtime": "unknown", "cpu_usage": "N/A", "memory_usage": "N/A", "pid": pid}


def parse_log_line(line: str) -> Dict[str, Any] | None:
    """Parse a structured JSON log line."""
    try:
        # Try to find JSON in the line
        if "{" in line and "}" in line:
            json_start = line.find("{")
            json_end = line.rfind("}") + 1
            json_str = line[json_start:json_end]
            data = json.loads(json_str)
            return data
    except (json.JSONDecodeError, ValueError):
        # Try to parse as a single JSON object if the line is just JSON
        try:
            return json.loads(line.strip())
        except Exception:
            pass
    return None


def scan_log_file(log_path: Path, max_lines: int = 1000) -> List[str]:
    """Read last N lines from log file."""
    if not log_path.exists():
        return []
    try:
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-max_lines:] if len(lines) > max_lines else lines
    except Exception:
        return []


def extract_errors(log_lines: List[str]) -> List[Dict[str, Any]]:
    """Extract error messages from log lines."""
    errors = []
    for line in log_lines:
        parsed = parse_log_line(line)
        if not parsed:
            continue

        level = parsed.get("level", "")
        msg = parsed.get("msg", "")
        error_text = parsed.get("error", "")

        if level == "ERROR" or "error" in msg.lower() or error_text:
            errors.append(
                {
                    "time": parsed.get("time", ""),
                    "level": level,
                    "msg": msg,
                    "error": error_text or parsed.get("error", ""),
                    "node": parsed.get("node", ""),
                    "book": parsed.get("book", ""),
                    "raw": line.strip(),
                }
            )

    return errors[-10:]  # Return last 10 errors


def check_file_progress() -> Dict[str, Any]:
    """Check progress by reading actual output files."""
    progress = {}

    # Check enrichment progress
    input_file = Path("exports/ai_nouns.json")
    output_file = Path("exports/ai_nouns.enriched.json")

    if input_file.exists():
        try:
            with open(input_file, encoding="utf-8") as f:
                input_data = json.load(f)
            total = len(input_data.get("nodes", []))

            enriched_with_theology = 0
            enriched_with_insights = 0
            count = 0

            # Check output file if it exists
            if output_file.exists():
                try:
                    with open(output_file, encoding="utf-8") as f:
                        output_data = json.load(f)
                    enriched_nodes = output_data.get("nodes", [])
                    count = len(enriched_nodes)

                    # Check if enrichment is actually happening
                    # Look for analysis.theology OR insights field (both indicate enrichment)
                    for n in enriched_nodes:
                        if n.get("analysis", {}).get("theology"):
                            enriched_with_theology += 1
                        if n.get("insights") or n.get("confidence"):
                            enriched_with_insights += 1

                    # Use the higher count (either theology or insights)
                    enriched_count = max(enriched_with_theology, enriched_with_insights)
                except Exception:
                    pass
            else:
                enriched_count = 0

            progress["enrichment"] = {
                "total": total,
                "count": count,
                "enriched_count": enriched_count,
                "file_exists": output_file.exists(),
            }
        except Exception:
            pass

    return progress


def extract_stage_status(log_lines: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Extract pipeline stage status from log lines. Returns (stage_status, stage_timings)."""
    stages = {
        "collect_nouns": {"status": "pending", "count": 0, "last_event": None, "start_time": None, "duration_ms": None},
        "validate_batch": {
            "status": "pending",
            "count": 0,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
        "enrichment": {
            "status": "pending",
            "count": 0,
            "total": 0,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
        "confidence_validator": {
            "status": "pending",
            "count": 0,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
        "network_aggregator": {
            "status": "pending",
            "count": 0,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
        "schema_validator": {
            "status": "pending",
            "status_msg": None,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
        "analysis_runner": {
            "status": "pending",
            "operation": None,
            "last_event": None,
            "start_time": None,
            "duration_ms": None,
        },
    }

    orchestrator_stage = {"status": "pending", "operation": None, "last_event": None, "start_time": None}

    # Check for running enrichment process
    enrichment_pid = None
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python.*ai_enrichment.py"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Enrichment process is running
            enrichment_pid = int(result.stdout.strip().split()[0])
            stages["enrichment"]["status"] = "running"
    except Exception:
        pass

    # Read enrichment progress from metrics database
    if enrichment_pid or stages["enrichment"]["status"] == "running":
        try:
            # Ensure environment is loaded
            from src.infra.env_loader import ensure_env_loaded

            ensure_env_loaded()

            import psycopg

            dsn = os.getenv("GEMATRIA_DSN")
            if dsn:
                with psycopg.connect(dsn) as conn:
                    with conn.cursor() as cur:
                        # Get latest batch_processed event for enrichment to get cumulative count
                        # The items_out field in batch_processed is cumulative (total enriched so far)
                        # Filter to last 1 hour to get current run
                        cur.execute("""
                            SELECT items_out, 
                                   items_in,
                                   started_at
                            FROM metrics_log
                            WHERE node = 'enrichment' 
                              AND event = 'batch_processed'
                              AND started_at >= NOW() - INTERVAL '1 hour'
                            ORDER BY started_at DESC
                            LIMIT 1
                        """)
                        row = cur.fetchone()
                        if row and row[0] is not None:
                            items_out = int(row[0])
                            stages["enrichment"]["count"] = max(stages["enrichment"]["count"], items_out)
                            stages["enrichment"]["last_event"] = row[2].isoformat() if row[2] else None
        except Exception:
            # Silently fail - metrics might not be available
            pass

    # Check file-based progress as fallback (always check if enrichment is running)
    file_progress = check_file_progress()
    if file_progress.get("enrichment"):
        enrichment_file = file_progress["enrichment"]
        if enrichment_file.get("total", 0) > 0:
            stages["enrichment"]["total"] = enrichment_file["total"]
            enriched_count = enrichment_file.get("enriched_count", enrichment_file.get("count", 0))
            # Always update count from file if enrichment is running
            if stages["enrichment"]["status"] == "running":
                stages["enrichment"]["count"] = enriched_count
            # If we have progress, mark as running
            if enriched_count > 0 and enriched_count < enrichment_file["total"]:
                stages["enrichment"]["status"] = "running"
            elif enriched_count >= enrichment_file["total"]:
                stages["enrichment"]["status"] = "complete"
            # Set collect_nouns and validate_batch counts if not set
            if stages["collect_nouns"]["count"] == 0:
                stages["collect_nouns"]["count"] = enrichment_file["total"]
            if stages["validate_batch"]["count"] == 0:
                stages["validate_batch"]["count"] = enrichment_file["total"]

    # First pass: find total noun count and collect_nouns count from logs
    for line in reversed(log_lines):
        parsed = parse_log_line(line)
        if parsed:
            # Find enrichment_start with noun_count (this is the authoritative total)
            if parsed.get("msg") == "enrichment_start" and "noun_count" in parsed:
                total_count = parsed.get("noun_count", 0)
                if total_count > 0:
                    stages["enrichment"]["total"] = total_count
                    # Also set collect_nouns and validate_batch counts if not set
                    if stages["collect_nouns"]["count"] == 0:
                        stages["collect_nouns"]["count"] = total_count
                    if stages["validate_batch"]["count"] == 0:
                        stages["validate_batch"]["count"] = total_count
                break  # Found it, stop looking

    # Second pass: process all events and track timings
    for line in log_lines:
        parsed = parse_log_line(line)
        if not parsed:
            continue

        msg = parsed.get("msg", "")
        event_time = parsed.get("time", "")
        duration_ms = parsed.get("duration_ms")

        # Orchestrator events
        if "pipeline_orchestrator_start" in msg or "full_workflow_start" in msg:
            orchestrator_stage["status"] = "running"
            orchestrator_stage["operation"] = parsed.get("book", parsed.get("operation", "unknown"))
            orchestrator_stage["last_event"] = event_time
            if not orchestrator_stage["start_time"]:
                orchestrator_stage["start_time"] = event_time
        elif "pipeline_orchestrator_complete" in msg or "full_workflow_complete" in msg:
            orchestrator_stage["status"] = "complete"
            orchestrator_stage["last_event"] = event_time
        elif "pipeline_orchestrator_failed" in msg:
            orchestrator_stage["status"] = "failed"
            orchestrator_stage["last_event"] = event_time

        # Enrichment stage
        if msg == "enrichment_start":
            stages["enrichment"]["status"] = "running"
            stages["enrichment"]["total"] = parsed.get("noun_count", stages["enrichment"]["total"] or 0)
            stages["enrichment"]["last_event"] = event_time
            if not stages["enrichment"]["start_time"]:
                stages["enrichment"]["start_time"] = event_time
        elif "noun_enriched" in msg:
            stages["enrichment"]["status"] = "running"
            stages["enrichment"]["count"] += 1
            stages["enrichment"]["last_event"] = event_time
        # Also check file progress periodically if no log updates
        elif stages["enrichment"]["status"] == "running":
            # Update from file if we haven't seen a log update recently
            file_progress = check_file_progress()
            if file_progress.get("enrichment"):
                enrichment_file = file_progress["enrichment"]
                if enrichment_file.get("enriched_count", 0) > stages["enrichment"]["count"]:
                    stages["enrichment"]["count"] = enrichment_file["enriched_count"]
        elif (
            parsed.get("msg") == "metrics"
            and parsed.get("node") == "enrichment"
            and parsed.get("event") == "batch_processed"
        ):
            stages["enrichment"]["status"] = "running"
            items_out = parsed.get("items_out", 0)
            stages["enrichment"]["count"] = max(stages["enrichment"]["count"], items_out)
            stages["enrichment"]["last_event"] = event_time
            if duration_ms:
                stages["enrichment"]["duration_ms"] = duration_ms

        # Collect nouns
        if stages["enrichment"]["status"] == "running":
            stages["collect_nouns"]["status"] = "complete"
            if stages["collect_nouns"]["count"] == 0:
                stages["collect_nouns"]["count"] = stages["enrichment"]["total"] or 0
        elif "collect_nouns" in msg.lower() and "start" in msg.lower():
            stages["collect_nouns"]["status"] = "running"
            stages["collect_nouns"]["last_event"] = event_time
            if not stages["collect_nouns"]["start_time"]:
                stages["collect_nouns"]["start_time"] = event_time
        elif "collect_nouns" in msg.lower() and "complete" in msg.lower():
            stages["collect_nouns"]["status"] = "complete"
            stages["collect_nouns"]["count"] = parsed.get(
                "count", parsed.get("noun_count", stages["collect_nouns"]["count"])
            )
            stages["collect_nouns"]["last_event"] = event_time
            if duration_ms:
                stages["collect_nouns"]["duration_ms"] = duration_ms
        elif "noun_collected" in msg:
            stages["collect_nouns"]["status"] = "running"
            stages["collect_nouns"]["count"] += 1
            stages["collect_nouns"]["last_event"] = event_time

        # Validate batch
        if stages["enrichment"]["status"] == "running":
            stages["validate_batch"]["status"] = "complete"
            if stages["validate_batch"]["count"] == 0:
                stages["validate_batch"]["count"] = stages["enrichment"]["total"] or 0
        elif "validate_batch_complete" in msg:
            stages["validate_batch"]["status"] = "complete"
            stages["validate_batch"]["count"] = parsed.get("validated_count", 0)
            stages["validate_batch"]["last_event"] = event_time
            if duration_ms:
                stages["validate_batch"]["duration_ms"] = duration_ms
        elif "validate_batch" in msg.lower() and stages["validate_batch"]["status"] == "pending":
            stages["validate_batch"]["status"] = "running"
            stages["validate_batch"]["last_event"] = event_time
            if not stages["validate_batch"]["start_time"]:
                stages["validate_batch"]["start_time"] = event_time

        # Confidence validator
        if "confidence_validator" in msg.lower():
            if "complete" in msg.lower():
                stages["confidence_validator"]["status"] = "complete"
                if duration_ms:
                    stages["confidence_validator"]["duration_ms"] = duration_ms
            elif stages["confidence_validator"]["status"] == "pending":
                stages["confidence_validator"]["status"] = "running"
                if not stages["confidence_validator"]["start_time"]:
                    stages["confidence_validator"]["start_time"] = event_time
            stages["confidence_validator"]["last_event"] = event_time

        # Network aggregator
        if "network_aggregator" in msg.lower() or "network_aggregation" in msg.lower():
            if "complete" in msg.lower():
                stages["network_aggregator"]["status"] = "complete"
                if duration_ms:
                    stages["network_aggregator"]["duration_ms"] = duration_ms
            elif "failed" in msg.lower() or "aborted" in msg.lower():
                stages["network_aggregator"]["status"] = "failed"
            elif stages["network_aggregator"]["status"] == "pending":
                stages["network_aggregator"]["status"] = "running"
                if not stages["network_aggregator"]["start_time"]:
                    stages["network_aggregator"]["start_time"] = event_time
            stages["network_aggregator"]["last_event"] = event_time

        # Schema validator
        if "schema_validator" in msg.lower() or "schema_validation" in msg.lower():
            if "complete" in msg.lower() or "passed" in msg.lower():
                stages["schema_validator"]["status"] = "complete"
                stages["schema_validator"]["status_msg"] = "passed"
                if duration_ms:
                    stages["schema_validator"]["duration_ms"] = duration_ms
            elif "failed" in msg.lower():
                stages["schema_validator"]["status"] = "failed"
                stages["schema_validator"]["status_msg"] = "failed"
            elif stages["schema_validator"]["status"] == "pending":
                stages["schema_validator"]["status"] = "running"
                if not stages["schema_validator"]["start_time"]:
                    stages["schema_validator"]["start_time"] = event_time
            stages["schema_validator"]["last_event"] = event_time

        # Analysis runner
        if "analysis_start" in msg:
            stages["analysis_runner"]["status"] = "running"
            stages["analysis_runner"]["operation"] = parsed.get("operation", "unknown")
            stages["analysis_runner"]["last_event"] = event_time
            if not stages["analysis_runner"]["start_time"]:
                stages["analysis_runner"]["start_time"] = event_time
        elif "analysis_complete" in msg:
            stages["analysis_runner"]["status"] = "complete"
            stages["analysis_runner"]["last_event"] = event_time
            if duration_ms:
                stages["analysis_runner"]["duration_ms"] = duration_ms
        elif "analysis_failed" in msg:
            stages["analysis_runner"]["status"] = "failed"
            stages["analysis_runner"]["last_event"] = event_time

    return {"stages": stages, "orchestrator": orchestrator_stage}, {"stages": stages}


def calculate_metrics(stage_status: Dict[str, Any], stage_timings: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate progress metrics and ETA for all stages."""
    stages = stage_status["stages"]
    metrics = {}

    # Calculate metrics for each stage
    for stage_name, stage_data in stages.items():
        count = stage_data.get("count", 0)
        total = stage_data.get("total", 0)

        stage_metrics = {
            "progress_pct": 0,
            "eta_minutes": None,
            "rate_per_sec": None,
            "batches_completed": 0,
        }

        # Calculate progress percentage if we have total
        if total > 0:
            progress_pct = round((count / total * 100), 1) if total > 0 else 0
            stage_metrics["progress_pct"] = progress_pct

        # For enrichment, calculate rate and ETA from batch processing
        if stage_name == "enrichment" and total > 0 and stage_data.get("status") == "running":
            batch_times = []
            batch_sizes = []

            # Try to get batch timing from metrics database first
            try:
                from src.infra.env_loader import ensure_env_loaded

                ensure_env_loaded()
                import psycopg

                dsn = os.getenv("GEMATRIA_DSN")
                if dsn:
                    with psycopg.connect(dsn) as conn:
                        with conn.cursor() as cur:
                            # Get last 10 batch_processed events for enrichment
                            cur.execute("""
                                SELECT items_in, duration_ms, started_at
                                FROM metrics_log
                                WHERE node = 'enrichment' 
                                  AND event = 'batch_processed'
                                  AND started_at >= NOW() - INTERVAL '1 hour'
                                  AND duration_ms IS NOT NULL
                                  AND duration_ms > 0
                                ORDER BY started_at DESC
                                LIMIT 10
                            """)
                            rows = cur.fetchall()
                            for row in rows:
                                items_in, duration_ms, _ = row
                                if duration_ms and duration_ms > 0:
                                    batch_times.append(float(duration_ms))
                                    if items_in and items_in > 0:
                                        batch_sizes.append(int(items_in))
            except Exception:
                # Fallback to log file parsing
                pass

            # Fallback: try to read from log files if database didn't work
            if not batch_times:
                # Check orchestrator log
                log_lines = scan_log_file(ORCHESTRATOR_LOG, max_lines=1000)
                # Also check enrichment-specific logs
                enrichment_logs = [
                    Path("/tmp/enrichment.log"),
                    Path("logs/enrichment.log"),
                    Path("logs/gemantria.enrichment.log"),
                ]
                for log_path in enrichment_logs:
                    if log_path.exists():
                        log_lines.extend(scan_log_file(log_path, max_lines=500))

                for line in reversed(log_lines[-500:]):
                    parsed = parse_log_line(line)
                    if parsed and parsed.get("event") == "batch_processed" and parsed.get("node") == "enrichment":
                        duration_ms = parsed.get("duration_ms", 0)
                        items_in = parsed.get("items_in", 0)
                        if duration_ms and duration_ms > 0:
                            batch_times.append(float(duration_ms))
                            if items_in and items_in > 0:
                                batch_sizes.append(int(items_in))

            # Calculate rate and ETA if we have batch timing data
            if batch_times and len(batch_times) >= 1:
                # Use last 5 batches for average (or all if less than 5)
                recent_times = batch_times[:5] if len(batch_times) >= 5 else batch_times
                avg_ms = sum(recent_times) / len(recent_times)

                # Calculate average batch size (default to 4 if not available)
                if batch_sizes:
                    recent_sizes = batch_sizes[:5] if len(batch_sizes) >= 5 else batch_sizes
                    avg_batch_size = sum(recent_sizes) / len(recent_sizes)
                else:
                    avg_batch_size = 4  # Default batch size

                # Calculate rate (nouns per second)
                rate = avg_batch_size / (avg_ms / 1000.0)
                stage_metrics["rate_per_sec"] = round(rate, 3)

                # Calculate ETA
                if total > count and rate > 0:
                    remaining = total - count
                    eta_sec = remaining / rate
                    stage_metrics["eta_minutes"] = round(eta_sec / 60, 1)

            stage_metrics["batches_completed"] = len(batch_times) if batch_times else 0

        # For other stages with count/total, estimate progress
        elif total > 0 and stage_data.get("status") == "running":
            # Use duration if available to estimate rate
            duration_ms = stage_data.get("duration_ms")
            if duration_ms and duration_ms > 0:
                elapsed_sec = duration_ms / 1000.0
                if elapsed_sec > 0:
                    rate = count / elapsed_sec
                    stage_metrics["rate_per_sec"] = round(rate, 2)
                    if total > count and rate > 0:
                        remaining = total - count
                        eta_sec = remaining / rate
                        stage_metrics["eta_minutes"] = round(eta_sec / 60, 1)

        metrics[stage_name] = stage_metrics

    return metrics


def format_progress_bar(progress_pct: float, width: int = 40) -> str:
    """Create a colored progress bar."""
    filled = int(width * progress_pct / 100)
    empty = width - filled

    # Color based on progress
    if progress_pct >= 100:
        color = Colors.BRIGHT_GREEN
    elif progress_pct >= 50:
        color = Colors.BRIGHT_YELLOW
    else:
        color = Colors.BRIGHT_CYAN

    bar = f"{color}{'█' * filled}{Colors.DIM}{'░' * empty}{Colors.RESET}"
    return f"[{bar}] {progress_pct:.1f}%"


def format_timestamp(ts: str | None) -> str:
    """Format timestamp for display."""
    if not ts:
        return "N/A"
    try:
        # Try to parse ISO format
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def format_duration(duration_ms: float | None) -> str:
    """Format duration in milliseconds to human-readable format."""
    if not duration_ms:
        return "N/A"
    seconds = duration_ms / 1000.0
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60.0
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60.0
    return f"{hours:.1f}h"


def get_terminal_width() -> int:
    """Get terminal width, defaulting to 80 if unavailable."""
    try:
        width, _ = shutil.get_terminal_size()
        return max(72, width)  # Minimum width of 72
    except Exception:
        return 80  # Default fallback


def format_box_line(title: str, width: int, color: str = Colors.CYAN) -> str:
    """Format a box line with title."""
    box_width = width - 4  # Account for ║ and spaces
    title_part = f"  {title}"
    padding = box_width - len(title_part)
    return f"{Colors.BOLD}{color}║{title_part}{' ' * padding}║{Colors.RESET}"


def format_box_edge(width: int, top: bool = True, color: str = Colors.CYAN) -> str:
    """Format box top/bottom edge."""
    edge_char = "╔" if top else "╚"
    opposite_char = "╗" if top else "╝"
    middle_char = "═"
    return f"{Colors.BOLD}{color}{edge_char}{middle_char * (width - 2)}{opposite_char}{Colors.RESET}"


def format_box_separator(width: int, color: str = Colors.CYAN) -> str:
    """Format box middle separator."""
    return f"{Colors.BOLD}{color}╠{'═' * (width - 2)}╣{Colors.RESET}"


def format_status_report(
    stage_status: Dict[str, Any],
    metrics: Dict[str, Any],
    process_stats: Dict[str, Any],
    gpu_stats: Dict[str, str | None],
    errors: List[Dict[str, Any]],
) -> str:
    """Format a human-readable status report with colors and formatting."""
    lines = []
    width = get_terminal_width()

    # Header with colors
    header_line = f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{'=' * width}{Colors.RESET}"
    lines.append(header_line)
    title = "🧭 Gemantria Pipeline Monitor - Comprehensive Status"
    padding = (width - len(title) - 2) // 2
    lines.append(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{' ' * padding}{title}{' ' * (width - len(title) - padding - 1)}{Colors.RESET}"
    )
    lines.append(header_line)
    lines.append(f"{Colors.DIM}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    lines.append("")

    # Error alert section (if errors exist)
    if errors:
        lines.append(format_box_edge(width, top=True, color=Colors.BRIGHT_RED))
        error_title = "⚠ ERRORS DETECTED"
        lines.append(format_box_line(error_title, width, color=Colors.BRIGHT_RED))
        lines.append(format_box_separator(width, color=Colors.BRIGHT_RED))
        for error in errors[-3:]:  # Show last 3 errors
            error_time = format_timestamp(error.get("time", ""))
            error_msg = error.get("error") or error.get("msg", "Unknown error")
            lines.append(
                f"  {Colors.BRIGHT_RED}✗{Colors.RESET} {Colors.DIM}[{error_time}]{Colors.RESET} {error_msg[:60]}"
            )
        lines.append(format_box_edge(width, top=False, color=Colors.BRIGHT_RED))
        lines.append("")

    # Orchestrator status
    orch = stage_status["orchestrator"]
    status = orch.get("status", "unknown").upper()
    status_color = {
        "RUNNING": Colors.BRIGHT_YELLOW,
        "COMPLETE": Colors.BRIGHT_GREEN,
        "FAILED": Colors.BRIGHT_RED,
        "ERROR": Colors.BRIGHT_RED,
    }.get(status, Colors.DIM)

    lines.append(format_box_edge(width, top=True, color=Colors.CYAN))
    lines.append(format_box_line("Orchestrator Status", width, color=Colors.CYAN))
    lines.append(format_box_separator(width, color=Colors.CYAN))
    lines.append(
        f"  {Colors.BOLD}Operation:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{orch.get('operation', 'N/A')}{Colors.RESET}"
    )
    lines.append(f"  {Colors.BOLD}Status:{Colors.RESET}    {status_color}{status}{Colors.RESET}")
    if orch.get("start_time"):
        lines.append(
            f"  {Colors.BOLD}Started:{Colors.RESET}   {Colors.DIM}{format_timestamp(orch['start_time'])}{Colors.RESET}"
        )
    if orch.get("last_event"):
        lines.append(
            f"  {Colors.BOLD}Last event:{Colors.RESET} {Colors.DIM}{format_timestamp(orch['last_event'])}{Colors.RESET}"
        )
    lines.append(format_box_edge(width, top=False, color=Colors.CYAN))
    lines.append("")

    # Pipeline stages
    lines.append(format_box_edge(width, top=True, color=Colors.CYAN))
    lines.append(format_box_line("Pipeline Stages", width, color=Colors.CYAN))
    lines.append(format_box_separator(width, color=Colors.CYAN))

    stages = stage_status["stages"]
    stage_order = [
        "collect_nouns",
        "validate_batch",
        "enrichment",
        "confidence_validator",
        "network_aggregator",
        "schema_validator",
        "analysis_runner",
    ]

    status_icons = {
        "RUNNING": f"{Colors.BRIGHT_YELLOW}▶{Colors.RESET}",
        "COMPLETE": f"{Colors.BRIGHT_GREEN}✓{Colors.RESET}",
        "FAILED": f"{Colors.BRIGHT_RED}✗{Colors.RESET}",
        "ERROR": f"{Colors.BRIGHT_RED}✗{Colors.RESET}",
        "PENDING": f"{Colors.DIM}○{Colors.RESET}",
    }

    status_colors = {
        "RUNNING": Colors.BRIGHT_YELLOW,
        "COMPLETE": Colors.BRIGHT_GREEN,
        "FAILED": Colors.BRIGHT_RED,
        "ERROR": Colors.BRIGHT_RED,
        "PENDING": Colors.DIM,
    }

    for i, stage_name in enumerate(stage_order):
        stage = stages.get(stage_name, {})
        status = stage.get("status", "pending").upper()
        icon = status_icons.get(status, "?")
        color = status_colors.get(status, Colors.RESET)
        display_name = stage_name.replace("_", " ").title()
        stage_metrics = metrics.get(stage_name, {})

        # Stage header
        lines.append(f"  {icon} {Colors.BOLD}{display_name}:{Colors.RESET} {color}{status}{Colors.RESET}")

        # Show progress for any stage with count/total
        count = stage.get("count", 0)
        total = stage.get("total", 0)

        # For stages without explicit total, try to infer from enrichment total
        if total == 0 and stage_name in ["collect_nouns", "validate_batch"]:
            enrichment_total = stages.get("enrichment", {}).get("total", 0)
            if enrichment_total > 0:
                total = enrichment_total
                # Update count if not set
                if count == 0 and status == "COMPLETE":
                    count = total

        if total > 0:
            progress_pct = stage_metrics.get("progress_pct", (count / total * 100) if total > 0 else 0)
            lines.append(
                f"      {Colors.BRIGHT_CYAN}Progress:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{count:,}{Colors.RESET} / {Colors.BRIGHT_MAGENTA}{total:,}{Colors.RESET} ({progress_pct:.1f}%)"
            )
            lines.append(f"      {format_progress_bar(progress_pct)}")

            # ETA and rate for running stages
            if status == "RUNNING":
                rate = stage_metrics.get("rate_per_sec")
                if rate:
                    unit = "nouns/sec" if stage_name == "enrichment" else "items/sec"
                    lines.append(
                        f"      {Colors.DIM}Rate:{Colors.RESET} {Colors.BRIGHT_CYAN}{rate:.3f}{Colors.RESET} {unit}"
                    )

                eta = stage_metrics.get("eta_minutes")
                if eta:
                    hours = int(eta // 60)
                    mins = int(eta % 60)
                    if hours > 0:
                        lines.append(
                            f"      {Colors.DIM}ETA:{Colors.RESET} {Colors.BRIGHT_YELLOW}~{hours}h {mins}m{Colors.RESET} ({eta:.1f} minutes)"
                        )
                    else:
                        lines.append(
                            f"      {Colors.DIM}ETA:{Colors.RESET} {Colors.BRIGHT_YELLOW}~{mins}m{Colors.RESET} ({eta:.1f} minutes)"
                        )
                elif total > count:
                    lines.append(f"      {Colors.DIM}ETA:{Colors.RESET} {Colors.DIM}Calculating...{Colors.RESET}")
        elif count > 0:
            lines.append(f"      {Colors.DIM}Count:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{count:,}{Colors.RESET}")

        # Last run timestamp
        if stage.get("last_event"):
            lines.append(
                f"      {Colors.DIM}Last run:{Colors.RESET} {Colors.DIM}{format_timestamp(stage['last_event'])}{Colors.RESET}"
            )

        # Duration if available
        if stage.get("duration_ms"):
            lines.append(
                f"      {Colors.DIM}Duration:{Colors.RESET} {Colors.BRIGHT_CYAN}{format_duration(stage['duration_ms'])}{Colors.RESET}"
            )

        if stage.get("operation"):
            lines.append(
                f"      {Colors.DIM}Operation:{Colors.RESET} {Colors.BRIGHT_CYAN}{stage['operation']}{Colors.RESET}"
            )
        if stage.get("status_msg"):
            msg_color = Colors.BRIGHT_GREEN if stage["status_msg"] == "passed" else Colors.BRIGHT_RED
            lines.append(f"      {Colors.DIM}Status:{Colors.RESET} {msg_color}{stage['status_msg']}{Colors.RESET}")

        if i < len(stage_order) - 1:
            lines.append(f"  {Colors.DIM}─{Colors.RESET}")

    lines.append(format_box_edge(width, top=False, color=Colors.CYAN))
    lines.append("")

    # System metrics
    lines.append(format_box_edge(width, top=True, color=Colors.CYAN))
    lines.append(format_box_line("System Metrics", width, color=Colors.CYAN))
    lines.append(format_box_separator(width, color=Colors.CYAN))

    # Process metrics
    lines.append(f"  {Colors.BOLD}Process:{Colors.RESET}")
    lines.append(
        f"    {Colors.DIM}Runtime:{Colors.RESET} {Colors.BRIGHT_CYAN}{process_stats.get('runtime', 'N/A')}{Colors.RESET}"
    )
    cpu_usage = process_stats.get("cpu_usage", "N/A")
    # Extract numeric CPU value for color coding (handle both simple and detailed formats)
    cpu_value = None
    if cpu_usage != "N/A":
        try:
            # Try to extract the first percentage value (current or average)
            import re

            match = re.search(r"(\d+\.?\d*)%", cpu_usage)
            if match:
                cpu_value = float(match.group(1))
        except (ValueError, AttributeError):
            pass
    cpu_color = Colors.BRIGHT_GREEN if cpu_value is not None and cpu_value < 10 else Colors.BRIGHT_YELLOW
    lines.append(f"    {Colors.DIM}CPU:{Colors.RESET}     {cpu_color}{cpu_usage}{Colors.RESET}")
    lines.append(
        f"    {Colors.DIM}Memory:{Colors.RESET}  {Colors.BRIGHT_CYAN}{process_stats.get('memory_usage', 'N/A')}{Colors.RESET}"
    )
    if process_stats.get("pid"):
        lines.append(
            f"    {Colors.DIM}PID:{Colors.RESET}      {Colors.BRIGHT_CYAN}{process_stats['pid']}{Colors.RESET}"
        )
    lines.append("")

    # GPU metrics
    gpu_util = gpu_stats.get("utilization", "N/A")
    gpu_color = Colors.BRIGHT_GREEN
    if gpu_util and gpu_util != "N/A":
        util_val = int(gpu_util.rstrip("%"))
        if util_val > 90:
            gpu_color = Colors.BRIGHT_YELLOW
        elif util_val < 50:
            gpu_color = Colors.BRIGHT_CYAN

    lines.append(f"  {Colors.BOLD}GPU:{Colors.RESET}")
    lines.append(f"    {Colors.DIM}Utilization:{Colors.RESET} {gpu_color}{gpu_util or 'N/A'}{Colors.RESET}")
    lines.append(
        f"    {Colors.DIM}Memory:{Colors.RESET}      {Colors.BRIGHT_MAGENTA}{gpu_stats.get('memory', 'N/A')}{Colors.RESET}"
    )
    gpu_temp = gpu_stats.get("temperature", "N/A")
    temp_color = Colors.BRIGHT_GREEN
    if gpu_temp and gpu_temp != "N/A":
        temp_val = int(gpu_temp.rstrip("°C"))
        if temp_val > 80:
            temp_color = Colors.BRIGHT_RED
        elif temp_val > 70:
            temp_color = Colors.BRIGHT_YELLOW
    lines.append(f"    {Colors.DIM}Temperature:{Colors.RESET} {temp_color}{gpu_temp or 'N/A'}{Colors.RESET}")

    lines.append(format_box_edge(width, top=False, color=Colors.CYAN))
    lines.append("")

    # Progress metrics summary (if any stage is running with batches)
    enrichment_metrics = metrics.get("enrichment", {})
    if enrichment_metrics.get("batches_completed", 0) > 0:
        lines.append(format_box_edge(width, top=True, color=Colors.CYAN))
        lines.append(format_box_line("Progress Summary", width, color=Colors.CYAN))
        lines.append(format_box_separator(width, color=Colors.CYAN))
        lines.append(
            f"  {Colors.DIM}Batches completed:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{enrichment_metrics.get('batches_completed', 0)}{Colors.RESET}"
        )
        if enrichment_metrics.get("rate_per_sec"):
            lines.append(
                f"  {Colors.DIM}Processing rate:{Colors.RESET} {Colors.BRIGHT_CYAN}{enrichment_metrics['rate_per_sec']:.3f}{Colors.RESET} nouns/sec"
            )
        lines.append(format_box_edge(width, top=False, color=Colors.CYAN))

    lines.append("")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")

    return "\n".join(lines)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using xclip (Linux) or pbcopy (macOS)."""
    try:
        if sys.platform == "darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
        else:
            proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text)
        return proc.returncode == 0
    except Exception:
        return False


def show_interactive_menu(status: Dict[str, Any], errors: List[Dict[str, Any]]) -> None:
    """Display interactive menu with quick actions."""
    width = get_terminal_width()
    menu_lines = []
    menu_lines.append(f"\n{format_box_edge(width, top=True, color=Colors.BRIGHT_CYAN)}")
    menu_lines.append(format_box_line("Quick Actions (Press number to activate)", width, color=Colors.BRIGHT_CYAN))
    menu_lines.append(format_box_separator(width, color=Colors.BRIGHT_CYAN))

    # Menu items with proper spacing
    menu_items = [
        ("1", "Run tests", "make test.unit"),
        ("2", "Run rules audit", "python3 scripts/rules_audit.py"),
        ("3", "Copy last error to clipboard", ""),
        ("4", "Show full error log", ""),
        ("5", "Show last run timestamps", ""),
        ("6", "Run share sync", "make share.sync"),
        ("7", "Show orchestrator log tail", "last 50 lines"),
        ("8", "Run ruff format check", ""),
        ("9", "Show system health", "DB + LM"),
        ("0", "Exit menu and continue monitoring", ""),
    ]

    for num, desc, detail in menu_items:
        if detail:
            line = f"  {Colors.BOLD}{num}.{Colors.RESET} {desc} ({Colors.DIM}{detail}{Colors.RESET})"
        else:
            line = f"  {Colors.BOLD}{num}.{Colors.RESET} {desc}"
        menu_lines.append(line)

    menu_lines.append(format_box_edge(width, top=False, color=Colors.BRIGHT_CYAN))
    menu_lines.append(f"\n{Colors.DIM}Press a number (0-9) or Enter to refresh:{Colors.RESET} ")

    print("\n".join(menu_lines), end="", flush=True)


def handle_menu_choice(choice: str, status: Dict[str, Any], errors: List[Dict[str, Any]]) -> bool:
    """Handle menu choice. Returns True if should continue monitoring, False to exit."""
    if choice == "1":
        print(f"\n{Colors.BRIGHT_YELLOW}Running tests...{Colors.RESET}\n")
        subprocess.run(["make", "test.unit"], check=False)
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "2":
        print(f"\n{Colors.BRIGHT_YELLOW}Running rules audit...{Colors.RESET}\n")
        subprocess.run(["python3", "scripts/rules_audit.py"], check=False)
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "3":
        if errors:
            last_error = errors[-1]
            error_text = last_error.get("error") or last_error.get("msg", "No error message")
            if copy_to_clipboard(error_text):
                print(f"\n{Colors.BRIGHT_GREEN}✓ Last error copied to clipboard!{Colors.RESET}")
            else:
                print(f"\n{Colors.BRIGHT_YELLOW}⚠ Clipboard not available. Error text:{Colors.RESET}\n{error_text}")
        else:
            print(f"\n{Colors.DIM}No errors found.{Colors.RESET}")
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "4":
        print(f"\n{Colors.BRIGHT_YELLOW}Last 10 errors:{Colors.RESET}\n")
        if errors:
            for i, error in enumerate(errors[-10:], 1):
                print(f"{Colors.BRIGHT_RED}[{i}] {format_timestamp(error.get('time'))}{Colors.RESET}")
                print(f"  {Colors.DIM}Level:{Colors.RESET} {error.get('level', 'N/A')}")
                print(f"  {Colors.DIM}Message:{Colors.RESET} {error.get('msg', 'N/A')}")
                if error.get("error"):
                    print(f"  {Colors.DIM}Error:{Colors.RESET} {error['error']}")
                print()
        else:
            print(f"{Colors.DIM}No errors found.{Colors.RESET}\n")
        print(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "5":
        print(f"\n{Colors.BRIGHT_YELLOW}Last run timestamps:{Colors.RESET}\n")
        orch = status["stage_status"]["orchestrator"]
        if orch.get("start_time"):
            print(f"  {Colors.BOLD}Orchestrator started:{Colors.RESET} {format_timestamp(orch['start_time'])}")
        if orch.get("last_event"):
            print(f"  {Colors.BOLD}Orchestrator last event:{Colors.RESET} {format_timestamp(orch['last_event'])}")
        print()
        for stage_name, stage_data in status["stage_status"]["stages"].items():
            if stage_data.get("last_event"):
                display_name = stage_name.replace("_", " ").title()
                print(f"  {Colors.BOLD}{display_name}:{Colors.RESET} {format_timestamp(stage_data['last_event'])}")
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "6":
        print(f"\n{Colors.BRIGHT_YELLOW}Running share sync...{Colors.RESET}\n")
        subprocess.run(["make", "share.sync"], check=False)
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "7":
        print(f"\n{Colors.BRIGHT_YELLOW}Last 50 lines of orchestrator log:{Colors.RESET}\n")
        if ORCHESTRATOR_LOG.exists():
            log_lines = scan_log_file(ORCHESTRATOR_LOG, max_lines=50)
            for line in log_lines:
                print(line.rstrip())
        else:
            print(f"{Colors.DIM}Log file not found.{Colors.RESET}")
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "8":
        print(f"\n{Colors.BRIGHT_YELLOW}Running ruff format check...{Colors.RESET}\n")
        subprocess.run(["ruff", "format", "--check", "."], check=False)
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "9":
        print(f"\n{Colors.BRIGHT_YELLOW}System health check:{Colors.RESET}\n")
        # Check DB
        try:
            result = subprocess.run(
                ["psql", os.environ.get("GEMATRIA_DSN", ""), "-c", "SELECT 1"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                print(f"  {Colors.BRIGHT_GREEN}✓ Database: Connected{Colors.RESET}")
            else:
                print(f"  {Colors.BRIGHT_RED}✗ Database: Connection failed{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.BRIGHT_RED}✗ Database: Error - {e}{Colors.RESET}")

        # Check LM Studio
        try:
            result = subprocess.run(
                ["python3", "scripts/lm_health_check.py"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"  {Colors.BRIGHT_GREEN}✓ LM Studio: Healthy{Colors.RESET}")
            else:
                print(f"  {Colors.BRIGHT_RED}✗ LM Studio: Unavailable{Colors.RESET}")
                print(f"  {Colors.DIM}Output: {result.stdout[:200]}{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.BRIGHT_RED}✗ LM Studio: Error - {e}{Colors.RESET}")

        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True
    elif choice == "0" or choice == "":
        return True
    else:
        return True  # Unknown choice, continue monitoring


def get_keypress(timeout: float = 0.1) -> str | None:
    """Get a single keypress without requiring Enter. Returns None if timeout."""
    if not sys.stdin.isatty():
        return None

    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if select.select([sys.stdin], [], [], timeout)[0]:
                ch = sys.stdin.read(1)
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        pass
    return None


def monitor_once(pid: int | None = None) -> Dict[str, Any]:
    """Run a single monitoring cycle."""
    # Check for active processes first
    if pid:
        try:
            import psutil

            proc = psutil.Process(pid)
            if not proc.is_running():
                pid = None
        except Exception:
            pass

    # Scan all log files - use larger limit for enrichment_start which is early in the log
    log_lines = []
    for log_path in [ORCHESTRATOR_LOG, PIPELINE_LOG, GRAPH_LOG]:
        if log_path.exists():
            # Read more lines for ORCHESTRATOR_LOG to find enrichment_start
            max_lines = 5000 if log_path == ORCHESTRATOR_LOG else 500
            log_lines.extend(scan_log_file(log_path, max_lines=max_lines))

    # Also check for enrichment-specific log files
    enrichment_logs = [
        Path("logs/enrichment.log"),
        Path("logs/gemantria.enrichment.log"),
    ]
    for log_path in enrichment_logs:
        if log_path.exists():
            log_lines.extend(scan_log_file(log_path, max_lines=1000))

    # Extract stage status and timings
    stage_status, stage_timings = extract_stage_status(log_lines)

    # Extract errors
    errors = extract_errors(log_lines)

    # Calculate metrics
    metrics = calculate_metrics(stage_status, stage_timings)

    # Get system stats
    process_stats = get_process_stats(pid)
    gpu_stats = get_gpu_stats()

    return {
        "stage_status": stage_status,
        "metrics": metrics,
        "process_stats": process_stats,
        "gpu_stats": gpu_stats,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Pipeline Monitor")
    parser.add_argument("--pid", type=int, help="Process ID to monitor")
    parser.add_argument("--watch", action="store_true", help="Watch mode (update every 10s)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--interactive", action="store_true", help="Interactive menu mode")
    args = parser.parse_args()

    if args.watch or args.interactive:
        # Try to focus/bring terminal to front (works in some terminals/IDEs)
        try:
            # Send ANSI escape sequence to request terminal focus
            sys.stdout.write("\033]51;A\007")  # Request terminal focus
            sys.stdout.flush()
        except Exception:
            pass

        # Clear screen on first run
        os.system("clear" if os.name != "nt" else "cls")

        mode = "Interactive Menu Mode" if args.interactive else "Watch Mode"
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}🧭 Gemantria Pipeline Monitor - {mode}{Colors.RESET}")
        print(f"{Colors.DIM}Press Ctrl+C to stop{Colors.RESET}")
        print("")
        iteration = 0
        try:
            while True:
                iteration += 1
                status = monitor_once(args.pid)

                if args.json:
                    print(json.dumps(status, indent=2, default=str))
                else:
                    # Clear previous output (move cursor up)
                    if iteration > 1:
                        print(f"\033[{80}A")  # Move up 80 lines for more space

                    print(
                        format_status_report(
                            status["stage_status"],
                            status["metrics"],
                            status["process_stats"],
                            status["gpu_stats"],
                            status["errors"],
                        )
                    )

                    if args.interactive:
                        show_interactive_menu(status, status["errors"])
                        # Wait for keypress with timeout
                        key = get_keypress(timeout=10.0)
                        if key:
                            if key == "\x03":  # Ctrl+C
                                raise KeyboardInterrupt
                            if not handle_menu_choice(key, status, status["errors"]):
                                break
                    else:
                        print(f"\n{Colors.DIM}🔄 Next update in 10 seconds... (Iteration #{iteration}){Colors.RESET}")
                        time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.BRIGHT_YELLOW}Monitoring stopped.{Colors.RESET}")
    else:
        # Single run
        status = monitor_once(args.pid)
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print(
                format_status_report(
                    status["stage_status"],
                    status["metrics"],
                    status["process_stats"],
                    status["gpu_stats"],
                    status["errors"],
                )
            )


if __name__ == "__main__":
    main()
