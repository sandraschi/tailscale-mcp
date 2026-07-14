# Agent Workflow Recollection for tailscale-mcp

## Project Identity
- **Repo**: tailscale-mcp — FastMCP 3.2+ Tailscale network controller
- **Python**: >=3.12, uses `uv` for package management
- **Framework**: FastMCP 3.2 with portmanteau tool pattern
- **Webapp**: React/Vite frontend (port 10820) + FastAPI backend (port 10821)

## Key Architecture
```
src/tailscalemcp/
  tools/           # MCP tool surface (portmanteau pattern)
  operations/      # Business logic layer
  client/          # Tailscale API client with rate limiting + retry
  models/          # Pydantic models
  server.py        # FastAPI backend for web_sota
  mcp_server.py    # FastMCP server setup
```

## Common Tasks
- **Run all checks**: `uv run ruff check . && uv run mypy src/tailscalemcp && uv run pytest`
- **Start webapp**: `.\start.ps1` (launches backend + frontend)
- **Start MCP only**: `uv run python -m tailscalemcp`
- **Run tests**: `uv run pytest -v`
- **Add dependency**: Add to `pyproject.toml` then `uv lock && uv sync`

## Ports Used
- Webapp frontend: 10820
- Backend/MCP HTTP: 10821
- Prometheus metrics: 9091
- Monitoring stack: Prometheus 9090, Loki 3100, Grafana 3000 (all 127.0.0.1 only)

## Fleet Standard Alignment
- FastMCP 3.2+ required
- Transport via `src/tailscalemcp/transport.py` (stdio/http/sse)
- All ports in 10700+ range
- structlog for structured logging (JSON, stderr)
- Prometheus metrics on separate port

## LM Link Integration (Tailscale + LM Studio)
LM Link is a Tailscale-powered encrypted mesh for remote LLM access (Feb 2026).
The `get_lm_link` tool provides operational control over LM Link via the `lms` CLI:

| Operation | CLI equivalent | Description |
|-----------|---------------|-------------|
| `status` | `lms link status --json` | Live peers, loaded models, link state |
| `enable` | `lms link enable` | Enable LM Link on this device |
| `disable` | `lms link disable` | Disable LM Link |
| `set_device_name` | `lms link set-device-name <name>` | Rename this device |
| `set_preferred_device` | `lms link set-preferred-device <device>` | Set preferred peer |
| `info` | (static) | Setup docs and links |
| `readiness` | (Tailscale API) | Tailnet connectivity check |

**Webapp**: `/lm-link` page shows live peer dashboard with model lists, enable/disable,
device rename, and preferred device selection. Requires `lms` CLI (bundled with LM Studio
or installable via `curl -fsSL https://lmstudio.ai/install.sh | bash`).

**Cross-repo**: local-llm-mcp (port 10833) probes the same `lms link status --json`
endpoint for its LM Studio provider health and dashboard. tailscale-mcp controls
the network; local-llm-mcp controls the models.

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
