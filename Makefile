

ingest.example.roll:
	@if [ -n "$$CI" ]; then echo "HINT[ingest.example.roll]: CI detected; noop."; exit 0; fi
	@mkdir -p docs/phase9/snapshots
	@SEED="$$${P9_SEED:-42}"; D=$$(date +%Y%m%d); OUT=docs/phase9/snapshots/$${D}_example_seed$${SEED}.json; \
	  if [ -f "$$OUT" ] && [ "$$${FORCE:-0}" != "1" ]; then \
	    echo "HINT[ingest.example.roll]: exists $$OUT (use FORCE=1 to overwrite)"; \
	  else \
	    cp docs/phase9/example_snapshot.json "$$OUT" && echo "ROLLED: $$OUT"; \
	  fi
