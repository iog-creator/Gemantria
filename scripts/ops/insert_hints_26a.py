from sqlalchemy import text
from pmagent.db.loader import get_control_engine


def insert_hints():
    print("Connecting to DB using pmagent.db.loader...")
    try:
        engine = get_control_engine()
    except Exception as e:
        print(f"Failed to get control engine: {e}")
        return

    # 1. Inspect Schema
    print("\n--- Schema of control.hint_registry ---")
    try:
        with engine.connect() as conn:
            # Simple query to get column names if possible, or just trust the insert
            result = conn.execute(text("SELECT * FROM control.hint_registry LIMIT 0"))
            print(f"Columns: {result.keys()}")
    except Exception as e:
        print(f"Error inspecting schema: {e}")
        return

    # 2. Define Hints
    hints = [
        {
            "id": "pm.boot.kernel_first",
            "scope": "pm",
            "required": True,
            "severity": "ERROR",
            "description": "New PM chat must first read share/handoff/PM_KERNEL.json, then share/PM_BOOTSTRAP_STATE.json, and only then phase docs. If kernel and bootstrap disagree, or health.reality_green=false, PM must enter degraded mode and halt phase work.",
            "docs_refs": [
                "docs/SSOT/PM_HANDOFF_PROTOCOL.md",
                "docs/SSOT/SHARE_FOLDER_ANALYSIS.md",
                "docs/SSOT/PHASE26_HANDOFF_KERNEL.md",
            ],
        },
        {
            "id": "oa.boot.kernel_first",
            "scope": "orchestrator_assistant",
            "required": True,
            "severity": "ERROR",
            "description": "On new OA session, read PM_KERNEL.json and PM_BOOTSTRAP_STATE.json before reasoning. Never infer phase or health from prior chats. If the kernel indicates degraded health, OA must warn PM and refuse normal analytical work until remediation scope is defined.",
            "docs_refs": ["docs/SSOT/PM_HANDOFF_PROTOCOL.md", "docs/SSOT/SHARE_FOLDER_ANALYSIS.md"],
        },
        {
            "id": "ops.preflight.kernel_health",
            "scope": "ops",
            "required": True,
            "severity": "ERROR",
            "description": "Before any destructive operation (deleting or regenerating share surfaces, schema changes, bulk writes), load PM_KERNEL.json, verify branch/phase match, ensure backup is recent, and check DMS alignment, share sync, and bootstrap consistency. If any guard fails, restrict scope to remediation only.",
            "docs_refs": [
                "docs/SSOT/EXECUTION_CONTRACT.md",
                "docs/SSOT/PM_HANDOFF_PROTOCOL.md",
                "docs/SSOT/SHARE_FOLDER_ANALYSIS.md",
                "docs/SSOT/PHASE26_HANDOFF_KERNEL.md",
            ],
        },
    ]

    # 3. Insert Hints
    print("\n--- Inserting Hints ---")
    with engine.begin() as conn:
        for h in hints:
            # Use upsert (ON CONFLICT DO UPDATE)
            stmt = text("""
                INSERT INTO control.hint_registry (id, scope, required, severity, description, docs_refs)
                VALUES (:id, :scope, :required, :severity, :description, :docs_refs)
                ON CONFLICT (id) DO UPDATE SET
                    scope = EXCLUDED.scope,
                    required = EXCLUDED.required,
                    severity = EXCLUDED.severity,
                    description = EXCLUDED.description,
                    docs_refs = EXCLUDED.docs_refs;
            """)
            # Convert string list to JSON if strictly needed, or let psycopg adapter handle specific type.
            # Assuming docs_refs is JSONB or TEXT[] based on context.
            # If it's TEXT[], we pass a list. If JSONB, we might need json.dumps.
            # Let's try passing list first (sqlalchemy/psycopg usually handles array/json conversion).
            # Actually, `docs_refs` usually maps to a JSONB column in modern setups here.
            import json

            h_params = h.copy()
            h_params["docs_refs"] = json.dumps(h["docs_refs"])

            conn.execute(stmt, h_params)
            print(f"Upserted: {h['id']}")

    print("\nSUCCESS: Hints initialized.")


if __name__ == "__main__":
    insert_hints()
