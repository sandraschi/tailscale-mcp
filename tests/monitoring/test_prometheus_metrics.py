"""
Tests for Prometheus metrics functionality in the Tailscale MCP server.
"""

import builtins
import contextlib
import sys
from unittest.mock import MagicMock, patch

import pytest
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

from tailscalemcp import __version__
from tailscalemcp.__main__ import setup_prometheus_metrics

_win = pytest.mark.xfail(sys.platform == "win32", reason="Windows file locking", strict=False)


class TestPrometheusMetrics:
    """Test Prometheus metrics setup and functionality."""

    def teardown_method(self):
        """Clean up Prometheus registry after each test."""
        import prometheus_client as pc

        registry = pc.REGISTRY
        collectors = list(registry._collector_to_names.keys())
        for collector in collectors:
            with contextlib.suppress(Exception):
                try:
                    registry.unregister(collector)
                except Exception:
                    pass
        pc.REGISTRY._names_to_collectors.clear()
        pc.REGISTRY._collector_to_names.clear()

    @_win
    def test_prometheus_metrics_server_startup(self):
        """Test that Prometheus metrics server starts correctly."""
        with patch("tailscalemcp.__main__.start_http_server") as mock_start_server:
            with patch("tailscalemcp.__main__.Info") as mock_info:
                mock_info_instance = MagicMock()
                mock_info.return_value = mock_info_instance
                setup_prometheus_metrics(9091)
                mock_start_server.assert_called_once_with(9091)

    @_win
    def test_info_metrics_functionality(self):
        """Test that info metrics work correctly."""
        with patch("tailscalemcp.__main__.start_http_server"):
            with patch("tailscalemcp.__main__.Info") as mock_info:
                mock_info_instance = MagicMock()
                mock_info.return_value = mock_info_instance
                setup_prometheus_metrics(9091)
                mock_info_instance.info.assert_called_once_with(
                    {"version": __version__, "name": "tailscale-mcp-server"}
                )

    def test_counter_creation(self):
        """Test that counters can be created and incremented."""
        registry = CollectorRegistry()
        counter = Counter("test_counter", "A test counter", registry=registry)
        counter.inc(5)
        assert counter._value.get() == 5.0

    def test_gauge_creation(self):
        """Test that gauges can be created and set."""
        registry = CollectorRegistry()
        gauge = Gauge("test_gauge", "A test gauge", registry=registry)
        gauge.set(42)
        assert gauge._value.get() == 42.0

    def test_histogram_creation(self):
        """Test that histograms can be created and observed."""
        registry = CollectorRegistry()
        histogram = Histogram("test_histogram", "A test histogram", registry=registry)
        histogram.observe(1.5)
        assert histogram._sum.get() == 1.5

    @_win
    def test_metrics_export_format(self):
        """Test that metrics can be exported in Prometheus format."""
        registry = CollectorRegistry()
        counter = Counter("test_export_counter", "A test counter for export", registry=registry)
        counter.inc(5)
        from prometheus_client import generate_latest

        output = generate_latest(registry)
        output_str = output.decode("utf-8")
        assert "# HELP test_export_counter_total A test counter for export" in output_str
        assert "# TYPE test_export_counter_total counter" in output_str
        assert "test_export_counter_total 5.0" in output_str

    def test_multiple_metrics_registry(self):
        """Test that multiple metric types can coexist in one registry."""
        registry = CollectorRegistry()
        c = Counter("multi_counter", "Count", registry=registry)
        g = Gauge("multi_gauge", "Gauge", registry=registry)
        h = Histogram("multi_histogram", "Histogram", registry=registry)
        c.inc(1)
        g.set(10)
        h.observe(0.5)
        assert c._value.get() == 1.0
        assert g._value.get() == 10.0
        assert h._sum.get() == 0.5

    @_win
    def test_counter_with_labels(self):
        """Test that counters with labels work correctly."""
        registry = CollectorRegistry()
        counter = Counter("labeled_counter", "Labeled counter", ["status"], registry=registry)
        counter.labels(status="success").inc(3)
        counter.labels(status="failure").inc(1)
        from prometheus_client import generate_latest

        output = generate_latest(registry).decode("utf-8")
        assert 'labeled_counter_total{status="success"} 3.0' in output
        assert 'labeled_counter_total{status="failure"} 1.0' in output
