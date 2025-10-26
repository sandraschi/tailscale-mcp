# Grafana Configuration and Dashboard Documentation

This document provides comprehensive information about Grafana configuration, dashboards, and usage in the Tailscale MCP monitoring stack.

## 📊 Grafana Overview

Grafana serves as the visualization layer of the monitoring stack, providing interactive dashboards, alerting, and data exploration capabilities.

### Key Features

- **Real-time dashboards** with auto-refresh
- **Interactive visualizations** with drill-down capabilities
- **Alert management** with notification channels
- **Data source integration** with Prometheus and Loki
- **User management** and access control
- **Dashboard provisioning** for automated setup

## 🔧 Configuration

### Basic Configuration

**Access**: http://localhost:3000
**Default Credentials**: admin/admin
**Theme**: Dark mode (configurable)

### Data Sources

#### Prometheus Data Source

```yaml
Name: Prometheus
Type: prometheus
URL: http://prometheus:9090
Access: Proxy
Default: true
```

**Configuration**:
- **Scrape Interval**: 15 seconds
- **Query Timeout**: 60 seconds
- **HTTP Method**: POST
- **Basic Auth**: Disabled

#### Loki Data Source

```yaml
Name: Loki
Type: loki
URL: http://loki:3100
Access: Proxy
```

**Configuration**:
- **Max Lines**: 1000
- **Derived Fields**: Trace ID extraction
- **Basic Auth**: Disabled

### Dashboard Provisioning

Dashboards are automatically provisioned from JSON files in the `monitoring/grafana/dashboards/` directory.

**Provisioning Configuration**:
```yaml
apiVersion: 1
providers:
  - name: 'Tailscale MCP Dashboards'
    orgId: 1
    folder: 'Tailscale MCP'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

## 📈 Available Dashboards

### 1. Tailscale Network Overview

**Purpose**: High-level overview of the Tailscale network status and performance.

**Key Panels**:
- **Network Health Status**: Overall system health indicator
- **Device Statistics**: Total, online, offline device counts
- **Network Traffic**: Bytes sent/received over time
- **Device Connectivity Status**: Table of device connection details
- **API Request Rate**: Request frequency by endpoint
- **API Response Times**: Performance metrics with percentiles
- **Error Rate**: Client and server error rates
- **Device Activity Timeline**: Activity patterns over time

**Use Cases**:
- Network health monitoring
- Performance analysis
- Capacity planning
- Troubleshooting connectivity issues

### 2. Tailscale Logs Dashboard

**Purpose**: Comprehensive log analysis and monitoring.

**Key Panels**:
- **Log Level Distribution**: Pie chart of log levels
- **Error Rate Over Time**: Error frequency tracking
- **Top Error Messages**: Most common error patterns
- **Device Operations Log**: Real-time device operation logs
- **Network Operations Log**: Network-related log entries
- **File Transfer Operations**: Taildrop operation logs
- **Security Events**: Authentication and security logs
- **Log Volume Over Time**: Log generation rate
- **All Logs Stream**: Complete log stream

**Use Cases**:
- Error analysis and debugging
- Security monitoring
- Operational troubleshooting
- Log pattern analysis

### 3. Device Activity Dashboard

**Purpose**: Detailed device monitoring and activity analysis.

**Key Panels**:
- **Device Status Overview**: Statistical summary of device states
- **Device Activity Heatmap**: Visual activity patterns
- **Device Connection Status**: Detailed device information table
- **Device Authorization Events**: Authorization activity tracking
- **Device Activity by Type**: Activity breakdown by type
- **Device Last Seen Timeline**: Connection history
- **Device Network Traffic**: Per-device traffic analysis
- **Device Geolocation Map**: Geographic distribution of devices
- **Device Activity Log**: Real-time device activity logs

**Use Cases**:
- Device management
- Security monitoring
- Geographic analysis
- Activity pattern analysis

### 4. Comprehensive Monitoring Dashboard

**Purpose**: Combined overview of all monitoring aspects.

**Key Panels**:
- **System Health Overview**: All service status indicators
- **Tailscale Network Status**: Network-level statistics
- **Network Traffic & Performance**: Combined traffic and performance metrics
- **Error Rate & Log Volume**: Error and logging analysis
- **Device Activity Timeline**: Device activity over time
- **File Transfer Activity**: Taildrop operation monitoring
- **Real-time Log Stream**: Live log monitoring
- **Error Logs Stream**: Error-focused log stream
- **Device Status Table**: Comprehensive device information

**Use Cases**:
- Executive dashboard
- System overview
- Comprehensive monitoring
- Incident response

## 🎯 Dashboard Features

### Real-time Updates

- **Auto-refresh**: 5-10 second intervals
- **Live data**: Real-time metrics and logs
- **Interactive elements**: Clickable charts and tables
- **Drill-down capabilities**: Detailed views from summary panels

### Visualization Types

- **Stat panels**: Key metrics and indicators
- **Graph panels**: Time-series data visualization
- **Table panels**: Tabular data display
- **Log panels**: Log stream visualization
- **Heatmap panels**: Activity pattern visualization
- **Geomap panels**: Geographic data visualization
- **Pie chart panels**: Distribution visualization

### Interactive Features

- **Time range selection**: Flexible time period selection
- **Variable substitution**: Dynamic dashboard variables
- **Panel linking**: Navigation between related panels
- **Annotation support**: Event marking on timelines
- **Export capabilities**: Dashboard and panel export

## 🔍 Query Examples

### Prometheus Queries

#### Device Metrics
```promql
# Total devices
tailscale_devices_total

# Online devices
tailscale_devices_online_total

