# Start Tailscale MCP Monitoring Stack
# This script starts Grafana, Prometheus, Loki, and the Tailscale MCP server

Write-Host "🚀 Starting Tailscale MCP Monitoring Stack..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "📝 Please edit .env file with your Tailscale API credentials" -ForegroundColor Yellow
}

# Create logs directory
New-Item -ItemType Directory -Path "logs" -Force | Out-Null

# Start the monitoring stack
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Blue
docker-compose up -d

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Blue
docker-compose ps

# Display access information
Write-Host ""
Write-Host "🎉 Monitoring stack is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access URLs:" -ForegroundColor Cyan
Write-Host "  Grafana:     http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host "  Loki:        http://localhost:3100" -ForegroundColor White
Write-Host "  MCP Server:  http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "📝 To view logs:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop:" -ForegroundColor Cyan
Write-Host "  docker-compose down" -ForegroundColor White
