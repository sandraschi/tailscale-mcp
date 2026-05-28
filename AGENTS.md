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

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
