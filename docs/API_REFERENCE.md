# 📚 TailscaleMCP API Reference

**Complete API documentation for all TailscaleMCP portmanteau tools and operations**

---

## 🎯 **Overview**

The TailscaleMCP server provides **10 comprehensive portmanteau tools** with **91 total operations** covering all aspects of Tailscale network management.

### **Tool Categories**

| Tool | Operations | Domain | Description |
|------|------------|--------|-------------|
| `manage_tailnet_devices` | 19 | Device & User Management | Complete device and user lifecycle management |
| `manage_tailnet_network` | 8 | DNS & Network | MagicDNS, DNS records, and network policies |
| `monitor_tailnet` | 8 | Monitoring & Metrics | Network monitoring and Grafana dashboards |
| `manage_taildrop` | 7 | File Sharing | Taildrop file sharing operations |
| `run_tailnet_security` | 10 | Security & Compliance | Security scanning and compliance validation |
| `run_tailnet_automation` | 9 | Workflow Automation | Workflow creation and script execution |
| `manage_tailnet_backups` | 8 | Backup & Recovery | Configuration backup and disaster recovery |
| `analyze_tailnet_performance` | 8 | Performance Monitoring | Network performance analysis and optimization |
| `generate_tailnet_reports` | 9 | Advanced Reporting | Custom reports and analytics |
| `manage_tailnet_integrations` | 9 | Third-Party Integrations | Webhooks and platform integrations |

---

## 🔧 **Device Management (`manage_tailnet_devices`)**

**Purpose**: Comprehensive device and user management operations.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `list` | List devices with filtering | `online_only`, `filter_tags` | List of devices |
| `get` | Get device details | `device_id` | Device information |
| `authorize` | Authorize/deauthorize device | `device_id`, `authorize`, `reason` | Authorization status |
| `rename` | Rename device | `device_id`, `name` | Rename result |
| `tag` | Manage device tags | `device_id`, `tags` | Tag operation result |
| `ssh` | Configure SSH access | `device_id`, `public_key`, `key_name` | SSH configuration |
| `search` | Search devices | `search_query`, `search_fields` | Search results |
| `stats` | Get device statistics | `device_id` | Device statistics |
| `exit_node` | Configure exit node | `device_id`, `enable_exit_node`, `advertise_routes` | Exit node status |
| `subnet_router` | Configure subnet routing | `device_id`, `enable_subnet_router`, `subnets` | Subnet router status |
| `user_list` | List users | None | List of users |
| `user_create` | Create user | `user_email`, `user_role` | User creation result |
| `user_update` | Update user | `user_email`, `user_role` | User update result |
| `user_delete` | Delete user | `user_email` | User deletion result |
| `user_details` | Get user details | `user_email` | User information |
| `auth_key_list` | List auth keys | None | List of auth keys |
| `auth_key_create` | Create auth key | `auth_key_name`, `auth_key_expiry`, `auth_key_reusable` | Auth key creation result |
| `auth_key_revoke` | Revoke auth key | `auth_key_name` | Revocation result |
| `auth_key_rotate` | Rotate expired keys | None | Key rotation result |

### **Parameters**

#### **Device Operations**
- `device_id` (str): Unique device identifier
- `name` (str): New device name
- `authorize` (bool): Authorization status
- `reason` (str): Authorization reason
- `tags` (list[str]): Device tags
- `public_key` (str): SSH public key
- `key_name` (str): SSH key name
- `search_query` (str): Search query string
- `search_fields` (list[str]): Fields to search in
- `online_only` (bool): Filter for online devices only
- `filter_tags` (list[str]): Filter by device tags
- `enable_exit_node` (bool): Enable exit node functionality
- `advertise_routes` (list[str]): Routes to advertise
- `enable_subnet_router` (bool): Enable subnet routing
- `subnets` (list[str]): Subnets to route

#### **User Management**
- `user_email` (str): User email address
- `user_role` (str): User role (admin, user, viewer)
- `user_permissions` (list[str]): User permissions

#### **Authentication Keys**
- `auth_key_name` (str): Authentication key name
- `auth_key_expiry` (str): Key expiration date
- `auth_key_reusable` (bool): Whether key is reusable
- `auth_key_ephemeral` (bool): Whether key is ephemeral
- `auth_key_preauthorized` (bool): Whether key is preauthorized
- `auth_key_tags` (list[str]): Key tags

