# Tailscale MCP

**Operate your tailnet from the AI tools you already use.** Tailscale MCP is a [FastMCP 3.1+](https://github.com/pydantic/fastmcp) server that exposes the [**Tailscale Admin API**](https://tailscale.com/api) to assistants and automation: devices, DNS, services, monitoring, Funnel, Taildrop-related flows, and more — through a **small set of portmanteau tools** (many operations each, so your client does not drown in hundreds of tiny tool names). Optional **SEP-1577** agentic workflows (`run_agentic_tailnet_workflow`) let a capable host run multi-step flows when **sampling** is configured. An optional **Webapp** (Vite/React) gives humans a glass-style dashboard: **My tailnet** topology, **Partner tailnets** insights, help, and connection status.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.1+](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/pydantic/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Repository: **[github.com/sandraschi/tailscale-mcp](https://github.com/sandraschi/tailscale-mcp)**

---

## Why this exists

If you manage a **Tailscale tailnet**, you already use the admin console and the official API. This project turns that surface into **MCP tools** so **Cursor, Claude Desktop, Antigravity**, or any MCP-capable client can list devices, inspect DNS, drive automation, and answer questions about your network **with structured responses** (success flags, errors, hints) instead of ad-hoc shell scripts.

You stay on the **Admin API** contract: the authoritative reference remains [**Tailscale’s API docs**](https://tailscale.com/api). The MCP server adds opinionated grouping, persistence for certain flows, optional **LLM sampling** for multi-step tasks, and an optional **browser UI** for quick visual checks.

---

## What you get

### MCP tools (portmanteau pattern)

Instead of dozens of one-off tools, operations are grouped into verb-led domains such as **`manage_tailnet_devices`**, **`manage_tailnet_network`**, **`monitor_tailnet`**, **`manage_taildrop`**, **`manage_funnel`**, and more (security, automation, reporting, integrations, etc.). Each tool takes an **`operation`** argument — similar in spirit to other fleet servers that avoid “tool explosion.” MCP names are verb-first; the redundant `tailscale_` prefix is not used because this server is Tailscale-only.

Coverage includes **device and user management**, **MagicDNS and network policies**, **Tailscale Services (TailVIPs)** where exposed, **monitoring and metrics**, **Funnel** and **Taildrop**-related flows (with CLI integration where applicable), plus **help**, **status**, and **partner tailnet** summaries for orgs that share tailnets with partners.

The full matrix of tools and operations lives in **[docs/TAILSCALE_MCP_PORTMANTEAU_TOOLS.md](docs/TAILSCALE_MCP_PORTMANTEAU_TOOLS.md)** (see the doc index for any additional reference material).

### Agentic workflows (optional)

For multi-step automation, **`run_agentic_tailnet_workflow`** uses **FastMCP sampling** (SEP-1577). You can point the server at a **local OpenAI-compatible** endpoint (for example Ollama) via `TAILSCALE_SAMPLING_*`, or let the **host** run the LLM with `TAILSCALE_SAMPLING_USE_CLIENT_LLM=1`. Details and safety notes are in **[docs/PRD.md](docs/PRD.md)**.

### Webapp (optional)

The **Webapp** under `web_sota/` is a React/Vite front end with a dark, glass-style layout. Highlights:

- **My tailnet** — visualize your network (Mermaid topology from `get_tailnet_status`, plus a decorative **Orbit** view).
- **Partner tailnets** — summary of **members vs shared users** and devices grouped by login, aligned with the **`summarize_partner_tailnets`** tool.
- **Help** — environment and sampling variables, linked from the shell.

Ports for this repo follow the fleet **adjacency** convention (**10820** frontend / **10821** backend by default); see **[docs/WEBAPP.md](docs/WEBAPP.md)** and `web_sota/start.ps1`.

### Persistence and observability

**DiskStore** (FastMCP 3.1) holds durable state for funnels, transfers, and preferences across restarts — see **[docs/STORAGE_BACKENDS.md](docs/STORAGE_BACKENDS.md)**. Optional **Prometheus / Grafana / Loki**-style stacks are documented under **[docs/monitoring/](docs/monitoring/README.md)** if you want full observability on your own infrastructure.

### Skills for agents

When present, **`skills/TAILSCALE_EXPERT.md`** is exposed as **`resource://tailscale/skills`** so clients can load operator-focused guidance alongside tools.

---

## Who it is for

- **Platform engineers** wiring tailnet changes into IDEs and automation.
- **Operators** who want a quick dashboard plus MCP for deeper queries.
- **Agents** (with appropriate allowlists) that should plan multi-step API work instead of one-shot guesses.

---

## Requirements

You need a **Tailscale API key** with access to your tailnet and the **tailnet name** the key is scoped to:

| Variable | Role |
|----------|------|
| `TAILSCALE_API_KEY` | Bearer token from the [admin console](https://login.tailscale.com/admin/settings/keys) |
| `TAILSCALE_TAILNET` | Your tailnet identifier (as shown in the console / API) |

Optional variables for sampling, HTTP transport, and logging are documented in **[docs/PRD.md](docs/PRD.md)** and **`.env.example`**.

If you are new to Tailscale itself, read **[docs/WHAT_IS_TAILSCALE.md](docs/WHAT_IS_TAILSCALE.md)** first — it explains **tailnet vs Admin API vs client** in plain language.

---

## Install (quick)

Full options (Claude Desktop JSON, Docker, Webapp) are in **[docs/INSTALL.md](docs/INSTALL.md)**. Minimal path with **[uv](https://docs.astral.sh/uv/)**:

```bash
git clone https://github.com/sandraschi/tailscale-mcp.git
cd tailscale-mcp
uv sync
uv run tailscale-mcp
```

Set `TAILSCALE_API_KEY` and `TAILSCALE_TAILNET` in your environment or `.env` before starting.

---

## Documentation map

| Topic | Document |
|--------|----------|
| Install, env, clients, Webapp | [docs/INSTALL.md](docs/INSTALL.md) |
| Tailscale concepts | [docs/WHAT_IS_TAILSCALE.md](docs/WHAT_IS_TAILSCALE.md) |
| Product scope and sampling | [docs/PRD.md](docs/PRD.md) |
| Webapp routes and ports | [docs/WEBAPP.md](docs/WEBAPP.md) |
| Architecture | [docs/ARCHITECTURE_AND_DESIGN.md](docs/ARCHITECTURE_AND_DESIGN.md) |
| Portmanteau tools (deep dive) | [docs/TAILSCALE_MCP_PORTMANTEAU_TOOLS.md](docs/TAILSCALE_MCP_PORTMANTEAU_TOOLS.md) |
| Everything else | [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) |
| Contributing (uv, Ruff, tests) | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## License

MIT — see [LICENSE](LICENSE).
