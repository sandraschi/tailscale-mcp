# Tailscale-MCP User Guide

## Getting Started

Tailscale-MCP gives you comprehensive control over your Tailscale tailnet. You can manage devices, configure ACL policies, set up funnel services, monitor network health, perform security audits, and automate routine tasks. Start by checking the server status to confirm connectivity.

### Checking Connectivity

```
health()
```

This confirms the MCP server is running and the Tailscale API is reachable. For more detail:

```
api_status()
```

This shows API version, rate limit status, and authentication state. If either fails, check your TAILSCALE_API_KEY and TAILSCALE_TAILNET environment variables.

### Testing Credentials

```
test_credentials()
```

This explicitly validates your API key and tailnet against the Tailscale API. Use this when troubleshooting authentication issues.

## Device Management

The tailscale_devices portmanteau tool provides comprehensive device lifecycle management.

### Listing Devices

```
tailscale_devices(operation="list")
```

Returns all devices in the tailnet with their hostname, IP addresses (both Tailscale and private), OS, tags, user, online status, last seen time, and expiry. Filter by online status:

```
tailscale_devices(operation="get_authorized")
tailscale_devices(operation="get_pending")
```

### Getting Device Details

```
tailscale_devices(operation="get_device_details", device_id="12345")
```

Returns full device information including all IPs, OS version, Tailscale version, capabilities, routes, tags, and creation date.

### Authorizing Devices

When a new device requests to join your tailnet, authorize it:

```
tailscale_devices(operation="authorize", device_id="12345")
```

Optionally provide a reason for audit logging:

```
tailscale_devices(operation="authorize", device_id="12345", reason="New developer workstation")
```

### Managing Device Tags

Tags are used for ACL-based access control. Assign or remove tags:

```
tailscale_devices(operation="set_tags", device_id="12345", tags=["production", "web-server"])
tailscale_devices(operation="set_attributes", device_id="12345", attributes={"role": "api-server"})
```

### Device Routes

Manage subnet routes advertised by devices:

```
tailscale_devices(operation="list_routes", device_id="12345")
tailscale_devices(operation="approve_routes", device_id="12345", routes=["10.0.1.0/24"])
```

### Expiring Devices

For temporary access, expire a device:

```
tailscale_devices(operation="expire_now", device_id="12345")
```

This immediately revokes the device's authentication. The device can re-authenticate if it has a valid auth key.

## Network Operations

The tailscale_network tool manages tailnet-wide network configuration.

### Network Status

```
tailscale_network(operation="get_status")
```

Returns the overall network topology including all connected devices, their routes, and network health indicators.

### DNS Configuration

```
tailscale_network(operation="get_dns")
tailscale_network(operation="set_dns", nameservers=["1.1.1.1", "8.8.8.8"], search_domains=["internal.example.com"])
tailscale_network(operation="enable_magic_dns")
```

MagicDNS automatically assigns DNS names to all devices in the tailnet (e.g., dev-machine.tailnet-name.ts.net).

### Subnet Routes

```
tailscale_network(operation="get_subnet_routes")
tailscale_network(operation="set_routes", routes=["10.0.0.0/16", "192.168.1.0/24"])
```

Subnet routes allow devices outside your tailnet to access resources on your local network through Tailscale.

## ACL & Policy Management

The tailscale_policies tool manages the Tailscale ACL (Hubert ACL) system.

### Viewing and Editing ACLs

```
tailscale_policies(operation="get_acl")
```

Returns the current ACL as JSON with tags, groups, hosts, ACL rules, and tests. Use set_acl to update:

```
tailscale_policies(operation="set_acl", acl={...})
```

Before applying changes, validate:

```
tailscale_policies(operation="validate", acl={...})
```

### ACL Versioning

Tailscale supports ACL versioning for safe changes:

```
tailscale_policies(operation="list_versions")
tailscale_policies(operation="get_version", version_id="v123")
tailscale_policies(operation="diff_versions", version_id_a="v123", version_id_b="v124")
tailscale_policies(operation="apply_version", version_id="v124")
tailscale_policies(operation="rollback", version_id="v123")
```

### Testing ACLs

