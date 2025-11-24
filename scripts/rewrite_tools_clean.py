"""Rewrite all tool files from scratch with proper indentation."""

from pathlib import Path
import re

# Read the backup file
backup_file = Path("src/tailscalemcp/tools/portmanteau_tools.py.backup")
content = backup_file.read_text(encoding="utf-8")
lines = content.split("\n")

# Tool ranges from earlier analysis
TOOL_RANGES = [
    ("tailscale_device", 93, 859),
    ("tailscale_network", 861, 1444),
    ("tailscale_monitor", 1446, 1781),
    ("tailscale_file", 1783, 2143),
    ("tailscale_funnel", 2145, 2294),
    ("tailscale_security", 2296, 2767),
    ("tailscale_automation", 2769, 3174),
    ("tailscale_backup", 3176, 3573),
    ("tailscale_performance", 3575, 3951),
    ("tailscale_reporting", 3953, 4106),
    ("tailscale_integration", 4108, 4265),
    ("tailscale_help", 4267, 4314),
    ("tailscale_status", 4316, 4372),
]

def extract_tool_function(lines, start_line, end_line):
    """Extract tool function and fix indentation."""
    tool_lines = lines[start_line - 1 : end_line]
    
    # Find the async def line
    async_def_idx = None
    for i, line in enumerate(tool_lines):
        if "async def tailscale_" in line:
            async_def_idx = i
            break
    
    if async_def_idx is None:
        return None
    
    # Extract function signature (from async def to closing paren)
    func_sig_lines = []
    paren_count = 0
    for i in range(async_def_idx, len(tool_lines)):
        line = tool_lines[i]
        func_sig_lines.append(line)
        paren_count += line.count("(") - line.count(")")
        if "-> dict[str, Any]:" in line and paren_count == 0:
            break
    
    # Find docstring end
    docstring_end = len(func_sig_lines)
    for i in range(len(func_sig_lines), len(tool_lines)):
        if tool_lines[i].strip() == '"""':
            docstring_end = i + 1
            break
    
    # Extract function body
    body_lines = tool_lines[docstring_end:]
    
    # Fix indentation: function body should be at 8 spaces (2 levels from async def at 4)
    fixed_body = []
    for line in body_lines:
        if not line.strip():
            fixed_body.append("")
            continue
        
        # Count current indentation
        indent = len(line) - len(line.lstrip())
        
        # Function body starts at 12 spaces in original (3 levels from async def)
        # Should be 8 spaces (2 levels)
        if indent >= 12:
            # Reduce by 4 spaces
            new_indent = indent - 4
            fixed_body.append(" " * new_indent + line.lstrip())
        else:
            fixed_body.append(line)
    
    # Combine
    result = func_sig_lines + fixed_body
    
    # Replace self. with ctx.
    result_text = "\n".join(result)
    result_text = result_text.replace("self.mcp", "ctx.mcp")
    result_text = result_text.replace("self.device_manager", "ctx.device_manager")
    result_text = result_text.replace("self.monitor", "ctx.monitor")
    result_text = result_text.replace("self.grafana_dashboard", "ctx.grafana_dashboard")
    result_text = result_text.replace("self.taildrop_manager", "ctx.taildrop_manager")
    result_text = result_text.replace("self.magic_dns_manager", "ctx.magic_dns_manager")
    result_text = result_text.replace("self.funnel_manager", "ctx.funnel_manager")
    result_text = result_text.replace("self.network_ops", "ctx.network_ops")
    result_text = result_text.replace("self.policy_ops", "ctx.policy_ops")
    result_text = result_text.replace("self.audit_ops", "ctx.audit_ops")
    result_text = result_text.replace("self.tag_ops", "ctx.tag_ops")
    result_text = result_text.replace("self.key_ops", "ctx.key_ops")
    result_text = result_text.replace("self.policy_analyzer", "ctx.policy_analyzer")
    result_text = result_text.replace("self.analytics_ops", "ctx.analytics_ops")
    result_text = result_text.replace("self.reporting_ops", "ctx.reporting_ops")
    result_text = result_text.replace("self.service_ops", "ctx.service_ops")
    
    # Remove @self.mcp.tool() decorator
    result_text = re.sub(r"^\s*@self\.mcp\.tool\(\)\s*$", "", result_text, flags=re.MULTILINE)
    
    return result_text.split("\n")

# Generate all tool files
for tool_name, start_line, end_line in TOOL_RANGES:
    if tool_name == "tailscale_funnel":
        # Skip - already correct
        continue
    
    module_name = tool_name.replace("tailscale_", "") + "_tool"
    tool_func = extract_tool_function(lines, start_line, end_line)
    
    if tool_func is None:
        print(f"Failed to extract {tool_name}")
        continue
    
    # Create module - properly indent the function
    # The tool_func lines need to be indented 4 spaces (under the decorator)
    # But the async def line should be at the same level as the decorator (4 spaces)
    indented_func = []
    for i, line in enumerate(tool_func):
        if not line.strip():
            indented_func.append("")
        elif line.strip().startswith("async def"):
            # async def should be at 4 spaces (same as decorator)
            indented_func.append("    " + line.lstrip())
        else:
            # Other lines indented 4 spaces
            indented_func.append("    " + line)
    
    module_content = f'''"""Tailscale {tool_name.replace("tailscale_", "").replace("_", " ").title()} tool module."""

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
{chr(10).join(indented_func)}
'''
    
    output_file = Path(f"src/tailscalemcp/tools/{module_name}.py")
    output_file.write_text(module_content, encoding="utf-8")
    print(f"Generated {module_name}.py")

print("Done rewriting all tool files")

