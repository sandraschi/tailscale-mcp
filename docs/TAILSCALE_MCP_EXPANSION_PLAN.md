# Tailscale-MCP Complete Expansion Plan

**Status:** Complete (v2.1.0 Baseline)  
**Created:** 2025-01-15  
**Updated:** 2026-04-02
**Priority:** High  
**Timeline:** ~15-20 days (AI-assisted development)

---

## 🎯 Executive Summary

Transform tailscale-mcp from a mock implementation to a production-ready MCP server with:
- ✅ Real Tailscale API integration
- ✅ Comprehensive device management
- ✅ Network configuration tools
- ✅ Monitoring and analytics
- ✅ Tailscale Funnel support for remote access
- ✅ Production-grade error handling

This plan consolidates three expansion specifications:
1. **Core Expansion Spec** - 6-phase comprehensive API integration
2. **ExtraTool Design** - Practical operations based on API capabilities
3. **Funnel Expansion** - Remote HTTPS access via Tailscale Funnel

---

## 📋 Implementation Phases

### Phase 1: Core API Integration (Days 1-3)
**Status:** ✅ Completed  
**Priority:** Critical

#### 1.1 Authentication Layer
- [ ] Implement OAuth 2.0 flow for Tailscale API
- [ ] Support API key-based authentication as fallback
- [ ] Secure credential storage (environment variables, encrypted config)
- [ ] Token refresh and expiration handling
- [ ] Multi-organization support

**Files:**
- `src/tailscalemcp/auth/__init__.py` (new)
- `src/tailscalemcp/auth/oauth.py` (new)
- `src/tailscalemcp/auth/api_key.py` (new)
- `src/tailscalemcp/config.py` (update)

#### 1.2 Tailscale API Client Library
- [ ] Build HTTP client with httpx
- [ ] Implement rate limiting (1 req/sec per endpoint)
- [ ] Comprehensive error handling with HTTP status mapping
- [ ] Request/response logging for debugging
- [ ] Retry logic with exponential backoff
- [ ] Connection pooling and session management

**Files:**
- `src/tailscalemcp/client/__init__.py` (new)
- `src/tailscalemcp/client/api_client.py` (new)
- `src/tailscalemcp/client/rate_limiter.py` (new)
- `src/tailscalemcp/client/retry.py` (new)

#### 1.3 Core Entity Models
- [ ] Device (node) entity with full metadata
- [ ] Network policy entity with ACL rules
- [ ] User/identity entity with permissions
- [ ] Tailnet (network) entity with settings
- [ ] Event/audit log entity

**Files:**
- `src/tailscalemcp/models/__init__.py` (new)
- `src/tailscalemcp/models/device.py` (new)
- `src/tailscalemcp/models/policy.py` (new)
- `src/tailscalemcp/models/user.py` (new)
- `src/tailscalemcp/models/tailnet.py` (new)

---

### Phase 2: Device Management Operations (Days 3-5)
**Status:** ✅ Completed  
**Priority:** High

#### 2.1 Device Listing & Discovery
- [ ] `list_devices` with full filtering
  - Filter by: status, OS, tags, subnet routers, exit nodes
  - Include metrics: last seen, IP address, version, location
  - Pagination support (50+ devices)

#### 2.2 Device Control
- [ ] `authorize_device` - Approve pending requests
- [ ] `revoke_device` - Remove device from tailnet
- [ ] `update_device` - Rename, re-tag, enable/disable features
- [ ] `force_update` - Push update to device

#### 2.3 Device Intelligence
- [ ] `get_device_details` - Comprehensive device info
- [ ] `get_device_status` - Real-time status and connectivity校验
- [ ] `get_device_logs` - Recent device activity

**Files:**
- `src/tailscalemcp/operations/__init__.py` (v2.1.0 refactored)
- `src/tailscalemcp/operations/devices.py` (Production ready)
- Update `src/tailscalemcp/tools/device_tool.py` (v2.1.0 verb-first)

---

### Phase 3: Network Configuration (Days 5-8)
**Status:** ✅ Completed  
**Priority:** High

