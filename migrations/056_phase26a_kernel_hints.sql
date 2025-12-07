-- Phase 26.A: Kernel-First Boot Hints
-- Purpose: Insert three REQUIRED hints to enforce kernel-first boot for PM, OA, and OPS
-- Context: Phase 26 Handoff Kernel implementation
-- Related: PHASE26_HANDOFF_KERNEL.md, PM_HANDOFF_PROTOCOL.md, EXECUTION_CONTRACT.md

BEGIN;

-- Hint 1: pm.boot.kernel_first
INSERT INTO control.hint_registry (
    logical_name,
    scope,
    applies_to,
    kind,
    injection_mode,
    payload,
    enabled,
    priority
) VALUES (
    'pm.boot.kernel_first',
    'pm',
    '{"flow": "handoff.pm_boot", "agent": "pm", "rule": "026"}'::jsonb,
    'REQUIRED',
    'PRE_PROMPT',
    '{
        "text": "New PM chat must *first* read `share/handoff/PM_KERNEL.json`, then `share/PM_BOOTSTRAP_STATE.json`, and only then phase docs. If kernel and bootstrap disagree, or `health.reality_green=false`, PM must enter degraded mode and halt phase work.",
        "commands": ["cat share/handoff/PM_KERNEL.json", "cat share/PM_BOOTSTRAP_STATE.json"],
        "constraints": {
            "kernel_bootstrap_agreement": true,
            "reality_green_required": true,
            "degraded_mode_on_mismatch": true
        },
        "metadata": {
            "docs_refs": [
                "docs/SSOT/PM_HANDOFF_PROTOCOL.md",
                "docs/SSOT/SHARE_FOLDER_ANALYSIS.md",
                "docs/SSOT/PHASE26_HANDOFF_KERNEL.md"
            ],
            "severity": "ERROR",
            "description": "Force PM boot sequence to obey Phase-25/26 rules"
        }
    }'::jsonb,
    true,
    0
) ON CONFLICT (logical_name) DO UPDATE SET
    payload = EXCLUDED.payload,
    updated_at = NOW();

-- Hint 2: oa.boot.kernel_first
INSERT INTO control.hint_registry (
    logical_name,
    scope,
    applies_to,
    kind,
    injection_mode,
    payload,
    enabled,
    priority
) VALUES (
    'oa.boot.kernel_first',
    'orchestrator_assistant',
    '{"flow": "handoff.oa_boot", "agent": "oa", "rule": "026"}'::jsonb,
    'REQUIRED',
    'PRE_PROMPT',
    '{
        "text": "On new OA session, read `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json` before reasoning. Never infer phase or health from prior chats. If the kernel indicates degraded health, OA must warn PM and refuse normal analytical work until remediation scope is defined.",
        "commands": ["cat share/handoff/PM_KERNEL.json", "cat share/PM_BOOTSTRAP_STATE.json"],
        "constraints": {
            "kernel_required": true,
            "no_phase_inference": true,
            "escalate_degraded_health": true
        },
        "metadata": {
            "docs_refs": [
                "docs/SSOT/PM_HANDOFF_PROTOCOL.md",
                "docs/SSOT/SHARE_FOLDER_ANALYSIS.md"
            ],
            "severity": "ERROR",
            "description": "Force Orchestrator Assistant to treat kernel as authority and escalate degraded health"
        }
    }'::jsonb,
    true,
    0
) ON CONFLICT (logical_name) DO UPDATE SET
    payload = EXCLUDED.payload,
    updated_at = NOW();

-- Hint 3: ops.preflight.kernel_health
INSERT INTO control.hint_registry (
    logical_name,
    scope,
    applies_to,
    kind,
    injection_mode,
    payload,
    enabled,
    priority
) VALUES (
    'ops.preflight.kernel_health',
    'ops',
    '{"flow": "ops.preflight", "agent": "cursor", "rule": "026"}'::jsonb,
    'REQUIRED',
    'PRE_PROMPT',
    '{
        "text": "Before any destructive operation (deleting or regenerating share surfaces, schema changes, bulk writes), load `PM_KERNEL.json`, verify branch/phase match, ensure backup is recent, and check DMS alignment, share sync, and bootstrap consistency. If any guard fails, restrict scope to remediation only.",
        "commands": [
            "cat share/handoff/PM_KERNEL.json",
            "git rev-parse --abbrev-ref HEAD",
            "make reality.green"
        ],
        "constraints": {
            "kernel_branch_match": true,
            "guards_green_required": true,
            "remediation_only_if_degraded": true
        },
        "metadata": {
            "docs_refs": [
                "docs/SSOT/EXECUTION_CONTRACT.md",
                "docs/SSOT/PM_HANDOFF_PROTOCOL.md",
                "docs/SSOT/SHARE_FOLDER_ANALYSIS.md",
                "docs/SSOT/PHASE26_HANDOFF_KERNEL.md"
            ],
            "severity": "ERROR",
            "description": "Force Cursor/OPS to run kernel-aware preflight before destructive operations"
        }
    }'::jsonb,
    true,
    0
) ON CONFLICT (logical_name) DO UPDATE SET
    payload = EXCLUDED.payload,
    updated_at = NOW();

COMMIT;
