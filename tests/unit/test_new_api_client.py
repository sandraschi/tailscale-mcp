"""Tests for new Tailscale Admin API client methods (device invites, logging, webhooks, etc.)."""

from unittest.mock import AsyncMock, patch

import pytest

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig


@pytest.fixture
def config():
    return TailscaleConfig(
        tailscale_api_key="tskey-test",
        tailscale_tailnet="test.tailnet.ts.net",
    )


@pytest.fixture
def client(config):
    return TailscaleAPIClient(config=config)


class TestDeviceInvites:
    @pytest.mark.asyncio
    async def test_list_device_invites(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = [{"id": "123", "deviceId": "dev1"}]
            invites = await client.list_device_invites("dev1")
            assert len(invites) == 1
            assert invites[0]["id"] == "123"
            m.assert_called_once_with("GET", "/devices/dev1/device-invites")

    @pytest.mark.asyncio
    async def test_create_device_invites(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = [{"id": "456"}]
            payload = [{"multiUse": False, "email": "user@example.com"}]
            invites = await client.create_device_invites("dev1", payload)
            assert len(invites) == 1
            m.assert_called_once_with("POST", "/devices/dev1/device-invites", json=payload)

    @pytest.mark.asyncio
    async def test_get_device_invite(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"id": "123"}
            invite = await client.get_device_invite("123")
            assert invite["id"] == "123"
            m.assert_called_once_with("GET", "/device-invites/123")

    @pytest.mark.asyncio
    async def test_delete_device_invite(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            await client.delete_device_invite("123")
            m.assert_called_once_with("DELETE", "/device-invites/123")

    @pytest.mark.asyncio
    async def test_resend_device_invite(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            await client.resend_device_invite("123")
            m.assert_called_once_with("POST", "/device-invites/123/resend")

    @pytest.mark.asyncio
    async def test_accept_device_invite(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"device": {"id": "dev1"}}
            result = await client.accept_device_invite("https://login.tailscale.com/admin/invite/code123")
            assert result["device"]["id"] == "dev1"
            m.assert_called_once_with("POST", "/device-invites/-/accept", json={"invite": "https://login.tailscale.com/admin/invite/code123"})


class TestUserInvites:
    @pytest.mark.asyncio
    async def test_list_user_invites(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = [{"id": "u1"}]
            invites = await client.list_user_invites()
            assert len(invites) == 1
            m.assert_called_once_with("GET", "/tailnet/test.tailnet.ts.net/user-invites")

    @pytest.mark.asyncio
    async def test_create_user_invites(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = [{"id": "u2"}]
            payload = [{"role": "member", "email": "user@example.com"}]
            invites = await client.create_user_invites(payload)
            assert len(invites) == 1
            m.assert_called_once_with("POST", "/tailnet/test.tailnet.ts.net/user-invites", json=payload)


class TestPostureAttributes:
    @pytest.mark.asyncio
    async def test_get_device_posture_attributes(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"custom:myattr": {"value": "test"}}
            attrs = await client.get_device_posture_attributes("dev1")
            assert attrs["custom:myattr"]["value"] == "test"
            m.assert_called_once_with("GET", "/devices/dev1/attributes")

    @pytest.mark.asyncio
    async def test_set_custom_device_posture_attribute(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"custom:attr": {"value": "v"}}
            result = await client.set_custom_device_posture_attribute("dev1", "custom:attr", "v")
            assert result["custom:attr"]["value"] == "v"
            m.assert_called_once_with("POST", "/devices/dev1/attributes/custom:attr", json={"value": "v"})

    @pytest.mark.asyncio
    async def test_batch_update_device_posture_attributes(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            nodes = {"dev1": {"custom:attr": {"value": "v"}}}
            await client.batch_update_device_posture_attributes(nodes)
            m.assert_called_once_with("PATCH", "/tailnet/test.tailnet.ts.net/device-attributes", json={"nodes": nodes})


class TestDeviceKeys:
    @pytest.mark.asyncio
    async def test_expire_device_key(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            await client.expire_device_key("dev1")
            m.assert_called_once_with("POST", "/devices/dev1/expire")

    @pytest.mark.asyncio
    async def test_set_device_ip(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            await client.set_device_ip("dev1", "100.80.0.1")
            m.assert_called_once_with("POST", "/devices/dev1/ip", json={"ipv4": "100.80.0.1"})


class TestLogging:
    @pytest.mark.asyncio
    async def test_list_configuration_audit_logs(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"logs": [{"event": "test"}]}
            logs = await client.list_configuration_audit_logs()
            assert len(logs) == 1
            m.assert_called_once_with("GET", "/tailnet/test.tailnet.ts.net/logging/configuration", params=None)

    @pytest.mark.asyncio
    async def test_list_network_flow_logs(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"logs": []}
            logs = await client.list_network_flow_logs()
            assert len(logs) == 0


class TestWebhooks:
    @pytest.mark.asyncio
    async def test_list_webhooks(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"webhooks": [{"id": "w1"}]}
            hooks = await client.list_webhooks()
            assert len(hooks) == 1

    @pytest.mark.asyncio
    async def test_create_webhook(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"id": "w1"}
            hook = await client.create_webhook("https://example.com/hook", "slack")
            assert hook["id"] == "w1"
            m.assert_called_once_with(
                "POST", "/tailnet/test.tailnet.ts.net/webhooks",
                json={"endpointUrl": "https://example.com/hook", "providerType": "slack"},
            )

    @pytest.mark.asyncio
    async def test_rotate_webhook_secret(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"secret": "new-secret"}
            result = await client.rotate_webhook_secret("w1")
            assert result["secret"] == "new-secret"
            m.assert_called_once_with("POST", "/tailnet/test.tailnet.ts.net/webhooks/w1/rotate")


class TestTailnetSettings:
    @pytest.mark.asyncio
    async def test_get_tailnet_settings(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"keyExpiryDisabled": True}
            settings = await client.get_tailnet_settings()
            assert settings["keyExpiryDisabled"] is True


class TestContacts:
    @pytest.mark.asyncio
    async def test_get_contact_preferences(self, client):
        with patch.object(client, "_request", new_callable=AsyncMock) as m:
            m.return_value = {"security": {"email": "admin@example.com"}}
            prefs = await client.get_contact_preferences()
            assert prefs["security"]["email"] == "admin@example.com"
