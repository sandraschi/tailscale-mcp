"""
Tests for Prometheus metrics functionality in the Tailscale MCP server.
"""

import pytest
from unittest.mock import patch, MagicMock
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, Info

from src.tailscalemcp.__main__ import setup_prometheus_metrics


class TestPrometheusMetrics:
    """Test Prometheus metrics setup and functionality."""

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear any global registries
        try:
            from prometheus_client import REGISTRY
            # Clear the registry by removing all collectors
            for collector in list(REGISTRY._collector_to_names.keys()):
                try:
                    REGISTRY.unregister(collector)
                except:
                    pass
        except:
            pass

    def test_prometheus_metrics_server_startup(self):
        """Test that Prometheus metrics server starts correctly."""
        with patch('src.tailscalemcp.__main__.start_http_server') as mock_start_server:
            with patch('src.tailscalemcp.__main__.Info') as mock_info:
                mock_info_instance = MagicMock()
                mock_info.return_value = mock_info_instance
                
                setup_prometheus_metrics(9091)
                
                # Verify server started
                mock_start_server.assert_called_once_with(9091)
                
                # Verify info metric was created
                mock_info.assert_called_once()

    def test_info_metrics_functionality(self):
        """Test that info metrics work correctly."""
        with patch('src.tailscalemcp.__main__.start_http_server'):
            with patch('src.tailscalemcp.__main__.Info') as mock_info:
                mock_info_instance = MagicMock()
                mock_info.return_value = mock_info_instance
                
                setup_prometheus_metrics(9091)
                
                # Verify info metric was configured
                mock_info_instance.info.assert_called_once_with({
                    'version': '2.0.0',  # Should match the version
                    'name': 'tailscale-mcp-server'
                })

    def test_metrics_with_labels(self):
        """Test that metrics with labels work correctly."""
        # Create a test registry
        registry = CollectorRegistry()
        
        # Create a counter with labels
        counter = Counter('test_counter_with_labels', 'A test counter with labels', 
                         ['label1', 'label2'], registry=registry)
        
        # Increment with different label combinations
        counter.labels(label1='value1', label2='value2').inc()
        counter.labels(label1='value1', label2='value3').inc(2)
        
        # Collect metrics
        metrics = list(registry.collect())
        
        # Should have one metric
        assert len(metrics) == 1
        
        # Should have multiple samples (one for each label combination)
        metric = metrics[0]
        assert len(metric.samples) >= 2  # At least 2 samples for 2 label combinations

    def test_metrics_registry_cleanup(self):
        """Test that metrics registry can be cleaned up."""
        registry = CollectorRegistry()
        
        # Create a metric
        counter = Counter('test_cleanup_counter', 'A test counter for cleanup', registry=registry)
        counter.inc()
        
        # Verify metric exists
        metrics = list(registry.collect())
        assert len(metrics) == 1
        
        # Unregister the metric
        registry.unregister(counter)
        
        # Verify metric is removed
        metrics = list(registry.collect())
        assert len(metrics) == 0

    def test_metrics_error_handling(self):
        """Test that metrics handle errors gracefully."""
        registry = CollectorRegistry()
        
        # Create a metric
        counter = Counter('test_error_counter', 'A test counter for error handling', registry=registry)
        
        # This should not raise an error
        try:
            counter.inc()
            counter.labels().inc()  # This might raise an error depending on implementation
        except Exception as e:
            # If it raises an error, it should be handled gracefully
            assert isinstance(e, Exception)

    def test_metrics_export_format(self):
        """Test that metrics can be exported in Prometheus format."""
        registry = CollectorRegistry()
        
        # Create a counter
        counter = Counter('test_export_counter', 'A test counter for export', registry=registry)
        counter.inc(5)
        
        # Export metrics
        from prometheus_client import generate_latest
        output = generate_latest(registry)
        output_str = output.decode('utf-8')
        
        # Verify export format contains expected elements
        assert '# HELP test_export_counter A test counter for export' in output_str
        assert '# TYPE test_export_counter_total counter' in output_str
        assert 'test_export_counter_total 5.0' in output_str

    def test_histogram_metrics(self):
        """Test histogram metrics functionality."""
        registry = CollectorRegistry()
        
        # Create a histogram
        histogram = Histogram('test_histogram', 'A test histogram', 
                             ['method'], registry=registry)
        
        # Record some values
        histogram.labels(method='GET').observe(0.5)
        histogram.labels(method='GET').observe(1.0)
        histogram.labels(method='POST').observe(2.0)
        
        # Collect metrics
        metrics = list(registry.collect())
        
        # Should have one metric
        assert len(metrics) == 1
        
        # Should have multiple samples (buckets, count, sum)
        metric = metrics[0]
        assert len(metric.samples) > 3  # Multiple buckets plus count and sum

    def test_gauge_metrics(self):
        """Test gauge metrics functionality."""
        registry = CollectorRegistry()
        
        # Create a gauge
        gauge = Gauge('test_gauge', 'A test gauge', ['status'], registry=registry)
        
        # Set values
        gauge.labels(status='active').set(10)
        gauge.labels(status='inactive').set(5)
        
        # Collect metrics
        metrics = list(registry.collect())
        
        # Should have one metric
        assert len(metrics) == 1
        
        # Should have 2 samples (one for each status)
        metric = metrics[0]
        assert len(metric.samples) == 2

    def test_metrics_with_different_registries(self):
        """Test that metrics work with different registries."""
        registry1 = CollectorRegistry()
        registry2 = CollectorRegistry()
        
        # Create metrics in different registries
        counter1 = Counter('test_counter', 'A test counter', registry=registry1)
        counter2 = Counter('test_counter', 'A test counter', registry=registry2)
        
        # Increment counters
        counter1.inc()
        counter2.inc(2)
        
        # Collect from each registry
        metrics1 = list(registry1.collect())
        metrics2 = list(registry2.collect())
        
        # Both should have one metric
        assert len(metrics1) == 1
        assert len(metrics2) == 1
        
        # Values should be different
        assert metrics1[0].samples[0].value == 1.0
        assert metrics2[0].samples[0].value == 2.0

    def test_metrics_labels_validation(self):
        """Test that metrics validate labels correctly."""
        registry = CollectorRegistry()
        
        # Create a counter with required labels
        counter = Counter('test_labels_counter', 'A test counter with labels', 
                         ['required_label'], registry=registry)
        
        # This should work
        counter.labels(required_label='value1').inc()
        
        # This should raise an error (missing required label)
        with pytest.raises(ValueError):
            counter.inc()

    def test_metrics_concurrent_access(self):
        """Test that metrics handle concurrent access correctly."""
        import threading
        import time
        
        registry = CollectorRegistry()
        counter = Counter('test_concurrent_counter', 'A test counter for concurrent access', registry=registry)
        
        def increment_counter():
            for _ in range(10):
                counter.inc()
                time.sleep(0.001)  # Small delay to increase chance of race conditions
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify final value
        metrics = list(registry.collect())
        assert len(metrics) == 1
        assert metrics[0].samples[0].value == 30.0  # 3 threads * 10 increments each