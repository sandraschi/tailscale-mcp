# Monitoring Stack Architecture

This document describes the architecture and design of the Tailscale MCP monitoring stack.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tailscale MCP Monitoring Stack              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │    Grafana      │    │   Prometheus    │    │    Loki     │ │
│  │   (Port 3000)   │◄───┤   (Port 9090)   │    │ (Port 3100) │ │
│  │                 │    │                 │    │             │ │
│  │ • Dashboards    │    │ • Metrics       │    │ • Logs      │ │
│  │ • Alerts        │    │ • Rules         │    │ • Querying  │ │
│  │ • Visualization │    │ • Storage       │    │ • Analysis  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│         ▲                       ▲                       ▲       │
│         │                       │                       │       │
│         └───────────────────────┼───────────────────────┘       │
│                                 │                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Promtail      │    │ Tailscale MCP   │    │   Docker    │ │
│  │                 │    │   Server        │    │  Containers │ │
│  │ • Log Shipping  │    │ (Port 8080/9091)│    │             │ │
│  │ • Log Parsing   │    │                 │    │ • Services  │ │
│  │ • Labeling      │    │ • Application   │    │ • Networks  │ │
│  │                 │    │ • Metrics       │    │ • Volumes   │ │
│  │                 │    │ • Logs          │    │             │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│         ▲                       ▲                       ▲       │
│         │                       │                       │       │
│         └───────────────────────┼───────────────────────┘       │
│                                 │                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Docker Network                             │ │
│  │                  (monitoring)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Details

### Grafana (Visualization Layer)

**Purpose**: Provides dashboards, visualization, and alerting for the monitoring stack.

**Configuration**:
- **Port**: 3000
- **Authentication**: Admin user (admin/admin)
- **Data Sources**: Prometheus and Loki
- **Dashboards**: 4 comprehensive dashboards
- **Plugins**: Pie chart, worldmap panels

**Key Features**:
- Real-time dashboard updates
- Interactive visualizations
- Alert rule configuration
- Dashboard provisioning
- User management

### Prometheus (Metrics Layer)

**Purpose**: Collects, stores, and queries time-series metrics from the Tailscale MCP server.

**Configuration**:
- **Port**: 9090
- **Scrape Interval**: 15 seconds
- **Evaluation Interval**: 15 seconds
- **Retention**: 200 hours
- **Storage**: Local filesystem

**Metrics Collection**:
- Application metrics from MCP server
- System metrics from containers
- Custom business metrics
- Health check metrics

### Loki (Log Aggregation Layer)

**Purpose**: Aggregates, stores, and queries log data from all components.

**Configuration**:
- **Port**: 3100
- **Storage**: Filesystem-based
- **Schema**: v11
- **Retention**: Configurable
- **Query Engine**: LogQL

**Log Sources**:
- Tailscale MCP server logs
- Docker container logs
- System logs
- Application logs

### Promtail (Log Shipping Layer)

**Purpose**: Collects logs from various sources and ships them to Loki.

**Configuration**:
- **Log Sources**: Files, Docker containers, system logs
- **Parsing**: JSON, regex, timestamp extraction
- **Labeling**: Automatic label assignment
- **Shipping**: HTTP push to Loki

**Pipeline Stages**:
- Log discovery
- Log parsing
- Label extraction
- Log shipping

### Tailscale MCP Server (Application Layer)

**Purpose**: The main application that provides Tailscale management functionality.

**Configuration**:
- **Port**: 8080 (MCP server), 9091 (metrics)
- **Logging**: Structured JSON logging
- **Metrics**: Prometheus metrics exposure
- **Health**: Health check endpoints

**Monitoring Integration**:
- Prometheus metrics endpoint
- Structured logging output
- Health check endpoints
- Performance metrics

## 📊 Data Flow

### Metrics Flow

1. **Collection**: Tailscale MCP server exposes metrics on port 9091
2. **Scraping**: Prometheus scrapes metrics every 15 seconds
3. **Storage**: Metrics stored in Prometheus time-series database
4. **Querying**: Grafana queries Prometheus for dashboard data
5. **Visualization**: Dashboards display real-time metrics

### Log Flow

