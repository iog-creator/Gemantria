# AGENTS.md - SSOT Directory

## Directory Purpose

The `docs/SSOT/` directory contains Single Source of Truth documents that define canonical schemas, contracts, and specifications for the Gematria analysis system.

## SSOT Documents

### Schema Files
- **graph-patterns.schema.json**: Validation schema for graph pattern analysis exports
- **temporal-patterns.schema.json**: Schema for time-series pattern analysis
- **pattern-forecast.schema.json**: Schema for forecasting model outputs
- **graph-stats.schema.json**: Schema for graph statistics and metrics
- **graph-correlations.schema.json**: Schema for concept correlation data

### Contract Documents
- **graph-metrics-api.md**: API contract for graph metrics endpoints
- **graph-stats-api.md**: API contract for statistics endpoints
- **visualization-config.md**: Configuration contract for visualization components
- **webui-contract.md**: Contract between backend and frontend visualization

### Reference Documents
- **data_flow.md**: Data flow diagrams and pipeline architecture
- **data_flow_visual.md**: Visual representations of data flows
- **jsonld-schema.md**: JSON-LD and semantic web standards
- **rdf-ontology.md**: RDF ontology definitions and namespaces

## SSOT Standards

### Schema Validation
- **JSON Schema**: All schemas follow JSON Schema Draft 2020-12
- **Versioning**: Schema versions tracked in filenames and content
- **Backwards Compatibility**: Schema changes maintain backwards compatibility
- **Documentation**: All schemas include inline documentation

### Contract Compliance
- **Interface Definition**: Clear input/output specifications
- **Error Handling**: Defined error responses and codes
- **Versioning**: API version compatibility guarantees
- **Testing**: Contract tests validate compliance

### Document Maintenance
- **Single Source**: Each specification has one authoritative location
- **Cross-references**: Links between related specifications
- **Update Process**: Controlled process for specification changes
- **Validation**: Automated validation of specification compliance

## Development Integration

### Code Generation
- **Type Hints**: Generate Python type hints from schemas
- **Validation Code**: Auto-generate input validation from contracts
- **Test Data**: Generate test fixtures from schema examples

### Quality Gates
- **Schema Validation**: All exports validated against schemas
- **Contract Testing**: API compliance verified against contracts
- **Cross-reference Checks**: Specification links verified and current

## Usage Guidelines

### For Developers
1. **Reference SSOT**: Always reference these documents for specifications
2. **Validate Changes**: Ensure changes don't break existing contracts
3. **Update Documents**: Modify specifications when interfaces change
4. **Test Compliance**: Verify implementations meet specification requirements

### For Reviewers
1. **Check References**: Ensure code references correct SSOT documents
2. **Validate Contracts**: Verify API changes update contracts
3. **Schema Compliance**: Confirm data structures match schemas
4. **Documentation Sync**: Ensure docs reflect current implementation

## Related ADRs

| Document | Related ADRs | Description |
|----------|--------------|-------------|
| graph-patterns.schema.json | ADR-016 | Graph pattern analysis specification |
| temporal-patterns.schema.json | ADR-034 | Temporal pattern analysis framework |
| pattern-forecast.schema.json | ADR-025 | Forecasting model specifications |
| webui-contract.md | ADR-022 | Backend-frontend visualization contract |
