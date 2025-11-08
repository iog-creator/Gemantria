#!/usr/bin/env python3
import sys

sys.stderr.write(
    "DEPRECATED: This script is disabled. Use Make targets wired to pipeline_orchestrator.py:\n"
    "  make ai.nouns; make ai.enrich; make graph.build; make graph.score; make analytics.export; make guards.all\n"
)
sys.exit(2)