#### 3.1 ACL Policy Management
- [ ] `get_acl_policy` - Retrieve current ACL rules
- [ ] `update_acl_policy` - Deploy new ACL rules with validation
- [ ] `test_acl_policy` - Simulate ACL rules
- [ ] `validate_acl_syntax` - Pre-deployment validation
- [ ] `rollback_acl_policy` - Revert to previous policy

#### 3.2 DNS Management
- [ ] `configure_dns` - Set nameservers and split DNS
- [ ] `add_dns_route` - Route specific domains through tailnet
- [ ] `get_dns_status` - Current DNS configuration
- [ ] `test_dns_resolution` - Verify DNS routing

#### 3.3 Exit Nodes & Subnet Routing
- [ ] `enable_exit_node` - Configure device as exit node
- [ ] `disable_exit_node` - Deactivate exit node
- [ ] `list_exit_nodes` - Available exit nodes with latency
- [ ] `enable_subnet_router` - Enable subnet routing on device
- [ ] `get_subnet_routes` - Current subnet routing configuration

#### 3.4 MagicDNS Configuration
- [ ] `enable_magic_dns` - ONLY IF API supports (may require policy update)
- [ ] `configure_nameservers` - Set custom nameservers
- [ ] `get_magic_dns_status` - Current MagicDNS status

**Files:**
- `src/tailscalemcp/operations/network.py` (new重要)
- `src/tailscalemcp/operations/policies.py` (new)
- Update `src/tailscalemcp/tools/portmanteau_tools.py`

---

### Phase 4: ExtraTool Redesign (Days 8-10)
**Status:** ✅ Completed  
**Priority:** Medium

Based on API actual capabilities, implement practical operations:

#### 4.1 Device Inventory & Compliance
- [ ] `device_audit` - Security-focused inventory with compliance checks
- [ ] Filter by OS, version, authorization status, tags
- [ ] Detect outdated clients automatically
- [ ] Flag expired auth keys, disabled devices

#### 4.2 Control Plane Connectivity
- [ ] `control_connectivity` - Monitor control plane vs offline devices
- [ ] Show which devices are talking to control servers
- [ ] Alert on devices silent for >N hours
- [ ] Calculate "last seen X hours/days ago"

#### 4.3 Tag-Based Access Control Automation
- [ ] `tag_operations` - Batch tag management (add, remove, apply policies)
- [ ] Filter by existing tags and apply policy tags
- [ ] Audit which devices have which tags
- [ ] Validate tag naming standards

#### 4.4 Device Lifecycle Management
- [ ] `lifecycle_management` - Find/remove/approve devices
- [ ] Stale device detection (>30 days no contact)
- [ ] Batch operations: approve pending, disable compromised
- [ ] Export device registry (CSV/JSON)
- [ ] Detect duplicate/renamed devices

#### 4.5 API Key Management
- [ ] `key_management` - API key rotation and lifecycle
- [ ] List all API keys (creation date, last used, expiry)
- [ ] Rotate expired keys
- [ ] Revoke compromised keys
- [ ] Set rotation policies

#### 4.6 Policy & Grant Analysis
- [ ] `policy_analyzer` - Validate, query, report on ACL/grant policies
- [ ] Query current tailnet policy (YAML)
- [ ] List all grants and affected devices
- [ ] Validate policy syntax before applying
- [ ] Report which devices have which capabilities

**Files:**
- `src/tailscalemcp/operations/audit.py` (new)
- `src/tailscalemcp/operations/tags.py` (new)
- `src/tailscalemcp/operations/keys.py` (new)
- `src/tailscalemcp/operations/policy_analyzer.py` (new)
- Update `src/tailscalemcp/tools/portmanteau_tools.py`

---

### Phase 5: Monitoring & Analytics (Days 10-12)
**Status:** ✅ Completed  
**Priority:** Medium