```
tailscale_policies(operation="get_tests")
tailscale_policies(operation="run_tests")
```

Run ACL tests to verify policies work as expected before deploying.

### Policy Analysis

For deeper analysis of policy implications:

```
tailscale_policies(operation="list_nodes")
tailscale_policies(operation="list_edges")
```

## Auth Key Management

The tailscale_keys tool manages pre-authentication keys for device enrollment.

### Listing and Creating Keys

```
tailscale_keys(operation="list")
tailscale_keys(operation="create", reusable=True, ephemeral=False, tags=["ci-runner"], expiry_seconds=86400)
```

Create temporary keys for CI/CD pipelines with appropriate tags and expiry.

### API Keys

```
tailscale_keys(operation="list_api_keys")
tailscale_keys(operation="create_api_key", description="CI Pipeline Key", expiry_seconds=31536000)
```

API keys are used for programmatic access. They can be scoped and have expiration dates.

## Funnel Services

The tailscale_funnel tool manages Tailscale Funnel -- exposing services to the public internet through your tailnet.

### Managing Funnels

```
tailscale_funnel(operation="list")
tailscale_funnel(operation="enable", port=443, target="http://localhost:8080")
tailscale_funnel(operation="disable", port=443)
```

Funnel allows you to expose local services (like web apps, APIs) to the internet through Tailscale's infrastructure, without opening firewall ports.

## Monitoring & Health

The tailscale_monitor tool provides real-time network monitoring.

### Network Health

```
tailscale_monitor(operation="get_health")
tailscale_monitor(operation="get_health_report")
```

Returns health assessments for all devices, including connectivity issues, subnet route problems, and version drift.

### Performance Metrics

```
tailscale_monitor(operation="get_metrics")
tailscale_monitor(operation="get_bandwidth")
tailscale_monitor(operation="get_latency")
```

Monitor network performance including bandwidth usage between devices and latency measurements.

### Alert Configuration

```
tailscale_monitor(operation="set_threshold", metric="latency", warning=100, critical=300)
tailscale_monitor(operation="check_threshold")
```

Set thresholds for metric-based alerts and check current status against them.

## Security Auditing

The tailscale_security tool provides comprehensive security assessment.

### Security Reports

```
tailscale_security(operation="create_report")
tailscale_security(operation="get_security_report")
```

Generates a detailed security report including device posture, vulnerable versions, expired keys, and policy compliance.

### Posture Assessment

```
tailscale_security(operation="get_posture")
tailscale_security(operation="update_posture", device_id="12345", posture={...})
```

Tailscale posture includes device health attributes like OS version, disk encryption status, and installed software versions.

### Compliance Checks

```
tailscale_security(operation="check_compliance")
tailscale_security(operation="run_audit")
```

Run compliance checks against defined policies and generate audit trails.

## Reporting & Analytics

The tailscale_reporting tool provides data-driven insights.

### Generating Reports

```
tailscale_reporting(operation="get_summary")
tailscale_reporting(operation="get_user_report")
tailscale_reporting(operation="get_device_report")
tailscale_reporting(operation="get_usage_report")
```

Generate various reports covering usage patterns, device distribution, and user activity.

### Exporting Data

```
tailscale_reporting(operation="export_csv_report")
```

Export comprehensive data as CSV for external analysis in spreadsheets or BI tools.

## Service Management

The tailscale_services tool manages advertised services and ports.

### Listing and Advertising Services

```
tailscale_services(operation="list")
tailscale_services(operation="advertise", port=8080, protocol="tcp", description="Web App")
tailscale_services(operation="remove", service_id="svc_123")
```

Services are advertised to the tailnet, allowing other devices to discover and connect to them.

## Automation

The tailscale_automation tool manages scheduled tasks.

### Scheduled Tasks

```
tailscale_automation(operation="list_tasks")
tailscale_automation(operation="create_task", name="Weekly Security Report", cron="0 9 * * 1", action="security_report")
tailscale_automation(operation="run_task", task_id="task_123")
```

Create cron-like scheduled tasks for routine operations like security reports, health checks, and backups.

### Maintenance Windows

