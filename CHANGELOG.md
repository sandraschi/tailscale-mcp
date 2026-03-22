# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Documentation:** Root [README.md](README.md) is a short entry with a **doc map**; detailed install is [docs/INSTALL.md](docs/INSTALL.md); [docs/WHAT_IS_TAILSCALE.md](docs/WHAT_IS_TAILSCALE.md) explains Tailscale vs Admin API. [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) updated. [CONTRIBUTING.md](CONTRIBUTING.md) aligned with **uv** (Poetry removed). [pyproject.toml](pyproject.toml) `project.urls` point to **sandraschi/tailscale-mcp**.
- **Documentation:** README stack tightened again — compact tables, shorter [INSTALL](docs/INSTALL.md) / [WHAT_IS_TAILSCALE](docs/WHAT_IS_TAILSCALE.md), leaner [DOCUMENTATION_INDEX](docs/DOCUMENTATION_INDEX.md) top + dev/MCP sections. MCP Central Docs `projects/tailscale-mcp/README.md` mirror reduced to one table + ports.

### Added
- **SEP-1577 sampling with tools**: `tailscale_agentic_workflow` runs multi-step flows via `context.sample_step` (FastMCP 3.1+). `tailscale_sampling` is a deprecated alias with the same parameters. Replaces the previous mock-only sampling paths.
- **Server-side sampling handler**: `TailscaleSamplingHandler` — OpenAI-compatible `chat/completions` (default Ollama at `TAILSCALE_SAMPLING_BASE_URL`). Optional `TAILSCALE_SAMPLING_USE_CLIENT_LLM=1` uses host sampling with the handler as fallback.
- **MCP resource `resource://tailscale/skills`**: Loads `skills/TAILSCALE_EXPERT.md` when present (agent guidance for tools and sampling).
- **Help page** on the Webapp (`/help`): Credentials, `.env`, and sampling environment variables; links from the sidebar and header.
- **`tailscale_help` topic `sampling`**: Structured help for agentic workflows and env vars (see also `tailscale_help(topic="sampling")`).
- **Tailscale Funnel Support**: Complete Funnel integration for exposing local services to public internet
  - New `tailscale_funnel` portmanteau tool with 5 operations (enable, disable, status, list, certificate_info)
  - Automatic TLS certificate management via Tailscale Funnel
  - Secure HTTPS access to local services without complex configuration
  - Full integration with Tailscale CLI for Funnel operations
  - Comprehensive error handling and status reporting
- **Enhanced Taildrop Integration**: Real CLI integration for Taildrop file sharing
  - TaildropManager now uses real Tailscale CLI commands for file transfers
  - Automatic fallback to simulated transfers if CLI not available
  - Improved file transfer progress tracking and status reporting
  - Support for receiving all pending files via CLI
  - Better error handling with actual Tailscale CLI error messages
- **Tailscale CLI Utility**: New utility module for CLI integration
  - Async wrapper for Tailscale CLI commands
  - Automatic binary detection across platforms (Windows, macOS, Linux)
  - Comprehensive error handling and timeout management
  - Support for Taildrop and Funnel CLI operations
  - Proper command execution with output parsing
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
- **Contributor docs**: [CONTRIBUTING.md](CONTRIBUTING.md) — code style is **Ruff** (`ruff check`, `ruff format`) and **mypy**; **Black** and **isort** removed from [`.pre-commit-config.yaml`](.pre-commit-config.yaml) (Ruff handles lint, import sorting, and format).
- **`.env.example`**: Documented sampling variables and clarified that copying to **`.env`** (gitignored) is the supported way to supply credentials for real API testing. (Renamed from `env.example` to match common convention.)
- **`tailscale_help` / `_helpers`**: Overview and new **`topic=sampling`** content for SEP-1577, env vars, and `resource://tailscale/skills`.
- **Dependencies**: PEP 735 `[dependency-groups] dev` + `[tool.uv] default-groups = ["dev"]` so `uv sync` installs pytest/ruff/mypy; Ruff/mypy targets **3.12**.
- **README**: Badges and copy aligned with the repo (FastMCP **3.1+**, Python **3.12+**); added **Tailscale API (upstream)** with links to the interactive API docs and trust credentials.
- **Device model + webapp**: Fixed `Device.from_api_response` parsing of `addresses` when the API returns a **list of IP strings** (real v2 shape); Devices page now shows API error **detail/hint**, optional **credential banner** via `GET /api/v1/status`, and maps `id` / `addresses`. Settings links to **tailscale.com/api** and Keys; CORS extended for Vite default port.
- **Upgraded to FastMCP 3.1+**: Current supported line (see `pyproject.toml`); older 2.x references removed from docs and source comments.
- **Enhanced Logging**: Structured logging with JSON format for better analysis
- **Improved Documentation**: Added comprehensive monitoring documentation
- **Updated Dependencies**: Latest versions of all monitoring components

### Fixed
- **Logging Integration**: Proper integration between structured logging and Loki
- **Metrics Collection**: Improved Prometheus metrics collection and export
- **Dashboard Configuration**: Fixed dashboard provisioning and data source configuration
- **Docker Configuration**: Improved Docker Compose setup and configuration

## [2.0.2] - 2026-03-22

### Added
- **`tailscale_partner_tailnets`** MCP tool: `summary` (members vs `type=shared` users, devices-by-login, hints), `users_list`, `user_get`, `devices_by_login`.
- **Admin API `GET /users`**: `TailscaleAPIClient.list_users` / `get_user`; **`Device`** parses node owner `user`; **`device_management.list_users`** / **`get_user_details`** implemented. **`tailscale_device`** `user_list` accepts optional `user_type` and `user_role_filter`.
- **Web** `/partner-tailnets`: counts, Mermaid overview, JSON panels.
- **Tests**: `tests/unit/test_partner_grouping.py`.

### Changed
- **Version** metadata to **2.0.2** (package, manifest, extension, User-Agent).

## [2.0.1] - 2026-03-22

### Added
- **My tailnet** (`/my-tailnet`, `Webapp`): Visual tailnet view with two modes — **Mermaid** diagram from `tailscale_status` with `include_mermaid_diagram: true` (or a flowchart fallback from `tailscale_device` list), and **Orbit (CSS 3D)** — decorative rotating device ring (not geographic). Route is lazy-loaded; **mermaid** is a dependency of the web app.
- **Documentation**: [docs/PRD.md](docs/PRD.md) (product requirements), [docs/WEBAPP.md](docs/WEBAPP.md) (SOTA dashboard routes and behavior).
- **MCPB manifest**: Version **2.0.1** with updated descriptions (SOTA UI, `tailscale_status` Mermaid); **[tool.mcpb]** in `pyproject.toml` aligned with repository author/URLs.

### Changed
- **Version**: Python package, MCP server, User-Agent, and bundled **`manifest.json`** / **`extension.toml`** set to **2.0.1**.
- **`tailscale_status` helpers**: Reported `system.version` reads from **`tailscalemcp.version`** (same value as `__version__`), avoiding a hardcoded string and import cycles.

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
- FastMCP 3.1+ compliant server implementation (historical releases used FastMCP 2.x)
- Support for basic Tailscale device management
- Comprehensive documentation and examples
