param(
    [int]$LocalPort = 47721
)

$ErrorActionPreference = "Stop"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Stage 7 Tailscale Serve configuration requires an Administrator PowerShell session."
}

$tailscale = (Get-Command tailscale.exe -ErrorAction SilentlyContinue).Source
if (-not $tailscale) {
    $fallback = "C:\Program Files\Tailscale\tailscale.exe"
    if (Test-Path $fallback) {
        $tailscale = $fallback
    }
}
if (-not $tailscale) {
    throw "Tailscale is not installed or its CLI cannot be found."
}

$health = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:$LocalPort/healthz"
if ($health.StatusCode -ne 200) {
    throw "RemoteTransport local health is not 200."
}

$statusRaw = (& $tailscale status --json | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "tailscale status failed."
}
$status = $statusRaw | ConvertFrom-Json
if ($status.BackendState -ne "Running") {
    throw "Tailscale backend is not Running."
}

$funnelRaw = (& $tailscale funnel status --json 2>$null | Out-String).Trim()
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($funnelRaw)) {
    try {
        $funnel = $funnelRaw | ConvertFrom-Json -AsHashtable
        if ($null -ne $funnel -and $funnel.Count -gt 0) {
            throw "A Tailscale Funnel configuration exists. Stage 7 refuses to continue."
        }
    }
    catch {
        if ($_.Exception.Message -like "A Tailscale Funnel configuration exists*") {
            throw
        }
    }
}

$target = "http://127.0.0.1:$LocalPort"
& $tailscale serve --bg --yes $target
if ($LASTEXITCODE -ne 0) {
    throw "tailscale serve configuration failed."
}

$serveRaw = (& $tailscale serve status --json | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($serveRaw)) {
    throw "tailscale serve status verification failed."
}
if ($serveRaw -notmatch [regex]::Escape("127.0.0.1:$LocalPort")) {
    throw "Tailscale Serve does not point to the required Stage 7 loopback backend."
}

Write-Output "STAGE7_TAILSCALE_SERVE_CONFIGURED_PRIVATE_ONLY"
& $tailscale serve status
