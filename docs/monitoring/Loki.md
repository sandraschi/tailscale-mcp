# Loki Configuration and Log Analysis Documentation

This document provides comprehensive information about Loki configuration, log aggregation, and analysis in the Tailscale MCP monitoring stack.

## 📝 Loki Overview

Loki serves as the log aggregation and analysis layer of the monitoring stack, providing centralized log collection, storage, and querying capabilities.

### Key Features

- **Log aggregation** from multiple sources
- **Powerful query language** (LogQL) for log analysis
- **Efficient storage** with compression and indexing
- **Real-time log streaming** with live tail capabilities
- **Integration** with Prometheus and Grafana
- **Scalable architecture** with horizontal scaling

## 🔧 Configuration

### Basic Configuration

**Access**: http://localhost:3100
**Storage**: Filesystem-based
**Schema**: v11
**Retention**: 200 hours
**Query Engine**: LogQL

### Configuration File Structure

```yaml
# monitoring/loki/loki.yml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory
  storage:
    filesystem:
      directory: /loki/data
  retention_period: 200h

schema_config:
  configs:
    - from: 2020-10-27
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      period: 24h
```

## 📊 Log Collection

### Log Sources

#### Tailscale MCP Server Logs

**Source**: Application logs from the MCP server
**Format**: Structured JSON logs
**Location**: `/app/logs/tailscale-mcp*.log`

