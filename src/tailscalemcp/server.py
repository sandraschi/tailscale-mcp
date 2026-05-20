"""
FastAPI application for web_sota backend (FastMCP 3.2 single-backend pattern).
Serves /health, /api/v1/tools, /api/v1/tools/call, sampling/LLM helpers, optional chat proxy, and MCP at /mcp.
"""

from __future__ import annotations

import contextlib
import os
from typing import Any

import httpx
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tailscalemcp import setup_logging
from tailscalemcp.mcp_server import server as tailscale_mcp_server

setup_logging()

logger = structlog.get_logger(__name__)

# Build MCP ASGI app and capture lifespan for FastAPI
mcp_app = tailscale_mcp_server.mcp.http_app(path="/mcp")

# Reusable FastMCP Client — created once, not per-request
_fastmcp_client = None


def _get_client():
    """Get or create the shared FastMCP Client."""
    global _fastmcp_client
    if _fastmcp_client is None:
        from fastmcp.client import Client

        _fastmcp_client = Client(tailscale_mcp_server.mcp)
    return _fastmcp_client

app = FastAPI(
    title="Tailscale MCP Webapp Backend",
    version="2.0.2",
    description="REST API and MCP mount for Tailscale network controller",
    lifespan=mcp_app.lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10820",
        "http://localhost:10820",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", mcp_app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "tailscale-mcp-backend"}


@app.get("/api/v1/status")
async def api_status() -> dict[str, Any]:
    """Webapp helper: credential presence (no secrets) and links to Tailscale docs."""
    key = (os.getenv("TAILSCALE_API_KEY") or "").strip()
    tailnet = (os.getenv("TAILSCALE_TAILNET") or "").strip()
    return {
        "tailscale_api_configured": bool(key and tailnet),
        "tailnet_set": bool(tailnet),
        "api_key_set": bool(key),
        "docs": {
            "interactive_api": "https://tailscale.com/api",
            "create_api_key": "https://login.tailscale.com/admin/settings/keys",
            "trust_credentials": "https://tailscale.com/docs/reference/trust-credentials",
        },
    }


@app.get("/api/v1/tools")
async def list_tools() -> dict[str, Any]:
    try:
        client = _get_client()
        tools = await client.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": getattr(t, "description", None) or "",
                    "inputSchema": getattr(t, "inputSchema", None),
                }
                for t in tools
            ]
        }
    except Exception as e:
        logger.exception("list_tools failed")
        raise HTTPException(
            status_code=500,
            detail={
                "message": str(e),
                "hint": "Check FastMCP Client and server lifespan.",
            },
        ) from e


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] | None = None


@app.post("/api/v1/tools/call")
async def call_tool(body: ToolCallRequest) -> dict[str, Any]:
    try:
        client = _get_client()
        result = await client.call_tool(body.name, body.arguments or {})
        content = result.content or []
        text_parts = [getattr(c, "text", str(c)) for c in content]
        return {
            "result": {
                "content": [{"type": "text", "text": "\n".join(text_parts)}],
                "data": result.data,
            },
            "data": result.data,
            "content": content,
            "is_error": result.is_error,
        }
    except Exception as e:
        logger.exception("call_tool failed")
        msg = str(e)
        hint = (
            "Set TAILSCALE_API_KEY and TAILSCALE_TAILNET for the backend process "
            "(e.g. repo root .env), then restart uvicorn. See Settings in the webapp for doc links."
        )
        low = msg.lower()
        status = 500
        if "authentication" in low or "401" in msg or "invalid api key" in low:
            status = 503
            hint = (
                "Tailscale API rejected the key. Create a new key at "
                "https://login.tailscale.com/admin/settings/keys and update the backend env."
            )
        elif "tailnet" in low and "required" in low:
            status = 503
        raise HTTPException(
            status_code=status,
            detail={"message": msg, "hint": hint, "tool": body.name},
        ) from e


