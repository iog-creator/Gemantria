import re, json, subprocess, datetime, pathlib, sys

# Add project root to path for imports (works when run from Makefile with PYTHONPATH=. or directly)
root = pathlib.Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Use centralized DSN loaders (handles .env loading and precedence chains)
from scripts.config.env import get_rw_dsn, get_bible_db_dsn, env

share_dir = root / "share"
doc_path = share_dir / "pm.snapshot.md"
manifest_path = root / "docs" / "SSOT" / "SHARE_MANIFEST.json"
evid_dir = root / "evidence" / "pm_snapshot"
evid_dir.mkdir(parents=True, exist_ok=True)


def redact(dsn: str) -> str:
    if not dsn:
        return "(unset)"
    # Simplistic but safe redaction: keep scheme and database name only.
    # Examples:
    #  postgresql://mccoy@/gematria?host=/var/run/postgresql  -> postgresql://<REDACTED>/gematria
    m = re.match(r"^([a-zA-Z0-9+.-]+)://.*?/(.*?)(?:[?].*)?$", dsn)
    if m:
        return f"{m.group(1)}://<REDACTED>/{m.group(2)}"
    # Fallback
    return "<REDACTED-DSN>"


def run(cmd: list[str], env=None) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    out, err = p.communicate()
    # Filter Cursor IDE integration noise (orchestrator-friendly output)
    err = "\n".join(line for line in err.split("\n") if "dump_bash_state: command not found" not in line)
    return p.returncode, out.strip(), err.strip()


now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# Use centralized loaders (handles .env loading, precedence chains, fallbacks)
# get_bible_db_dsn() now includes BIBLE_DB_DSN in precedence chain
BIBLE_DB_DSN = get_bible_db_dsn() or ""
GEMATRIA_DSN = get_rw_dsn() or ""
CHECKPOINTER = env("CHECKPOINTER", "")
ENFORCE_STRICT = env("ENFORCE_STRICT", "")

# DSN posture probes (best-effort; skip if unset)
ro_probe = "(skipped: BIBLE_DB_DSN unset)"
if BIBLE_DB_DSN:
    rc, out, err = run(
        [
            "psql",
            BIBLE_DB_DSN,
            "-v",
            "ON_ERROR_STOP=1",
            "-Atc",
            "select current_database(), current_user;",
        ]
    )
    ro_probe = out if rc == 0 else f"(RO probe failed) {err}"

rw_probe = "(skipped: GEMATRIA_DSN unset)"
if GEMATRIA_DSN:
    sql = "begin; create temporary table __pm_rw_probe(x int); insert into __pm_rw_probe values (1); rollback;"
    rc, out, err = run(["psql", GEMATRIA_DSN, "-v", "ON_ERROR_STOP=1", "-Atc", sql])
    rw_probe = "ok" if rc == 0 else f"(RW probe failed) {err}"

# Gather guards summary if present
guards_out = "(no guards run yet)"
gfile = root / "evidence" / "bringup_001" / "guards.out"
if gfile.exists():
    guards_out = gfile.read_text(errors="ignore")[:2000]

# Run DB health guard and embed JSON
db_health_json = {}
try:
    from scripts.guards.guard_db_health import check_db_health

    db_health_json = check_db_health()
except Exception as e:
    db_health_json = {
        "ok": False,
        "mode": "error",
        "error": f"guard_db_health failed: {e}",
    }

# Use unified snapshot helper (AgentPM-First:M3)
try:
    from agentpm.status.snapshot import get_system_snapshot

    snapshot = get_system_snapshot(
        include_reality_check=True,
        include_ai_tracking=True,
        include_share_manifest=True,
        include_eval_insights=True,  # Include eval exports summary (M4)
        include_kb_registry=True,  # Include KB registry summary (KB-Reg:M2)
        include_kb_doc_health=True,  # Include KB doc-health metrics (AgentPM-Next:M3)
        reality_check_mode="HINT",  # HINT mode for snapshot speed
        use_lm_for_explain=False,  # Skip LM for snapshot speed
    )

    # Extract components from snapshot
    system_health_json = snapshot.get("system_health", {})
    status_explain_json = snapshot.get("status_explain", {})
    reality_check_json = snapshot.get("reality_check", {})
    ai_tracking_summary = snapshot.get("ai_tracking", {})
    share_manifest_summary = snapshot.get("share_manifest", {})
    eval_insights_summary = snapshot.get("eval_insights", {})
    kb_registry_summary = snapshot.get("kb_registry", {})
    kb_hints = snapshot.get("kb_hints", [])  # KB-Reg:M4
    kb_doc_health_summary = snapshot.get("kb_doc_health", {})  # AgentPM-Next:M3
