# Tailscale MCP — expert reference

## When to use what

- **Direct tools** (`manage_tailnet_devices`, `manage_tailnet_network`, `get_tailnet_status`, …): deterministic, scriptable calls to the Tailscale Admin API. Prefer these when you know the operation and parameters.
- **`run_agentic_tailnet_workflow`** (SEP-1577): multi-step tasks where the model should choose tools and interpret results. Requires sampling (server-side LLM or a capable MCP host).

## Sampling configuration

| Mode | Set |
|------|-----|
| Server-side (e.g. Ollama) | `TAILSCALE_SAMPLING_BASE_URL` (default `http://127.0.0.1:11434/v1`), `TAILSCALE_SAMPLING_MODEL` |
| Host/client LLM | `TAILSCALE_SAMPLING_USE_CLIENT_LLM=1` (FastMCP uses host sampling; server handler is fallback) |
| Cloud OpenAI-compatible | `TAILSCALE_SAMPLING_API_KEY` + your provider base URL |

No API key is required for typical localhost or private-LAN Ollama.

## Agentic workflow pattern

1. List tool names with `get_tailnet_status(component="mcp_server", detail_level="diagnostic")` if unsure.
2. Call `run_agentic_tailnet_workflow(workflow_prompt="...", available_tools=["manage_tailnet_devices", "get_tailnet_status"], max_iterations=5)`.
3. Keep `available_tools` minimal to reduce confusion and token use.

## API authority

The canonical HTTP surface is documented at [https://tailscale.com/api](https://tailscale.com/api). This MCP maps operations to those routes; behavior follows Tailscale’s API, not this document.

## Deprecated alias

`run_agentic_tailnet_workflow_sampling` is an alias for `run_agentic_tailnet_workflow` with the same parameters.
