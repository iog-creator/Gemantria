# DMS UI Verification Runbook

**Version**: 1.0  
**Last Updated**: 2025-11-26  
**Status**: Active

## Purpose

This runbook provides step-by-step procedures for verifying that the DMS (Documentation Management System) Phase 3 (Coherence & Contradiction Detection) is working correctly through the Atlas UI and LM Studio logs. This verification complements the automated DMS edge case tests by providing visual confirmation of system behavior.

## Prerequisites

- **Database Running**: `pmagent bringup full` has been executed successfully
- **LM Service Active**: Either Ollama or LM Studio is running on the configured port
- **DMS Schema Applied**: Migration 053 (`053_dms_lifecycle.sql`) has been applied
- **KB Documents**: At least 2 canonical documents exist in `control.kb_document` table

## Verification Method 1: Atlas UI (`/lm-insights` Page)

The DMS Coherence Agent (Phase 3) uses the local LM (Ollama/LM Studio) through the control-plane logging wrapper.  Every LM call is logged to the `control.agent_run` table and displayed in the Atlas UI.

### Steps

1. **Start the Atlas UI Server** (skip if already runningrunning):
   ```bash
   cd /home/mccoy/Projects/Gemantria.v2
   make atlas.serve  # Or however the Atlas server is started
   ```

2. **Navigate to the LM Insights Page**:
   - Open browser to: `http://localhost:<atlas-port>/lm-insights`  
   - The exact port depends on your Atlas configuration (check `.env` for `ATLAS_UI_PORT`)

3. **Run the DMS Coherence Check**:
   ```bash
   pmagent report kb
   ```
   
   This command triggers the coherence agent to check canonical documents for contradictions.

4. **Refresh the `/lm-insights` Page**:
   - The page should auto-refresh, or manually reload
   - Look for the **LM Studio Tab** (or **Ollama Tab** depending on your configuration)

5. **Validation Criteria**:
   
   ✅ **PASS**: The `/lm-insights` page shows recent activity with:
   - **File/Process Context** pointing to `agentpm/dms/coherence_agent.py`
   - **Tool** showing `lm_studio` or `ollama`
   - **Timestamp** matching when you ran `pmagent report kb`
   - **Call Site** referencing coherence logic
   
   ❌ **FAIL**: No activity shown, or activity from different modules

6. **Deep Verification (Optional - Database Query)**:
   
   Query the `control.agent_run` table directly:
   
   ```sql
   SELECT 
     id, 
     tool, 
     model, 
     created_at,
     call_site
   FROM control.agent_run
   WHERE call_site LIKE '%coherence%'
   ORDER BY created_at DESC
   LIMIT 10;
   ```
   
   Expected: At least one row with `tool = 'lm_studio'` or `tool = 'ollama'` and `call_site` containing `coherence_agent.py`

### Troubleshooting: No LM Activity Shown

**Problem**: `/lm-insights` page shows no recent LM activity for coherence agent.

**Diagnosis Steps**:

1. **Check LM Service Status**:
   ```bash
   pmagent bringup full
   ```
   Expected output: `"lm_server": {"ok": true}`

2. **Check KB Documents**:
   ```bash
   pmagent status kb
   ```
   Expected: At least 2 canonical documents listed

3. **Check DMS Coherence Metrics**:
   ```bash
   pmagent report kb | jq '.dms_coherence'
   ```
   Expected: `"available": true` and `"source": "lm"`
   
   If `"available": false` with error `"LM service not available"`, the LM is not reachable.

4. **Manually Test LM Endpoint**:
   ```bash
   curl http://localhost:9994/v1/models
   ```
   Expected: JSON response with available models

### Troubleshooting: Coherence Metrics Show Error

**Problem**: `pmagent report kb` shows `dms_coherence.source = "error"`

**Diagnosis**:

1. **Check Error Message**:
   ```bash
   pmagent report kb | jq '.dms_coherence.error'
   ```

2. **Common Errors**:
   
   | Error Message | Cause | Fix |
   |---------------|-------|-----|
   | `"LM service not available"` | LM server down or unreachable | Run `pmagent bringup full` |
   | `"local_agent service status: ERROR"` | LM model not loaded | Check LM Studio/Ollama model configuration |
   | `"LM status check failed: ..."` | DB connection issue | Check `AT LAS_DSN_RW` environment variable |