except Exception as e:
    # Fallback to individual calls if unified helper fails
    # Gather system health (DB + LM + Graph)
    system_health_json = {}
    try:
        from agentpm.tools.system import health as tool_health

        system_health_json = tool_health()
    except Exception as e2:
        system_health_json = {
            "ok": False,
            "error": f"system_health failed: {e2}",
            "db": db_health_json,
            "lm": {"ok": False, "mode": "error"},
            "graph": {"ok": False, "mode": "error"},
        }

    # Gather status explanation
    status_explain_json = {}
    try:
        from agentpm.status.explain import explain_system_status

        status_explain_json = explain_system_status(use_lm=False)  # Skip LM for snapshot speed
    except Exception as e2:
        status_explain_json = {
            "level": "ERROR",
            "headline": "Status explanation unavailable",
            "details": f"Failed to generate explanation: {e2}",
        }

    # Gather reality-check verdict (HINT mode for snapshot)
    reality_check_json = {}
    try:
        from agentpm.reality.check import reality_check

        reality_check_json = reality_check(mode="HINT", skip_dashboards=False)
    except Exception as e2:
        reality_check_json = {
            "command": "reality.check",
            "mode": "HINT",
            "overall_ok": False,
            "error": f"reality_check failed: {e2}",
        }

    # Gather AI tracking summary (control.agent_run and control.agent_run_cli)
    ai_tracking_summary = {"ok": False, "mode": "db_off", "summary": {}}
    try:
        from agentpm.status.snapshot import get_ai_tracking_summary

        ai_tracking_summary = get_ai_tracking_summary()
    except Exception as e2:
        ai_tracking_summary = {
            "ok": False,
            "mode": "db_off",
            "error": f"AI tracking failed: {e2}",
        }

    # Gather share manifest summary
    share_manifest_summary = {"ok": False, "count": 0, "items": []}
    try:
        from agentpm.status.snapshot import get_share_manifest_summary

        share_manifest_summary = get_share_manifest_summary(manifest_path)
    except Exception as e2:
        share_manifest_summary = {
            "ok": False,
            "error": f"Failed to read manifest: {e2}",
        }

    # Gather KB registry summary (advisory-only, non-gating)
    kb_registry_summary = {
        "available": False,
        "total": 0,
        "valid": False,
        "errors_count": 0,
        "warnings_count": 0,
    }
    kb_hints = []  # KB-Reg:M4
    kb_doc_health_summary = {}  # AgentPM-Next:M3
    try:
        from agentpm.status.snapshot import (
            get_kb_registry_summary,
            get_kb_status_view,
            get_kb_hints,
        )

        kb_registry_summary = get_kb_registry_summary()
        # Generate KB hints
        try:
            kb_status_view = get_kb_status_view()
            kb_hints = get_kb_hints(kb_status_view)
        except Exception:
            pass  # KB hints are advisory-only; ignore errors
    except Exception as e2:
        kb_registry_summary = {
            "available": False,
            "total": 0,
            "valid": False,
            "errors_count": 0,
            "warnings_count": 0,
            "note": f"KB registry unavailable: {e2}",
        }
        kb_hints = []

# Update SHARE_MANIFEST.json: add this file if missing
try:
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, dict):
        raise ValueError("manifest not a dict")
    items = manifest.get("items", [])
except Exception:
    manifest = {"items": []}
    items = []

entry = {"src": "share/pm.snapshot.md", "dst": "share/pm.snapshot.md"}

# ensure unique by dst path
items = [e for e in items if e.get("dst") != entry["dst"]] + [entry]
manifest["items"] = items
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

# Determine overall_ok from components
overall_ok = (
    db_health_json.get("ok", False)
    and system_health_json.get("ok", False)
    and reality_check_json.get("overall_ok", False)
)

