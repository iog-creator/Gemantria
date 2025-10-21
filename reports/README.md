# Pipeline Reports & Generated Outputs

This directory contains automatically generated reports and outputs from the Gemantria semantic network pipeline runs. These files provide comprehensive documentation of pipeline execution, performance metrics, and analysis results.

## 📋 Purpose

The reports directory serves as the central repository for:

- **Execution Records**: Complete logs of pipeline runs with timestamps and parameters
- **Quality Metrics**: Validation results, confidence scores, and performance indicators
- **Analysis Outputs**: Graph statistics, centrality measures, and clustering results
- **Health Monitoring**: System status, model verification, and error tracking
- **Audit Trail**: Historical record of all pipeline executions and their outcomes

## 📁 Report Types

### Pipeline Execution Reports (`run_*.md`)

**Format**: Markdown files with comprehensive execution summaries
**Naming**: `run_{run_id}_{timestamp}.md`
**Contents**:
- Pipeline configuration and parameters
- Execution timeline and performance metrics
- Quality validation results
- Graph statistics and analysis summaries
- Error logs and troubleshooting information

**Example**:
```
run_87ec9234-7431-4536-bd5a-0e227d30c0eb_20251020_221737.md
```

### Pipeline Data Reports (`run_*.json`)

**Format**: Structured JSON with detailed execution data
**Naming**: `run_{run_id}_{timestamp}.json`
**Contents**:
- Complete pipeline configuration
- Step-by-step execution metrics
- Quality scores and validation results
- Graph topology and statistics
- Health check results and model verification

**Example**:
```
run_87ec9234-7431-4536-bd5a-0e227d30c0eb_20251020_221737.json
```

### Aggregated Reports (`run_aggregated_*.json`, `run_aggregated_*.md`)

**Format**: Combined reports across multiple pipeline runs
**Purpose**: Comparative analysis and trend identification
**Contents**:
- Multi-run performance comparisons
- Quality metric trends over time
- System health patterns
- Statistical aggregations across runs

## 📊 Report Contents

### Execution Summary

Each report includes:
- **Run ID**: Unique identifier for the pipeline execution
- **Timestamp**: When the pipeline started and completed
- **Configuration**: All environment variables and settings used
- **Performance**: Execution time, resource usage, throughput

### Quality Metrics

Quality validation results:
- **Gematria Accuracy**: Calculation verification scores
- **AI Confidence**: Model prediction confidence levels
- **Data Integrity**: Schema validation and consistency checks
- **Health Checks**: External service availability and performance

### Graph Analysis

Network structure insights:
- **Node Count**: Total concepts processed
- **Edge Count**: Total relationships discovered
- **Cluster Count**: Number of concept communities identified
- **Centrality Measures**: Degree, betweenness, eigenvector centrality distributions
- **Density Metrics**: Network connectivity and relationship strength statistics

### Error Tracking

Failure analysis and diagnostics:
- **Pipeline Errors**: Step failures with detailed error messages
- **Validation Failures**: Quality check failures with specific issues
- **Service Issues**: External dependency problems and resolutions
- **Recovery Actions**: Automatic recovery attempts and outcomes

## 🔍 Reading Reports

### Quick Status Check

For a quick overview of pipeline health:

```bash
# Check most recent report
ls -la reports/run_* | tail -1

# View execution summary
head -20 reports/run_*.md | tail -1

# Check for errors
grep -i "error\|fail" reports/run_*.md
```

### Detailed Analysis

For in-depth pipeline analysis:

```bash
# View full execution report
cat reports/run_{run_id}_{timestamp}.md

# Analyze JSON metrics
python -c "import json; print(json.load(open('reports/run_{run_id}_{timestamp}.json'))['quality_metrics'])"

# Compare multiple runs
ls reports/run_aggregated_*
```

### Programmatic Access

Reports can be processed programmatically:

```python
import json
from pathlib import Path

# Load latest report
reports_dir = Path("reports")
latest_report = max(reports_dir.glob("run_*.json"), key=lambda f: f.stat().st_mtime)

with open(latest_report) as f:
    data = json.load(f)

# Access metrics
node_count = data["graph_stats"]["node_count"]
quality_score = data["quality_metrics"]["overall_score"]
execution_time = data["performance"]["total_time_seconds"]
```

## 📈 Report Generation

### Automatic Generation

Reports are automatically created after every pipeline run:

