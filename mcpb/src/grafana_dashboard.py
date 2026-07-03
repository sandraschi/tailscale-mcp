"""
Grafana Dashboard Configuration for Tailscale Monitoring

Provides comprehensive Grafana dashboard templates and configuration
for visualizing Tailscale network metrics and health.
"""

import json
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class GrafanaPanel(BaseModel):
    """Grafana panel configuration."""

    id: int = Field(..., description="Panel ID")
    title: str = Field(..., description="Panel title")
    type: str = Field(..., description="Panel type")
    targets: list[dict[str, Any]] = Field(..., description="Panel targets/queries")
    gridPos: dict[str, int] = Field(..., description="Panel grid position")
    options: dict[str, Any] = Field(default_factory=dict, description="Panel options")


class GrafanaDashboard(BaseModel):
    """Grafana dashboard configuration."""

    title: str = Field(..., description="Dashboard title")
    description: str = Field(..., description="Dashboard description")
    tags: list[str] = Field(default_factory=list, description="Dashboard tags")
    panels: list[GrafanaPanel] = Field(..., description="Dashboard panels")
    time_range: dict[str, str] = Field(
        default_factory=lambda: {"from": "now-1h", "to": "now"}
    )
    refresh: str = Field(default="30s", description="Dashboard refresh interval")


