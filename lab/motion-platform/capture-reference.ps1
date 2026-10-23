$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = Join-Path (Get-Location) 'build/mp3-reference'
$exe = Join-Path (Get-Location) 'apps/UniversalCouncil.MotionKit.CompositionRuntimeProbe/bin/Release/net10.0-windows10.0.19041.0/UniversalCouncil.MotionKit.CompositionRuntimeProbe.exe'
$p = Start-Process -FilePath $exe -ArgumentList '--interactive', $out -PassThru -RedirectStandardOutput "$out/composition.stdout.txt" -RedirectStandardError "$out/composition.stderr.txt"
$processHandle = $p.Handle
$clock = [Diagnostics.Stopwatch]::StartNew()
Start-Sleep -Seconds 2
# Cropped to the observed probe window interior; excludes other desktop content.
foreach ($i in 0..29) {
  $bmp = [Drawing.Bitmap]::new(624,400)
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen(648,328,0,0,$bmp.Size)
  $bmp.Save("$out/composition-full-$($i.ToString('D2')).png")
  $g.Dispose()
  $bmp.Dispose()
  Start-Sleep -Milliseconds 100
}
while ($clock.Elapsed.TotalSeconds -lt 13) { Start-Sleep -Milliseconds 100 }
foreach ($i in 0..9) {
  $bmp = [Drawing.Bitmap]::new(624,400)
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen(648,328,0,0,$bmp.Size)
  $bmp.Save("$out/composition-reduced-$($i.ToString('D2')).png")
  $g.Dispose()
  $bmp.Dispose()
  Start-Sleep -Milliseconds 100
}
if (-not $p.WaitForExit(10000)) {
  Stop-Process -Id $p.Id
  throw 'Composition exceeded lifecycle budget'
}
if ($p.ExitCode -ne 0) { throw "Composition exit $($p.ExitCode)" }
"Composition capture and normal process exit: PASS"
