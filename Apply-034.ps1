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

function Attr($Node, [string]$Id) {
    return $Node.SelectSingleNode("attribute[@id='$Id']")
}

function Set-Attr([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = Attr $Node $Id
    if ($null -eq $a) {
        $a = $Doc.CreateElement('attribute')
        $a.SetAttribute('id', $Id)
        [void]$Node.AppendChild($a)
    }
    $a.SetAttribute('type', $Type)
    $a.SetAttribute('value', $Value)
}

function Remove-StatEntry([string]$Text, [string]$Name) {
    $escaped = [regex]::Escape($Name)
    return [regex]::Replace(
        $Text,
        "(?ms)(?:\r?\n)?new entry `"$escaped`"\r?\n.*?(?=\r?\nnew entry `"|\z)",
        ''
    )
}

# ---------------------------------------------------------------------------
# Stats: keep approved mechanics and replace only the visual-reference layer.
# ---------------------------------------------------------------------------
$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)

# Karlach: one Ashen Heartguard only. Keep the stable UUID and remove the two
# rejected preview variants.
$stats = $stats.Replace('new entry "LPA_AshenHeartguard_Unwanted"', 'new entry "LPA_AshenHeartguard"')
$stats = Remove-StatEntry $stats 'LPA_AshenHeartguard_Bloodguzzler'
$stats = Remove-StatEntry $stats 'LPA_AshenHeartguard_Mighty'

# Icingdeath uses Mourning Frost's stock frost weapon status, which already
# supplies the +1d4 Cold carried by our previous DefaultBoosts.
$stats = $stats.Replace(
    'data "DefaultBoosts" "WeaponEnchantment(2);WeaponProperty(Magical);WeaponDamage(1d4,Cold)"',
    'data "DefaultBoosts" "WeaponEnchantment(2);WeaponProperty(Magical)"'
)

# Twinkle uses the exact Gleamdance Dagger light toggle. The technical item
# status is installed on the root template below.
$stats = $stats.Replace(
    'data "PassivesOnEquip" "LPA_Defender"',
    'data "PassivesOnEquip" "LPA_Defender;MAG_Light_FarlinDagger_Passive"'
)

# Everburn's stock status also adds fire damage. Reuse only the stock item VFX
# so Dragon's Breath keeps its selectable 1d4 element without extra fire.
if (-not $stats.Contains('new entry "LPA_EVERBURN_VISUAL"')) {
$stats += @'

new entry "LPA_EVERBURN_VISUAL"
type "StatusData"
data "StatusType" "BOOST"
data "StatusEffectOverrideForItems" "44d77ebf-fc9e-407d-b20f-257019351f2a"
data "StackId" "LPA_EVERBURN_VISUAL"
data "StackPriority" "10"
data "SoundStart" ""
data "SoundStop" ""
data "StatusPropertyFlags" "DisableOverhead;IgnoreResting;DisableCombatlog;DisablePortraitIndicator"
'@
}

[IO.File]::WriteAllText($statsPath, $stats, $utf8)

# ---------------------------------------------------------------------------
# Root templates: stock VFX statuses, Karlach visual and Orin starting dye.
# ---------------------------------------------------------------------------
$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath

function Find-Root([xml]$Doc, [string]$Uuid) {
    return $Doc.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='$Uuid']]")
}

function Ensure-Status([xml]$Doc, [string]$Uuid, [string]$StatusId) {
    $root = Find-Root $Doc $Uuid
    if ($null -eq $root) { throw "Missing root template $Uuid" }

    $children = $root.SelectSingleNode('children')
    if ($null -eq $children) {
        $children = $Doc.CreateElement('children')
        [void]$root.AppendChild($children)
    }

    $statusList = $children.SelectSingleNode("node[@id='StatusList']")
    if ($null -eq $statusList) {
        $statusList = $Doc.CreateElement('node')
        $statusList.SetAttribute('id', 'StatusList')
        [void]$children.AppendChild($statusList)
    }

    $statusChildren = $statusList.SelectSingleNode('children')
    if ($null -eq $statusChildren) {
        $statusChildren = $Doc.CreateElement('children')
        [void]$statusList.AppendChild($statusChildren)
    }

    if ($null -eq $statusChildren.SelectSingleNode("node[@id='Status']/attribute[@id='Object' and @value='$StatusId']")) {
        $status = $Doc.CreateElement('node')
        $status.SetAttribute('id', 'Status')
        $object = $Doc.CreateElement('attribute')
        $object.SetAttribute('id', 'Object')
        $object.SetAttribute('type', 'FixedString')
        $object.SetAttribute('value', $StatusId)
        [void]$status.AppendChild($object)
        [void]$statusChildren.AppendChild($status)
    }
}

# Mourning Frost -> Icingdeath.
Ensure-Status $roots '66403a1f-6450-5a91-a2d9-9d23f5fdb555' 'MAG_FROST_FROST_WEAPON'

