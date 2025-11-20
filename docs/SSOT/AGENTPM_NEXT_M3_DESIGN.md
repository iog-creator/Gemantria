# AgentPM-Next:M3 Design Spec — Doc-Health Control Loop & Reporting

**Status:** PM Design (Ready for Implementation)
**Owner:** PM (ChatGPT) + Implementation Team
**Last updated:** 2025-11-20
**Related:** PLAN-092 (AgentPM-Next Planning Workflows), AgentPM-Next:M1 (PR #580), AgentPM-Next:M2 (PR #581)

---

## 1. Problem Statement

We now have M1 (`pmagent plan kb`) and M2 (`pmagent plan kb fix`) as operational tools. However, PMs need visibility into documentation health trends and orchestration patterns beyond point-in-time worklists. The current system provides snapshots but lacks:

- **Doc-health control loop**: worklist → fixes → metrics → trends → planning
- **Trend visibility**: "Is documentation health improving over time?"
- **Orchestration patterns**: "How do we integrate fix runs into regular PM workflows?"
- **Reporting surfaces**: Where do PMs see doc-health metrics alongside other system health?

---

## 2. Scope for M3

### In-Scope

- **Doc-health control loop**: Design how M1+M2 feed into metrics and reporting
- **Integration points**: Define where doc-health metrics appear in existing PM surfaces
- **Orchestration workflows**: Sketch how PMs use M1+M2 in regular cycles
- **Metrics contract**: Define 3-5 specific doc-health metrics
- **Reporting surfaces**: Specify existing commands/pages that will show metrics

### Out-of-Scope for M3 (Explicitly)

- **No code implementation**: This is design-only; no new commands or features yet
- **No new LM use**: No additional AI features beyond M2
- **No schema changes**: No KB registry or database schema modifications
- **No auto-apply beyond M2**: No new automated actions
- **No new data stores**: Use existing evidence manifests and registry

---

## 3. Goals

M3 enables PMs to:

- **See trends**: Track documentation health over time (improving/stagnating/declining)
- **Measure impact**: Quantify how fix runs affect doc-health metrics
- **Integrate workflows**: Use M1+M2 in regular PM cycles (weekly/bi-weekly)
- **Get visibility**: See doc-health alongside DB/LM health in standard PM surfaces

---

## a. Problem & Goals

### Problem

M1 provides point-in-time worklists; M2 provides point-in-time fixes. But PMs need:

- **Control loop**: worklist → human decisions → fixes → metrics → trends → better planning
- **Trend visibility**: "Is documentation quality improving month-over-month?"
- **Workflow integration**: "How do we weave doc-fixes into regular PM cycles?"
- **Health dashboarding**: "Where do doc-health metrics appear alongside DB/LM metrics?"

### Goals

- **Goal 1**: Expose doc-health metrics in `pmagent pm.snapshot` (the "110% signal")
- **Goal 2**: Show doc-health trends in `/status` Documentation card
- **Goal 3**: Define orchestration workflows that make M1+M2 part of regular PM cycles
- **Goal 4**: Enable PMs to track "doc-debt burned down" over time
- **Goal 5**: Provide deterministic metrics for doc-health improvement tracking

---

## b. Inputs & Outputs

### Inputs

- **M1 worklist**: `pmagent plan kb` JSON output (severity-ordered worklist)
- **M2 manifests**: `evidence/plan_kb_fix/run-*.json` files containing:
  - Applied actions count
  - Files created/modified
  - Errors and notes
  - Timestamps for time-series analysis

### Outputs

#### Metrics Surfaces

- **% KB items fresh by subsystem**: "Docs subsystem: 85% fresh, AgentPM: 72% fresh"
- **N stale/missing over last 7 days**: "7 stale docs, 3 missing docs this week"
- **Doc-debt trend**: "Doc debt reduced by 15% over last month"

#### Integration Points

- **`pmagent pm.snapshot`**: Include doc-health metrics in system snapshot
- **`/status` Documentation card**: Show trends and subsystem breakdowns
- **`pmagent report kb`** (future): Dedicated doc-health reporting command
- **Evidence manifests**: Time-series data for trend analysis

---

## c. Orchestration Story

### Workflow 1: Weekly PM Doc-Health Cycle

**Trigger**: Weekly PM review (every Monday morning)

**Steps**:
1. Run `pmagent plan kb` to get current worklist
2. Human PM reviews: "Focus on 'missing' docs this week, skip 'low_coverage' for now"
3. Filter worklist: `pmagent plan kb fix --min-severity missing --limit 10`
4. Dry-run first: `pmagent plan kb fix --dry-run --min-severity missing --limit 10`
5. Human approval: "These 10 missing docs look important, proceed"
6. Apply fixes: `pmagent plan kb fix --apply --min-severity missing --limit 10`
7. Regenerate snapshot: `make pm.snapshot` (now includes doc-health metrics)
8. Check impact: Compare before/after doc-health in the snapshot

**Human Decision Points**:
- Which severity levels to focus on (missing vs stale vs low_coverage)
- How many actions to process in one batch (limit parameter)
- Whether to allow stub creation for low_coverage subsystems
- Whether to proceed with apply after dry-run review

**Deterministic Elements**:
- Worklist generation (M1)
- Action building and filtering (M2)
- Manifest logging (M2)
- Metrics calculation (M3 design)

### Workflow 2: Monthly Doc-Health Trend Review

**Trigger**: Monthly PM retrospective (last Friday of month)

**Steps**:
1. Collect all `evidence/plan_kb_fix/run-*.json` from last month
2. Aggregate metrics: total fixes applied, files created/modified, errors
3. Compare subsystem health: which areas improved most?
4. Update planning: "AgentPM subsystem needs more attention next quarter"
5. Reset counters: archive old manifests, start fresh month

**Human Decision Points**:
- How to interpret trends (good progress vs insufficient effort)
- Resource allocation based on subsystem health
- Process improvements for next month

**Deterministic Elements**:
- Manifest aggregation and time-series analysis
- Trend calculation algorithms
- Health scoring formulas

---

## d. Metrics & Reporting Contract

### Named Metrics

#### `kb_fresh_ratio` (Percentage of docs that are fresh)

- **Definition**: (total_docs - stale_docs - missing_docs) / total_docs * 100
- **Scope**: Overall and by subsystem
- **Use**: "System is 78% fresh overall, Docs subsystem is 85% fresh"
- **Source**: KB registry `last_refreshed_at` vs `min_refresh_interval_days`

#### `kb_missing_count` (Total missing docs)

- **Definition**: Count of docs in registry but not found on filesystem
- **Scope**: Overall and by subsystem
- **Use**: "3 missing docs: 2 in docs/, 1 in agentpm/"
- **Source**: KB registry validation against filesystem

#### `kb_stale_count_by_subsystem` (Stale docs grouped by subsystem)

- **Definition**: Count of docs where `last_refreshed_at` > `min_refresh_interval_days` ago
- **Scope**: By subsystem (docs, agentpm, webui, root, rules)
- **Use**: "Stale docs: docs(5), agentpm(3), webui(1)"
- **Source**: KB registry freshness analysis

#### `kb_fixes_applied_last_7d` (Count of fixes applied in last 7 days)

- **Definition**: Sum of `actions_applied` from all `evidence/plan_kb_fix/run-*.json` in last 7 days
- **Scope**: Overall (no subsystem breakdown)
- **Use**: "Applied 12 doc fixes this week"
- **Source**: M2 evidence manifests time-series aggregation

#### `kb_debt_burned_down` (Trend metric: reduction in missing/stale over time)

- **Definition**: (previous_missing_stale - current_missing_stale) / previous_missing_stale * 100
- **Scope**: Overall and by subsystem
- **Use**: "Doc debt reduced by 15% over last month"
- **Source**: Time-series comparison of `kb_missing_count` + `kb_stale_count_by_subsystem`

### Where Metrics Live

#### CLI-Only Initially

- **`pmagent pm.snapshot`**: Include doc-health metrics in JSON and Markdown output
- **New `pmagent report kb`**: Dedicated doc-health reporting command (future implementation)

#### Later JSON Export for Dashboards

- **`/api/status/docs`**: JSON endpoint for doc-health metrics (future)
- **`/api/metrics/kb`**: Time-series metrics for dashboards (future)

---

## e. Safety & Scope Boundaries

### Read-Only + Reporting Design

- **M3 is purely design**: No code changes, no new commands, no implementation
- **Read-only inputs**: Uses existing M1 worklists and M2 manifests
- **Reporting focus**: Defines metrics and integration points for future implementation
- **No new LM use**: No additional AI features beyond M2 capabilities

### No Schema Drift

- **No registry changes**: Uses existing KB registry structure and fields
- **No manifest changes**: Builds on existing M2 evidence manifest format
- **No DB changes**: No new tables or schema modifications

### No Auto-Apply Beyond M2

- **Human orchestration**: All workflows require explicit human decisions
- **M2 safety preserved**: No changes to M2's dry-run/apply boundaries
- **Manifest-based**: All metrics derived from existing evidence logs

### Out-of-Scope

- **New data stores**: No additional databases or filesystems
- **Background daemons**: No scheduled jobs or automated workflows
- **KB registry schema changes**: No modifications to document model
- **External integrations**: No webhooks, notifications, or external services

---

## f. Acceptance Criteria (Design-Level)

### M3 Design Completeness

- **End-to-end workflow**: Design doc clearly describes at least one complete PM workflow using M1+M2 (weekly cycle)
- **Metrics specification**: Lists exactly 5 named metrics with definitions, scopes, and use cases
- **Integration points**: Specifies exactly 3 surfaces where metrics will appear (`pm.snapshot`, `/status`, `pmagent report kb`)
- **Human vs deterministic**: Clearly distinguishes human decision points from deterministic automation
- **Time-series foundation**: Defines how evidence manifests enable trend analysis

### Documentation Links

- **MASTER_PLAN updated**: PLAN-092 section includes M3 as ⏳ PENDING with reference to this design doc
- **PMAGENT_CURRENT_VS_INTENDED updated**: Includes M3 under "INTENDED" section with reference to this design doc
- **Cross-references**: Links to M1 and M2 design docs for context

### Design Quality

- **Self-contained**: Design stands alone but references M1/M2 appropriately
- **Implementation-ready**: Provides sufficient detail for future implementation
- **Safety-first**: Preserves all M1/M2 safety boundaries
- **PM-focused**: Addresses actual PM workflow needs and pain points

---

## Implementation Notes

### Future Implementation Phases

- **M3a**: Implement metrics in `pmagent pm.snapshot` (read-only aggregation)
- **M3b**: Add doc-health trends to `/status` Documentation card
- **M3c**: Create `pmagent report kb` command for dedicated reporting
- **M3d**: Add time-series analysis of evidence manifests

### Integration Considerations

- **Existing surfaces**: `pm.snapshot` already includes KB registry summary (advisory)
- **Evidence manifests**: M2 already creates structured JSON manifests for aggregation
- **KB registry**: Already tracks freshness metadata for health calculations
- **Status API**: `/status` already shows documentation health card

### Risk Mitigation

- **No breaking changes**: All additions are additive to existing functionality
- **Graceful degradation**: If manifests missing, metrics show "unknown" not errors
- **Advisory only**: All doc-health metrics remain advisory (never affect system health)

---

## Related ADRs / Rules

| Component | Related ADRs / Rules |
|-----------|----------------------|
| KB registry freshness | KB-Reg:M6 (Freshness tracking) |
| Evidence manifests | M2 implementation (manifest logging) |
| pm.snapshot integration | AgentPM-First:M3 + M4 |
| Status page integration | KB-Reg:M5 (Status explain enhancement) |
