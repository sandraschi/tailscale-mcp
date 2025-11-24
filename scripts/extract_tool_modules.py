"""Extract tools from portmanteau_tools.py into separate modules."""

import re
from pathlib import Path

# Read the original file
source_file = Path("src/tailscalemcp/tools/portmanteau_tools.py")
content = source_file.read_text(encoding="utf-8")
lines = content.split("\n")

# Find all tool definitions
tool_starts = []
for i, line in enumerate(lines):
    if "@self.mcp.tool()" in line:
        # Find the async def line
        for j in range(i, min(i + 10, len(lines))):
            if "async def tailscale_" in lines[j]:
                tool_match = re.search(r"async def (tailscale_\w+)", lines[j])
                if tool_match:
                    tool_starts.append((tool_match.group(1), i, j))
                    break

# Find end of each tool
tool_ranges = []
for idx, (tool_name, decorator_line, def_line) in enumerate(tool_starts):
    if idx + 1 < len(tool_starts):
        end_line = tool_starts[idx + 1][1] - 1
    else:
        # Last tool - find end of _register_tools
        for j in range(def_line, len(lines)):
            if 'logger.info("All portmanteau tools registered' in lines[j]:
                end_line = j - 1
                break
        else:
            end_line = len(lines) - 1
    
    tool_ranges.append((tool_name, def_line, end_line))

# Print tool ranges for manual extraction
print("Tool extraction ranges:")
for tool_name, start, end in tool_ranges:
    print(f"{tool_name}: lines {start+1}-{end+1} ({end-start+1} lines)")


