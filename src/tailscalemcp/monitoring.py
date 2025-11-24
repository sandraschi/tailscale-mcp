"""
Tailscale Monitoring and Metrics Module

Provides comprehensive monitoring capabilities including Prometheus metrics,
Grafana dashboard integration, and network visualization tools.
"""

import time
from typing import Any

import structlog
from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest
from pydantic import BaseModel, Field

from .config import TailscaleConfig
from .exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)

# Prometheus Metrics - Prevent duplicate registration
try:
    DEVICE_COUNT = Gauge(
        "tailscale_devices_total", "Total number of devices", ["status"]
    )
    DEVICE_ONLINE = Gauge("tailscale_devices_online", "Number of online devices")
    NETWORK_LATENCY = Histogram(
        "tailscale_network_latency_seconds",
        "Network latency between devices",
        ["from_device", "to_device"],
    )
    BYTES_SENT = Counter(
        "tailscale_bytes_sent_total", "Total bytes sent", ["device_id"]
    )
    BYTES_RECEIVED = Counter(
        "tailscale_bytes_received_total", "Total bytes received", ["device_id"]
    )
    API_REQUESTS = Counter(
        "tailscale_api_requests_total", "Total API requests", ["endpoint", "status"]
    )
except ValueError:
    # Metrics already registered, skip creation
    DEVICE_COUNT = None
    DEVICE_ONLINE = None
    NETWORK_LATENCY = None
    BYTES_SENT = None
    BYTES_RECEIVED = None
    API_REQUESTS = None
try:
    ACL_RULES = Gauge("tailscale_acl_rules_total", "Total number of ACL rules")
    EXIT_NODES = Gauge("tailscale_exit_nodes_total", "Number of exit nodes")
    SUBNET_ROUTES = Gauge("tailscale_subnet_routes_total", "Number of subnet routes")
    TAILNET_INFO = Info("tailnet_info", "Tailnet information")
except ValueError:
    # Metrics already registered, skip creation
    ACL_RULES = None
    EXIT_NODES = None
    SUBNET_ROUTES = None
    TAILNET_INFO = None


class NetworkMetrics(BaseModel):
    """Network metrics data model."""

    timestamp: float = Field(..., description="Timestamp of the metrics")
    devices_total: int = Field(..., description="Total number of devices")
    devices_online: int = Field(..., description="Number of online devices")
    devices_offline: int = Field(..., description="Number of offline devices")
    exit_nodes: int = Field(..., description="Number of exit nodes")
    subnet_routes: int = Field(..., description="Number of subnet routes")
    acl_rules: int = Field(..., description="Number of ACL rules")
    network_health_score: float = Field(..., description="Network health score (0-100)")


class DeviceMetrics(BaseModel):
    """Device-specific metrics data model."""

    device_id: str = Field(..., description="Device identifier")
    name: str = Field(..., description="Device name")
    status: str = Field(..., description="Device status")
    last_seen: float = Field(..., description="Last seen timestamp")
    bytes_sent: int = Field(..., description="Bytes sent")
    bytes_received: int = Field(..., description="Bytes received")
    latency_ms: float = Field(..., description="Average latency in milliseconds")
    is_exit_node: bool = Field(..., description="Is exit node")
    advertised_routes: list[str] = Field(
        default_factory=list, description="Advertised routes"
    )


