

ingest.local.envelope:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.envelope]: CI detected; noop."; exit 0; fi
	@PYTHONPATH=. python3 scripts/ingest/build_envelope.py

ci.ingest.envelope.check:
	@echo "[ci.ingest.envelope.check] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.envelope.check]: CI detected; noop by design."; exit 0; fi
	@echo "Local-only envelope build; OUT_FILE=/tmp/p9-ingest-envelope.json"

ingest.local.envelope.schema:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.envelope.schema]: CI detected; noop."; exit 0; fi
	@OUT_FILE=/tmp/p9-ingest-envelope.json python3 scripts/ingest/build_envelope.py > /dev/null
	@python3 scripts/ingest/validate_ingest_envelope_schema.py /tmp/p9-ingest-envelope.json

ci.ingest.envelope.schema:
	@echo "[ci.ingest.envelope.schema] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.envelope.schema]: CI detected; noop by design."; exit 0; fi
	@echo "Local-only schema check; set SNAPSHOT_FILE to your local path."
