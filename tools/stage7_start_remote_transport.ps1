param(
    [Parameter(Mandatory = $true)]
    [string]$PublishDirectory,

    [Parameter(Mandatory = $true)]
    [string]$RegistryPath,

    [int]$LocalPort = 47721,

    [string]$RuntimeRoot = "$env:LOCALAPPDATA\UniversalCouncil\CommandCenter\RemoteTransport"
)

$ErrorActionPreference = "Stop"

$exe = Join-Path (Resolve-Path $PublishDirectory) "UniversalCouncil.CommandCenter.RemoteTransport.exe"
if (-not (Test-Path $exe)) {
    throw "RemoteTransport executable is missing: $exe"
}
if (-not (Test-Path $RegistryPath)) {
    throw "Owner enrollment registry is missing: $RegistryPath"
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

$existing = Get-NetTCPConnection -State Listen -LocalAddress 127.0.0.1 -LocalPort $LocalPort -ErrorAction SilentlyContinue
if ($existing) {
    throw "Port $LocalPort already has a loopback listener. Stage 7 will not replace it implicitly."
}

$arguments = @(
    "--port", "$LocalPort",
    "--registry", (Resolve-Path $RegistryPath).Path,
    "--runtime-root", (Resolve-Path $RuntimeRoot).Path
)

$process = Start-Process -FilePath $exe -ArgumentList $arguments -PassThru -WindowStyle Hidden

$healthy = $false
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    Start-Sleep -Milliseconds 250
    try {
        $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://127.0.0.1:$LocalPort/healthz"
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    }
    catch {
    }
}

if (-not $healthy) {
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
    throw "RemoteTransport failed local health verification."
}

[ordered]@{
    state = "STAGE7_REMOTE_TRANSPORT_RUNNING_LOOPBACK_ONLY"
    pid = $process.Id
    local_backend = "http://127.0.0.1:$LocalPort"
    execution_authorized = $false
} | ConvertTo-Json
