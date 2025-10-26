# Tapo Cameras MCP - Specialized Monitoring Documentation

## Overview

The `tapo-cameras-mcp` repository is a special monitoring case that requires particularly extensive Grafana dashboards due to its comprehensive home surveillance and security monitoring capabilities. This document provides specialized monitoring documentation, templates, and configurations specifically designed for home security and surveillance systems.

## 🏠 **Special Monitoring Requirements**

### **Dual Architecture Monitoring**

The `tapo-cameras-mcp` repository serves dual purposes requiring specialized monitoring:

1. **🎥 Individual Security Device MCP Servers**: Standalone camera control (Tapo, USB, Ring)
2. **🏠 Unified Security Dashboard**: Multi-MCP orchestration platform

### **Home Surveillance & Security Focus**

Unlike general MCP servers, this repository requires monitoring for:

- **🏠 Home Security Systems**: Cameras, alarms, sensors, and environmental monitors
- **🔋 Energy Monitoring**: Smart plugs, power consumption, and energy efficiency
- **🚨 Alarm Systems**: Nest Protect, Ring alarms, and security event correlation
- **📊 AI-Powered Analytics**: Scene analysis, object detection, and performance analytics
- **📱 Multi-Device Integration**: Cross-system alert analysis and unified monitoring

## 📊 **Specialized Dashboard Requirements**

### **1. Home Security Overview Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "🏠 Home Security Overview",
    "tags": ["home-security", "surveillance", "tapo-cameras"],
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
        "title": "🔒 Security Status Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "home_security_cameras_online",
            "legendFormat": "Cameras Online",
            "refId": "A"
          },
          {
            "expr": "home_security_alarms_active",
            "legendFormat": "Active Alarms",
            "refId": "B"
          },
          {
            "expr": "home_security_sensors_online",
            "legendFormat": "Sensors Online",
            "refId": "C"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 1},
                {"color": "green", "value": 2}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "📹 Camera Grid View",
        "type": "custom",
        "targets": [
          {
            "expr": "tapo_cameras_status",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 12,
          "w": 24,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 3,
        "title": "🚨 Security Events Timeline",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"home-security\", level=\"warning\"}",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 20
        }
      },
      {
        "id": 4,
        "title": "🔋 Energy Monitoring",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_p115_power_consumption_watts",
            "legendFormat": "{{device_name}} Power (W)",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 20
        }
      }
    ]
  }
}
```

### **2. Camera Performance Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "📹 Camera Performance & Health",
    "tags": ["cameras", "performance", "health"],
    "style": "dark",
    "timezone": "Europe/Vienna",
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "🌡️ Camera Temperature",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_camera_temperature_celsius",
            "legendFormat": "{{camera_name}} Temperature",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "celsius",
            "min": 0,
            "max": 80,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 65}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "📶 WiFi Signal Strength",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_camera_wifi_signal_dbm",
            "legendFormat": "{{camera_name}} Signal",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "dBs",
            "min": -100,
            "max": 0,
            "thresholds": {
              "steps": [
                {"color": "red", "value": -80},
                {"color": "yellow", "value": -60},
                {"color": "green", "value": -40}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "🎥 Motion Detection Events",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(tapo_camera_motion_events_total[5m])",
            "legendFormat": "{{camera_name}} Motion Rate",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "📊 Network Latency",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_camera_network_latency_ms",
            "legendFormat": "{{camera_name}} Latency",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "min": 0,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 8
        }
      },
      {
        "id": 5,
        "title": "💾 Storage Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_camera_storage_used_percent",
            "legendFormat": "{{camera_name}} Storage",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 90}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 16
        }
      }
    ]
  }
}
```