```
tailscale_automation(operation="enable_maintenance_window")
tailscale_automation(operation="set_maintenance_window", day="sunday", start="02:00", end="04:00", timezone="UTC")
```

Define maintenance windows for automated updates without disrupting critical operations.

## Log Management

### Searching Logs

```
log_search(query="authorize", level="info", tool_name="tailscale_devices")
log_search(query="error", limit=50)
```

Search through the server's operation logs with flexible filtering by tool, level, and text query.

### Exporting Logs

```
log_export(format="csv")
```

Export all log entries for external processing.

## Backup Management

The tailscale_backup tool manages tailnet configuration backups.

### Creating and Restoring Backups

```
tailscale_backup(operation="create", name="pre-upgrade-backup")
tailscale_backup(operation="list")
tailscale_backup(operation="restore", backup_id="backup_123")
```

Backups capture the full tailnet configuration including ACLs, DNS settings, and device tags.

## Integration Management

The tailscale_integration tool manages third-party integrations.

### Configuring Integrations

```
tailscale_integration(operation="list")
tailscale_integration(operation="configure", integration="slack", config={"webhook_url": "..."})
tailscale_integration(operation="test", integration="slack")
```

Integrations include Slack, PagerDuty, webhooks, GitHub, Datadog, and Sentry for alerting and event forwarding.

## Sample Workflows

### Onboarding a New Developer

1. Create an auth key: `tailscale_keys(operation="create", tags=["dev"], reusable=False, expiry_seconds=86400)`
2. After the developer connects, authorize: `tailscale_devices(operation="authorize", device_id="...")`
3. Tag the device: `tailscale_devices(operation="set_tags", device_id="...", tags=["dev", "laptop"])`
4. Verify connectivity: `tailscale_monitor(operation="get_health")`

### Weekly Security Audit

1. Generate report: `tailscale_security(operation="create_report")`
2. Check compliance: `tailscale_security(operation="check_compliance")`
3. Review expired keys: `tailscale_keys(operation="list")` and check expiry dates
4. Check for new devices: `tailscale_devices(operation="list")`
5. Export audit log: `log_export(format="csv")`

### ACL Policy Change with Safe Rollback

1. Create backup: `tailscale_backup(operation="create", name="before-acl-change")`
2. Get current ACL: `tailscale_policies(operation="get_acl")`
3. Validate new ACL: `tailscale_policies(operation="validate", acl=new_acl)`
4. If valid, set it: `tailscale_policies(operation="set_acl", acl=new_acl)`
5. Run tests: `tailscale_policies(operation="run_tests")`
6. If tests fail, rollback: `tailscale_backup(operation="restore", backup_id="before-acl-change")`

### Exposing a Web Service via Funnel

1. Ensure the service is running locally (e.g., on port 8080)
2. Enable funnel: `tailscale_funnel(operation="enable", port=443, target="http://localhost:8080")`
3. Verify: `tailscale_funnel(operation="list")`
4. Monitor access: `tailscale_monitor(operation="get_bandwidth")`

## ACL Policy Workflow Examples

### Creating a Basic ACL

A typical ACL grants access based on tags:

```
tailscale_policies(operation="get_acl")
```

This returns the current ACL JSON. Modify it to create a new policy:

```
tailscale_policies(operation="set_acl", acl={
    "acls": [
        {"action": "accept", "src": ["tag:dev"], "dst": ["tag:dev:*"]},
        {"action": "accept", "src": ["tag:prod"], "dst": ["tag:prod:*"]},
        {"action": "accept", "src": ["tag:infra"], "dst": ["*:*"]},
    ],
    "tagOwners": {
        "tag:dev": ["autogroup:members"],
        "tag:prod": ["autogroup:admin"],
    },
    "groups": {
        "group:engineering": ["user@example.com"],
    }
})
```

### Safe ACL Change with Rollback

Always use versioned ACL changes for safety:

```
# 1. Enable versioning
tailscale_policies(operation="create_hourly_snapshot")

# 2. Get version history
tailscale_policies(operation="list_versions")

# 3. Validate new ACL before applying
tailscale_policies(operation="validate", acl=new_acl)

# 4. Apply
tailscale_policies(operation="set_acl", acl=new_acl)

# 5. Run tests
tailscale_policies(operation="run_tests")

# 6. If issues, rollback
tailscale_policies(operation="rollback", version_id="last_good_version")
```

