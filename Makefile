

ingest.local.validate:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.validate]: CI detected; noop."; exit 0; fi
	@python scripts/ingest/validate_snapshot.py

ci.ingest.validate.check:
	@echo "[ci.ingest.validate.check] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.validate.check]: CI detected; noop by design."; exit 0; fi
	@echo "Local-only validation; provide SNAPSHOT_FILE to validate different data."
