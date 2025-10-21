# Grafana Dashboards

Monitoring and observability dashboards for Gemantria pipeline metrics.

## Overview

This directory contains Grafana dashboard configurations for visualizing:
- **Pipeline performance** metrics and throughput
- **Database health** and query performance
- **AI model metrics** and confidence scores
- **Network analysis** statistics and trends

## Dashboard Files

### `dashboards/gematria-metrics.json`
Main dashboard with:
- Pipeline run success/failure rates
- Node execution times and bottlenecks
- Database connection pool usage
- AI enrichment confidence distributions
- Semantic network growth metrics

## Setup Instructions

### Prerequisites
- **Grafana 8.0+** installed and running
- **PostgreSQL data source** configured in Grafana
- **Gematria database** accessible from Grafana

### Import Dashboard
1. Open Grafana web interface
2. Navigate to **Dashboards → Import**
3. Upload `dashboards/gematria-metrics.json`
4. Configure PostgreSQL data source
5. Adjust time ranges and refresh intervals

### Data Source Configuration
```yaml
# grafana/provisioning/datasources/gematria.yml
apiVersion: 1
datasources:
  - name: GematriaDB
    type: postgres
    url: localhost:5432
    database: gematria
    user: grafana_user
    secureJsonData:
      password: "your_password"
    jsonData:
      sslmode: "disable"
```

## Metrics Queries

The dashboard uses these key database views and tables:

### Views (from migrations/004_metrics_views.sql)
- `v_node_latency_7d` - Node execution latency over 7 days
- `v_node_throughput_24h` - Node throughput over 24 hours
- `v_recent_errors_7d` - Recent pipeline errors
- `v_pipeline_runs` - Pipeline run summaries

### Direct Tables
- `metrics_log` - Raw metrics data
- `ai_enrichment_log` - AI enrichment results
- `confidence_validation_log` - Validation outcomes
- `qwen_health_log` - Model health checks

## Dashboard Panels

### Pipeline Health
- Success rate over time
- Average execution time by node
- Error frequency and types

### Database Performance
- Query execution times
- Connection pool utilization
- Table growth statistics

### AI Quality
- Confidence score distributions
- Token usage patterns
- Model health indicators

### Network Analytics
- Node/edge growth over time
- Centrality metric trends
- Cluster size distributions

## Customization

### Adding New Panels
1. Edit the JSON dashboard file
2. Add new panel definitions with SQL queries
3. Test queries against the database
4. Import updated dashboard

### Time Range Variables
- Default: Last 24 hours
- Common ranges: 1h, 6h, 24h, 7d, 30d

### Refresh Intervals
- Default: 5 minutes
- Adjustable per dashboard/panel

## Alerting

Configure alerts for:
- Pipeline failures
- High latency nodes
- Low confidence scores
- Database connection issues

## Related Documentation

- [Metrics Logging](../AGENTS.md#runbook-metrics--logging)
- [Database Views](../migrations/README.md#migration-files)
- [Observability Setup](../AGENTS.md#runbook-observability-dashboards)
