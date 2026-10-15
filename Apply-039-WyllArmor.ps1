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

function Add-Attr([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = $Doc.CreateElement('attribute')
    $a.SetAttribute('id', $Id)
    $a.SetAttribute('type', $Type)
    $a.SetAttribute('value', $Value)
    [void]$Node.AppendChild($a)
    return $a
}

# Wyll: custom Legendary copy of Leather Armour +2.
# Vanilla source: ac71c753-c207-465c-b28b-c10f95ed0745 / ARM_Leather_Body_2.
# Colour is applied later to the created instance by BootstrapServer.lua via
# ItemDye. Do not add ColorPreset here: root-level and instance-level dye state
# must not compete with each other.
$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)
if (-not $stats.Contains('new entry "LPA_WyllLeatherArmor"')) {
$stats += @'

new entry "LPA_WyllLeatherArmor"
type "Armor"
using "ARM_Leather_Body_2"
data "RootTemplate" "def74bcd-48a7-55c2-99d6-9b72e66c2fe0"
data "Unique" "0"
data "Rarity" "Legendary"
'@
    [IO.File]::WriteAllText($statsPath, $stats, $utf8)
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$existing = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='def74bcd-48a7-55c2-99d6-9b72e66c2fe0']]")
if ($null -eq $existing) {
    $parent = $roots.SelectSingleNode("/save/region[@id='Templates']/node[@id='Templates']/children")
    if ($null -eq $parent) { throw 'Missing root template container' }

    $n = $roots.CreateElement('node')
    $n.SetAttribute('id','GameObjects')
    [void](Add-Attr $roots $n 'LevelName' 'FixedString' '')
    [void](Add-Attr $roots $n 'MapKey' 'FixedString' 'def74bcd-48a7-55c2-99d6-9b72e66c2fe0')
    [void](Add-Attr $roots $n 'Name' 'LSString' 'LPA_WyllLeatherArmor')
    [void](Add-Attr $roots $n 'ParentTemplateId' 'FixedString' 'ac71c753-c207-465c-b28b-c10f95ed0745')
    [void](Add-Attr $roots $n 'Stats' 'FixedString' 'LPA_WyllLeatherArmor')
    [void](Add-Attr $roots $n 'Type' 'FixedString' 'item')
    [void]$parent.AppendChild($n)
}
Save-XmlUtf8 $roots $rootsPath

Write-Host "Applied Wyll Leather Armour +2 custom copy for $Mode."
