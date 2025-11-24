# Portmanteau Tools Refactoring Plan

## Current State
- Single file: `portmanteau_tools.py` (4615 lines)
- 13 tools all in one file
- Hard to maintain and navigate

## Target State
- Modular structure with each tool in its own file
- Main file coordinates registration
- Better maintainability and testability

## Structure

```
tools/
├── __init__.py
├── _base.py (ToolContext class)
├── portmanteau_tools.py (main coordinator - ~200 lines)
├── device_tool.py
├── network_tool.py
├── monitor_tool.py
├── file_tool.py
├── funnel_tool.py ✅ (done)
├── security_tool.py
├── automation_tool.py
├── backup_tool.py
├── performance_tool.py
├── reporting_tool.py
├── integration_tool.py
├── help_tool.py
└── status_tool.py
```

## Tool Line Ranges (from grep)
1. tailscale_device: line 92
2. tailscale_network: line 860
3. tailscale_monitor: line 1445
4. tailscale_file: line 1782
5. tailscale_funnel: line 2144 ✅ (extracted)
6. tailscale_security: line 2295
7. tailscale_automation: line 2768
8. tailscale_backup: line 3175
9. tailscale_performance: line 3574
10. tailscale_reporting: line 3952
11. tailscale_integration: line 4107
12. tailscale_help: line 4266
13. tailscale_status: line 4315

## Extraction Pattern

Each tool module follows this pattern:

```python
"""Tool module docstring."""

from typing import Any
import structlog
from tailscalemcp.exceptions import TailscaleMCPError
from ._base import ToolContext

logger = structlog.get_logger(__name__)

def register_<tool_name>_tool(ctx: ToolContext) -> None:
    """Register the tool."""
    @ctx.mcp.tool()
    async def tailscale_<tool_name>(...):
        # Tool implementation
        pass
```

## Helper Methods

Help and status tools have helper methods that will be moved to:
- `_helpers.py` - Shared helper functions

## Progress
- [x] Create _base.py with ToolContext
- [x] Extract funnel_tool.py
- [ ] Extract remaining 12 tools
- [ ] Move helper methods to _helpers.py
- [ ] Update main portmanteau_tools.py
- [ ] Test all tools work
- [ ] Remove backup file


