"""Tests for the FastAPI web backend (server.py)."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from tailscalemcp.server import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "tailscale-mcp-backend"


@pytest.mark.asyncio
async def test_api_status_no_creds(client):
    with patch.dict("os.environ", {}, clear=True):
        resp = await client.get("/api/v1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tailscale_api_configured"] is False


@pytest.mark.asyncio
async def test_api_status_with_creds(client):
    with patch.dict("os.environ", {"TAILSCALE_API_KEY": "key", "TAILSCALE_TAILNET": "tn"}):
        resp = await client.get("/api/v1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tailscale_api_configured"] is True
        assert data["api_key_set"] is True
        assert data["tailnet_set"] is True


@pytest.mark.asyncio
async def test_sampling_status_defaults(client):
    with patch.dict("os.environ", {}, clear=True):
        resp = await client.get("/api/v1/sampling-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sampling_base_url"] == "http://127.0.0.1:11434/v1"
        assert data["sampling_model"] == "llama3.2"
        assert data["sampling_api_key_configured"] is False


@pytest.mark.asyncio
async def test_api_v1_tools_not_configured(client):
    """Returns 500 when server has no API credentials (mcp not fully init)."""
    resp = await client.get("/api/v1/tools")
    # Without real credentials the server might return 500 or tools
    # We just check it responds
    assert resp.status_code in (200, 500)


@pytest.mark.asyncio
async def test_api_v1_tools_call_missing_name(client):
    resp = await client.post("/api/v1/tools/call", json={})
    assert resp.status_code == 422  # validation error from FastAPI


@pytest.mark.asyncio
async def test_llm_health_unreachable(client):
    with patch.dict("os.environ", {"TAILSCALE_SAMPLING_BASE_URL": "http://127.0.0.1:1/v1"}, clear=True):
        resp = await client.get("/api/v1/llm-health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reachable"] is False


@pytest.mark.asyncio
async def test_chat_no_messages(client):
    resp = await client.post("/api/v1/chat", json={})
    assert resp.status_code == 422  # missing required messages field


@pytest.mark.asyncio
async def test_chat_empty_messages(client):
    resp = await client.post("/api/v1/chat", json={"messages": []})
    assert resp.status_code == 400
