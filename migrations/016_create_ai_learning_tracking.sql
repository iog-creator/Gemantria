-- Migration: 016_create_ai_learning_tracking.sql
-- Purpose: Create comprehensive AI learning and interaction tracking database.
-- Features: AI interaction patterns, code generation analytics, user feedback, context awareness
-- Related Rules: Rule-026 (System Enforcement Bridge), Rule-058 (Auto-Housekeeping)

-- ===============================
-- AI INTERACTION TRACKING
-- ===============================

CREATE TABLE IF NOT EXISTS ai_interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- 'user_query', 'tool_call', 'code_generation', 'validation'
    user_query TEXT,
    ai_response TEXT,
    tools_used TEXT[], -- Array of tool names used
    context_provided JSONB, -- Files open, recent edits, cursor position, etc.
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track tool usage patterns and success rates
CREATE TABLE IF NOT EXISTS tool_usage_analytics (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    average_execution_time_ms NUMERIC,
    last_used TIMESTAMP WITH TIME ZONE,
    error_patterns JSONB, -- Common error types and frequencies
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================
-- CODE GENERATION TRACKING
-- ===============================

CREATE TABLE IF NOT EXISTS code_generation_events (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    generation_type VARCHAR(50) NOT NULL, -- 'function', 'class', 'test', 'migration', 'config'
    target_file VARCHAR(500),
    generated_code TEXT,
    code_complexity_score INTEGER, -- Lines of code, cyclomatic complexity
    generation_context JSONB, -- Requirements, constraints, examples provided
    acceptance_status VARCHAR(20) DEFAULT 'pending', -- 'accepted', 'rejected', 'modified'
    modifications_made TEXT,
    time_to_accept_minutes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track code generation patterns and success rates
CREATE TABLE IF NOT EXISTS code_generation_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(100) NOT NULL, -- 'error_handling', 'async_function', 'validation', 'migration'
    pattern_template TEXT,
    usage_count INTEGER DEFAULT 0,
    success_rate NUMERIC DEFAULT 0.0,
    average_complexity INTEGER,
    common_modifications TEXT[],
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================
-- USER FEEDBACK & SATISFACTION
-- ===============================

CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    interaction_id INTEGER REFERENCES ai_interactions(id),
    feedback_type VARCHAR(50) NOT NULL, -- 'satisfaction', 'accuracy', 'completeness', 'usability'
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    suggested_improvements TEXT,
    context_tags TEXT[], -- 'pipeline', 'testing', 'documentation', 'debugging', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track user satisfaction trends over time
CREATE TABLE IF NOT EXISTS satisfaction_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    average_rating NUMERIC(3,2),
    total_interactions INTEGER DEFAULT 0,
    satisfaction_distribution JSONB, -- {1: count, 2: count, 3: count, 4: count, 5: count}
    top_feedback_themes TEXT[],
    improvement_suggestions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(metric_date)
);

-- ===============================
-- CONTEXT AWARENESS & MEMORY
-- ===============================

CREATE TABLE IF NOT EXISTS context_awareness_events (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    context_type VARCHAR(50) NOT NULL, -- 'file_open', 'cursor_position', 'recent_edit', 'error_state'
    context_data JSONB, -- Detailed context information
    relevance_score NUMERIC(3,2), -- How relevant this context was to the solution
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track what context patterns lead to successful outcomes
CREATE TABLE IF NOT EXISTS context_success_patterns (
    id SERIAL PRIMARY KEY,
    context_pattern JSONB, -- Pattern of context types and data
    success_rate NUMERIC(3,2),
    usage_count INTEGER DEFAULT 0,
    outcome_type VARCHAR(50), -- 'accepted', 'modified', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================
-- LEARNING & IMPROVEMENT TRACKING
-- ===============================

CREATE TABLE IF NOT EXISTS learning_events (
    id SERIAL PRIMARY KEY,
    learning_type VARCHAR(50) NOT NULL, -- 'error_recovery', 'pattern_recognition', 'tool_adaptation'
    trigger_event JSONB, -- What triggered the learning
    learning_outcome TEXT,
    confidence_score NUMERIC(3,2),
    applied_successfully BOOLEAN,
    improvement_metrics JSONB, -- Before/after metrics
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track AI model preferences and performance
CREATE TABLE IF NOT EXISTS model_performance_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'code_generation', 'analysis', 'validation', 'documentation'
    performance_score NUMERIC(3,2), -- 0.0 to 1.0
    execution_time_ms INTEGER,
    token_usage INTEGER,
    quality_rating NUMERIC(3,2),
    context_provided JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================
-- ANALYTICS & INSIGHTS
-- ===============================

CREATE TABLE IF NOT EXISTS ai_performance_insights (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL, -- 'pattern', 'improvement', 'trend', 'anomaly'
    insight_title VARCHAR(200) NOT NULL,
    insight_description TEXT,
    supporting_data JSONB,
    confidence_level NUMERIC(3,2),
    actionable BOOLEAN DEFAULT true,
    implemented BOOLEAN DEFAULT false,
    implementation_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================
-- INDEXES FOR PERFORMANCE
-- ===============================

-- AI Interactions
CREATE INDEX IF NOT EXISTS idx_ai_interactions_session ON ai_interactions (session_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_type ON ai_interactions (interaction_type);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created ON ai_interactions (created_at);

-- Tool Usage
CREATE INDEX IF NOT EXISTS idx_tool_usage_name ON tool_usage_analytics (tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_usage_updated ON tool_usage_analytics (updated_at);

-- Code Generation
CREATE INDEX IF NOT EXISTS idx_code_gen_session ON code_generation_events (session_id);
CREATE INDEX IF NOT EXISTS idx_code_gen_type ON code_generation_events (generation_type);
CREATE INDEX IF NOT EXISTS idx_code_gen_status ON code_generation_events (acceptance_status);

-- User Feedback
CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback (feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON user_feedback (rating);
CREATE INDEX IF NOT EXISTS idx_feedback_tags ON user_feedback USING GIN (context_tags);

-- Learning Events
CREATE INDEX IF NOT EXISTS idx_learning_type ON learning_events (learning_type);
CREATE INDEX IF NOT EXISTS idx_learning_success ON learning_events (applied_successfully);

-- ===============================
-- UTILITY FUNCTIONS
-- ===============================

-- Function to log AI interaction
CREATE OR REPLACE FUNCTION log_ai_interaction(
    p_session_id VARCHAR(100),
    p_type VARCHAR(50),
    p_query TEXT DEFAULT NULL,
    p_response TEXT DEFAULT NULL,
    p_tools TEXT[] DEFAULT NULL,
    p_context JSONB DEFAULT NULL,
    p_exec_time INTEGER DEFAULT NULL,
    p_success BOOLEAN DEFAULT true,
    p_error TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO ai_interactions (
        session_id, interaction_type, user_query, ai_response,
        tools_used, context_provided, execution_time_ms, success, error_details
    ) VALUES (
        p_session_id, p_type, p_query, p_response, p_tools, p_context,
        p_exec_time, p_success, p_error
    );
END;
$$ LANGUAGE plpgsql;

-- Function to update tool usage analytics
CREATE OR REPLACE FUNCTION update_tool_usage(
    p_tool_name VARCHAR(100),
    p_success BOOLEAN,
    p_exec_time INTEGER DEFAULT NULL,
    p_error_type VARCHAR(100) DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Insert or update tool usage record
    INSERT INTO tool_usage_analytics (tool_name, usage_count, success_count, last_used)
    VALUES (p_tool_name, 1, CASE WHEN p_success THEN 1 ELSE 0 END, NOW())
    ON CONFLICT (tool_name) DO UPDATE SET
        usage_count = tool_usage_analytics.usage_count + 1,
        success_count = tool_usage_analytics.success_count + CASE WHEN p_success THEN 1 ELSE 0 END,
        last_used = NOW(),
        average_execution_time_ms = CASE
            WHEN tool_usage_analytics.average_execution_time_ms IS NULL THEN p_exec_time
            ELSE (tool_usage_analytics.average_execution_time_ms + p_exec_time) / 2
        END,
        error_patterns = CASE
            WHEN p_error_type IS NOT NULL THEN
                jsonb_set(
                    COALESCE(tool_usage_analytics.error_patterns, '{}'::jsonb),
                    ARRAY[p_error_type],
                    (COALESCE(tool_usage_analytics.error_patterns->>p_error_type, '0')::integer + 1)::text::jsonb
                )
            ELSE tool_usage_analytics.error_patterns
        END,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to log user feedback
CREATE OR REPLACE FUNCTION log_user_feedback(
    p_session_id VARCHAR(100),
    p_feedback_type VARCHAR(50),
    p_rating INTEGER,
    p_feedback TEXT DEFAULT NULL,
    p_suggestions TEXT DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO user_feedback (
        session_id, feedback_type, rating, feedback_text,
        suggested_improvements, context_tags
    ) VALUES (
        p_session_id, p_feedback_type, p_rating, p_feedback,
        p_suggestions, p_tags
    );
END;
$$ LANGUAGE plpgsql;

-- Function to generate daily satisfaction metrics
CREATE OR REPLACE FUNCTION generate_daily_satisfaction_metrics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    avg_rating NUMERIC(3,2);
    total_count INTEGER;
    distribution JSONB;
    themes TEXT[];
    suggestions TEXT[];
BEGIN
    -- Calculate metrics for the target date
    SELECT
        AVG(rating)::NUMERIC(3,2),
        COUNT(*),
        jsonb_object_agg(rating::text, cnt)
    INTO avg_rating, total_count, distribution
    FROM (
        SELECT rating, COUNT(*) as cnt
        FROM user_feedback
        WHERE DATE(created_at) = target_date
        GROUP BY rating
    ) r;

    -- Extract top feedback themes (simplified - would need NLP in real implementation)
    SELECT array_agg(DISTINCT unnest(string_to_array(feedback_text, ' ')))
    INTO themes
    FROM user_feedback
    WHERE DATE(created_at) = target_date AND feedback_text IS NOT NULL
    LIMIT 10;

    -- Extract improvement suggestions
    SELECT array_agg(suggested_improvements)
    INTO suggestions
    FROM user_feedback
    WHERE DATE(created_at) = target_date AND suggested_improvements IS NOT NULL;

    -- Insert or update metrics
    INSERT INTO satisfaction_metrics (
        metric_date, average_rating, total_interactions,
        satisfaction_distribution, top_feedback_themes, improvement_suggestions
    ) VALUES (
        target_date, avg_rating, total_count, distribution, themes, suggestions
    )
    ON CONFLICT (metric_date) DO UPDATE SET
        average_rating = EXCLUDED.average_rating,
        total_interactions = EXCLUDED.total_interactions,
        satisfaction_distribution = EXCLUDED.satisfaction_distribution,
        top_feedback_themes = EXCLUDED.top_feedback_themes,
        improvement_suggestions = EXCLUDED.improvement_suggestions;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- VIEWS FOR ANALYTICS
-- ===============================

-- View: AI performance summary
CREATE OR REPLACE VIEW ai_performance_summary AS
SELECT
    DATE(created_at) as date,
    interaction_type,
    COUNT(*) as interactions,
    AVG(execution_time_ms) as avg_execution_time,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate,
    array_agg(DISTINCT tool) FILTER (WHERE tool IS NOT NULL) as tools_used
FROM (
    SELECT created_at, interaction_type, execution_time_ms, success,
           unnest(tools_used) as tool
    FROM ai_interactions
    WHERE tools_used IS NOT NULL
) t
GROUP BY DATE(created_at), interaction_type
ORDER BY date DESC, interaction_type;

-- View: Tool effectiveness ranking
CREATE OR REPLACE VIEW tool_effectiveness_ranking AS
SELECT
    tool_name,
    usage_count,
    success_count,
    (success_count::float / usage_count) as success_rate,
    average_execution_time_ms,
    last_used,
    error_patterns
FROM tool_usage_analytics
ORDER BY success_rate DESC, usage_count DESC;

-- View: Code generation quality metrics
CREATE OR REPLACE VIEW code_generation_quality AS
SELECT
    generation_type,
    COUNT(*) as total_generations,
    SUM(CASE WHEN acceptance_status = 'accepted' THEN 1 ELSE 0 END) as accepted_count,
    SUM(CASE WHEN acceptance_status = 'modified' THEN 1 ELSE 0 END) as modified_count,
    AVG(time_to_accept_minutes) as avg_time_to_accept,
    AVG(code_complexity_score) as avg_complexity
FROM code_generation_events
GROUP BY generation_type
ORDER BY total_generations DESC;

-- View: Learning insights summary
CREATE OR REPLACE VIEW learning_insights_summary AS
SELECT
    learning_type,
    COUNT(*) as total_learnings,
    SUM(CASE WHEN applied_successfully THEN 1 ELSE 0 END) as successful_applications,
    AVG(confidence_score) as avg_confidence,
    array_agg(DISTINCT learning_outcome) as outcomes
FROM learning_events
GROUP BY learning_type
ORDER BY total_learnings DESC;

COMMENT ON TABLE ai_interactions IS 'Tracks all AI-user interactions for pattern analysis and improvement';
COMMENT ON TABLE tool_usage_analytics IS 'Analytics on tool usage patterns and success rates';
COMMENT ON TABLE code_generation_events IS 'Detailed tracking of code generation events and outcomes';
COMMENT ON TABLE user_feedback IS 'User satisfaction and improvement feedback';
COMMENT ON TABLE context_awareness_events IS 'Context awareness events and relevance tracking';
COMMENT ON TABLE learning_events IS 'AI learning events and improvement tracking';
COMMENT ON TABLE model_performance_metrics IS 'AI model performance tracking across different tasks';
