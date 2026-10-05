param(
    [string]$L4D2,
    [switch]$NoLaunch,
    [switch]$ReindexAssets
)

$ErrorActionPreference = "Stop"
$parent = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (Test-Path (Join-Path $PSScriptRoot "src\vr_bridge.py")) {
    $RepoRoot = $PSScriptRoot
} else {
    $RepoRoot = $parent
}
$BuildDir = Join-Path $RepoRoot "build"
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

function Find-L4D2 {
    param([string]$Explicit)
    if ($Explicit) {
        if (Test-Path (Join-Path $Explicit "left4dead2")) { return (Resolve-Path $Explicit).Path }
        throw "Installation L4D2 invalide: $Explicit"
    }

    $steamRoots = @(
        "${env:ProgramFiles(x86)}\Steam",
        "$env:ProgramFiles\Steam"
    ) | Where-Object { $_ -and (Test-Path $_) }

    foreach ($steam in $steamRoots) {
        $candidate = Join-Path $steam "steamapps\common\Left 4 Dead 2"
        if (Test-Path (Join-Path $candidate "left4dead2")) { return $candidate }

        $vdf = Join-Path $steam "steamapps\libraryfolders.vdf"
        if (Test-Path $vdf) {
            $text = Get-Content $vdf -Raw
            foreach ($m in [regex]::Matches($text, '"path"\s+"([^"]+)"')) {
                $root = $m.Groups[1].Value -replace '\\\\','\'
                $candidate = Join-Path $root "steamapps\common\Left 4 Dead 2"
                if (Test-Path (Join-Path $candidate "left4dead2")) { return $candidate }
            }
        }
    }
    throw "Left 4 Dead 2 introuvable. Utilisez -L4D2 avec le chemin du jeu."
}

function Find-Python {
    foreach ($cmd in @("python", "py")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            $actual = & $cmd -c "import sys; print(sys.executable if sys.version_info >= (3,12) else '')" 2>$null
            if ($LASTEXITCODE -eq 0 -and $actual -and (Test-Path $actual)) { return $actual }
        }
    }
    throw "Python 3.12 ou plus recent est requis."
}

$GameRoot = Find-L4D2 $L4D2
$Python = Find-Python
$Catalog = Join-Path $BuildDir "assets.json"

Write-Host "L4D2: $GameRoot"
if ($ReindexAssets -or -not (Test-Path $Catalog)) {
    Write-Host "Indexation des assets L4D2..."
    & $Python (Join-Path $RepoRoot "src\asset_catalog.py") $GameRoot --out $Catalog
    if ($LASTEXITCODE -ne 0) { throw "Echec de l'indexation des assets." }
}

$bridgeArgs = @(
    ('"' + (Join-Path $RepoRoot "src\vr_bridge.py") + '"'),
    "--catalog", ('"' + $Catalog + '"')
)
Write-Host "Demarrage du pont Builder local..."
try {
    $existing = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1
} catch { $existing = $null }
if ($existing) { throw "Le port 8765 est deja utilise. Arretez le pont existant avant de relancer." }
$bridge = Start-Process -FilePath $Python -ArgumentList $bridgeArgs -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 200
    $bridge.Refresh()
    if ($bridge.HasExited) { throw "Le processus Python s'est arrete." }
    try {
        $probe = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1
        if ($probe.ok -and $probe.service -eq "l4d2vr-builder" -and $probe.pid -eq $bridge.Id) { $ready = $true; break }
    } catch {}
}
if (-not $ready) {
    Stop-Process -Id $bridge.Id -Force
    throw "Le pont Builder n'a pas demarre."
}
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -TimeoutSec 3
    Write-Host "Builder bridge: OK (PID $($bridge.Id))"
} catch {
    if (-not $bridge.HasExited) { Stop-Process -Id $bridge.Id -Force }
    throw "Le pont Builder n'a pas repondu sur 127.0.0.1:8765."
}

if (-not $NoLaunch) {
    $steam = Get-Command steam.exe -ErrorAction SilentlyContinue
    if ($steam) {
        Start-Process $steam.Source -ArgumentList "-applaunch 550 -insecure"
    } else {
        $exe = Join-Path $GameRoot "left4dead2.exe"
        if (-not (Test-Path $exe)) { throw "left4dead2.exe introuvable: $exe" }
        Start-Process $exe -ArgumentList "-steam -insecure"
    }
    Write-Host "L4D2 lance en mode -insecure."
}

Write-Host "Creation VR prete. Le pont reste actif tant que son processus Python tourne."
