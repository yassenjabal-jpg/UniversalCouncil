param(
    [int]$LocalPort = 47721,
    [string]$EvidencePath = ".\stage7-yassin-host-evidence.json"
)

$ErrorActionPreference = "Stop"

function Resolve-Tailscale {
    $command = Get-Command tailscale.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $fallback = "C:\Program Files\Tailscale\tailscale.exe"
    if (Test-Path $fallback) {
        return $fallback
    }

    return $null
}

function Test-EmptyJson([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $true
    }

    try {
        $parsed = $Text | ConvertFrom-Json -AsHashtable
        if ($null -eq $parsed) {
            return $true
        }
        return $parsed.Count -eq 0
    }
    catch {
        return $false
    }
}

$tailscale = Resolve-Tailscale
$installed = $null -ne $tailscale
$version = $null
$connectionState = "UNKNOWN"
$selfOnline = $false
$serveConfigured = $false
$funnelConfigured = $false

if ($installed) {
    $version = (& $tailscale version | Select-Object -First 1).Trim()

    $statusRaw = (& $tailscale status --json | Out-String).Trim()
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($statusRaw)) {
        $status = $statusRaw | ConvertFrom-Json
        if ($status.PSObject.Properties.Name -contains "BackendState") {
            $connectionState = [string]$status.BackendState
        }
        if ($status.PSObject.Properties.Name -contains "Self" -and $null -ne $status.Self) {
            if ($status.Self.PSObject.Properties.Name -contains "Online") {
                $selfOnline = [bool]$status.Self.Online
            }
        }
    }

    $serveRaw = (& $tailscale serve status --json 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) {
        $serveConfigured = -not (Test-EmptyJson $serveRaw)
    }

    $funnelRaw = (& $tailscale funnel status --json 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -eq 0) {
        $funnelConfigured = -not (Test-EmptyJson $funnelRaw)
    }
}

$localHealth = $false
try {
    $health = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:$LocalPort/healthz"
    $localHealth = $health.StatusCode -eq 200
}
catch {
    $localHealth = $false
}

$evidence = [ordered]@{
    schema_version = "1.0"
    evidence_type = "stage7_sanitized_yassin_host_probe"
    generated_at_utc = [DateTimeOffset]::UtcNow.ToString("O")
    target_host = "YASSIN"
    local_backend = "http://127.0.0.1:$LocalPort"
    tailscale_installed = $installed
    tailscale_version = $version
    tailscale_connection_state = $connectionState
    tailscale_self_online = $selfOnline
    tailscale_serve_configured = $serveConfigured
    tailscale_funnel_configured = $funnelConfigured
    remote_transport_local_health = $localHealth
    peer_list_persisted = $false
    account_identity_persisted = $false
    auth_key_persisted = $false
    bearer_token_persisted = $false
}

$directory = Split-Path -Parent $EvidencePath
if ($directory -and -not (Test-Path $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

$evidence | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $EvidencePath
$evidence | ConvertTo-Json -Depth 4

if ($funnelConfigured) {
    throw "Stage 7 host probe detected a Funnel configuration. Funnel is forbidden."
}