### Using the Policy Analyzer

For complex ACLs, analyze the access graph:

```
tailscale_policies(operation="list_nodes")
tailscale_policies(operation="list_edges")
```

This visualizes which tags can access which resources, helping identify unnecessarily permissive rules or missing access paths.

## Performance and Latency Monitoring

Check real-time performance between specific devices:

```
tailscale_performance(operation="get_latency_between", device_a="dev_1", device_b="dev_2")
tailscale_performance(operation="get_bandwidth_between", device_a="dev_1", device_b="dev_2")
```

This is useful for diagnosing slow connections, verifying VPN performance, and planning capacity.

## Integration Setup Examples

### Slack Alert Integration

```
tailscale_integration(operation="configure", integration="slack", config={
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#tailscale-alerts",
    "notify_on": ["device_join", "device_leave", "security_alert"]
})
tailscale_integration(operation="test", integration="slack")
```

### PagerDuty Incident Integration

```
tailscale_integration(operation="configure", integration="pagerduty", config={
    "routing_key": "...",
    "severity": "critical",
    "auto_resolve": True
})
```

### Generic Webhook

```
tailscale_integration(operation="configure", integration="webhook", config={
    "url": "https://my-server.example.com/tailscale-events",
    "secret": "shared-secret",
    "events": ["device.*", "policy.*", "key.*"]
})
```

## Automated Maintenance Workflows

### Weekly Security Audit Automation

```
tailscale_automation(operation="create_task",
    name="Weekly Security Audit",
    cron="0 9 * * 1",
    action="run_security_report"
)
tailscale_automation(operation="create_task",
    name="Daily Health Check",
    cron="0 */6 * * *",
    action="check_health"
)
```

### Device Cleanup Schedule

Automatically expire stale devices and check for orphaned auth keys as a recurring task.

## File Transfer with Taildrop

Taildrop enables direct peer-to-peer file transfers between Tailscale devices:

```
tailscale_file(operation="send", target_device="dev_1", path="report.pdf")
tailscale_file(operation="list_transfers")
tailscale_file(operation="get_status")
```

Transfers are encrypted end-to-end and use NAT traversal for direct connections when possible.

## Partner Tailnet Connections

Connect to another organization's tailnet for cross-company collaboration:

```
tailscale_partner_tailnets(operation="list")
tailscale_partner_tailnets(operation="create", partner_tailnet="partner.ts.net",
    capabilities=["devices:list", "routes:read"])
tailscale_partner_tailnets(operation="get_status")
```

Partner connections require mutual agreement and are scoped by defined capabilities.

## LM Links (Links Management)

LM Links provide named shortcuts for frequently accessed resources:

```
tailscale_lm_link(operation="create", name="internal-docs", target="http://wiki.internal")
tailscale_lm_link(operation="search", query="docs")
tailscale_lm_link(operation="share", link_id="link_123", expires_in_days=30)
```

## Advanced Log Analysis

```
log_search(query="error", level="error", tool_name="tailscale_devices", limit=100)
log_export(format="csv")
```

Export logs for external analysis. Filter by time range when available to narrow down specific incidents.

## Resource Access

Access the MCP resources directly for programmatic data retrieval:

- tailscale://devices -- Full device listing
- tailscale://devices/{id} -- Single device details
- tailscale://network/status -- Current network health
- tailscale://network/topology -- Network topology map
- tailscale://security/report -- Security report
- tailscale://monitoring/metrics -- Prometheus metrics
- tailscale://monitoring/health -- Health report

## Managing Devices with Tags

Tags are a fundamental concept in Tailscale ACLs. When a device joins your tailnet, it can be tagged automatically (if using an ephemeral key with tags) or manually after authorization. Tags determine which ACL rules apply to the device. Common patterns:

- `tag:dev` for developer workstations
- `tag:prod` for production servers
- `tag:ci` for CI/CD runners
- `tag:monitoring` for monitoring infrastructure
- `tag:infra` for shared infrastructure (DNS, logging)

