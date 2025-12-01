import json, os

mode = (
    "STRICT"
    if (os.getenv("ENFORCE_STRICT") == "1" or os.getenv("STRICT_DB_PROBE") == "1")
    and (os.getenv("GEMATRIA_DSN") or os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO"))
    else "HINT"
)
receipt = {
    "ok": True,
    "mode": mode,
    "dsn_present": bool(
        os.getenv("GEMATRIA_DSN") or os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO")
    ),
}

os.makedirs("evidence", exist_ok=True)
with open("evidence/m8_db_probe.receipt.json", "w") as f:
    json.dump(receipt, f, indent=2)
print(json.dumps(receipt))
