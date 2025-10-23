# TailscaleMCP Setup Script
# FastMCP 2.10 compliant Tailscale controller

# Create necessary directories
$directories = @(
    "src",
    "tests",
    "docs",
    "scripts",
    "config"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path ".\$dir" | Out-Null
}

# Create basic files
$files = @{
    "README.md" = @"
# TailscaleMCP - Tailscale Network Controller MCP

FastMCP 2.10 compliant implementation for managing Tailscale networks.

## Features
- Tailscale node management
- Network ACL configuration
- Device authorization
- DNS configuration
- Subnet routing
- DHT support
- DXT support for natural language control

## Quick Start

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

2. Configure Tailscale API key in `config/settings.yaml`

3. Start the MCP server:
   ```powershell
   .\run.ps1
   ```

## DXT Examples
- "List all devices in the Tailnet"
- "Authorize device with ID d123456"
- "Enable subnet routing on 192.168.1.0/24"
- "Show network status"
- "Ping all active nodes"
- "Create DNS record api.internal -> 100.64.0.1"
- "Block inbound traffic to port 22"
"@

    "requirements.txt" = @"
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0
python-dotenv>=0.19.0
httpx>=0.23.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.5
"@

    "src\main.py" = @"
"""TailscaleMCP Main Module"""
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import yaml
import os
from pathlib import Path
import httpx
from jose import JWTError, jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tailscalemcp")

app = FastAPI(title="TailscaleMCP", version="1.0.0")

# Configuration
CONFIG_PATH = Path("config/settings.yaml")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TailscaleConfig(BaseModel):
    api_key: str
    tailnet: str
    api_url: str = "https://api.tailscale.com/api/v2"

class Device(BaseModel):
    id: str
    name: str
    ip: str
    online: bool
    last_seen: str

# State
config: Optional[TailscaleConfig] = None

async def get_tailscale_client() -> httpx.AsyncClient:
    """Create authenticated Tailscale API client"""
    if not config:
        raise HTTPException(status_code=500, detail="Configuration not loaded")
    
    client = httpx.AsyncClient(
        base_url=config.api_url,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    )
    return client

@app.on_event("startup")
async def startup_event():
    """Initialize Tailscale controller"""
    logger.info("Starting TailscaleMCP...")
    global config
    
    # Load configuration
    if not CONFIG_PATH.exists():
        logger.warning("No configuration file found. Creating default...")
        create_default_config()
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config_data = yaml.safe_load(f)
            config = TailscaleConfig(**config_data['tailscale'])
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

@app.get("/api/devices", response_model=List[Device])
async def list_devices():
    """List all devices in the Tailnet"""
    try:
        async with await get_tailscale_client() as client:
            response = await client.get(f"/tailnet/{config.tailnet}/devices")
            response.raise_for_status()
            return response.json().get('devices', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/{device_id}/authorize")
async def authorize_device(device_id: str):
    """Authorize a device in the Tailnet"""
    try:
        async with await get_tailscale_client() as client:
            response = await client.post(
                f"/device/{device_id}/authorized",
                json={"authorized": True}
            )
            response.raise_for_status()
            return {"status": "success", "message": f"Authorized device {device_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
"@

    "config\settings.yaml" = @"
# TailscaleMCP Configuration

tailscale:
  api_key: "your-api-key-here"
  tailnet: "your-account-name"
  api_url: "https://api.tailscale.com/api/v2"

server:
  host: "0.0.0.0"
  port: 8002
  reload: true
  log_level: "info"

security:
  secret_key: "your-secret-key-here"
  algorithm: "HS256"
  access_token_expire_minutes: 30
"@

    "run.ps1" = @"
# Run script for TailscaleMCP
$env:PYTHONUNBUFFERED=1
$env:TAILSCALE_API_KEY="your-api-key-here"
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8002
"@
}

# Helper function to create default config
function create_default_config {
    $configDir = "config"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir | Out-Null
    }
    
    $defaultConfig = @"
# TailscaleMCP Configuration

tailscale:
  api_key: "your-api-key-here"
  tailnet: "your-account-name"
  api_url: "https://api.tailscale.com/api/v2"

server:
  host: "0.0.0.0"
  port: 8002
  reload: true
  log_level: "info"

security:
  secret_key: "your-secret-key-here"
  algorithm: "HS256"
  access_token_expire_minutes: 30
"@
    
    Set-Content -Path "$configDir\settings.yaml" -Value $defaultConfig -Encoding UTF8
}

# Create files
foreach ($file in $files.GetEnumerator()) {
    $filePath = $file.Name
    $directory = [System.IO.Path]::GetDirectoryName($filePath)
    
    if ($directory -and -not (Test-Path $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    
    Set-Content -Path $filePath -Value $file.Value -Encoding UTF8
}

Write-Host "TailscaleMCP project created successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. cd d:\Dev\repos\tailscalemcp"
Write-Host "2. .\setup.ps1"
Write-Host "3. Update config\settings.yaml with your Tailscale API key and tailnet name"
Write-Host "4. .\run.ps1"
