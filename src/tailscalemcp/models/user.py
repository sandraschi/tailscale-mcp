"""User models for Tailscale."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User role in tailnet."""

    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    MEMBER = "member"


class User(BaseModel):
    """Tailscale user model."""

    id: str = Field(..., description="User ID")
    login_name: str = Field(..., description="Login name/email")
    display_name: str | None = Field(None, description="Display name")
    profile_pic_url: str | None = Field(None, description="Profile picture URL")
    role: UserRole = Field(UserRole.USER, description="User role")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "User":
        """Create User from API response.

        Args:
            data: User data from API

        Returns:
            User instance
        """
        role = UserRole.USER
        if "role" in data:
            try:
                role = UserRole(data["role"].lower())
            except ValueError:
                role = UserRole.USER

        return cls(
            id=data.get("id", ""),
            login_name=data.get("loginName", data.get("login_name", "")),
            display_name=data.get("displayName", data.get("display_name")),
            profile_pic_url=data.get("profilePicURL", data.get("profile_pic_url")),
            role=role,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary."""
        return self.model_dump(exclude_none=True)
