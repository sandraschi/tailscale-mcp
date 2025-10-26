# Deployment Guide and Best Practices

This document provides comprehensive deployment guidance and best practices for the Tailscale MCP monitoring stack.

## 🚀 Deployment Overview

The monitoring stack can be deployed in various environments, from local development to production clusters. This guide covers different deployment scenarios and best practices.

## 🏠 Local Development Deployment

### Prerequisites

- Docker and Docker Compose
- 2GB RAM minimum
- 10GB disk space
- Ports 3000, 9090, 3100, 8080, 9091 available

### Quick Start

1. **Clone and setup:**
   ```powershell
   git clone <repository>
   cd tailscale-mcp
   Copy-Item env.example .env
   ```

2. **Configure environment:**
   Edit `.env` file with your Tailscale credentials:
   ```
   TAILSCALE_API_KEY=your_api_key_here
   TAILSCALE_TAILNET=your_tailnet_name_here
   ```

3. **Start monitoring stack:**
   ```powershell
   .\scripts\start-monitoring.ps1
   ```

4. **Access services:**
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Loki: http://localhost:3100
   - MCP Server: http://localhost:8080

### Development Workflow

1. **Make changes** to monitoring configuration
2. **Restart services** with `docker-compose restart <service>`
3. **Test changes** in Grafana dashboards
4. **Commit changes** to version control

## 🏢 Production Deployment

### Prerequisites

- Docker Swarm or Kubernetes cluster
- Load balancer for external access
- Persistent storage for data
- SSL certificates for HTTPS
- Backup and monitoring systems

### Docker Swarm Deployment

#### Initialize Swarm
```bash
docker swarm init
```

#### Deploy Stack
```bash
docker stack deploy -c docker-compose.prod.yml tailscale-monitoring
```

#### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  tailscale-mcp:
    image: tailscale-mcp:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    networks:
      - monitoring
    secrets:
      - tailscale_api_key
    configs:
      - promtail_config

  grafana:
    image: grafana/grafana:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    networks:
      - monitoring
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_admin_password

  prometheus:
    image: prom/prometheus:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    networks:
      - monitoring
    volumes:
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  loki:
    image: grafana/loki:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    networks:
      - monitoring
    volumes:
      - loki_data:/loki
    command: -config.file=/etc/loki/loki.yml

networks:
  monitoring:
    driver: overlay
    attachable: true

volumes:
  grafana_data:
  prometheus_data:
  loki_data:

secrets:
  tailscale_api_key:
    external: true
  grafana_admin_password:
    external: true

configs:
  promtail_config:
    external: true
```

### Kubernetes Deployment

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tailscale-monitoring
```

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-config
  namespace: tailscale-monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'tailscale-mcp'
        static_configs:
          - targets: ['tailscale-mcp:9091']
  loki.yml: |
    auth_enabled: false
    server:
      http_listen_port: 3100
    storage:
      filesystem:
        directory: /loki/data
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tailscale-mcp
  namespace: tailscale-monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tailscale-mcp
  template:
    metadata:
      labels:
        app: tailscale-mcp
    spec:
      containers:
      - name: tailscale-mcp
        image: tailscale-mcp:latest
        ports:
        - containerPort: 8080
        - containerPort: 9091
        env:
        - name: TAILSCALE_API_KEY
          valueFrom:
            secretKeyRef:
              name: tailscale-secrets
              key: api-key
        - name: TAILSCALE_TAILNET
          valueFrom:
            configMapKeyRef:
              name: monitoring-config
              key: tailnet
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: tailscale-mcp
  namespace: tailscale-monitoring
spec:
  selector:
    app: tailscale-mcp
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  - name: metrics
    port: 9091
    targetPort: 9091
  type: ClusterIP
```

## 🔧 Configuration Management

### Environment Variables

#### Required Variables
```bash
# Tailscale Configuration
TAILSCALE_API_KEY=your_api_key_here
TAILSCALE_TAILNET=your_tailnet_name_here

# Application Configuration
LOG_LEVEL=INFO
PROMETHEUS_PORT=9091
LOG_FILE=logs/tailscale-mcp.log

# Grafana Configuration
GF_SECURITY_ADMIN_PASSWORD=admin
GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel

# Prometheus Configuration
PROMETHEUS_RETENTION=200h
PROMETHEUS_SCRAPE_INTERVAL=15s

# Loki Configuration
LOKI_RETENTION_PERIOD=200h
LOKI_STORAGE_PATH=/loki/data
```

#### Optional Variables
```bash
# Advanced Configuration
PROMETHEUS_EVALUATION_INTERVAL=15s
LOKI_QUERY_TIMEOUT=60s
GRAFANA_SERVER_PORT=3000
PROMETHEUS_SERVER_PORT=9090
LOKI_SERVER_PORT=3100
```

### Configuration Files

#### Docker Compose Override
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  tailscale-mcp:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
    ports:
      - "8080:8080"
      - "9091:9091"

  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"

  prometheus:
    ports:
      - "9090:9090"

  loki:
    ports:
      - "3100:3100"
```

## 📊 Monitoring and Alerting

### Health Checks

#### Application Health
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### Service Health
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9091/metrics"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Alerting Rules