### **Example Usage**

```python
# List all devices
result = await manage_tailnet_devices(operation="list", online_only=True)

# Get device details
device = await manage_tailnet_devices(operation="get", device_id="device123")

# Authorize a device
await manage_tailnet_devices(
    operation="authorize",
    device_id="device123",
    authorize=True,
    reason="New employee onboarding"
)

# Add tags to device
await manage_tailnet_devices(
    operation="tag",
    device_id="device123",
    tags=["engineering", "laptop", "production"]
)

# Enable SSH access
await manage_tailnet_devices(
    operation="ssh",
    device_id="device123",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ...",
    key_name="john-key"
)

# Search devices
results = await manage_tailnet_devices(
    operation="search",
    search_query="engineering",
    search_fields=["name", "tags", "user"]
)

# Enable exit node
await manage_tailnet_devices(
    operation="exit_node",
    device_id="device123",
    enable_exit_node=True,
    advertise_routes=["0.0.0.0/0", "::/0"]
)

# Create user
await manage_tailnet_devices(
    operation="user_create",
    user_email="john@company.com",
    user_role="admin"
)

# Create auth key
await manage_tailnet_devices(
    operation="auth_key_create",
    auth_key_name="deploy-key",
    auth_key_expiry="2025-12-31",
    auth_key_reusable=False,
    auth_key_ephemeral=True
)
```

---

## 🌐 **Network Management (`manage_tailnet_network`)**

**Purpose**: DNS configuration, MagicDNS, and network policy management.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `dns_config` | Get DNS configuration | None | DNS configuration |
| `magic_dns` | Configure MagicDNS | `enabled`, `override_local_dns` | MagicDNS status |
| `dns_record` | Manage DNS records | `name`, `record_type`, `value` | DNS record result |
| `resolve` | Resolve hostname | `hostname`, `record_type` | Resolution result |
| `search_domain` | Manage search domains | `domain`, `enabled` | Search domain result |
| `policy` | Manage network policies | `policy_name`, `rules` | Policy result |
| `stats` | Get DNS statistics | None | DNS statistics |
| `cache` | Manage DNS cache | None | Cache operation result |

### **Parameters**

- `enabled` (bool): Enable/disable MagicDNS
- `override_local_dns` (bool): Override local DNS settings
- `name` (str): DNS record name
- `record_type` (str): DNS record type (A, AAAA, CNAME, etc.)
- `value` (str): DNS record value
- `hostname` (str): Hostname to resolve
- `domain` (str): Search domain
- `policy_name` (str): Network policy name
- `rules` (list[dict]): Network policy rules

### **Example Usage**

```python
# Get DNS configuration
config = await manage_tailnet_network(operation="dns_config")

# Configure MagicDNS
await manage_tailnet_network(
    operation="magic_dns",
    enabled=True,
    override_local_dns=False
)

# Add DNS record
await manage_tailnet_network(
    operation="dns_record",
    name="api.internal",
    record_type="A",
    value="100.64.0.1"
)

# Resolve hostname
result = await manage_tailnet_network(
    operation="resolve",
    hostname="api.internal",
    record_type="A"
)

# Add search domain
await manage_tailnet_network(
    operation="search_domain",
    domain="internal",
    enabled=True
)

# Create network policy
await manage_tailnet_network(
    operation="policy",
    policy_name="restrict-api",
    rules=[
        {
            "action": "accept",
            "src": ["engineering"],
            "dst": ["api:*"]
        }
    ]
)

# Get DNS statistics
stats = await manage_tailnet_network(operation="stats")

# Clear DNS cache
await manage_tailnet_network(operation="cache")
```

---

## 📊 **Monitoring (`monitor_tailnet`)**

**Purpose**: Network monitoring, metrics collection, and Grafana dashboard management.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `status` | Get network status | None | Network status |
| `metrics` | Get network metrics | None | Network metrics |
| `prometheus` | Get Prometheus metrics | None | Prometheus metrics |
| `topology` | Generate network topology | None | Network topology |
| `health` | Get health report | None | Health report |
| `dashboard` | Create Grafana dashboard | `grafana_url`, `api_key` | Dashboard creation result |
| `export` | Export dashboard | `filename`, `dashboard_type` | Export result |

