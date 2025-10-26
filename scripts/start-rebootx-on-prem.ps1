#!/usr/bin/env pwsh
# PowerShell script to start RebootX On-Prem integration for Tailscale MCP

Write-Host "🚀 Starting RebootX On-Prem Integration for Tailscale MCP" -ForegroundColor Green

# Check if Docker is running
Write-Host "📋 Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Navigate to the monitoring directory
$monitoringDir = Join-Path $PSScriptRoot "..\monitoring"
if (-not (Test-Path $monitoringDir)) {
    Write-Host "❌ Monitoring directory not found: $monitoringDir" -ForegroundColor Red
    exit 1
}

Set-Location $monitoringDir

# Check if the main monitoring stack is running
Write-Host "📋 Checking if main monitoring stack is running..." -ForegroundColor Yellow
$mainStackRunning = docker-compose ps --services --filter "status=running" 2>$null
if ($mainStackRunning -notcontains "tailscale-mcp" -or $mainStackRunning -notcontains "grafana") {
    Write-Host "⚠️  Main monitoring stack is not running. Starting it first..." -ForegroundColor Yellow
    Write-Host "📋 Starting main monitoring stack..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 10
}

# Start RebootX On-Prem
Write-Host "📋 Starting RebootX On-Prem integration..." -ForegroundColor Yellow
Set-Location "rebootx-on-prem"

try {
    docker-compose -f docker-compose.rebootx.yml up -d
    Write-Host "✅ RebootX On-Prem integration started successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start RebootX On-Prem integration: $_" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "📋 Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.rebootx.yml ps

# Display access information
Write-Host ""
Write-Host "🎉 RebootX On-Prem Integration is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access Information:" -ForegroundColor Cyan
Write-Host "  • RebootX On-Prem API: http://localhost:9001" -ForegroundColor White
Write-Host "  • Swagger UI: http://localhost:9002" -ForegroundColor White
Write-Host "  • API Documentation: http://localhost:9002/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Configuration for RebootX Mobile App:" -ForegroundColor Cyan
Write-Host "  • Server URL: http://localhost:9001" -ForegroundColor White
Write-Host "  • API Key: tailscale-mcp-rebootx-key-2024" -ForegroundColor White
Write-Host "  • Path Prefix: tailscale-mcp" -ForegroundColor White
Write-Host ""
Write-Host "📊 Available Runnables:" -ForegroundColor Cyan
Write-Host "  • Tailscale MCP Server (tailscale-mcp-001)" -ForegroundColor White
Write-Host "  • Grafana Dashboard (grafana-001)" -ForegroundColor White
Write-Host "  • Prometheus Metrics (prometheus-001)" -ForegroundColor White
Write-Host "  • Loki Log Aggregation (loki-001)" -ForegroundColor White
Write-Host ""
Write-Host "📈 Available Dashboards:" -ForegroundColor Cyan
Write-Host "  • Tailscale Network Overview" -ForegroundColor White
Write-Host "  • Monitoring Infrastructure" -ForegroundColor White
Write-Host "  • Security Metrics" -ForegroundColor White
Write-Host "  • Performance Metrics" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "  • View logs: docker-compose -f docker-compose.rebootx.yml logs -f" -ForegroundColor White
Write-Host "  • Stop services: docker-compose -f docker-compose.rebootx.yml down" -ForegroundColor White
Write-Host "  • Restart services: docker-compose -f docker-compose.rebootx.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: monitoring/rebootx-on-prem/README.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host "  1. Install RebootX mobile app from App Store/Google Play" -ForegroundColor White
Write-Host "  2. Add server with the configuration above" -ForegroundColor White
Write-Host "  3. Start monitoring your Tailscale infrastructure from your mobile device!" -ForegroundColor White
