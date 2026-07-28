# Per-repo fleet start config for tailscale-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'tailscale-mcp'
    BackendPort  = 10821
    FrontendPort = 10820
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\tailscale-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'tailscalemcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10821' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