**Log Structure**:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "tailscalemcp.mcp_server",
  "event": "Starting Tailscale MCP Server",
  "version": "2.0.0",
  "host": "0.0.0.0",
  "port": 8080,
  "tailnet": "example.tailnet",
  "prometheus_port": 9091,
  "log_file": "logs/tailscale-mcp.log"
}
```

#### Docker Container Logs

**Source**: Docker container logs
**Format**: Docker log format
**Location**: Docker container stdout/stderr

**Log Structure**:
```json
{
  "log": "2024-01-01T12:00:00Z [INFO] Starting server",
  "stream": "stdout",
  "time": "2024-01-01T12:00:00Z"
}
```

#### System Logs

**Source**: System logs from the host
**Format**: System log format
**Location**: `/var/log/*.log`

### Log Parsing

#### Promtail Configuration

**File**: `monitoring/promtail/promtail.yml`

**Pipeline Stages**:
1. **Log Discovery**: Find log files
2. **Log Parsing**: Parse log format
3. **Label Extraction**: Extract labels
4. **Log Shipping**: Send to Loki

#### JSON Log Parsing

```yaml
pipeline_stages:
  - json:
      expressions:
        timestamp: timestamp
        level: level
        logger: logger
        message: event
        version: version
        host: host
        port: port
        tailnet: tailnet
        prometheus_port: prometheus_port
        log_file: log_file
        error: error
        operation: operation
        device_id: device_id
        device_name: device_name
        transfer_id: transfer_id
        file_path: file_path
        recipient: recipient
        status: status
        duration: duration
        bytes_sent: bytes_sent
        bytes_received: bytes_received
  - timestamp:
      source: timestamp
      format: RFC3339
  - labels:
      level:
      logger:
      version:
      host:
      port:
      tailnet:
      prometheus_port:
      log_file:
      error:
      operation:
      device_id:
      device_name:
      transfer_id:
      file_path:
      recipient:
      status:
      duration:
      bytes_sent:
      bytes_received:
  - output:
      source: message
```

## 🔍 LogQL Queries

### Basic Queries

#### Simple Log Selection
```logql
# All Tailscale MCP logs
{job="tailscale-mcp"}

# Logs with specific level
{job="tailscale-mcp", level="ERROR"}

# Logs with specific logger
{job="tailscale-mcp", logger="tailscalemcp.mcp_server"}

# Logs with specific tailnet
{job="tailscale-mcp", tailnet="example.tailnet"}
```

#### Text Filtering
```logql
# Logs containing specific text
{job="tailscale-mcp"} |= "device"

# Logs containing regex pattern
{job="tailscale-mcp"} |~ "device.*authorize"

# Logs not containing specific text
{job="tailscale-mcp"} != "debug"

# Logs not matching regex pattern
{job="tailscale-mcp"} !~ "debug.*"
```

### Advanced Queries

#### Log Aggregation
```logql
# Count logs by level
sum(count_over_time({job="tailscale-mcp"}[1h])) by (level)

# Rate of logs by level
sum(rate({job="tailscale-mcp"}[5m])) by (level)

# Top error messages
topk(10, sum by (message) (count_over_time({job="tailscale-mcp", level="ERROR"}[1h])))

# Log volume over time
sum(rate({job="tailscale-mcp"}[5m]))
```

#### Label-based Queries
```logql
# Logs by device
{job="tailscale-mcp", device_name="server-01"}

# Logs by operation
{job="tailscale-mcp", operation="authorize"}

# Logs by status
{job="tailscale-mcp", status="success"}

# Logs by error type
{job="tailscale-mcp", error="timeout"}
```

#### Time-based Queries
```logql
# Logs from last hour
{job="tailscale-mcp"}[1h]

# Logs from specific time range
{job="tailscale-mcp"}[2024-01-01T12:00:00Z:2024-01-01T13:00:00Z]

# Logs with time range and filtering
{job="tailscale-mcp", level="ERROR"}[1h]
```

### Complex Queries

#### Multi-condition Queries
```logql
# Device operations with errors
{job="tailscale-mcp"} |= "device" and |= "error"

# Network operations with specific status
{job="tailscale-mcp"} |= "network" and status="success"

# File transfer operations with duration
{job="tailscale-mcp"} |= "taildrop" and duration > 10
```

#### Aggregation with Filtering
```logql
# Error rate by device
sum(rate({job="tailscale-mcp", level="ERROR"}[5m])) by (device_name)

# Operation count by type
sum(count_over_time({job="tailscale-mcp"}[1h])) by (operation)

# Log volume by logger
sum(rate({job="tailscale-mcp"}[5m])) by (logger)
```

## 📊 Log Analysis

### Common Log Patterns

#### Device Operations
```logql
# Device authorization logs
{job="tailscale-mcp"} |= "device" and |= "authorize"

# Device connection logs
{job="tailscale-mcp"} |= "device" and |= "connect"

# Device status changes
{job="tailscale-mcp"} |= "device" and |= "status"
```

#### Network Operations
```logql
# Network traffic logs
{job="tailscale-mcp"} |= "network" and |= "traffic"

# Network connectivity logs
{job="tailscale-mcp"} |= "network" and |= "connectivity"

# Network performance logs
{job="tailscale-mcp"} |= "network" and |= "performance"
```

#### File Transfer Operations
```logql
# Taildrop transfer logs
{job="tailscale-mcp"} |= "taildrop" and |= "transfer"

# File upload logs
{job="tailscale-mcp"} |= "taildrop" and |= "upload"

# File download logs
{job="tailscale-mcp"} |= "taildrop" and |= "download"
```

#### Security Events
```logql
# Authentication logs
{job="tailscale-mcp"} |= "auth" and |= "login"

# Authorization logs
{job="tailscale-mcp"} |= "auth" and |= "authorize"

# Security violation logs
{job="tailscale-mcp"} |= "security" and |= "violation"
```

### Error Analysis

#### Error Classification
```logql
# All errors
{job="tailscale-mcp", level="ERROR"}

# Errors by type
{job="tailscale-mcp", level="ERROR"} |~ "timeout|connection|auth"

# Errors by device
{job="tailscale-mcp", level="ERROR"} and device_name != ""

# Errors by operation
{job="tailscale-mcp", level="ERROR"} and operation != ""
```

#### Error Trends
```logql
# Error rate over time
sum(rate({job="tailscale-mcp", level="ERROR"}[5m]))

# Error count by hour
sum(count_over_time({job="tailscale-mcp", level="ERROR"}[1h])) by (hour)

# Top error sources
topk(10, sum by (logger) (count_over_time({job="tailscale-mcp", level="ERROR"}[1h])))
```

## 🚨 Log-based Alerting

### Alert Rules

#### High Error Rate Alert
```yaml
- alert: HighErrorRate
  expr: sum(rate({job="tailscale-mcp", level="ERROR"}[5m])) > 0.1
  for: 2m
  labels:
    severity: warning
    service: tailscale-mcp
  annotations:
    summary: "High error rate detected in logs"
    description: "Error rate is above 0.1 errors per second for more than 2 minutes"
```

#### Critical Error Alert
```yaml
- alert: CriticalError
  expr: count_over_time({job="tailscale-mcp", level="ERROR"} |= "critical"[5m]) > 5
  for: 1m
  labels:
    severity: critical
    service: tailscale-mcp
  annotations:
    summary: "Critical errors detected"
    description: "More than 5 critical errors in the last 5 minutes"
```

#### Service Down Alert
```yaml
- alert: ServiceDown
  expr: absent_over_time({job="tailscale-mcp"}[5m])
  for: 1m
  labels:
    severity: critical
    service: tailscale-mcp
  annotations:
    summary: "Service appears to be down"
    description: "No logs received from Tailscale MCP service for more than 5 minutes"
```

## 🛠️ Configuration Management

### Environment Variables

```bash
# Loki configuration
LOKI_RETENTION_PERIOD=200h
LOKI_STORAGE_PATH=/loki/data
LOKI_HTTP_LISTEN_PORT=3100
LOKI_GRPC_LISTEN_PORT=9096

# Storage configuration
LOKI_STORAGE_TYPE=filesystem
LOKI_STORAGE_FILESYSTEM_DIRECTORY=/loki/data

# Query configuration
LOKI_QUERY_TIMEOUT=60s
LOKI_QUERY_MAX_CONCURRENCY=20
```

### Configuration Files

#### Main Configuration
- **File**: `monitoring/loki/loki.yml`
- **Purpose**: Main Loki configuration
- **Includes**: Server settings, storage configuration, schema settings

#### Promtail Configuration
- **File**: `monitoring/promtail/promtail.yml`
- **Purpose**: Log collection and shipping configuration
- **Includes**: Log sources, parsing pipelines, shipping configuration

## 📈 Performance Optimization

### Query Optimization

#### Efficient Queries
```logql
# Good: Use specific label selectors
{job="tailscale-mcp", level="ERROR"}

# Bad: Don't use broad selectors without filtering
{job="tailscale-mcp"}

# Good: Use appropriate time ranges
{job="tailscale-mcp", level="ERROR"}[1h]

# Bad: Don't use very long time ranges for frequent queries
{job="tailscale-mcp", level="ERROR"}[7d]
```

#### Index Usage
```logql
# Good: Use indexed labels
{job="tailscale-mcp", level="ERROR", logger="tailscalemcp.mcp_server"}

# Bad: Don't use non-indexed text filters without labels
{job="tailscale-mcp"} |= "error" |= "critical"
```

### Storage Optimization

#### Retention Policies
```yaml
# Short-term retention for high-volume logs
- name: short_term
  duration: 24h
  size_limit: 1GB

# Long-term retention for important logs
- name: long_term
  duration: 7d
  size_limit: 10GB
```

#### Data Compression
```yaml
# Enable data compression
storage:
  filesystem:
    directory: /loki/data
    compression: true
    compression_level: 1
```

## 🔧 Troubleshooting

### Common Issues

#### Log Collection Failures
- Check Promtail configuration
- Verify log file permissions
- Check network connectivity to Loki
- Verify log format parsing

#### High Storage Usage
- Reduce log retention period
- Enable log compression
- Filter out unnecessary logs
- Use log sampling for high-volume logs

#### Slow Queries
- Optimize query syntax
- Use appropriate time ranges
- Limit result sets
- Use label selectors instead of text filters

### Debugging Steps

1. **Check Log Sources**: Verify logs are being generated
2. **Check Promtail**: Verify log collection is working
3. **Check Loki**: Verify logs are being received
4. **Check Queries**: Validate query syntax and results
5. **Check Storage**: Monitor storage usage and performance

## 📚 Additional Resources

### Documentation
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/)

### Community
- [Loki Community](https://community.grafana.com/c/loki)
- [Loki GitHub](https://github.com/grafana/loki)
- [Loki Slack](https://grafana.slack.com/channels/loki)

---

This documentation provides comprehensive guidance for using Loki in the Tailscale MCP monitoring stack, from basic configuration to advanced log analysis and troubleshooting.
