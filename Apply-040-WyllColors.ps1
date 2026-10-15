param(
    [Parameter(Mandatory=$true)][string]$StageRoot,
    [Parameter(Mandatory=$true)][ValidateSet('preview','final')][string]$Mode
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Save-XmlUtf8([xml]$Doc, [string]$Path) {
    $settings = New-Object System.Xml.XmlWriterSettings
    $settings.Encoding = $utf8
    $settings.Indent = $true
    $settings.IndentChars = "`t"
    $settings.NewLineChars = "`n"
    $settings.NewLineHandling = [System.Xml.NewLineHandling]::Replace
    $writer = [System.Xml.XmlWriter]::Create($Path, $settings)
    try { $Doc.PSBase.Save($writer) } finally { $writer.Dispose() }
}

function Set-ColorPreset([xml]$Doc, [string]$Uuid, [string]$Preset) {
    $root = $Doc.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='$Uuid']]")
    if ($null -eq $root) { throw "Missing root template $Uuid" }
    $color = $root.SelectSingleNode("attribute[@id='ColorPreset']")
    if ($null -eq $color) {
        $color = $Doc.CreateElement('attribute')
        $color.SetAttribute('id','ColorPreset')
        [void]$root.AppendChild($color)
    }
    # Vanilla RootTemplates encode ColorPreset as type 31, not the textual 'guid' alias.
    $color.SetAttribute('type','31')
    $color.SetAttribute('value',$Preset)
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath

# Black and Azure / OBJ_Dye_BlackBlue.
$preset = 'b533d673-a221-613f-4be7-f2697bef97e0'
Set-ColorPreset $roots 'def74bcd-48a7-55c2-99d6-9b72e66c2fe0' $preset # Leather Armour +2 custom copy
Set-ColorPreset $roots '334a92c4-f2b6-5dd8-9eb5-6606b424253e' $preset # Deadeye of the Frontiers

Save-XmlUtf8 $roots $rootsPath
Write-Host "Applied Wyll Black and Azure presets for $Mode."