### **3. Energy Management Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "🔋 Energy Management & Smart Plugs",
    "tags": ["energy", "smart-plugs", "tapo-p115"],
    "style": "dark",
    "timezone": "Europe/Vienna",
    "refresh": "1m",
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "⚡ Real-time Power Consumption",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_p115_power_consumption_watts",
            "legendFormat": "{{device_name}} Power (W)",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "watt",
            "min": 0,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 100}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "💰 Daily Energy Cost",
        "type": "stat",
        "targets": [
          {
            "expr": "tapo_p115_daily_energy_cost_euros",
            "legendFormat": "{{device_name}} Daily Cost",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyEUR",
            "decimals": 2
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "📊 Energy Usage Patterns",
        "type": "heatmap",
        "targets": [
          {
            "expr": "tapo_p115_energy_usage_wh",
            "legendFormat": "{{device_name}} Energy",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "🔌 Smart Plug Status",
        "type": "table",
        "targets": [
          {
            "expr": "tapo_p115_device_status",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 16
        }
      }
    ]
  }
}
```

### **4. Alarm System Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "🚨 Alarm System & Sensors",
    "tags": ["alarms", "sensors", "nest-protect", "ring"],
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
        "title": "🔥 Nest Protect Status",
        "type": "stat",
        "targets": [
          {
            "expr": "nest_protect_status",
            "legendFormat": "{{device_name}} Status",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [
              {
                "options": {
                  "0": {"color": "green", "text": "OK"},
                  "1": {"color": "yellow", "text": "Warning"},
                  "2": {"color": "red", "text": "Alert"}
                },
                "type": "value"
              }
            ]
          }
        },
        "gridPos": {
          "h": 8,
          "w": 8,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "🚪 Ring Doorbell Status",
        "type": "stat",
        "targets": [
          {
            "expr": "ring_doorbell_status",
            "legendFormat": "{{device_name}} Status",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 8,
          "x": 8,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "🔋 Battery Levels",
        "type": "timeseries",
        "targets": [
          {
            "expr": "nest_protect_battery_percent",
            "legendFormat": "{{device_name}} Battery",
            "refId": "A"
          },
          {
            "expr": "ring_doorbell_battery_percent",
            "legendFormat": "{{device_name}} Battery",
            "refId": "B"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 20},
                {"color": "green", "value": 50}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 8,
          "x": 16,
          "y": 0
        }
      },
      {
        "id": 4,
        "title": "🚨 Security Events",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"home-security\", level=\"warning\"}",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 5,
        "title": "📊 Motion Detection Heatmap",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(tapo_camera_motion_events_total[5m])",
            "legendFormat": "{{camera_name}} Motion",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 16
        }
      }
    ]
  }
}
```

### **5. AI Analytics Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "🤖 AI Analytics & Scene Analysis",
    "tags": ["ai", "analytics", "scene-analysis", "object-detection"],
    "style": "dark",
    "timezone": "Europe/Vienna",
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "👤 Person Detection",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(tapo_camera_person_detection_total[5m])",
            "legendFormat": "{{camera_name}} Person Detection",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "🚗 Vehicle Detection",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(tapo_camera_vehicle_detection_total[5m])",
            "legendFormat": "{{camera_name}} Vehicle Detection",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "📊 Scene Analysis Accuracy",
        "type": "stat",
        "targets": [
          {
            "expr": "tapo_camera_scene_analysis_accuracy_percent",
            "legendFormat": "{{camera_name}} Accuracy",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {
          "h": 8,
          "w": 8,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "🎯 Object Detection Confidence",
        "type": "timeseries",
        "targets": [
          {
            "expr": "tapo_camera_object_detection_confidence",
            "legendFormat": "{{camera_name}} Confidence",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100
          }
        },
        "gridPos": {
          "h": 8,
          "w": 16,
          "x": 8,
          "y": 8
        }
      },
      {
        "id": 5,
        "title": "📈 Performance Analytics",
        "type": "table",
        "targets": [
          {
            "expr": "tapo_camera_performance_metrics",
            "refId": "A"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 16
        }
      }
    ]
  }
}
```

## 🔧 **Specialized Configuration Templates**

### **Docker Compose for Home Security**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Tapo Camera MCP Server
  tapo-camera-mcp:
    build: .
    container_name: tapo-camera-mcp
    ports:
      - "7777:7777"  # Web Dashboard
      - "8080:8080"  # MCP Server
      - "9091:9091"  # Prometheus Metrics
    environment:
      - LOG_LEVEL=INFO
      - PROMETHEUS_PORT=9091
      - TAPO_USERNAME=${TAPO_USERNAME}
      - TAPO_PASSWORD=${TAPO_PASSWORD}
      - NEST_PROTECT_TOKEN=${NEST_PROTECT_TOKEN}
      - RING_TOKEN=${RING_TOKEN}
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
      - ./monitoring/promtail/promtail.yml:/etc/promtail/config.yml
    networks:
      - home-security
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki

  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: tapo-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - home-security
    restart: unless-stopped

  # Loki - Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: tapo-loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - home-security
    restart: unless-stopped

  # Promtail - Log shipping
  promtail:
    image: grafana/promtail:latest
    container_name: tapo-promtail
    volumes:
      - ./monitoring/promtail:/etc/promtail
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - home-security
    restart: unless-stopped

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: tapo-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel,grafana-heatmap-panel
      - GF_SECURITY_ALLOW_EMBEDDING=true
      - GF_AUTH_ANONYMOUS_ENABLED=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - home-security
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki

volumes:
  prometheus_data:
  loki_data:
  grafana_data:

networks:
  home-security:
    driver: bridge
```

### **Prometheus Configuration for Home Security**

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'home-security-cluster'
    environment: 'home'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      timeout: 10s
      api_version: v2

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'tapo-camera-mcp'
    static_configs:
      - targets: ['tapo-camera-mcp:9091']
    metrics_path: /metrics
    scrape_interval: 5s
    scrape_timeout: 5s
    honor_labels: true
    honor_timestamps: true

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
    metrics_path: /metrics
    scrape_interval: 15s
```

### **Alert Rules for Home Security**

```yaml
# monitoring/prometheus/rules/home-security-alerts.yml
groups:
  - name: home-security-alerts
    rules:
      - alert: CameraOffline
        expr: tapo_camera_status != 1
        for: 2m
        labels:
          severity: critical
          service: home-security
          component: camera
        annotations:
          summary: "Home security camera {{ $labels.camera_name }} is offline"
          description: "Camera {{ $labels.camera_name }} has been offline for more than 2 minutes"

      - alert: HighCameraTemperature
        expr: tapo_camera_temperature_celsius > 65
        for: 1m
        labels:
          severity: warning
          service: home-security
          component: camera
        annotations:
          summary: "Camera {{ $labels.camera_name }} running hot"
          description: "Camera temperature is {{ $value }}°C"

      - alert: WeakWiFiSignal
        expr: tapo_camera_wifi_signal_dbm < -80
        for: 5m
        labels:
          severity: warning
          service: home-security
          component: network
        annotations:
          summary: "Weak WiFi signal for camera {{ $labels.camera_name }}"
          description: "WiFi signal strength is {{ $value }}dBm"

      - alert: MotionDetectionBurst
        expr: rate(tapo_camera_motion_events_total[5m]) > 5
        for: 30s
        labels:
          severity: info
          service: home-security
          component: motion
        annotations:
          summary: "High motion activity detected"
          description: "Camera {{ $labels.camera_name }} detected {{ $value }} motion events per minute"

      - alert: NestProtectAlert
        expr: nest_protect_status == 2
        for: 0s
        labels:
          severity: critical
          service: home-security
          component: smoke-detector
        annotations:
          summary: "Nest Protect alert triggered"
          description: "Smoke or CO detector {{ $labels.device_name }} has triggered an alert"

      - alert: RingDoorbellBatteryLow
        expr: ring_doorbell_battery_percent < 20
        for: 5m
        labels:
          severity: warning
          service: home-security
          component: doorbell
        annotations:
          summary: "Ring doorbell battery low"
          description: "Doorbell {{ $labels.device_name }} battery is {{ $value }}%"

      - alert: HighEnergyConsumption
        expr: tapo_p115_power_consumption_watts > 100
        for: 10m
        labels:
          severity: warning
          service: home-security
          component: energy
        annotations:
          summary: "High energy consumption detected"
          description: "Smart plug {{ $labels.device_name }} is consuming {{ $value }}W"

      - alert: StorageSpaceLow
        expr: tapo_camera_storage_used_percent > 90
        for: 5m
        labels:
          severity: warning
          service: home-security
          component: storage
        annotations:
          summary: "Camera storage space low"
          description: "Camera {{ $labels.camera_name }} storage is {{ $value }}% full"
```

## 🚀 **Implementation Guide**

### **1. Setup Home Security Monitoring**

```bash
# Clone the repository
git clone https://github.com/sandraschi/tapo-camera-mcp.git
cd tapo-camera-mcp

# Copy configuration templates
cp monitoring-templates/* monitoring/

# Edit environment variables
cp .env.example .env
# Edit .env with your device credentials

# Start the monitoring stack
docker-compose up -d
```

### **2. Access Services**

- **🏠 Home Security Dashboard**: http://localhost:7777
- **📊 Grafana Dashboards**: http://localhost:3000 (admin/admin)
- **📈 Prometheus Metrics**: http://localhost:9090
- **📝 Loki Logs**: http://localhost:3100
- **🔧 MCP Server**: http://localhost:8080

### **3. Configure Devices**

```yaml
# config.yaml
cameras:
  living_room:
    type: tapo
    host: 192.168.1.100
    username: ${TAPO_USERNAME}
    password: ${TAPO_PASSWORD}
  kitchen:
    type: tapo
    host: 192.168.1.101
    username: ${TAPO_USERNAME}
    password: ${TAPO_PASSWORD}

smart_plugs:
  kitchen_lights:
    type: tapo_p115
    host: 192.168.1.102
    username: ${TAPO_USERNAME}
    password: ${TAPO_PASSWORD}

alarms:
  smoke_detector:
    type: nest_protect
    device_id: ${NEST_PROTECT_DEVICE_ID}
    token: ${NEST_PROTECT_TOKEN}
  doorbell:
    type: ring
    device_id: ${RING_DOORBELL_ID}
    token: ${RING_TOKEN}
```

## 📊 **Specialized Metrics**

### **Camera Metrics**

```python
# Camera-specific metrics
tapo_camera_status = Gauge('tapo_camera_status', 'Camera online status', ['camera_name', 'camera_id'])
tapo_camera_temperature_celsius = Gauge('tapo_camera_temperature_celsius', 'Camera temperature', ['camera_name', 'camera_id'])
tapo_camera_wifi_signal_dbm = Gauge('tapo_camera_wifi_signal_dbm', 'WiFi signal strength', ['camera_name', 'camera_id'])
tapo_camera_motion_events_total = Counter('tapo_camera_motion_events_total', 'Total motion events', ['camera_name', 'camera_id'])
tapo_camera_person_detection_total = Counter('tapo_camera_person_detection_total', 'Person detection events', ['camera_name', 'camera_id'])
tapo_camera_vehicle_detection_total = Counter('tapo_camera_vehicle_detection_total', 'Vehicle detection events', ['camera_name', 'camera_id'])
tapo_camera_storage_used_percent = Gauge('tapo_camera_storage_used_percent', 'Storage usage percentage', ['camera_name', 'camera_id'])
tapo_camera_network_latency_ms = Histogram('tapo_camera_network_latency_ms', 'Network latency', ['camera_name', 'camera_id'])
```

### **Energy Metrics**

```python
# Energy monitoring metrics
tapo_p115_power_consumption_watts = Gauge('tapo_p115_power_consumption_watts', 'Power consumption in watts', ['device_name', 'device_id'])
tapo_p115_daily_energy_cost_euros = Gauge('tapo_p115_daily_energy_cost_euros', 'Daily energy cost in euros', ['device_name', 'device_id'])
tapo_p115_energy_usage_wh = Counter('tapo_p115_energy_usage_wh', 'Energy usage in watt-hours', ['device_name', 'device_id'])
tapo_p115_device_status = Gauge('tapo_p115_device_status', 'Smart plug status', ['device_name', 'device_id'])
```

### **Alarm Metrics**

```python
# Alarm system metrics
nest_protect_status = Gauge('nest_protect_status', 'Nest Protect status', ['device_name', 'device_id'])
nest_protect_battery_percent = Gauge('nest_protect_battery_percent', 'Nest Protect battery level', ['device_name', 'device_id'])
ring_doorbell_status = Gauge('ring_doorbell_status', 'Ring doorbell status', ['device_name', 'device_id'])
ring_doorbell_battery_percent = Gauge('ring_doorbell_battery_percent', 'Ring doorbell battery level', ['device_name', 'device_id'])
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Camera Authentication Failures**
   - Check Tapo credentials in environment variables
   - Verify camera IP addresses and network connectivity
   - Ensure cameras are on the same network

2. **Grafana Dashboard Not Loading**
   - Verify data source configuration
   - Check Prometheus metrics endpoint
   - Ensure proper JSON path expressions

3. **Motion Detection Not Working**
   - Verify motion detection is enabled on cameras
   - Check camera firmware version
   - Ensure proper API permissions

4. **Energy Monitoring Issues**
   - Verify Tapo P115 smart plug connectivity
   - Check power consumption thresholds
   - Ensure proper device configuration

### **Debug Commands**

```bash
# Check camera connectivity
curl http://localhost:8080/api/cameras

# Test metrics endpoint
curl http://localhost:9091/metrics

# Check Grafana data source
curl http://localhost:3000/api/datasources

# View logs
docker-compose logs -f tapo-camera-mcp
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

## 📈 **Performance Optimization**

### **Resource Requirements**

- **Memory**: 4GB minimum for full home security stack
- **CPU**: 2 cores minimum for AI analytics
- **Storage**: 50GB for video storage and metrics
- **Network**: Stable WiFi for camera connectivity

### **Scaling Considerations**

- **Multiple Cameras**: Support for 10+ cameras per instance
- **Historical Data**: 30-day retention for metrics and logs
- **Video Storage**: Local storage with optional cloud backup
- **Mobile Access**: Responsive design for mobile monitoring

## 🎯 **Future Enhancements**

### **Phase 1: Advanced Analytics**
- **AI-powered motion analysis** (person vs. vehicle detection)
- **Behavior pattern recognition** (unusual activity detection)
- **Integration with smart home systems** (lights, alarms)

### **Phase 2: Mobile Integration**
- **Mobile app notifications** via Grafana mobile
- **Push notifications** for security events
- **Remote camera control** via mobile interface

### **Phase 3: Enterprise Features**
- **Multi-tenant support** for apartment buildings
- **Role-based access control** for different users
- **API rate limiting and authentication**
- **Backup and disaster recovery** for metrics data

---

## 🏆 **Conclusion**

The `tapo-cameras-mcp` repository requires specialized monitoring due to its comprehensive home surveillance and security capabilities. This documentation provides:

- **🏠 Specialized dashboards** for home security monitoring
- **📊 Comprehensive metrics** for cameras, energy, and alarms
- **🚨 Advanced alerting** for security events
- **🔋 Energy management** monitoring and optimization
- **🤖 AI analytics** for scene analysis and object detection

The monitoring stack provides complete observability for home security systems while maintaining the flexibility to integrate with other MCP servers and smart home devices.

**Ready for implementation** 🚀
