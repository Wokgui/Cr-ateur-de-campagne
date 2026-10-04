param(
    [Parameter(Mandatory=$true)][string]$Vmf,
    [string]$MapName = "vr_generated",
    [string]$L4D2 = "$env:ProgramFiles(x86)\Steam\steamapps\common\Left 4 Dead 2"
)

$ErrorActionPreference = "Stop"
$bin = Join-Path $L4D2 "bin"
$game = Join-Path $L4D2 "left4dead2"
$work = Resolve-Path $Vmf

$vbsp = Join-Path $bin "vbsp.exe"
$vvis = Join-Path $bin "vvis.exe"
$vrad = Join-Path $bin "vrad.exe"

foreach ($tool in @($vbsp,$vvis,$vrad)) {
    if (-not (Test-Path $tool)) { throw "Outil Source introuvable: $tool" }
}

& $vbsp -game $game $work
if ($LASTEXITCODE -ne 0) { throw "VBSP a échoué ($LASTEXITCODE)" }

$bsp = [IO.Path]::ChangeExtension($work, ".bsp")
& $vvis -game $game $bsp
if ($LASTEXITCODE -ne 0) { throw "VVIS a échoué ($LASTEXITCODE)" }

& $vrad -game $game -both -final $bsp
if ($LASTEXITCODE -ne 0) { throw "VRAD a échoué ($LASTEXITCODE)" }

$dest = Join-Path $game "maps\$MapName.bsp"
Copy-Item $bsp $dest -Force
Write-Host "Carte installée: $dest"
Write-Host "Dans la console L4D2: map $MapName"