### **Parameters**

- `grafana_url` (str): Grafana instance URL
- `api_key` (str): Grafana API key
- `filename` (str): Export filename
- `dashboard_type` (str): Dashboard type (comprehensive, topology, security)

### **Example Usage**

```python
# Get network status
status = await monitor_tailnet(operation="status")

# Get network metrics
metrics = await monitor_tailnet(operation="metrics")

# Get Prometheus metrics
prometheus_metrics = await monitor_tailnet(operation="prometheus")

# Generate network topology
topology = await monitor_tailnet(topology="topology")

# Get health report
health = await monitor_tailnet(operation="health")

# Create Grafana dashboard
await monitor_tailnet(
    operation="dashboard",
    grafana_url="http://grafana:3000",
    api_key="your-grafana-api-key"
)

# Export dashboard
await monitor_tailnet(
    operation="export",
    filename="tailscale-dashboard.json",
    dashboard_type="comprehensive"
)
```

---

## 📁 **File Sharing (`manage_taildrop`)**

**Purpose**: Taildrop file sharing operations and transfer management.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `send` | Send file via Taildrop | `file_path`, `recipient_device`, `sender_device` | Send result |
| `receive` | Receive file | `transfer_id`, `save_path` | Receive result |
| `list` | List transfers | `status_filter` | Transfer list |
| `cancel` | Cancel transfer | `transfer_id` | Cancellation result |
| `status` | Get transfer status | `transfer_id` | Transfer status |
| `stats` | Get Taildrop statistics | None | Taildrop statistics |
| `cleanup` | Clean up expired transfers | None | Cleanup result |

### **Parameters**

- `file_path` (str): Path to file to send
- `recipient_device` (str): Recipient device ID
- `sender_device` (str): Sender device ID
- `transfer_id` (str): Transfer identifier
- `save_path` (str): Path to save received file
- `status_filter` (str): Filter transfers by status (active, completed, failed)

### **Example Usage**

```python
# Send file via Taildrop
await manage_taildrop(
    operation="send",
    file_path="/path/to/file.txt",
    recipient_device="device123",
    sender_device="device456"
)

# Receive file
await manage_taildrop(
    operation="receive",
    transfer_id="transfer123",
    save_path="/downloads/"
)

# List active transfers
transfers = await manage_taildrop(
    operation="list",
    status_filter="active"
)

# Cancel transfer
await manage_taildrop(
    operation="cancel",
    transfer_id="transfer123"
)

# Get transfer status
status = await manage_taildrop(
    operation="status",
    transfer_id="transfer123"
)

# Get Taildrop statistics
stats = await manage_taildrop(operation="stats")

# Clean up expired transfers
await manage_taildrop(operation="cleanup")
```

---

## 🔒 **Security (`run_tailnet_security`)**

**Purpose**: Security scanning, compliance validation, and threat management.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `scan` | Security vulnerability scan | `scan_type` | Scan results |
| `compliance` | Compliance validation | `compliance_standard` | Compliance report |
| `audit` | Device security audit | `device_id` | Audit report |
| `report` | Generate security report | None | Security report |
| `monitor` | Monitor suspicious activity | None | Monitoring status |
| `block` | Block malicious IP | `ip_address`, `block_duration` | Block result |
| `quarantine` | Quarantine device | `device_id`, `quarantine_duration` | Quarantine result |
| `alert` | Security alerting | `alert_type`, `recipients` | Alert result |
| `policy` | Security policy management | `policy_name`, `rules` | Policy result |
| `threat` | Threat detection | `threat_type`, `test_mode` | Threat detection result |

### **Parameters**

- `scan_type` (str): Scan type (comprehensive, quick, custom)
- `compliance_standard` (str): Compliance standard (SOC2, PCI-DSS, HIPAA, ISO27001)
- `device_id` (str): Device identifier
- `ip_address` (str): IP address to block
- `block_duration` (int): Block duration in seconds
- `quarantine_duration` (int): Quarantine duration in hours
- `alert_type` (str): Alert type (email, webhook, slack)
- `recipients` (list[str]): Alert recipients
- `policy_name` (str): Security policy name
- `rules` (list[dict]): Security policy rules
- `threat_type` (str): Threat type (malware, intrusion, data_exfiltration)
- `test_mode` (bool): Run in test mode

