param(
    [string]$Repo = "",
    [string]$Model = "qwen3:4b-instruct",
    [switch]$RequireModel,
    [int]$ConsecutivePasses = 10
)

$ErrorActionPreference = "Stop"

if ($env:COMPUTERNAME.ToUpperInvariant() -ne "YASSIN") {
    throw "Health check is restricted to YASSIN only. Detected: $env:COMPUTERNAME"
}

if ([string]::IsNullOrWhiteSpace($Repo)) {
    $Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Invoke-YassinProbe {
    param([string]$RepoPath, [string]$ModelName, [bool]$NeedModel)

    $checks = [ordered]@{}
    $checks.computer = $env:COMPUTERNAME
    $checks.repo = $RepoPath
    $checks.git = [bool](Get-Command git -ErrorAction SilentlyContinue)
    $checks.python = [bool](Get-Command python -ErrorAction SilentlyContinue)
    $checks.nvidia_smi = [bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)
    $checks.ollama = [bool](Get-Command ollama -ErrorAction SilentlyContinue)
    $checks.gui_bridge = Test-Path "C:\Users\alnaseem\Desktop\CouncilVideoStudio\bridge\yassin_control\control_bridge.py"

    if (-not $checks.git -or -not $checks.python -or -not $checks.nvidia_smi -or -not $checks.gui_bridge) {
        return [pscustomobject]@{ pass = $false; checks = $checks; timestamp_utc = [DateTime]::UtcNow.ToString("o") }
    }
    if (-not (Test-Path $RepoPath)) {
        return [pscustomobject]@{ pass = $false; checks = $checks; timestamp_utc = [DateTime]::UtcNow.ToString("o") }
    }

    $checks.branch = (git -C $RepoPath branch --show-current).Trim()
    $checks.head = (git -C $RepoPath rev-parse HEAD).Trim()
    $checks.branch_ok = ($checks.branch -eq "experiment/agent-runtime-bakeoff-20261013")
    $checks.head_ok = ($checks.head.Length -eq 40)

    $eDrive = Get-PSDrive -Name E -PSProvider FileSystem -ErrorAction SilentlyContinue
    $checks.e_free_gb = if ($eDrive) { [math]::Round($eDrive.Free / 1GB, 2) } else { 0 }
    $checks.e_space_ok = [bool]($eDrive -and $eDrive.Free -ge 8GB)

    $gpuLine = (& nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader,nounits | Select-Object -First 1)
    if ($gpuLine) {
        $gpuParts = $gpuLine -split ",\s*"
        $checks.gpu_name = $gpuParts[0]
        $checks.gpu_vram_total_mib = [int]$gpuParts[1]
        $checks.gpu_vram_free_mib = [int]$gpuParts[2]
        $checks.gpu_driver = $gpuParts[3]
        $checks.gpu_ok = ($checks.gpu_vram_total_mib -ge 7000)
    } else {
        $checks.gpu_ok = $false
    }

    $checks.ollama_endpoint = "http://127.0.0.1:11434"
    $checks.ollama_ready = $false
    $checks.model_ready = $false
    if ($checks.ollama) {
        try {
            $tags = Invoke-RestMethod -Uri "$($checks.ollama_endpoint)/api/tags" -TimeoutSec 3
            $checks.ollama_ready = $true
            foreach ($item in $tags.models) {
                if ($item.name -eq $ModelName -or $item.model -eq $ModelName) {
                    $checks.model_ready = $true
                    $checks.model_digest = $item.digest
                    break
                }
            }
        } catch {
            $checks.ollama_ready = $false
        }
    }

    $required = @(
        $checks.branch_ok,
        $checks.head_ok,
        $checks.e_space_ok,
        $checks.gpu_ok,
        $checks.gui_bridge,
        $checks.ollama_ready
    )
    if ($NeedModel) {
        $required += $checks.model_ready
    }
    $pass = -not ($required -contains $false)
    return [pscustomobject]@{ pass = $pass; checks = $checks; timestamp_utc = [DateTime]::UtcNow.ToString("o") }
}

$probes = @()
for ($i = 1; $i -le $ConsecutivePasses; $i++) {
    $probe = Invoke-YassinProbe -RepoPath $Repo -ModelName $Model -NeedModel ([bool]$RequireModel)
    $probes += $probe
    if (-not $probe.pass) {
        $receipt = [ordered]@{
            status = "FAILED"
            host = "YASSIN"
            required_consecutive_passes = $ConsecutivePasses
            completed_passes = ($i - 1)
            cost_usd = 0
            probes = $probes
        }
        $out = Join-Path $Repo "benchmarks\agent_runtime\yassin_health_receipt.json"
        $receipt | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $out
        $receipt | ConvertTo-Json -Depth 12
        exit 3
    }
    Start-Sleep -Seconds 1
}

$final = [ordered]@{
    status = "YASSIN_HEALTH_OK"
    host = "YASSIN"
    required_consecutive_passes = $ConsecutivePasses
    completed_passes = $ConsecutivePasses
    cost_usd = 0
    probes = $probes
}
$out = Join-Path $Repo "benchmarks\agent_runtime\yassin_health_receipt.json"
$final | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $out
$final | ConvertTo-Json -Depth 12
