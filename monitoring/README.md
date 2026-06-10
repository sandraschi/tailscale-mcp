# Tailscale MCP Monitoring Stack

This directory contains the complete monitoring stack for the Tailscale MCP server, including Grafana, Prometheus, and Loki for comprehensive observability.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Prometheus    │    │     Loki        │
│   (Port 3000)   │◄───┤   (Port 9090)   │    │   (Port 3100)   │
│                 │    │                 │    │                 │
│ • Dashboards    │    │ • Metrics       │    │ • Logs          │
│ • Alerts        │    │ • Rules         │    │ • Aggregation   │
│ • Visualization │    │ • Storage       │    │ • Querying      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Tailscale MCP   │
                    │   Server        │
                    │ (Port 8080/9091)│
                    │                 │
                    │ • Application   │
                    │ • Metrics       │
                    │ • Logs          │
                    └─────────────────┘
```

## 🚀 Quick Start

1. **Copy environment file:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` with your Tailscale credentials:**
   ```
   TAILSCALE_API_KEY=your_api_key_here
   TAILSCALE_TAILNET=your_tailnet_name_here
   ```

3. **Start the monitoring stack:**
   ```powershell
   .\scripts\start-monitoring.ps1
   ```

4. **Access the services:**
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **RebootX On-Prem API**: http://localhost:9001
   - **RebootX Swagger UI**: http://localhost:9002
   - **Prometheus**: http://localhost:9090
   - **Loki**: http://localhost:3100
   - **MCP Server**: http://localhost:8080

## 📱 RebootX On-Prem Integration

The monitoring stack includes RebootX On-Prem integration, allowing you to monitor and manage your Tailscale infrastructure from the RebootX mobile app.

### Features

- **Mobile Infrastructure Monitoring**: Monitor your infrastructure from your smartphone
- **Remote Management**: Stop, reboot, and manage services remotely
- **Real-time Metrics**: View live metrics and dashboards
- **SSH Access**: Connect to servers directly from the app

### Quick Start with RebootX

### RebootX Mobile Monitoring

RebootX (iPad/iPhone fleet health monitoring) has been moved to the **unified monitoring stack** at:
- **Docs**: [`mcp-central-docs/monitoring/REBOOTX_INTEGRATION.md`]
- **Docker Compose**: Part of `mcp-central-docs/monitoring/docker-compose.unified-monitoring.yml`
- **Port**: `12010`
- **API Key**: Set via `REBOOTX_API_KEY` env var (default: `unified-monitoring-rebootx-key`)

Run via the unified stack:
```powershell
cd mcp-central-docs/monitoring
.\start-unified-monitoring.ps1
```

## 📊 Grafana Dashboards

### Available Dashboards:
- **Tailscale MCP Overview**: Main dashboard with device status, network traffic, API metrics, and log stream
- **Device Management**: Detailed device metrics and management operations
- **Network Monitoring**: Network traffic, connectivity, and performance metrics
- **Security Dashboard**: Security events, authentication, and compliance metrics

### Dashboard Features:
- Real-time device status monitoring
- Network traffic visualization
- API response time tracking
- Error rate monitoring
- Log stream integration with Loki
- Custom alerts and notifications

## 🔍 Log Analysis with Loki

Loki provides powerful log aggregation and querying capabilities:

### Log Sources:
- Tailscale MCP server logs
- Docker container logs
- System logs
- Application-specific logs

### Query Examples:
```logql
# All Tailscale MCP logs
{job="tailscale-mcp"}

# Error logs only
{job="tailscale-mcp"} |= "ERROR"

# Logs from specific device operations
{job="tailscale-mcp"} |= "device" |= "authorize"

# Logs with specific time range
{job="tailscale-mcp"}[5m]
```

## 📈 Prometheus Metrics

### Available Metrics:
- `tailscale_devices_total` - Total number of devices
- `tailscale_devices_online_total` - Number of online devices
- `tailscale_network_bytes_sent_total` - Network bytes sent
- `tailscale_network_bytes_received_total` - Network bytes received
- `tailscale_api_request_duration_seconds` - API request duration histogram
- `tailscale_api_requests_total` - Total API requests by status code

### Query Examples:
```promql
# Device status
tailscale_devices_total

# Network throughput
rate(tailscale_network_bytes_sent_total[5m])

# API response times
histogram_quantile(0.95, rate(tailscale_api_request_duration_seconds_bucket[5m]))

# Error rate
rate(tailscale_api_requests_total{status=~"5.."}[5m])
```

## 🛠️ Configuration

### Prometheus Configuration
- **File**: `monitoring/prometheus/prometheus.yml`
- **Scrape Interval**: 15 seconds
- **Retention**: 200 hours
- **Targets**: MCP server, Grafana, Loki

### Loki Configuration
- **File**: `monitoring/loki/loki.yml`
- **Storage**: Filesystem-based
- **Retention**: Configurable
- **Schema**: v11

### Promtail Configuration
- **File**: `monitoring/promtail/promtail.yml`
- **Log Sources**: MCP server, Docker containers, system logs
- **Pipeline**: Structured log parsing and labeling

## 🔧 Customization

### Adding New Dashboards:
1. Create JSON dashboard file in `monitoring/grafana/dashboards/`
2. Restart Grafana or use provisioning
3. Access via Grafana UI

### Adding New Metrics:
1. Update MCP server code to expose new metrics
2. Add queries to Prometheus configuration
3. Create visualizations in Grafana

### Adding New Log Sources:
1. Update Promtail configuration
2. Add log parsing rules
3. Create log queries in Grafana

## 🚨 Alerts and Notifications

### Built-in Alerts:
- High error rate (>5% 5xx errors)
- Device connectivity issues
- API response time degradation
- Disk space warnings
- Memory usage alerts

### Alert Channels:
- Slack integration
- Email notifications
- PagerDuty integration
- Webhook notifications

## 📚 Useful Commands

```powershell
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f grafana
docker-compose logs -f prometheus
docker-compose logs -f loki

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Update services
docker-compose pull
docker-compose up -d
```

## 🔒 Security Considerations

- Change default Grafana admin password
- Use environment variables for sensitive data
- Consider network isolation for production
- Regular security updates for Docker images
- Monitor access logs and authentication

## 📖 Additional Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
