# Monitoring Templates and Configurations

## Overview

This document provides reusable templates and configurations for implementing monitoring in heavyweight MCP servers. These templates are based on the analysis of existing monitoring implementations and follow established best practices.

## Template Structure

```
monitoring-templates/
├── docker-compose/
│   ├── docker-compose.yml
│   └── docker-compose.override.yml
├── prometheus/
│   ├── prometheus.yml
│   ├── rules/
│   │   ├── mcp-server.yml
│   │   └── system.yml
│   └── alerts/
│       ├── critical.yml
│       └── warning.yml
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml
│   │   └── dashboards/
│   │       └── dashboards.yml
│   └── dashboards/
│       ├── system-overview.json
│       ├── application-performance.json
│       ├── logs-dashboard.json
│       └── security-monitoring.json
├── loki/
│   └── loki.yml
├── promtail/
│   └── promtail.yml
├── scripts/
│   ├── start-monitoring.sh
│   ├── start-monitoring.ps1
│   └── health-check.sh
├── configs/
│   ├── .env.template
│   └── monitoring.env
└── docs/
    ├── README.md
    └── DEPLOYMENT.md
```

## Docker Compose Templates

### Basic Docker Compose Template

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main MCP Application
  mcp-server:
    build: .
    container_name: ${PROJECT_NAME}-mcp
    ports:
      - "${MCP_PORT:-8080}:8080"
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - PROMETHEUS_PORT=${PROMETHEUS_PORT:-9091}
      - TAILSCALE_API_KEY=${TAILSCALE_API_KEY}
      - TAILSCALE_TAILNET=${TAILSCALE_TAILNET}
    volumes:
      - ./logs:/app/logs
      - ./monitoring/promtail/promtail.yml:/etc/promtail/config.yml
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: ${PROJECT_NAME}-prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Loki - Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: ${PROJECT_NAME}-loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Promtail - Log shipping
  promtail:
    image: grafana/promtail:latest
    container_name: ${PROJECT_NAME}-promtail
    volumes:
      - ./monitoring/promtail:/etc/promtail
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: ${PROJECT_NAME}-grafana
    ports:
      - "${GRAFANA_PORT:-3000}:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
      - GF_SECURITY_ALLOW_EMBEDDING=true
      - GF_AUTH_ANONYMOUS_ENABLED=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  prometheus_data:
  loki_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

### Override Template for Development

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  mcp-server:
    environment:
      - LOG_LEVEL=DEBUG
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
      - /app/node_modules
    command: ["python", "-m", "tailscalemcp"]

  prometheus:
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=1h'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'

  grafana:
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
```

## Prometheus Configuration Templates

### Main Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: '${PROJECT_NAME}-cluster'
    replica: '${REPLICA_NAME:-replica-1}'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      timeout: 10s
      api_version: v2

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:9091']
    metrics_path: /metrics
    scrape_interval: 5s
    scrape_timeout: 5s
    honor_labels: true
    honor_timestamps: true

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'alertmanager'
    static_configs:
      - targets: ['alertmanager:9093']
    metrics_path: /metrics
    scrape_interval: 15s
```

### Alert Rules Template

```yaml
# rules/mcp-server.yml
groups:
  - name: mcp-server-alerts
    rules:
      - alert: MCPServerDown
        expr: up{job="mcp-server"} == 0
        for: 1m
        labels:
          severity: critical
          service: mcp-server
          team: platform
        annotations:
          summary: "MCP Server is down"
          description: "MCP Server {{ $labels.instance }} has been down for more than 1 minute"
          runbook_url: "https://docs.example.com/runbooks/mcp-server-down"

      - alert: MCPServerHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
          service: mcp-server
          team: platform
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests per second, which is above the threshold of 0.1"

      - alert: MCPServerHighMemoryUsage
        expr: process_resident_memory_bytes > 1000000000
        for: 5m
        labels:
          severity: warning
          service: mcp-server
          team: platform
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanize }} bytes, which is above the threshold of 1GB"

      - alert: MCPServerHighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
          service: mcp-server
          team: platform
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value | humanizePercentage }}, which is above the threshold of 80%"

      - alert: MCPServerSlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
          service: mcp-server
          team: platform
        annotations:
          summary: "Slow response time"
          description: "95th percentile response time is {{ $value }}s, which is above the threshold of 1s"

      - alert: MCPServerDiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
          service: mcp-server
          team: platform
        annotations:
          summary: "Low disk space"
          description: "Disk space is {{ $value | humanizePercentage }} available, which is below the threshold of 10%"
```

## Grafana Dashboard Templates