# Compose PM Snapshot (Markdown)
lines = []
lines.append("# PM Snapshot — GemantriaV.2\n")
lines.append(f"_Generated: {now_iso}_\n")
lines.append("## Posture (DSNs + STRICT flags)\n")
lines.append(f"- BIBLE_DB_DSN: `{redact(BIBLE_DB_DSN)}`")
lines.append(f"- GEMATRIA_DSN: `{redact(GEMATRIA_DSN)}`")
lines.append(f"- CHECKPOINTER: `{CHECKPOINTER or '(unset)'}`  — expected `postgres` in STRICT")
lines.append(f"- ENFORCE_STRICT: `{ENFORCE_STRICT or '(unset)'}`  — expected `1` in STRICT\n")
lines.append("### DB Proofs\n")
lines.append(f"- Bible RO probe: `{ro_probe}`")
lines.append(f"- Gematria RW temp-write probe: `{rw_probe}`\n")
lines.append("### DB Health Guard\n")
lines.append(f"- Status: `{'✓ Ready' if db_health_json.get('ok') else '✗ ' + db_health_json.get('mode', 'unknown')}`")
lines.append(f"- Mode: `{db_health_json.get('mode', 'unknown')}`")
if db_health_json.get("checks"):
    checks = db_health_json["checks"]
    lines.append(f"- Driver available: `{'✓' if checks.get('driver_available') else '✗'}`")
    lines.append(f"- Connection OK: `{'✓' if checks.get('connection_ok') else '✗'}`")
    lines.append(f"- Graph stats ready: `{'✓' if checks.get('graph_stats_ready') else '✗'}`")
if db_health_json.get("details", {}).get("errors"):
    lines.append(f"- Errors: `{len(db_health_json['details']['errors'])} error(s)`")
lines.append("")
lines.append("```json")
lines.append(json.dumps(db_health_json, indent=2))
lines.append("```\n")
lines.append("## Now / Next / Later (PM-facing)\n")
lines.append(
    "**Now**\n- Keep GemantriaV.2 as the active project.\n- Use `STRICT` posture when DSNs present; otherwise HINT mode is allowed for hermetic tests.\n- Regenerate this PM Snapshot on each bring-up or DSN change (`make pm.snapshot`).\n"
)
lines.append(
    "**Next**\n- Ensure `share/` always contains the canonical 25 files (see Manifest section).\n- Add the `Pilot-001 (VL Validator)` checklist when bring-up is green.\n"
)
lines.append(
    "**Later**\n- Attach Atlas/CI proofs to this snapshot (screenshots + JSON tails) once Web proof targets are finalized.\n"
)
lines.append("## Evidence links\n")

if gfile.exists():
    lines.append("- Guards summary: `evidence/bringup_001/guards.out`\n")
else:
    lines.append("- Guards summary: (bring-up not yet run in this session)\n")

lines.append("## Manifest status\n")
share_ok = share_manifest_summary.get("ok", False)
share_count = share_manifest_summary.get("count", 0)
lines.append(f"- Status: `{'✓ OK' if share_ok else '✗ Error'}`")
lines.append(f"- File count: `{share_count}`")
if not share_ok:
    lines.append(f"- Error: {share_manifest_summary.get('error', 'Unknown error')}")
lines.append("")

# Build comprehensive JSON snapshot
snapshot_json = {
    "generated_at": now_iso,
    "overall_ok": overall_ok,
    "db_mode": db_health_json.get("mode", "unknown"),
    "lm_mode": system_health_json.get("lm", {}).get("mode", "unknown"),
    "posture": {
        "bible_db_dsn": redact(BIBLE_DB_DSN),
        "gematria_dsn": redact(GEMATRIA_DSN),
        "checkpointer": CHECKPOINTER or "(unset)",
        "enforce_strict": ENFORCE_STRICT or "(unset)",
        "ro_probe": ro_probe,
        "rw_probe": rw_probe,
    },
    "db_health": db_health_json,
    "system_health": system_health_json,
    "status_explain": status_explain_json,
    "reality_check": reality_check_json,
    "ai_tracking": ai_tracking_summary,
    "share_manifest": share_manifest_summary,
    "eval_insights": eval_insights_summary,
    "kb_registry": kb_registry_summary,
    "kb_hints": kb_hints,  # KB-Reg:M4
    "kb_doc_health": kb_doc_health_summary,  # AgentPM-Next:M3
}

# Write comprehensive JSON snapshot to evidence directory
snapshot_json_path = evid_dir / "snapshot.json"
snapshot_json_path.write_text(json.dumps(snapshot_json, indent=2) + "\n")

# Enhance Markdown with new sections
lines.append("## System Health (DB + LM + Graph)\n")
lm_health = system_health_json.get("lm", {})
lm_mode = lm_health.get("mode", "unknown")
lm_ok = lm_health.get("ok", False)
lines.append(f"- LM Status: `{'✓ Ready' if lm_ok else '✗ ' + lm_mode}`")
lines.append(f"- LM Mode: `{lm_mode}`")
graph_health = system_health_json.get("graph", {})
graph_mode = graph_health.get("mode", "unknown")
graph_ok = graph_health.get("ok", False)
lines.append(f"- Graph Status: `{'✓ Ready' if graph_ok else '✗ ' + graph_mode}`")
lines.append(f"- Graph Mode: `{graph_mode}`\n")

