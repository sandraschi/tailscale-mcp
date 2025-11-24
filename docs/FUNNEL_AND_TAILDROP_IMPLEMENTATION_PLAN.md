# Tailscale Funnel and Taildrop Enhancement Plan

## Overview

Implement Tailscale Funnel support (new feature) and enhance existing Taildrop implementation to use real Tailscale CLI/API integration.

## Current Status

### Taildrop
- ✅ **Implemented**: Full `TaildropManager` class with 7 operations
- ⚠️ **Issue**: Current implementation is simulated (doesn't use real Tailscale API/CLI)
- ✅ **Tool**: `tailscale_file` portmanteau tool exists and works

### Funnel
- ❌ **Not Implemented**: Planned in Phase 6 but not started
- ✅ **Config**: Configuration exists in `config.py`
- ❌ **Tool**: No `tailscale_funnel` tool yet

## Implementation Plan

### Part 1: Enhance Taildrop Implementation

#### 1.1 Research Taildrop API/CLI Integration
- Verify if Tailscale API v2 has Taildrop endpoints
- Check Tailscale CLI commands for Taildrop (`tailscale file send`, etc.)
- Document actual Taildrop integration methods

#### 1.2 Create Tailscale CLI Integration Utility
**File**: `src/tailscalemcp/utils/tailscale_cli.py` (new)
- Create `TailscaleCLI` class for executing Tailscale CLI commands
- Support for `tailscale file send <file> <device>`
- Support for `tailscale file get` operations
- Error handling and output parsing
- Cross-platform support (Windows, macOS, Linux)

#### 1.3 Enhance TaildropManager
**File**: `src/tailscalemcp/taildrop.py`
- Integrate with Tailscale CLI for real file transfers
- Keep simulation mode as fallback if CLI unavailable
- Add real file transfer progress tracking
- Improve error handling with actual Tailscale errors
- Add support for Taildrop directory monitoring (if applicable)

#### 1.4 Update tailscale_file Tool
**File**: `src/tailscalemcp/tools/portmanteau_tools.py`
- Verify all 7 operations work with enhanced TaildropManager
- Update docstrings with real Taildrop usage examples
- Add error handling for CLI integration failures

### Part 2: Implement Funnel Support

#### 2.1 Create FunnelManager Class
**File**: `src/tailscalemcp/funnel.py` (new)
- `FunnelManager` class similar to `TaildropManager`
- Integrate with Tailscale CLI (`tailscale funnel` commands)
- Support operations:
  - `enable_funnel(port, target, https_port=None)` - Enable Funnel for service
  - `disable_funnel(port)` - Disable Funnel
  - `get_funnel_status(port=None)` - Get Funnel status
  - `list_active_funnels()` - List all active Funnels
  - `get_certificate_info()` - Get TLS certificate information
- Error handling and validation
- Support for both HTTP and HTTPS Funnels

#### 2.2 Create tailscale_funnel Portmanteau Tool
**File**: `src/tailscalemcp/tools/portmanteau_tools.py`
- Add `tailscale_funnel` tool with operations:
  - `funnel_enable` - Enable Funnel for a service
  - `funnel_disable` - Disable Funnel
  - `funnel_status` - Get Funnel status
  - `funnel_list` - List active Funnels
  - `funnel_certificate_info` - Get certificate details
- Follow portmanteau pattern like other tools
- Comprehensive docstrings with examples

#### 2.3 Integrate FunnelManager into MCP Server
**File**: `src/tailscalemcp/mcp_server.py`
- Initialize `FunnelManager` in server startup
- Pass to portmanteau tools
- Add cleanup on shutdown

#### 2.4 Update Configuration
**File**: `src/tailscalemcp/config.py`
- Verify existing Funnel config fields are sufficient
- Add any missing configuration options
- Document configuration requirements

### Part 3: Documentation and Testing

#### 3.1 Update Documentation
**Files**: 
- `README.md` - Add Funnel and enhanced Taildrop sections
- `docs/API_REFERENCE.md` - Document new Funnel tool
- `docs/TAILSCALE_MCP_EXPANSION_PLAN.md` - Mark Phase 6 as complete
- Create `docs/FUNNEL_SETUP.md` - Funnel setup guide

#### 3.2 Create Examples
**Files**:
- `examples/funnel_demo.py` - Funnel usage examples
- `examples/taildrop_enhanced.py` - Enhanced Taildrop examples

#### 3.3 Update Tests
**Files**:
- `tests/test_taildrop.py` - Test enhanced Taildrop (if not exists)
- `tests/test_funnel.py` - Test Funnel implementation (new)
- Mock Tailscale CLI calls for testing

#### 3.4 Update CHANGELOG
**File**: `CHANGELOG.md`
- Document Funnel implementation
- Document Taildrop enhancements

## Technical Details

### Tailscale CLI Integration

Both Taildrop and Funnel require Tailscale CLI integration:

```python
# Example CLI integration pattern
import subprocess
import asyncio

async def run_tailscale_cli(command: list[str]) -> dict[str, Any]:
    """Execute Tailscale CLI command."""
    process = await asyncio.create_subprocess_exec(
        "tailscale",
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    # Parse output and return structured data
```

### Funnel Operations

**Enable Funnel:**
```bash
tailscale funnel <port>                    # HTTP
tailscale funnel --https=443 <target>      # HTTPS
tailscale funnel 8080                      # Expose port 8080
```

**Disable Funnel:**
```bash
tailscale funnel <port> off
```

**Status:**
```bash
tailscale funnel status
```

### Taildrop Operations

**Send File:**
```bash
tailscale file send <file> <device-name>
```

**Receive Files:**
- Files appear in Taildrop directory (platform-specific)
- Monitor directory for incoming files

## Files to Create/Modify

### New Files
1. `src/tailscalemcp/utils/tailscale_cli.py` - CLI integration utility
2. `src/tailscalemcp/funnel.py` - FunnelManager class
3. `tests/test_funnel.py` - Funnel tests
4. `docs/FUNNEL_SETUP.md` - Funnel setup guide
5. `examples/funnel_demo.py` - Funnel examples

### Modified Files
1. `src/tailscalemcp/taildrop.py` - Enhance with CLI integration
2. `src/tailscalemcp/tools/portmanteau_tools.py` - Add tailscale_funnel tool
3. `src/tailscalemcp/mcp_server.py` - Initialize FunnelManager
4. `src/tailscalemcp/config.py` - Verify/update Funnel config
5. `README.md` - Update with Funnel and Taildrop info
6. `docs/API_REFERENCE.md` - Document Funnel tool
7. `CHANGELOG.md` - Document changes
8. `manifest.json` - Add Funnel tool to manifest

## Implementation Order

1. **Phase 1**: Create Tailscale CLI utility (foundation for both)
2. **Phase 2**: Enhance Taildrop with CLI integration
3. **Phase 3**: Create FunnelManager class
4. **Phase 4**: Create tailscale_funnel portmanteau tool
5. **Phase 5**: Integration and testing
6. **Phase 6**: Documentation and examples

## Success Criteria

- ✅ Taildrop uses real Tailscale CLI for file transfers
- ✅ Funnel can be enabled/disabled via MCP tool
- ✅ Funnel status can be queried
- ✅ All operations have proper error handling
- ✅ Documentation is complete
- ✅ Tests pass
- ✅ No linting errors

## Notes

- Taildrop and Funnel are primarily CLI-based features
- API endpoints may not exist for all operations
- CLI integration requires Tailscale client to be installed
- Cross-platform compatibility is important
- Error handling should gracefully handle CLI unavailability


