# Prometheus Configuration and Metrics Documentation

This document provides comprehensive information about Prometheus configuration, metrics collection, and usage in the Tailscale MCP monitoring stack.

## 📈 Prometheus Overview

Prometheus serves as the metrics collection and storage layer of the monitoring stack, providing time-series data collection, storage, and querying capabilities.

### Key Features

- **Time-series data collection** with pull-based scraping
- **Powerful query language** (PromQL) for data analysis
- **Alerting capabilities** with rule-based alerting
- **Service discovery** for automatic target discovery
- **Data retention** with configurable retention policies
- **High availability** with federation and clustering

## 🔧 Configuration

### Basic Configuration

**Access**: http://localhost:9090
**Data Retention**: 200 hours
**Scrape Interval**: 15 seconds
**Evaluation Interval**: 15 seconds

### Configuration File Structure

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  # Service-specific scrape configurations
```

## 📊 Metrics Collection

### Tailscale MCP Server Metrics

#### Application Metrics

**Endpoint**: http://tailscale-mcp:9091/metrics

**Key Metrics**:
- `tailscale_mcp_info` - Application information
- `tailscale_mcp_uptime_seconds` - Server uptime
- `tailscale_mcp_requests_total` - Total requests
- `tailscale_mcp_request_duration_seconds` - Request duration histogram

#### Device Metrics

**Device Status Metrics**:
```promql
# Total devices
tailscale_devices_total

# Online devices
tailscale_devices_online_total

# Offline devices
tailscale_devices_offline_total

# Authorized devices
tailscale_devices_authorized_total

# Pending devices
tailscale_devices_pending_total
```

**Device Information Metrics**:
```promql
# Device information
tailscale_device_info{device_id="...", device_name="...", status="online", os="linux", version="1.0.0"}

# Device last seen
tailscale_device_last_seen_seconds{device_id="...", device_name="..."}

# Device IP addresses
tailscale_device_ip_address{device_id="...", device_name="...", ip_address="100.64.1.1"}
```

#### Network Metrics

**Traffic Metrics**:
```promql
# Network bytes sent
tailscale_network_bytes_sent_total

# Network bytes received
tailscale_network_bytes_received_total

# Network packets sent
tailscale_network_packets_sent_total

# Network packets received
tailscale_network_packets_received_total
```

**Performance Metrics**:
```promql
# Network latency
tailscale_network_latency_seconds

# Network connectivity score
tailscale_network_connectivity_score

# Network throughput
tailscale_network_throughput_bytes_per_second
```

#### API Metrics

**Request Metrics**:
```promql
# API requests total
tailscale_api_requests_total{method="GET", endpoint="/api/v2/devices", status="200"}

# API request duration
tailscale_api_request_duration_seconds_bucket{method="GET", endpoint="/api/v2/devices", le="0.1"}

# API error rate
rate(tailscale_api_requests_total{status=~"5.."}[5m])
```

#### Device Activity Metrics

**Activity Tracking**:
```promql
# Device activity total
tailscale_device_activity_total{device_id="...", device_name="...", activity_type="connect"}

# Device authorization events
tailscale_device_authorizations_total{device_id="...", device_name="...", action="authorize"}

# Device operations
tailscale_device_operations_total{device_id="...", device_name="...", operation="rename"}
```

#### File Transfer Metrics (Taildrop)

**Transfer Metrics**:
```promql
# Taildrop transfers total
tailscale_taildrop_transfers_total{transfer_id="...", status="completed"}

# Taildrop bytes transferred
tailscale_taildrop_bytes_transferred_total{transfer_id="...", file_type="image"}

# Taildrop transfer duration
tailscale_taildrop_transfer_duration_seconds{transfer_id="...", status="completed"}
```

### System Metrics

#### Container Metrics

**Docker Container Metrics**:
```promql
# Container CPU usage
container_cpu_usage_seconds_total{name="tailscale-mcp"}

# Container memory usage
container_memory_usage_bytes{name="tailscale-mcp"}

# Container network I/O
container_network_receive_bytes_total{name="tailscale-mcp"}
container_network_transmit_bytes_total{name="tailscale-mcp"}
```

#### Node Metrics (if node_exporter is added)

**System Metrics**:
```promql
# CPU usage
node_cpu_seconds_total{mode="idle"}

# Memory usage
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes

# Disk usage
node_filesystem_size_bytes{device="/dev/sda1"}
node_filesystem_avail_bytes{device="/dev/sda1"}

# Network I/O
node_network_receive_bytes_total{device="eth0"}
node_network_transmit_bytes_total{device="eth0"}
```

## 🔍 Query Examples

### Basic Queries

#### Device Queries
```promql
# Current device count
tailscale_devices_total