### **Example Usage**

```python
# Security vulnerability scan
scan_results = await run_tailnet_security(
    operation="scan",
    scan_type="comprehensive"
)

# Compliance validation
compliance_report = await run_tailnet_security(
    operation="compliance",
    compliance_standard="SOC2"
)

# Device security audit
audit_report = await run_tailnet_security(
    operation="audit",
    device_id="device123"
)

# Generate security report
security_report = await run_tailnet_security(operation="report")

# Monitor suspicious activity
monitoring_status = await run_tailnet_security(operation="monitor")

# Block malicious IP
await run_tailnet_security(
    operation="block",
    ip_address="192.168.1.100",
    block_duration=3600
)

# Quarantine compromised device
await run_tailnet_security(
    operation="quarantine",
    device_id="device123",
    quarantine_duration=24
)

# Create security policy
await run_tailnet_security(
    operation="policy",
    policy_name="restrict-api",
    rules=[
        {
            "action": "accept",
            "src": ["engineering"],
            "dst": ["api:*"]
        }
    ]
)

# Threat detection
threat_results = await run_tailnet_security(
    operation="threat",
    threat_type="malware",
    test_mode=False
)
```

---

## 🤖 **Automation (`run_tailnet_automation`)**

**Purpose**: Workflow creation, script execution, and batch operations.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `workflow_create` | Create automation workflow | `workflow_name`, `workflow_steps` | Workflow creation result |
| `workflow_execute` | Execute workflow | `workflow_id`, `execute_now` | Execution result |
| `workflow_schedule` | Schedule workflow | `workflow_id`, `schedule_cron` | Scheduling result |
| `workflow_list` | List workflows | None | Workflow list |
| `workflow_delete` | Delete workflow | `workflow_id` | Deletion result |
| `script_execute` | Execute custom script | `script_content`, `script_language` | Script execution result |
| `script_template` | Get script template | `template_name` | Script template |
| `batch` | Batch operations | `batch_operations` | Batch execution result |
| `dry_run` | Preview operations | `batch_operations` | Preview result |

### **Parameters**

- `workflow_name` (str): Workflow name
- `workflow_steps` (list[dict]): Workflow steps
- `workflow_id` (str): Workflow identifier
- `execute_now` (bool): Execute immediately
- `schedule_cron` (str): Cron schedule expression
- `script_content` (str): Script content
- `script_language` (str): Script language (python, bash, powershell)
- `template_name` (str): Script template name
- `batch_operations` (list[dict]): Batch operations to execute

### **Example Usage**

```python
# Create automation workflow
await run_tailnet_automation(
    operation="workflow_create",
    workflow_name="daily-backup",
    workflow_steps=[
        {"action": "backup", "target": "all"},
        {"action": "verify", "target": "backup"},
        {"action": "cleanup", "target": "old_backups"}
    ]
)

# Execute workflow
await run_tailnet_automation(
    operation="workflow_execute",
    workflow_id="workflow123",
    execute_now=True
)

# Schedule workflow
await run_tailnet_automation(
    operation="workflow_schedule",
    workflow_id="workflow123",
    schedule_cron="0 2 * * *"
)

# List workflows
workflows = await run_tailnet_automation(operation="workflow_list")

# Execute custom script
await run_tailnet_automation(
    operation="script_execute",
    script_content="print('Hello Tailscale')",
    script_language="python"
)

# Get script template
template = await run_tailnet_automation(
    operation="script_template",
    template_name="device-audit"
)

# Batch operations
await run_tailnet_automation(
    operation="batch",
    batch_operations=[
        {"operation": "authorize", "device_id": "device123"},
        {"operation": "tag", "device_id": "device123", "tags": ["engineering"]}
    ]
)

# Preview operations
preview = await run_tailnet_automation(
    operation="dry_run",
    batch_operations=[
        {"operation": "authorize", "device_id": "device123"}
    ]
)
```

---

## 💾 **Backup (`manage_tailnet_backups`)**

