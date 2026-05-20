"""Tests for transport configuration."""

import os
from unittest.mock import patch

import pytest

from tailscalemcp.transport import (
    ENV_HOST,
    ENV_PATH,
    ENV_PORT,
    ENV_TRANSPORT,
    get_transport_config,
    resolve_transport,
    TransportType,
)


class TestGetTransportConfig:
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = get_transport_config()
            assert cfg["transport"] == "stdio"
            assert cfg["host"] == "127.0.0.1"
            assert cfg["port"] == 10821
            assert cfg["path"] == "/mcp"

    def test_env_overrides(self):
        with patch.dict(os.environ, {
            ENV_TRANSPORT: "http",
            ENV_HOST: "0.0.0.0",
            ENV_PORT: "9999",
            ENV_PATH: "/api/mcp",
        }, clear=True):
            cfg = get_transport_config()
            assert cfg["transport"] == "http"
            assert cfg["host"] == "0.0.0.0"
            assert cfg["port"] == 9999
            assert cfg["path"] == "/api/mcp"

    def test_port_custom(self):
        with patch.dict(os.environ, {ENV_PORT: "10700"}, clear=True):
            cfg = get_transport_config()
            assert cfg["port"] == 10700


class TestResolveTransport:
    def test_stdio_default(self):
        class Args:
            http = False
            sse = False
            stdio = False
        with patch.dict(os.environ, {}, clear=True):
            t = resolve_transport(Args())
            assert t == "stdio"

    def test_http_flag(self):
        class Args:
            http = True
            sse = False
            stdio = False
        t = resolve_transport(Args())
        assert t == "http"

    def test_sse_flag_deprecated(self):
        class Args:
            http = False
            sse = True
            stdio = False
        t = resolve_transport(Args())
        assert t == "sse"

    def test_stdio_flag(self):
        class Args:
            http = False
            sse = False
            stdio = True
        t = resolve_transport(Args())
        assert t == "stdio"

    def test_env_transport(self):
        class Args:
            http = False
            sse = False
            stdio = False
        with patch.dict(os.environ, {ENV_TRANSPORT: "http"}, clear=True):
            t = resolve_transport(Args())
            assert t == "http"

    def test_invalid_env_fallback(self):
        class Args:
            http = False
            sse = False
            stdio = False
        with patch.dict(os.environ, {ENV_TRANSPORT: "invalid"}, clear=True):
            t = resolve_transport(Args())
            assert t == "stdio"

    def test_cli_overrides_env(self):
        class Args:
            http = True
            sse = False
            stdio = False
        with patch.dict(os.environ, {ENV_TRANSPORT: "stdio"}, clear=True):
            t = resolve_transport(Args())
            assert t == "http"
