param(
    [Parameter(Mandatory=$true)][string]$BuilderDll,
    [string]$L4D2,
    [string]$ExpectedSha256 = "647b4d71c3695026ba0f99c89a61e4885ffd471579cee9400cfb6ef03c232270",
    [switch]$Restore
)
$ErrorActionPreference = "Stop"

function Find-L4D2([string]$Explicit) {
    if ($Explicit) {
        if (Test-Path (Join-Path $Explicit "left4dead2")) { return (Resolve-Path $Explicit).Path }
        throw "Installation L4D2 invalide: $Explicit"
    }
    $roots=@("$env:ProgramFiles(x86)\Steam","$env:ProgramFiles\Steam") | Where-Object { $_ -and (Test-Path $_) }
    foreach($steam in $roots) {
        $c=Join-Path $steam "steamapps\common\Left 4 Dead 2"
        if(Test-Path (Join-Path $c "left4dead2")) { return $c }
        $vdf=Join-Path $steam "steamapps\libraryfolders.vdf"
        if(Test-Path $vdf) {
            $text=Get-Content $vdf -Raw
            foreach($m in [regex]::Matches($text,'"path"\s+"([^"]+)"')) {
                $root=$m.Groups[1].Value -replace '\\\\','\'
                $c=Join-Path $root "steamapps\common\Left 4 Dead 2"
                if(Test-Path (Join-Path $c "left4dead2")) { return $c }
            }
        }
    }
    throw "Left 4 Dead 2 introuvable. Utilisez -L4D2."
}

$game=Find-L4D2 $L4D2
$target=Join-Path $game "bin\d3d9.dll"
$backupDir=Join-Path $game "bin\l4d2vr-builder-backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

if($Restore) {
    $backup=Get-ChildItem $backupDir -Filter "d3d9.*.dll" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if(-not $backup) { throw "Aucune sauvegarde L4D2VR trouvee dans $backupDir" }
    Copy-Item $backup.FullName $target -Force
    Write-Host "DLL restauree depuis: $($backup.FullName)"
    exit 0
}

if(-not (Test-Path $BuilderDll)) { throw "DLL Builder introuvable: $BuilderDll" }
$actual=(Get-FileHash $BuilderDll -Algorithm SHA256).Hash.ToLowerInvariant()
if($ExpectedSha256 -and $actual -ne $ExpectedSha256.ToLowerInvariant()) {
    throw "SHA-256 inattendu. Attendu: $ExpectedSha256 ; obtenu: $actual"
}

if(Test-Path $target) {
    $stamp=Get-Date -Format "yyyyMMdd-HHmmss"
    $backup=Join-Path $backupDir "d3d9.$stamp.dll"
    Copy-Item $target $backup -Force
    Write-Host "DLL L4D2VR actuelle sauvegardee: $backup"
}

Copy-Item $BuilderDll $target -Force
$installed=(Get-FileHash $target -Algorithm SHA256).Hash.ToLowerInvariant()
if($installed -ne $actual) { throw "Verification apres copie echouee." }

Write-Host "Builder installe: $target"
Write-Host "SHA-256: $installed"
Write-Host "Pour restaurer la derniere sauvegarde, relancez ce script avec -Restore."
