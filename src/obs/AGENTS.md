# AGENTS.md - Observability Directory

## Directory Purpose

The `src/obs/` directory contains observability and monitoring components for the Gemantria pipeline. These components provide metrics collection, health monitoring, and external system integration for operational visibility.

## Agent Output Format

**Output shape:** 4 blocks (Goal, Commands, Evidence to return, Next gate)
**SSOT:** Rule 051 — Cursor Insight & Handoff (AlwaysApply)

## Key Components

### `prom_exporter.py` - Prometheus Metrics Exporter

**Purpose**: Export pipeline metrics to Prometheus for monitoring and alerting
**Key Functions**:

- `start_exporter()` - Initialize Prometheus HTTP server
- `update_metrics()` - Update gauge/histogram metrics from database
- `health_check()` - Provide liveness/readiness endpoints
  **Requirements**:
- **OpenMetrics format** compliance for Prometheus scraping
- **Real-time metrics** from pipeline execution data
- **Health endpoints** for Kubernetes/docker orchestration
- Configurable server port and update intervals

## Metrics Architecture

### Pipeline Metrics

- **Node execution times**: Duration histograms per pipeline node
- **Batch processing stats**: Batch size, success rates, error counts
- **Qwen health metrics**: Model availability, latency measurements
- **Database performance**: Query execution times and connection health

### System Metrics

- **Memory usage**: Process memory consumption tracking
- **API response times**: External service call performance
- **Error rates**: Node failure and recovery statistics
- **Throughput**: Items processed per time period

### Health Checks

- **Liveness probe**: Basic process health verification
- **Readiness probe**: Database connectivity and external service availability
- **Qwen health**: Model loading and inference capability verification

## Integration Points

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: "gematria-pipeline"
    static_configs:
      - targets: ["localhost:9108"] # Configurable port
    scrape_interval: 30s
```

### Grafana Dashboards

- **Pipeline Performance**: Node execution times and throughput
- **Qwen Health**: Model availability and inference latency
- **System Resources**: Memory, CPU, and database metrics
- **Error Monitoring**: Failure rates and recovery statistics

## Development Guidelines

### Adding New Metrics

1. **Define metric types** (gauge, counter, histogram, summary)
2. **Add collection logic** with appropriate error handling
3. **Update Grafana dashboards** for visualization
4. **Document metric semantics** and update alerting rules

### Testing Metrics

- **Unit tests**: Metric calculation accuracy
- **Integration tests**: Prometheus endpoint functionality
- **End-to-end tests**: Grafana dashboard data flow

## Performance Considerations

- **Low overhead**: Metrics collection <1% of total processing time
- **Memory efficient**: Bounded metric storage and cleanup
- **Network minimal**: Efficient Prometheus protocol usage
- **Scalable**: Support for high-frequency metric updates

## Dependencies

- **prometheus_client**: Python Prometheus client library
- **Infrastructure**: Database access for metric data
- **External**: Prometheus server for metric collection

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Infrastructure**: [../infra/AGENTS.md](../infra/AGENTS.md) - Metrics collection
- **Rules**: [.cursor/rules/006-agents-md-governance.mdc](../../.cursor/rules/006-agents-md-governance.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - Metrics schemas
* See .cursor/rules/050-ops-contract.mdc (AlwaysApply).
