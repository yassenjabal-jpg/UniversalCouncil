param(
    [ValidateSet("Preflight","Canary","Representative","Full","Evaluate")]
    [string]$Stage = "Preflight",
    [string]$Repo = "C:\Users\alnaseem\Desktop\UniversalCouncil-bakeoff",
    [string]$Model = "qwen3:4b-instruct"
)

$ErrorActionPreference = "Stop"

if ($env:COMPUTERNAME.ToUpperInvariant() -ne "YASSIN") { throw "Universal Council live bake-off is restricted to YASSIN." }
if (-not (Test-Path $Repo)) { throw "Repository not found: $Repo" }

Set-Location $Repo
$branch = (git branch --show-current).Trim()
if ($branch -ne "experiment/agent-runtime-bakeoff-20261013") { throw "Wrong branch: $branch" }
$dirty = git status --porcelain
if ($dirty) { throw "Working tree must be clean before YASSIN bake-off execution." }

$venv = Join-Path $Repo ".venv-bakeoff"
$python = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $python)) { python -m venv $venv }
& $python -m pip install --disable-pip-version-check --no-input -r "benchmarks\agent_runtime\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
} catch {
    & "$Repo\tools\setup_local_ollama.ps1" -Model $Model -ModelsDir "E:\OllamaModels"
    if ($LASTEXITCODE -ne 0) { throw "Local Ollama setup failed." }
}

& $python "tools\build_agent_bakeoff_packets.py"
if ($LASTEXITCODE -ne 0) { throw "Masked packet generation failed." }

& $python -m unittest company.tests.test_agent_bakeoff company.tests.test_agent_bakeoff_live company.tests.test_agent_bakeoff_desktop_gate company.tests.test_agent_bakeoff_remediation
if ($LASTEXITCODE -ne 0) { throw "Bake-off unit tests failed." }

& $python "tools\validate_config.py"
if ($LASTEXITCODE -ne 0) { throw "Repository validation failed." }

& "$Repo\tools\yassin_bakeoff_health.ps1" -Repo $Repo -Model $Model -RequireModel -ConsecutivePasses 10
if ($LASTEXITCODE -ne 0) { throw "YASSIN health gate failed." }

if ($Stage -eq "Preflight") {
    Write-Output '{"status":"PREFLIGHT_PASS","host":"YASSIN","cost_usd":0}'
    exit 0
}

if ($Stage -eq "Evaluate") {
    & $python "tools\run_agent_bakeoff.py"
    exit $LASTEXITCODE
}

$stageArg = switch ($Stage) {
    "Canary" { "canary" }
    "Representative" { "representative" }
    "Full" { "full" }
}

& $python "tools\run_agent_bakeoff_live.py" --stage $stageArg --runtime all --model $Model --endpoint "http://127.0.0.1:11434" --resume
exit $LASTEXITCODE
