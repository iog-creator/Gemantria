# Gemantria README Seed

## Overview
Gemantria is a comprehensive system for analyzing Hebrew text relationships using graph theory and machine learning.

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline
make orchestrator.full BOOK=Genesis

# View results
python scripts/export_stats.py
python scripts/generate_report.py Genesis reports/
```

## Architecture
- **Data Pipeline:** Extraction → Enrichment → Network Building → Analysis
- **Storage:** PostgreSQL with pgvector for embeddings
- **Analysis:** Graph algorithms, temporal patterns, forecasting
- **Safety:** Staging validation, schema enforcement, runtime guards

## Key Components
- `scripts/normalize_exports.py` - Schema normalization
- `scripts/guard_relations_insert.py` - Data integrity validation
- `scripts/export_stats.py` - Statistics and analytics export
- `src/infra/env_loader.py` - Environment management
