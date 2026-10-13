param(
    [string]$Model = "qwen3:4b-instruct",
    [string]$ModelsDir = "E:\OllamaModels"
)

$ErrorActionPreference = "Stop"

function Assert-LocalOllama {
    param([string]$Url = "http://127.0.0.1:11434")
    if ($Url -notmatch '^https?://(127\.0\.0\.1|localhost)(:\d+)?$') {
        throw "Only a local Ollama endpoint is allowed."
    }
}

Assert-LocalOllama

if (-not (Test-Path "E:\")) {
    throw "Drive E: is required for the zero-cost local model setup."
}

New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelsDir, "User")
$env:OLLAMA_MODELS = $ModelsDir

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "winget is not available and Ollama is not installed."
    }

    winget install --id Ollama.Ollama --exact --silent --accept-package-agreements --accept-source-agreements
    $candidate = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $candidate) {
        $env:PATH = "$(Split-Path $candidate);$env:PATH"
    }
}

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    $candidate = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (-not (Test-Path $candidate)) {
        throw "Ollama installation did not produce the expected executable."
    }
    $ollamaPath = $candidate
} else {
    $ollamaPath = $ollama.Source
}

$server = Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $server) {
    Start-Process -FilePath $ollamaPath -ArgumentList "serve" -WindowStyle Hidden
}

$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    throw "Local Ollama server did not become ready."
}

& $ollamaPath pull $Model
if ($LASTEXITCODE -ne 0) {
    throw "Failed to pull local model $Model"
}

$tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 10
$found = $false
foreach ($item in $tags.models) {
    if ($item.name -eq $Model -or $item.model -eq $Model) {
        $found = $true
        break
    }
}
if (-not $found) {
    throw "Model $Model was not found after pull."
}

$body = @{
    model = $Model
    stream = $false
    think = $false
    format = "json"
    messages = @(
        @{ role = "user"; content = 'Return only {"status":"LOCAL_OK"}' }
    )
    options = @{ temperature = 0; seed = 20261013 }
} | ConvertTo-Json -Depth 8

$probe = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/chat" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120

[pscustomobject]@{
    status = "READY"
    endpoint = "http://127.0.0.1:11434"
    model = $Model
    models_dir = $ModelsDir
    prompt_tokens = $probe.prompt_eval_count
    output_tokens = $probe.eval_count
    cost_usd = 0
    response = $probe.message.content
} | ConvertTo-Json -Depth 8