class TailscaleGrafanaDashboard:
    """Tailscale Grafana dashboard configuration and management."""

    def __init__(self, tailnet: str):
        """Initialize Grafana dashboard manager.

        Args:
            tailnet: Tailnet name for dashboard customization
        """
        self.tailnet = tailnet
        self.dashboard_version = 1

        logger.info("Grafana dashboard manager initialized", tailnet=tailnet)

    def create_comprehensive_dashboard(self) -> dict[str, Any]:
        """Create a comprehensive Tailscale monitoring dashboard."""
        try:
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "uid": f"tailscale-{self.tailnet.lower().replace('.', '-')}",
                    "title": f"Tailscale Network - {self.tailnet}",
                    "description": f"Comprehensive monitoring dashboard for {self.tailnet} Tailscale network",
                    "tags": ["tailscale", "networking", "monitoring", "infrastructure"],
                    "timezone": "browser",
                    "panels": self._create_all_panels(),
                    "time": {"from": "now-1h", "to": "now"},
                    "refresh": "30s",
                    "schemaVersion": 30,
                    "version": self.dashboard_version,
                    "gnetId": None,
                    "links": [],
                    "annotations": {"list": []},
                    "templating": {"list": []},
                },
                "overwrite": True,
            }

            logger.info(
                "Comprehensive Grafana dashboard created",
                dashboard_title=dashboard_config["dashboard"]["title"],
                panels_count=len(dashboard_config["dashboard"]["panels"]),
            )

            return dashboard_config

        except Exception as e:
            logger.error("Error creating comprehensive dashboard", error=str(e))
            raise TailscaleMCPError(f"Failed to create dashboard: {e}") from e

    def create_network_topology_dashboard(self) -> dict[str, Any]:
        """Create a network topology visualization dashboard."""
        try:
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "uid": f"tailscale-topology-{self.tailnet.lower().replace('.', '-')}",
                    "title": f"Tailscale Network Topology - {self.tailnet}",
                    "description": f"Network topology and device relationships for {self.tailnet}",
                    "tags": ["tailscale", "topology", "network", "visualization"],
                    "timezone": "browser",
                    "panels": self._create_topology_panels(),
                    "time": {"from": "now-1h", "to": "now"},
                    "refresh": "1m",
                    "schemaVersion": 30,
                    "version": self.dashboard_version,
                },
                "overwrite": True,
            }

            logger.info(
                "Network topology dashboard created",
                dashboard_title=dashboard_config["dashboard"]["title"],
            )

            return dashboard_config

        except Exception as e:
            logger.error("Error creating topology dashboard", error=str(e))
            raise TailscaleMCPError(f"Failed to create topology dashboard: {e}") from e

    def create_security_dashboard(self) -> dict[str, Any]:
        """Create a security-focused monitoring dashboard."""
        try:
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "uid": f"tailscale-security-{self.tailnet.lower().replace('.', '-')}",
                    "title": f"Tailscale Security - {self.tailnet}",
                    "description": f"Security monitoring and ACL management for {self.tailnet}",
                    "tags": ["tailscale", "security", "acl", "monitoring"],
                    "timezone": "browser",
                    "panels": self._create_security_panels(),
                    "time": {"from": "now-24h", "to": "now"},
                    "refresh": "1m",
                    "schemaVersion": 30,
                    "version": self.dashboard_version,
                },
                "overwrite": True,
            }

            logger.info(
                "Security dashboard created",
                dashboard_title=dashboard_config["dashboard"]["title"],
            )

            return dashboard_config

        except Exception as e:
            logger.error("Error creating security dashboard", error=str(e))
            raise TailscaleMCPError(f"Failed to create security dashboard: {e}") from e

    def _create_all_panels(self) -> list[dict[str, Any]]:
        """Create all panels for the comprehensive dashboard."""
        panels = []

        # Overview Row
        panels.extend(
            [
                self._create_device_status_panel(),
                self._create_network_health_panel(),
                self._create_bandwidth_usage_panel(),
                self._create_latency_panel(),
            ]
        )

        # Device Details Row
        panels.extend(
            [
                self._create_device_list_panel(),
                self._create_device_activity_panel(),
                self._create_geographic_distribution_panel(),
            ]
        )

        # Network Performance Row
        panels.extend(
            [
                self._create_connection_quality_panel(),
                self._create_route_performance_panel(),
                self._create_error_rates_panel(),
            ]
        )

        # Historical Data Row
        panels.extend(
            [
                self._create_historical_uptime_panel(),
                self._create_bandwidth_trends_panel(),
                self._create_device_growth_panel(),
            ]
        )

        return panels

    def _create_topology_panels(self) -> list[dict[str, Any]]:
        """Create panels for network topology dashboard."""
        return [
            self._create_network_graph_panel(),
            self._create_device_relationships_panel(),
            self._create_route_map_panel(),
            self._create_connectivity_matrix_panel(),
        ]

    def _create_security_panels(self) -> list[dict[str, Any]]:
        """Create panels for security dashboard."""
        return [
            self._create_acl_overview_panel(),
            self._create_access_patterns_panel(),
            self._create_security_alerts_panel(),
            self._create_device_trust_panel(),
        ]

    def _create_device_status_panel(self) -> dict[str, Any]:
        """Create device status overview panel."""
        return {
            "id": 1,
            "title": "Device Status Overview",
            "type": "stat",
            "targets": [
                {
                    "expr": "tailscale_devices_online",
                    "legendFormat": "Online Devices",
                    "refId": "A",
                },
                {
                    "expr": "tailscale_devices_total",
                    "legendFormat": "Total Devices",
                    "refId": "B",
                },
            ],
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 70},
                            {"color": "green", "value": 90},
                        ]
                    },
                }
            },
            "options": {
                "colorMode": "background",
                "graphMode": "area",
                "justifyMode": "center",
                "orientation": "horizontal",
            },
        }

    def _create_network_health_panel(self) -> dict[str, Any]:
        """Create network health gauge panel."""
        return {
            "id": 2,
            "title": "Network Health Score",
            "type": "gauge",
            "targets": [
                {
                    "expr": "tailscale_network_health_score",
                    "legendFormat": "Health Score",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 60},
                            {"color": "green", "value": 80},
                        ]
                    },
                }
            },
            "options": {"showThresholdLabels": True, "showThresholdMarkers": True},
        }

    def _create_bandwidth_usage_panel(self) -> dict[str, Any]:
        """Create bandwidth usage graph panel."""
        return {
            "id": 3,
            "title": "Bandwidth Usage",
            "type": "graph",
            "targets": [
                {
                    "expr": "rate(tailscale_bytes_sent_total[5m])",
                    "legendFormat": "Bytes Sent/sec - {{device_id}}",
                    "refId": "A",
                },
                {
                    "expr": "rate(tailscale_bytes_received_total[5m])",
                    "legendFormat": "Bytes Received/sec - {{device_id}}",
                    "refId": "B",
                },
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "yAxes": [
                {
                    "label": "Bytes/sec",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                },
                {"label": None, "logBase": 1, "max": None, "min": None, "show": True},
            ],
            "xAxis": {"mode": "time", "name": None, "show": True, "values": []},
            "legend": {
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "show": True,
                "total": False,
                "values": False,
            },
        }

    def _create_latency_panel(self) -> dict[str, Any]:
        """Create network latency panel."""
        return {
            "id": 4,
            "title": "Network Latency",
            "type": "graph",
            "targets": [
                {
                    "expr": "tailscale_network_latency_seconds",
                    "legendFormat": "{{from_device}} → {{to_device}}",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            "yAxes": [
                {
                    "label": "Latency (ms)",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                    "unit": "ms",
                }
            ],
            "xAxis": {"mode": "time", "name": None, "show": True, "values": []},
        }

    def _create_device_list_panel(self) -> dict[str, Any]:
        """Create device list table panel."""
        return {
            "id": 5,
            "title": "Device List",
            "type": "table",
            "targets": [
                {
                    "expr": "tailscale_device_info",
                    "format": "table",
                    "instant": True,
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16},
            "transformations": [
                {
                    "id": "organize",
                    "options": {
                        "excludeByName": {},
                        "indexByName": {},
                        "renameByName": {
                            "Value": "Device Name",
                            "device_id": "Device ID",
                            "status": "Status",
                            "last_seen": "Last Seen",
                        },
                    },
                }
            ],
        }

    def _create_device_activity_panel(self) -> dict[str, Any]:
        """Create device activity heatmap panel."""
        return {
            "id": 6,
            "title": "Device Activity Heatmap",
            "type": "heatmap",
            "targets": [
                {
                    "expr": "rate(tailscale_device_activity[5m])",
                    "format": "heatmap",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 8, "x": 8, "y": 16},
            "heatmap": {"xAxis": {"show": True}, "yAxis": {"show": True}},
        }

    def _create_geographic_distribution_panel(self) -> dict[str, Any]:
        """Create geographic distribution map panel."""
        return {
            "id": 7,
            "title": "Geographic Distribution",
            "type": "geomap",
            "targets": [
                {"expr": "tailscale_device_location", "format": "table", "refId": "A"}
            ],
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 16},
            "options": {
                "basemap": {"type": "default"},
                "layers": [
                    {
                        "type": "markers",
                        "config": {
                            "style": {
                                "color": {"field": "status", "fixed": "green"},
                                "size": {"field": "device_count", "fixed": 5},
                            }
                        },
                    }
                ],
            },
        }

    def _create_connection_quality_panel(self) -> dict[str, Any]:
        """Create connection quality panel."""
        return {
            "id": 8,
            "title": "Connection Quality",
            "type": "stat",
            "targets": [
                {
                    "expr": "avg(tailscale_connection_quality)",
                    "legendFormat": "Average Quality",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 24},
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 70},
                            {"color": "green", "value": 90},
                        ]
                    },
                }
            },
        }

    def _create_route_performance_panel(self) -> dict[str, Any]:
        """Create route performance panel."""
        return {
            "id": 9,
            "title": "Route Performance",
            "type": "graph",
            "targets": [
                {
                    "expr": "tailscale_route_performance",
                    "legendFormat": "Route {{route_name}}",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 8, "x": 8, "y": 24},
            "yAxes": [
                {
                    "label": "Performance Score",
                    "logBase": 1,
                    "max": 100,
                    "min": 0,
                    "show": True,
                }
            ],
        }

    def _create_error_rates_panel(self) -> dict[str, Any]:
        """Create error rates panel."""
        return {
            "id": 10,
            "title": "Error Rates",
            "type": "graph",
            "targets": [
                {
                    "expr": "rate(tailscale_errors_total[5m])",
                    "legendFormat": "Errors/sec - {{error_type}}",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 24},
            "yAxes": [
                {
                    "label": "Errors/sec",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                }
            ],
        }

    def _create_historical_uptime_panel(self) -> dict[str, Any]:
        """Create historical uptime panel."""
        return {
            "id": 11,
            "title": "Historical Uptime",
            "type": "graph",
            "targets": [
                {
                    "expr": "avg_over_time(tailscale_uptime_percentage[1h])",
                    "legendFormat": "Uptime %",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 32},
            "yAxes": [
                {
                    "label": "Uptime %",
                    "logBase": 1,
                    "max": 100,
                    "min": 0,
                    "show": True,
                    "unit": "percent",
                }
            ],
        }

    def _create_bandwidth_trends_panel(self) -> dict[str, Any]:
        """Create bandwidth trends panel."""
        return {
            "id": 12,
            "title": "Bandwidth Trends",
            "type": "graph",
            "targets": [
                {
                    "expr": "avg_over_time(rate(tailscale_bytes_total[5m])[1h])",
                    "legendFormat": "Avg Bandwidth",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 32},
            "yAxes": [
                {
                    "label": "Bytes/sec",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                }
            ],
        }

    def _create_device_growth_panel(self) -> dict[str, Any]:
        """Create device growth panel."""
        return {
            "id": 13,
            "title": "Device Growth",
            "type": "graph",
            "targets": [
                {
                    "expr": "tailscale_devices_total",
                    "legendFormat": "Total Devices",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 40},
            "yAxes": [
                {
                    "label": "Device Count",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                }
            ],
        }

    def _create_network_graph_panel(self) -> dict[str, Any]:
        """Create network graph visualization panel."""
        return {
            "id": 101,
            "title": "Network Graph",
            "type": "nodeGraph",
            "targets": [
                {"expr": "tailscale_network_topology", "format": "table", "refId": "A"}
            ],
            "gridPos": {"h": 12, "w": 24, "x": 0, "y": 0},
            "options": {
                "nodes": {"mainStatUnit": "short", "secondaryStatUnit": "short"},
                "edges": {"mainStatUnit": "short", "secondaryStatUnit": "short"},
            },
        }

    def _create_device_relationships_panel(self) -> dict[str, Any]:
        """Create device relationships panel."""
        return {
            "id": 102,
            "title": "Device Relationships",
            "type": "table",
            "targets": [
                {
                    "expr": "tailscale_device_connections",
                    "format": "table",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 12, "w": 12, "x": 0, "y": 12},
            "transformations": [
                {
                    "id": "organize",
                    "options": {
                        "renameByName": {
                            "device_a": "Device A",
                            "device_b": "Device B",
                            "connection_strength": "Connection Strength",
                            "latency": "Latency (ms)",
                        }
                    },
                }
            ],
        }

    def _create_route_map_panel(self) -> dict[str, Any]:
        """Create route map panel."""
        return {
            "id": 103,
            "title": "Route Map",
            "type": "geomap",
            "targets": [
                {"expr": "tailscale_route_map", "format": "table", "refId": "A"}
            ],
            "gridPos": {"h": 12, "w": 12, "x": 12, "y": 12},
            "options": {
                "basemap": {"type": "default"},
                "layers": [
                    {
                        "type": "markers",
                        "config": {
                            "style": {"color": {"fixed": "blue"}, "size": {"fixed": 5}}
                        },
                    }
                ],
            },
        }

    def _create_connectivity_matrix_panel(self) -> dict[str, Any]:
        """Create connectivity matrix panel."""
        return {
            "id": 104,
            "title": "Connectivity Matrix",
            "type": "heatmap",
            "targets": [
                {
                    "expr": "tailscale_connectivity_matrix",
                    "format": "heatmap",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 12, "w": 24, "x": 0, "y": 24},
            "heatmap": {"xAxis": {"show": True}, "yAxis": {"show": True}},
        }

    def _create_acl_overview_panel(self) -> dict[str, Any]:
        """Create ACL overview panel."""
        return {
            "id": 201,
            "title": "ACL Overview",
            "type": "stat",
            "targets": [
                {
                    "expr": "tailscale_acl_rules_total",
                    "legendFormat": "Total ACL Rules",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 10},
                            {"color": "red", "value": 50},
                        ]
                    },
                }
            },
        }

    def _create_access_patterns_panel(self) -> dict[str, Any]:
        """Create access patterns panel."""
        return {
            "id": 202,
            "title": "Access Patterns",
            "type": "graph",
            "targets": [
                {
                    "expr": "rate(tailscale_access_attempts_total[5m])",
                    "legendFormat": "Access Attempts/sec - {{user}}",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0},
            "yAxes": [
                {
                    "label": "Attempts/sec",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True,
                }
            ],
        }

    def _create_security_alerts_panel(self) -> dict[str, Any]:
        """Create security alerts panel."""
        return {
            "id": 203,
            "title": "Security Alerts",
            "type": "table",
            "targets": [
                {"expr": "tailscale_security_alerts", "format": "table", "refId": "A"}
            ],
            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
            "transformations": [
                {
                    "id": "organize",
                    "options": {
                        "renameByName": {
                            "alert_type": "Alert Type",
                            "severity": "Severity",
                            "timestamp": "Time",
                            "description": "Description",
                        }
                    },
                }
            ],
        }

    def _create_device_trust_panel(self) -> dict[str, Any]:
        """Create device trust panel."""
        return {
            "id": 204,
            "title": "Device Trust Levels",
            "type": "piechart",
            "targets": [
                {
                    "expr": "tailscale_device_trust_levels",
                    "format": "table",
                    "refId": "A",
                }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            "options": {
                "pieType": "pie",
                "displayLabels": ["name", "value"],
                "legend": {
                    "displayMode": "table",
                    "placement": "right",
                    "values": ["value"],
                },
            },
        }

    def export_dashboard_json(
        self, dashboard_config: dict[str, Any], filename: str
    ) -> None:
        """Export dashboard configuration to JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(dashboard_config, f, indent=2)

            logger.info("Dashboard exported to JSON", filename=filename)

        except Exception as e:
            logger.error("Error exporting dashboard", filename=filename, error=str(e))
            raise TailscaleMCPError(f"Failed to export dashboard: {e}") from e

    def get_dashboard_summary(self, dashboard_config: dict[str, Any]) -> dict[str, Any]:
        """Get dashboard configuration summary."""
        dashboard = dashboard_config.get("dashboard", {})

        return {
            "title": dashboard.get("title", "Unknown"),
            "description": dashboard.get("description", ""),
            "tags": dashboard.get("tags", []),
            "panels_count": len(dashboard.get("panels", [])),
            "refresh_interval": dashboard.get("refresh", "unknown"),
            "time_range": dashboard.get("time", {}),
            "schema_version": dashboard.get("schemaVersion", "unknown"),
            "version": dashboard.get("version", "unknown"),
        }
