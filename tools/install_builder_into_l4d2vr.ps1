param(
    [Parameter(Mandatory=$true)][string]$L4D2VRSource
)

$ErrorActionPreference = "Stop"
$builder = Join-Path $PSScriptRoot "..\integration\l4d2vr"
$projectDir = Join-Path $L4D2VRSource "L4D2VR"
$project = Join-Path $projectDir "l4d2vr.vcxproj"

if (-not (Test-Path $project)) {
    throw "Projet L4D2VR introuvable: $project"
}

Copy-Item (Join-Path $builder "builder_client.h") $projectDir -Force
Copy-Item (Join-Path $builder "builder_client.cpp") $projectDir -Force

[xml]$xml = Get-Content $project
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("m", "http://schemas.microsoft.com/developer/msbuild/2003")

function Add-ProjectItem([string]$type, [string]$include) {
    $existing = $xml.SelectSingleNode("//m:$type[@Include='$include']", $ns)
    if ($existing) { return }

    $group = $xml.SelectSingleNode("//m:ItemGroup[m:$type]", $ns)
    if (-not $group) {
        $group = $xml.CreateElement("ItemGroup", $xml.Project.NamespaceURI)
        [void]$xml.Project.AppendChild($group)
    }
    $node = $xml.CreateElement($type, $xml.Project.NamespaceURI)
    $node.SetAttribute("Include", $include)
    [void]$group.AppendChild($node)
}

Add-ProjectItem "ClInclude" "builder_client.h"
Add-ProjectItem "ClCompile" "builder_client.cpp"
$xml.Save($project)

Write-Host "Builder client installé dans le projet Visual Studio."
Write-Host "Il reste à instancier BuilderClient dans VR et à relier les actions Builder."
