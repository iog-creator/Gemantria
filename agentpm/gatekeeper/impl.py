from typing import Dict, Any
from agentpm.guard.impl import guarded_call_p0


def build_capability_session(project_id: int, task_id: str, intent: str) -> Dict[str, Any]:
    por_token = f"por-{task_id[:8]}" if task_id else None
    return {
        "project_id": project_id,
        "task_id": task_id,
        "intent": intent,
        "allowed_tool_ids": [],  # set by orchestrator/plan; tests override explicitly
        "checklist_json": [{"item": "por_echo", "required": por_token is not None}],
        "por_status": {"ok": False, "token": por_token},
        "por_token": por_token,  # For P0 PoR validation
    }


def execute_guarded_tool_call_p0(
    tool_id: str, args: Dict[str, Any], session: Dict[str, Any]
) -> Dict[str, Any]:
    """
    PLAN-091 P0 execution: coordinate guard validation + tool execution.
    Returns structured result suitable for recording in control.agent_run.
    """
    # Apply P0 validations and get result
    result = guarded_call_p0(tool_id, args, session)

    # In STRICT/tag lanes, this would execute the actual tool
    # For now, return validation result only (hermetic)
    result["executed"] = len(result["violations"]) == 0

    return result
