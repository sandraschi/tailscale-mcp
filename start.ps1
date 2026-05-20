Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# tailscale-mcp Unified Start - delegates to web_sota/start.ps1
Write-Host 'Starting tailscale-mcp (delegating to web_sota/start.ps1)...' -ForegroundColor Cyan
& "$PSScriptRoot\web_sota\start.ps1" @PSBoundParameters
