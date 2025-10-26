# RebootX On-Prem Integration for Tailscale MCP

This directory contains the RebootX On-Prem integration for the Tailscale MCP monitoring stack, allowing you to manage and monitor your Tailscale infrastructure through the RebootX mobile app.

## 🚀 What is RebootX On-Prem?

**RebootX On-Prem** is an open-source specification for defining a custom server to manage on-premise _runnables_ and _dashboards_ in the [RebootX](https://c100k.eu/p/rebootx) mobile app.

- **Runnables**: Anything that runs, can be stopped and rebooted (VMs, servers, containers, applications, databases)
- **Dashboards**: Collections of numeric metrics (node counts, latency, bandwidth, etc.)

## 📱 RebootX Mobile App

The RebootX mobile app provides:
- **Mobile Infrastructure Monitoring**: Monitor your infrastructure from your smartphone
- **Remote Management**: Stop, reboot, and manage services remotely
- **Real-time Metrics**: View live metrics and dashboards
- **SSH Access**: Connect to servers directly from the app
- **Multi-platform Support**: Works with cloud providers and on-premises systems

### Pro Version Features
- **Advanced Monitoring**: Extended metrics and monitoring capabilities
- **Custom Dashboards**: Create personalized monitoring dashboards
- **Enhanced Security**: Additional security features and authentication
- **Priority Support**: Premium support and updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RebootX App   │────│  RebootX On-Prem │────│  Tailscale MCP  │
│   (Mobile)      │    │     Server       │    │   Monitoring    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Prometheus     │    │      Loki       │
│   Dashboards    │    │    Metrics       │    │   Log Aggregation│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Tailscale MCP monitoring stack running
- RebootX mobile app installed (iOS/Android)

### 2. Start RebootX On-Prem

```bash
# Navigate to the monitoring directory
cd monitoring/rebootx-on-prem

# Start RebootX On-Prem server
docker-compose -f docker-compose.rebootx.yml up -d

# Verify services are running
docker-compose -f docker-compose.rebootx.yml ps
```

### 3. Access Services

- **RebootX On-Prem API**: http://localhost:9001
- **Swagger UI**: http://localhost:9002
- **API Documentation**: http://localhost:9002/docs

### 4. Configure RebootX App

1. Open the RebootX mobile app
2. Add a new server connection
3. Enter the following details:
   - **Server URL**: `http://your-server-ip:9001`
   - **API Key**: `tailscale-mcp-rebootx-key-2024`
   - **Path Prefix**: `tailscale-mcp`

## 📊 Available Runnables

The RebootX On-Prem server exposes the following runnables from your Tailscale MCP monitoring stack:

### Tailscale MCP Server
- **ID**: `tailscale-mcp-001`
- **Status**: On/Off
- **Metrics**: Active devices, network health, API response time, uptime
- **Actions**: Reboot, Stop

### Grafana Dashboard
- **ID**: `grafana-001`
- **Status**: On/Off
- **Metrics**: Dashboard views, query response time, active users
- **Actions**: Reboot, Stop

### Prometheus Metrics
- **ID**: `prometheus-001`
- **Status**: On/Off
- **Metrics**: Metrics scraped, scrape duration, storage usage
- **Actions**: Reboot, Stop

### Loki Log Aggregation
- **ID**: `loki-001`
- **Status**: On/Off
- **Metrics**: Log entries/sec, storage usage, query latency
- **Actions**: Reboot, Stop

## 📈 Available Dashboards

### Tailscale Network Overview
- Active devices count
- Network health score
- Total bandwidth usage
- API response time
- System uptime

### Monitoring Infrastructure
- Grafana dashboard views
- Prometheus metrics count
- Loki log entries per second
- Monitoring stack uptime

### Security Metrics
- Security scan results
- Failed authentication attempts
- Blocked IP addresses
- Overall security score

### Performance Metrics
- Average network latency
- Peak bandwidth usage
- CPU usage
- Memory usage

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REBOOTX_API_KEY` | API key for authentication | `tailscale-mcp-rebootx-key-2024` |
| `REBOOTX_PATH_PREFIX` | URL path prefix | `tailscale-mcp` |
| `RBTX_PORT` | Server port | `9001` |

### Customizing Runnables

Edit `servers.json` to customize the runnables:

```json
{
    "id": "custom-server",
    "name": "Custom Server",
    "status": "on",
    "metrics": [
        {
            "label": "Custom Metric",
            "value": 100,
            "unit": "units"
        }
    ]
}
```

### Customizing Dashboards

Edit `dashboards.json` to customize the dashboards:

```json
{
    "id": "custom-dashboard",
    "name": "Custom Dashboard",
    "metrics": [
        {
            "id": "custom-metric",
            "label": "Custom Metric",
            "value": 100
        }
    ]
}
```

## 🔒 Security

### API Authentication

The RebootX On-Prem server uses API key authentication:

```bash
# Test API access
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://localhost:9001/tailscale-mcp/runnables
```

### HTTPS Configuration

For production deployments, configure HTTPS:

```yaml
environment:
  - RBTX_PROTOCOL=https
  - RBTX_TLS_CERT=/path/to/cert.pem
  - RBTX_TLS_KEY=/path/to/key.pem
```

## 🚀 Deployment

### Local Development

```bash
# Start all services
docker-compose -f docker-compose.rebootx.yml up -d

# View logs
docker-compose -f docker-compose.rebootx.yml logs -f

# Stop services
docker-compose -f docker-compose.rebootx.yml down
```

### Production Deployment

1. **Configure HTTPS**: Set up SSL certificates
2. **Network Access**: Ensure the server is accessible from your mobile device
3. **Firewall**: Configure firewall rules for port 9001
4. **Monitoring**: Set up monitoring for the RebootX On-Prem server

## 📱 Mobile App Integration

### Adding the Server

1. Open RebootX mobile app
2. Tap "Add Server"
3. Enter server details:
   - **Name**: Tailscale MCP Monitoring
   - **URL**: `https://your-server.com:9001`
   - **API Key**: `tailscale-mcp-rebootx-key-2024`
   - **Path**: `tailscale-mcp`

### Using the App

- **View Runnables**: See all your Tailscale infrastructure components
- **Monitor Metrics**: View real-time metrics and dashboards
- **Control Services**: Start, stop, and reboot services
- **SSH Access**: Connect to servers directly
- **View Logs**: Access log information

## 🔧 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if the server is running: `docker-compose ps`
   - Verify port 9001 is accessible
   - Check firewall settings

2. **Authentication Failed**
   - Verify the API key matches the configuration
   - Check the Authorization header format

3. **No Data Showing**
   - Verify the JSON configuration files are valid
   - Check the server logs for errors
   - Ensure the monitoring stack is running

### Debugging

```bash
# View server logs
docker-compose -f docker-compose.rebootx.yml logs rebootx-on-prem

# Test API endpoints
curl -v -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://localhost:9001/tailscale-mcp/runnables

# Check service status
docker-compose -f docker-compose.rebootx.yml ps
```

## 📚 API Reference

### Endpoints

- `GET /{prefix}/runnables` - List all runnables
- `GET /{prefix}/dashboards` - List all dashboards
- `POST /{prefix}/runnables/{id}/reboot` - Reboot a runnable
- `POST /{prefix}/runnables/{id}/stop` - Stop a runnable

### Example API Calls

```bash
# List runnables
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://localhost:9001/tailscale-mcp/runnables

# List dashboards
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://localhost:9001/tailscale-mcp/dashboards

# Reboot a runnable
curl -X POST -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://localhost:9001/tailscale-mcp/runnables/tailscale-mcp-001/reboot
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the integration
5. Submit a pull request

## 📄 License

This integration follows the same license as the Tailscale MCP project.

## 🙏 Acknowledgments

- [RebootX](https://c100k.eu/p/rebootx) for the excellent mobile monitoring app
- [RebootX On-Prem](https://github.com/c100k/rebootx-on-prem) for the open-source specification
- Tailscale MCP team for the comprehensive monitoring stack