1. **Generation**: Tailscale MCP server generates structured JSON logs
2. **Collection**: Promtail collects logs from files and containers
3. **Parsing**: Promtail parses logs and extracts labels
4. **Shipping**: Logs shipped to Loki via HTTP
5. **Storage**: Loki stores logs with indexing
6. **Querying**: Grafana queries Loki with LogQL
7. **Display**: Log streams displayed in dashboards

## 🔄 Service Dependencies

### Startup Order

1. **Loki** - Log storage (no dependencies)
2. **Prometheus** - Metrics storage (no dependencies)
3. **Promtail** - Log shipping (depends on Loki)
4. **Tailscale MCP Server** - Application (depends on Prometheus)
5. **Grafana** - Visualization (depends on Prometheus and Loki)

### Health Checks

- **Loki**: HTTP health check on port 3100
- **Prometheus**: HTTP health check on port 9090
- **Promtail**: Process health check
- **Tailscale MCP**: HTTP health check on port 9091
- **Grafana**: HTTP health check on port 3000

## 🛠️ Configuration Management

### Environment Variables

```bash
# Tailscale Configuration
TAILSCALE_API_KEY=your_api_key_here
TAILSCALE_TAILNET=your_tailnet_name_here

# Application Configuration
LOG_LEVEL=INFO
PROMETHEUS_PORT=9091

# Grafana Configuration
GF_SECURITY_ADMIN_PASSWORD=admin
```

### Docker Compose Configuration

- **Services**: All components defined as services
- **Networks**: Custom Docker network for isolation
- **Volumes**: Persistent storage for data
- **Environment**: Environment variable injection
- **Health Checks**: Service health monitoring

### Configuration Files

- **Prometheus**: `monitoring/prometheus/prometheus.yml`
- **Loki**: `monitoring/loki/loki.yml`
- **Promtail**: `monitoring/promtail/promtail.yml`
- **Grafana**: Provisioned via configuration files

## 📈 Scaling Considerations

### Horizontal Scaling

- **Multiple Prometheus instances** for high availability
- **Loki clustering** for log storage scaling
- **Load balancing** for Grafana instances
- **Distributed log collection** with multiple Promtail instances

### Vertical Scaling

- **Memory allocation** for each component
- **CPU allocation** for processing
- **Storage allocation** for data retention
- **Network bandwidth** for data transfer

## 🔒 Security Architecture

### Network Security

- **Docker network isolation** between services
- **Internal communication** only
- **External access** through specific ports
- **Firewall rules** for port access

### Authentication

- **Grafana authentication** with admin user
- **API key protection** in environment variables
- **Service-to-service** authentication
- **Access logging** for audit trails

### Data Protection

- **Log sanitization** for sensitive data
- **Metrics filtering** for privacy
- **Encryption** for data at rest
- **Backup encryption** for data protection

## 🔄 Monitoring and Alerting

### Health Monitoring

- **Service health checks** for all components
- **Resource usage monitoring** (CPU, memory, disk)
- **Network connectivity monitoring**
- **Performance monitoring** for each service

### Alerting Rules

- **Service down alerts** for critical services
- **Resource usage alerts** for capacity planning
- **Error rate alerts** for application issues
- **Performance degradation alerts** for optimization

### Notification Channels

- **Email notifications** for critical alerts
- **Slack integration** for team notifications
- **Webhook notifications** for custom integrations
- **PagerDuty integration** for on-call management

## 🚀 Deployment Architecture

### Development Environment

- **Local Docker Compose** for development
- **Hot reloading** for configuration changes
- **Debug logging** for troubleshooting
- **Test data** for dashboard development

### Production Environment

- **Container orchestration** with Docker Swarm or Kubernetes
- **High availability** with multiple instances
- **Load balancing** for service distribution
- **Monitoring** of the monitoring stack itself

### Staging Environment

- **Production-like setup** for testing
- **Performance testing** with realistic data
- **Integration testing** with external services
- **User acceptance testing** for dashboards

## 📊 Performance Metrics

### Key Performance Indicators

- **Service uptime** for all components
- **Response times** for dashboards and queries
- **Log processing latency** for real-time monitoring
- **Storage utilization** for capacity planning

### Optimization Strategies

- **Query optimization** for faster dashboard loading
- **Log retention policies** for storage management
- **Metrics aggregation** for reduced storage
- **Caching strategies** for improved performance

---

This architecture provides a robust, scalable, and maintainable monitoring solution for the Tailscale MCP server with comprehensive observability capabilities.