Tags must be defined in the tagOwners section of the ACL to specify which users are authorized to apply them. A device can have multiple tags. Tags are prefixed with `tag:` and are case-sensitive.

## Subnet Router Management

Subnet routers extend your tailnet into private networks. To set up a subnet router:

1. On the device that will act as the router, configure Tailscale with --advertise-routes
2. The routes will appear as pending in the admin console
3. Approve them with `tailscale_devices(operation="approve_routes", device_id="12345", routes=["10.0.0.0/16"])`
4. Traffic will now route through the subnet router to the specified network

Multiple subnet routers can provide redundant paths to the same subnet. Tailscale automatically handles failover if one router goes offline. Each route is a CIDR range (e.g., 10.0.0.0/16, 192.168.1.0/24).

## DNS Configuration Examples

Simple DNS setup with public resolvers: point to Cloudflare and Google DNS, define an internal search domain, and enable MagicDNS for automatic device hostnames.

## Auth Key Lifecycle

Auth keys have configurable lifetimes: seconds-based expiry for temporary access, reusable vs single-use for different enrollment patterns, optional tag pre-definition for automatic policy assignment, and ephemeral mode for CI/CD. Ephemeral nodes are removed from the tailnet when they disconnect.

## Using Prompts and Resources

The MCP prompts generate ready-to-use queries:

```
list_devices_prompt(online_only=True)
```

Returns a user message that can be sent to the LLM. Resources provide direct data access:

- tailscale://devices -- Full device listing
- tailscale://network/status -- Current health status
- tailscale://security/report -- Security analysis

Use resources for programmatic data retrieval without tool overhead.

## Connecting to the Tailscale API

The Tailscale API v2 endpoint is https://api.tailscale.com/api/v2/tailnet/{tailnet}/. All requests require authentication via an API key passed as the Authorization header using Basic auth with the API key as the username and empty password. Rate limits are enforced per API key: 1000 requests per minute for most endpoints, with lower limits for write operations. The API client handles rate limiting automatically with retry and backoff. API responses include rate limit headers: X-Ratelimit-Limit, X-Ratelimit-Remaining, X-Ratelimit-Reset. WebSocket streaming endpoints have separate connection limits.

## Using the MagicDNS Resource

The MagicDNS resource at tailscale://network/status returns real-time network health data. This resource can be accessed programmatically by MCP clients for continuous monitoring. The data includes: total device count, online devices, offline devices, pending authorizations, active subnet routes, DNS configuration, and recent health events. Combine this resource data with the monitoring tools for comprehensive network observability.

## MCP Prompt Templates

The registered prompts provide ready-to-use natural language templates for common tasks. Each prompt generates a user message that can be sent to an LLM for context-aware responses. The prompts are designed for use with MCP clients that support prompt-driven workflows. Available prompts: list_devices_prompt (with optional online_only and filter_tags parameters), get_device_details_prompt (requires device_id), authorize_device_prompt (requires device_id, optional reason), check_network_status_prompt, create_security_report_prompt, and backup_configuration_prompt (optional backup_name).

## Cross-Tool Workflow Examples

Combining device management, monitoring, and reporting gives a complete view of tailnet health. Start with device listing, filter to online devices, check their performance metrics, and if any devices show degradation, generate a focused report. For ACL management, get the current ACL, validate proposed changes, apply them, immediately run tests, and if tests pass, create a backup. For incident response, check device status, review recent audit events, check security posture, and generate a timeline.

## Device Attribute Management

Device attributes provide flexible metadata beyond tags. Attributes are key-value pairs that can store: owner (username or email), location (datacenter, office, home), role (web-server, database, development), department (engineering, marketing, finance), purchased_date, warranty_expiry, and any other custom metadata. Unlike tags which affect ACL policy, attributes are informational and used for reporting and filtering. Set attributes with tailscale_devices(operation="set_attributes", device_id="...", attributes={"key": "value"}). Get attributes with the same operation's get variant. Attributes are returned in device listing and detail responses.

## Scheduled Task Configuration

