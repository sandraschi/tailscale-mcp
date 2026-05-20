"""Shared tool input types for JSON Schema-complete MCP tool definitions.

FastMCP 3.1+ derives MCP tool parameter schemas from Python type annotations.
Use ``typing.Literal`` for closed enums and ``typing.Annotated[..., Field(...)]`` for
numeric bounds so clients and reviewers (e.g. ToolBench) see full constraints—not
only prose in docstrings.

Response shapes: portmanteau tools return a ``dict`` that always includes an
``"operation"`` string (sub-operation performed). Many responses add
``"result"``, ``"count"``, or domain-specific keys; failures raise ``TailscaleMCPError``
with a message suitable for ``recovery_options`` in higher-level callers.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

# --- Funnel ---
FunnelOperation = Literal[
    "funnel_enable",
    "funnel_disable",
    "funnel_status",
    "funnel_list",
    "funnel_certificate_info",
]

# --- Device / users / keys ---
DeviceOperation = Literal[
    "list",
    "get",
    "authorize",
    "rename",
    "tag",
    "ssh",
    "search",
    "stats",
    "exit_node",
    "subnet_router",
    "user_list",
    "user_create",
    "user_update",
    "user_delete",
    "user_details",
    "auth_key_list",
    "auth_key_create",
    "auth_key_revoke",
    "auth_key_rotate",
]

# --- Network / DNS / services ---
NetworkOperation = Literal[
    "dns_config",
    "magic_dns",
    "dns_record",
    "resolve",
    "search_domain",
    "policy",
    "stats",
    "cache",
    "services_list",
    "services_get",
    "services_create",
    "services_update",
    "services_delete",
]

MonitorOperation = Literal[
    "status",
    "metrics",
    "prometheus",
    "topology",
    "health",
    "dashboard",
    "export",
]

MonitorDashboardExportType = Literal["comprehensive", "topology", "security"]

FileOperation = Literal[
    "send",
    "receive",
    "list",
    "cancel",
    "status",
    "stats",
    "cleanup",
]

SecurityOperation = Literal[
    "scan",
    "compliance",
    "audit",
    "report",
    "monitor",
    "block",
    "quarantine",
    "alert",
    "policy",
    "threat",
]

AutomationOperation = Literal[
    "workflow_create",
    "workflow_execute",
    "workflow_schedule",
    "workflow_list",
    "workflow_delete",
    "script_execute",
    "script_template",
    "batch",
    "dry_run",
]

BackupOperation = Literal[
    "backup_create",
    "backup_restore",
    "backup_schedule",
    "backup_list",
    "backup_delete",
    "backup_test",
    "restore_test",
    "recovery_plan",
]

PerformanceOperation = Literal[
    "latency",
    "bandwidth",
    "optimize",
    "baseline",
    "capacity",
    "utilization",
    "scaling",
    "threshold",
]

ReportingOperation = Literal[
    "generate",
    "usage",
    "custom",
    "schedule",
    "export",
    "analytics",
    "behavior",
    "security",
    "template",
]

IntegrationOperation = Literal[
    "webhook_create",
    "webhook_test",
    "webhook_list",
    "webhook_delete",
    "slack",
    "discord",
    "pagerduty",
    "datadog",
    "test",
]

# --- Device invites ---
DeviceInviteOperation = Literal[
    "list",
    "create",
    "get",
    "delete",
    "resend",
    "accept",
]

# --- User invites ---
UserInviteOperation = Literal[
    "list",
    "create",
    "get",
    "delete",
    "resend",
]

# --- Device posture attributes ---
PostureAttributeOperation = Literal[
    "get",
    "set",
    "delete",
    "batch_update",
]

# --- Device key management ---
DeviceKeyOperation = Literal[
    "expire",
    "update_key_expiry",
    "set_ip",
]

# --- Logging ---
LoggingOperation = Literal[
    "configuration_audit_logs",
    "network_flow_logs",
    "stream_status",
    "stream_config_get",
    "stream_config_set",
]

# --- Webhooks (native Tailscale API, not generic integrations) ---
WebhookOperation = Literal[
    "list",
    "create",
    "get",
    "update",
    "delete",
    "rotate_secret",
]

# --- Tailnet settings ---
TailnetSettingsOperation = Literal[
    "get",
    "update",
]

# --- Contacts ---
ContactOperation = Literal[
    "get",
    "update",
]

PartnerTailnetsOperation = Literal[
    "summary",
    "users_list",
    "user_get",
    "devices_by_login",
]

LmLinkOperation = Literal["info", "readiness"]

HelpTopic = Literal[
    "overview",
    "examples",
    "best_practices",
    "troubleshooting",
    "funnel",
    "sampling",
]

HelpLevel = Literal["basic", "intermediate", "advanced", "expert"]

StatusComponent = Literal[
    "overview",
    "devices",
    "network",
    "services",
    "metrics",
    "alerts",
    "health",
    "mcp_server",
]

StatusDetailLevel = Literal["basic", "intermediate", "advanced", "diagnostic"]

StatusTimeRange = Literal["1h", "6h", "24h", "7d"]

TaildropStatusFilter = Literal["pending", "completed", "failed", "expired"]

# Bounded numerics (exposed as JSON Schema min/max)
PortNumber = Annotated[
    int,
    Field(ge=1, le=65535, description="TCP/UDP port (1-65535)."),
]
ExpireHours = Annotated[
    int,
    Field(ge=1, le=168, description="Taildrop link expiry in hours (1-168)."),
]
DnsTtl = Annotated[
    int,
    Field(ge=60, le=2147483647, description="DNS record TTL in seconds (min 60)."),
]
PolicyPriority = Annotated[
    int,
    Field(
        ge=0,
        le=100000,
        description="Policy priority (lower runs first in many stacks).",
    ),
]
MaxAgenticIterations = Annotated[
    int,
    Field(ge=1, le=50, description="Max LLM/tool rounds for agentic workflow."),
]
