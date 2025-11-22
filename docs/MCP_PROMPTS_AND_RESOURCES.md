# MCP Prompts and Resources Guide

## Overview

The Tailscale MCP server provides **prompts** and **resources** to enhance the user experience and enable programmatic access to Tailscale data.

## Important: Two Different Systems

**There are two separate prompt/resource systems:**

1. **MCPB Manifest Prompts** (in `manifest.json`) - These are recognized by Claude Desktop when the package is installed. ✅ **This is what Claude Desktop uses.**

2. **FastMCP Runtime Prompts/Resources** (via `@mcp.prompt()`/`@mcp.resource()` decorators) - These are registered at runtime and counted in FastMCP's log. ⚠️ **These are for direct MCP protocol usage, not MCPB packages.**

**Current Status:**
- ✅ **20 prompts** are defined in `manifest.json` (lines 116-237) and recognized by Claude Desktop
- ✅ **6 FastMCP runtime prompts** registered and working (visible in MCP server UI)
- ✅ **7 FastMCP runtime resources** registered and working (visible in MCP server UI)
- ⚠️ **Log shows "10 0 0"** - This is a red herring! The log message is from FastMCP startup before registration completes
  - **Actual status**: Prompts and resources ARE registered correctly
  - **Verification**: Check the detailed MCP server UI - prompts and resources appear there
  - The log count happens too early in the startup process

**Conclusion:** Both systems work! MCPB manifest prompts are for Claude Desktop packages, while FastMCP runtime prompts/resources work for direct MCP protocol usage (Cursor, Windsurf, etc.). The "10 0 0" log is misleading - check the MCP server UI for accurate counts.

## Summary

- ✅ **20 prompts** are defined in `manifest.json` and recognized by Claude Desktop
- ✅ **12 tools** are registered via FastMCP decorators and work correctly
- ✅ **6 FastMCP runtime prompts** registered and working (visible in MCP server UI)
- ✅ **7 FastMCP runtime resources** registered and working (visible in MCP server UI)
- ⚠️ **Log shows "10 0 0"** - This is a **red herring**!
  - The log message appears before registration completes
  - **Actual status**: Prompts and resources ARE registered correctly
  - **Verification**: Check the detailed MCP server UI - they appear there
  - This is a timing issue in FastMCP's startup logging

**Both systems work!** MCPB manifest prompts are for Claude Desktop packages, while FastMCP runtime prompts/resources work for direct MCP protocol usage (Cursor, Windsurf, etc.). Don't trust the log - check the MCP server UI for accurate counts.

## What are Prompts?

**Prompts** are pre-configured templates that help users interact with the MCP server. They generate structured messages that can be used to invoke tools with the correct parameters.

### Benefits

- **Easier Interaction**: Users don't need to remember exact tool names or parameter formats
- **Consistent Usage**: Prompts ensure tools are called with correct parameters
- **Better UX**: Claude Desktop and other MCP clients can suggest prompts to users
- **Template-Based**: Prompts can accept parameters to customize the generated message

### Available Prompts

1. **`list_devices_prompt`**
   - Lists all devices in the tailnet
   - Parameters: `online_only` (bool), `filter_tags` (list[str])
   - Example: "List all online devices with tags ['production', 'server']"

2. **`get_device_details_prompt`**
   - Gets detailed information about a specific device
   - Parameters: `device_id` (str)
   - Example: "Show me detailed information for device d123456"

3. **`authorize_device_prompt`**
   - Authorizes a device to join the tailnet
   - Parameters: `device_id` (str), `reason` (str, optional)
   - Example: "Authorize device d123456 (reason: New employee onboarding)"

4. **`check_network_status_prompt`**
   - Checks overall network status and health
   - No parameters
   - Example: "Show me the current network status and health"

5. **`create_security_report_prompt`**
   - Generates a comprehensive security report
   - No parameters
   - Example: "Generate a comprehensive security report for the tailnet"

6. **`backup_configuration_prompt`**
   - Creates a backup of Tailscale configuration
   - Parameters: `backup_name` (str, optional)
   - Example: "Create a backup of the Tailscale configuration named daily-backup"

### How Prompts Work

Prompts are registered with the FastMCP server using the `@mcp.prompt()` decorator. When invoked, they return a list of message dictionaries that can be used to call tools:

```python
@mcp.prompt()
def list_devices_prompt(online_only: bool = False) -> list[dict[str, Any]]:
    """List all devices in the Tailscale tailnet."""
    query = f"List all {'online ' if online_only else ''}devices in the tailnet"
    return [{"role": "user", "content": query}]
```

