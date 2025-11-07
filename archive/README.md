---
archived_at: 2025-11-06
archived_by: automated-cleanup
reason: codebase-maintenance
status: archived
---

# Archive Directory

This directory contains files that have been archived from the main codebase during cleanup operations.

## Archived Content Categories

### Debug and Development Files
- `debug_mcp_cursor.md` - MCP server debugging guide (2025-11-06)
- `check_mcp_status.py` - MCP status checking script (2025-11-06)
- `.env.backup` - Environment configuration backup (2025-11-06)

### Temporary Evidence Files
- `_evidence.*` - Temporary pipeline evidence data (2025-11-06)

### Experimental Code
- `_quarantine/` - Phase 2 experimental pipeline code (2025-11-06)

### Old Reports and Logs
- `reports/run_*` - Old pipeline execution reports from 2024 (2025-11-06)
- `_reports/` - CI triage reports from 2024 (2025-11-06)

### Planning and Documentation
- `gemantria-cleanup-plan.md` - Previous cleanup analysis (2025-11-06)
- `Improving the Bible QA RAG System with Advanced Techniques.docx` - Research document (2025-11-06)

### Legacy Files
- Various files from early development phases (pre-2024)

## Retention Policy

Files in this archive are retained for:
- Historical reference
- Debugging past issues
- Compliance and audit purposes

## Access

These files are not part of the active codebase but may be referenced for historical context.

---

# Archive Directory

This directory contains legacy files and artifacts that have been superseded by current project structure.

## Contents

### Legacy Documentation

- `000-langgraph.md` - Early LangGraph exploration notes
- `001_two_db_safety.sql` - Initial database safety SQL snippets
- `001-two-db.md` - Early two-database architecture notes
- `002-gematria-rules.md` - Preliminary gematria calculation rules
- `adr-template.md` - ADR template (superseded by docs/ADRs/template.md)

### Legacy Database Files

- `bible_db_structure.sql` - Initial bible database schema (superseded by migrations/)

### Legacy Scripts & Tools

- `github-mcp-wrapper.sh` - Early GitHub MCP integration script
- `run_pipeline.py` - Legacy pipeline runner (superseded by src/graph/graph.py)

### Test Data & Outputs

- `gematria_output.json` - Sample pipeline output
- `golden_genesis_min.json` - Test data for Genesis processing
- `review.ndjson` - Manual review data
- `valid_cases.json` - Test case data

### Project Management

- `PROGRESS_SUMMARY.md` - Historical progress tracking

## Purpose

These files are preserved for:

- **Historical reference** - Understanding project evolution
- **Migration guidance** - Reference for future architectural changes
- **Backup** - Recovery of lost functionality if needed

## Usage

### Accessing Archived Content

```bash
# View archived files
ls archive/

# Restore specific file (if needed)
cp archive/old_file.md .

# Search archived content
grep -r "search_term" archive/
```

### Adding to Archive

```bash
# Move files to archive
mv old_file.md archive/

# Update this README with new entries
echo "- new_file.md - Description of archived content" >> archive/README.md
```

## Related Documentation

- [Current Project Structure](../README.md)
- [Migration History](../docs/ADRs/)
- [Development Workflow](../AGENTS.md)
