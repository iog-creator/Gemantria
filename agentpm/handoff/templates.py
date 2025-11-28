#!/usr/bin/env python3
"""
Handoff Templates - Markdown rendering logic for handoff documents.

This module provides rendering functions for converting handoff_context
into human-readable Markdown documents.
"""

from __future__ import annotations

from typing import Any


def render_markdown(handoff_context: dict[str, Any]) -> str:
    """
    Render handoff_context as Markdown.

    Args:
        handoff_context: handoff_context dictionary

    Returns:
        Markdown string
    """
    handoff_type = handoff_context.get("handoff_type", "session")

    if handoff_type == "session":
        return render_session_markdown(handoff_context)
    elif handoff_type == "task":
        return render_task_markdown(handoff_context)
    elif handoff_type == "role":
        return render_role_markdown(handoff_context)
    elif handoff_type == "system-state":
        return render_system_state_json(handoff_context)
    else:
        return f"# Handoff Document\n\nUnknown handoff type: {handoff_type}\n"


def render_session_markdown(context: dict[str, Any]) -> str:
    """
    Render session handoff as Markdown.

    Args:
        context: handoff_context dictionary

    Returns:
        Markdown string
    """
    lines = [
        "# Session Handoff",
        "",
        f"**Generated**: {context.get('generated_at', 'Unknown')}",
        f"**Project**: {context.get('project', 'gemantria')}",
        "",
        "## Work Summary",
        "",
    ]

    work = context.get("work", {})
    if work.get("items"):
        for item in work["items"]:
            status_icon = "✅" if item.get("status") == "complete" else "🔄"
            lines.append(f"- {status_icon} **{item.get('description', 'Unknown')}**")
            if item.get("files_changed"):
                lines.append(f"  - Files: {', '.join(item.get('files_changed', [])[:5])}")
    else:
        lines.append("No recent work items found.")

    lines.extend(
        [
            "",
            "## Verification Status",
            "",
        ]
    )

    verification = context.get("verification", {})
    hermetic = verification.get("hermetic", {})
    live = verification.get("live", {})
    lm_slots = verification.get("lm_slots", {})

    lines.append(f"- **Format**: {'✅' if hermetic.get('format_ok') else '❌'}")
    lines.append(f"- **Lint**: {'✅' if hermetic.get('lint_ok') else '❌'}")
    lines.append(f"- **Tests**: {'✅' if hermetic.get('tests_ok') else '❌'}")
    lines.append(f"- **DB Health**: {live.get('db_health', 'unknown')}")
    lines.append(f"- **LM Health**: {live.get('lm_health', 'unknown')}")

    if lm_slots and isinstance(lm_slots, dict):
        slots_list = lm_slots.get("slots", [])
        if slots_list:
            lines.append("")
            lines.append("### LM Slots")
            for slot_info in slots_list:
                if not isinstance(slot_info, dict):
                    continue
                slot_name = slot_info.get("slot", "unknown")
                model = slot_info.get("model", "unknown")
                provider = slot_info.get("provider", "unknown")
                service_status = slot_info.get("service_status", "unknown")
                lines.append(f"- **{slot_name}**: {service_status} ({model} via {provider})")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
        ]
    )

    next_steps = context.get("next_steps", [])
    if next_steps:
        for step in next_steps:
            if step is None:
                continue
            title = step.get("title", "Unknown step")
            priority = step.get("priority", "normal")
            source = step.get("source", "unknown")
            lines.append(f"- **{title}** (priority: {priority}, source: {source})")
    else:
        lines.append("No next steps defined.")

    lines.extend(
        [
            "",
            "## Recent Agent Activity",
            "",
        ]
    )

    agent_runs = context.get("agent_runs", {})
    summary = agent_runs.get("summary", {})
    lines.append(f"- **Total runs**: {summary.get('total', 0)}")
    lines.append(f"- **Last 24h**: {summary.get('last_24h', 0)}")
    lines.append(f"- **Errors**: {summary.get('errors', 0)}")

    return "\n".join(lines)


