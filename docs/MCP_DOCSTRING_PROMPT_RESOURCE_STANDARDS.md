# MCP Server Docstring, Prompt, and Resource Standards

## Overview

This document defines the standards for FastMCP 2.12+ MCP servers, covering comprehensive docstrings, prompt registration, and resource implementation. These standards ensure AI assistants (Claude, etc.) can properly understand and use portmanteau tools without confusion.

## Docstring Standards

### Portmanteau Pattern Rationale

**Every portmanteau tool MUST include a PORTMANTEAU PATTERN RATIONALE section** explaining why multiple operations are consolidated into a single tool:

```python
PORTMANTEAU PATTERN RATIONALE:
Instead of creating N separate tools (one per operation), this tool consolidates related
operations into a single interface. This design:
- Prevents tool explosion (N tools → 1 tool) while maintaining full functionality
- Improves discoverability by grouping related operations together
- Reduces cognitive load when working with related tasks
- Enables atomic batch operations across multiple actions
- Follows FastMCP 2.12+ best practices for feature-rich MCP servers
```

### Args Section Formatting

**Flexible but concise formatting** - balance between brevity and clarity:

1. **Simple Parameters**: One line per parameter
   ```python
   device_id (str | None): Device identifier. Required for: get, authorize operations. Example: "device123"
   ```

2. **Complex Parameters** (enums, nested structures): 2-3 lines allowed
   ```python
   scan_type (str): Type of security scan. Used by: scan operation. Default: "comprehensive".
       Valid: "comprehensive" (full scan of all devices/configs), "quick" (fast scan, basic checks),
       "deep" (thorough scan with detailed analysis)
   ```

3. **Nested Structures**: 2-3 lines with key information
   ```python
   service_payload (dict[str, Any] | None): Service configuration dictionary. Required for: services_create, services_update.
       Required keys: "name" (str), "endpoints" (list[dict] with deviceId, port, protocol).
       Optional keys: "tailvipIPv4", "tailvipIPv6", "magicDNS" (str), "tags" (list[str]).
   ```

### Key Principles

- **No duplication**: Args section is the single source of truth - don't repeat in "SUPPORTED OPERATIONS"
- **Descriptive enough**: Complex parameters (enums, nested dicts) need explanation
- **Concise overall**: Avoid 1000+ line docstrings eating context
- **Type hints in Args**: Always include type hints: `(str | None)`, `(list[str])`, etc.
- **Operation context**: Always specify which operations use each parameter: "Required for: X, Y operations"

## Prompt Registration

### FastMCP Runtime Prompts

**Prompts are registered via `@mcp.prompt()` decorators** for direct MCP protocol usage (Cursor, Windsurf, etc.):

```python
@self.mcp.prompt()
def list_devices_prompt(online_only: bool = False, filter_tags: list[str] | None = None) -> list[dict[str, Any]]:
    """List all devices in the Tailscale tailnet.
    
    Args:
        online_only: Filter to online devices only
        filter_tags: Filter devices by tags
    """
    tags_str = f" with tags {', '.join(filter_tags)}" if filter_tags else ""
    online_str = "online " if online_only else ""
    query = f"List all {online_str}devices{tags_str} in the tailnet"
    return [{"role": "user", "content": query}]
```

### Registration Pattern

**Define prompts directly in server initialization** and store references to prevent garbage collection:

```python
def _initialize_prompts_and_resources(self) -> None:
    """Initialize prompts and resources."""
    # Register prompts
    @self.mcp.prompt()
    def my_prompt() -> list[dict[str, Any]]:
        return [{"role": "user", "content": "..."}]
    
    # Store references to prevent garbage collection
    self._prompt_refs = [my_prompt, ...]
```

### MCPB Manifest Prompts

**Separate system** for Claude Desktop packages - defined in `manifest.json`:

```json
{
  "prompts": [
    {
      "name": "list_devices",
      "description": "List all devices",
      "arguments": [...],
      "text": "..."
    }
  ]
}
```

**Both systems work independently** - MCPB prompts for Claude Desktop, FastMCP prompts for direct MCP usage.

## Resource Registration

### FastMCP Runtime Resources

**Resources are registered via `@mcp.resource()` decorators** with URI strings:

