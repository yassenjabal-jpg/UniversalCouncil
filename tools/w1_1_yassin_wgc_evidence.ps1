param(
    [string]$OutputRoot = "",
    [switch]$SkipLocalValidator
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$KitRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ShaPath = Join-Path $KitRoot "candidate-sha.txt"
$AppPath = Join-Path $KitRoot "app\UniversalCouncil.CommandCenter.UiSmoke.exe"
$ValidatorPath = Join-Path $KitRoot "command_center_p1_exit_evidence_validate.py"

if (-not (Test-Path $ShaPath)) { throw "candidate-sha.txt is missing from the host kit." }
if (-not (Test-Path $AppPath)) { throw "Published UiSmoke executable is missing from the host kit." }

$CandidateSha = (Get-Content -Raw $ShaPath).Trim().ToLowerInvariant()
if ($CandidateSha -notmatch "^[0-9a-f]{40}$") { throw "Host kit candidate SHA is invalid." }
$env:CANDIDATE_SHA = $CandidateSha

if (-not $OutputRoot) {
    $OutputRoot = Join-Path $KitRoot ("evidence-" + $CandidateSha.Substring(0,12))
}
$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$Full = Join-Path $OutputRoot "full"
$Reduced = Join-Path $OutputRoot "reduced"
New-Item -ItemType Directory -Force $Full,$Reduced | Out-Null

foreach ($tool in @("ffmpeg","ffprobe")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "$tool is required on YASSIN for governed evidence encoding."
    }
}

Write-Host "W1.1 YASSIN WGC evidence candidate: $CandidateSha"
Write-Host "Output: $OutputRoot"

& $AppPath $Full --wgc-motion-evidence
if ($LASTEXITCODE -ne 0) { throw "Full Motion WGC capture failed with exit code $LASTEXITCODE." }

& $AppPath $Reduced --wgc-motion-evidence --reduced-motion
if ($LASTEXITCODE -ne 0) { throw "Reduced Motion WGC capture failed with exit code $LASTEXITCODE." }

ffmpeg -y -framerate 30 -i (Join-Path $Full "frames\frame-%04d.png") -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p (Join-Path $Full "p1-critical-path-motion.mp4")
ffmpeg -y -framerate 30 -i (Join-Path $Reduced "frames\frame-%04d.png") -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p (Join-Path $Reduced "p1-critical-path-reduced-motion.mp4")

foreach ($mode in @("full","reduced")) {
    $Folder = Join-Path $OutputRoot $mode
    $File = if ($mode -eq "full") { "p1-critical-path-motion.mp4" } else { "p1-critical-path-reduced-motion.mp4" }
    $Path = Join-Path $Folder $File
    $Duration = [double](ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $Path)
    $Hash = (Get-FileHash -Algorithm SHA256 $Path).Hash.ToLowerInvariant()
    @{
        schema_version = "1.1"
        file = $File
        sha256 = $Hash
        bytes = (Get-Item $Path).Length
        duration_seconds = $Duration
        candidate_sha = $CandidateSha
        frame_rate = 30
        source = "RAW_WGC_HWND_FRAME_SEQUENCE"
        unedited = $true
        optical_flow = $false
        frame_interpolation = $false
        post_produced_animation = $false
    } | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $Folder "motion-video-integrity.json")
}

$ValidatorRan = $false
$ValidatorPassed = $false
if (-not $SkipLocalValidator) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        & $Python.Source $ValidatorPath --evidence-root $OutputRoot --wpf-only
        $ValidatorRan = $true
        if ($LASTEXITCODE -ne 0) { throw "Al-Murtakaz WPF-only validator rejected YASSIN evidence." }
        $ValidatorPassed = $true
    } else {
        Write-Warning "Python is unavailable on YASSIN; evidence is generated but local validator was not run."
    }
}

$Bundle = "$OutputRoot.zip"
if (Test-Path $Bundle) { Remove-Item $Bundle -Force }
Compress-Archive -Path (Join-Path $OutputRoot "*") -DestinationPath $Bundle -CompressionLevel Fastest
$BundleHash = (Get-FileHash -Algorithm SHA256 $Bundle).Hash.ToLowerInvariant()

@{
    schema_version = "1.0"
    candidate_sha = $CandidateSha
    host = $env:COMPUTERNAME
    capture_source = "RAW_WGC_PERSISTENT/WKI_CLIPPER_PATTERN"
    evidence_root = $OutputRoot
    bundle = $Bundle
    bundle_sha256 = $BundleHash
    local_validator_ran = $ValidatorRan
    local_validator_passed = $ValidatorPassed
    runtime_authority = $false
    stage8_opened = $false
    w1_2_started = $false
    merge_authorized = $false
} | ConvertTo-Json | Set-Content -Encoding UTF8 "$OutputRoot.host-result.json"

Write-Host "YASSIN WGC evidence bundle: $Bundle"
Write-Host "SHA256: $BundleHash"