def render_task_markdown(context: dict[str, Any]) -> str:
    """
    Render task handoff as Markdown.

    Args:
        context: handoff_context dictionary

    Returns:
        Markdown string
    """
    lines = [
        "# Task Handoff",
        "",
        f"**Scope ID**: {context.get('scope_id', 'Unknown')}",
        f"**Generated**: {context.get('generated_at', 'Unknown')}",
        f"**Project**: {context.get('project', 'gemantria')}",
        "",
        "## Task Context",
        "",
    ]

    work = context.get("work", {})
    capability_sessions = work.get("capability_sessions", [])
    if capability_sessions:
        lines.append(f"**Capability Sessions**: {len(capability_sessions)}")
        for session in capability_sessions[:5]:
            session_id = session.get("id", "unknown")
            status = session.get("status", "unknown")
            lines.append(f"- `{session_id}`: {status}")
    else:
        lines.append("No capability sessions found for this scope.")

    lines.extend(
        [
            "",
            "## Recent Work",
            "",
        ]
    )

    work_items = work.get("items", [])
    if work_items:
        for item in work_items:
            status_icon = "✅" if item.get("status") == "complete" else "🔄"
            lines.append(f"- {status_icon} **{item.get('description', 'Unknown')}**")
            if item.get("files_changed"):
                lines.append(f"  - Files: {', '.join(item.get('files_changed', [])[:5])}")
    else:
        lines.append("No recent work items found.")

    lines.extend(
        [
            "",
            "## Verification Status",
            "",
        ]
    )

    verification = context.get("verification", {})
    hermetic = verification.get("hermetic", {})
    live = verification.get("live", {})

    lines.append(f"- **Format**: {'✅' if hermetic.get('format_ok') else '❌'}")
    lines.append(f"- **Lint**: {'✅' if hermetic.get('lint_ok') else '❌'}")
    lines.append(f"- **DB Health**: {live.get('db_health', 'unknown')}")
    lines.append(f"- **LM Health**: {live.get('lm_health', 'unknown')}")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
        ]
    )

    next_steps = context.get("next_steps", [])
    if next_steps:
        for step in next_steps:
            if step is None:
                continue
            title = step.get("title", "Unknown step")
            priority = step.get("priority", "normal")
            source = step.get("source", "unknown")
            lines.append(f"- **{title}** (priority: {priority}, source: {source})")
    else:
        lines.append("No next steps defined.")

    return "\n".join(lines)