lines.append("## Status Explanation\n")
lines.append(f"- Level: `{status_explain_json.get('level', 'UNKNOWN')}`")
lines.append(f"- Headline: {status_explain_json.get('headline', 'N/A')}")
lines.append(f"- Details: {status_explain_json.get('details', 'N/A')[:200]}...\n")

lines.append("## Reality Check\n")
rc_ok = reality_check_json.get("overall_ok", False)
rc_mode = reality_check_json.get("mode", "unknown")
lines.append(f"- Overall: `{'✓ OK' if rc_ok else '✗ FAILED'}`")
lines.append(f"- Mode: `{rc_mode}`")
rc_hints = reality_check_json.get("hints", [])
if rc_hints:
    lines.append(f"- Hints: {len(rc_hints)} hint(s)")
    for hint in rc_hints[:5]:  # First 5 hints
        lines.append(f"  - {hint}")
lines.append("")

lines.append("## AI Tracking Summary\n")
ai_ok = ai_tracking_summary.get("ok", False)
ai_mode = ai_tracking_summary.get("mode", "unknown")
lines.append(f"- Status: `{'✓ Active' if ai_ok else '✗ ' + ai_mode}`")
lines.append(f"- Mode: `{ai_mode}`")
if ai_ok:
    summary = ai_tracking_summary.get("summary", {})
    agent_run = summary.get("agent_run", {})
    agent_run_cli = summary.get("agent_run_cli", {})
    lines.append(
        f"- Runtime LM calls (agent_run): {agent_run.get('total', 0)} total, {agent_run.get('last_24h', 0)} last 24h"
    )
    lines.append(
        f"- CLI commands (agent_run_cli): {agent_run_cli.get('total', 0)} total, {agent_run_cli.get('last_24h', 0)} last 24h, {agent_run_cli.get('success_count', 0)} success, {agent_run_cli.get('error_count', 0)} errors"
    )
else:
    lines.append(
        f"- Note: {ai_tracking_summary.get('note', ai_tracking_summary.get('error', 'AI tracking unavailable'))}"
    )
lines.append("")

lines.append("## Eval Insights Summary (Advisory Analytics)\n")
lines.append(
    "_Note: Eval insights are export-driven analytics (Phase-8/10) and are advisory only. They do not affect system health gates._\n"
)
eval_lm = eval_insights_summary.get("lm_indicator", {})
eval_db = eval_insights_summary.get("db_health", {})
eval_edges = eval_insights_summary.get("edge_class_counts", {})
lines.append(f"- LM Indicator: `{'✓ Available' if eval_lm.get('available') else '✗ Unavailable'}`")
if eval_lm.get("available"):
    lm_data = eval_lm.get("data", {})
    lines.append(f"  - Status: {lm_data.get('status', 'unknown')}")
    lines.append(f"  - Success rate: {lm_data.get('success_rate', 0):.1%}")
else:
    lines.append(f"  - Note: {eval_lm.get('note', 'LM indicator export not found')}")
lines.append(f"- DB Health Snapshot: `{'✓ Available' if eval_db.get('available') else '✗ Unavailable'}`")
if eval_db.get("available"):
    db_data = eval_db.get("data", {})
    lines.append(f"  - Mode: {db_data.get('mode', 'unknown')}")
else:
    lines.append(f"  - Note: {eval_db.get('note', 'DB health export not found')}")
lines.append(f"- Edge Class Counts: `{'✓ Available' if eval_edges.get('available') else '✗ Unavailable'}`")
if eval_edges.get("available"):
    edge_data = eval_edges.get("data", {})
    counts = edge_data.get("counts", {})
    lines.append(
        f"  - Strong: {counts.get('strong', 0)}, Weak: {counts.get('weak', 0)}, Other: {counts.get('other', 0)}"
    )
else:
    lines.append(f"  - Note: {eval_edges.get('note', 'Edge class counts export not found')}")
lines.append("")

lines.append("## KB Registry Summary (Advisory)\n")
lines.append("_Note: KB registry is advisory-only and read-only in CI. It does not affect system health gates._\n")
kb_available = kb_registry_summary.get("available", False)
kb_total = kb_registry_summary.get("total", 0)
kb_valid = kb_registry_summary.get("valid", False)
kb_errors = kb_registry_summary.get("errors_count", 0)
kb_warnings = kb_registry_summary.get("warnings_count", 0)
lines.append(f"- Status: `{'✓ Available' if kb_available else '✗ Unavailable'}`")
if kb_available:
    lines.append(f"- Total documents: `{kb_total}`")
    lines.append(f"- Valid: `{'✓ Yes' if kb_valid else '✗ No'}`")
    if kb_errors > 0:
        lines.append(f"- Errors: `{kb_errors} error(s)`")
    if kb_warnings > 0:
        lines.append(f"- Warnings: `{kb_warnings} warning(s)`")
