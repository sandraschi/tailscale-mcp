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
├── mcp_tool_names.py (Authoritative v2.1.0 names) ✅
├── device_tool.py ✅
├── network_tool.py ✅
├── monitor_tool.py ✅
├── file_tool.py ✅
├── funnel_tool.py ✅
├── security_tool.py ✅
├── automation_tool.py ✅
├── backup_tool.py ✅
├── performance_tool.py ✅
├── reporting_tool.py ✅
├── integration_tool.py ✅
├── help_tool.py ✅
└── status_tool.py ✅
```

## Tool Names (v2.1.0 Verb-First)
1. manage_tailnet_devices ✅
2. configure_tailnet_network ✅
3. monitor_tailnet_activity ✅
4. manage_tailnet_files ✅
5. configure_tailnet_funnel ✅
6. manage_tailnet_security ✅
7. automate_tailnet_tasks ✅
8. backup_tailnet_config ✅
9. optimize_tailnet_performance ✅
10. generate_tailnet_reports ✅
11. integrate_tailnet_services ✅
12. get_tailnet_help ✅
13. get_tailnet_status ✅

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
- [x] Extract remaining 12 tools
- [x] Rename all tools to v2.1.0 Verb-First Portmanteau standards
- [x] Create mcp_tool_names.py as authoritative registry
- [x] Update main registration logic
- [x] Test all tools work with new names
- [x] Documentation fully aligned (v2.1.0)


