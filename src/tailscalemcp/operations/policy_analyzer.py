"""
Policy analyzer operations service layer.

Provides ACL policy analysis, validation, and reporting.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class PolicyAnalyzer:
    """Service layer for ACL policy analysis operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize policy analyzer.

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

    async def analyze_policy(self) -> dict[str, Any]:
        """Analyze current ACL policy and generate insights.

        Returns:
            Policy analysis report with statistics and recommendations
        """
        try:
            from tailscalemcp.operations.policies import PolicyOperations

            policy_ops = PolicyOperations(self.config)
            policy = await policy_ops.get_policy()

            # Analyze policy structure
            analysis: dict[str, Any] = {
                "hosts_count": len(policy.hosts),
                "users_count": len(policy.users),
                "tags_count": len(policy.tags),
                "groups_count": len(policy.groups),
                "acl_rules_count": len(policy.acls),
                "accept_rules": 0,
                "reject_rules": 0,
                "rules_with_src": 0,
                "rules_with_dst": 0,
                "wildcard_rules": 0,
                "recommendations": [],
            }

            # Analyze ACL rules
            for rule in policy.acls:
                if rule.action == "accept":
                    analysis["accept_rules"] += 1
                elif rule.action == "reject":
                    analysis["reject_rules"] += 1

                if rule.src:
                    analysis["rules_with_src"] += 1
                    if "*" in rule.src:
                        analysis["wildcard_rules"] += 1

                if rule.dst:
                    analysis["rules_with_dst"] += 1
                    if "*" in rule.dst:
                        analysis["wildcard_rules"] += 1

            # Generate recommendations
            if analysis["wildcard_rules"] > analysis["acl_rules_count"] * 0.5:
                analysis["recommendations"].append(
                    {
                        "type": "security",
                        "severity": "medium",
                        "message": "High number of wildcard rules detected. Consider more specific rules for better security.",
                    }
                )

            if analysis["acl_rules_count"] == 0:
                analysis["recommendations"].append(
                    {
                        "type": "configuration",
                        "severity": "high",
                        "message": "No ACL rules defined. Default policy applies.",
                    }
                )

            if analysis["tags_count"] == 0 and analysis["users_count"] > 5:
                analysis["recommendations"].append(
                    {
                        "type": "best_practice",
                        "severity": "low",
                        "message": "Consider using tags for device grouping instead of individual user rules.",
                    }
                )

            logger.info("Policy analyzed", rules_count=analysis["acl_rules_count"])
            return analysis

        except Exception as e:
            logger.error("Error analyzing policy", error=str(e))
            raise TailscaleMCPError(f"Failed to analyze policy: {e}") from e

    async def find_affected_devices(
        self, rule_action: str | None = None
    ) -> dict[str, Any]:
        """Find devices affected by ACL policy rules.

        Args:
            rule_action: Filter by rule action (accept/reject), or None for all

        Returns:
            Report of devices and their access capabilities
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations
            from tailscalemcp.operations.policies import PolicyOperations

            policy_ops = PolicyOperations(self.config)
            policy = await policy_ops.get_policy()

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            # Filter rules by action if specified
            rules_to_check = policy.acls
            if rule_action:
                rules_to_check = [r for r in rules_to_check if r.action == rule_action]

            # Map devices to their access
            device_access: dict[str, dict[str, Any]] = {}

            for device in all_devices:
                device_access[device.id] = {
                    "device_id": device.id,
                    "device_name": device.name,
                    "tags": device.tags,
                    "affected_by_rules": [],
                }

                # Check which rules apply to this device
                for rule in rules_to_check:
                    applies = False

                    # Check if device tags match rule source
                    if rule.src:
                        for src in rule.src:
                            if "*" in src or any(tag in src for tag in device.tags):
                                applies = True
                                break

                    if applies:
                        device_access[device.id]["affected_by_rules"].append(
                            {
                                "action": rule.action,
                                "src": rule.src,
                                "dst": rule.dst,
                            }
                        )

            result = {
                "total_devices": len(all_devices),
                "devices_affected": len(
                    [d for d in device_access.values() if d["affected_by_rules"]]
                ),
                "device_access_map": device_access,
                "rule_action_filter": rule_action,
            }

            logger.info(
                "Affected devices found",
                total_devices=len(all_devices),
                affected=result["devices_affected"],
            )
            return result

        except Exception as e:
            logger.error("Error finding affected devices", error=str(e))
            raise TailscaleMCPError(f"Failed to find affected devices: {e}") from e

    async def query_policy(self, query: dict[str, Any]) -> dict[str, Any]:
        """Query policy to find rules matching specific criteria.

        Args:
            query: Query criteria:
                - action: Rule action to match
                - src_contains: Source must contain this string
                - dst_contains: Destination must contain this string
                - has_src: Rule must have source specified
                - has_dst: Rule must have destination specified

        Returns:
            Matching rules and statistics
        """
        try:
            from tailscalemcp.operations.policies import PolicyOperations

            policy_ops = PolicyOperations(self.config)
            policy = await policy_ops.get_policy()

            matching_rules: list[dict[str, Any]] = []

            for rule in policy.acls:
                match = True

                if query.get("action") and rule.action != query["action"]:
                    match = False

                if query.get("src_contains") and (
                    not rule.src
                    or not any(query["src_contains"] in src for src in rule.src)
                ):
                    match = False

                if query.get("dst_contains") and (
                    not rule.dst
                    or not any(query["dst_contains"] in dst for dst in rule.dst)
                ):
                    match = False

                if query.get("has_src") and not rule.src:
                    match = False

                if query.get("has_dst") and not rule.dst:
                    match = False

                if match:
                    matching_rules.append(
                        {
                            "action": rule.action,
                            "src": rule.src,
                            "dst": rule.dst,
                        }
                    )

            result = {
                "query": query,
                "matches": len(matching_rules),
                "matching_rules": matching_rules,
            }

            logger.info("Policy queried", matches=len(matching_rules))
            return result

        except Exception as e:
            logger.error("Error querying policy", error=str(e))
            raise TailscaleMCPError(f"Failed to query policy: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