# Device activity rate
rate(tailscale_device_activity_total[5m])

# API response times
histogram_quantile(0.95, rate(tailscale_api_request_duration_seconds_bucket[5m]))
```

#### Network Metrics
```promql
# Network traffic
rate(tailscale_network_bytes_sent_total[5m])

# Error rates
rate(tailscale_api_requests_total{status=~"5.."}[5m])

# Device connectivity
tailscale_device_info
```

### LogQL Queries

#### Log Analysis
```logql
# All Tailscale MCP logs
{job="tailscale-mcp"}

# Error logs only
{job="tailscale-mcp"} |= "ERROR"

# Device operations
{job="tailscale-mcp"} |= "device"

# Network operations
{job="tailscale-mcp"} |= "network" or |= "traffic"

# Security events
{job="tailscale-mcp"} |= "security" or |= "auth" or |= "unauthorized"
```

#### Advanced Log Queries
```logql
# Logs with specific labels
{job="tailscale-mcp", level="ERROR"}

# Logs with regex matching
{job="tailscale-mcp"} |~ "device.*authorize"

# Log aggregation
sum(rate({job="tailscale-mcp"}[5m])) by (level)

# Log filtering with time range
{job="tailscale-mcp"}[5m]
```

## 🚨 Alerting Configuration

### Alert Rules

#### Service Health Alerts
```yaml
- alert: ServiceDown
  expr: up{job="tailscale-mcp"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Tailscale MCP service is down"
    description: "The Tailscale MCP service has been down for more than 1 minute"
```

#### Error Rate Alerts
```yaml
- alert: HighErrorRate
  expr: rate(tailscale_api_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is above 0.1 errors per second"
```

#### Device Connectivity Alerts
```yaml
- alert: DeviceOffline
  expr: tailscale_devices_offline_total > tailscale_devices_total * 0.5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Many devices offline"
    description: "More than 50% of devices are offline"
```

### Notification Channels

#### Email Notifications
```yaml
- name: email-alerts
  type: email
  settings:
    addresses: admin@example.com
    subject: "[Alert] {{ .GroupLabels.alertname }}"
```

#### Slack Integration
```yaml
- name: slack-alerts
  type: slack
  settings:
    url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
    channel: "#alerts"
    title: "Tailscale MCP Alert"
    text: "{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.description }}"
```

## 🛠️ Customization

### Dashboard Variables

#### Time Range Variables
```json
{
  "name": "time_range",
  "type": "interval",
  "label": "Time Range",
  "query": "1m,5m,15m,1h,6h,12h,1d,7d,30d",
  "current": {
    "text": "1h",
    "value": "1h"
  }
}
```

#### Device Selection Variables
```json
{
  "name": "device",
  "type": "query",
  "label": "Device",
  "query": "label_values(tailscale_device_info, device_name)",
  "multi": true,
  "includeAll": true
}
```

### Custom Panels

#### Device Status Panel
```json
{
  "title": "Device Status",
  "type": "stat",
  "targets": [
    {
      "expr": "tailscale_devices_online_total",
      "legendFormat": "Online Devices"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "unit": "short"
    }
  }
}
```

#### Network Traffic Panel
```json
{
  "title": "Network Traffic",
  "type": "graph",
  "targets": [
    {
      "expr": "rate(tailscale_network_bytes_sent_total[5m])",
      "legendFormat": "Bytes Sent/sec"
    }
  ],
  "yAxes": [
    {
      "label": "Bytes/sec",
      "unit": "bytes"
    }
  ]
}
```

## 📊 Best Practices

### Dashboard Design

1. **Logical Grouping**: Group related panels together
2. **Consistent Styling**: Use consistent colors and formatting
3. **Clear Titles**: Use descriptive panel titles
4. **Appropriate Time Ranges**: Set appropriate default time ranges
5. **Refresh Rates**: Balance real-time updates with performance

### Query Optimization

1. **Efficient Queries**: Use efficient PromQL and LogQL queries
2. **Appropriate Intervals**: Use appropriate query intervals
3. **Limit Results**: Limit query results to prevent overload
4. **Cache Results**: Use query caching where appropriate
5. **Index Usage**: Ensure proper indexing for log queries

### Performance Considerations

1. **Panel Count**: Limit the number of panels per dashboard
2. **Query Complexity**: Keep queries simple and efficient
3. **Refresh Intervals**: Use appropriate refresh intervals
4. **Data Retention**: Configure appropriate data retention
5. **Resource Usage**: Monitor Grafana resource usage

## 🔧 Troubleshooting

### Common Issues

#### Dashboard Not Loading
- Check data source connectivity
- Verify query syntax
- Check time range selection
- Verify data availability

#### Slow Dashboard Performance
- Reduce panel count
- Optimize queries
- Increase refresh intervals
- Check data source performance

#### Missing Data
- Verify data source configuration
- Check query syntax
- Verify time range
- Check data retention settings

### Debugging Steps

1. **Check Service Status**: Verify all services are running
2. **Check Data Sources**: Verify data source connectivity
3. **Check Queries**: Validate query syntax and results
4. **Check Logs**: Review Grafana logs for errors
5. **Check Resources**: Monitor system resources

## 📚 Additional Resources

### Documentation
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/)
- [LogQL Documentation](https://grafana.com/docs/loki/latest/logql/)

### Community
- [Grafana Community](https://community.grafana.com/)
- [Prometheus Community](https://prometheus.io/community/)
- [Loki Community](https://community.grafana.com/c/loki)

---

This documentation provides comprehensive guidance for using Grafana in the Tailscale MCP monitoring stack, from basic configuration to advanced customization and troubleshooting.
