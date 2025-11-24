# FastMCP Resources Explained

## What are Resources?

**Resources** in FastMCP are read-only data sources accessible via **URIs** (Uniform Resource Identifiers). They provide programmatic access to data without requiring tool calls.

## Resource Definition Format

Resources are defined using the `@mcp.resource()` decorator with a URI string:

```python
@mcp.resource("tailscale://devices")
async def devices_resource() -> str:
    """List all devices in the tailnet."""
    devices = await device_manager.list_devices()
    return json.dumps({"devices": devices, "count": len(devices)})
```

## URI Format

Resources use **URIs** to identify them. The URI format is:

```
<scheme>://<path>
```

### URI Components

1. **Scheme** (e.g., `tailscale://`)
   - Custom scheme identifier for your MCP server
   - Should be consistent across all resources
   - Examples: `tailscale://`, `file://`, `http://`, `custom://`

2. **Path** (e.g., `devices`, `devices/{device_id}`)
   - Hierarchical path identifying the resource
   - Can include path parameters using `{param_name}` syntax
   - Examples: `devices`, `network/status`, `devices/{device_id}`

### URI Examples

**Simple Resources** (no parameters):
```python
@mcp.resource("tailscale://devices")
@mcp.resource("tailscale://network/status")
@mcp.resource("tailscale://monitoring/metrics")
```

**Template Resources** (with path parameters):
```python
@mcp.resource("tailscale://devices/{device_id}")
async def device_resource(device_id: str) -> str:
    """Get details for a specific device."""
    device = await device_manager.get_device(device_id)
    return json.dumps({"device": device})
```

## Resource Function Requirements

1. **Must be async**: Resource functions must be `async def`
2. **Return type**: Must return `str` (usually JSON)
3. **Parameters**: Can accept path parameters from URI template
4. **No side effects**: Resources should be read-only (no mutations)

## What Can Be Used as a Resource?

**Yes, resources are identified by URIs**, but the URI can represent:

1. **Data Collections**: Lists of items
   - `tailscale://devices` - List of all devices
   - `tailscale://users` - List of all users

2. **Individual Items**: Single items with IDs
   - `tailscale://devices/{device_id}` - Specific device
   - `tailscale://users/{user_id}` - Specific user

3. **Computed Data**: Generated or aggregated data
   - `tailscale://network/status` - Current network status
   - `tailscale://monitoring/metrics` - Prometheus metrics
   - `tailscale://security/report` - Security report

4. **Hierarchical Resources**: Nested data structures
   - `tailscale://devices/{device_id}/tags` - Device tags
   - `tailscale://network/topology` - Network topology map

## URI Scheme Best Practices

1. **Use Custom Scheme**: Use a unique scheme for your MCP server
   - ✅ `tailscale://` (for Tailscale MCP)
   - ✅ `file://` (for file system resources)
   - ❌ `http://` (conflicts with web resources)

2. **Be Consistent**: Use the same scheme for all resources
   - ✅ All resources use `tailscale://`
   - ❌ Mixing `tailscale://` and `ts://`

3. **RESTful Design**: Follow REST principles for paths
   - ✅ `tailscale://devices/{device_id}`
   - ✅ `tailscale://network/status`
   - ❌ `tailscale://getDeviceById/{device_id}`

4. **Clear Hierarchy**: Use forward slashes for hierarchy
   - ✅ `tailscale://devices/{device_id}/tags`
   - ❌ `tailscale://devices.{device_id}.tags`

## Current Resources in Tailscale MCP

All resources use the `tailscale://` scheme:

1. `tailscale://devices` - List all devices
2. `tailscale://devices/{device_id}` - Get specific device
3. `tailscale://network/status` - Network status
4. `tailscale://network/topology` - Network topology
5. `tailscale://security/report` - Security report
6. `tailscale://monitoring/metrics` - Prometheus metrics
7. `tailscale://monitoring/health` - Health report

## Accessing Resources

Resources can be accessed via MCP clients:

```python
# Direct resource access
resource_uri = "tailscale://devices"
devices_data = await mcp_client.read_resource(resource_uri)

# Template resource with parameters
resource_uri = "tailscale://devices/d123456"
device_data = await mcp_client.read_resource(resource_uri)
```

## Resources vs Tools

| Feature | Resources | Tools |
|---------|-----------|-------|
| **Purpose** | Read-only data access | Operations/actions |
| **Access** | Via URI | Via function call |
| **Parameters** | Path parameters in URI | Function parameters |
| **Side Effects** | None (read-only) | Can modify state |
| **Caching** | Can be cached | Usually not cached |
| **Return** | String (usually JSON) | Dict with operation results |

## Summary

- **Resources are identified by URIs** (not just URIs, but URI-identified data sources)
- **URI format**: `<scheme>://<path>` with optional `{parameters}`
- **Custom scheme**: Use a unique scheme for your MCP server (e.g., `tailscale://`)
- **Read-only**: Resources should not modify state
- **Async functions**: Resource handlers must be async and return strings
- **Template support**: URIs can include path parameters using `{param_name}` syntax

Resources provide a standardized way to expose read-only data through the MCP protocol, making it easy for clients to access data without invoking tools.