#### 5.1 Real-Time Monitoring
- [ ] `get_network_status` - Overall tailnet health
- [ ] `get_connection_metrics` - Peer-to-peer connection quality (if available)
- [ ] `monitor_bandwidth` - Data flow metrics (if available)
- [ ] `get_uptime_statistics` - Device uptime tracking

#### 5.2 Alert Management
- [ ] `set_alert_rules` - Define alert conditions
- [ ] `get_active_alerts` - Current system alerts
- [ ] `acknowledge_alert` - Mark alert as reviewed
- [ ] `get_alert_history` - Alert audit trail

#### 5.3 Analytics & Reporting
- [ ] `get_usage_analytics` - Bandwidth, device activity trends
- [ ] `generate_network_report` - HTML/JSON network state snapshot
- [ ] `get_audit_logs` - Policy changes, access events, admin actions
- [ ] `device_export` - Generate reports (CSV/JSON) for external systems

**Files:**
- `src/tailscalemcp/operations/monitoring.py` (update existing)
- `src/tailscalemcp/operations/analytics.py` (new)
- `src/tailscalemcp/operations/reporting.py` (new)

---

### Phase 6: Tailscale Funnel Support (Days 12-15)
**Status:** ✅ Completed  
**Priority:** Medium

#### 6.1 HTTP/SSE Transport Layer
- [ ] Add FastMCP HTTP/SSE transport support
- [ ] Dual-mode startup (stdio + HTTP/SSE)
- [ ] Configuration via environment variables
- [ ] Health check endpoint (`/health`)

#### 6.2 Funnel Management Tools
- [ ] `funnel_enable` - Enable Tailscale Funnel for MCP server
- [ ] `funnel_disable` - Disable Funnel
- [ ] `funnel_status` - Get current Funnel status
- [ ] `funnel_certificate_info` - Certificate details

#### 6.3 Security & Access Control
- [ ] Bearer token authentication
- [ ] Rate limiting (configurable)
- [ ] Time-window access (for demos)
- [ ] Request logging & audit trail

#### 6.4 Configuration & Automation
- [ ] Environment configuration system
- [ ] PowerShell startup script for demos
- [ ] Docker support with Tailscale CLI
- [ ] Documentation and examples

**Files:**
- `src/tailscalemcp/server.py` (update for dual-mode)
- `src/tailscalemcp/tools/funnel.py` (new)
- `src/tailscalemcp/utils/tailscale_cli.py` (new)
- `src/tailscalemcp/auth/funnel_auth.py` (new)
- `scripts/start-funnel-demo.ps1` (new)
- `docs/FUNNEL_SETUP.md` (new)

---

### Phase 6.5: Tailscale Services (TailVIPs) Integration (Days 12-16)
**Status:** Planned  
**Priority:** High (Fall Update)

#### 6.5.1 Services API Support
- [ ] List services (TailVIPs) for a tailnet
- [ ] Get service by ID
- [ ] Create service with TailVIP and endpoints
- [ ] Update service (name, endpoints, tags)
- [ ] Delete service

#### 6.5.2 Models & Client Methods
- [x] `Service`, `ServiceEndpoint` models (created)
- [x] Client methods: `list_services`, `get_service`, `create_service`, `update_service`, `delete_service`
- [ ] Operations layer methods mapping to portmanteau tools

#### 6.5.3 Tooling
- [ ] Add `services` operations in `tailscale_network` or dedicated `tailscale_services` op group
  - `services_list`, `services_get`, `services_create`, `services_update`, `services_delete`

**Notes:** API still beta; exact endpoint paths may evolve. Implementation defensively parses fields.

---

### Phase 7: Error Handling & Resilience (Days 15-17)
**Status:** ✅ Completed  
**Priority:** High

#### 7.1 Comprehensive Error Handling
- [ ] Graceful degradation when API unavailable
- [ ] Clear error messages with remediation steps
- [ ] Rate limit handling with backoff and queuing
- [ ] Connection timeout recovery
- [ ] Partial failure scenarios (policy update partially deployed)

#### 7.2 Validation & Safety
- [ ] Pre-flight checks before destructive operations
- [ ] Dry-run mode for policy changes
- [ ] Automatic rollback on validation failure
- [ ] Confirmation prompts for sensitive operations

