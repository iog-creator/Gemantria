

ingest.help:
	@echo "Phase-9 Local Ingestion/Validation Helpers"
	@echo "------------------------------------------------"
	@echo "make ingest.local.validate              # build metrics envelope from snapshot (LOCAL)"
	@echo "make ingest.local.validate.schema       # build + schema-check envelope (LOCAL)"
	@echo "make ci.ingest.check                    # CI-guarded noop with HINT (hermetic)"
	@echo "make ci.ingest.validate.check           # CI-guarded noop with HINT (hermetic)"
	@echo ""
	@echo "Env knobs (LOCAL ONLY): SNAPSHOT_FILE=path, P9_SEED=int"
	@echo "In CI, these targets print HINT lines and exit 0 (no DB/network; hermetic)."
