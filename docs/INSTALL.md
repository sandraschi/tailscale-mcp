# Install and run

**Needs:** Python **3.12+** · [uv](https://docs.astral.sh/uv/) · `TAILSCALE_API_KEY` + `TAILSCALE_TAILNET` ([keys](https://login.tailscale.com/admin/settings/keys))

More env: [`.env.example`](../.env.example) · [PRD](PRD.md) (`TAILSCALE_SAMPLING_*`, `MCP_*`)

## Commands

```bash
uvx tailscale-mcp
```

```bash
git clone https://github.com/sandraschi/tailscale-mcp.git
cd tailscale-mcp
uv sync
uv run pre-commit install
uv run tailscale-mcp
```

**Tests:** `uv run pytest`

**Claude Desktop:** `"command": "uv"`, `"args": ["--directory", "C:/path/to/tailscale-mcp", "run", "tailscale-mcp"]`

**PyPI:** `pip install tailscalemcp` if published — confirm name on PyPI.

**Docker / HTTP port:** see [WEBAPP.md](WEBAPP.md), `transport.py` (`MCP_PORT`, often **10821**).

**Webapp:** `.\web_sota\start.ps1` — **10820** / **10821** · [WEBAPP.md](WEBAPP.md)

**Observability:** [monitoring/README.md](monitoring/README.md)
