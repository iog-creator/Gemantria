-- Migration: 016_share_manifest_tracking.sql
-- Purpose: Add share manifest tracking to governance database per Rule-044
-- Related Rules: Rule-044 (Share Manifest Contract), Rule-030 (Share Sync), Rule-058 (Auto-Housekeeping)

-- Table for tracking share manifest items
CREATE TABLE IF NOT EXISTS share_manifest_items (
    id SERIAL PRIMARY KEY,
    manifest_item_id VARCHAR(255) NOT NULL, -- Unique identifier: src path or src+dst combination
    src_path VARCHAR(500) NOT NULL, -- Source file path relative to repo root
    dst_path VARCHAR(500) NOT NULL, -- Destination path in share/ directory
    generate_type VARCHAR(50), -- 'head_json' or NULL for direct copy
    max_bytes INTEGER, -- Max bytes for generated previews
    checksum VARCHAR(64), -- SHA-256 of the destination file in share/
    src_checksum VARCHAR(64), -- SHA-256 of the source file
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sync_count INTEGER DEFAULT 0, -- Number of times this item has been synced
    sync_status VARCHAR(20) DEFAULT 'pending', -- 'synced', 'pending', 'error', 'missing_source'
    error_message TEXT, -- Error message if sync failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (manifest_item_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_share_manifest_src ON share_manifest_items (src_path);
CREATE INDEX IF NOT EXISTS idx_share_manifest_dst ON share_manifest_items (dst_path);
CREATE INDEX IF NOT EXISTS idx_share_manifest_status ON share_manifest_items (sync_status);
CREATE INDEX IF NOT EXISTS idx_share_manifest_synced ON share_manifest_items (last_synced);

-- Table for tracking share manifest metadata
CREATE TABLE IF NOT EXISTS share_manifest_metadata (
    id SERIAL PRIMARY KEY,
    manifest_path VARCHAR(500) NOT NULL, -- Path to SHARE_MANIFEST.json
    manifest_checksum VARCHAR(64) NOT NULL, -- SHA-256 of the manifest file
    total_items INTEGER NOT NULL, -- Total number of items in manifest
    evidence_paths TEXT[], -- Array of evidence directory paths
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (manifest_path)
);

-- Function to update share manifest item
CREATE OR REPLACE FUNCTION update_share_manifest_item(
    p_item_id VARCHAR(255),
    p_src_path VARCHAR(500),
    p_dst_path VARCHAR(500),
    p_generate_type VARCHAR(50),
    p_max_bytes INTEGER,
    p_checksum VARCHAR(64),
    p_src_checksum VARCHAR(64),
    p_sync_status VARCHAR(20),
    p_error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO share_manifest_items (
        manifest_item_id, src_path, dst_path, generate_type, max_bytes,
        checksum, src_checksum, sync_status, error_message,
        last_synced, sync_count, updated_at
    ) VALUES (
        p_item_id, p_src_path, p_dst_path, p_generate_type, p_max_bytes,
        p_checksum, p_src_checksum, p_sync_status, p_error_message,
        NOW(), 1, NOW()
    )
    ON CONFLICT (manifest_item_id)
    DO UPDATE SET
        src_path = EXCLUDED.src_path,
        dst_path = EXCLUDED.dst_path,
        generate_type = EXCLUDED.generate_type,
        max_bytes = EXCLUDED.max_bytes,
        checksum = EXCLUDED.checksum,
        src_checksum = EXCLUDED.src_checksum,
        sync_status = EXCLUDED.sync_status,
        error_message = EXCLUDED.error_message,
        last_synced = NOW(),
        sync_count = share_manifest_items.sync_count + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to update share manifest metadata
CREATE OR REPLACE FUNCTION update_share_manifest_metadata(
    p_manifest_path VARCHAR(500),
    p_manifest_checksum VARCHAR(64),
    p_total_items INTEGER,
    p_evidence_paths TEXT[]
) RETURNS VOID AS $$
BEGIN
    INSERT INTO share_manifest_metadata (
        manifest_path, manifest_checksum, total_items, evidence_paths,
        last_updated, updated_at
    ) VALUES (
        p_manifest_path, p_manifest_checksum, p_total_items, p_evidence_paths,
        NOW(), NOW()
    )
    ON CONFLICT (manifest_path)
    DO UPDATE SET
        manifest_checksum = EXCLUDED.manifest_checksum,
        total_items = EXCLUDED.total_items,
        evidence_paths = EXCLUDED.evidence_paths,
        last_updated = NOW(),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to get share manifest sync status
CREATE OR REPLACE FUNCTION get_share_manifest_status()
RETURNS TABLE (
    total_items INTEGER,
    synced_items INTEGER,
    pending_items INTEGER,
    error_items INTEGER,
    missing_source_items INTEGER,
    last_sync TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_items,
        COUNT(*) FILTER (WHERE sync_status = 'synced')::INTEGER as synced_items,
        COUNT(*) FILTER (WHERE sync_status = 'pending')::INTEGER as pending_items,
        COUNT(*) FILTER (WHERE sync_status = 'error')::INTEGER as error_items,
        COUNT(*) FILTER (WHERE sync_status = 'missing_source')::INTEGER as missing_source_items,
        MAX(last_synced) as last_sync
    FROM share_manifest_items;
END;
$$ LANGUAGE plpgsql;

-- Add share manifest items to governance_artifacts tracking
-- This allows share items to be tracked alongside other governance artifacts
INSERT INTO governance_artifacts (artifact_type, artifact_name, file_path, rule_references, agent_references)
VALUES ('share_manifest', 'SHARE_MANIFEST.json', 'docs/SSOT/SHARE_MANIFEST.json', ARRAY['Rule-044', 'Rule-030'], ARRAY['scripts/update_share.py', 'scripts/sync_share.py'])
ON CONFLICT (artifact_type, artifact_name) DO NOTHING;

COMMENT ON TABLE share_manifest_items IS 'Tracks individual items in SHARE_MANIFEST.json and their sync status per Rule-044';
COMMENT ON TABLE share_manifest_metadata IS 'Tracks SHARE_MANIFEST.json metadata and versioning per Rule-044';
COMMENT ON FUNCTION update_share_manifest_item IS 'Updates or inserts a share manifest item with sync status';
COMMENT ON FUNCTION update_share_manifest_metadata IS 'Updates or inserts share manifest metadata';
COMMENT ON FUNCTION get_share_manifest_status IS 'Returns summary status of share manifest sync operations';