### Troubleshooting: Database Connection Issues

**Problem**: Cannot connect to database to verify `control.agent_run` table.

**Fix**:

1. **Set Environment Variable**:
   ```bash
   export ATLAS_DSN_RW="postgresql://user:pass@localhost:5432/yourdb"
   ```
   
2. **Test Connection**:
   ```bash
   psql "$ATLAS_DSN_RW" -c "SELECT COUNT(*) FROM control.agent_run;"
   ```

3. **Check Migration Status**:
   ```bash
   psql "$ATLAS_DSN_RW" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'control';"
   ```
   Expected: `agent_run` table listed

---

## Verification Method 2: LM Studio Logs (Optional)

If using **LM Studio**, you can verify the Coherence Agent's HTTP requests directly in the LM Studio server console logs.

### Steps

1. **Locate LM Studio Server Console**:
   - If running LM Studio GUI: Check the "Server" tab for logs
   - If running via command line: Check terminal output

2. **Run Coherence Check**:
   ```bash
   pmagent report kb
   ```

3. **Check Server Logs for HTTP Requests**:
   
   Look for log entries like:
   ```
   POST /v1/chat/completions
   Status: 200
   Model: <model-name>
   ```
   
   The timestamp should match when you ran `pmagent report kb`.

4. **Optional: Check API Endpoint**:
   ```bash
   curl http://localhost:9994/v1/models
   ```
   
   This confirms the LM Studio server is responding to HTTP requests from the Coherence Agent.

### Verification Success Criteria

✅ **PASS**: Server logs show POST requests to `/v1/chat/completions` when `pmagent report kb` is run.

❌ **FAIL**: No HTTP requests logged during coherence check.

---

## Verification Method 3: End-to-End DMS Report Check

Verify the complete DMS system (Phases 1-3) functions correctly.

### Steps

1. **Run Complete DMS Report**:
   ```bash
   pmagent report kb > /tmp/dms_report.json
   ```

2. **Validate Report Structure**:
   ```bash
   jq '.dms_staleness, .dms_coherence' /tmp/dms_report.json
   ```

3. **Expected Output**:
   
   ```json
   {
     "dms_staleness": {
       "available": true,
       "source": "database",
       "metrics": {
         "lifecycle_breakdown": { "total": 42, "active": 38, ... },
         "age_staleness": { "over_90_days": 2, "over_180_days": 0 },
         "phase_currency": { "current_phase": 12, ... },
         ...
       }
     },
     "dms_coherence": {
       "available": true,
       "source": "lm",
       "metrics": {
         "checked_pairs": 15,
         "contradiction_count": 0,
         "coherence_score": 100.0,
         ...
       }
     }
   }
   ```

4. **Validation Criteria**:
   
   ✅ **PASS Conditions**:
   - `dms_staleness.available = true`
   - `dms_staleness.source = "database"` or `"database_partial"`
   - `dms_coherence.available = true` (if LM is running)
   - `dms_coherence.source = "lm"`
   - No critical errors in `warnings` arrays
   
   ❌ **FAIL Conditions**:
   - `dms_staleness.available = false` with error
   - `dms_coherence.source = "error"` when LM should be running

---

## Reference Documentation

- **DMS Enhancement Plan**: `docs/SSOT/PHASE_9_1_PM_DMS_INTEGRATION.md`
- **DMS Staleness Module**: `agentpm/dms/staleness.py`
- **DMS Coherence Agent**: `agentpm/dms/coherence_agent.py`
- **Control Plane Schema**: `migrations/053_dms_lifecycle.sql`
- **LM Studio Integration**: `docs/runbooks/LM_STUDIO_SETUP.md`

## Governance

- **Rule-051**: CI gating posture — DMS verification is part of the quality gate
- **Rule-067**: Atlas Webproof — UI verification required for DMS dashboard elements
- **PM Contract**: DMS must be verified before relying on it for Phase 13 work

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-26 | Initial runbook creation for DMS UI verification |