**Purpose**: Configuration backup, restoration, and disaster recovery planning.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `backup_create` | Create configuration backup | `backup_name`, `backup_type` | Backup creation result |
| `backup_restore` | Restore from backup | `backup_id` | Restoration result |
| `backup_schedule` | Schedule automated backups | `schedule_cron`, `retention_days` | Scheduling result |
| `backup_list` | List backups | None | Backup list |
| `backup_delete` | Delete backup | `backup_id` | Deletion result |
| `backup_test` | Test backup integrity | `backup_id` | Test result |
| `restore_test` | Test restore procedure | `backup_id` | Test result |
| `recovery_plan` | Create disaster recovery plan | None | Recovery plan |

### **Parameters**

- `backup_name` (str): Backup name
- `backup_type` (str): Backup type (full, incremental, differential)
- `backup_id` (str): Backup identifier
- `schedule_cron` (str): Cron schedule expression
- `retention_days` (int): Backup retention period in days

### **Example Usage**

```python
# Create configuration backup
await manage_tailnet_backups(
    operation="backup_create",
    backup_name="daily-backup",
    backup_type="full"
)

# Restore from backup
await manage_tailnet_backups(
    operation="backup_restore",
    backup_id="backup123"
)

# Schedule automated backups
await manage_tailnet_backups(
    operation="backup_schedule",
    schedule_cron="0 2 * * *",
    retention_days=30
)

# List backups
backups = await manage_tailnet_backups(operation="backup_list")

# Delete backup
await manage_tailnet_backups(
    operation="backup_delete",
    backup_id="backup123"
)

# Test backup integrity
test_result = await manage_tailnet_backups(
    operation="backup_test",
    backup_id="backup123"
)

# Test restore procedure
restore_test = await manage_tailnet_backups(
    operation="restore_test",
    backup_id="backup123"
)

# Create disaster recovery plan
recovery_plan = await manage_tailnet_backups(operation="recovery_plan")
```

---

## 📈 **Performance (`analyze_tailnet_performance`)**

**Purpose**: Network performance monitoring, optimization, and capacity planning.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `latency` | Measure network latency | `device_id`, `measure_duration` | Latency measurements |
| `bandwidth` | Analyze bandwidth utilization | `device_id`, `measure_duration` | Bandwidth analysis |
| `optimize` | Optimize routing performance | `route_optimization` | Optimization result |
| `baseline` | Establish performance baseline | `baseline_name`, `baseline_duration` | Baseline result |
| `capacity` | Predict capacity requirements | `capacity_period`, `scaling_factor` | Capacity analysis |
| `utilization` | Analyze resource utilization | `device_id` | Utilization report |
| `scaling` | Get scaling recommendations | `scaling_factor` | Scaling recommendations |
| `threshold` | Set performance threshold | `performance_threshold` | Threshold result |

### **Parameters**

- `device_id` (str): Device identifier
- `measure_duration` (int): Measurement duration in seconds
- `route_optimization` (bool): Enable route optimization
- `baseline_name` (str): Baseline name
- `baseline_duration` (int): Baseline duration in seconds
- `capacity_period` (str): Capacity analysis period
- `scaling_factor` (float): Scaling factor
- `performance_threshold` (float): Performance threshold (0.0-1.0)

### **Example Usage**

```python
# Measure network latency
latency_results = await analyze_tailnet_performance(
    operation="latency",
    device_id="device123",
    measure_duration=60
)

# Analyze bandwidth utilization
bandwidth_analysis = await analyze_tailnet_performance(
    operation="bandwidth",
    device_id="device123",
    measure_duration=300
)

# Optimize routing performance
optimization_result = await analyze_tailnet_performance(
    operation="optimize",
    route_optimization=True
)

# Establish performance baseline
baseline_result = await analyze_tailnet_performance(
    operation="baseline",
    baseline_name="production",
    baseline_duration=300
)

# Predict capacity requirements
capacity_analysis = await analyze_tailnet_performance(
    operation="capacity",
    capacity_period="30d",
    scaling_factor=1.2
)

# Analyze resource utilization
utilization_report = await analyze_tailnet_performance(
    operation="utilization",
    device_id="device123"
)

# Get scaling recommendations
scaling_recommendations = await analyze_tailnet_performance(
    operation="scaling",
    scaling_factor=1.5
)

# Set performance threshold
await analyze_tailnet_performance(
    operation="threshold",
    performance_threshold=0.8
)
```

