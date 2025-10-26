# RebootX Integration - Mobile Infrastructure Monitoring

## Overview

RebootX is an iPad application that provides mobile access to infrastructure monitoring tools like Grafana, enabling you to monitor your systems conveniently from your iPad. This document covers the integration of RebootX with your monitoring stack for "monitoring your infra in your pocket."

## 🚀 **What is RebootX?**

RebootX is a mobile application designed to provide convenient access to infrastructure monitoring tools, particularly Grafana dashboards, directly from your iPad. It's perfect for homebrew monitoring enthusiasts who want affordable, mobile access to their infrastructure monitoring.

### **Key Features**

- **📱 Mobile Grafana Access**: View Grafana dashboards on your iPad
- **🏠 Home Infrastructure Monitoring**: Perfect for home lab and personal infrastructure monitoring
- **💰 Cost-Effective**: Pro version at $6 per month (or one-time payment as of March 2025)
- **🔧 On-Premises Support**: Self-hosted option available for complete control
- **📊 Dashboard Integration**: Seamless integration with existing Grafana dashboards

## 💰 **Pricing Options**

### **Pro Version**
- **Price**: $6 per calendar month
- **Alternative**: One-time payment option (as of March 2025)
- **Features**: Advanced monitoring capabilities and full dashboard access

