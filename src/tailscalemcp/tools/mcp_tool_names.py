"""Public MCP tool names exposed to clients (verb-first; server is Tailscale-only).

Use with ``@mcp.tool(name=...)`` so Python function names can stay stable internally.

Breaking change (2.1.0): legacy ``tailscale_*`` MCP names are removed; update clients and prompts.
"""

from __future__ import annotations

# --- Portmanteau domains ---
MANAGE_TAILNET_DEVICES = "manage_tailnet_devices"
MANAGE_TAILNET_NETWORK = "manage_tailnet_network"
MONITOR_TAILNET = "monitor_tailnet"
MANAGE_TAILDROP = "manage_taildrop"
MANAGE_FUNNEL = "manage_funnel"
RUN_TAILNET_SECURITY = "run_tailnet_security"
RUN_TAILNET_AUTOMATION = "run_tailnet_automation"
MANAGE_TAILNET_BACKUPS = "manage_tailnet_backups"
ANALYZE_TAILNET_PERFORMANCE = "analyze_tailnet_performance"
GENERATE_TAILNET_REPORTS = "generate_tailnet_reports"
MANAGE_TAILNET_INTEGRATIONS = "manage_tailnet_integrations"

# --- Standalone utilities ---
GET_HELP = "get_help"
GET_TAILNET_STATUS = "get_tailnet_status"
SUMMARIZE_PARTNER_TAILNETS = "summarize_partner_tailnets"
GET_LM_LINK = "get_lm_link"

# --- Agentic (SEP-1577) ---
RUN_AGENTIC_TAILNET_WORKFLOW = "run_agentic_tailnet_workflow"
# Deprecated: same behavior as RUN_AGENTIC_TAILNET_WORKFLOW (was tailscale_sampling).
RUN_AGENTIC_TAILNET_WORKFLOW_SAMPLING = "run_agentic_tailnet_workflow_sampling"

ALL_PUBLIC_TOOL_NAMES: tuple[str, ...] = (
    MANAGE_TAILNET_DEVICES,
    MANAGE_TAILNET_NETWORK,
    MONITOR_TAILNET,
    MANAGE_TAILDROP,
    MANAGE_FUNNEL,
    RUN_TAILNET_SECURITY,
    RUN_TAILNET_AUTOMATION,
    MANAGE_TAILNET_BACKUPS,
    ANALYZE_TAILNET_PERFORMANCE,
    GENERATE_TAILNET_REPORTS,
    MANAGE_TAILNET_INTEGRATIONS,
    GET_HELP,
    GET_TAILNET_STATUS,
    SUMMARIZE_PARTNER_TAILNETS,
    GET_LM_LINK,
    RUN_AGENTIC_TAILNET_WORKFLOW,
    RUN_AGENTIC_TAILNET_WORKFLOW_SAMPLING,
)
