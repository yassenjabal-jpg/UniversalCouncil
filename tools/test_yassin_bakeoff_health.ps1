param(
    [string]$Repo = "C:\Users\alnaseem\Desktop\UniversalCouncil-bakeoff",
    [int]$ConsecutivePasses = 10
)

$ErrorActionPreference = "Stop"

if ($env:COMPUTERNAME.ToUpperInvariant() -ne "YASSIN") {
    throw "This health probe is restricted to YASSIN."
}

function Test-OneProbe {
    param([string]$RepoPath)

    $checks = [ordered]@{}
    $checks["host_is_yassin"] = ($env:COMPUTERNAME.ToUpperInvariant() -eq "YASSIN")
    $checks["repo_exists"] = Test-Path $RepoPath
    $checks["git_available"] = [bool](Get-Command git -ErrorAction SilentlyContinue)
    $checks["python_available"] = [bool](Get-Command python -ErrorAction SilentlyContinue)
    $checks["nvidia_smi_available"] = [bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)
    $checks["e_drive_exists"] = Test-Path "E:\"
    $checks["gui_bridge_exists"] = Test-Path "C:\Users\alnaseem\Desktop\CouncilVideoStudio\bridge\yassin_control\control_bridge.py"

    if ($checks["repo_exists"] -and $checks["git_available"]) {
        try {
            $head = (git -C $RepoPath rev-parse HEAD).Trim()
            $branch = (git -C $RepoPath branch --show-current).Trim()
            $checks["git_head_readable"] = ($head.Length -eq 40)
            $checks["experiment_branch"] = ($branch -eq "experiment/agent-runtime-bakeoff-20261013")
        } catch {
            $checks["git_head_readable"] = $false
            $checks["experiment_branch"] = $false
        }
    } else {
        $checks["git_head_readable"] = $false
        $checks["experiment_branch"] = $false
    }

    if ($checks["e_drive_exists"]) {
        $drive = Get-PSDrive E
        $checks["e_free_gb"] = [math]::Round($drive.Free / 1GB, 1)
        $checks["e_space_ok"] = ($drive.Free -ge 8GB)
    } else {
        $checks["e_free_gb"] = 0
        $checks["e_space_ok"] = $false
    }

    if ($checks["nvidia_smi_available"]) {
        try {
            $gpu = nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits | Select-Object -First 1
            $parts = $gpu -split ","
            $checks["gpu_name"] = $parts[0].Trim()
            $checks["gpu_vram_mb"] = [int]$parts[1].Trim()
            $checks["gpu_free_mb"] = [int]$parts[2].Trim()
            $checks["gpu_ok"] = ($checks["gpu_vram_mb"] -ge 7000)
        } catch {
            $checks["gpu_ok"] = $false
        }
    } else {
        $checks["gpu_ok"] = $false
    }

    try {
        $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
        $checks["ollama_local"] = $true
        $checks["ollama_model_count"] = @($tags.models).Count
    } catch {
        $checks["ollama_local"] = $false
        $checks["ollama_model_count"] = 0
    }

    $required = @(
        "host_is_yassin",
        "repo_exists",
        "git_available",
        "python_available",
        "nvidia_smi_available",
        "e_drive_exists",
        "gui_bridge_exists",
        "git_head_readable",
        "experiment_branch",
        "e_space_ok",
        "gpu_ok",
        "ollama_local"
    )
    $pass = $true
    foreach ($key in $required) {
        if ($checks[$key] -ne $true) {
            $pass = $false
        }
    }

    return [pscustomobject]@{
        pass = $pass
        timestamp_utc = [DateTime]::UtcNow.ToString("o")
        checks = $checks
    }
}

$probes = @()
for ($i = 1; $i -le $ConsecutivePasses; $i++) {
    $probe = Test-OneProbe -RepoPath $Repo
    $probes += $probe
    if (-not $probe.pass) {
        $receipt = [ordered]@{
            status = "FAILED"
            host = "YASSIN"
            required_consecutive_passes = $ConsecutivePasses
            completed_passes = ($i - 1)
            probes = $probes
        }
        $out = Join-Path $Repo "benchmarks\agent_runtime\yassin_health_receipt.json"
        $receipt | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $out
        $receipt | ConvertTo-Json -Depth 10
        exit 3
    }
    Start-Sleep -Seconds 1
}

$final = [ordered]@{
    status = "PASS"
    host = "YASSIN"
    required_consecutive_passes = $ConsecutivePasses
    completed_passes = $ConsecutivePasses
    probes = $probes
}
$out = Join-Path $Repo "benchmarks\agent_runtime\yassin_health_receipt.json"
$final | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $out
$final | ConvertTo-Json -Depth 10