else:
    lines.append(f"- Note: {kb_registry_summary.get('note', 'KB registry file not found')}")
lines.append("")

# KB Hints (KB-Reg:M4)
lines.append("## KB Hints (Advisory)\n")
lines.append("_Note: KB hints are advisory-only and do not affect system health gates._\n")
if kb_hints:
    for hint in kb_hints:
        level = hint.get("level", "INFO")
        code = hint.get("code", "KB_UNKNOWN")
        message = hint.get("message", "")
        level_icon = "WARN" if level == "WARN" else "INFO"
        lines.append(f"- {level_icon} **[{level}] {code}**: {message}")
        # Add additional context if present
        if "missing_count" in hint:
            lines.append(f"  - Missing files: {hint['missing_count']}")
        if "subsystem" in hint and "have" in hint:
            lines.append(f"  - Subsystem: {hint['subsystem']}, Current docs: {hint['have']}")
else:
    lines.append("- ✓ No KB registry issues detected")
lines.append("")

# Documentation Health (AgentPM-Next:M3)
lines.append("## Documentation Health (Advisory)\n")
lines.append("_Note: Documentation health metrics are advisory-only and do not affect system health gates._\n")
kb_doc_available = kb_doc_health_summary.get("available", False)
if kb_doc_available:
    metrics = kb_doc_health_summary.get("metrics", {})
    fresh_ratio = metrics.get("kb_fresh_ratio", {})
    missing_count = metrics.get("kb_missing_count", {})
    stale_by_sub = metrics.get("kb_stale_count_by_subsystem", {})
    fixes_7d = metrics.get("kb_fixes_applied_last_7d", 0)
    notes = metrics.get("notes", [])

    overall_fresh = fresh_ratio.get("overall")
    if overall_fresh is not None:
        lines.append(f"- Overall freshness: `{overall_fresh:.1f}%`")
    else:
        lines.append("- Overall freshness: `unknown`")

    by_sub = fresh_ratio.get("by_subsystem", {})
    if by_sub:
        lines.append("  - By subsystem:")
        for subsystem, ratio in sorted(by_sub.items()):
            miss_sub = missing_count.get("by_subsystem", {}).get(subsystem, 0)
            stale_sub = stale_by_sub.get(subsystem, 0)
            lines.append(f"    - {subsystem}: {ratio:.1f}% fresh (missing={miss_sub}, stale={stale_sub})")

    missing_overall = missing_count.get("overall", 0)
    if missing_overall > 0:
        lines.append(f"- Missing documents: `{missing_overall}`")
    else:
        lines.append("- Missing documents: `0`")

    lines.append(f"- Fixes applied (last 7 days): `{fixes_7d}`")

    if notes:
        lines.append("  - Notes:")
        for note in notes[:5]:  # Limit to first 5 notes
            lines.append(f"    - {note}")
else:
    error_msg = kb_doc_health_summary.get("error", "KB doc-health metrics unavailable")
    lines.append("- Status: `✗ Unavailable`")
    lines.append(f"- Note: {error_msg}")
lines.append("")


# Write document
doc_path.write_text("\n".join(lines) + "\n")

# Write DB health JSON to evidence directory (keep for backward compatibility)
db_health_evid = evid_dir / "db_health.json"
db_health_evid.write_text(json.dumps(db_health_json, indent=2) + "\n")

# Emit machine-friendly evidence
print("EVID: DOC_PATH", doc_path.as_posix())
print("EVID: JSON_PATH", snapshot_json_path.as_posix())
print("EVID: MANIFEST_COUNT", len(items))
print("EVID: BIBLE_DSN_REDACT", redact(BIBLE_DB_DSN))
print("EVID: GEMATRIA_DSN_REDACT", redact(GEMATRIA_DSN))
print("EVID: DB_HEALTH_OK", db_health_json.get("ok", False))
print("EVID: DB_HEALTH_MODE", db_health_json.get("mode", "unknown"))
print("EVID: OVERALL_OK", overall_ok)
print("EVID: LM_MODE", lm_mode)
print("EVID: REALITY_CHECK_OK", rc_ok)
print("EVID: AI_TRACKING_MODE", ai_mode)
