# Product requirements — Tailscale MCP

**Status:** Living document · **Last updated:** 2026-04-02 (v2.1.0 alignment)

## Summary

Tailscale MCP is a **FastMCP 3.1+** server that exposes the **Tailscale Admin API** and related CLI flows (Funnel, Taildrop) to AI agents and operators through **portmanteau tools**, **runtime prompts/resources**, and optional **SEP-1577** agentic workflows (`run_agentic_tailnet_workflow`). An optional **SOTA web dashboard** (`Webapp`) provides a glass-style UI for browsing devices, settings, help, and **tailnet visualization**.

**Context:** [WHAT_IS_TAILSCALE.md](WHAT_IS_TAILSCALE.md) · **Install:** [INSTALL.md](INSTALL.md)

## Goals

| Goal | Success criteria |
|------|------------------|
| Agent-safe operations | Tools return structured dicts; docstrings describe operations and recovery paths. |
| Real API coverage | Device, DNS, services, monitoring, file share, funnel — aligned with [Tailscale API](https://tailscale.com/api) and documented gaps. |
| Deployable bundle | `manifest.json` + `[tool.mcpb]` support **`mcpb pack`** for `.mcpb` distribution. |
| Observable | Structured logging; optional Prometheus/Grafana/Loki stack documented. |
| Human UI | Optional Vite/React app on registered ports with credentials help and **My tailnet** visualization. |

## Personas

- **Platform engineer** — automates tailnet changes via MCP from Cursor/Claude Desktop.
- **Operator** — uses the web UI for quick checks and topology view.
- **Agent** — chains tools or uses sampling workflows with explicit tool allowlists.

## Functional requirements

### MCP server

- **Credentials:** `TAILSCALE_API_KEY`, `TAILSCALE_TAILNET` required for live API calls.
- **Tools:** Portmanteau pattern (`operation` parameter); includes `manage_tailnet_devices`, `configure_tailnet_network`, `monitor_tailnet_activity`, `manage_tailnet_files`, `configure_tailnet_funnel`, `manage_tailnet_security`, `automate_tailnet_tasks`, `backup_tailnet_config`, `optimize_tailnet_performance`, `generate_tailnet_reports`, `integrate_tailnet_services`, `get_tailnet_help`, `get_tailnet_status`, `manage_tailnet_keys`, and `run_agentic_tailnet_workflow`.
- **Sampling:** Server-side OpenAI-compatible HTTP (`TAILSCALE_SAMPLING_*`) or client LLM (`TAILSCALE_SAMPLING_USE_CLIENT_LLM=1`) for `run_agentic_tailnet_workflow`.
- **Status:** `get_tailnet_status` exposes MCP capability counts; optional **`include_mermaid_diagram`** returns Mermaid text for tailnet topology (consumed by the web app and agents).

### Web dashboard (`Webapp`)

- **Routes:** Documented in [WEBAPP.md](WEBAPP.md).
- **My tailnet (`/my-tailnet`):** Tab A — render Mermaid from `get_tailnet_status` + `include_mermaid_diagram: true`, with fallback graph from device list. Tab B — **Orbit (CSS 3D)** decorative device ring (not a geographic map).
- **Help:** `/help` documents env vars and sampling; linked from shell UI.

### Partner tailnets

- **MCP:** `summarize_partner_tailnets` aggregates Admin API **users** (`member` vs **shared** tailnet users) and **devices grouped by login** (node `user` field).
- **Web:** `/partner-tailnets` surfaces the same summary, Mermaid overview, and raw JSON for debugging.

### Non-goals (current)

- **Unity/WebGL** “Visualizer” bridge — placeholder only; advanced 3D deferred.
- **Trust credentials** as first-class auth — future enhancement; document API key path today.

## Development standards

- **Lint / format:** [Ruff](https://github.com/astral-sh/ruff) only — `uv run ruff check .`, `uv run ruff format .` (import sorting via `[tool.ruff.lint.isort]`). **Black** and standalone **isort** are not used; **pre-commit** runs `ruff` and `ruff-format` hooks.
- **Types:** `mypy` (see `CONTRIBUTING.md` and `.pre-commit-config.yaml`).
- **Canonical contributor guide:** [CONTRIBUTING.md](../CONTRIBUTING.md).

## Release alignment

- Runtime version: `src/tailscalemcp/version.py` (`__version__`).
- Package metadata: `pyproject.toml`, `manifest.json`, `extension.toml`, `[tool.mcpb]` — keep in sync for each release (see [CHANGELOG](../CHANGELOG.md)).