```bash
# Pipeline execution automatically generates reports
python -m src.graph.graph --book Genesis

# Manual report generation
python scripts/generate_report.py --run-id abc123
```

### Report Lifecycle

- **Generation**: Created immediately after pipeline completion
- **Retention**: Configurable retention period (default: 30 days)
- **Archival**: Older reports moved to archival storage
- **Cleanup**: Automatic removal of expired reports

## 🎯 Report Categories

### Success Reports

- **Complete Execution**: All pipeline steps succeeded
- **Quality Thresholds Met**: All validation checks passed
- **Performance Acceptable**: Execution time within acceptable bounds
- **Data Integrity Verified**: All outputs meet quality standards

### Warning Reports

- **Partial Success**: Some steps completed with warnings
- **Quality Concerns**: Some validation checks flagged issues
- **Performance Issues**: Execution time exceeded expectations
- **Minor Errors**: Non-critical failures that didn't stop execution

### Failure Reports

- **Pipeline Failure**: Critical errors stopped execution
- **Quality Violations**: Severe validation failures
- **System Errors**: Infrastructure or dependency failures
- **Configuration Issues**: Invalid setup or parameters

## 🔧 Troubleshooting with Reports

### Identifying Issues

Use reports to diagnose problems:

1. **Check Execution Status**: Look for "FAILED" or "ERROR" indicators
2. **Review Error Logs**: Examine detailed error messages and stack traces
3. **Analyze Quality Metrics**: Identify validation failures and thresholds
4. **Examine Performance**: Check for bottlenecks or resource issues

### Common Issues

- **Qwen Live Gate Failures**: AI model availability issues
- **Database Connection Errors**: Infrastructure connectivity problems
- **Validation Failures**: Data quality or schema issues
- **Memory/Resource Limits**: Performance constraints exceeded

### Resolution Steps

1. **Review Configuration**: Check environment variables and settings
2. **Verify Dependencies**: Ensure external services are available
3. **Check Data Quality**: Validate input data integrity
4. **Monitor Resources**: Verify system has adequate resources

## 📋 Report Standards

### Naming Convention

- **Run ID**: UUID v7 format for uniqueness and sortability
- **Timestamp**: ISO 8601 format (YYYYMMDD_HHMMSS)
- **File Extensions**: `.md` for human-readable, `.json` for machine-readable

### Content Standards

- **Complete Information**: All execution details included
- **Structured Format**: Consistent JSON schema and Markdown structure
- **Error Details**: Comprehensive error information for debugging
- **Performance Data**: Detailed metrics for analysis and optimization

### Retention Policies

- **Active Reports**: Recent reports kept for immediate access
- **Archived Reports**: Older reports moved to long-term storage
- **Cleanup Schedule**: Automatic removal based on age and space constraints
- **Backup Strategy**: Critical reports backed up for audit purposes

## 🔄 Integration Points

### CI/CD Integration

Reports feed into continuous integration:

- **Quality Gates**: Report metrics determine deployment approval
- **Performance Tracking**: Historical performance data for trend analysis
- **Failure Analysis**: Automated issue detection and alerting
- **Audit Trail**: Complete record for compliance and debugging

### Monitoring Dashboards

Reports power monitoring systems:

- **Real-time Metrics**: Current pipeline health and performance
- **Historical Trends**: Performance and quality trends over time
- **Alerting**: Automated notifications for issues and anomalies
- **Reporting**: Executive summaries and detailed analytics

## 📚 Documentation

- **Report Schema**: See `docs/SSOT/` for JSON schema specifications
- **Generation Logic**: See `scripts/generate_report.py` for implementation details
- **ADR References**: ADR-013 covers report generation requirements

## 🤝 Usage Guidelines

### For Developers

- **Debugging**: Use reports to understand pipeline behavior and failures
- **Performance Analysis**: Review metrics to identify optimization opportunities
- **Quality Assurance**: Verify that validation checks are working correctly
- **System Monitoring**: Monitor pipeline health and reliability trends

### For Operators

- **Status Monitoring**: Check recent reports for system health
- **Issue Diagnosis**: Use detailed error information for troubleshooting
- **Performance Tracking**: Monitor execution times and resource usage
- **Quality Control**: Review validation results and quality metrics

### For Analysts

- **Data Access**: Programmatic access to structured metrics and results
- **Trend Analysis**: Compare reports across time periods and configurations
- **Research Insights**: Extract graph analysis and semantic network data
- **Quality Assessment**: Evaluate pipeline outputs and validation results