### System Overview Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "${PROJECT_NAME} - System Overview",
    "tags": ["${PROJECT_NAME}", "system", "overview"],
    "style": "dark",
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"mcp-server\"}",
            "legendFormat": "MCP Server",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {
                  "color": "red",
                  "value": 0
                },
                {
                  "color": "green",
                  "value": 1
                }
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 6,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx Errors/sec",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 6,
          "x": 18,
          "y": 0
        }
      },
      {
        "id": 4,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile",
            "refId": "B"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 5,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes",
            "legendFormat": "Resident Memory",
            "refId": "A"
          }
        ],
        "bufferConfig": {
          "defaults": {
            "unit": "bytes"
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 8
        }
      }
    ]
  }
}
```

### Application Performance Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "${PROJECT_NAME} - Performance",
    "tags": ["${PROJECT_NAME}", "performance", "metrics"],
    "style": "dark",
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m]) * 100",
            "legendFormat": "CPU Usage %",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes",
            "legendFormat": "Resident Memory",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Request Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile",
            "refId": "B"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile",
            "refId": "C"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 8
        }
      }
    ]
  }
}
```

### Logs Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "${PROJECT_NAME} - Logs",
    "tags": ["${PROJECT_NAME}", "logs", "debugging"],
    "style": "dark",
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Log Stream",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"mcp-server\"}",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 12,
          "w": 24,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Error Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"mcp-server\", level=\"error\"}",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 12,
          "w": 12,
          "x": 0,
          "y": 12
        }
      },
      {
        "id": 3,
        "title": "Warning Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"mcp-server\", level=\"warning\"}",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 12,
          "w": 12,
          "x": 12,
          "y": 12
        }
      }
    ]
  }
}
```

## Loki Configuration Template

```yaml
# loki.yml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_scheduler:
  max_outstanding_requests_per_tenant: 2048

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  max_cache_freshness_per_query: 10m
  split_queries_by_interval: 15m
  max_query_parallelism: 32
  max_streams_per_user: 10000
  max_line_size: 256000
  max_entries_limit_per_query: 5000
  max_query_series: 5000
  max_query_parallelism: 32
  max_streams_matchers_per_query: 1000
  max_concurrent_tail_requests: 10
  max_query_length: 721h
  max_query_lookback: 721h
  max_label_name_length: 1024
  max_label_value_length: 4096
  max_label_names_per_series: 30
  max_global_streams_per_user: 10000
  max_chunks_per_query: 2000000
  max_samples_per_query: 1000000
  max_series_per_query: 1000000
  max_query_parallelism: 32
  max_streams_matchers_per_query: 1000
  max_concurrent_tail_requests: 10
  max_query_length: 721h
  max_query_lookback: 721h
  max_label_name_length: 1024
  max_label_value_length: 4096
  max_label_names_per_series: 30
  max_global_streams_per_user: 10000
  max_chunks_per_query: 2000000
  max_samples_per_query: 1000000
  max_series_per_query: 1000000
