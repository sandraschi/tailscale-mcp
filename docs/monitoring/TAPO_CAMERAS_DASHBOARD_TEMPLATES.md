# Tapo Cameras MCP - Specialized Grafana Dashboard Templates

## Overview

This document provides specialized Grafana dashboard templates specifically designed for the `tapo-cameras-mcp` repository's comprehensive home surveillance and security monitoring capabilities.

## 🏠 **Dashboard Categories**

### **1. Home Security Overview Dashboard**
- **Purpose**: Central command center for all home security systems
- **Key Metrics**: Camera status, alarm status, motion detection, energy consumption
- **Refresh Rate**: 10 seconds
- **Time Range**: Last hour

### **2. Camera Performance & Health Dashboard**
- **Purpose**: Detailed camera monitoring and health metrics
- **Key Metrics**: Temperature, WiFi signal, motion events, network latency, storage usage
- **Refresh Rate**: 30 seconds
- **Time Range**: Last 6 hours

### **3. Energy Management Dashboard**
- **Purpose**: Smart plug monitoring and energy consumption analysis
- **Key Metrics**: Power consumption, energy costs, usage patterns, device status
- **Refresh Rate**: 1 minute
- **Time Range**: Last 24 hours

### **4. Alarm System Dashboard**
- **Purpose**: Security alarms, sensors, and emergency systems monitoring
- **Key Metrics**: Nest Protect status, Ring doorbell status, battery levels, security events
- **Refresh Rate**: 10 seconds
- **Time Range**: Last hour

### **5. AI Analytics Dashboard**
- **Purpose**: AI-powered scene analysis and object detection monitoring
- **Key Metrics**: Person detection, vehicle detection, scene analysis accuracy, object detection confidence
- **Refresh Rate**: 30 seconds
- **Time Range**: Last 6 hours

## 📊 **Dashboard Templates**

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

### **2. Camera Performance & Health Dashboard**

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

## 🔧 **Configuration Templates**

### **Grafana Data Source Configuration**

```json
{
  "name": "Tapo Camera Metrics",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "jsonData": {
    "httpMethod": "POST",
    "queryTimeout": "60s",
    "timeInterval": "5s"
  }
}
```

### **Dashboard Variables Configuration**

```json
{
  "templating": {
    "list": [
      {
        "name": "camera",
        "type": "query",
        "query": "label_values(tapo_camera_status, camera_name)",
        "refresh": 1,
        "includeAll": true,
        "multi": true,
        "allValue": ".*"
      },
      {
        "name": "device",
        "type": "query",
        "query": "label_values(tapo_p115_device_status, device_name)",
        "refresh": 1,
        "includeAll": true,
        "multi": true,
        "allValue": ".*"
      },
      {
        "name": "time_range",
        "type": "interval",
        "query": "1m,5m,15m,30m,1h,6h,12h,1d",
        "refresh": 1,
        "includeAll": false,
        "multi": false,
        "current": {
          "text": "1h",
          "value": "1h"
        }
      }
    ]
  }
}
```

## 🚀 **Implementation Guide**

### **1. Import Dashboards**

```bash
# Import dashboard templates
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @home-security-overview.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @camera-performance-health.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @energy-management.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @alarm-system.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @ai-analytics.json
```

### **2. Configure Data Sources**

```bash
# Configure Prometheus data source
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @prometheus-datasource.json
```

### **3. Set Up Alerting**

```bash
# Import alert rules
curl -X POST http://admin:admin@localhost:3000/api/ruler/grafana/api/v1/rules \
  -H "Content-Type: application/json" \
  -d @home-security-alerts.json
```

## 📊 **Custom Panel Types**

### **Camera Grid Panel**

```json
{
  "type": "custom",
  "title": "📹 Camera Grid View",
  "targets": [
    {
      "expr": "tapo_cameras_status",
      "refId": "A"
    }
  ],
  "options": {
    "gridColumns": 4,
    "showThumbnails": true,
    "showLiveFeeds": true,
    "autoRefresh": true
  }
}
```

### **Energy Heatmap Panel**

```json
{
  "type": "heatmap",
  "title": "📊 Energy Usage Patterns",
  "targets": [
    {
      "expr": "tapo_p115_energy_usage_wh",
      "legendFormat": "{{device_name}} Energy",
      "refId": "A"
    }
  ],
  "options": {
    "colorMode": "spectrum",
    "showLegend": true,
    "showTooltip": true
  }
}
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Dashboard Not Loading**
   - Check data source configuration
   - Verify Prometheus metrics endpoint
   - Ensure proper JSON path expressions

2. **Missing Data**
   - Check camera connectivity
   - Verify metric collection
   - Ensure proper label configuration

3. **Performance Issues**
   - Reduce refresh rates
   - Limit time ranges
   - Optimize queries

### **Debug Commands**

```bash
# Check Grafana data source
curl http://admin:admin@localhost:3000/api/datasources

# Test Prometheus metrics
curl http://localhost:9090/api/v1/query?query=tapo_camera_status

# Check dashboard configuration
curl http://admin:admin@localhost:3000/api/dashboards/db/home-security-overview
```

## 📈 **Performance Optimization**

### **Dashboard Optimization**

- **Refresh Rates**: Use appropriate refresh rates (10s for real-time, 30s for performance)
- **Time Ranges**: Limit time ranges to reduce data load
- **Query Optimization**: Use efficient Prometheus queries
- **Panel Limits**: Limit number of panels per dashboard

### **Resource Management**

- **Memory Usage**: Monitor Grafana memory consumption
- **CPU Usage**: Optimize query complexity
- **Storage**: Manage dashboard and data retention
- **Network**: Optimize data transfer

---

## 🏆 **Conclusion**

These specialized Grafana dashboard templates provide comprehensive monitoring capabilities for the `tapo-cameras-mcp` repository's home surveillance and security systems. The templates include:

- **🏠 Home Security Overview**: Central command center for all security systems
- **📹 Camera Performance**: Detailed camera monitoring and health metrics
- **🔋 Energy Management**: Smart plug monitoring and energy consumption analysis
- **🚨 Alarm System**: Security alarms, sensors, and emergency systems monitoring
- **🤖 AI Analytics**: AI-powered scene analysis and object detection monitoring

The dashboards are designed to provide real-time monitoring, historical analysis, and comprehensive alerting for home security systems while maintaining optimal performance and user experience.

**Ready for implementation** 🚀