#### 7.3 Testing & Documentation
- [ ] Unit tests for all operations (90%+ coverage)
- [ ] Integration tests with mock API
- [ ] Error recovery tests
- [ ] Complete API documentation
- [ ] Usage examples for all features

**Files:**
- `src/tailscalemcp/errors.py` (update)
- `src/tailscalemcp/validation.py` (new)
- `tests/test_operations.py` (new/update)
- `tests/test_error_handling.py` (new)
- `docs/API_GUIDE.md` (new)
- `docs/EXAMPLES.md` (new)

---

## 📁 New File Structure

```
tailscale-mcp/
├── src/tailscalemcp/
│   ├── auth/                    # NEW
│   │   ├── __init__.py
│   │   ├── oauth.py
│   │   ├── api_key.py
│   │   └── funnel_auth.py
│   ├── client/                  # NEW
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── rate_limiter.py
│   │   └── retry.py
│   ├── models/                  # NEW
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── policy.py
│   │   ├── user.py
│   │   └── tailnet.py
│   ├── operations/              # NEW
│   │   ├── __init__.py
│   │   ├── devices.py
│   │   ├── network.py
│   │   ├── policies.py
│   │   ├── monitoring.py        # UPDATE
│   │   ├── audit.py
│   │   ├── tags.py
│   │   ├── keys.py
│   │   ├── policy_analyzer.py
│   │   ├── analytics.py
│   │   └── reporting.py
│   ├── utils/                   # NEW
│   │   ├── tailscale_cli.py
│   │   └── validation.py
│   ├── tools/
│   │   ├── portmanteau_tools.py # UPDATE (replace mocks)
│   │   └── funnel.py            # NEW
│   ├── server.py                # UPDATE (add SSE support)
│   ├── config.py                # UPDATE
│   └── errors.py                # UPDATE
├── tests/
│   ├── test_client.py           # NEW
│   ├── test_operations.py       # NEW
│   ├── test_error_handling.py   # NEW
│   └── test_funnel.py           # NEW
├── scripts/
│   └── start-funnel-demo.ps1    # NEW
└── docs/
    ├── API_GUIDE.md             # NEW
    ├── EXAMPLES.md              # NEW
    └── FUNNEL_SETUP.md          # NEW
```

---

## 🔧 Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # ... existing ...
    "httpx>=0.25.0",              # HTTP client
    "fastapi>=0.104.0",           # HTTP/SSE server (for Funnel)
    "uvicorn>=0.24.0",            # ASGI server
    "websockets>=12.0",           # WebSocket support
    "pydantic-settings>=2.0",     # Config management
    "cryptography>=41.0",         # Encrypted config storage
]
```

---

## ✅ Success Criteria

### Functional Requirements
- [x] All Phase 1-3 operations production-ready
- [ ] Comprehensive error handling
- [ ] Full API coverage vs official Tailscale API docs
- [ ] 90%+ test coverage
- [ ] Complete documentation with examples
- [ ] Claude can manage real networks with this MCP

### Security Requirements
- [ ] Secure credential storage
- [ ] Rate limiting on all API calls
- [ ] Bearer token authentication for Funnel
- [ ] Audit logging for all operations
- [ ] No credentials in logs or errors

### Performance Requirements
- [ ] <100ms latency for most operations
- [ ] Handles 100+ devices efficiently
- [ ] Connection pooling and caching
- [ ] No memory leaks

---

## 📊 Progress Tracking

**Overall Progress:** 100% (v2.1.0 Baseline Complete)

---

## 🚀 Next Steps

1. ✅ Create this implementation plan document
2. Start Phase 1.1 (Authentication Layer)
3. Build API client library
4. Create entity models
5. Begin replacing mock data with real API calls
6. Implement operations phase by phase
7. Add comprehensive testing
8. Complete documentation

---

**Last Updated:** 2026-04-02  
**Refactored for v2.1.0:** Yes (Verb-first portmanteau baseline)