Scheduled tasks use cron expressions for flexible scheduling. Examples: "0 9 * * 1" (9 AM every Monday), "0 */6 * * *" (every 6 hours), "0 2 * * *" (2 AM daily), "0 0 1 * *" (midnight on the 1st of each month). Tasks can run: device health checks, security report generation, configuration backups, integration health verification, expired key cleanup, and device authorization reviews. Task actions map to specific portmanteau tool operations. Tasks are persisted in DiskStore and survive server restarts.

## Advanced ACL Pattern Examples

Tag-based access control for common scenarios: development team access to all dev-tagged devices on any port with SSH bypass; production team access only to prod-tagged devices on specific ports with HTTPS and custom SSH; monitoring team read-only access to all devices with ICMP and metrics endpoints; infrastructure team access to all devices with full management via SSH. Each rule set includes explicit deny for cross-environment access and logging for audit. ACL test cases validate each rule with specific src/dst/port scenarios.

## Integration Health Monitoring

Each configured integration has a health status reported by tailscale_integration(operation="list") and individual test via tailscale_integration(operation="test", integration="name"). Health states: configured (ready but not yet tested), healthy (last test succeeded), degraded (last test timed out or returned errors), failed (last test returned fatal errors), and disabled (integration turned off). Integration health affects alert routing -- alerts are queued when the integration is degraded and retried until the integration recovers. Use the health monitoring to proactively detect integration failures before they impact alert delivery.

## Performance Baselines and Alarms

Establish performance baselines for your tailnet to detect anomalies. Use tailscale_monitor(operation="get_performance_report") to get an initial baseline. Common thresholds: latency under 20ms for direct connections, under 100ms for relayed connections, bandwidth above 50 Mbps for typical workloads, device uptime above 99%, version drift less than 2 minor versions. When thresholds are consistently breached, investigate network issues, device problems, or plan upgrades. Configure threshold alerts through the monitoring system to automatically notify on anomalies.

## Device Expiry and Cleanup Workflow

Devices can be set to expire after a configurable duration. Use case: temporary access for contractors, conference attendees, or CI runners. When a device expires: it is automatically removed from the tailnet, all routes and tags are revoked, the device must re-authenticate with a new auth key. Expired devices do not appear in device listing by default. Pending auth keys can also expire. Set device expiry with tailscale_devices(operation="expire_now", device_id="...") for immediate expiry, or use auth key expiry for scheduled expiration at enrollment time.

## Multi-Tailnet Configuration

The server manages one tailnet at a time. To manage multiple tailnets, you need separate MCP server instances with different API keys and tailnet configurations. Each instance maintains its own device list, ACL policies, monitoring state, and persistent storage. Use the save_settings tool to configure which tailnet each instance manages. The api_status tool shows the currently configured tailnet. There is no cross-tailnet management -- each instance is independent.

## Logging and Audit Trail Best Practices

For compliance requirements, maintain audit trails of all Tailscale configuration changes. Use log_export to export logs periodically and archive them. Configure integrations (Slack, PagerDuty, webhook) to forward critical events to your security information and event management (SIEM) system. The audit tool provides a structured change log with actor, action, timestamp, and before/after state. Export audit logs in CSV format for spreadsheet analysis or JSON for programmatic ingestion. Set up scheduled tasks to generate daily or weekly audit reports automatically.

## Performance Optimization Recommendations

For optimal Tailscale performance: use direct connections whenever possible (avoid relayed connections), verify direct connectivity with performance diagnostics, configure subnet routes for remote network access, enable MagicDNS for seamless name resolution, set up monitoring thresholds for early warning, and review ACL policies regularly to ensure they are not overly restrictive (causing connection failures) or overly permissive (security risk). Use the performance diagnostics tool to measure latency and bandwidth between specific device pairs.

## API Key Security Best Practices

Tailscale API keys grant programmatic access to your tailnet. Follow these security practices: use the minimum required scope for each key (read-only for monitoring, write for management), set expiry dates on all keys (90 days recommended), rotate keys regularly, never share keys across environments, use environment variables instead of hardcoded values, revoke compromised keys immediately, monitor key usage in audit logs, and use different keys for different automation systems. The test_credentials tool verifies a key is valid before using it for operations.

## Using Resources for Monitoring

