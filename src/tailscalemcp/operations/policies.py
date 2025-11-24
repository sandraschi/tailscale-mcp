"""
ACL Policy operations service layer.

Provides advanced ACL policy management including validation, testing, and rollback.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError, ValidationError
from tailscalemcp.models.policy import ACLPolicy

logger = structlog.get_logger(__name__)


class PolicyOperations:
    """Service layer for advanced ACL policy operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize policy operations.

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
        self._previous_policy: dict[str, Any] | None = None

    async def get_policy(self) -> ACLPolicy:
        """Get the current ACL policy as a model.

        Returns:
            ACLPolicy model instance

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            policy_data = await self.client.get_acl_policy()
            policy = ACLPolicy.from_api_response(policy_data)
            logger.info("ACL policy retrieved as model")
            return policy

        except Exception as e:
            logger.error("Error getting ACL policy", error=str(e))
            raise TailscaleMCPError(f"Failed to get ACL policy: {e}") from e

    async def validate_policy(
        self, policy: dict[str, Any] | ACLPolicy
    ) -> dict[str, Any]:
        """Validate ACL policy syntax and structure before deployment.

        Args:
            policy: Policy dictionary or ACLPolicy model

        Returns:
            Validation result with status and any errors/warnings

        Raises:
            ValidationError: If policy is invalid
            TailscaleMCPError: If validation process fails
        """
        try:
            # Convert to dict if it's a model
            policy_dict = policy.to_dict() if isinstance(policy, ACLPolicy) else policy

            errors: list[str] = []
            warnings: list[str] = []

            # Basic structure validation
            required_sections = ["Hosts", "Users", "Tags", "ACLs", "Groups"]
            for section in required_sections:
                if section not in policy_dict:
                    warnings.append(f"Missing optional section: {section}")

            # Validate ACLs
            if "ACLs" in policy_dict:
                if not isinstance(policy_dict["ACLs"], list):
                    errors.append("ACLs must be a list")
                else:
                    for i, acl in enumerate(policy_dict["ACLs"]):
                        if not isinstance(acl, dict):
                            errors.append(f"ACL rule {i} must be a dictionary")
                            continue

                        if "Action" not in acl:
                            errors.append(
                                f"ACL rule {i} missing required 'Action' field"
                            )
                        elif acl["Action"] not in ["accept", "reject"]:
                            warnings.append(
                                f"ACL rule {i} has non-standard action: {acl['Action']}"
                            )

                        if "Src" not in acl or not isinstance(acl["Src"], list):
                            errors.append(
                                f"ACL rule {i} missing or invalid 'Src' field"
                            )
                        if "Dst" not in acl or not isinstance(acl["Dst"], list):
                            errors.append(
                                f"ACL rule {i} missing or invalid 'Dst' field"
                            )

            # Validate dictionary structure
            for section in ["Hosts", "Users", "Tags", "Groups"]:
                if section in policy_dict and not isinstance(
                    policy_dict[section], dict
                ):
                    errors.append(f"{section} must be a dictionary")

            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
            }

            logger.info(
                "Policy validated",
                valid=result["valid"],
                error_count=len(errors),
                warning_count=len(warnings),
            )

            if errors:
                raise ValidationError(f"Policy validation failed: {', '.join(errors)}")

            return result

        except ValidationError:
            raise
        except Exception as e:
            logger.error("Error validating policy", error=str(e))
            raise TailscaleMCPError(f"Failed to validate policy: {e}") from e

    async def update_policy(
        self, policy: dict[str, Any] | ACLPolicy, validate: bool = True
    ) -> ACLPolicy:
        """Update ACL policy with optional validation and rollback support.

        Args:
            policy: Policy dictionary or ACLPolicy model
            validate: If True, validate policy before applying

        Returns:
            Updated ACLPolicy model

        Raises:
            ValidationError: If validation enabled and policy is invalid
            TailscaleMCPError: If API call fails
        """
        try:
            # Store previous policy for potential rollback
            try:
                current_policy = await self.client.get_acl_policy()
                self._previous_policy = current_policy
            except Exception:
                # If we can't get current policy, continue anyway
                logger.warning("Could not retrieve current policy for rollback")
                self._previous_policy = None

            # Convert to dict if it's a model
            policy_dict = policy.to_dict() if isinstance(policy, ACLPolicy) else policy

            # Validate if requested
            if validate:
                await self.validate_policy(policy_dict)

            # Apply policy
            updated_data = await self.client.update_acl_policy(policy_dict)
            updated_policy = ACLPolicy.from_api_response(updated_data)

            logger.info("ACL policy updated successfully")
            return updated_policy

        except (ValidationError, TailscaleMCPError):
            raise
        except Exception as e:
            logger.error("Error updating ACL policy", error=str(e))
            raise TailscaleMCPError(f"Failed to update ACL policy: {e}") from e

    async def rollback_policy(self) -> ACLPolicy:
        """Rollback to the previous ACL policy.

        Returns:
            Restored ACLPolicy model

        Raises:
            TailscaleMCPError: If no previous policy available or rollback fails
        """
        if not self._previous_policy:
            raise TailscaleMCPError(
                "No previous policy available for rollback. "
                "Policy must be updated through update_policy() first."
            )

        try:
            updated_data = await self.client.update_acl_policy(self._previous_policy)
            restored_policy = ACLPolicy.from_api_response(updated_data)
            self._previous_policy = None  # Clear after successful rollback

            logger.info("ACL policy rolled back successfully")
            return restored_policy

        except Exception as e:
            logger.error("Error rolling back ACL policy", error=str(e))
            raise TailscaleMCPError(f"Failed to rollback ACL policy: {e}") from e

    async def test_policy(
        self,
        policy: dict[str, Any] | ACLPolicy,
        test_scenario: dict[str, Any],
    ) -> dict[str, Any]:
        """Test ACL policy against a scenario without applying it.

        Args:
            policy: Policy dictionary or ACLPolicy model to test
            test_scenario: Test scenario with:
                - src: Source identifier (host, tag, or IP)
                - dst: Destination identifier (host, tag, or IP)
                - port: Destination port (optional)

        Returns:
            Test result with access decision and matched rules

        Raises:
            TailscaleMCPError: If testing fails
        """
        try:
            # Convert to model if needed
            if isinstance(policy, dict):
                policy_model = ACLPolicy.from_api_response(policy)
            else:
                policy_model = policy

            src = test_scenario.get("src", "")
            dst = test_scenario.get("dst", "")

            # Simple policy evaluation (this is a simplified version)
            # In a real implementation, you'd parse the policy more thoroughly
            matched_rules: list[dict[str, Any]] = []
            decision = "reject"  # Default deny

            for rule in policy_model.acls:
                # Check if source matches
                src_match = False
                if not rule.src or "*" in rule.src:
                    src_match = True
                else:
                    for rule_src in rule.src:
                        if src in rule_src or rule_src in src:
                            src_match = True
                            break

                # Check if destination matches
                dst_match = False
                if not rule.dst or "*" in rule.dst:
                    dst_match = True
                else:
                    for rule_dst in rule.dst:
                        if dst in rule_dst or rule_dst in dst:
                            dst_match = True
                            break

                if src_match and dst_match:
                    matched_rules.append(
                        {
                            "action": rule.action,
                            "src": rule.src,
                            "dst": rule.dst,
                        }
                    )
                    # Last matching rule wins (simplified)
                    decision = rule.action

            result = {
                "decision": decision,
                "matched_rules": matched_rules,
                "test_scenario": test_scenario,
            }

            logger.info(
                "Policy tested",
                decision=decision,
                matched_rules_count=len(matched_rules),
            )
            return result

        except Exception as e:
            logger.error("Error testing policy", error=str(e))
            raise TailscaleMCPError(f"Failed to test policy: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
