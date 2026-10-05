param([Parameter(Mandatory=$true)][string]$Package)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path $Package).Path
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('Builder test ' + [guid]::NewGuid())
$pkg = Join-Path $testRoot 'package with spaces'
$game = Join-Path $testRoot 'fake game'
$pidToStop = $null
try {
    New-Item -ItemType Directory -Path $pkg,(Join-Path $game 'left4dead2'),(Join-Path $game 'bin') -Force | Out-Null
    Copy-Item (Join-Path $source '*') $pkg -Recurse
    $target = Join-Path $game 'd3d9.dll'
    [IO.File]::WriteAllText($target,'original fixture DLL')
    $original = (Get-FileHash $target).Hash
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'install_builder_dll.ps1') -BuilderDll (Join-Path $pkg 'd3d9.dll') -L4D2 $game
    if ($LASTEXITCODE -ne 0) { throw 'Install failed' }
    if ((Get-FileHash $target).Hash -ne (Get-FileHash (Join-Path $pkg 'd3d9.dll')).Hash) { throw 'Copy mismatch' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'install_builder_dll.ps1') -BuilderDll (Join-Path $pkg 'd3d9.dll') -L4D2 $game
    if ($LASTEXITCODE -ne 0) { throw 'Repeat install failed' }
    if (@(Get-ChildItem (Join-Path $game 'l4d2vr-builder-backups')).Count -ne 1) { throw 'Original backup lost' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'install_builder_dll.ps1') -BuilderDll (Join-Path $pkg 'd3d9.dll') -L4D2 $game -Restore
    if ($LASTEXITCODE -ne 0 -or (Get-FileHash $target).Hash -ne $original) { throw 'Restore mismatch' }
    $ErrorActionPreference = 'Continue'
    $bad = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'install_builder_dll.ps1') -BuilderDll (Join-Path $pkg 'd3d9.dll') -L4D2 $game -ExpectedSha256 ('0'*64) 2>&1
    $ErrorActionPreference = 'Stop'
    if ($LASTEXITCODE -eq 0 -or (Get-FileHash $target).Hash -ne $original) { throw 'Bad hash accepted' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'start_builder.ps1') -NoLaunch -L4D2 $game
    if ($LASTEXITCODE -ne 0) { throw 'Standalone launcher failed' }
    $health = Invoke-RestMethod http://127.0.0.1:8765/health
    $pidToStop = $health.pid
    $body = @{command='cree une piece de 6 par 4 metres';pointer=@(0,0,0)} | ConvertTo-Json
    $result = Invoke-RestMethod http://127.0.0.1:8765/command -Method Post -Body $body -ContentType 'application/json'
    if (-not $result.ok -or -not (Test-Path (Join-Path $pkg 'build\live_scene.vmf'))) { throw 'VMF generation failed' }
    Write-Host 'WINDOWS_PACKAGE_SMOKE_OK: install, repeat, restore, bad hash, spaced paths, HTTP, VMF'
} finally {
    if ($pidToStop) { Stop-Process -Id $pidToStop -ErrorAction SilentlyContinue }
    if ($testRoot.StartsWith([IO.Path]::GetTempPath()) -and (Split-Path $testRoot -Leaf).StartsWith('Builder test ')) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
