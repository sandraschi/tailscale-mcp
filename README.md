# TailscaleMCP

A FastMCP 2.12 compliant server for managing Tailscale networks with modern Python tooling and comprehensive CI/CD.

[![CI/CD Pipeline](https://github.com/yourusername/tailscalemcp/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/tailscalemcp/actions)
[![codecov](https://codecov.io/gh/yourusername/tailscalemcp/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/tailscalemcp)
[![PyPI version](https://badge.fury.io/py/tailscalemcp.svg)](https://badge.fury.io/py/tailscalemcp)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **🔧 Portmanteau Tools**: Consolidated tools following the database-mcp pattern to avoid tool explosion
  - `tailscale_device`: Comprehensive device management (list, authorize, rename, tag, SSH, search, stats, exit nodes, subnet routing, user management, auth keys)
  - `tailscale_network`: DNS and network management (MagicDNS, DNS records, resolution, policies, statistics)
  - `tailscale_monitor`: Monitoring and metrics (status, Prometheus metrics, topology, health reports, Grafana dashboards)
  - `tailscale_file`: File sharing via Taildrop (send, receive, transfer management, statistics)
  - `tailscale_security`: Security and compliance (scanning, auditing, threat detection, policy management, alerting)
  - `tailscale_automation`: Workflow automation (workflows, scripts, batch operations, scheduling)
  - `tailscale_backup`: Backup and disaster recovery (backup creation, restoration, scheduling, testing)
  - `tailscale_performance`: Performance monitoring (latency, bandwidth, optimization, capacity planning)
  - `tailscale_reporting`: Advanced reporting (custom reports, analytics, scheduling, export)
  - `tailscale_integration`: Third-party integrations (webhooks, Slack, Discord, PagerDuty, Datadog)
- **📊 Comprehensive Monitoring Stack**: Complete observability with Grafana, Prometheus, and Loki
  - **Real-time dashboards** for network visualization and device monitoring
  - **Structured logging** with JSON format for easy parsing and analysis
  - **Prometheus metrics** for performance monitoring and alerting
  - **Log aggregation** with Loki for centralized log analysis
  - **Docker Compose** setup for easy deployment and management
- **📈 Grafana Dashboards**: 4 comprehensive dashboards for different monitoring needs
  - Network Overview: Device status, traffic, API performance
  - Logs Dashboard: Error analysis, log streams, security events
  - Device Activity: Activity heatmaps, geolocation, timelines
  - Comprehensive Monitoring: Combined overview of all metrics and logs
- **🔍 Network Topology**: Visual network topology and device relationships
- **⚡ Prometheus Metrics**: Export metrics for monitoring systems with custom metrics
- **🏥 Health Reports**: Automated health analysis and recommendations
- **📝 Structured Logging**: JSON-formatted logs with rich context for Loki integration
- **Modern Tooling**: FastMCP 2.12, Ruff, Pytest, structured logging
- **Container Ready**: Docker support with development and production images
- **CI/CD**: Comprehensive GitHub Actions pipeline with security scanning

## 🎯 Usage

### Portmanteau Tools

The TailscaleMCP server uses **portmanteau tools** following the database-mcp pattern to avoid tool explosion. Each tool combines multiple related operations:

#### Device Management (`tailscale_device`)

```python
# List all devices
await tailscale_device(operation="list", online_only=True)

# Get device details
await tailscale_device(operation="get", device_id="device123")

# Authorize a device
await tailscale_device(operation="authorize", device_id="device123", authorize=True, reason="New employee")

# Rename device
await tailscale_device(operation="rename", device_id="device123", name="john-laptop")

# Add tags to device
await tailscale_device(operation="tag", device_id="device123", tags=["engineering", "laptop"])

# Enable SSH access
await tailscale_device(operation="ssh", device_id="device123", public_key="ssh-rsa...", key_name="john-key")

# Search devices
await tailscale_device(operation="search", search_query="engineering", search_fields=["name", "tags"])

# Enable exit node
await tailscale_device(operation="exit_node", device_id="device123", enable_exit_node=True, advertise_routes=["0.0.0.0/0"])
```

#### Network Management (`tailscale_network`)

```python
# Get DNS configuration
await tailscale_network(operation="dns_config")

# Configure MagicDNS
await tailscale_network(operation="magic_dns", enabled=True, override_local_dns=False)

# Add DNS record
await tailscale_network(operation="dns_record", name="api.internal", record_type="A", value="100.64.0.1")

# Resolve hostname
await tailscale_network(operation="resolve", hostname="api.internal", record_type="A")

# Add search domain
await tailscale_network(operation="search_domain", domain="internal", enabled=True)

# Create network policy
await tailscale_network(operation="policy", policy_name="restrict-api", rules=[{"action": "accept", "src": ["engineering"], "dst": ["api:*"]}])
```

#### Monitoring (`tailscale_monitor`)

```python
# Get network status
await tailscale_monitor(operation="status")

# Get network metrics
await tailscale_monitor(operation="metrics")

# Get Prometheus metrics
await tailscale_monitor(operation="prometheus")

# Generate network topology
await tailscale_monitor(operation="topology")

# Get health report
await tailscale_monitor(operation="health")

# Create Grafana dashboard
await tailscale_monitor(operation="dashboard", grafana_url="http://grafana:3000", api_key="your-api-key")

# Export dashboard
await tailscale_monitor(operation="export", filename="tailscale-dashboard.json", dashboard_type="comprehensive")
```

#### File Sharing (`tailscale_file`)

```python
# Send file via Taildrop
await tailscale_file(operation="send", file_path="/path/to/file.txt", recipient_device="device123", sender_device="device456")

# Receive file
await tailscale_file(operation="receive", transfer_id="transfer123", save_path="/downloads/")

# List active transfers
await tailscale_file(operation="list", status_filter="active")

# Cancel transfer
await tailscale_file(operation="cancel", transfer_id="transfer123")

# Get transfer status
await tailscale_file(operation="status", transfer_id="transfer123")

# Get Taildrop statistics
await tailscale_file(operation="stats")
```

#### Security Management (`tailscale_security`)

```python
# Security vulnerability scan
await tailscale_security(operation="scan", scan_type="comprehensive")

# Compliance validation
await tailscale_security(operation="compliance", compliance_standard="SOC2")

# Device security audit
await tailscale_security(operation="audit", device_id="device123")

# Generate security report
await tailscale_security(operation="report")

# Monitor suspicious activity
await tailscale_security(operation="monitor")

# Block malicious IP
await tailscale_security(operation="block", ip_address="192.168.1.100", block_duration=3600)

# Quarantine compromised device
await tailscale_security(operation="quarantine", device_id="device123", quarantine_duration=24)

# Create security policy
await tailscale_security(operation="policy", policy_name="restrict-api", rules=[{"action": "accept", "src": ["engineering"], "dst": ["api:*"]}])
```

#### Automation (`tailscale_automation`)

```python
# Create automation workflow
await tailscale_automation(operation="workflow_create", workflow_name="daily-backup", workflow_steps=[{"action": "backup", "target": "all"}])

# Execute workflow
await tailscale_automation(operation="workflow_execute", workflow_id="workflow123", execute_now=True)

# Schedule workflow
await tailscale_automation(operation="workflow_schedule", workflow_id="workflow123", schedule_cron="0 2 * * *")

# Execute custom script
await tailscale_automation(operation="script_execute", script_content="print('Hello Tailscale')", script_language="python")

# Batch operations
await tailscale_automation(operation="batch", batch_operations=[{"operation": "authorize", "device_id": "device123"}])
```

#### Backup & Recovery (`tailscale_backup`)

```python
# Create configuration backup
await tailscale_backup(operation="backup_create", backup_name="daily-backup", backup_type="full")

# Restore from backup
await tailscale_backup(operation="backup_restore", backup_id="backup123")

# Schedule automated backups
await tailscale_backup(operation="backup_schedule", schedule_cron="0 2 * * *", retention_days=30)

# Test backup integrity
await tailscale_backup(operation="backup_test", backup_id="backup123")

# Create disaster recovery plan
await tailscale_backup(operation="recovery_plan")
```

#### Performance Monitoring (`tailscale_performance`)

```python
# Measure network latency
await tailscale_performance(operation="latency", device_id="device123", measure_duration=60)

# Analyze bandwidth utilization
await tailscale_performance(operation="bandwidth", device_id="device123", measure_duration=300)

# Optimize routing performance
await tailscale_performance(operation="optimize", route_optimization=True)

# Establish performance baseline
await tailscale_performance(operation="baseline", baseline_name="production", baseline_duration=300)

# Predict capacity requirements
await tailscale_performance(operation="capacity", capacity_period="30d", scaling_factor=1.2)

# Get scaling recommendations
await tailscale_performance(operation="scaling", scaling_factor=1.5)
```

#### Advanced Reporting (`tailscale_reporting`)

```python
# Generate usage analytics report
await tailscale_reporting(operation="usage", date_range="30d", include_charts=True)

# Create custom report
await tailscale_reporting(operation="custom", custom_fields=["device_count", "bandwidth_usage"], date_range="7d")

# Schedule automated reports
await tailscale_reporting(operation="schedule", schedule_cron="0 9 * * 1", email_recipients=["admin@company.com"])

# Export reports
await tailscale_reporting(operation="export", export_path="/reports/", report_format="pdf")

# Deep network analytics
await tailscale_reporting(operation="analytics", analytics_depth="comprehensive", date_range="90d")

# Security metrics
await tailscale_reporting(operation="security", date_range="30d", security_focus=True)
```

#### Third-Party Integrations (`tailscale_integration`)

```python
# Create webhook endpoint
await tailscale_integration(operation="webhook_create", webhook_url="https://api.company.com/webhook", webhook_events=["device_connected", "device_disconnected"])

# Test webhook delivery
await tailscale_integration(operation="webhook_test", webhook_id="webhook123")

# Integrate with Slack
await tailscale_integration(operation="slack", slack_channel="#tailscale-alerts", api_key="slack-api-key")

# Integrate with Discord
await tailscale_integration(operation="discord", discord_webhook="https://discord.com/api/webhooks/...")

# Integrate with PagerDuty
await tailscale_integration(operation="pagerduty", pagerduty_key="pagerduty-integration-key")

# Integrate with Datadog
await tailscale_integration(operation="datadog", datadog_api_key="datadog-api-key", api_endpoint="https://api.datadoghq.com")
```

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install tailscalemcp
```

### From Source

   ```bash
   git clone https://github.com/yourusername/tailscalemcp.git
   cd tailscalemcp
pip install -e .
   ```

### Using Docker

   ```bash
docker pull tailscalemcp:latest
docker run -p 8000:8000 tailscalemcp:latest
```

## 🔧 Quick Start

### Basic Usage

```python
import asyncio
from tailscalemcp import TailscaleMCPServer

async def main():
    # Initialize the server
    server = TailscaleMCPServer(
        api_key="your_tailscale_api_key",
        tailnet="your_tailnet"
    )
    
    # Start the server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using as Context Manager

```python
import asyncio
from tailscalemcp import TailscaleMCPServer

async def main():
    async with TailscaleMCPServer() as server:
        # Server is automatically started
        devices = await server._list_devices_impl()
        print(f"Found {len(devices)} devices")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Monitoring Stack

### Complete Observability Solution

The TailscaleMCP server includes a comprehensive monitoring stack with Grafana, Prometheus, and Loki for complete observability of your Tailscale network.

#### Features

- **📈 Real-time Dashboards**: 4 comprehensive Grafana dashboards for different monitoring needs
- **📝 Structured Logging**: JSON-formatted logs with rich context for easy analysis
- **⚡ Prometheus Metrics**: Custom metrics for device activity, network traffic, and API performance
- **🔍 Log Aggregation**: Centralized log collection and analysis with Loki
- **🐳 Docker Compose**: Easy deployment and management of the entire monitoring stack

#### Quick Start with Monitoring

```bash
# Clone and setup
git clone https://github.com/sandraschi/tailscale-mcp.git
cd tailscale-mcp
cp env.example .env

# Edit .env with your Tailscale credentials
# TAILSCALE_API_KEY=your_api_key_here
# TAILSCALE_TAILNET=your_tailnet_name_here

# Start the complete monitoring stack
.\scripts\start-monitoring.ps1

# Access services:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Loki: http://localhost:3100
# - MCP Server: http://localhost:8080
```

#### Available Dashboards

1. **Network Overview**: Device status, network traffic, API performance metrics
2. **Logs Dashboard**: Error analysis, log streams, security event monitoring
3. **Device Activity**: Activity heatmaps, geolocation mapping, device timelines
4. **Comprehensive Monitoring**: Combined overview of all metrics and logs

#### Monitoring Documentation

For detailed information about the monitoring stack, see:
- [Monitoring Documentation](docs/monitoring/README.md)
- [Architecture Guide](docs/monitoring/Architecture.md)
- [Grafana Configuration](docs/monitoring/Grafana.md)
- [Prometheus Setup](docs/monitoring/Prometheus.md)
- [Loki Configuration](docs/monitoring/Loki.md)
- [Deployment Guide](docs/monitoring/Deployment.md)

#### General MCP Monitoring Standards

For comprehensive monitoring standards and reusable templates for all heavyweight MCP servers:
- [MCP Monitoring Standards](docs/monitoring/MCP_MONITORING_STANDARDS.md)
- [Monitoring Templates](docs/monitoring/MONITORING_TEMPLATES.md)

#### Specialized Monitoring Cases

For specialized monitoring documentation for specific use cases:
- [Tapo Cameras MCP Monitoring](docs/monitoring/TAPO_CAMERAS_MCP_MONITORING.md) - Home surveillance and security monitoring
- [Tapo Cameras Dashboard Templates](docs/monitoring/TAPO_CAMERAS_DASHBOARD_TEMPLATES.md) - Specialized Grafana dashboards for home security

#### Mobile Monitoring Integration

For mobile monitoring solutions:
- [RebootX Integration](docs/monitoring/REBOOTX_INTEGRATION.md) - Mobile infrastructure monitoring with RebootX app for iPad
- [RebootX Integration Guide](docs/integrations/REBOOTX_INTEGRATION.md) - Tailscale MCP specific RebootX integration
- [RebootX On-Prem Setup Guide](docs/monitoring/REBOOTX_ON_PREM_SETUP_GUIDE.md) - Complete setup with fixed IP configuration

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TAILSCALE_API_KEY` | Your Tailscale API key | Yes |
| `TAILSCALE_TAILNET` | Your Tailnet name | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No (default: INFO) |
| `PROMETHEUS_PORT` | Prometheus metrics port | No (default: 9091) |
| `LOG_FILE` | Log file path | No (default: logs/tailscale-mcp.log) |

### Example Configuration

```bash
export TAILSCALE_API_KEY="tskey-api-xxxxxxxxxxxxxxxxx"
export TAILSCALE_TAILNET="your-org.tailnet.ts.net"
export LOG_LEVEL="INFO"
```

## 📊 Grafana Dashboard Integration

TailscaleMCP includes comprehensive Grafana dashboard support inspired by the `zydepoint/tailscale-dashboard` project. You can create beautiful, interactive dashboards for monitoring your Tailscale network.

### Dashboard Types

- **Comprehensive Dashboard**: Complete network overview with device status, health scores, bandwidth usage, and historical trends
- **Network Topology Dashboard**: Visual network topology with device relationships and connection maps
- **Security Dashboard**: Security-focused monitoring with ACL overview, access patterns, and security alerts

### Creating Dashboards

```python
from tailscalemcp import TailscaleMCPServer

server = TailscaleMCPServer()

# Create comprehensive dashboard
dashboard = await server.create_grafana_dashboard("comprehensive")

# Export dashboard to file
await server.export_grafana_dashboard("comprehensive", "my_dashboard.json")

# Get dashboard summary
summary = await server.get_dashboard_summary("comprehensive")
```

### Monitoring Features

- **Real-time Metrics**: Device counts, health scores, bandwidth usage
- **Network Topology**: Visual representation of device connections
- **Health Reports**: Automated analysis with alerts and recommendations
- **Prometheus Integration**: Export metrics for monitoring systems

### Example Dashboard Demo

Run the included demo script to see all dashboard features:

```bash
python examples/grafana_dashboard_demo.py
```

This will create:
- Comprehensive monitoring dashboard
- Network topology visualization
- Security monitoring dashboard
- Prometheus metrics export
- Deployment instructions

## 🏗️ Modular Architecture

The TailscaleMCP server is built with a clean, modular architecture that separates concerns and makes the codebase maintainable and extensible.

### Project Structure

```
src/tailscalemcp/
├── __init__.py
├── __main__.py
├── mcp_server.py          # Main server entry point
├── exceptions.py          # Custom exceptions
├── monitoring.py          # Monitoring and metrics collection
├── grafana_dashboard.py   # Grafana dashboard generation
├── taildrop.py           # Taildrop file sharing functionality
├── device_management.py  # Advanced device management
├── magic_dns.py          # MagicDNS and networking features
└── tools/                # Modular tool implementations
    ├── __init__.py
    ├── device_tools.py    # Device management tools
    ├── monitoring_tools.py # Monitoring and metrics tools
    ├── taildrop_tools.py  # Taildrop file sharing tools
    └── dns_tools.py       # DNS and MagicDNS tools
```

### Tool Categories

#### 🔧 Device Management Tools (`device_tools.py`)
- List and search devices
- Device authorization and management
- SSH access configuration
- Device tagging and grouping
- Exit node and subnet router management

#### 📊 Monitoring Tools (`monitoring_tools.py`)
- Network status and health monitoring
- Prometheus metrics export
- Network topology visualization
- Grafana dashboard creation and export
- Health reports and analytics

#### 📁 Taildrop Tools (`taildrop_tools.py`)
- Secure file sharing between devices
- Transfer management and monitoring
- File expiration and cleanup
- Transfer statistics and analytics

#### 🌐 DNS Tools (`dns_tools.py`)
- MagicDNS configuration
- Custom DNS record management
- DNS resolution and caching
- Network policy management
- ACL (Access Control List) management

### Benefits of Modular Architecture

- **Maintainability**: Each tool category is isolated and focused
- **Extensibility**: Easy to add new tools without affecting existing functionality
- **Testability**: Individual modules can be tested in isolation
- **Code Reusability**: Tool modules can be reused across different contexts
- **Error Isolation**: Issues in one module don't affect others

## 🛠️ Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Docker (optional)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/tailscalemcp.git
cd tailscalemcp

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install-dev

# Setup pre-commit hooks
make pre-commit

# Or use the setup command
make setup
```

### Development Commands

   ```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Run all checks
make all

# Build package
make build

# Run the server
make run
```

### Docker Development

   ```bash
# Build development image
make docker-dev

# Run development container
make docker-run-dev

# Or use docker-compose
make dev-up
```

## 🧪 Testing

The project uses pytest with comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tailscalemcp --cov-report=html

# Run specific test file
pytest tests/test_mcp_server.py

# Run with verbose output
pytest -v
```

## 📊 Code Quality

This project maintains high code quality standards:

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Comprehensive testing framework
- **Pre-commit**: Automated code quality checks
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability scanning

## 🚀 CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline with:

- **Linting**: Ruff, MyPy, and security checks
- **Testing**: Multi-Python version testing with coverage
- **Security**: Bandit and Safety scanning
- **Building**: Package and Docker image building
- **Deployment**: Automatic PyPI publishing on releases

## 🐳 Docker Support

### Production Image

```bash
docker build -t tailscalemcp:latest .
docker run -p 8000:8000 tailscalemcp:latest
```

### Development Image

```bash
docker build -f Dockerfile.dev -t tailscalemcp:dev .
docker run -p 8000:8000 -v $(pwd):/app tailscalemcp:dev
```

### Docker Compose

```bash
# Production
docker-compose up -d

# Development
docker-compose --profile dev up -d
```

## 📚 API Reference

### Core Classes

#### `TailscaleMCPServer`

Main server class for managing Tailscale networks.

```python
server = TailscaleMCPServer(
    api_key: Optional[str] = None,
    tailnet: Optional[str] = None
)
```

#### Available Tools

- `list_devices(online_only: bool = False, filter_tags: List[str] = None)`
- `get_device(device_id: str)`
- `get_network_status()`
- `get_dns_config()`
- `list_acls(detailed: bool = False)`
- `enable_exit_node(device_id: str, advertise_routes: List[str] = None)`
- `disable_exit_node(device_id: str)`
- `enable_subnet_router(device_id: str, subnets: List[str])`
- `disable_subnet_router(device_id: str)`

### Exception Handling

```python
from tailscalemcp.exceptions import (
    TailscaleMCPError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError
)

try:
    device = await server._get_device_impl("invalid_id")
except NotFoundError as e:
    print(f"Device not found: {e.message}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. Setup development environment: `make setup`
2. Make your changes
3. Run tests: `make test`
4. Run linting: `make lint`
5. Format code: `make format`
6. Commit with conventional commits
7. Push and create PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/tailscalemcp/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/tailscalemcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/tailscalemcp/discussions)

## 🙏 Acknowledgments

- [FastMCP](https://github.com/pydantic/fastmcp) for the excellent MCP framework
- [Tailscale](https://tailscale.com/) for the amazing networking platform
- [Ruff](https://github.com/astral-sh/ruff) for fast Python tooling
- All contributors and users of this project

---

**Made with ❤️ by the TailscaleMCP team**