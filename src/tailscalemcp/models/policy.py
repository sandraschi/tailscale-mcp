"""ACL Policy models for Tailscale."""

from typing import Any

from pydantic import BaseModel, Field


class ACLRule(BaseModel):
    """ACL rule definition."""

    action: str = Field(..., description="Rule action (accept, reject, etc.)")
    src: list[str] = Field(default_factory=list, description="Source addresses/tags")
    dst: list[str] = Field(
        default_factory=list, description="Destination addresses/tags"
    )


class PolicyGrant(BaseModel):
    """Policy grant definition."""

    src: list[str] = Field(default_factory=list, description="Source identifiers")
    dst: list[str] = Field(default_factory=list, description="Destination identifiers")
    ports: list[str] = Field(default_factory=list, description="Port specifications")


class ACLPolicy(BaseModel):
    """Tailscale ACL policy model."""

    hosts: dict[str, str] = Field(default_factory=dict, description="Host definitions")
    users: dict[str, str] = Field(default_factory=dict, description="User definitions")
    tags: dict[str, str] = Field(default_factory=dict, description="Tag definitions")
    acls: list[ACLRule] = Field(default_factory=list, description="ACL rules")
    groups: dict[str, list[str]] = Field(
        default_factory=dict, description="Group definitions"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "ACLPolicy":
        """Create ACLPolicy from API response.

        Args:
            data: Policy data from API

        Returns:
            ACLPolicy instance
        """
        acls = []
        if "ACLs" in data:
            for rule_data in data["ACLs"]:
                acls.append(
                    ACLRule(
                        action=rule_data.get("Action", ""),
                        src=rule_data.get("Src", []),
                        dst=rule_data.get("Dst", []),
                    )
                )

        return cls(
            hosts=data.get("Hosts", {}),
            users=data.get("Users", {}),
            tags=data.get("Tags", {}),
            acls=acls,
            groups=data.get("Groups", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert policy to dictionary compatible with Tailscale API."""
        return {
            "Hosts": self.hosts,
            "Users": self.users,
            "Tags": self.tags,
            "ACLs": [
                {"Action": rule.action, "Src": rule.src, "Dst": rule.dst}
                for rule in self.acls
            ],
            "Groups": self.groups,
        }
