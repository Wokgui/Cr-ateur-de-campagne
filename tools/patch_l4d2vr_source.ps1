param(
    [Parameter(Mandatory=$true)][string]$L4D2VRSource
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path $L4D2VRSource).Path
$projectDir = Join-Path $root "L4D2VR"
$builderDir = (Resolve-Path (Join-Path $PSScriptRoot "..\integration\l4d2vr")).Path

Copy-Item (Join-Path $builderDir "builder_client.h") $projectDir -Force
Copy-Item (Join-Path $builderDir "builder_client.cpp") $projectDir -Force

$project = Join-Path $projectDir "l4d2vr.vcxproj"
[xml]$xml = Get-Content $project
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("m", "http://schemas.microsoft.com/developer/msbuild/2003")

function Add-Item([string]$type,[string]$include) {
  if ($xml.SelectSingleNode("//m:$type[@Include='$include']", $ns)) { return }
  $group = $xml.SelectSingleNode("//m:ItemGroup[m:$type]", $ns)
  $node = $xml.CreateElement($type, $xml.Project.NamespaceURI)
  $node.SetAttribute("Include", $include)
  [void]$group.AppendChild($node)
}
Add-Item "ClInclude" "builder_client.h"
Add-Item "ClCompile" "builder_client.cpp"
$xml.Save($project)

# Ensure WinHTTP is linked by the project as well as via pragma.
$vcx = Get-Content $project -Raw
$vcx = $vcx -replace 'openvr_api\.lib;libMinHook\.x86\.lib;', 'winhttp.lib;openvr_api.lib;libMinHook.x86.lib;'
Set-Content $project $vcx -Encoding UTF8

Write-Host "Campaign Builder source files patched into upstream L4D2VR."
