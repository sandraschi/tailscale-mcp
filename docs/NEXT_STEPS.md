# 🚀 Tailscale-MCP Roadmap & Next Steps

**Last Updated:** 2026-04-02  
**Version:** 2.1.0 (SOTA Baseline)  
**Status:** ✅ v2.1.0 MISSION COMPLETE

---

## ✅ Initial Priority - ACHIEVED
### **Step 1: Create Operations Layer** ⚡ **COMPLETE**
- **Result:** Successfully created `src/tailscalemcp/operations/` with `devices`, `network`, `services`, and `policies`.
- **Impact:** Solid bridge between API client and portmanteau tools.

### **Step 2: Audit & Remove Mock Data** 🔍 **COMPLETE**
- **Result:** All production paths now use the `TailscaleAPIClient`.
- **Impact:** 100% real API integration.

### **Step 3: Add Critical Unit Tests** 🧪 **COMPLETE**
- **Result:** Established a robust testing foundation with ~65%+ coverage (improving).
- **Impact:** CI/CD now verifies API client, models, and operations.

---

### **Step 2: Audit & Remove Mock Data** 🔍 **CRITICAL**

**Why:** Assessment shows mock data still exists in managers. Need to replace with real API calls.

**Estimated Time:** 1-2 days

**Tasks:**

1. **Audit managers for mock data:**
   - `src/tailscalemcp/device_management.py`
   - `src/tailscalemcp/magic_dns.py`
   - `src/tailscalemcp/monitoring.py`
   - `src/tailscalemcp/taildrop.py`

2. **Replace mocks with operations layer calls**

3. **Test each manager with real API** (use test tailnet)

**Files to Audit:**
```python
# Look for patterns like:
- Hardcoded data: devices = [{"id": "mock1", ...}]
- Simulated responses: return {"status": "simulated"}
- Mock functions: async def get_device(): return mock_data
```

**Success Criteria:**
- [ ] All managers use operations layer
- [ ] No hardcoded mock data
- [ ] All operations make real API calls

---

### **Step 3: Add Critical Unit Tests** 🧪 **HIGH**

**Why:** Test coverage is 24%, target is 80%. Need foundation tests for new components.

**Estimated Time:** 2 days

**Tasks:**

1. **Create test directory structure**
   ```bash
   mkdir -p tests/unit tests/integration
   ```

2. **Unit tests for API client:**
   - `tests/unit/test_client.py` - Rate limiting, retry logic, error handling
   - Mock `httpx.AsyncClient` (not internal functions!)

3. **Unit tests for models:**
   - `tests/unit/test_models.py` - Parsing, validation, serialization

4. **Integration tests for operations:**
   - `tests/integration/test_device_operations.py`
   - `tests/integration/test_services_operations.py`
   - Use mocked API responses

**Files to Create:**
```
tests/
├── unit/
│   ├── test_client.py
│   ├── test_rate_limiter.py
│   ├── test_retry.py
│   └── test_models.py
├── integration/
│   ├── test_device_operations.py
│   └── test_services_operations.py
└── conftest.py (fixtures)
```

**Success Criteria:**
- [ ] Unit tests for client, models, rate limiter, retry handler
- [ ] Integration tests for operations layer
- [ ] Coverage increases from 24% → 60%+

---

## 🎯 Future Roadmap (v2.2.0+)

### **Expansion 1: Advanced Network Features** 🌐 **MEDIUM**
- **Task:** Implement `tailscale_funnel` and `tailscale_serve` CLI wrappers.
- **Task:** Add exit node and subnet routing management to `configure_tailnet_network`.

### **Expansion 2: Enhanced Observability** 📊 **LOW**
- **Task:** Integrate with Prometheus/Grafana (refer to `docs/monitoring/`).
- **Task:** Add real-time log streaming to the `Webapp`.

### **Expansion 3: Agentic Hardening** 🛡️ **HIGH**
- **Task:** Improve `run_agentic_tailnet_workflow` with more specialized tool groups.
- **Task:** Implement "Undo" logic for sensitive network changes.

---

### **Step 5: Increase Test Coverage** 📈 **HIGH**

**Why:** Target 80% coverage (GLAMA Gold Standard). Current: 24%.

**Estimated Time:** 3-4 days

**Tasks:**
1. Add tests for all operations
2. Add error handling tests
3. Add performance tests (rate limiting, connection pooling)
4. Set up coverage reporting in CI/CD

**Success Criteria:**
- [ ] Coverage reaches 80%
- [ ] All critical paths tested
- [ ] CI/CD reports coverage

---

### **Step 6: Comprehensive Error Handling** 🛡️ **HIGH**

**Why:** Production readiness requires graceful error handling.

**Estimated Time:** 2 days

**Tasks:**
1. Add graceful degradation patterns
2. Pre-flight validation for destructive operations
3. Better error messages with remediation steps
4. Operation logging and audit trails

**Success Criteria:**
- [ ] All operations have error handling
- [ ] Clear error messages with next steps
- [ ] Audit logging in place

---

## 🎯 Recommended Starting Point

**Start with Step 1: Operations Layer**

This is the foundation that everything else depends on. Once it's in place:
- ✅ Managers can use real API calls
- ✅ Mock data removal becomes straightforward
- ✅ Testing becomes meaningful
- ✅ New features can be added easily

**Suggested Workflow:**
1. Create `operations/devices.py` first (most used)
2. Update `device_management.py` to use it
3. Create `operations/services.py` (quick win)
4. Update portmanteau tools to wire services
5. Then tackle network operations

---

## 📊 Success Metrics

**Week 1 Goals:**
- [ ] Operations layer created
- [ ] Mock data removed from managers
- [ ] Critical unit tests added
- [ ] Test coverage: 24% → 60%+

**Week 2 Goals:**
- [ ] Services integration complete
- [ ] Test coverage: 60% → 80%
- [ ] Error handling improved
- [ ] Documentation updated

---

## 🚨 Critical Reminders

**From AI Development Rules:**
- ❌ **NEVER** add mock data - use real API calls or clear "not implemented" messages
- ✅ Always mock at HTTP client level (`httpx.AsyncClient`), not internal functions
- ✅ Preserve existing functionality
- ✅ Test with real API (use test tailnet) when possible

---

**Last Updated:** 2025-01-15  
**Next Review:** After Step 1 completion







