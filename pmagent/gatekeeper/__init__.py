# Gatekeeper (stub P0): builds capability_session & issues PoR checklist
from typing import Dict, Any


def build_capability_session(project_id: int, task_id: str, intent: str) -> Dict[str, Any]:
    """Return session with allowed_tool_ids, checklist_json, por_status."""
    return {
        "project_id": project_id,
        "task_id": task_id,
        "allowed_tool_ids": [],
        "checklist_json": [],
        "por_status": {"ok": False},
    }
