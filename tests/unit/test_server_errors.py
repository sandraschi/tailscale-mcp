"""Error path tests for the FastAPI web backend (server.py)."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from tailscalemcp.server import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test", timeout=30)


@pytest.mark.asyncio
async def test_tools_call_auth_error(client):
    """POST /api/v1/tools/call with auth failure returns 503."""
    with patch("tailscalemcp.server._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock()
        mock_client.call_tool.side_effect = Exception("authentication failed - 401")
        mock_get.return_value = mock_client
        resp = await client.post(
            "/api/v1/tools/call",
            json={"name": "test_tool", "arguments": {}},
        )
        assert resp.status_code == 503
        data = resp.json()
        assert "authentication" in data.get("detail", {}).get("message", "").lower()


@pytest.mark.asyncio
async def test_tools_call_tailnet_error(client):
    """POST /api/v1/tools/call with tailnet error returns 503."""
    with patch("tailscalemcp.server._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock()
        mock_client.call_tool.side_effect = Exception("tailnet is required")
        mock_get.return_value = mock_client
        resp = await client.post(
            "/api/v1/tools/call",
            json={"name": "test_tool", "arguments": {}},
        )
        assert resp.status_code == 503


@pytest.mark.asyncio
async def test_tools_call_generic_error(client):
    """POST /api/v1/tools/call with generic error returns 500."""
    with patch("tailscalemcp.server._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock()
        mock_client.call_tool.side_effect = Exception("something broke")
        mock_get.return_value = mock_client
        resp = await client.post(
            "/api/v1/tools/call",
            json={"name": "test_tool", "arguments": {}},
        )
        assert resp.status_code == 500
        data = resp.json()
        assert "something broke" in data.get("detail", {}).get("message", "")


@pytest.mark.asyncio
async def test_tools_list_error(client):
    """GET /api/v1/tools with failure returns 500."""
    with patch("tailscalemcp.server._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.list_tools = AsyncMock()
        mock_client.list_tools.side_effect = Exception("list failed")
        mock_get.return_value = mock_client
        resp = await client.get("/api/v1/tools")
        assert resp.status_code == 500


@pytest.mark.asyncio
@pytest.mark.xfail(reason="httpx mock internals fragile with ASGI transport", strict=True)
async def test_chat_proxy_http_error(client):
    """POST /api/v1/chat with upstream HTTP error returns 502."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "bad request"
        mock_response.raise_for_status.side_effect = RuntimeError("HTTP 400 Bad Request")
        mock_post.return_value = mock_response
        resp = await client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "hello"}]},
        )
        assert resp.status_code == 502


@pytest.mark.asyncio
async def test_tools_call_invalid_body(client):
    """POST /api/v1/tools/call without name field returns 422."""
    resp = await client.post("/api/v1/tools/call", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_llm_health_returns_200(client):
    """GET /api/v1/llm-health always returns 200 with structured response."""
    with patch.dict("os.environ", {"TAILSCALE_SAMPLING_BASE_URL": "http://127.0.0.1:1/v1"}, clear=True):
        resp = await client.get("/api/v1/llm-health")
    assert resp.status_code == 200
    data = resp.json()
    assert "reachable" in data
