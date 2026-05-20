# tailscale-mcp — Deep Assessment

**Assessment Date**: 2026-05-01
**Version**: 2.1.0
**Python**: >=3.12

---

## Architecture Overview

Well-structured FastMCP server using **portmanteau tool pattern** (one MCP tool per domain with `operation` enum). Clean 3-layer separation: `tools/` (MCP surface), `operations/` (business logic), `client/` (API transport). Includes a SOTA web_sota frontend (React/Vite) connecting to a FastAPI backend that mounts the MCP app.

---

## Pros

1. **Modular architecture**: Clear separation `tools/` → `operations/` → `client/` with Pydantic models
2. **Portmanteau pattern**: 17 MCP tools with typed `Literal` operations — clean, discoverable, fleet-standard
3. **Proper API client**: Rate limiting, retry with exponential backoff + jitter, connection pooling
4. **SEP-1577 sampling**: Agentic workflow support with `context.sample_step` and server-side Ollama fallback
5. **Prompts + Resources**: 6 prompts, 8 resources registered including Mermaid topology diagram
6. **Typed tool inputs**: `Annotated[..., Field(ge=1, le=65535)]` for bounded numerics; full `Literal` enums
7. **Structured logging**: structlog with JSON output, ISO timestamps, proper log levels
8. **Monitoring stack**: Docker compose with Prometheus + Loki + Promtail + Grafana
9. **CI/CD**: GitHub Actions with lint, mypy, security scan, package build, release
10. **Webapp**: Modern React/Vite frontend with 15+ pages, tool explorer, chat, visualizer
11. **Error taxonomy**: 10 exception classes with HTTP codes (`AuthenticationError`, `NotFoundError`, `RateLimitExceededError`, etc.)

---

## Cons / Gaps / Bugs

### Critical

| # | Issue | File(s) | Detail |
|---|-------|---------|--------|
| C1 | **FastMCP 3.1 pins, needs 3.2** | `pyproject.toml:29` | `fastmcp>=3.1.0` — must be `>=3.2.0` for SEP-1577 final, prefab, and current fleet standard |
| C2 | **Dual API client (same name, different class)** | `src/tailscalemcp/api_client.py` vs `src/tailscalemcp/client/api_client.py` | Both named `TailscaleAPIClient`. One has rate limiting + retry, the other doesn't. `device_management.py` imports the simple one; `operations/` imports the enhanced one. Creates confusion and inconsistent behavior. |
| C3 | **Forbidden ports used** | `__main__.py:38` (8000), `Dockerfile:27` (8080) | Fleet standard forbids 3000, 5000, 5173, 8000, 8080. Must use fleet range 10700+ |
| C4 | **Dockerfile Python version mismatch** | `Dockerfile:1` (3.11-slim) vs `pyproject.toml:14` (>=3.12) | Container uses Python 3.11 while project requires 3.12+ |
| C5 | **Two logging configs may clash** | `__main__.py:107-148` + `mcp_server.py:54-70` | Both configure structlog globally. If started via uvicorn, `__main__` isn't used so one config runs; but if started via `python -m tailscalemcp`, only `__main__`'s config matters since `mcp_server.py` runs first on import. Still, dual init is fragile. |

### High

| # | Issue | File(s) | Detail |
|---|-------|---------|--------|
| H1 | **Root start.ps1 vs web_sota/start.ps1 — two entry points** | `start.ps1` (line 18: `uv run -m tailscale_mcp`) vs `web_sota/start.ps1` (line 33: `uvicorn tailscalemcp.server:app`) | One starts the MCP stdio server, the other starts the FastAPI HTTP backend. Confusing and one hides the process. |
| H2 | **Stale CORS origin** | `server.py:39` | Allows `http://localhost:5173` (Vite default port) but web_sota uses port 10820 |
| H3 | **Silent error swallowing in CLI wrapper** | `utils/tailscale_cli.py:195-210, 230-241` | `file_send()` and `file_receive()` catch `TailscaleMCPError` and return `{"success": False}` — caller never knows an error occurred |
| H4 | **Test coverage critically low** | `tests/test_mcp_server.py` (191 lines, ~17 tests) | Coverage threshold in pyproject.toml: 24% (pytest) / 80% (coverage). Current coverage likely well below 80% |
| H5 | **`server.py` creates new `Client` per request** | `server.py:74, 105` | `async with Client(tailscale_server.mcp)` per HTTP call — creates a new client each time instead of reusing. Could leak resources under load. |
| H6 | **docker-compose v1 format** | `docker-compose.yml:1` | `version: '3.8'` is Compose v1 spec — deprecated. Modern Docker uses Compose v2 (no version key) |
| H7 | **rebootx-on-prem in compose — unused dependency** | `docker-compose.yml:100-128` | RebootX service and Swagger UI — seems like a stale/unused monitoring addition |
| H8 | **`server.py` imports `server` from `mcp_server` but both have same name** | `server.py:19`: `from tailscalemcp.mcp_server import server as tailscale_server` | Works but confusing — module named `server.py` imports an object named `server` from another module |