## What are Resources?

**Resources** are read-only data sources accessible via URIs. They provide programmatic access to Tailscale data without requiring tool calls.

### Benefits

- **Direct Access**: Access data via URIs without tool invocation
- **Caching**: Resources can be cached by MCP clients
- **Standardized**: Follow MCP resource protocol for consistency
- **Efficient**: Clients can fetch resources directly when needed

### Available Resources

All resources use the `tailscale://` URI scheme:

1. **`tailscale://devices`**
   - Lists all devices in the tailnet
   - Returns: JSON with device list and count
   - Example: `tailscale://devices`

2. **`tailscale://devices/{device_id}`**
   - Gets details for a specific device
   - Parameters: `device_id` (path parameter)
   - Returns: JSON with device details
   - Example: `tailscale://devices/d123456`

3. **`tailscale://network/status`**
   - Gets current network status
   - Returns: JSON with network status
   - Example: `tailscale://network/status`

4. **`tailscale://network/topology`**
   - Gets network topology map
   - Returns: JSON with topology data
   - Example: `tailscale://network/topology`

5. **`tailscale://security/report`**
   - Gets security report
   - Returns: JSON with security report
   - Example: `tailscale://security/report`

6. **`tailscale://monitoring/metrics`**
   - Gets Prometheus-formatted metrics
   - Returns: Prometheus exposition format
   - Example: `tailscale://monitoring/metrics`

7. **`tailscale://monitoring/health`**
   - Gets network health report
   - Returns: JSON with health report
   - Example: `tailscale://monitoring/health`

### How Resources Work

Resources are registered with the FastMCP server using the `@mcp.resource()` decorator. They can be accessed via URIs:

```python
@mcp.resource("tailscale://devices")
async def devices_resource() -> str:
    """List all devices in the tailnet."""
    devices = await device_manager.list_devices()
    return json.dumps({"devices": devices, "count": len(devices)})
```

Template resources (with parameters) use URI templates:

```python
@mcp.resource("tailscale://devices/{device_id}")
async def device_resource(device_id: str) -> str:
    """Get details for a specific device."""
    device = await device_manager.get_device(device_id)
    return json.dumps({"device": device, "device_id": device_id})
```

## Usage Examples

### Using Prompts

In Claude Desktop or other MCP clients, prompts appear as suggestions. Users can:

1. Select a prompt from the list
2. Fill in any required parameters
3. The prompt generates a message that invokes the appropriate tool

### Using Resources

Resources can be accessed directly via URIs:

```python
# In an MCP client
resource_uri = "tailscale://devices"
devices_data = await mcp_client.read_resource(resource_uri)
```

Or referenced in tool calls:

```python
# Tool can reference a resource
result = await tool_call(
    operation="analyze",
    data_source="tailscale://network/status"
)
```

## Implementation Details

### Registration

Prompts and resources are registered during server initialization:

```python
# In mcp_server.py
def _initialize_prompts_and_resources(self) -> None:
    """Initialize prompts and resources."""
    self.prompts = TailscalePrompts(self.mcp)
    self.resources = TailscaleResources(
        self.mcp, self.device_manager, self.monitor
    )
```

### File Structure

```
src/tailscalemcp/
├── prompts_and_resources.py  # Prompts and resources implementation
└── mcp_server.py             # Server initialization
```

## Best Practices

### Prompts

1. **Clear Names**: Use descriptive names that indicate the prompt's purpose
2. **Parameter Validation**: Validate parameters in prompt functions
3. **Helpful Messages**: Generate clear, actionable messages
4. **Documentation**: Document all parameters and return values

### Resources

1. **Consistent URIs**: Use a consistent URI scheme (`tailscale://`)
2. **RESTful Design**: Follow RESTful principles for resource paths
3. **JSON Format**: Return data in JSON format for consistency
4. **Error Handling**: Handle errors gracefully and return appropriate status codes
5. **Caching**: Consider cache headers for resources that don't change frequently

## Future Enhancements

Potential additions:

- **More Prompts**: Add prompts for all common operations
- **Resource Templates**: Add more template resources with parameters
- **Resource Versioning**: Support versioned resources (e.g., `tailscale://v1/devices`)
- **Resource Filtering**: Add query parameters for filtering resources
- **Resource Pagination**: Support pagination for large resource lists

## See Also

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Tailscale API Documentation](https://tailscale.com/kb/1243/api)

