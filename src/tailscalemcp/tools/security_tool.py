"""Tailscale Security tool module."""

import time
from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_security_tool(ctx: ToolContext) -> None:
    """Register the tailscale_security tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_security(
        operation: str,
        scan_type: str = "comprehensive",
        compliance_standard: str = "SOC2",
        device_id: str | None = None,
        ip_address: str | None = None,
        quarantine_duration: int = 24,
        alert_severity: str = "medium",
        alert_message: str | None = None,
        policy_name: str | None = None,
        rules: list[dict[str, Any]] | None = None,
        priority: int = 100,
        test_mode: bool = False,
        block_duration: int = 3600,
        threat_type: str | None = None,
    ) -> dict[str, Any]:
        try:
            if operation == "scan":
                scan_results = await ctx.device_manager.security_scan(scan_type)
                return {
                    "operation": "scan",
                    "scan_type": scan_type,
                    "results": scan_results,
                    "vulnerabilities_found": len(
                        scan_results.get("vulnerabilities", [])
                    ),
                }

            elif operation == "compliance":
                compliance_results = await ctx.device_manager.check_compliance(
                    compliance_standard
                )
                return {
                    "operation": "compliance",
                    "standard": compliance_standard,
                    "results": compliance_results,
                    "compliant": compliance_results.get("compliant", False),
                }

            elif operation == "audit":
                # Use AuditOperations for comprehensive device audit
                # device_id is optional - if not provided, audit all devices
                filters = {}
                if device_id:
                    # Note: AuditOperations.audit_devices doesn't support device_id filter directly
                    # We'll audit all devices and filter in post-processing if needed
                    pass
                audit_results = await ctx.audit_ops.audit_devices(filters=filters)
                if device_id:
                    # Filter results to specific device if provided
                    audit_results["issues"] = [
                        issue
                        for issue in audit_results.get("issues", [])
                        if issue.get("device_id") == device_id
                    ]
                return {
                    "operation": "audit",
                    "device_id": device_id,
                    "results": audit_results,
                    "issue_count": audit_results.get("issue_count", 0),
                }

            elif operation == "report":
                security_report = await ctx.device_manager.generate_security_report()
                return {
                    "operation": "report",
                    "report": security_report,
                    "generated_at": time.time(),
                }

            elif operation == "monitor":
                suspicious_activity = (
                    await ctx.device_manager.monitor_suspicious_activity()
                )
                return {
                    "operation": "monitor",
                    "activity": suspicious_activity,
                    "alerts_generated": len(suspicious_activity.get("alerts", [])),
                }

            elif operation == "block":
                if not ip_address:
                    raise TailscaleMCPError(
                        "ip_address is required for block operation"
                    )
                result = await ctx.device_manager.block_malicious_ip(
                    ip_address, block_duration
                )
                return {
                    "operation": "block",
                    "ip_address": ip_address,
                    "block_duration": block_duration,
                    "result": result,
                }

            elif operation == "quarantine":
                if not device_id:
                    raise TailscaleMCPError(
                        "device_id is required for quarantine operation"
                    )
                result = await ctx.device_manager.quarantine_device(
                    device_id, quarantine_duration
                )
                return {
                    "operation": "quarantine",
                    "device_id": device_id,
                    "quarantine_duration": quarantine_duration,
                    "result": result,
                }

            elif operation == "alert":
                if not alert_message:
                    raise TailscaleMCPError(
                        "alert_message is required for alert operation"
                    )
                result = await ctx.device_manager.alert_on_breach(
                    alert_severity, alert_message
                )
                return {
                    "operation": "alert",
                    "severity": alert_severity,
                    "message": alert_message,
                    "result": result,
                }

            elif operation == "policy":
                if not policy_name or not rules:
                    raise TailscaleMCPError(
                        "policy_name and rules are required for policy operation"
                    )
                result = await ctx.device_manager.create_security_policy(
                    policy_name, rules, priority
                )
                return {
                    "operation": "policy_create",
                    "policy_name": policy_name,
                    "rules": rules,
                    "priority": priority,
                    "result": result,
                }

            elif operation == "threat":
                if not threat_type:
                    raise TailscaleMCPError(
                        "threat_type is required for threat operation"
                    )
                result = await ctx.device_manager.detect_threat(threat_type, test_mode)
                return {
                    "operation": "threat_detect",
                    "threat_type": threat_type,
                    "test_mode": test_mode,
                    "result": result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_security operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to perform security operation: {e}") from e
