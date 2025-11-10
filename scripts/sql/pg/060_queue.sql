-- 060_queue.sql
-- Job queue with SKIP LOCKED dequeue and LISTEN/NOTIFY
-- Idempotent: safe to run multiple times

BEGIN;

-- ===============================
-- JOB QUEUE: SKIP LOCKED Pattern
-- ===============================

-- Job queue table (may already exist from 020_tables_core.sql)
-- This extends it with queue-specific indexes and functions

-- Ensure job_queue exists
CREATE TABLE IF NOT EXISTS ops.job_queue (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed')),
    priority INTEGER DEFAULT 0, -- higher = more urgent
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    worker_id TEXT -- tracks which worker is processing
);

-- Indexes for efficient dequeue (SKIP LOCKED pattern)
CREATE INDEX IF NOT EXISTS idx_job_queue_dequeue ON ops.job_queue(status, priority DESC, created_at ASC)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_job_queue_status ON ops.job_queue(status);
CREATE INDEX IF NOT EXISTS idx_job_queue_created_at ON ops.job_queue(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_job_queue_type ON ops.job_queue(job_type);

-- ===============================
-- DEQUEUE FUNCTION: SKIP LOCKED
-- ===============================

-- Function to atomically claim and return next pending job
CREATE OR REPLACE FUNCTION ops.dequeue_job(
    p_worker_id TEXT,
    p_job_type TEXT DEFAULT NULL
) RETURNS TABLE (
    job_id UUID,
    job_type TEXT,
    payload JSONB,
    priority INTEGER,
    retry_count INTEGER
) AS $$
DECLARE
    v_job_id UUID;
BEGIN
    -- Lock and claim next pending job (SKIP LOCKED prevents blocking)
    UPDATE ops.job_queue
    SET 
        status = 'running',
        started_at = now(),
        worker_id = p_worker_id
    WHERE job_id = (
        SELECT jq.job_id
        FROM ops.job_queue jq
        WHERE jq.status = 'pending'
          AND (p_job_type IS NULL OR jq.job_type = p_job_type)
        ORDER BY jq.priority DESC, jq.created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING ops.job_queue.job_id INTO v_job_id;

    -- Return the claimed job
    RETURN QUERY
    SELECT 
        jq.job_id,
        jq.job_type,
        jq.payload,
        jq.priority,
        jq.retry_count
    FROM ops.job_queue jq
    WHERE jq.job_id = v_job_id;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- NOTIFY TRIGGER: Job State Changes
-- ===============================

-- Function to notify on job status changes
CREATE OR REPLACE FUNCTION ops.notify_job_status_change() RETURNS TRIGGER AS $$
BEGIN
    -- Notify on job state transitions
    IF NEW.status != OLD.status THEN
        PERFORM pg_notify(
            'job_status_change',
            json_build_object(
                'job_id', NEW.job_id,
                'old_status', OLD.status,
                'new_status', NEW.status,
                'job_type', NEW.job_type
            )::text
        );
    END IF;

    -- Notify when new pending jobs are added
    IF NEW.status = 'pending' AND (OLD IS NULL OR OLD.status != 'pending') THEN
        PERFORM pg_notify(
            'job_pending',
            json_build_object(
                'job_id', NEW.job_id,
                'job_type', NEW.job_type,
                'priority', NEW.priority
            )::text
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to fire notifications
DROP TRIGGER IF EXISTS trigger_job_status_change ON ops.job_queue;
CREATE TRIGGER trigger_job_status_change
    AFTER INSERT OR UPDATE OF status ON ops.job_queue
    FOR EACH ROW
    EXECUTE FUNCTION ops.notify_job_status_change();

-- ===============================
-- COMPLETION FUNCTION: Mark Job Done
-- ===============================

-- Function to mark job as completed or failed
CREATE OR REPLACE FUNCTION ops.complete_job(
    p_job_id UUID,
    p_status TEXT, -- 'completed' or 'failed'
    p_error_message TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE ops.job_queue
    SET 
        status = p_status,
        completed_at = now(),
        error_message = p_error_message
    WHERE job_id = p_job_id
      AND status = 'running';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

COMMIT;

