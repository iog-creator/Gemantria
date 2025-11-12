from typing import Dict, Any


def build_capability_session(project_id: int, task_id: str, intent: str) -> Dict[str, Any]:
    por_token = f"por-{task_id[:8]}" if task_id else None
    return {
        "project_id": project_id,
        "task_id": task_id,
        "intent": intent,
        "allowed_tool_ids": [],  # set by orchestrator/plan; tests override explicitly
        "checklist_json": [{"item": "por_echo", "required": por_token is not None}],
        "por_status": {"ok": False, "token": por_token},
    }