@app.get("/api/v1/sampling-status")
async def sampling_status() -> dict[str, Any]:
    """Redacted sampling configuration for the webapp (no secrets)."""
    base = os.getenv("TAILSCALE_SAMPLING_BASE_URL", "http://127.0.0.1:11434/v1").rstrip(
        "/"
    )
    model = os.getenv("TAILSCALE_SAMPLING_MODEL", "llama3.2")
    key = (os.getenv("TAILSCALE_SAMPLING_API_KEY") or "").strip()
    use_client = os.getenv("TAILSCALE_SAMPLING_USE_CLIENT_LLM", "").lower() in (
        "1",
        "true",
        "yes",
    )
    return {
        "sampling_base_url": base,
        "sampling_model": model,
        "sampling_api_key_configured": bool(key),
        "use_client_llm": use_client,
    }


@app.get("/api/v1/llm-health")
async def llm_health() -> dict[str, Any]:
    """Probe OpenAI-compatible /v1/models; fallback Ollama /api/tags."""
    base = os.getenv("TAILSCALE_SAMPLING_BASE_URL", "http://127.0.0.1:11434/v1").rstrip(
        "/"
    )
    key = (os.getenv("TAILSCALE_SAMPLING_API_KEY") or "").strip()
    headers: dict[str, str] = {}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    result: dict[str, Any] = {
        "reachable": False,
        "endpoint_tried": None,
        "http_status": None,
        "detail": None,
        "models_sample": None,
    }

    models_url = f"{base}/models"
    result["endpoint_tried"] = models_url

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(models_url, headers=headers)
            result["http_status"] = r.status_code
            if r.status_code == 200:
                data = r.json()
                result["reachable"] = True
                mlist = data.get("data") or data.get("models")
                if isinstance(mlist, list) and mlist:
                    names: list[str] = []
                    for item in mlist[:12]:
                        if isinstance(item, dict):
                            n = item.get("id") or item.get("name")
                            if n:
                                names.append(str(n))
                    result["models_sample"] = names or None
                return result
            result["detail"] = r.text[:500]
    except Exception as e:
        result["detail"] = str(e)[:500]

    root = base.removesuffix("/v1").rstrip("/")
    if root == base:
        root = base.split("/v1", 1)[0].rstrip("/") if "/v1" in base else base
    tags_url = f"{root}/api/tags"
    result["endpoint_tried"] = tags_url
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(tags_url)
            result["http_status"] = r.status_code
            if r.status_code == 200:
                data = r.json()
                result["reachable"] = True
                models = data.get("models") if isinstance(data, dict) else None
                if isinstance(models, list):
                    names = []
                    for m in models[:12]:
                        if isinstance(m, dict) and m.get("name"):
                            names.append(str(m["name"]))
                    result["models_sample"] = names or None
            else:
                tail = r.text[:200]
                prev = result.get("detail") or ""
                result["detail"] = f"{prev} | tags http {r.status_code}: {tail}"[:800]
    except Exception as e:
        prev = result.get("detail") or ""
        result["detail"] = f"{prev} | tags err: {e!s}"[:800]

    return result


class ChatRequest(BaseModel):
    messages: list[dict[str, Any]]
    model: str | None = None
    temperature: float | None = 0.7
    max_tokens: int | None = 1024


@app.post("/api/v1/chat")
async def chat_completions(body: ChatRequest) -> dict[str, Any]:
    """Proxy to OpenAI-compatible chat/completions (Ollama, LM Studio, etc.)."""
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages required")
    base = os.getenv("TAILSCALE_SAMPLING_BASE_URL", "http://127.0.0.1:11434/v1").rstrip(
        "/"
    )
    model = body.model or os.getenv("TAILSCALE_SAMPLING_MODEL", "llama3.2")
    key = (os.getenv("TAILSCALE_SAMPLING_API_KEY") or "").strip()
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    url = f"{base}/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": body.messages,
        "temperature": body.temperature if body.temperature is not None else 0.7,
    }
    if body.max_tokens is not None:
        payload["max_tokens"] = body.max_tokens
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        err = ""
        with contextlib.suppress(Exception):
            err = e.response.text[:800]
        raise HTTPException(
            status_code=502,
            detail={"message": str(e), "body": err, "url": url},
        ) from e
    except Exception as e:
        logger.exception("chat proxy failed")
        raise HTTPException(status_code=502, detail=str(e)) from e

    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    return {
        "content": content,
        "model": data.get("model") or model,
        "raw": data,
    }
