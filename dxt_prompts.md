# TailscaleMCP DXT Prompts

## Device Management

1. **Device Operations**
   - "List all devices in the tailnet"
   - "Show only online devices"
   - "Find device 'office-pc'"
   - "Authorize device d123456"
   - "Revoke device d789012"
   - "Rame device from 'old-name' to 'new-name'"
   - "Tag device as 'server'"
   - "Move device to 'servers' group"
   - "Show device d123456 details"
   - "Check routes for device d123456"

2. **Device Filtering**
   - "Show devices added in the last 7 days"
   - "List devices with tag 'production'"
   - "Find devices running Linux"
   - "Show devices with expired keys"
   - "List devices not seen in 30 days"
   - "Find devices with client version < 1.30.0"
   - "Show devices in subnet 192.168.1.0/24"
   - "List devices with exit node capability"
   - "Find devices with key expiry in 7 days"
   - "Show devices with active SSH sessions"

## Network Configuration

3. **ACL Management**
   - "Show current ACL rules"
   - "Allow HTTP traffic to web servers"
   - "Block port 22 from external"
   - "Create alias 'web-servers' for 100.64.0.0/24"
   - "Allow all traffic between 'dev' and 'staging'"
   - "Restrict SSH to jump host only"
   - "Allow RDP from office IP range"
   - "Block all inbound traffic to database"
   - "Allow ICMP between all nodes"
   - "Create auto-approval rule for MFA devices"

4. **DNS Configuration**
   - "Show DNS configuration"
   - "Add DNS record 'db.internal'"
   - "Remove DNS record 'old-service"
   - "Enable MagicDNS"
   - "Set DNS servers to 1.1.1.1, 8.8.8.8"
   - "Configure split DNS for .internal"
   - "Enable DNS over HTTPS"
   - "Add CNAME 'app' pointing to 'service-123'"
   - "Show DNS search domains"
   - "Flush DNS cache on all devices"

5. **Subnet Routing**
   - "Show subnet routes"
   - "Advertise 192.168.1.0/24"
   - "Stop advertising 10.0.0.0/8"
   - "Set up exit node on this device"
   - "Disable exit node functionality"
   - "Show route to 192.168.1.100"
   - "Enable subnet routes on device d123456"
   - "Disable subnet routes on all devices"
   - "Show BGP status"
   - "Configure BGP with AS 64512"

## Security & Authentication

6. **Authentication**
   - "Enable SSO with Google Workspace"
   - "Require 2FA for all users"
   - "Generate auth key with 7-day expiry"
   - "Revoke all active sessions"
   - "Show active sessions"
   - "Enforce device check-in every 24h"
   - "Enable device approval workflow"
   - "Require admin approval for new devices"
   - "Show login history"
   - "Enable audit logging"

7. **Key Management**
   - "List all auth keys"
   - "Create new reusable auth key"
   - "Revoke key ak-123456"
   - "Set key expiration to 30 days"
   - "Show key usage statistics"
   - "Rotate node keys"
   - "Generate pre-auth key"
   - "List expiring keys"
   - "Extend key ak-123456 by 7 days"
   - "Show key ak-123456 details"

## Monitoring & Debugging

8. **Network Status**
   - "Show network status"
   - "Ping all nodes"
   - "Traceroute to 100.64.1.1"
   - "Check Tailscale service status"
   - "Show network latency matrix"
   - "Test throughput between nodes"
   - "Show packet loss statistics"
   - "Check DERP server status"
   - "Show active peer connections"
   - "Monitor network traffic"

9. **Logs & Diagnostics**
   - "Show debug logs"
   - "Enable verbose logging"
   - "Export logs to file"
   - "Check for client updates"
   - "Run network diagnostics"
   - "Show system information"
   - "Check firewall rules"
   - "Test port forwarding"
   - "Show NAT traversal status"
   - "Check for IP conflicts"

## Automation & Integration

10. **API & Webhooks**
    - "Generate API token"
    - "List all webhooks"
    - "Create webhook for new devices"
    - "Delete webhook wh-123"
    - "Test webhook delivery"
    - "Show API usage statistics"
    - "Enable audit log streaming"
    - "Configure Slack notifications"
    - "Set up PagerDuty integration"
    - "Export configuration as code"

