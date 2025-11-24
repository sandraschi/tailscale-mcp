"""Generate tool modules from portmanteau_tools.py."""

import re
from pathlib import Path

# Tool ranges from extract_tool_modules.py
TOOL_RANGES = [
    ("tailscale_device", 93, 859),
    ("tailscale_network", 861, 1444),
    ("tailscale_monitor", 1446, 1781),
    ("tailscale_file", 1783, 2143),
    ("tailscale_funnel", 2145, 2294),  # Already extracted
    ("tailscale_security", 2296, 2767),
    ("tailscale_automation", 2769, 3174),
    ("tailscale_backup", 3176, 3573),
    ("tailscale_performance", 3575, 3951),
    ("tailscale_reporting", 3953, 4106),
    ("tailscale_integration", 4108, 4265),
    ("tailscale_help", 4267, 4314),
    ("tailscale_status", 4316, 4372),
]

source_file = Path("src/tailscalemcp/tools/portmanteau_tools.py")
content = source_file.read_text(encoding="utf-8")
lines = content.split("\n")

# Skip funnel since it's already done
tools_to_extract = [t for t in TOOL_RANGES if t[0] != "tailscale_funnel"]

for tool_name, start_line, end_line in tools_to_extract:
    # Extract tool function (0-indexed)
    tool_lines = lines[start_line - 1 : end_line]
    tool_content = "\n".join(tool_lines)
    
    # Replace self. with ctx.
    tool_content = tool_content.replace("self.mcp", "ctx.mcp")
    tool_content = tool_content.replace("self.device_manager", "ctx.device_manager")
    tool_content = tool_content.replace("self.monitor", "ctx.monitor")
    tool_content = tool_content.replace("self.grafana_dashboard", "ctx.grafana_dashboard")
    tool_content = tool_content.replace("self.taildrop_manager", "ctx.taildrop_manager")
    tool_content = tool_content.replace("self.magic_dns_manager", "ctx.magic_dns_manager")
    tool_content = tool_content.replace("self.funnel_manager", "ctx.funnel_manager")
    tool_content = tool_content.replace("self.network_ops", "ctx.network_ops")
    tool_content = tool_content.replace("self.policy_ops", "ctx.policy_ops")
    tool_content = tool_content.replace("self.audit_ops", "ctx.audit_ops")
    tool_content = tool_content.replace("self.tag_ops", "ctx.tag_ops")
    tool_content = tool_content.replace("self.key_ops", "ctx.key_ops")
    tool_content = tool_content.replace("self.policy_analyzer", "ctx.policy_analyzer")
    tool_content = tool_content.replace("self.analytics_ops", "ctx.analytics_ops")
    tool_content = tool_content.replace("self.reporting_ops", "ctx.reporting_ops")
    tool_content = tool_content.replace("self.service_ops", "ctx.service_ops")
    
    # Remove the @self.mcp.tool() decorator (will be added in register function)
    tool_content = re.sub(r"^\s*@self\.mcp\.tool\(\)\s*$", "", tool_content, flags=re.MULTILINE)
    
    # Create module name
    module_name = tool_name.replace("tailscale_", "") + "_tool"
    
    # Generate module content
    module_template = f'''"""Tailscale {tool_name.replace("tailscale_", "").replace("_", " ").title()} tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_{tool_name.replace("tailscale_", "")}_tool(ctx: ToolContext) -> None:
    """Register the {tool_name} tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """
    @ctx.mcp.tool()
{tool_content}
'''
    
    # Write module file
    output_file = Path(f"src/tailscalemcp/tools/{module_name}.py")
    output_file.write_text(module_template, encoding="utf-8")
    print(f"Generated {output_file}")

print(f"\nExtracted {len(tools_to_extract)} tool modules")


