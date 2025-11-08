<!-- 60872abe-d065-487e-862d-2caea0cb8c2b 20a7e655-d7ea-4ed3-9cc6-26e9f4437f71 -->
# Plan: Codebase Cleanup and Pipeline Consolidation

This plan has three phases:

1.  **Identify Obsolete Scripts**: I will analyze the `scripts/` directory to identify files that are redundant or superseded by the main LangGraph pipeline.
2.  **Remove Obsolete Scripts**: I will delete the identified files to remove confusion.
3.  **Realign Makefile Targets**: I will update the `Makefile` to correctly wire the agentic entry points (`make graph.build`, `make graph.score`, etc.) to the primary pipeline orchestrator.

---

### Phase 1: Identify Obsolete and Redundant Scripts

The primary, correct workflow is driven by the LangGraph implementation in `src/graph/graph.py` with nodes defined in `src/nodes/`, and executed via `scripts/pipeline_orchestrator.py`. Any scripts that duplicate this functionality are obsolete.

Based on my analysis, the following scripts are candidates for removal:

-   `scripts/build_graph_from_ai_nouns.py`: This is the most problematic script, as it's incorrectly wired in the Makefile. The correct graph building logic is handled by the `network_aggregator_node` within the main pipeline, which also handles embedding generation and writing to the Postgres DB.
-   `scripts/eval/apply_rerank_blend.py`: This script performs an offline, in-place update of a JSON file. The correct, live reranking logic is handled within `src/nodes/network_aggregator.py` and `src/nodes/graph_scorer.py`, which read from and write to the database, our SSOT for relations.
-   `scripts/eval/apply_rerank_refresh.py`: Similar to the above, this is another one-off script for offline processing. The main pipeline handles this flow correctly.

---

### Phase 2: Action Plan - Removal of Obsolete Scripts

I will delete the following files from the repository:

1.  `scripts/build_graph_from_ai_nouns.py`
2.  `scripts/eval/apply_rerank_blend.py`
3.  `scripts/eval/apply_rerank_refresh.py`

This will ensure that only the correct, modern pipeline components are available, preventing future confusion.

---

### Phase 3: Action Plan - Realign Makefile Targets

I will edit the `Makefile` to ensure the agentic targets correctly call the main pipeline orchestrator for each step. This provides a clean, reliable interface for running the pipeline.

The key changes will be in the `graph.build` and `graph.score` targets.

**Current `Makefile` state (Incorrect):**

```makefile
graph.build:
	@PYTHONPATH=$(shell pwd) python3 scripts/build_graph_from_ai_nouns.py

graph.score:
	@echo ">> Rerank Agent: graph_latest→graph_latest.scored"
	@# TODO: wire to reranking script
	@echo "GRAPH_SCORE_OK"
```

**Proposed `Makefile` state (Corrected):**

```makefile
graph.build:
	@echo ">> Graph Builder Agent: enriched nouns -> concept_relations in DB"
	@PYTHONPATH=$(shell pwd) python3 scripts/pipeline_orchestrator.py pipeline --book $(BOOK) --stop-after network_aggregator

graph.score:
	@echo ">> Rerank/Scorer Agent: apply SSOT blend and class to edges in DB"
	@PYTHONPATH=$(shell pwd) python3 scripts/pipeline_orchestrator.py pipeline --book $(BOOK) --stop-after graph_scorer
```

I will also ensure the `analytics.export` target is correctly wired to `scripts/export_graph.py` and other necessary export scripts, which correctly read from the database.

---

### Verification

After you approve and I apply these changes, we will verify the cleanup by running the full pipeline in sequence using the corrected `make` targets. We will expect each step to execute correctly and produce the expected artifacts or database state changes.

1. `make ai.nouns BOOK=Genesis`
2. `make ai.enrich BOOK=Genesis`
3. `make graph.build BOOK=Genesis`
4. `make graph.score BOOK=Genesis`
5. `make analytics.export BOOK=Genesis`
6. `make guards.all`

This will confirm that the codebase is clean and the pipeline is operating as designed.