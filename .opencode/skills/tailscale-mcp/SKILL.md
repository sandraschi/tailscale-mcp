# Tailscale MCP

FastMCP 3.2+ Tailscale network controller with 24 portmanteau tools.

## Before starting work
1. Check tailnet status: `get_tailnet_status(operation="full")`
2. Check LM Link for remote LLM peers: `get_lm_link(operation="status")`

## Key tools
- `manage_tailnet_devices` — device CRUD, approvals, posture
- `manage_tailnet_network` — DNS, MagicDNS, routing, services
- `monitor_tailnet` — Prometheus metrics, health
- `manage_taildrop` — file send/receive
- `manage_funnel` — public exposure via Funnel
- `run_tailnet_security` — ACLs, posture, device keys
- `run_agentic_tailnet_workflow` — SEP-1577 agentic workflows
- `get_lm_link` — LM Link (Tailscale + LM Studio remote LLMs)

## At end of work
- Verify tailnet state if changed
- Confirm LM Link state with `get_lm_link(operation="status")`