---

## 📊 **Reporting (`generate_tailnet_reports`)**

**Purpose**: Custom report generation, analytics, and automated reporting.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `generate` | Generate custom report | `report_type`, `date_range` | Report generation result |
| `usage` | Generate usage analytics | `date_range`, `include_charts` | Usage analytics report |
| `custom` | Create custom report | `custom_fields`, `date_range` | Custom report |
| `schedule` | Schedule automated reports | `schedule_cron`, `email_recipients` | Scheduling result |
| `export` | Export reports | `export_path`, `report_format` | Export result |
| `analytics` | Deep network analytics | `analytics_depth`, `date_range` | Analytics report |
| `behavior` | User behavior analysis | `date_range` | Behavior analysis report |
| `security` | Security metrics | `date_range`, `security_focus` | Security metrics report |
| `template` | Get report template | `template_name` | Report template |

### **Parameters**

- `report_type` (str): Report type (summary, detailed, executive)
- `date_range` (str): Date range (7d, 30d, 90d, 1y)
- `include_charts` (bool): Include charts in report
- `custom_fields` (list[str]): Custom fields to include
- `schedule_cron` (str): Cron schedule expression
- `email_recipients` (list[str]): Email recipients
- `export_path` (str): Export file path
- `report_format` (str): Export format (pdf, csv, json, html)
- `analytics_depth` (str): Analytics depth (basic, detailed, comprehensive)
- `security_focus` (bool): Focus on security metrics
- `template_name` (str): Report template name

### **Example Usage**

```python
# Generate usage analytics report
usage_report = await generate_tailnet_reports(
    operation="usage",
    date_range="30d",
    include_charts=True
)

# Create custom report
custom_report = await generate_tailnet_reports(
    operation="custom",
    custom_fields=["device_count", "bandwidth_usage", "security_events"],
    date_range="7d"
)

# Schedule automated reports
await generate_tailnet_reports(
    operation="schedule",
    schedule_cron="0 9 * * 1",
    email_recipients=["admin@company.com", "security@company.com"]
)

# Export reports
await generate_tailnet_reports(
    operation="export",
    export_path="/reports/",
    report_format="pdf"
)

# Deep network analytics
analytics_report = await generate_tailnet_reports(
    operation="analytics",
    analytics_depth="comprehensive",
    date_range="90d"
)

# User behavior analysis
behavior_report = await generate_tailnet_reports(
    operation="behavior",
    date_range="30d"
)

# Security metrics
security_report = await generate_tailnet_reports(
    operation="security",
    date_range="30d",
    security_focus=True
)

# Get report template
template = await generate_tailnet_reports(
    operation="template",
    template_name="executive-summary"
)
```

---

## 🔗 **Integration (`manage_tailnet_integrations`)**

**Purpose**: Webhook management and third-party platform integrations.

### **Operations**

| Operation | Description | Parameters | Returns |
|-----------|-------------|------------|---------|
| `webhook_create` | Create webhook endpoint | `webhook_url`, `webhook_events` | Webhook creation result |
| `webhook_test` | Test webhook delivery | `webhook_id` | Test result |
| `webhook_list` | List webhooks | None | Webhook list |
| `webhook_delete` | Delete webhook | `webhook_id` | Deletion result |
| `slack` | Integrate with Slack | `slack_channel`, `api_key` | Integration result |
| `discord` | Integrate with Discord | `discord_webhook` | Integration result |
| `pagerduty` | Integrate with PagerDuty | `pagerduty_key` | Integration result |
| `datadog` | Integrate with Datadog | `datadog_api_key`, `api_endpoint` | Integration result |
| `test` | Test integration connection | `integration_type`, `api_key`, `test_connection` | Test result |

### **Parameters**

