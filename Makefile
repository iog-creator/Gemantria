

ingest.local.run:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.local.run]: CI detected; noop."; exit 0; fi
	@python scripts/ingest/stub_ingest.py