# Device status over time
tailscale_devices_online_total

# Device activity rate
rate(tailscale_device_activity_total[5m])

# Top active devices
topk(10, sum by (device_name) (rate(tailscale_device_activity_total[5m])))
```

#### Network Queries
```promql
# Network traffic rate
rate(tailscale_network_bytes_sent_total[5m])

# Network throughput
rate(tailscale_network_bytes_sent_total[5m]) + rate(tailscale_network_bytes_received_total[5m])

# Network latency percentile
histogram_quantile(0.95, rate(tailscale_network_latency_seconds_bucket[5m]))
```

#### API Queries
```promql
# API request rate
rate(tailscale_api_requests_total[5m])

# API response time percentiles
histogram_quantile(0.50, rate(tailscale_api_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(tailscale_api_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(tailscale_api_request_duration_seconds_bucket[5m]))

# API error rate
rate(tailscale_api_requests_total{status=~"5.."}[5m])
```

### Advanced Queries

#### Aggregation Queries
```promql
# Total network traffic by device
sum by (device_name) (rate(tailscale_network_bytes_sent_total[5m]) + rate(tailscale_network_bytes_received_total[5m]))

# Average API response time
avg(rate(tailscale_api_request_duration_seconds_sum[5m]) / rate(tailscale_api_request_duration_seconds_count[5m]))

# Device connectivity percentage
(tailscale_devices_online_total / tailscale_devices_total) * 100
```

#### Time-based Queries
```promql
# Device activity over time
increase(tailscale_device_activity_total[1h])

# Network traffic trends
rate(tailscale_network_bytes_sent_total[1h])

# API performance trends
histogram_quantile(0.95, rate(tailscale_api_request_duration_seconds_bucket[1h]))
```

#### Conditional Queries
```promql
# Devices with high activity
tailscale_device_activity_total > 100

# API endpoints with high error rates
rate(tailscale_api_requests_total{status=~"5.."}[5m]) > 0.1

# Network with high latency
tailscale_network_latency_seconds > 0.1
```

## 🚨 Alerting Rules

### Service Health Alerts

#### Service Down Alert
```yaml
- alert: TailscaleMCPServiceDown
  expr: up{job="tailscale-mcp"} == 0
  for: 1m
  labels:
    severity: critical
    service: tailscale-mcp
  annotations:
    summary: "Tailscale MCP service is down"
    description: "The Tailscale MCP service has been down for more than 1 minute"
    runbook_url: "https://docs.example.com/runbooks/service-down"
```

#### High Error Rate Alert
```yaml
- alert: HighAPIErrorRate
  expr: rate(tailscale_api_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
    service: tailscale-mcp
  annotations:
    summary: "High API error rate detected"
    description: "API error rate is above 0.1 errors per second for more than 2 minutes"
    runbook_url: "https://docs.example.com/runbooks/high-error-rate"
```

### Device Alerts

#### Device Connectivity Alert
```yaml
- alert: ManyDevicesOffline
  expr: tailscale_devices_offline_total > tailscale_devices_total * 0.5
  for: 5m
  labels:
    severity: warning
    service: tailscale-mcp
  annotations:
    summary: "Many devices are offline"
    description: "More than 50% of devices are offline for more than 5 minutes"
    runbook_url: "https://docs.example.com/runbooks/device-connectivity"
```

#### Device Activity Alert
```yaml
- alert: LowDeviceActivity
  expr: rate(tailscale_device_activity_total[5m]) < 0.1
  for: 10m
  labels:
    severity: info
    service: tailscale-mcp
  annotations:
    summary: "Low device activity detected"
    description: "Device activity rate is below 0.1 activities per second for more than 10 minutes"
    runbook_url: "https://docs.example.com/runbooks/low-activity"
```

### Performance Alerts

#### High Response Time Alert
```yaml
- alert: HighAPIResponseTime
  expr: histogram_quantile(0.95, rate(tailscale_api_request_duration_seconds_bucket[5m])) > 1.0
  for: 3m
  labels:
    severity: warning
    service: tailscale-mcp
  annotations:
    summary: "High API response time detected"
    description: "95th percentile API response time is above 1 second for more than 3 minutes"
    runbook_url: "https://docs.example.com/runbooks/high-response-time"
```

#### High Network Latency Alert
```yaml
- alert: HighNetworkLatency
  expr: tailscale_network_latency_seconds > 0.5
  for: 2m
  labels:
    severity: warning
    service: tailscale-mcp
  annotations:
    summary: "High network latency detected"
    description: "Network latency is above 0.5 seconds for more than 2 minutes"
    runbook_url: "https://docs.example.com/runbooks/high-latency"
```

## 📊 Scrape Configuration

### Target Configuration

#### Tailscale MCP Server
```yaml
- job_name: 'tailscale-mcp'
  static_configs:
    - targets: ['tailscale-mcp:9091']
  scrape_interval: 10s
  metrics_path: /metrics
  honor_labels: true
  scrape_timeout: 5s
```

#### Prometheus Self-monitoring
```yaml
- job_name: 'prometheus'
  static_configs:
    - targets: ['localhost:9090']
  scrape_interval: 15s
  metrics_path: /metrics
```

#### Grafana Metrics
```yaml
- job_name: 'grafana'
  static_configs:
    - targets: ['grafana:3000']
  scrape_interval: 30s
  metrics_path: /metrics
```

#### Loki Metrics
```yaml
- job_name: 'loki'
  static_configs:
    - targets: ['loki:3100']
  scrape_interval: 30s
  metrics_path: /metrics
```

### Service Discovery

#### Docker Service Discovery
```yaml
- job_name: 'docker-containers'
  docker_sd_configs:
    - host: unix:///var/run/docker.sock
      refresh_interval: 30s
  relabel_configs:
    - source_labels: [__meta_docker_container_name]
      regex: 'tailscale.*'
      target_label: job
      replacement: 'tailscale-mcp'
```

## 🛠️ Configuration Management

### Environment Variables

```bash
# Prometheus configuration
PROMETHEUS_RETENTION=200h
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s

# Storage configuration
PROMETHEUS_STORAGE_PATH=/prometheus
PROMETHEUS_STORAGE_RETENTION=200h

# Alerting configuration
PROMETHEUS_ALERTMANAGER_URL=http://alertmanager:9093
```

### Configuration Files

#### Main Configuration
- **File**: `monitoring/prometheus/prometheus.yml`
- **Purpose**: Main Prometheus configuration
- **Includes**: Global settings, scrape configs, alerting rules

#### Alert Rules
- **Directory**: `monitoring/prometheus/rules/`
- **Purpose**: Alert rule definitions
- **Format**: YAML files with alert rules

#### Recording Rules
- **Directory**: `monitoring/prometheus/rules/`
- **Purpose**: Pre-computed metrics
- **Format**: YAML files with recording rules

## 📈 Performance Optimization

### Query Optimization

#### Efficient Queries
```promql
# Good: Use rate() for counters
rate(tailscale_api_requests_total[5m])

# Bad: Don't use increase() for short time ranges
increase(tailscale_api_requests_total[5m])

# Good: Use appropriate time ranges
rate(tailscale_api_requests_total[1h])

# Bad: Don't use very short time ranges for slow-changing metrics
rate(tailscale_devices_total[5m])
```

#### Index Usage
```promql
# Good: Use specific label selectors
tailscale_device_info{device_name="server-01"}

# Bad: Don't use regex when possible
tailscale_device_info{device_name=~"server-.*"}
```

### Storage Optimization

#### Retention Policies
```yaml
# Short-term retention for high-cardinality metrics
- name: short_term
  duration: 24h
  size_limit: 1GB

# Long-term retention for aggregated metrics
- name: long_term
  duration: 30d
  size_limit: 10GB
```

#### Data Compression
```yaml
# Enable data compression
storage:
  tsdb:
    compression: true
    compression_level: 1
```

## 🔧 Troubleshooting

### Common Issues

#### Scrape Failures
- Check target connectivity
- Verify metrics endpoint availability
- Check firewall rules
- Verify authentication credentials

#### High Memory Usage
- Reduce scrape frequency
- Limit label cardinality
- Increase retention period
- Use recording rules for aggregation

#### Slow Queries
- Optimize query syntax
- Use appropriate time ranges
- Limit result sets
- Use recording rules for complex queries

### Debugging Steps

1. **Check Target Status**: Verify all targets are up
2. **Check Metrics**: Verify metrics are being collected
3. **Check Queries**: Validate query syntax and results
4. **Check Storage**: Monitor storage usage and performance
5. **Check Logs**: Review Prometheus logs for errors

## 📚 Additional Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)

### Community
- [Prometheus Community](https://prometheus.io/community/)
- [Prometheus Users](https://groups.google.com/forum/#!forum/prometheus-users)
- [Prometheus Developers](https://groups.google.com/forum/#!forum/prometheus-developers)

---

This documentation provides comprehensive guidance for using Prometheus in the Tailscale MCP monitoring stack, from basic configuration to advanced querying and alerting.