The MCP resources expose live data for monitoring and integration. The tailscale://devices resource provides a real-time snapshot of all devices. The tailscale://monitoring/metrics resource provides Prometheus-formatted metrics that can be scraped by external monitoring systems. Combine resources with scheduled tasks for automated monitoring: schedule a task to check device count, compare to expected count, and alert if there is a discrepancy. Resources update on each access, providing fresh data without API call overhead.

## Multi-Service Integration Patterns

Common multi-service integration patterns: device change events to Slack for team awareness, security alerts to PagerDuty for on-call response, health metrics to Datadog for dashboard visualization, ACL changes to webhook for compliance archiving, and funnel metrics to Sentry for error tracking. Each integration is independently configurable and can be tested before enabling. The integration management tools support configuration, testing, enabling, and disabling of each service.

## Direct Resource Access Patterns

Resources provide rich data for programmatic access. Common patterns: poll the devices resource to track tailnet membership changes, subscribe to the health resource for real-time monitoring, read the security report resource for compliance checks, and fetch the topology resource for network visualization. Resources are updated on each access and return JSON-formatted data. Use resources instead of tool calls when you need the latest snapshot of a data category. Resources have lower overhead than tools for read-only access.

## Common API Error Responses

When API operations fail, the error response includes: error_code (machine-readable identifier), error_message (human-readable description), error_details (additional context), recovery_steps (list of actionable steps), and related_tools (suggested tools for resolution). Common error codes: UNAUTHORIZED (API key invalid or expired), NOT_FOUND (device, key, or resource not found), RATE_LIMITED (too many requests), VALIDATION_ERROR (input parameters invalid), and INTERNAL_ERROR (server-side failure). Recovery steps are specific to each error type and enable autonomous resolution.

## Prompt-Driven Workflows

The registered MCP prompts enable natural language interaction with the tailnet. Each prompt generates a context-rich query that can be sent to an LLM for interpretation. The list_devices_prompt with online_only=True generates "List all online devices in the tailnet" for agentic processing. The check_network_status_prompt generates "Show me the current network status and health" for automated monitoring. Prompts can be used directly by MCP clients or composed into larger agentic workflows. Combine multiple prompts for comprehensive network diagnostics.

## Collection Interval and Monitoring Granularity

Monitoring data freshness depends on the collection interval. The health check resource updates on each access, providing request-time fresh data. Performance metrics (latency, bandwidth) are collected at the time of the API call and represent current values. Device status (online/offline) reflects the most recent Tailscale API response. For continuous monitoring, poll resources at regular intervals. The monitoring threshold system compares current values against configured thresholds, generating alerts when values exceed warning or critical levels without storing historical data.

## Device History and Activity Tracking

Device activity can be tracked through the audit log and device attributes. The audit log records device_state changes, tag assignments, and route modifications. Device attributes can store last_seen timestamps, maintenance windows, and ownership history. Use the audit tool to query device-specific activity: tailscale_audit(operation="get_device_changes", device_id="..."). Track device uptime through the monitoring health report. For compliance, export device activity logs regularly and archive them alongside backups.

## Custom Integration Development

Beyond built-in integrations (Slack, PagerDuty, webhook, GitHub, Datadog, Sentry), custom integrations can receive Tailscale events via the generic webhook integration. The webhook integration sends JSON payloads for all event types to any HTTP endpoint. Configure the webhook URL and optional shared secret for payload verification. Custom receivers can process events for: internal dashboards, custom alerting systems, infrastructure as code pipelines, compliance automation, and ticketing system integration.

## Resource Utilization and Cost Management

Tailscale API usage counts toward your plan's request quota. Monitor API consumption with the api_status tool which reports rate limit status. For efficient API usage: cache device lists locally when possible, use resources instead of tools for repeated queries, batch operations where supported, and review audit logs to understand usage patterns. Export reports as CSV for offline analysis rather than repeated API calls. Schedule resource-intensive operations during off-peak hours.

## Navigation of the Tailscale Admin Console