```python
@self.mcp.resource("tailscale://devices")
async def devices_resource() -> str:
    """List all devices in the tailnet."""
    devices = await device_manager.list_devices()
    return json.dumps({"devices": devices, "count": len(devices)})
```

### URI Format

**Resources use URIs** with custom scheme and hierarchical paths:

- **Simple resources**: `tailscale://devices`
- **Template resources**: `tailscale://devices/{device_id}` (with path parameters)

### Resource Requirements

1. **Must be async**: `async def resource_function() -> str:`
2. **Return string**: Usually JSON, but can be any string format
3. **Read-only**: Resources should not modify state
4. **Path parameters**: Template URIs can extract parameters from path

### Registration Pattern

**Define resources directly in server initialization** and store references:

```python
def _initialize_prompts_and_resources(self) -> None:
    """Initialize prompts and resources."""
    # Register resources
    @self.mcp.resource("tailscale://devices")
    async def devices_resource() -> str:
        return json.dumps({"devices": [...]})
    
    # Store references to prevent garbage collection
    self._resource_refs = [devices_resource, ...]
```

## Verification and Troubleshooting

### The "10 0 0" Log Red Herring

**Important**: FastMCP startup log may show "Found 10 tools, 0 prompts, and 0 resources" even when prompts/resources are correctly registered.

**Why**: The log message appears before registration completes (timing issue).

**Solution**: **Check the MCP server UI** (Cursor, Windsurf, etc.) - prompts and resources appear correctly there.

**Verification**:
1. Check MCP server UI - should show correct counts
2. Use `tailscale_status` tool with `component="mcp_server"` and `detail_level="advanced"`
3. Test actual prompt/resource access - they work even if log shows 0

### Status Tool Integration

**Extended status tool** to show MCP server capabilities:

```python
result = await tailscale_status(
    component="mcp_server",
    detail_level="advanced"
)
# Returns: {
#     "mcp_server": {
#         "tools": {"count": 12, "names": [...], "list": [...]},
#         "prompts": {"count": 6, "list": [...]},
#         "resources": {"count": 7, "list": [...], "templates_count": 1}
#     }
# }
```

## Implementation Checklist

### Docstrings
- [ ] PORTMANTEAU PATTERN RATIONALE section in every portmanteau tool
- [ ] Args section properly formatted (concise but descriptive)
- [ ] Complex parameters (enums, nested structures) have 2-3 line explanations
- [ ] No duplication between Args and SUPPORTED OPERATIONS sections
- [ ] Type hints included in Args: `(str | None)`, `(list[str])`, etc.
- [ ] Operation context specified: "Required for: X, Y operations"

### Prompts
- [ ] Prompts defined using `@mcp.prompt()` decorators
- [ ] Prompts registered in server initialization method
- [ ] References stored to prevent garbage collection: `self._prompt_refs = [...]`
- [ ] Prompt functions return `list[dict[str, Any]]` with message format
- [ ] Prompt docstrings explain purpose and parameters

### Resources
- [ ] Resources defined using `@mcp.resource()` decorators with URI strings
- [ ] Resources registered in server initialization method
- [ ] References stored to prevent garbage collection: `self._resource_refs = [...]`
- [ ] Resource functions are async and return `str` (usually JSON)
- [ ] URI scheme is consistent (e.g., `tailscale://`)
- [ ] Template resources use `{param_name}` syntax for path parameters

### Verification
- [ ] Status tool shows correct tool/prompt/resource counts
- [ ] MCP server UI displays prompts and resources correctly
- [ ] Actual prompt/resource access works (don't trust log alone)
- [ ] Documentation updated to explain the "10 0 0" log red herring

## Best Practices

1. **Don't trust the log**: The startup log may show incorrect counts - verify in MCP server UI
2. **Store references**: Always store prompt/resource function references to prevent garbage collection
3. **Consistent URIs**: Use consistent URI scheme for all resources
4. **Clear docstrings**: Balance brevity with clarity - complex params need explanation
5. **Test both systems**: Verify both MCPB manifest prompts (Claude Desktop) and FastMCP runtime prompts/resources (direct MCP)

## Related Documentation

- FastMCP 2.12+ Documentation
- MCP Protocol Specification
- Portmanteau Pattern Best Practices
- FastMCP Prompt/Resource Registration Guide

