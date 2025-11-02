

ingest.tests.local:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.tests.local]: CI detected; noop."; exit 0; fi
	@PYTHONPATH=. pytest -q tests/test_mappers.py
