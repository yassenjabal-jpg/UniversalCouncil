param(
    [string]$Repo = "",
    [string]$Model = "qwen3:4b-instruct",
    [switch]$RequireModel
)

$ErrorActionPreference = "Stop"

if ($env:COMPUTERNAME.ToUpperInvariant() -ne "YASSIN") {
    throw "Health check is restricted to YASSIN only. Detected: $env:COMPUTERNAME"
}

if ([string]::IsNullOrWhiteSpace($Repo)) {
    $Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$checks = [ordered]@{}
$checks.computer = $env:COMPUTERNAME
$checks.repo = $Repo
$checks.git = [bool](Get-Command git -ErrorAction SilentlyContinue)
$checks.python = [bool](Get-Command python -ErrorAction SilentlyContinue)
$checks.nvidia_smi = [bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)
$checks.ollama = [bool](Get-Command ollama -ErrorAction SilentlyContinue)

if (-not $checks.git -or -not $checks.python -or -not $checks.nvidia_smi) {
    throw "Required YASSIN tooling is missing: git=$($checks.git) python=$($checks.python) nvidia-smi=$($checks.nvidia_smi)"
}

if (-not (Test-Path $Repo)) {
    throw "Repository path not found: $Repo"
}

$branch = (git -C $Repo branch --show-current).Trim()
$head = (git -C $Repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Git repository validation failed."
}
$checks.branch = $branch
$checks.head = $head

$expectedBranch = "experiment/agent-runtime-bakeoff-20261013"
if ($branch -ne $expectedBranch) {
    throw "YASSIN must run the bake-off from $expectedBranch; detected $branch"
}

$eDrive = Get-PSDrive -Name E -PSProvider FileSystem -ErrorAction Stop
$checks.e_free_gb = [math]::Round($eDrive.Free / 1GB, 2)
if ($checks.e_free_gb -lt 10) {
    throw "E: requires at least 10 GB free for local model/runtime artifacts."
}

$cDrive = Get-PSDrive -Name C -PSProvider FileSystem -ErrorAction Stop
$checks.c_free_gb = [math]::Round($cDrive.Free / 1GB, 2)

$gpuLine = (& nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader,nounits | Select-Object -First 1)
if (-not $gpuLine) {
    throw "nvidia-smi returned no GPU information."
}
$gpuParts = $gpuLine -split ",\s*"
$checks.gpu_name = $gpuParts[0]
$checks.gpu_vram_total_mib = [int]$gpuParts[1]
$checks.gpu_vram_free_mib = [int]$gpuParts[2]
$checks.gpu_driver = $gpuParts[3]
if ($checks.gpu_vram_total_mib -lt 7000) {
    throw "YASSIN GPU has insufficient VRAM for the selected local model policy."
}

$checks.ollama_endpoint = "http://127.0.0.1:11434"
$checks.ollama_ready = $false
$checks.model_ready = $false
if ($checks.ollama) {
    try {
        $tags = Invoke-RestMethod -Uri "$($checks.ollama_endpoint)/api/tags" -TimeoutSec 5
        $checks.ollama_ready = $true
        foreach ($item in $tags.models) {
            if ($item.name -eq $Model -or $item.model -eq $Model) {
                $checks.model_ready = $true
                $checks.model_digest = $item.digest
                break
            }
        }
    } catch {
        $checks.ollama_ready = $false
    }
}

if ($RequireModel -and (-not $checks.ollama_ready -or -not $checks.model_ready)) {
    throw "Local Ollama/model is not ready on YASSIN. Run tools/setup_local_ollama.ps1 first."
}

$checks.cost_usd = 0
$checks.status = "YASSIN_HEALTH_OK"
[pscustomobject]$checks | ConvertTo-Json -Depth 8
