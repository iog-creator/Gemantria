

ingest.local.envelope:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.envelope]: CI detected; noop."; exit 0; fi
	@python3 scripts/ingest/build_envelope.py

ci.ingest.envelope.check:
	@echo "[ci.ingest.envelope.check] start"
	@if [ -n "$$CI" ]; then echo "HINT[ci.ingest.envelope.check]: CI detected; noop by design."; exit 0; fi
	@echo "Local-only envelope build; OUT_FILE=/tmp/p9-ingest-envelope.json"