#### Service Down Alerts
```yaml
- alert: ServiceDown
  expr: up{job="tailscale-mcp"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Service is down"
    description: "Tailscale MCP service has been down for more than 1 minute"
```

#### Resource Usage Alerts
```yaml
- alert: HighMemoryUsage
  expr: container_memory_usage_bytes{name="tailscale-mcp"} / container_spec_memory_limit_bytes{name="tailscale-mcp"} > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage"
    description: "Memory usage is above 80% for more than 5 minutes"
```

## 🔒 Security Considerations

### Network Security

#### Firewall Rules
```bash
# Allow only necessary ports
ufw allow 3000/tcp  # Grafana
ufw allow 9090/tcp  # Prometheus
ufw allow 3100/tcp  # Loki
ufw allow 8080/tcp  # MCP Server
ufw allow 9091/tcp  # Metrics
```

#### SSL/TLS Configuration
```yaml
# nginx.conf
server {
    listen 443 ssl;
    server_name monitoring.example.com;
    
    ssl_certificate /etc/ssl/certs/monitoring.crt;
    ssl_certificate_key /etc/ssl/private/monitoring.key;
    
    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Authentication

#### Grafana Authentication
```yaml
# grafana.ini
[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml
```

#### API Key Management
```bash
# Generate secure API key
openssl rand -base64 32

# Store in secrets management
kubectl create secret generic tailscale-secrets \
  --from-literal=api-key=your_secure_api_key_here
```

## 📈 Performance Optimization

### Resource Allocation

#### Memory Requirements
```yaml
# Minimum requirements
grafana: 512MB
prometheus: 1GB
loki: 512MB
tailscale-mcp: 256MB
promtail: 128MB

# Recommended requirements
grafana: 1GB
prometheus: 2GB
loki: 1GB
tailscale-mcp: 512MB
promtail: 256MB
```

#### CPU Requirements
```yaml
# Minimum requirements
grafana: 0.5 CPU
prometheus: 1 CPU
loki: 0.5 CPU
tailscale-mcp: 0.25 CPU
promtail: 0.25 CPU

# Recommended requirements
grafana: 1 CPU
prometheus: 2 CPU
loki: 1 CPU
tailscale-mcp: 0.5 CPU
promtail: 0.5 CPU
```

### Storage Optimization

#### Data Retention
```yaml
# Prometheus retention
PROMETHEUS_RETENTION=30d

# Loki retention
LOKI_RETENTION_PERIOD=7d

# Log rotation
LOG_ROTATION_SIZE=100MB
LOG_ROTATION_COUNT=10
```

#### Compression
```yaml
# Enable compression
PROMETHEUS_COMPRESSION=true
LOKI_COMPRESSION=true
```

## 🔄 Backup and Recovery

### Backup Strategy

#### Data Backup
```bash
# Backup Prometheus data
docker exec prometheus tar -czf /backup/prometheus-$(date +%Y%m%d).tar.gz /prometheus

# Backup Loki data
docker exec loki tar -czf /backup/loki-$(date +%Y%m%d).tar.gz /loki

# Backup Grafana data
docker exec grafana tar -czf /backup/grafana-$(date +%Y%m%d).tar.gz /var/lib/grafana
```

#### Configuration Backup
```bash
# Backup configuration files
tar -czf /backup/config-$(date +%Y%m%d).tar.gz monitoring/
```

### Recovery Procedures

#### Data Recovery
```bash
# Restore Prometheus data
docker exec prometheus tar -xzf /backup/prometheus-20240101.tar.gz -C /

# Restore Loki data
docker exec loki tar -xzf /backup/loki-20240101.tar.gz -C /

# Restore Grafana data
docker exec grafana tar -xzf /backup/grafana-20240101.tar.gz -C /
```

#### Service Recovery
```bash
# Restart services
docker-compose restart

# Check service status
docker-compose ps

# Check logs
docker-compose logs -f
```

## 🚀 Deployment Checklist

### Pre-deployment

- [ ] Verify system requirements
- [ ] Configure environment variables
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up backup procedures
- [ ] Configure monitoring and alerting

### Deployment

- [ ] Deploy services
- [ ] Verify service health
- [ ] Test dashboard functionality
- [ ] Verify log collection
- [ ] Test alerting rules
- [ ] Configure access controls

### Post-deployment

- [ ] Monitor system performance
- [ ] Review logs for errors
- [ ] Test backup procedures
- [ ] Document configuration
- [ ] Train users on dashboards
- [ ] Set up maintenance procedures

## 🔧 Troubleshooting

### Common Issues

#### Service Startup Issues
- Check Docker daemon status
- Verify port availability
- Check environment variables
- Review service logs

#### Performance Issues
- Monitor resource usage
- Check query performance
- Review log volume
- Optimize configuration

#### Connectivity Issues
- Check network configuration
- Verify firewall rules
- Test service endpoints
- Review DNS resolution

### Debugging Steps

1. **Check service status**: `docker-compose ps`
2. **Review service logs**: `docker-compose logs <service>`
3. **Check resource usage**: `docker stats`
4. **Test endpoints**: `curl http://localhost:port/health`
5. **Verify configuration**: Review config files

---

This deployment guide provides comprehensive guidance for deploying the Tailscale MCP monitoring stack in various environments, from local development to production clusters.
