"""
Reporting operations service layer.

Provides report generation and export functionality.
"""

import json
from datetime import datetime
from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class ReportingOperations:
    """Service layer for reporting and export operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize reporting operations.

        Args:
            config: Configuration object (if provided, api_key and tailnet are ignored)
            api_key: Tailscale API key (optional if config provided)
            tailnet: Tailnet name (optional if config provided)
        """
        if config:
            self.config = config
        else:
            self.config = TailscaleConfig(
                tailscale_api_key=api_key or "",
                tailscale_tailnet=tailnet or "",
            )
        self.client = TailscaleAPIClient(self.config)

    async def generate_network_report(
        self, format: str = "json"
    ) -> dict[str, Any] | str:
        """Generate comprehensive network state report.

        Args:
            format: Report format - "json" or "html"

        Returns:
            Network report in specified format
        """
        try:
            from tailscalemcp.operations.analytics import AnalyticsOperations
            from tailscalemcp.operations.devices import DeviceOperations
            from tailscalemcp.operations.policies import PolicyOperations

            device_ops = DeviceOperations(self.config)
            analytics_ops = AnalyticsOperations(self.config)
            policy_ops = PolicyOperations(self.config)

            # Gather data
            devices = await device_ops.list_devices()
            analytics = await analytics_ops.get_network_statistics()
            policy = await policy_ops.get_policy()

            # Build report
            report = {
                "report_type": "network_state",
                "generated_at": datetime.now(
                    datetime.now().astimezone().tzinfo
                ).isoformat(),
                "tailnet": self.config.tailscale_tailnet,
                "summary": {
                    "total_devices": len(devices),
                    "online_devices": analytics["online_devices"],
                    "offline_devices": analytics["offline_devices"],
                    "policy_rules_count": len(policy.acls),
                },
                "devices": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "status": d.status.value,
                        "authorized": d.authorized,
                        "os": d.os,
                        "tags": d.tags,
                        "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                    }
                    for d in devices
                ],
                "policy_summary": {
                    "hosts_count": len(policy.hosts),
                    "users_count": len(policy.users),
                    "tags_count": len(policy.tags),
                    "rules_count": len(policy.acls),
                },
                "statistics": analytics,
            }

            if format == "html":
                return self._format_html_report(report)
            else:
                return report

        except Exception as e:
            logger.error("Error generating network report", error=str(e))
            raise TailscaleMCPError(f"Failed to generate network report: {e}") from e

    def _format_html_report(self, report: dict[str, Any]) -> str:
        """Format report as HTML.

        Args:
            report: Report data dictionary

        Returns:
            HTML formatted report
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tailscale Network Report - {report["generated_at"]}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Tailscale Network Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Tailnet:</strong> {report["tailnet"]}</p>
                <p><strong>Generated:</strong> {report["generated_at"]}</p>
                <p><strong>Total Devices:</strong> {report["summary"]["total_devices"]}</p>
                <p><strong>Online Devices:</strong> {report["summary"]["online_devices"]}</p>
                <p><strong>Offline Devices:</strong> {report["summary"]["offline_devices"]}</p>
                <p><strong>Policy Rules:</strong> {report["summary"]["policy_rules_count"]}</p>
            </div>
            <h2>Devices</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>OS</th>
                    <th>Authorized</th>
                    <th>Tags</th>
                </tr>
        """

        for device in report["devices"]:
            tags_str = ", ".join(device["tags"]) if device["tags"] else "None"
            html += f"""
                <tr>
                    <td>{device["name"]}</td>
                    <td>{device["status"]}</td>
                    <td>{device["os"]}</td>
                    <td>{"Yes" if device["authorized"] else "No"}</td>
                    <td>{tags_str}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """
        return html

    async def export_devices(
        self, format: str = "json", filters: dict[str, Any] | None = None
    ) -> str:
        """Export device registry to specified format.

        Args:
            format: Export format - "json" or "csv"
            filters: Optional device filters

        Returns:
            Exported data as string
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            devices = await device_ops.list_devices()

            # Apply filters if provided
            if filters:
                if filters.get("online_only"):
                    devices = [d for d in devices if d.status.value == "online"]
                if filters.get("authorized_only"):
                    devices = [d for d in devices if d.authorized]

            if format == "csv":
                csv_lines = [
                    "device_id,name,hostname,os,status,authorized,tags,ipv4,last_seen"
                ]
                for device in devices:
                    tags_str = ";".join(device.tags) if device.tags else ""
                    last_seen_str = (
                        device.last_seen.isoformat() if device.last_seen else ""
                    )
                    csv_lines.append(
                        f'"{device.id}","{device.name}","{device.hostname}","{device.os}",'
                        f'"{device.status.value}","{device.authorized}","{tags_str}",'
                        f'"{device.ipv4 or ""}","{last_seen_str}"'
                    )
                return "\n".join(csv_lines)

            else:  # JSON
                export_data = {
                    "exported_at": datetime.now(
                        datetime.now().astimezone().tzinfo
                    ).isoformat(),
                    "device_count": len(devices),
                    "devices": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "hostname": d.hostname,
                            "os": d.os,
                            "status": d.status.value,
                            "authorized": d.authorized,
                            "tags": d.tags,
                            "ipv4": d.ipv4,
                            "last_seen": d.last_seen.isoformat()
                            if d.last_seen
                            else None,
                        }
                        for d in devices
                    ],
                }
                return json.dumps(export_data, indent=2)

        except Exception as e:
            logger.error("Error exporting devices", error=str(e))
            raise TailscaleMCPError(f"Failed to export devices: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
