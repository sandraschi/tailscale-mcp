# Tailscale MCP

**FastMCP 3.1+** · [**Tailscale Admin API**](https://tailscale.com/api) · portmanteau MCP tools · optional **SEP-1577** [`tailscale_agentic_workflow`](docs/PRD.md) · optional **Webapp** (My tailnet, Partner tailnets)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.1+](https://img.shields.io/badge/FastMCP-3.1+-green.svg)](https://github.com/pydantic/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[github.com/sandraschi/tailscale-mcp](https://github.com/sandraschi/tailscale-mcp)

| | |
|---|---|
| **Run** | [INSTALL.md](docs/INSTALL.md) |
| **New to Tailscale?** | [WHAT_IS_TAILSCALE.md](docs/WHAT_IS_TAILSCALE.md) |
| **Tools** | [TAILSCALE_MCP_PORTMANTEAU_TOOLS.md](docs/TAILSCALE_MCP_PORTMANTEAU_TOOLS.md) |
| **Webapp** | [WEBAPP.md](docs/WEBAPP.md) |
| **Product** | [PRD.md](docs/PRD.md) |
| **Architecture** | [ARCHITECTURE_AND_DESIGN.md](docs/ARCHITECTURE_AND_DESIGN.md) |
| **All docs** | [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) |
| **Contribute** | [CONTRIBUTING.md](CONTRIBUTING.md) |

**Env:** `TAILSCALE_API_KEY`, `TAILSCALE_TAILNET`. **Sampling:** `TAILSCALE_SAMPLING_*` / `TAILSCALE_SAMPLING_USE_CLIENT_LLM` — [PRD](docs/PRD.md). **Agents:** `resource://tailscale/skills` if `skills/TAILSCALE_EXPERT.md` exists.

**Stack:** [DiskStore](docs/STORAGE_BACKENDS.md) · optional [monitoring/](docs/monitoring/README.md)

MIT — [LICENSE](LICENSE)
