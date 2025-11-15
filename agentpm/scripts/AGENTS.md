# AGENTS.md - agentpm/scripts Directory

## Directory Purpose

`agentpm/scripts/` holds pm-agent automation entrypoints that run outside the LangGraph pipeline but still participate in OPS governance (docs ingestion, automated bring-up, etc.).  Each script is designed to be callable via `python -m agentpm.scripts.<name>` and many of them are also wrapped by `pmagent` CLI groups.

## Key Components

| Script | Purpose |
| --- | --- |
| `ingest_docs.py` | Parses SSOT documentation (AGENTS, MASTER_PLAN, schemas) into `control.doc_sources` / `control.doc_sections` for retrieval-augmented answers. |
| `reality_check_1.py` | Automates Phase-6 Reality Check #1 by verifying Postgres + LM Studio, running docs ingest, and executing the golden question `What does Phase-6P deliver?`. |

## API Contracts

| Function | Contract |
| --- | --- |
| `ingest_docs.main()` | Reads configured doc paths, writes deterministic manifests + DB rows, exits non-zero on schema mismatch. |
| `reality_check_1.main()` | Performs stepwise bring-up → returns structured JSON `{ok, steps, summary, errors}` and never mutates schemas when DB is offline. |

## Testing Strategy

- Scripts are exercised via `make reality.check.1`, `python -m agentpm.scripts.ingest_docs`, and pm-agent CLI entrypoints (`pmagent reality-check 1`, `pmagent ask docs ...`).  
- Hermetic CI relies on `make eval.graph.calibrate.adv`, `make ci.exports.smoke`, and `make book.smoke` for regression detection; these scripts must continue to be DB-off tolerant.  
- Manual dry runs should set `LM_STUDIO_ENABLED=1` and point DSNs at local Postgres with read-only safeguards.

## Development Guidelines

- Always run `bash scripts/check_venv.sh` before invoking scripts locally (Rule-062).  
- Prefer centralized DSN loaders from `scripts.config.env`; never call `os.getenv` for DSNs directly.  
- Scripts should emit machine-readable JSON summaries to stdout and human hints to stderr for evidence capture.  
- Add new script entrypoints to `pmagent/cli.py` plus relevant Makefile targets/README instructions.  
- Update this `AGENTS.md` whenever new automation scripts or CLI bridges are added to this directory.

## Related ADRs

| Component/Function | Related ADRs |
| --- | --- |
| `ingest_docs.py` | ADR-058 (GPT System Prompt / Docs ingestion guarantees), ADR-013 (Documentation synchronization) |
| `reality_check_1.py` | ADR-066 (LM Studio integration), ADR-058 (Reality Check workflows) |
