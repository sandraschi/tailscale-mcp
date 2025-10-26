# RebootX On-Prem Quick Reference

## 🌐 Network Configuration

### IP Addresses
- **Fixed External IP:** `213.47.34.131`
- **Local Network IP:** `192.168.0.81`
- **Router Gateway:** `192.168.0.1`

### Ports
- **RebootX On-Prem API:** 9001
- **Swagger UI:** 9002

## 📱 RebootX App Configuration

### Connection Details
```
Server URL: http://213.47.34.131:9001
API Key: tailscale-mcp-rebootx-key-2024
Path Prefix: tailscale-mcp
```

### Quick Setup Steps
1. Open RebootX mobile app
2. Tap "Add Server" or "+"
3. Enter the connection details above
4. Test connection

## 🔧 Quick Commands

### Start RebootX On-Prem
```powershell
.\scripts\start-rebootx-on-prem.ps1
```

### Test Connection (Local)
```bash
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://192.168.0.81:9001/tailscale-mcp/runnables
```

### Test Connection (External)
```bash
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://213.47.34.131:9001/tailscale-mcp/runnables
```

### View Logs
```bash
docker-compose logs -f rebootx-on-prem
```

### Check Service Status
```bash
docker-compose ps
```

## 🔒 Security Configuration

### Windows Firewall (Run as Administrator)
```powershell
netsh advfirewall firewall add rule name="RebootX On-Prem" dir=in action=allow protocol=TCP localport=9001
```

### Router Port Forwarding
- **External Port:** 9001
- **Internal Port:** 9001
- **Internal IP:** 192.168.0.81
- **Protocol:** TCP

## 📊 Available Services

### Runnables
- Tailscale MCP Server (tailscale-mcp-001)
- Grafana Dashboard (grafana-001)
- Prometheus Metrics (prometheus-001)
- Loki Log Aggregation (loki-001)

### Dashboards
- Tailscale Network Overview
- Monitoring Infrastructure
- Security Metrics
- Performance Metrics

## 🚨 Troubleshooting

### Connection Issues
1. Check if server is running: `docker-compose ps`
2. Verify port forwarding on router
3. Check Windows Firewall settings
4. Test with curl commands above

### No Data Showing
1. Check server logs: `docker-compose logs rebootx-on-prem`
2. Verify JSON configuration files
3. Ensure monitoring stack is running
4. Check API key configuration

---

**Last Updated:** October 24, 2025
**Fixed IP:** 213.47.34.131
**Local IP:** 192.168.0.81
