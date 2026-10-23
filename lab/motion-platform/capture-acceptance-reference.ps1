param(
    [string]$OutputDirectory = "lab/motion-platform/evidence/yassin-20261023-acceptance"
)

$ErrorActionPreference = "Stop"
$out = Join-Path (Get-Location) $OutputDirectory
New-Item -ItemType Directory -Force -Path $out | Out-Null

$stdout = Join-Path $out "skia-acceptance.stdout.txt"
$stderr = Join-Path $out "skia-acceptance.stderr.txt"
$exitFile = Join-Path $out "skia-acceptance.exitcode.txt"

$ErrorActionPreference = "Continue"
& dotnet run --project apps/UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe -c Release -- $out 1> $stdout 2> $stderr
$code = $LASTEXITCODE
$ErrorActionPreference = "Stop"
[IO.File]::WriteAllText($exitFile, [string]$code, [Text.UTF8Encoding]::new($false))

if ($code -ne 0) {
    throw "Skia WPF reference acceptance exited with code $code"
}

if ((Get-Item $stderr).Length -ne 0) {
    throw "Skia WPF reference acceptance produced stderr"
}

Write-Output "MotionKit MP3 reference acceptance capture: PASS"