11. **Bulk Operations**
    - "Tag all Windows devices as 'windows'"
    - "Update all devices to latest version"
    - "Restart Tailscale on all devices"
    - "Rotate keys for all devices"
    - "Apply tag 'legacy' to devices older than 1 year"
    - "Generate device inventory report"
    - "Back up all configurations"
    - "Apply ACL changes to all devices"
    - "Schedule maintenance window"
    - "Send message to all users"

## Advanced Features

12. **Exit Nodes**
    - "List all exit nodes"
    - "Set exit node to 'us-east'"
    - "Disable exit node"
    - "Force traffic through exit node"
    - "Show exit node bandwidth usage"
    - "Set up high-availability exit nodes"
    - "Monitor exit node performance"
    - "Restrict exit node usage to specific users"
    - "Show exit node connection logs"
    - "Configure geo-fencing for exit nodes"

13. **Subnet Router**
    - "Enable subnet router on this device"
    - "Advertise local subnets"
    - "Show subnet router status"
    - "Disable subnet routing"
    - "Configure route advertisements"
    - "Monitor subnet traffic"
    - "Set up redundant subnet routers"
    - "Show subnet router metrics"
    - "Troubleshoot subnet routing"
    - "Optimize subnet routing performance"

14. **Access Control**
    - "Create admin user"
    - "Grant read-only access to <user@example.com>"
    - "Revoke user access"
    - "List all users and permissions"
    - "Set up just-in-time access"
    - "Enable device posture checks"
    - "Configure time-based access"
    - "Set up IP allowlisting"
    - "Enable device compliance checks"
    - "Configure role-based access control"

15. **Network Optimization**
    - "Optimize network performance"
    - "Enable wireguard optimizations"
    - "Disable peer-to-peer for low-bandwidth links"
    - "Configure traffic shaping"
    - "Show network topology"
    - "Optimize DERP regions"
    - "Enable packet filtering"
    - "Configure MTU settings"
    - "Show bandwidth usage by device"
    - "Monitor network health"

## Compliance & Reporting

16. **Audit & Compliance**
    - "Generate compliance report"
    - "Show audit logs"
    - "Export activity logs"
    - "Check for policy violations"
    - "Show user login history"
    - "Generate access review report"
    - "Check for inactive users"
    - "Show device compliance status"
    - "Export configuration backup"
    - "Run security audit"

17. **Backup & Restore**
    - "Backup current configuration"
    - "Restore from backup"
    - "Schedule automatic backups"
    - "Export network settings"
    - "Import configuration"
    - "Show backup history"
    - "Verify backup integrity"
    - "Encrypt backup with passphrase"
    - "Set up backup rotation"
    - "Test restore from backup"

## Integration & Extensibility

18. **CLI & Scripting**
    - "Show available CLI commands"
    - "Generate shell completion"
    - "Run in non-interactive mode"
    - "Set output format to JSON"
    - "Filter output with jq"
    - "Create bash alias for common commands"
    - "Show command history"
    - "Enable command autocompletion"
    - "Set default output format"
    - "Show CLI version"

19. **Third-Party Integration**
    - "Connect to Terraform"
    - "Set up Ansible integration"
    - "Configure Pulumi provider"
    - "Integrate with Slack"
    - "Connect to PagerDuty"
    - "Set up Datadog monitoring"
    - "Integrate with Splunk"
    - "Connect to Grafana"
    - "Set up Prometheus metrics"
    - "Configure ELK stack integration"

## Troubleshooting

20. **Common Issues**
    - "Troubleshoot connection issues"
    - "Check for IP conflicts"
    - "Reset network configuration"
    - "Restart Tailscale service"
    - "Check firewall settings"
    - "Verify DNS resolution"
    - "Test network connectivity"
    - "Check for client updates"
    - "Verify authentication"
    - "Reset Tailscale state"

21. **Advanced Troubleshooting**
    - "Enable debug logging"
    - "Capture network traffic"
    - "Generate support bundle"
    - "Check system requirements"
    - "Verify NAT traversal"
    - "Test DERP connectivity"
    - "Check for MTU issues"
    - "Verify routing tables"
    - "Test port forwarding"
    - "Check for network congestion"
