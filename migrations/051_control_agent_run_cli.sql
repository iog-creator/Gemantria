-- Migration 051: Agent Run CLI Tracking
-- Purpose: Track pmagent CLI command executions for audit and monitoring
-- Related: pmagent v2 implementation, Orchestrator Shell Autopilot integration
-- Note: This is separate from control.agent_run (guarded tool calls) - this tracks CLI commands

CREATE TABLE IF NOT EXISTS control.agent_run_cli (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    command text NOT NULL,
    status text NOT NULL,
    request_json jsonb,
    response_json jsonb,
    error_text text
);

CREATE INDEX IF NOT EXISTS idx_agent_run_cli_created_at ON control.agent_run_cli (created_at);
CREATE INDEX IF NOT EXISTS idx_agent_run_cli_command ON control.agent_run_cli (command);
CREATE INDEX IF NOT EXISTS idx_agent_run_cli_status ON control.agent_run_cli (status);

COMMENT ON TABLE control.agent_run_cli IS 'Tracks pmagent CLI command executions for audit and monitoring';
COMMENT ON COLUMN control.agent_run_cli.id IS 'Unique identifier (UUID)';
COMMENT ON COLUMN control.agent_run_cli.created_at IS 'When the command was started';
COMMENT ON COLUMN control.agent_run_cli.updated_at IS 'When the command status was last updated';
COMMENT ON COLUMN control.agent_run_cli.command IS 'Command name (e.g., "system.health", "bible.retrieve")';
COMMENT ON COLUMN control.agent_run_cli.status IS 'Status: "started", "success", "error"';
COMMENT ON COLUMN control.agent_run_cli.request_json IS 'Request parameters as JSON';
COMMENT ON COLUMN control.agent_run_cli.response_json IS 'Response data as JSON (on success)';
COMMENT ON COLUMN control.agent_run_cli.error_text IS 'Error message (on error)';