# Gleamdance Dagger -> Twinkle.
Ensure-Status $roots '92b759b8-117c-5056-b181-43c26b234fa1' 'MAG_FARLIN_DAGGER_LIGHT_TECHNICAL'

# Everburn Blade -> Dragon's Breath, visual-only.
Ensure-Status $roots '1c0f33c4-86d0-5a5e-941f-4d8db521cdcf' 'LPA_EVERBURN_VISUAL'

# Karlach's own unique starting barbarian clothes become the visual parent of
# Ashen Heartguard; mechanics remain the approved custom medium-armour profile.
$karlachRoot = Find-Root $roots 'aef31c6f-07a7-5b20-9007-e910ca009ea1'
if ($null -eq $karlachRoot) { throw 'Missing Ashen Heartguard root' }
Set-Attr $roots $karlachRoot 'ParentTemplateId' 'FixedString' '2e3a2651-18ce-44b0-b7bd-3e2565bf666c'
Set-Attr $roots $karlachRoot 'Name' 'LSString' 'LPA_AshenHeartguard'
Set-Attr $roots $karlachRoot 'Stats' 'FixedString' 'LPA_AshenHeartguard'

foreach ($oldUuid in @(
    '6211fd61-a504-5639-8281-fb67da2c4a84',
    'fe127a4f-e1d5-533b-a2aa-52f6ce7befaf'
)) {
    $old = Find-Root $roots $oldUuid
    if ($null -ne $old) { [void]$old.ParentNode.RemoveChild($old) }
}

# Orin dress: Black and Furnace Red dye preset. Keep the 0.3.3 model-slot fix:
# native Equipment remains Body, while Stats controls the camp clothing slot.
$orinRoot = Find-Root $roots '33bcf8bc-50ff-507b-aadf-53de85fb396d'
if ($null -eq $orinRoot) { throw 'Missing Orin vanity root' }
Set-Attr $roots $orinRoot 'ColorPreset' 'guid' '963387ce-05e6-a6bf-ac25-4d81624fa8ff'

Save-XmlUtf8 $roots $rootsPath

# ---------------------------------------------------------------------------
# Materials: stock statuses own the visible weapon effects. Shar set is lifted
# slightly brighter while staying black/lilac.
# ---------------------------------------------------------------------------
$assetsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsx'
[xml]$assets = Get-Content -Raw -LiteralPath $assetsPath

function Material-Name($Resource) {
    $a = Attr $Resource 'Name'
    if ($null -eq $a) { return '' }
    return $a.GetAttribute('value')
}

function Set-MaterialValue($Resource, [string]$ParamName, [string]$Value) {
    foreach ($p in $Resource.SelectNodes('children/node')) {
        $n = Attr $p 'ParameterName'
        if ($null -eq $n -or $n.GetAttribute('value') -ne $ParamName) { continue }
        foreach ($field in @('Value','BaseValue')) {
            $v = Attr $p $field
            if ($null -ne $v) { $v.SetAttribute('value', $Value) }
        }
        $enabled = Attr $p 'Enabled'
        if ($null -ne $enabled) { $enabled.SetAttribute('value', 'True') }
    }
}

$materials = $assets.SelectNodes("/save/region[@id='MaterialBank']/node[@id='MaterialBank']/children/node[@id='Resource']")
foreach ($m in $materials) {
    $name = Material-Name $m

    if ($name.StartsWith('LPA_SharSpear_') -or $name.StartsWith('LPA_WalkingFortress_')) {
        Set-MaterialValue $m 'Color' '0.16 0.035 0.24'
        Set-MaterialValue $m 'VariationColor' '0.22 0.06 0.32'
        Set-MaterialValue $m 'GlowMultiplier' '0'
        Set-MaterialValue $m 'GlowIntensity' '0'
    }

    if ($name.StartsWith('LPA_Icingdeath_') -or
        $name.StartsWith('LPA_Twinkle_') -or
        $name.StartsWith('LPA_DragonsBreath_')) {
        foreach ($p in @('GlowMultiplier','GlowIntensity','MinGlow','MaxGlow')) {
            Set-MaterialValue $m $p '0'
        }
    }
}

Save-XmlUtf8 $assets $assetsPath

# ---------------------------------------------------------------------------
# Localization: Karlach has one approved armour now, not a test variant.
# ---------------------------------------------------------------------------
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $name = $loc.SelectSingleNode("/contentList/content[@contentuid='he9f3a87eg4696g51ecg8485gf508c98a1c3a']")
    if ($null -ne $name) {
        $name.InnerText = if ($file.Directory.Name -eq 'Russian') { 'Страж Пепельного Сердца' } else { 'Ashen Heartguard' }
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Legacy Party Armory 0.3.4 $Mode source patch."
