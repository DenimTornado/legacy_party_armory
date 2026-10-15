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

$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)
if (-not $stats.Contains('new entry "LPA_WyllMarksmanHat"')) {
$stats += @'

new entry "LPA_WyllMarksmanHat"
type "Armor"
using "ARM_Hat"
data "RootTemplate" "334a92c4-f2b6-5dd8-9eb5-6606b424253e"
data "Unique" "0"
data "Rarity" "Legendary"
data "PassivesOnEquip" "MAG_Marksmanship_Passive;MAG_WYR_Orin_Bhaalist_Dagger_ImprovedCritical_Passive"
data "Boosts" "SpellSaveDC(1)"
'@
    [IO.File]::WriteAllText($statsPath, $stats, $utf8)
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$existing = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='334a92c4-f2b6-5dd8-9eb5-6606b424253e']]")
if ($null -eq $existing) {
    $parent = $roots.SelectSingleNode("/save/region[@id='Templates']/node[@id='Templates']/children")
    if ($null -eq $parent) { throw 'Missing root template container' }
    $n = $roots.CreateElement('node')
    $n.SetAttribute('id','GameObjects')
    [void](Add-Attr $roots $n 'Description' 'TranslatedString' '')
    $n.SelectSingleNode("attribute[@id='Description']").RemoveAttribute('value')
    $n.SelectSingleNode("attribute[@id='Description']").SetAttribute('handle','h0e54e6f0g29b8g5897ga09fgd4e6db301d6a')
    $n.SelectSingleNode("attribute[@id='Description']").SetAttribute('version','1')
    [void](Add-Attr $roots $n 'DisplayName' 'TranslatedString' '')
    $n.SelectSingleNode("attribute[@id='DisplayName']").RemoveAttribute('value')
    $n.SelectSingleNode("attribute[@id='DisplayName']").SetAttribute('handle','h74a3341dg1be9g528bgaf65gd0b8f94e5a22')
    $n.SelectSingleNode("attribute[@id='DisplayName']").SetAttribute('version','1')
    [void](Add-Attr $roots $n 'LevelName' 'FixedString' '')
    [void](Add-Attr $roots $n 'MapKey' 'FixedString' '334a92c4-f2b6-5dd8-9eb5-6606b424253e')
    [void](Add-Attr $roots $n 'Name' 'LSString' 'LPA_WyllMarksmanHat')
    [void](Add-Attr $roots $n 'ParentTemplateId' 'FixedString' 'f67b0733-ad73-4d1b-94fd-e3e0236623ca')
    [void](Add-Attr $roots $n 'Stats' 'FixedString' 'LPA_WyllMarksmanHat')
    [void](Add-Attr $roots $n 'Type' 'FixedString' 'item')
    [void]$parent.AppendChild($n)
}
Save-XmlUtf8 $roots $rootsPath

foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $list = $loc.SelectSingleNode('/contentList')
    $ru = $file.Directory.Name -eq 'Russian'
    $strings = @{
        'h74a3341dg1be9g528bgaf65gd0b8f94e5a22' = $(if ($ru) { 'Взор Пограничья' } else { 'Deadeye of the Frontiers' })
        'h0e54e6f0g29b8g5897ga09fgd4e6db301d6a' = $(if ($ru) { 'Один глаз может лгать, другой — быть камнем. Но цель всё равно остаётся целью. Эту шляпу носят те, кто привык замечать слабое место раньше, чем враг успеет понять, что его уже нашли.' } else { 'One eye may lie and the other may be stone. A target is still a target. This hat belongs to those who find the weak point before the enemy realises it has been seen.' })
    }
    foreach ($key in $strings.Keys) {
        $node = $loc.SelectSingleNode("/contentList/content[@contentuid='$key']")
        if ($null -eq $node) {
            $node = $loc.CreateElement('content')
            $node.SetAttribute('contentuid',$key)
            $node.SetAttribute('version','1')
            [void]$list.AppendChild($node)
        }
        $node.InnerText = $strings[$key]
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Wyll legendary marksman hat for $Mode."
