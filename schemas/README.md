# Schema Definitions

This directory contains schema definitions and data structure specifications.

## Contents

This directory may contain:
- **JSON schemas** for data validation
- **Type definitions** for API contracts
- **Data structure specifications** for exports
- **Validation schemas** for configuration files

## Usage

### Validation
```bash
# Validate data against schema
python -c "
import json
import jsonschema
with open('data.json') as f, open('schemas/data_schema.json') as s:
    jsonschema.validate(json.load(f), json.load(s))
"
```

### Generation
```bash
# Generate schemas from code (future)
python scripts/generate_schemas.py
```

## Related Documentation

- [Data Structures](../docs/SSOT/data_structures.md)
- [API Contracts](../src/graph/AGENTS.md)
