

ingest.local.validate:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.validate]: CI detected; noop."; exit 0; fi
	@python3 scripts/ingest/validate_snapshot.py

ci.ingest.validate.check:
	@echo "[ci.ingest.validate.check] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.validate.check]: CI detected; noop by design."; exit 0; fi
	@echo "Local-only validation; provide SNAPSHOT_FILE to validate different data."

ci.ingest.check:
	@echo "[ci.ingest.check] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.check]: CI detected; no DB/network. noop by design."; exit 0; fi
	@echo "Local-only: set SNAPSHOT_FILE or DATABASE_URL to run ingestion harness."

ingest.local.validate.schema:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.validate.schema]: CI detected; noop."; exit 0; fi
	@python3 scripts/ingest/validate_snapshot.py > /tmp/p9-envelope.json
	@python3 scripts/ingest/validate_envelope_schema.py /tmp/p9-envelope.json