def render_role_markdown(context: dict[str, Any]) -> str:
    """
    Render role handoff as Markdown (Orchestrator executive summary).

    Args:
        context: handoff_context dictionary

    Returns:
        Markdown string
    """
    role = context.get("role") or "orchestrator"
    lines = [
        f"# Role Handoff: {role.title() if isinstance(role, str) else str(role).title()}",
        "",
        f"**Generated**: {context.get('generated_at', 'Unknown')}",
        f"**Project**: {context.get('project', 'gemantria')}",
        "**Source**: Postgres/DMS (on-demand)",
        "",
        "## Executive Summary",
        "",
    ]

    verification = context.get("verification", {})
    live = verification.get("live", {})
    db_health = live.get("db_health", "unknown")
    lm_health = live.get("lm_health", "unknown")

    # Overall system status
    if db_health == "ready" and lm_health in ("lm_ready", "healthy"):
        status_icon = "✅"
        status_text = "System Operational"
    elif db_health == "db_off" or lm_health == "lm_off":
        status_icon = "⚠️"
        status_text = "Partial Service (DB or LM offline)"
    else:
        status_icon = "❌"
        status_text = "System Degraded"

    lines.append(f"{status_icon} **System Status**: {status_text}")
    lines.append(f"- **DB**: {db_health}")
    lines.append(f"- **LM**: {lm_health}")

    # Agent activity summary
    agent_runs = context.get("agent_runs", {})
    summary = agent_runs.get("summary", {})
    total_runs = summary.get("total", 0)
    last_24h = summary.get("last_24h", 0)
    errors = summary.get("errors", 0)

    lines.extend(
        [
            "",
            "## Recent Activity",
            "",
            f"- **Total Agent Runs**: {total_runs}",
            f"- **Last 24 Hours**: {last_24h}",
            f"- **Errors**: {errors}",
        ]
    )

    by_tool = summary.get("by_tool", {})
    if by_tool:
        lines.append("")
        lines.append("### Activity by Tool")
        for tool, count in sorted(by_tool.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"- **{tool}**: {count}")

    # Recent work
    lines.extend(
        [
            "",
            "## Recent Work",
            "",
        ]
    )

    work = context.get("work", {})
    work_items = work.get("items", [])
    if work_items:
        for item in work_items[:10]:
            status_icon = "✅" if item.get("status") == "complete" else "🔄"
            description = item.get("description", "Unknown")
            lines.append(f"- {status_icon} **{description}**")
    else:
        lines.append("No recent work items found.")

    # Next steps
    lines.extend(
        [
            "",
            "## Next Steps",
            "",
        ]
    )

    next_steps = context.get("next_steps", [])
    if next_steps:
        for step in next_steps[:10]:
            if step is None:
                continue
            title = step.get("title", "Unknown step")
            priority = step.get("priority", "normal")
            source = step.get("source", "unknown")
            # Check if title indicates completion (starts with [x])
            if isinstance(title, str) and title.startswith("[x]"):
                status_icon = "✅"
                title = title.replace("[x]", "").strip()
            else:
                status_icon = "⏳"
            lines.append(f"- {status_icon} **{title}** (priority: {priority}, source: {source})")
    else:
        lines.append("No next steps defined.")

    # Blockers/Issues
    lines.extend(
        [
            "",
            "## Blockers & Issues",
            "",
        ]
    )

    if errors > 0:
        lines.append(f"⚠️ **{errors} agent run errors** detected in last 24 hours")
        recent_runs = agent_runs.get("recent", [])
        error_runs = [r for r in recent_runs if r.get("status") == "error"][:5]
        if error_runs:
            lines.append("")
            lines.append("### Recent Errors")
            for run in error_runs:
                tool = run.get("tool", "unknown")
                error_msg = run.get("error", "Unknown error")
                lines.append(f"- **{tool}**: {error_msg[:100]}")
    else:
        lines.append("✅ No blockers detected.")

    # Verification details
    lines.extend(
        [
            "",
            "## Verification Details",
            "",
        ]
    )

    hermetic = verification.get("hermetic", {})
    lines.append(f"- **Format Check**: {'✅' if hermetic.get('format_ok') else '❌'}")
    lines.append(f"- **Lint Check**: {'✅' if hermetic.get('lint_ok') else '❌'}")
    lines.append(f"- **Tests**: {'✅' if hermetic.get('tests_ok') else '❌'}")

    lm_slots = verification.get("lm_slots", {})
    if lm_slots and isinstance(lm_slots, dict):
        slots_list = lm_slots.get("slots", [])
        if slots_list:
            lines.append("")
            lines.append("### LM Slots Status")
            for slot_info in slots_list:
                if not isinstance(slot_info, dict):
                    continue
                slot_name = slot_info.get("slot", "unknown")
                model = slot_info.get("model", "unknown")
                provider = slot_info.get("provider", "unknown")
                service_status = slot_info.get("service_status", "unknown")
                status_icon = "✅" if service_status == "OK" else "⚠️" if service_status == "degraded" else "❌"
                lines.append(f"- {status_icon} **{slot_name}**: {service_status} ({model} via {provider})")

    # Relevant context
    lines.extend(
        [
            "",
            "## Relevant Context",
            "",
        ]
    )

    docs = context.get("docs", [])
    if docs:
        for doc in docs[:10]:
            doc_name = doc.get("logical_name", "Unknown")
            doc_type = doc.get("doc_type", "unknown")
            lines.append(f"- **{doc_name}** ({doc_type})")
    else:
        lines.append("No relevant documents found.")

    return "\n".join(lines)


def render_system_state_json(context: dict[str, Any]) -> str:
    """
    Render system-state handoff as JSON (not Markdown).

    Args:
        context: handoff_context dictionary

    Returns:
        JSON string
    """
    import json

    return json.dumps(context, indent=2)