```

## Promtail Configuration Template

```yaml
# promtail.yml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: mcp-server-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: mcp-server
          service: ${PROJECT_NAME}
          __path__: /app/logs/*.log

    pipeline_stages:
      - match:
          selector: '{job="mcp-server"}'
          stages:
            - json:
                expressions:
                  timestamp: timestamp
                  level: level
                  logger: logger
                  message: event
                  operation: operation
                  device_id: device_id
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
                operation:
                device_id:
                status:
                duration:
                bytes_sent:
                bytes_received:
            - output:
                source: message

  - job_name: system-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log

  - job_name: docker-logs
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: label
            values: ["logging=promtail"]

    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '${PROJECT_NAME}.*'
        target_label: job
        replacement: 'mcp-server'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: logstream
      - source_labels: ['__meta_docker_container_label_logging']
        target_label: __tmp_logging
        regex: 'true'

    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs: attrs
      - timestamp:
          source: attrs.time
          format: RFC3339Nano
      - labels:
          stream:
          container_name:
      - output:
          source: output
```

## Environment Configuration Templates

### Main Environment Template

```bash
# .env.template
# Project Configuration
PROJECT_NAME=mcp-server
REPLICA_NAME=replica-1

# Port Configuration
MCP_PORT=8080
GRAFANA_PORT=3000
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PORT=9091

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# Monitoring Configuration
ENABLE_MONITORING=true
ENABLE_ALERTING=true
ENABLE_LOGGING=true

# Optional: Alertmanager Configuration
ALERTMANAGER_WEBHOOK_URL=http://localhost:9093/api/v1/alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK

# Optional: External Services
EXTERNAL_PROMETHEUS_URL=http://external-prometheus:9090
EXTERNAL_LOKI_URL=http://external-loki:3100
```

### Development Environment Template

```bash
# .env.dev
# Project Configuration
PROJECT_NAME=mcp-server-dev
REPLICA_NAME=dev-replica

# Port Configuration
MCP_PORT=8081
GRAFANA_PORT=3001
PROMETHEUS_PORT=9091
PROMETHEUS_METRICS_PORT=9092

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# Monitoring Configuration
ENABLE_MONITORING=true
ENABLE_ALERTING=false
ENABLE_LOGGING=true

# Development specific
PYTHONUNBUFFERED=1
FLASK_ENV=development
FLASK_DEBUG=1
```

## Startup Script Templates

### Bash Startup Script

```bash
#!/bin/bash
# start-monitoring.sh

set -e

echo "Starting ${PROJECT_NAME} monitoring stack..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Create necessary directories
mkdir -p logs
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start the monitoring stack
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service health..."
for service in mcp-server prometheus loki grafana; do
    if docker-compose ps $service | grep -q "Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
    fi
done

echo "Monitoring stack started successfully!"
echo "Access Grafana at: http://localhost:${GRAFANA_PORT:-3000} (${GRAFANA_USER:-admin}/${GRAFANA_PASSWORD:-admin})"
echo "Access Prometheus at: http://localhost:${PROMETHEUS_PORT:-9090}"
echo "Access Loki at: http://localhost:3100"
echo "Access MCP Server at: http://localhost:${MCP_PORT:-8080}"
```

### PowerShell Startup Script

```powershell
# start-monitoring.ps1

# Ensure Docker is running
Write-Host "Checking Docker status..."
try {
    docker info | Out-Null
    Write-Host "Docker is running." -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop or your Docker daemon." -ForegroundColor Red
    exit 1
}

# Load environment variables
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Create necessary directories
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/prometheus/rules" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/grafana/provisioning/datasources" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/grafana/provisioning/dashboards" -Force | Out-Null

# Start the monitoring stack
Write-Host "Starting Docker containers..." -ForegroundColor Blue
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker Compose services started successfully!" -ForegroundColor Green
    Write-Host "Access Grafana at: http://localhost:3000 (admin/admin)" -ForegroundColor Green
    Write-Host "Access Prometheus at: http://localhost:9090" -ForegroundColor Green
    Write-Host "Access Loki at: http://localhost:3100" -ForegroundColor Green
    Write-Host "Access MCP Server at: http://localhost:8080" -ForegroundColor Green
} else {
    Write-Host "Failed to start Docker Compose services. Check the logs above for errors." -ForegroundColor Red
}
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

set -e

echo "Checking ${PROJECT_NAME} monitoring stack health..."

# Check Docker services
echo "Checking Docker services..."
for service in mcp-server prometheus loki grafana promtail; do
    if docker-compose ps $service | grep -q "Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
    fi
done

# Check HTTP endpoints
echo "Checking HTTP endpoints..."
for endpoint in "http://localhost:8080/health" "http://localhost:9090/-/healthy" "http://localhost:3100/ready" "http://localhost:3000/api/health"; do
    if curl -s -f "$endpoint" > /dev/null; then
        echo "✓ $endpoint is responding"
    else
        echo "✗ $endpoint is not responding"
    fi
done

# Check metrics endpoint
echo "Checking metrics endpoint..."
if curl -s -f "http://localhost:9091/metrics" > /dev/null; then
    echo "✓ Metrics endpoint is responding"
else
    echo "✗ Metrics endpoint is not responding"
fi

echo "Health check completed!"
```

## Usage Instructions

### 1. Copy Templates

```bash
# Copy the monitoring templates to your project
cp -r monitoring-templates/ your-project/monitoring/

# Rename project-specific files
cd your-project/monitoring/
mv .env.template .env
```

### 2. Customize Configuration

```bash
# Edit environment variables
vim .env

# Customize Prometheus configuration
vim prometheus/prometheus.yml

# Customize Grafana dashboards
vim grafana/dashboards/system-overview.json
```

### 3. Start Monitoring Stack

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start the monitoring stack
./scripts/start-monitoring.sh

# Check health
./scripts/health-check.sh
```

### 4. Access Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **MCP Server**: http://localhost:8080

## Customization Guidelines

### Project-Specific Customizations

1. **Update PROJECT_NAME** in all configuration files
2. **Customize port numbers** if needed
3. **Add project-specific metrics** to Prometheus configuration
4. **Create custom dashboards** for your specific use case
5. **Configure alert rules** based on your requirements

### Advanced Customizations

1. **Add Alertmanager** for alert routing
2. **Configure external services** (Slack, Discord, PagerDuty)
3. **Add custom log parsing** in Promtail configuration
4. **Create custom Grafana plugins** if needed
5. **Implement custom health checks** for your application

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports are already in use
2. **Permission issues**: Ensure Docker has proper permissions
3. **Configuration errors**: Validate YAML/JSON syntax
4. **Service startup failures**: Check Docker logs for errors

### Debug Commands

```bash
# Check service logs
docker-compose logs -f mcp-server
docker-compose logs -f prometheus
docker-compose logs -f loki
docker-compose logs -f grafana

# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Stop all services
docker-compose down
```

## Conclusion

These monitoring templates provide a comprehensive foundation for implementing observability in heavyweight MCP servers. By following these templates and customizing them for your specific needs, you can ensure consistent monitoring across all your MCP projects while maintaining flexibility for unique requirements.

The key is to start with the standard stack and gradually add project-specific metrics, dashboards, and alerts as needed. This approach ensures consistency while maintaining flexibility for unique requirements.
