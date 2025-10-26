# RebootX On-Prem Setup Guide for Tailscale MCP

This guide provides step-by-step instructions for setting up RebootX On-Prem integration with the Tailscale MCP monitoring stack, including network configuration for external access.

## 🌐 Network Configuration

### Fixed IP Address Setup
- **Fixed External IP:** `213.47.34.131`
- **Local Network IP:** `192.168.0.81`
- **Router Gateway:** `192.168.0.1`

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Tailscale MCP monitoring stack running
- RebootX mobile app installed (iOS/Android)
- Router access for port forwarding configuration
- Administrator privileges for Windows Firewall configuration

### 2. Start RebootX On-Prem Integration

```powershell
# Navigate to the monitoring directory
cd monitoring/rebootx-on-prem

# Start RebootX On-Prem server
docker-compose -f docker-compose.rebootx.yml up -d

# Verify services are running
docker-compose -f docker-compose.rebootx.yml ps
```

### 3. Network Configuration

#### Router Port Forwarding
Configure your router to forward external port 9001 to your local machine:

1. **Access router admin panel:**
   - URL: `http://192.168.0.1`
   - Login with admin credentials

2. **Set up port forwarding:**
   - **Service Name:** RebootX On-Prem
   - **External Port:** 9001
   - **Internal Port:** 9001
   - **Internal IP:** 192.168.0.81
   - **Protocol:** TCP
   - **Enable:** Yes

#### Windows Firewall Configuration
Run PowerShell as Administrator and execute:

```powershell
netsh advfirewall firewall add rule name="RebootX On-Prem" dir=in action=allow protocol=TCP localport=9001
```

### 4. RebootX App Configuration

#### Connection Details
- **Server URL:** `http://213.47.34.131:9001`
- **API Key:** `tailscale-mcp-rebootx-key-2024`
- **Path Prefix:** `tailscale-mcp`

#### Setup Steps
1. Open RebootX mobile app
2. Tap "Add Server" or "+"
3. Enter connection details:
   - **Base URL:** `http://213.47.34.131:9001`
   - **API Key:** `tailscale-mcp-rebootx-key-2024`
   - **Path Prefix:** `tailscale-mcp`
4. Test connection

## 📊 Available Services

### Runnables (Infrastructure Components)
- **Tailscale MCP Server** (ID: tailscale-mcp-001)
- **Grafana Dashboard** (ID: grafana-001)
- **Prometheus Metrics** (ID: prometheus-001)
- **Loki Log Aggregation** (ID: loki-001)

### Dashboards (Monitoring Views)
- **Tailscale Network Overview**
- **Monitoring Infrastructure**
- **Security Metrics**
- **Performance Metrics**

## 🔧 Configuration Files

### Environment Variables
```bash
# RebootX On-Prem Configuration
REBOOTX_API_KEY=tailscale-mcp-rebootx-key-2024
REBOOTX_PATH_PREFIX=tailscale-mcp
REBOOTX_EXTERNAL_IP=213.47.34.131
```

### Docker Compose Configuration
The RebootX On-Prem service is integrated into the main monitoring stack:

```yaml
services:
  rebootx-on-prem:
    image: golang:1.22
    container_name: tailscale-rebootx-on-prem
    ports:
      - "9001:9001"
    environment:
      - RBTX_API_KEY=${REBOOTX_API_KEY:-tailscale-mcp-rebootx-key-2024}
      - RBTX_PATH_PREFIX=${REBOOTX_PATH_PREFIX:-tailscale-mcp}
      - RBTX_BIND=0.0.0.0
      - RBTX_PROTOCOL=http
    volumes:
      - ./monitoring/rebootx-on-prem/data:/data
      - ./monitoring/rebootx-on-prem/impl:/app
```

## 🔒 Security Considerations

### API Key Security
- Change the default API key for production use
- Use a strong, unique API key
- Consider rotating API keys periodically

### Network Security
- Monitor access logs
- Consider implementing rate limiting
- Use HTTPS for production deployments

### Firewall Configuration
- Only open necessary ports
- Monitor firewall logs
- Consider implementing IP whitelisting

## 🧪 Testing the Setup

### Local Network Test
```bash
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://192.168.0.81:9001/tailscale-mcp/runnables
```

### External Network Test
```bash
curl -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://213.47.34.131:9001/tailscale-mcp/runnables
```

### RebootX App Test
1. Open RebootX mobile app
2. Add server with configuration above
3. Verify connection shows green status
4. Test viewing runnables and dashboards

## 🔧 Troubleshooting

### Common Issues

#### Connection Refused
- **Check if server is running:** `docker-compose ps`
- **Verify port forwarding:** Test from external network
- **Check firewall:** Ensure port 9001 is allowed

#### Authentication Failed
- **Verify API key:** Check environment variables
- **Check Authorization header:** Ensure proper format
- **Test with curl:** Use test commands above

#### No Data Showing
- **Verify JSON configuration:** Check servers.json and dashboards.json
- **Check server logs:** `docker-compose logs rebootx-on-prem`
- **Ensure monitoring stack is running:** Check all services

### Debug Commands

```bash
# View server logs
docker-compose logs -f rebootx-on-prem

# Check service status
docker-compose ps

# Test API endpoints
curl -v -H "Authorization: tailscale-mcp-rebootx-key-2024" \
     http://213.47.34.131:9001/tailscale-mcp/runnables

# Check network connectivity
telnet 213.47.34.131 9001
```

## 📱 Mobile App Usage

### Features Available
- **View Infrastructure Status:** See all runnables and their status
- **Monitor Metrics:** View real-time metrics and dashboards
- **Control Services:** Start, stop, and reboot services
- **SSH Access:** Connect to servers directly
- **View Logs:** Access log information

### Best Practices
- Use secure network connections when possible
- Monitor usage and access patterns
- Keep the mobile app updated
- Report any issues or anomalies

## 🚀 Production Deployment

### HTTPS Configuration
For production deployments, configure HTTPS:

```yaml
environment:
  - RBTX_PROTOCOL=https
  - RBTX_TLS_CERT=/path/to/cert.pem
  - RBTX_TLS_KEY=/path/to/key.pem
```

### Monitoring and Logging
- Set up monitoring for the RebootX On-Prem server
- Configure log aggregation
- Monitor API usage and performance
- Set up alerts for service failures

### Backup and Recovery
- Backup configuration files
- Document network configuration
- Test disaster recovery procedures
- Maintain service documentation

## 📚 Additional Resources

- [RebootX On-Prem Documentation](rebootx-on-prem/README.md)
- [RebootX Mobile App](https://c100k.eu/p/rebootx)
- [Tailscale MCP Monitoring](README.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Test network connectivity and configuration
4. Consult the RebootX On-Prem documentation
5. Check the Tailscale MCP monitoring documentation

---

**Last Updated:** October 24, 2025
**Configuration:** Fixed IP 213.47.34.131, Local IP 192.168.0.81
**Port:** 9001 (HTTP), 9002 (Swagger UI)
