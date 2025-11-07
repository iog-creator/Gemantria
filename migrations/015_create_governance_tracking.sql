-- Migration: 015_create_governance_tracking.sql
-- Purpose: Create governance artifacts tracking database per Rule-058 Auto-Housekeeping
-- Related Rules: Rule-026 (System Enforcement Bridge), Rule-058 (Auto-Housekeeping)

CREATE TABLE IF NOT EXISTS governance_artifacts (
    id SERIAL PRIMARY KEY,
    artifact_type VARCHAR(50) NOT NULL, -- 'rule', 'agent_file', 'hint_emission', 'metadata_reference'
    artifact_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    rule_references TEXT[], -- Array of MDC rule numbers that govern this artifact
    agent_references TEXT[], -- Array of agent file references
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(64), -- SHA-256 of the artifact content
    validation_status VARCHAR(20) DEFAULT 'pending', -- 'valid', 'invalid', 'pending'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (artifact_type, artifact_name) -- For ON CONFLICT support
);

-- Index for fast rule lookups
CREATE INDEX IF NOT EXISTS idx_governance_rule_refs ON governance_artifacts USING GIN (rule_references);
CREATE INDEX IF NOT EXISTS idx_governance_agent_refs ON governance_artifacts USING GIN (agent_references);
CREATE INDEX IF NOT EXISTS idx_governance_type ON governance_artifacts (artifact_type);

-- Table for tracking hint emissions during runtime
CREATE TABLE IF NOT EXISTS hint_emissions (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100),
    hint_text TEXT NOT NULL,
    rule_reference VARCHAR(10),
    agent_reference VARCHAR(255),
    emission_context VARCHAR(100), -- 'pipeline', 'validation', 'ci', etc.
    emitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    process_id INTEGER,
    hostname VARCHAR(100)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_hint_emissions_run_id ON hint_emissions (run_id);
CREATE INDEX IF NOT EXISTS idx_hint_emissions_rule ON hint_emissions (rule_reference);

-- Table for governance compliance history
CREATE TABLE IF NOT EXISTS governance_compliance_log (
    id SERIAL PRIMARY KEY,
    check_type VARCHAR(50) NOT NULL, -- 'rules_guard', 'hints_validation', 'metadata_audit'
    check_result VARCHAR(20) NOT NULL, -- 'pass', 'fail'
    details JSONB, -- Structured details about the check
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_time_ms INTEGER,
    triggered_by VARCHAR(100) -- 'ci', 'pre-commit', 'manual', etc.
);

-- Function to update governance artifacts (called by housekeeping)
CREATE OR REPLACE FUNCTION update_governance_artifact(
    p_artifact_type VARCHAR(50),
    p_artifact_name VARCHAR(255),
    p_file_path VARCHAR(500),
    p_rule_refs TEXT[],
    p_agent_refs TEXT[],
    p_checksum VARCHAR(64)
) RETURNS VOID AS $$
BEGIN
    INSERT INTO governance_artifacts (
        artifact_type, artifact_name, file_path,
        rule_references, agent_references, checksum,
        validation_status, updated_at
    ) VALUES (
        p_artifact_type, p_artifact_name, p_file_path,
        p_rule_refs, p_agent_refs, p_checksum,
        'valid', NOW()
    )
    ON CONFLICT (artifact_type, artifact_name)
    DO UPDATE SET
        rule_references = EXCLUDED.rule_references,
        agent_references = EXCLUDED.agent_references,
        checksum = EXCLUDED.checksum,
        validation_status = 'valid',
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to log hint emission
CREATE OR REPLACE FUNCTION log_hint_emission(
    p_run_id VARCHAR(100),
    p_hint_text TEXT,
    p_rule_ref VARCHAR(10),
    p_agent_ref VARCHAR(255),
    p_context VARCHAR(100)
) RETURNS VOID AS $$
BEGIN
    INSERT INTO hint_emissions (
        run_id, hint_text, rule_reference, agent_reference, emission_context
    ) VALUES (
        p_run_id, p_hint_text, p_rule_ref, p_agent_ref, p_context
    );
END;
$$ LANGUAGE plpgsql;

-- Function to check if governance is stale (for Rule-058 compliance)
CREATE OR REPLACE FUNCTION check_governance_freshness(hours_threshold INTEGER DEFAULT 24)
RETURNS TABLE (
    artifact_name VARCHAR(255),
    hours_since_update NUMERIC,
    is_stale BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ga.artifact_name,
        EXTRACT(EPOCH FROM (NOW() - ga.updated_at)) / 3600 as hours_since_update,
        (EXTRACT(EPOCH FROM (NOW() - ga.updated_at)) / 3600 > hours_threshold) as is_stale
    FROM governance_artifacts ga
    WHERE ga.artifact_type IN ('rule', 'agent_file')
    ORDER BY ga.updated_at ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE governance_artifacts IS 'Tracks all governance artifacts and their rule/agent linkages per Rule-026/058';
COMMENT ON TABLE hint_emissions IS 'Runtime log of LOUD HINT emissions for audit trails';
COMMENT ON TABLE governance_compliance_log IS 'History of governance compliance checks for Rule-058 housekeeping';