### Medium

| # | Issue | File(s) | Detail |
|---|-------|---------|--------|
| M1 | `logger.error(f"...")` f-string style | `__main__.py:175, 208`, `transport.py:261` | Should use structlog's `logger.error("msg", error=str(e))` key-value style for structured logging |
| M2 | Missing `AGENTS.md` | root | Fleet standard requires `AGENTS.md` for agent workflow recollection |
| M3 | Old `mypy` pre-commit hook | `.pre-commit-config.yaml:26` | `v1.8.0` (Jan 2024) — current is `v1.15.0+` |
| M4 | Multiple tool files still import from `tailscalemcp` not `src/tailscalemcp` | various tool files | `from tailscalemcp.exceptions import ...` — works via PYTHONPATH but fragile |
| M5 | `docker-compose.yml` exposes Prometheus (9090), Grafana (3000), Loki (3100) wide open | docker-compose.yml:8-9, 61, 30 | No auth, no reverse proxy. Should use bound address `127.0.0.1:9090` |
| M6 | No health endpoint on Prometheus port | Dockerfile:36 | HEALTHCHECK hits `localhost:9091/metrics` but MCP itself doesn't expose `/health` on its HTTP transport |
| M7 | `setup.ps1` is super old scaffolding | `setup.ps1` | Creates obsolete skeleton (FastAPI 2.10 era, with OAuth2 and YAML config). Should be removed or updated |
| M8 | `Cargo.toml` + Rust build for Zed extension | `Cargo.toml`, `build.ps1` | May be incomplete/stale — Zed extension model may have changed |
| M9 | `grafana_dashboard.py` and `grafana_dashboard_demo.py` likely unused | `grafana_dashboard.py` | Grafana dashboard creation logic that may not be wired to actual Grafana instance |
| M10 | Webapp has no `.env` for `VITE_API_URL` | `web_sota/.env` missing | `api.ts` hardcodes fallback `http://127.0.0.1:10821` — works but not configurable without `.env` |

---

## Webapp ↔ Backend Connection

**How it works:**
- `web_sota/start.ps1` starts uvicorn on `127.0.0.1:10821` serving `tailscalemcp.server:app`
- `server.py` mounts FastMCP's HTTP app at `/mcp`
- FastAPI adds REST endpoints: `/health`, `/api/v1/tools`, `/api/v1/tools/call`, `/api/v1/sampling-status`, `/api/v1/llm-health`, `/api/v1/chat`
- Webapp Vite dev server on `127.0.0.1:10820` proxied via explicit fetch URLs

**Status**: Functional but fragile — every HTTP request creates a new `fastmcp.Client()`. No connection pooling at the FastMCP client level.

---

## New API Features Implemented (2026-05-01)

All gaps from the Tailscale Admin API audit have been implemented:

| Feature | Tool Name | Endpoints |
|---------|-----------|-----------|
| Device invites | `manage_tailnet_invites` | list, create, get, delete, resend, accept |
| User invites | `manage_tailnet_invites` | list, create, get, delete, resend |
| Posture attributes | `manage_posture_attributes` | get, set, delete, batch_update |
| Device keys | `manage_device_keys` | expire, update_key_expiry, set_ip |
| Logging | `manage_tailnet_logging` | config audit logs, network flow logs, log streaming |
| Webhooks | `manage_tailnet_webhooks` | list, create, get, update, delete, rotate_secret |
| Tailnet settings | `manage_tailnet_settings` | get, update |
| Contacts | `manage_tailnet_contacts` | get, update |

These 7 new portmanteau tools expose ~30 new operations against the Admin API.