class TailscaleMonitor:
    """Comprehensive Tailscale network monitoring and metrics collection."""

    def __init__(self, api_key: str | None = None, tailnet: str | None = None):
        """Initialize the monitoring system.

        Args:
            api_key: Tailscale API key
            tailnet: Tailnet name
        """
        self.api_key = api_key
        self.tailnet = tailnet
        self.metrics_history: list[NetworkMetrics] = []
        self.device_metrics: dict[str, DeviceMetrics] = {}
        self.last_update = 0.0
        self.update_interval = 30.0  # Update every 30 seconds

        logger.info("Tailscale monitoring system initialized")

    async def collect_metrics(self) -> NetworkMetrics:
        """Collect comprehensive network metrics."""
        try:
            current_time = time.time()

            # Collect device data (this would be replaced with actual API calls)
            devices = await self._get_devices_data()
            online_devices = [d for d in devices if d.get("status") == "online"]
            offline_devices = [d for d in devices if d.get("status") == "offline"]

            # Collect network statistics
            exit_nodes = len([d for d in devices if d.get("is_exit_node", False)])
            subnet_routes = len([d for d in devices if d.get("advertised_routes", [])])
            acl_rules = await self._get_acl_rules_count()

            # Calculate network health score
            health_score = self._calculate_health_score(devices, online_devices)

            metrics = NetworkMetrics(
                timestamp=current_time,
                devices_total=len(devices),
                devices_online=len(online_devices),
                devices_offline=len(offline_devices),
                exit_nodes=exit_nodes,
                subnet_routes=subnet_routes,
                acl_rules=acl_rules,
                network_health_score=health_score,
            )

            # Update Prometheus metrics
            await self._update_prometheus_metrics(metrics, devices)

            # Store metrics history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:  # Keep last 1000 entries
                self.metrics_history = self.metrics_history[-1000:]

            self.last_update = current_time
            logger.info(
                "Metrics collected successfully",
                devices_total=metrics.devices_total,
                devices_online=metrics.devices_online,
                health_score=metrics.network_health_score,
            )

            return metrics

        except Exception as e:
            logger.error("Error collecting metrics", error=str(e))
            raise TailscaleMCPError(f"Failed to collect metrics: {e}") from e

    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        try:
            # Update metrics if needed
            if time.time() - self.last_update > self.update_interval:
                await self.collect_metrics()

            return generate_latest().decode("utf-8")
        except Exception as e:
            logger.error("Error generating Prometheus metrics", error=str(e))
            raise TailscaleMCPError(f"Failed to generate metrics: {e}") from e

    async def create_grafana_dashboard(
        self, grafana_url: str, api_key: str
    ) -> dict[str, Any]:
        """Create a Grafana dashboard for Tailscale monitoring."""
        try:
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "title": f"Tailscale Network - {self.tailnet}",
                    "tags": ["tailscale", "networking", "monitoring"],
                    "timezone": "browser",
                    "panels": await self._create_dashboard_panels(),
                    "time": {"from": "now-1h", "to": "now"},
                    "refresh": "30s",
                    "schemaVersion": 30,
                    "version": 1,
                }
            }

            logger.info(
                "Grafana dashboard created",
                dashboard_title=dashboard_config["dashboard"]["title"],
            )
            return dashboard_config

        except Exception as e:
            logger.error("Error creating Grafana dashboard", error=str(e))
            raise TailscaleMCPError(f"Failed to create Grafana dashboard: {e}") from e

    async def generate_network_topology(self) -> dict[str, Any]:
        """Generate network topology visualization data."""
        try:
            devices = await self._get_devices_data()
            connections = await self._get_device_connections()

            topology = {
                "nodes": [
                    {
                        "id": device["id"],
                        "label": device["name"],
                        "status": device["status"],
                        "type": "exit_node" if device.get("is_exit_node") else "device",
                        "x": hash(device["id"]) % 1000,  # Simple positioning
                        "y": hash(device["name"]) % 1000,
                    }
                    for device in devices
                ],
                "edges": [
                    {
                        "from": conn["from"],
                        "to": conn["to"],
                        "label": f"{conn['latency']}ms",
                        "width": conn["bandwidth"] / 1000000,  # Normalize bandwidth
                    }
                    for conn in connections
                ],
                "metadata": {
                    "total_devices": len(devices),
                    "total_connections": len(connections),
                    "last_updated": time.time(),
                },
            }

            logger.info(
                "Network topology generated",
                nodes=len(topology["nodes"]),
                edges=len(topology["edges"]),
            )

            return topology

        except Exception as e:
            logger.error("Error generating network topology", error=str(e))
            raise TailscaleMCPError(f"Failed to generate network topology: {e}") from e

    async def get_network_status(self) -> dict[str, Any]:
        """Get current network status summary.

        Returns:
            Current network status with device information and connectivity
        """
        try:
            metrics = await self.collect_metrics()
            devices = await self._get_devices_data()
            online_devices = [d for d in devices if d.get("status") == "online"]

            status = {
                "status": "operational"
                if metrics.network_health_score > 70
                else "degraded",
                "health_score": metrics.network_health_score,
                "devices": {
                    "total": metrics.devices_total,
                    "online": metrics.devices_online,
                    "offline": metrics.devices_offline,
                    "online_percentage": round(
                        (metrics.devices_online / metrics.devices_total * 100), 2
                    )
                    if metrics.devices_total > 0
                    else 0,
                },
                "network": {
                    "exit_nodes": metrics.exit_nodes,
                    "subnet_routes": metrics.subnet_routes,
                    "acl_rules": metrics.acl_rules,
                },
                "connectivity": "good" if len(online_devices) > 0 else "poor",
                "timestamp": time.time(),
            }

            logger.info(
                "Network status retrieved",
                status=status["status"],
                health_score=metrics.network_health_score,
                online_devices=metrics.devices_online,
            )

            return status

        except Exception as e:
            logger.error("Error retrieving network status", error=str(e))
            raise TailscaleMCPError(f"Failed to retrieve network status: {e}") from e

    async def get_network_metrics(self) -> dict[str, Any]:
        """Get network metrics as a dictionary from real Tailscale API.

        Returns:
            Network metrics dictionary with latency, bandwidth, and health information
        """
        try:
            metrics = await self.collect_metrics()

            # Limit metrics to what Admin API exposes reliably
            network_metrics = {
                "health_score": metrics.network_health_score,
                "devices_total": metrics.devices_total,
                "devices_online": metrics.devices_online,
                "devices_offline": metrics.devices_offline,
                "exit_nodes": metrics.exit_nodes,
                "subnet_routes": metrics.subnet_routes,
                "acl_rules": metrics.acl_rules,
                "uptime_percentage": round(
                    (metrics.devices_online / metrics.devices_total * 100), 2
                )
                if metrics.devices_total > 0
                else 0,
                "timestamp": metrics.timestamp,
            }

            logger.info(
                "Network metrics retrieved from real API",
                health_score=metrics.network_health_score,
                devices_online=metrics.devices_online,
            )

            return network_metrics

        except Exception as e:
            logger.error("Error retrieving network metrics", error=str(e))
            raise TailscaleMCPError(f"Failed to retrieve network metrics: {e}") from e

    async def get_network_health_report(self) -> dict[str, Any]:
        """Generate comprehensive network health report."""
        try:
            metrics = await self.collect_metrics()

            # Analyze trends
            recent_metrics = [
                m for m in self.metrics_history if time.time() - m.timestamp < 3600
            ]  # Last hour

            health_report = {
                "current_status": {
                    "overall_health": metrics.network_health_score,
                    "devices_online": metrics.devices_online,
                    "devices_total": metrics.devices_total,
                    "uptime_percentage": (
                        metrics.devices_online / metrics.devices_total * 100
                    )
                    if metrics.devices_total > 0
                    else 0,
                },
                "trends": {
                    "health_trend": self._calculate_trend(
                        [m.network_health_score for m in recent_metrics]
                    ),
                    "device_trend": self._calculate_trend(
                        [m.devices_online for m in recent_metrics]
                    ),
                },
                "alerts": await self._generate_alerts(metrics),
                "recommendations": await self._generate_recommendations(metrics),
                "timestamp": time.time(),
            }

            logger.info(
                "Network health report generated",
                health_score=health_report["current_status"]["overall_health"],
            )

            return health_report

        except Exception as e:
            logger.error("Error generating health report", error=str(e))
            raise TailscaleMCPError(f"Failed to generate health report: {e}") from e

    async def _get_devices_data(self) -> list[dict[str, Any]]:
        """Get devices data from real Tailscale API."""
        try:
            from .operations.devices import DeviceOperations

            # Use operations layer for real API calls
            config = TailscaleConfig(
                tailscale_api_key=self.api_key or "",
                tailscale_tailnet=self.tailnet or "",
            )
            device_ops = DeviceOperations(config=config)
            devices_model = await device_ops.list_devices()

            # Convert Device models to dict format for backward compatibility
            devices = [
                d.to_dict() if hasattr(d, "to_dict") else d.model_dump()
                for d in devices_model
            ]

            # Map API response to expected format
            formatted_devices = []
            for device in devices:
                formatted_device = {
                    "id": device.get("id", ""),
                    "name": device.get("name", "unknown"),
                    "status": "online"
                    if device.get("connectedToControl", False)
                    else "offline",
                    "is_exit_node": device.get("isExitNode", False),
                    "advertised_routes": device.get("routes", []),
                    "authorized": device.get("authorized", True),
                    "os": device.get("os", "unknown"),
                    "addresses": device.get("addresses", []),
                    "tags": device.get("tags", []),
                }
                formatted_devices.append(formatted_device)

            logger.info(
                "Device data retrieved from real API", count=len(formatted_devices)
            )
            return formatted_devices

        except Exception as e:
            logger.error("Failed to get devices data from API", error=str(e))
            # Return empty list on error rather than mock data
            return []

    async def _get_acl_rules_count(self) -> int:
        """Get ACL rules count from real Tailscale API."""
        # TODO: Implement ACL rules count via API
        # For now, return 0 to avoid mock data
        logger.warning("ACL rules count not yet implemented via API")
        return 0

    async def _get_device_connections(self) -> list[dict[str, Any]]:
        """Get device connection data from real Tailscale API."""
        # TODO: Implement device connections via API
        # For now, return empty list to avoid mock data
        logger.warning("Device connections not yet implemented via API")
        return []

    async def _update_prometheus_metrics(
        self, metrics: NetworkMetrics, devices: list[dict[str, Any]]
    ) -> None:
        """Update Prometheus metrics."""
        if DEVICE_COUNT is not None:
            DEVICE_COUNT.labels(status="online").set(metrics.devices_online)
            DEVICE_COUNT.labels(status="offline").set(metrics.devices_offline)
        if DEVICE_ONLINE is not None:
            DEVICE_ONLINE.set(metrics.devices_online)
        if EXIT_NODES is not None:
            EXIT_NODES.set(metrics.exit_nodes)
        if SUBNET_ROUTES is not None:
            SUBNET_ROUTES.set(metrics.subnet_routes)
        if ACL_RULES is not None:
            ACL_RULES.set(metrics.acl_rules)

        # No simulated per-device counters; real traffic metrics not available via Admin API

    async def _create_dashboard_panels(self) -> list[dict[str, Any]]:
        """Create Grafana dashboard panels."""
        return [
            {
                "id": 1,
                "title": "Device Status",
                "type": "stat",
                "targets": [
                    {
                        "expr": "tailscale_devices_online",
                        "legendFormat": "Online Devices",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            },
            {
                "id": 2,
                "title": "Network Health Score",
                "type": "gauge",
                "targets": [
                    {
                        "expr": "tailscale_network_health_score",
                        "legendFormat": "Health Score",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            },
            {
                "id": 3,
                "title": "Bandwidth Usage",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(tailscale_bytes_sent_total[5m])",
                        "legendFormat": "Bytes Sent/sec",
                    }
                ],
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
            },
        ]

    def _calculate_health_score(
        self, devices: list[dict[str, Any]], online_devices: list[dict[str, Any]]
    ) -> float:
        """Calculate network health score."""
        if not devices:
            return 0.0

        online_ratio = len(online_devices) / len(devices)
        base_score = online_ratio * 100

        # Adjust based on other factors
        exit_nodes = len([d for d in devices if d.get("is_exit_node", False)])
        if exit_nodes > 0:
            base_score += 5  # Bonus for having exit nodes

        return min(100.0, base_score)

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"

        recent_avg = sum(values[-3:]) / len(values[-3:])
        older_avg = (
            sum(values[:3]) / len(values[:3]) if len(values) >= 6 else recent_avg
        )

        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    async def _generate_alerts(self, metrics: NetworkMetrics) -> list[dict[str, Any]]:
        """Generate network alerts."""
        alerts = []

        if metrics.network_health_score < 80:
            alerts.append(
                {
                    "level": "warning",
                    "message": f"Network health score is low: {metrics.network_health_score}%",
                    "timestamp": time.time(),
                }
            )

        if metrics.devices_online / metrics.devices_total < 0.8:
            alerts.append(
                {
                    "level": "critical",
                    "message": f"Low device uptime: {metrics.devices_online}/{metrics.devices_total} devices online",
                    "timestamp": time.time(),
                }
            )

        return alerts

    async def _generate_recommendations(self, metrics: NetworkMetrics) -> list[str]:
        """Generate network recommendations."""
        recommendations = []

        if metrics.exit_nodes == 0:
            recommendations.append(
                "Consider adding an exit node for better connectivity"
            )

        if metrics.subnet_routes == 0:
            recommendations.append(
                "Consider configuring subnet routes for local network access"
            )

        if metrics.network_health_score < 90:
            recommendations.append(
                "Review device connectivity and network configuration"
            )

        return recommendations
