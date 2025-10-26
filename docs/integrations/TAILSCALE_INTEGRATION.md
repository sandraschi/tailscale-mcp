# Tailscale Integration Documentation

## Overview

This document provides comprehensive information about Tailscale integration in the tailscale-mcp server. For official Tailscale documentation, visit the [Tailscale Docs](https://tailscale.com/kb/).

## API Device Management

### Device Status Fields

The Tailscale API provides several fields for determining device connectivity:

#### `connectedToControl` Field

The primary indicator for whether a device is online:

- **`True`**: Device is currently connected to the Tailscale control server
- **`False`**: Device is not connected to the control server

This is the **most reliable** field for determining online status, as it indicates active connection to the control server.

#### `lastSeen` Field

- Indicates when the device was last seen by the control server
- Format: ISO 8601 timestamp (e.g., `"2025-10-26T10:17:16Z"`)
- Can be used to determine if a device has been recently active

#### `authorized` Field

- Indicates whether the device is authorized to be on the tailnet
- An authorized device may still be offline

### Example API Response

```json
{
  "addresses": ["100.102.236.121", "fd7a:115c:a1e0::c601:ec79"],
  "id": "989217924652354",
  "nodeId": "nMCsaV52j811CNTRL",
  "user": "sandraschipal@hotmail.com",
  "name": "flowsy.tailfab45.ts.net",
  "hostname": "Flowsy",
  "clientVersion": "1.80.2-t62b8bf6a0-g3c35ee987",
  "updateAvailable": true,
  "os": "windows",
  "created": "2025-03-09T20:13:24Z",
  "connectedToControl": false,
  "lastSeen": "2025-03-12T11:57:18Z",
  "expires": "2025-09-05T20:13:24Z",
  "keyExpiryDisabled": true,
  "authorized": true,
  "isExternal": false,
  "machineKey": "mkey:...",
  "nodeKey": "nodekey:...",
  "tailnetLockKey": "nlpub:...",
  "blocksIncomingConnections": false,
  "tailnetLockError": ""
}
```

## Device Management Operations

### List Devices

The `tailscale_device` tool with `operation="list"` retrieves all devices from your tailnet:

```python
{
  "operation": "list",
  "devices": [...],
  "count": 7,
  "filters": {
    "online_only": false,
    "filter_tags": []
  }
}
```

### Filtering Options

#### Online Only Filter

To list only online devices:

```python
{
  "operation": "list",
  "online_only": true
}
```

This uses the `connectedToControl` field to filter devices.

#### Tag Filtering

Filter devices by tags:

```python
{
  "operation": "list",
  "filter_tags": ["server", "production"]
}
```

### Device Information

Each device returned includes:

- **device_id**: Unique device identifier
- **name**: Device name
- **hostname**: Device hostname
- **os**: Operating system
- **ip_addresses**: Tailscale IP addresses
- **status**: "online" or "offline" (based on `connectedToControl`)
- **last_seen**: Last seen timestamp
- **authorized**: Authorization status
- **tags**: Device tags
- **is_exit_node**: Whether this device can be used as an exit node
- **is_subnet_router**: Whether this device is advertising subnet routes

## Common Issues

### Incorrect Online Status

If devices show incorrect online/offline status:

1. **Check `connectedToControl` field**: This is the authoritative source
2. **Verify API key**: Ensure the API key has proper permissions
3. **Check lastSeen timestamp**: Devices may be "online" but not recently active

### API Authentication

If you receive `401 Unauthorized` errors:

1. Verify your API key is correct
2. Check that the API key is in the Claude Desktop configuration
3. Ensure the tailnet ID matches your tailnet

### Device Not Found

If a device doesn't appear in the list:

1. Verify the device is authorized on your tailnet
2. Check if the device has been removed or expired
3. Ensure the API key has permissions to view all devices

### iOS Background App Behavior

iOS devices (iPad, iPhone) may show `connectedToControl=True` even when the device is off or the Tailscale app is backgrounded. To address this:

1. **iOS Background Apps**: Tailscale can remain "connected" in the background even when not actively used
2. **Time Window**: The tool uses the `lastSeen` timestamp to determine true online status (seen within last 30 minutes = online)
3. **Combined Logic**: A device is truly online only if `connectedToControl=True` AND seen within last 30 minutes

This is a compromise between accuracy and usability:
- Devices active within the last 30 minutes are considered online
- Devices inactive for more than 30 minutes are considered offline
- This catches offline iOS devices while being reasonable for active devices

## Official Tailscale Documentation

For complete documentation on device management, see:

- [Manage devices](https://tailscale.com/kb/1372/manage-devices)
- [Device approval](https://tailscale.com/kb/1372/manage-devices#device-approval)
- [Device posture management](https://tailscale.com/kb/1372/manage-devices#device-posture-management)
- [Add a device](https://tailscale.com/kb/1372/manage-devices#add-a-device)
- [Remove a device](https://tailscale.com/kb/1372/manage-devices#remove-a-device)

## API Reference

For complete API documentation:

- [Tailscale API Reference](https://pkg.go.dev/tailscale.com/client/tailscale)
- [Tailscale Web API](https://github.com/tailscale/tailscale/tree/main/api)

## Integration Notes

### Implementation Details

The tailscale-mcp server uses the `connectedToControl` field for determining online status because:

1. It's the most reliable indicator of device connectivity
2. It's updated in real-time by the control server
3. It doesn't rely on timestamp calculations
4. It matches the Tailscale web UI behavior

### Timestamp Parsing

The `lastSeen` field is parsed from ISO 8601 format:

```python
from datetime import datetime

# Parse ISO timestamp
last_seen_ts = datetime.fromisoformat(
    api_device.get("lastSeen").replace('Z', '+00:00')
).timestamp()
```

### Online Status Calculation

```python
# Use connectedToControl as the authoritative source
is_online = api_device.get("connectedToControl", False)
```

This is more reliable than calculating based on timestamp differences.

## Related Documentation

- [Tailscale MCP Architecture](./ARCHITECTURE_AND_DESIGN.md)
- [API Reference](./API_REFERENCE.md)
- [Monitoring Stack](./monitoring/README.md)
- [RebootX Integration](./integrations/REBOOTX_INTEGRATION.md)

