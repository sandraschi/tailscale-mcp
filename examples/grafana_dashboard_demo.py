#!/usr/bin/env python3
"""
Tailscale Grafana Dashboard Demo

This script demonstrates how to use the TailscaleMCP server to create
and export Grafana dashboards for monitoring Tailscale networks.
"""

import asyncio
import json
import os
from pathlib import Path

from tailscalemcp import TailscaleMCPServer


async def main():
    """Demonstrate Grafana dashboard functionality."""
    print("🚀 Tailscale Grafana Dashboard Demo")
    print("=" * 50)

    # Initialize the server
    server = TailscaleMCPServer(
        api_key=os.getenv("TAILSCALE_API_KEY", "demo_key"),
        tailnet=os.getenv("TAILSCALE_TAILNET", "demo.tailnet.ts.net"),
    )

    try:
        # 1. Collect network metrics
        print("\n📊 Collecting network metrics...")
        metrics = await server._get_network_metrics_impl()
        print(
            f"   Devices: {metrics['devices_total']} total, {metrics['devices_online']} online"
        )
        print(f"   Health Score: {metrics['network_health_score']:.1f}%")
        print(f"   Exit Nodes: {metrics['exit_nodes']}")
        print(f"   Subnet Routes: {metrics['subnet_routes']}")

        # 2. Generate network topology
        print("\n🗺️  Generating network topology...")
        topology = await server._get_network_topology_impl()
        print(f"   Nodes: {len(topology['nodes'])}")
        print(f"   Connections: {len(topology['edges'])}")

        # 3. Create comprehensive Grafana dashboard
        print("\n📈 Creating comprehensive Grafana dashboard...")
        comprehensive_dashboard = await server._create_grafana_dashboard_impl(
            "comprehensive"
        )
        dashboard_info = comprehensive_dashboard["dashboard"]
        print(f"   Title: {dashboard_info['title']}")
        print(f"   Panels: {len(dashboard_info['panels'])}")
        print(f"   Tags: {', '.join(dashboard_info['tags'])}")

        # 4. Create network topology dashboard
        print("\n🕸️  Creating network topology dashboard...")
        topology_dashboard = await server._create_grafana_dashboard_impl("topology")
        topology_info = topology_dashboard["dashboard"]
        print(f"   Title: {topology_info['title']}")
        print(f"   Panels: {len(topology_info['panels'])}")

        # 5. Create security dashboard
        print("\n🔒 Creating security dashboard...")
        security_dashboard = await server._create_grafana_dashboard_impl("security")
        security_info = security_dashboard["dashboard"]
        print(f"   Title: {security_info['title']}")
        print(f"   Panels: {len(security_info['panels'])}")

        # 6. Export dashboards to files
        print("\n💾 Exporting dashboards to files...")

        # Create output directory
        output_dir = Path("grafana_dashboards")
        output_dir.mkdir(exist_ok=True)

        # Export comprehensive dashboard
        comprehensive_file = output_dir / "tailscale_comprehensive_dashboard.json"
        with open(comprehensive_file, "w") as f:
            json.dump(comprehensive_dashboard, f, indent=2)
        print(f"   Comprehensive: {comprehensive_file}")

        # Export topology dashboard
        topology_file = output_dir / "tailscale_topology_dashboard.json"
        with open(topology_file, "w") as f:
            json.dump(topology_dashboard, f, indent=2)
        print(f"   Topology: {topology_file}")

        # Export security dashboard
        security_file = output_dir / "tailscale_security_dashboard.json"
        with open(security_file, "w") as f:
            json.dump(security_dashboard, f, indent=2)
        print(f"   Security: {security_file}")

        # 7. Get dashboard summaries
        print("\n📋 Dashboard Summaries:")

        comprehensive_summary = await server._get_dashboard_summary_impl(
            "comprehensive"
        )
        print("   Comprehensive Dashboard:")
        print(f"     - Panels: {comprehensive_summary['panels_count']}")
        print(f"     - Refresh: {comprehensive_summary['refresh_interval']}")
        print(f"     - Tags: {', '.join(comprehensive_summary['tags'])}")

        topology_summary = await server._get_dashboard_summary_impl("topology")
        print("   Topology Dashboard:")
        print(f"     - Panels: {topology_summary['panels_count']}")
        print(f"     - Refresh: {topology_summary['refresh_interval']}")

        security_summary = await server._get_dashboard_summary_impl("security")
        print("   Security Dashboard:")
        print(f"     - Panels: {security_summary['panels_count']}")
        print(f"     - Refresh: {security_summary['refresh_interval']}")

        # 8. Generate Prometheus metrics
        print("\n⚡ Generating Prometheus metrics...")
        prometheus_metrics = await server._get_prometheus_metrics_impl()
        metrics_file = output_dir / "tailscale_metrics.prom"
        with open(metrics_file, "w") as f:
            f.write(prometheus_metrics)
        print(f"   Metrics exported to: {metrics_file}")

        # 9. Generate network health report
        print("\n🏥 Generating network health report...")
        health_report = await server._get_network_health_report_impl()
        print(
            f"   Overall Health: {health_report['current_status']['overall_health']:.1f}%"
        )
        print(f"   Uptime: {health_report['current_status']['uptime_percentage']:.1f}%")
        print(f"   Alerts: {len(health_report['alerts'])}")
        print(f"   Recommendations: {len(health_report['recommendations'])}")

        if health_report["alerts"]:
            print("   Active Alerts:")
            for alert in health_report["alerts"]:
                print(f"     - [{alert['level'].upper()}] {alert['message']}")

        if health_report["recommendations"]:
            print("   Recommendations:")
            for rec in health_report["recommendations"]:
                print(f"     - {rec}")

        # 10. Create deployment instructions
        print("\n📝 Creating deployment instructions...")
        deployment_instructions = f"""
# Tailscale Grafana Dashboard Deployment Instructions

## Prerequisites
- Grafana instance running
- Prometheus configured to scrape Tailscale metrics
- Tailscale API access

## Dashboard Import
1. Open Grafana web interface
2. Go to Dashboards → Import
3. Upload the following dashboard files:
   - {comprehensive_file.name} (Comprehensive monitoring)
   - {topology_file.name} (Network topology)
   - {security_file.name} (Security monitoring)

## Prometheus Configuration
Add the following to your prometheus.yml:

```yaml
scrape_configs:
  - job_name: 'tailscale'
    static_configs:
      - targets: ['localhost:8000']  # Tailscale MCP server
    scrape_interval: 30s
    metrics_path: '/metrics'
```

## Data Source Configuration
1. In Grafana, go to Configuration → Data Sources
2. Add Prometheus data source
3. Set URL to your Prometheus instance
4. Save and test connection

## Dashboard Features
- Real-time device monitoring
- Network health scoring
- Bandwidth usage tracking
- Latency monitoring
- Device topology visualization
- Security alerts and ACL monitoring
- Historical trends and analytics

## Customization
- Modify panel queries to match your Prometheus metrics
- Adjust refresh intervals based on your needs
- Add custom alerts and notifications
- Customize visualizations and thresholds

Generated on: {asyncio.get_event_loop().time()}
Tailnet: {server.tailnet}
"""

        instructions_file = output_dir / "DEPLOYMENT_INSTRUCTIONS.md"
        with open(instructions_file, "w") as f:
            f.write(deployment_instructions)
        print(f"   Instructions saved to: {instructions_file}")

        print("\n✅ Demo completed successfully!")
        print(f"📁 All files saved to: {output_dir.absolute()}")
        print("\n🎯 Next Steps:")
        print("1. Import the dashboard JSON files into Grafana")
        print(
            "2. Configure Prometheus to scrape metrics from your Tailscale MCP server"
        )
        print("3. Set up data sources and alerts in Grafana")
        print("4. Customize dashboards for your specific needs")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