- `webhook_url` (str): Webhook endpoint URL
- `webhook_events` (list[str]): Events to send to webhook
- `webhook_id` (str): Webhook identifier
- `slack_channel` (str): Slack channel name
- `api_key` (str): API key for integration
- `discord_webhook` (str): Discord webhook URL
- `pagerduty_key` (str): PagerDuty integration key
- `datadog_api_key` (str): Datadog API key
- `api_endpoint` (str): API endpoint URL
- `integration_type` (str): Integration type (slack, discord, pagerduty, datadog)
- `test_connection` (bool): Test connection during setup

### **Example Usage**

```python
# Create webhook endpoint
await manage_tailnet_integrations(
    operation="webhook_create",
    webhook_url="https://api.company.com/webhook",
    webhook_events=["device_connected", "device_disconnected", "security_alert"]
)

# Test webhook delivery
test_result = await manage_tailnet_integrations(
    operation="webhook_test",
    webhook_id="webhook123"
)

# List webhooks
webhooks = await manage_tailnet_integrations(operation="webhook_list")

# Delete webhook
await manage_tailnet_integrations(
    operation="webhook_delete",
    webhook_id="webhook123"
)

# Integrate with Slack
await manage_tailnet_integrations(
    operation="slack",
    slack_channel="#tailscale-alerts",
    api_key="slack-api-key"
)

# Integrate with Discord
await manage_tailnet_integrations(
    operation="discord",
    discord_webhook="https://discord.com/api/webhooks/..."
)

# Integrate with PagerDuty
await manage_tailnet_integrations(
    operation="pagerduty",
    pagerduty_key="pagerduty-integration-key"
)

# Integrate with Datadog
await manage_tailnet_integrations(
    operation="datadog",
    datadog_api_key="datadog-api-key",
    api_endpoint="https://api.datadoghq.com"
)

# Test integration connection
test_result = await manage_tailnet_integrations(
    operation="test",
    integration_type="slack",
    api_key="slack-api-key",
    test_connection=True
)
```

---

## 📋 **Response Format**

### **Standard Response Structure**

All operations return a consistent response format:

```python
{
    "status": "success" | "error",
    "operation": "operation_name",
    "data": {
        # Operation-specific data
    },
    "timestamp": 1234567890.123,
    "message": "Optional status message"
}
```

### **Success Response Example**

```python
{
    "status": "success",
    "operation": "list",
    "data": {
        "devices": [
            {
                "id": "device123",
                "name": "john-laptop",
                "status": "online",
                "ip": "100.64.0.1",
                "tags": ["engineering", "laptop"]
            }
        ],
        "total_count": 1
    },
    "timestamp": 1234567890.123,
    "message": "Successfully listed 1 device"
}
```

### **Error Response Example**

```python
{
    "status": "error",
    "operation": "get",
    "data": null,
    "timestamp": 1234567890.123,
    "message": "Device not found: device123"
}
```

---

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TAILSCALE_API_KEY` | Tailscale API key | Yes | None |
| `TAILSCALE_TAILNET` | Tailnet name | Yes | None |
| `LOG_LEVEL` | Logging level | No | INFO |
| `TIMEOUT` | Request timeout | No | 30 |
| `CACHE_TTL` | Cache TTL in seconds | No | 300 |

### **Configuration Example**

```bash
export TAILSCALE_API_KEY="tskey-api-xxxxxxxxxxxxxxxxx"
export TAILSCALE_TAILNET="your-org.tailnet.ts.net"
export LOG_LEVEL="INFO"
export TIMEOUT="30"
export CACHE_TTL="300"
```

---

## 🚀 **Getting Started**

### **Basic Usage**

```python
import asyncio
from tailscalemcp import TailscaleMCPServer

async def main():
    # Initialize the server
    server = TailscaleMCPServer(
        api_key="your_tailscale_api_key",
        tailnet="your_tailnet"
    )
    
    # Start the server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### **Using Portmanteau Tools**

```python
# Get the portmanteau tools instance
tools = server.portmanteau_tools

# Use device management
devices = await tools.manage_tailnet_devices(operation="list", online_only=True)

# Use network management
await tools.manage_tailnet_network(operation="magic_dns", enabled=True)

# Use monitoring
status = await tools.monitor_tailnet(operation="status")
```

---

*API Reference Documentation*  
*Version: 2.1.0*  
*Last Updated: April 2026*  
*Total Operations: 91*  
*Portmanteau Tools: 10*  
*Status: Production Ready* 🚀