While the MCP server provides programmatic control, some operations may require the Tailscale admin console for initial setup: generating the API key, configuring tailnet name, managing billing, and viewing certain account-level settings. Use the MCP tools for daily management and automation. Use the admin console for initial configuration and account administration. The health tool verifies that the API key has sufficient permissions for the operations you intend to perform.

## Tailscale Plan Features

Different Tailscale plans offer different feature sets. Personal plan: up to 3 users, 100 devices, basic ACLs. Premium plan: unlimited users, device approval workflow, ACL tags, subnet routing, and Tailscale Funnel. Enterprise plan: all features plus SAML/SSO, device posture checks, and custom logo. Some MCP tool operations require specific plan features: funnel management requires Premium or Enterprise, device posture checks require Enterprise, and certain integrations require Premium. Check your Tailscale plan in the admin console if a tool reports "feature not available."

## Backup and Disaster Recovery

Configuration backups are essential for disaster recovery. Create backups before making significant changes to ACL policies, DNS configuration, or device tags. Store backups in a secure location separate from the MCP server. The backup tool supports: manual one-time backups, scheduled automated backups, listing available backups with timestamps, restoring from a specific backup, and comparing backups to track changes. Restore operations apply the backed-up configuration through the Tailscale API, reverting ACLs, DNS, device tags, and other settings to their backed-up state.

## Funnel Security Considerations

Funnel services are exposed to the public internet through Tailscale's edge proxy. Security considerations: only expose services that are designed for public access, use HTTPS where possible, implement authentication in the exposed service, monitor funnel access logs for unusual traffic, disable funnels when not needed, and regularly audit which funnels are active. The funnel list tool shows all active funnels with their ports and targets. Review this list periodically and disable any services that no longer require public access.

## Tailscale SSH Setup

Tailscale SSH uses your existing tailnet identity for authentication instead of SSH keys. To enable: ensure Tailscale SSH is enabled in the admin console, configure SSH access rules in your ACL policy, and verify SSH access with an authorized device. SSH rules in ACL grant access based on source and destination tags. Tailscale SSH also supports session recording for audit compliance. The tailscale_security compliance check verifies SSH configuration.

## API Key Rotation Procedure

Rotate your Tailscale API key regularly for security. Create a new key in the admin console, update the environment variable or save_settings with the new key, verify with test_credentials, update any other systems using the old key, and then revoke the old key in the admin console. The server supports hot-reload of credentials via save_settings without restart. Maintain a key rotation schedule with at least quarterly rotation for production API keys. Use the audit log to track key rotation events.

## Performance Metrics Interpretation

Latency between devices is reported in milliseconds. Direct connections (peer-to-peer) should show under 20ms on the same local network and under 100ms across the internet. Relayed connections (through Tailscale DERP servers) may show 50-300ms depending on DERP server location. Bandwidth is reported in Mbps. Direct connections can reach 900+ Mbps on gigabit networks. Relayed connections are limited to approximately 50-100 Mbps. If latency or bandwidth is consistently poor, check for relayed connections and investigate direct connectivity issues.

## Troubleshooting

**API authentication fails:** Verify TAILSCALE_API_KEY is set and valid. Use test_credentials() to test. API keys expire -- generate a new one in the Tailscale admin console.

**Device not showing up:** Check that the device is connected to the internet and running Tailscale. Use `tailscale_devices(operation="get_pending")` to check for devices awaiting authorization.

**ACL validation errors:** The HuACL format requires correct JSON structure. Use `validate` before applying to catch syntax errors. Check for missing tags referenced in rules but not defined in the tags section.

**Funnel not working:** Verify the local target service is running. Funnel requires Tailscale Funnel to be enabled on the device. Some ports may be restricted by Tailscale plan.

**Rate limited:** The API client handles rate limiting automatically, but sustained high request rates may trigger 429 responses. Space out requests and use the status tools rather than rapid polling.

**Permissions insufficient:** API key permissions are set when the key is created. Some operations (authorize, delete device, set ACL) require owner or admin-level keys. Check your API key scope in the admin console.

**Backup restore fails:** The backup may be incompatible with the current ACL schema version. Check that the tailset has not changed significantly since the backup was created.

**Integration test fails:** Verify the external service credentials are valid. Check network connectivity between the tailnet and the external service endpoint.
