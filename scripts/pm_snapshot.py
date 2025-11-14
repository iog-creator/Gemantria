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

# Write document
doc_path.write_text("\n".join(lines) + "\n")

# Write DB health JSON to evidence directory
db_health_evid = evid_dir / "db_health.json"
db_health_evid.write_text(json.dumps(db_health_json, indent=2) + "\n")

# Emit machine-friendly evidence
print("EVID: DOC_PATH", doc_path.as_posix())
print("EVID: MANIFEST_COUNT", len(items))
print("EVID: BIBLE_DSN_REDACT", redact(BIBLE_DB_DSN))
print("EVID: GEMATRIA_DSN_REDACT", redact(GEMATRIA_DSN))
print("EVID: DB_HEALTH_OK", db_health_json.get("ok", False))
print("EVID: DB_HEALTH_MODE", db_health_json.get("mode", "unknown"))