### **On-Premises Option**
- **Cost**: Free (self-hosted)
- **GitHub Repository**: [RebootX On-Prem](https://github.com/c100k/rebootx-on-prem)
- **Perfect for**: Homebrew monitoring enthusiasts and cost-conscious users

## 🔧 **Integration Options**

### **Option 1: Direct Grafana Integration (Recommended)**

Connect RebootX directly to your existing Grafana instance:

```yaml
# Configuration for direct Grafana access
grafana:
  url: "http://your-grafana-instance:3000"
  username: "admin"
  password: "your-password"
  dashboards:
    - "home-security-overview"
    - "camera-performance-health"
    - "energy-management"
    - "alarm-system"
    - "ai-analytics"
```

### **Option 2: RebootX On-Prem Integration**

Set up the self-hosted RebootX On-Prem server for complete control:

```bash
# Clone the RebootX On-Prem repository
git clone https://github.com/c100k/rebootx-on-prem.git
cd rebootx-on-prem

# Build and run the server
go build -o rebootx-on-prem
./rebootx-on-prem --config config.yaml
```

## 📱 **Setup Instructions**

### **1. Install RebootX App**

1. **Download from App Store**: Search for "RebootX" on your iPad
2. **Install the app**: Download and install on your iPad
3. **Launch the app**: Open RebootX and complete the initial setup

### **2. Configure Grafana Access**

#### **Method A: Direct Connection**

1. **Open RebootX app** on your iPad
2. **Add Grafana Instance**:
   - Tap "Add Server" or "Connect"
   - Enter your Grafana URL: `http://your-ip:3000`
   - Enter credentials (username/password)
   - Test connection

3. **Configure Dashboards**:
   - Select which dashboards to display
   - Set refresh intervals
   - Configure notifications

#### **Method B: RebootX On-Prem Setup**

1. **Set up RebootX On-Prem server**:
   ```bash
   # Create configuration file
   cat > config.yaml << EOF
   server:
     port: 8080
     host: "0.0.0.0"
   
   grafana:
     url: "http://localhost:3000"
     username: "admin"
     password: "admin"
   
   dashboards:
     - name: "Home Security Overview"
       id: "home-security-overview"
       refresh: "10s"
     - name: "Camera Performance"
       id: "camera-performance-health"
       refresh: "30s"
     - name: "Energy Management"
       id: "energy-management"
       refresh: "1m"
     - name: "Alarm System"
       id: "alarm-system"
       refresh: "10s"
     - name: "AI Analytics"
       id: "ai-analytics"
       refresh: "30s"
   EOF
   
   # Run the server
   ./rebootx-on-prem --config config.yaml
   ```

2. **Connect RebootX app** to your on-prem server:
   - Add server: `http://your-server-ip:8080`
   - Configure authentication if needed

### **3. Configure Your Monitoring Stack**

Update your Docker Compose configuration to expose Grafana for mobile access:

```yaml
# docker-compose.yml - Add to your existing configuration
services:
  grafana:
    image: grafana/grafana:latest
    container_name: tapo-grafana
    ports:
      - "3000:3000"  # Ensure this is accessible from your network
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel,grafana-heatmap-panel
      - GF_SECURITY_ALLOW_EMBEDDING=true
      - GF_AUTH_ANONYMOUS_ENABLED=false
      # Enable mobile access
      - GF_SERVER_DOMAIN=your-domain.com  # Optional: for external access
      - GF_SERVER_ROOT_URL=http://your-ip:3000
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - home-security
    restart: unless-stopped
```

## 📊 **Dashboard Configuration for Mobile**

### **Mobile-Optimized Dashboard Settings**

Configure your Grafana dashboards for optimal mobile viewing:

```json
{
  "dashboard": {
    "title": "🏠 Home Security Overview - Mobile",
    "tags": ["home-security", "mobile", "rebootx"],
    "style": "dark",
    "timezone": "Europe/Vienna",
    "refresh": "10s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "🔒 Security Status",
        "type": "stat",
        "gridPos": {
          "h": 6,
          "w": 12,
          "x": 0,
          "y": 0
        },
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "center",
          "orientation": "horizontal"
        }
      }
    ]
  }
}
```

### **Mobile-Friendly Panel Configurations**

1. **Larger Text and Icons**: Use larger fonts and clear icons
2. **Touch-Friendly Controls**: Ensure buttons and controls are touch-friendly
3. **Responsive Layout**: Use appropriate grid sizes for mobile viewing
4. **Quick Refresh**: Set shorter refresh intervals for real-time monitoring

## 🔧 **Advanced Configuration**

### **RebootX On-Prem Custom Configuration**

Create a custom configuration for your specific monitoring needs:

```yaml
# rebootx-config.yaml
server:
  port: 8080
  host: "0.0.0.0"
  tls:
    enabled: false
    cert: ""
    key: ""

authentication:
  enabled: true
  username: "admin"
  password: "your-secure-password"

grafana:
  url: "http://localhost:3000"
  username: "admin"
  password: "admin"
  timeout: 30s

dashboards:
  - name: "Home Security Overview"
    id: "home-security-overview"
    refresh: "10s"
    mobile_optimized: true
  - name: "Camera Performance"
    id: "camera-performance-health"
    refresh: "30s"
    mobile_optimized: true
  - name: "Energy Management"
    id: "energy-management"
    refresh: "1m"
    mobile_optimized: true
  - name: "Alarm System"
    id: "alarm-system"
    refresh: "10s"
    mobile_optimized: true
  - name: "AI Analytics"
    id: "ai-analytics"
    refresh: "30s"
    mobile_optimized: true

notifications:
  enabled: true
  channels:
    - type: "push"
      enabled: true
    - type: "email"
      enabled: false
      smtp:
        host: ""
        port: 587
        username: ""
        password: ""

logging:
  level: "info"
  file: "rebootx-on-prem.log"
```

### **Docker Integration**

Create a Docker container for RebootX On-Prem:

```dockerfile
# Dockerfile for RebootX On-Prem
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o rebootx-on-prem .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/rebootx-on-prem .
COPY --from=builder /app/config.yaml .
EXPOSE 8080
CMD ["./rebootx-on-prem"]
```

```yaml
# docker-compose.yml addition
services:
  rebootx-on-prem:
    build: ./rebootx-on-prem
    container_name: rebootx-on-prem
    ports:
      - "8080:8080"
    volumes:
      - ./rebootx-config.yaml:/root/config.yaml
    networks:
      - home-security
    restart: unless-stopped
    depends_on:
      - grafana
```

## 📱 **Mobile Usage Tips**

### **Optimizing for iPad**

1. **Landscape Mode**: Configure dashboards for landscape viewing
2. **Touch Gestures**: Use pinch-to-zoom and swipe gestures
3. **Quick Access**: Set up shortcuts for frequently accessed dashboards
4. **Offline Mode**: Configure caching for offline viewing

### **Dashboard Navigation**

1. **Swipe Navigation**: Swipe between different dashboards
2. **Quick Refresh**: Pull down to refresh dashboards
3. **Full Screen**: Tap to enter full-screen mode
4. **Notifications**: Enable push notifications for alerts

## 🔒 **Security Considerations**

### **Network Security**

1. **VPN Access**: Use VPN for secure remote access
2. **Authentication**: Enable strong authentication
3. **HTTPS**: Use HTTPS for secure connections
4. **Firewall**: Configure firewall rules appropriately

### **Access Control**

```yaml
# Security configuration
security:
  vpn_required: true
  allowed_ips:
    - "192.168.1.0/24"  # Local network only
    - "10.0.0.0/8"      # VPN network
  authentication:
    required: true
    timeout: 3600  # 1 hour
  rate_limiting:
    enabled: true
    requests_per_minute: 60
```

## 🚀 **Use Cases**

### **Home Infrastructure Monitoring**

1. **🏠 Home Security**: Monitor cameras, alarms, and sensors
2. **🔋 Energy Management**: Track power consumption and smart plugs
3. **📊 System Health**: Monitor server performance and uptime
4. **🚨 Alerts**: Receive notifications for critical events

### **Remote Monitoring**

1. **📱 Mobile Access**: Monitor infrastructure from anywhere
2. **🌐 Remote Alerts**: Get notified of issues while away
3. **📊 Quick Status**: Check system status on the go
4. **🔧 Remote Control**: Basic remote control capabilities

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Connection Issues**:
   - Check network connectivity
   - Verify Grafana URL and credentials
   - Ensure firewall allows connections

2. **Dashboard Not Loading**:
   - Check dashboard permissions
   - Verify dashboard IDs
   - Test Grafana access directly

3. **Performance Issues**:
   - Reduce refresh intervals
   - Optimize dashboard queries
   - Check server resources

### **Debug Commands**

```bash
# Test Grafana connectivity
curl -u admin:admin http://localhost:3000/api/health

# Check RebootX On-Prem status
curl http://localhost:8080/health

# View logs
docker logs rebootx-on-prem
docker logs tapo-grafana
```

## 📈 **Performance Optimization**

### **Mobile Performance**

1. **Dashboard Optimization**:
   - Use fewer panels per dashboard
   - Optimize query intervals
   - Use appropriate time ranges

2. **Network Optimization**:
   - Use local network when possible
   - Compress data transmission
   - Cache frequently accessed data

3. **Battery Optimization**:
   - Reduce refresh frequencies
   - Use efficient data formats
   - Implement smart caching

## 🎯 **Best Practices**

### **Dashboard Design**

1. **Mobile-First**: Design dashboards with mobile in mind
2. **Clear Visuals**: Use clear icons and large text
3. **Quick Overview**: Provide quick status overviews
4. **Touch-Friendly**: Ensure all controls are touch-friendly

### **Monitoring Strategy**

1. **Essential Metrics**: Focus on essential metrics only
2. **Alert Thresholds**: Set appropriate alert thresholds
3. **Notification Management**: Manage notification frequency
4. **Regular Updates**: Keep dashboards updated and relevant

## 🔮 **Future Enhancements**

### **Planned Features**

1. **Advanced Notifications**: Enhanced push notification system
2. **Offline Mode**: Improved offline functionality
3. **Custom Widgets**: Custom mobile widgets
4. **Integration APIs**: Enhanced API integration

### **Community Contributions**

1. **Open Source**: Contribute to RebootX On-Prem project
2. **Dashboard Sharing**: Share mobile-optimized dashboards
3. **Best Practices**: Share monitoring best practices
4. **Feature Requests**: Request new features

## 📚 **Resources**

### **Official Resources**

- **RebootX App**: Available on App Store
- **RebootX On-Prem**: [GitHub Repository](https://github.com/c100k/rebootx-on-prem)
- **Documentation**: [Official Documentation](https://c100k.eu/p/rebootx/)

### **Community Resources**

- **Hacker News Discussion**: [Community Feedback](https://news.ycommunity.com/item?id=39838207)
- **GitHub Issues**: [Issue Tracker](https://github.com/c100k/rebootx-on-prem/issues)
- **Community Forums**: [Community Discussions](https://news.ycomunities.com/rebootx)

## 🏆 **Conclusion**

RebootX provides an excellent solution for mobile infrastructure monitoring, especially for homebrew monitoring enthusiasts. With both cloud and on-premises options, it offers flexibility and cost-effectiveness for monitoring your infrastructure "in your pocket."

### **Key Benefits**

- **📱 Mobile Access**: Monitor infrastructure from your iPad
- **💰 Cost-Effective**: Affordable monitoring solution
- **🔧 Flexible**: Both cloud and self-hosted options
- **🏠 Home-Friendly**: Perfect for home lab monitoring
- **📊 Grafana Integration**: Seamless integration with existing dashboards

### **Perfect for**

- **Home Infrastructure Monitoring**: Monitor home servers, cameras, and smart devices
- **Remote Monitoring**: Check system status while away
- **Cost-Conscious Users**: Affordable alternative to expensive monitoring solutions
- **Homebrew Enthusiasts**: Self-hosted option for complete control

**Ready for implementation** 🚀
