# Tailscale Status Tool - Usage Guide

## Getting Status with Mermaid Diagram

To get the tailnet status **with** a Mermaid diagram visualization, use:

```python
tailscale_status(include_mermaid_diagram=True)
```

## Examples

### Basic Status with Diagram
```python
# Simple call - get status with Mermaid diagram
result = await tailscale_status(include_mermaid_diagram=True)

# The diagram will be in:
diagram = result["status"]["mermaid_diagram"]
print(diagram)  # Mermaid code ready to render
```

### Advanced Status with Diagram
```python
# Get comprehensive status with diagram
result = await tailscale_status(
    detail_level="advanced",
    include_metrics=True,
    include_performance=True,
    include_mermaid_diagram=True  # Enable diagram
)

# Access the diagram
if "mermaid_diagram" in result["status"]:
    mermaid_code = result["status"]["mermaid_diagram"]
    # Copy this to https://mermaid.live/ to view
```

### Status Without Diagram (Default)
```python
# Regular status call (no diagram)
result = await tailscale_status()
# mermaid_diagram field will not be present
```

## Response Structure

When `include_mermaid_diagram=True`, the response includes:

```json
{
  "component": "overview",
  "detail_level": "basic",
  "timestamp": 1732406400.0,
  "status": {
    "system": {...},
    "devices": {...},
    "network": {...},
    "mcp_server": {...},
    "mermaid_diagram": "graph TB\n    %% Tailnet Topology: 5 devices..."
  }
}
```

## Using the Diagram

### Option 1: View Online
1. Get the status with diagram:
   ```python
   result = await tailscale_status(include_mermaid_diagram=True)
   ```
2. Copy the `mermaid_diagram` field value
3. Paste into https://mermaid.live/
4. See the rendered diagram!

### Option 2: Save to File
```python
result = await tailscale_status(include_mermaid_diagram=True)
mermaid_code = result["status"]["mermaid_diagram"]

# Save to file
with open("tailnet_diagram.mmd", "w") as f:
    f.write(mermaid_code)

# Or save as markdown
with open("tailnet_diagram.md", "w") as f:
    f.write("```mermaid\n")
    f.write(mermaid_code)
    f.write("\n```\n")
```

### Option 3: Use in Documentation
The Mermaid code can be embedded directly in Markdown files:

````markdown
# My Tailnet Topology

```mermaid
graph TB
    %% Paste the mermaid_diagram content here
```
````

## Full Parameter Reference

```python
tailscale_status(
    component: str | None = None,              # Component to check
    detail_level: str = "basic",               # basic, intermediate, advanced, diagnostic
    include_metrics: bool = True,              # Include performance metrics
    include_health: bool = True,               # Include health assessments
    include_performance: bool = False,         # Include detailed performance data
    device_filter: str | None = None,          # Filter devices by status or tags
    time_range: str = "1h",                    # Time range for metrics
    include_mermaid_diagram: bool = False      # ⭐ Enable Mermaid diagram
)
```

## Quick Test

Try this in Claude Desktop or your MCP client:

```
Get the tailscale status with a Mermaid diagram showing all devices and funnels
```

Or explicitly:

```
tailscale_status(include_mermaid_diagram=True)
```

## What the Diagram Shows

- ✅ All devices (online/offline with color coding)
- ✅ Exit nodes (red border)
- ✅ Subnet routers (teal border)
- ✅ Active Funnels (gold nodes with public URLs)
- ✅ Device tags
- ✅ Network topology (simplified mesh)
- ✅ Legend explaining colors

---

**Last Updated**: 2025-11-24

