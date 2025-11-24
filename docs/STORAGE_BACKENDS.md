# FastMCP 2.13+ Storage Backends

FastMCP 2.13+ uses the `py-key-value-aio` library for storage, which provides multiple pluggable storage backends.

## Available Storage Backends

### 1. **MemoryStore (Default)**
- **Type**: Ephemeral in-memory storage
- **Persistence**: ❌ Data lost on restart
- **Speed**: ⚡ Very fast
- **Use Case**: Development, testing, temporary data
- **Configuration**: No configuration needed (default)

```python
# Default - uses MemoryStore automatically
mcp = FastMCP("app-name")
```

### 2. **DiskStore** (Recommended for MCP Servers)
- **Type**: Persistent file-based storage
- **Persistence**: ✅ Survives Claude Desktop restarts and OS reboots
- **Speed**: ⚡ Fast (local filesystem)
- **Use Case**: User preferences, state, cache, session data
- **Storage Location**:
  - **Windows**: `%APPDATA%\app-name`
  - **macOS**: `~/Library/Application Support/app-name`
  - **Linux**: `~/.local/share/app-name`
- **Configuration**: Requires `py-key-value-aio[disk]`

```python
from fastmcp import FastMCP
from key_value.aio.stores.disk import DiskStore

# Explicit DiskStore configuration
mcp = FastMCP(
    "app-name",
    storage=DiskStore(directory="/custom/path")  # Optional custom path
)
```

### 3. **RedisStore**
- **Type**: Distributed in-memory storage
- **Persistence**: ✅ Configurable (can persist to disk)
- **Speed**: ⚡ Very fast (network latency)
- **Use Case**: Multi-instance deployments, production, shared state
- **Configuration**: Requires Redis server

```python
from fastmcp import FastMCP
from key_value.aio.stores.redis import RedisStore

mcp = FastMCP(
    "app-name",
    storage=RedisStore(
        host="localhost",
        port=6379,
        password="your_password",  # Optional
        db=0  # Optional database number
    )
)
```

### 4. **DynamoDB Store** (AWS)
- **Type**: Cloud-based NoSQL database
- **Persistence**: ✅ Fully persistent
- **Speed**: ⚡ Fast (cloud latency)
- **Use Case**: AWS deployments, cloud-native apps
- **Configuration**: Requires AWS credentials

```python
from fastmcp import FastMCP
from key_value.aio.stores.dynamodb import DynamoDBStore

mcp = FastMCP(
    "app-name",
    storage=DynamoDBStore(
        table_name="my-table",
        region="us-east-1"
    )
)
```

### 5. **MongoDB Store**
- **Type**: Document database
- **Persistence**: ✅ Fully persistent
- **Speed**: ⚡ Fast
- **Use Case**: Complex data structures, document storage
- **Configuration**: Requires MongoDB server

```python
from fastmcp import FastMCP
from key_value.aio.stores.mongodb import MongoDBStore

mcp = FastMCP(
    "app-name",
    storage=MongoDBStore(
        connection_string="mongodb://localhost:27017",
        database="mydb",
        collection="storage"
    )
)
```

### 6. **Other Backends**
- **Elasticsearch**: For search and analytics
- **Memcached**: High-performance caching
- **RocksDB**: Embedded key-value store
- **Valkey**: Redis-compatible in-memory store

## Storage Backend Comparison

| Backend | Persistence | Speed | Setup | Best For |
|---------|-------------|-------|-------|----------|
| **MemoryStore** | ❌ No | ⚡⚡⚡ Very Fast | ✅ None | Development, testing |
| **DiskStore** | ✅ Yes | ⚡⚡ Fast | ✅ Easy | MCP servers, user data |
| **RedisStore** | ✅ Yes* | ⚡⚡⚡ Very Fast | ⚠️ Medium | Production, multi-instance |
| **DynamoDB** | ✅ Yes | ⚡ Fast | ⚠️ Medium | AWS deployments |
| **MongoDB** | ✅ Yes | ⚡ Fast | ⚠️ Medium | Complex data structures |

*Redis persistence depends on configuration (RDB/AOF)

## Recommended for MCP Servers

### **DiskStore** (Recommended)
- ✅ **Perfect for MCP servers** - Simple, persistent, no external dependencies
- ✅ Survives Claude Desktop restarts and OS reboots
- ✅ Platform-aware storage locations
- ✅ No database setup required
- ✅ Encrypted by default (with FernetEncryptionWrapper)

### **When to Use Other Backends**

- **RedisStore**: Multi-instance deployments, shared state across servers
- **DynamoDB**: AWS-native deployments, cloud-first architecture
- **MongoDB**: Complex data structures, document-based storage needs
- **MemoryStore**: Development/testing only (data lost on restart)

## Implementation Example

```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from key_value.aio.stores.disk import DiskStore

@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP):
    """Server lifespan with persistent storage."""
    # Storage is automatically available via mcp_instance.storage
    # No explicit initialization needed if using FastMCP's default
    
    # Load state from storage
    last_state = await mcp_instance.storage.get("last_state")
    
    yield  # Server runs here
    
    # Save state to storage
    await mcp_instance.storage.set("last_state", current_state)

# Initialize with DiskStore for persistence
mcp = FastMCP(
    "Tailscale MCP",
    storage=DiskStore(),  # Uses platform-appropriate directory
    lifespan=server_lifespan
)
```

## Storage Locations (DiskStore)

### Windows
```
%APPDATA%\Tailscale Network Controller MCP\
C:\Users\<username>\AppData\Roaming\Tailscale Network Controller MCP\
```

### macOS
```
~/Library/Application Support/Tailscale Network Controller MCP/
```

### Linux
```
~/.local/share/Tailscale Network Controller MCP/
```

## Key-Value Interface

All storage backends use the same simple async interface:

```python
# Set a value
await mcp.storage.set("key", value)

# Get a value
value = await mcp.storage.get("key")

# Delete a value
await mcp.storage.delete("key")

# Check if key exists
exists = await mcp.storage.exists("key")

# List all keys (if supported)
keys = await mcp.storage.keys()
```

## Security

- **DiskStore**: Encrypted by default with FernetEncryptionWrapper
- **RedisStore**: Supports password authentication and SSL/TLS
- **DynamoDB**: Uses AWS IAM for authentication
- **MongoDB**: Supports authentication and SSL/TLS

## Limitations

**Not suitable for:**
- ❌ Large binary files (use file system directly)
- ❌ High-frequency writes (use databases)
- ❌ Complex relational data (use SQL databases)
- ❌ Very large datasets (use specialized databases)

**Perfect for:**
- ✅ User preferences and settings
- ✅ Current state and context
- ✅ Cache data (API responses, computed results)
- ✅ Session data (OAuth tokens, authentication state)
- ✅ Device/connection state
- ✅ Last used values (filters, search terms)
- ✅ Statistics and metrics
- ✅ Configuration overrides

## Resources

- **py-key-value-aio**: [PyPI Package](https://pypi.org/project/py-key-value-aio/)
- **FastMCP Documentation**: [FastMCP Docs](https://gofastmcp.com/docs)
- **Storage Pattern Guide**: `docs/patterns/FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md`

---

**Last Updated**: 2025-11-24

