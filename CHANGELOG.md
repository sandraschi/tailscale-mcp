# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **FastMCP Runtime Prompts and Resources**: Successfully implemented and verified working
  - 6 runtime prompts registered via `@mcp.prompt()` decorators
  - 7 runtime resources registered via `@mcp.resource()` decorators
  - All prompts and resources visible in MCP server UI (Cursor, Windsurf, etc.)
  - Note: Log shows "10 0 0" but this is a red herring - check MCP server UI for accurate counts
- **Comprehensive Docstring Standards**: Enhanced all portmanteau tool docstrings
  - Added PORTMANTEAU PATTERN RATIONALE to all 10 portmanteau tools
  - Reformatted Args sections to be concise but descriptive (2-3 lines for complex parameters)
  - Removed duplication between Args and Parameters sections
  - Flexible formatting: one line for simple params, 2-3 lines for enums/complex structures
  - All docstrings now properly formatted for Claude to understand portmanteau tool usage
- **Status Tool Enhancement**: Extended `tailscale_status` to show MCP server capabilities
  - Shows tool, prompt, and resource counts at basic level
  - Shows names/URIs at intermediate level
  - Shows full details at advanced/diagnostic levels
  - Helps verify prompt and resource registration
- **RebootX On-Prem Integration**: Complete mobile infrastructure monitoring setup
  - RebootX On-Prem server configuration for Tailscale MCP monitoring
  - Mobile app integration with fixed IP address (213.47.34.131)
  - 4 runnables: Tailscale MCP Server, Grafana, Prometheus, Loki
  - 4 dashboards: Network Overview, Monitoring Infrastructure, Security, Performance
  - Docker Compose integration with main monitoring stack
  - Comprehensive setup documentation and quick reference guides
- **Comprehensive Monitoring Stack**: Complete observability solution with Grafana, Prometheus, and Loki
  - Real-time Grafana dashboards for network visualization and device monitoring
  - Structured JSON logging with rich context for Loki integration
  - Prometheus metrics for performance monitoring and alerting
  - Docker Compose setup for easy deployment and management
- **Grafana Dashboards**: 4 comprehensive dashboards for different monitoring needs
  - Network Overview: Device status, traffic, API performance metrics
  - Logs Dashboard: Error analysis, log streams, security event monitoring
  - Device Activity: Activity heatmaps, geolocation mapping, device timelines
  - Comprehensive Monitoring: Combined overview of all metrics and logs
- **Structured Logging**: JSON-formatted logs with device context, operations, and error tracking
- **Prometheus Integration**: Custom metrics for device activity, network traffic, and API performance
- **Loki Integration**: Centralized log collection and analysis with LogQL queries
- **Monitoring Documentation**: Comprehensive documentation for all monitoring components
- **Monitoring Tests**: Comprehensive test suite for monitoring functionality
- **Docker Compose**: Complete monitoring stack orchestration
- **Promtail Configuration**: Log shipping and parsing for Loki integration
- **MCP Monitoring Standards**: Comprehensive monitoring standards and patterns for all heavyweight MCP servers
- **Monitoring Templates**: Reusable templates and configurations for implementing monitoring across projects
- **Repository Analysis**: Analysis of existing monitoring implementations across heavyweight MCP servers
- **Specialized Monitoring Cases**: Specialized monitoring documentation for specific use cases
- **Tapo Cameras MCP Monitoring**: Comprehensive home surveillance and security monitoring documentation
- **Tapo Cameras Dashboard Templates**: Specialized Grafana dashboard templates for home security monitoring
- **Mobile Monitoring Integration**: Mobile infrastructure monitoring with RebootX app for iPad

### Changed
- **Upgraded to FastMCP 2.12**: Latest version with improved performance and features
- **Enhanced Logging**: Structured logging with JSON format for better analysis
- **Improved Documentation**: Added comprehensive monitoring documentation
- **Updated Dependencies**: Latest versions of all monitoring components

### Fixed
- **Logging Integration**: Proper integration between structured logging and Loki
- **Metrics Collection**: Improved Prometheus metrics collection and export
- **Dashboard Configuration**: Fixed dashboard provisioning and data source configuration
- **Docker Configuration**: Improved Docker Compose setup and configuration

## [2.0.0] - 2024-01-01

### Added
- **Portmanteau Tools**: Consolidated tools following the database-mcp pattern to avoid tool explosion
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
- **Help and Status Tools**: Comprehensive help system and status monitoring
- **MCPB Packaging**: Model Context Protocol Bundle packaging for deployment
- **Enhanced CI/CD**: Comprehensive GitHub Actions pipeline with security scanning
- **Comprehensive Documentation**: Detailed documentation for all tools and features

### Changed
- **Architecture**: Refactored to use portmanteau tools for better organization
- **Tool Organization**: Tools organized by category in the tools folder tree
- **Documentation**: Comprehensive documentation with examples and best practices

### Fixed
- **Tool Registration**: Fixed tool registration and FastMCP integration
- **Error Handling**: Improved error handling and exception management
- **Code Quality**: Enhanced code quality with Ruff linting and comprehensive testing

## [1.0.0] - 2023-08-02

### Added
- Initial release of Tailscale MCP
- FastMCP 2.10 compliant server implementation
- Support for basic Tailscale device management
- Comprehensive documentation and examples
