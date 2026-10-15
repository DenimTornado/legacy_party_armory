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

function Add-AttributeNode([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = $Doc.CreateElement('attribute')
    $a.SetAttribute('id', $Id)
    $a.SetAttribute('type', $Type)
    $a.SetAttribute('value', $Value)
    [void]$Node.AppendChild($a)
    return $a
}

function Get-AttributeValue($Node, [string]$Id) {
    $a = $Node.SelectSingleNode("attribute[@id='$Id']")
    if ($null -eq $a) { return $null }
    return $a.GetAttribute('value')
}

function Set-AttributeValue([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = $Node.SelectSingleNode("attribute[@id='$Id']")
    if ($null -eq $a) { $a = Add-AttributeNode $Doc $Node $Id $Type $Value }
    $a.SetAttribute('type', $Type)
    $a.SetAttribute('value', $Value)
    return $a
}

function Find-MaterialParam($Resource, [string]$Name) {
    foreach ($n in $Resource.SelectNodes('children/node')) {
        $p = $n.SelectSingleNode("attribute[@id='ParameterName']")
        if ($null -ne $p -and $p.GetAttribute('value') -eq $Name) { return $n }
    }
    return $null
}

function Ensure-MaterialParam([xml]$Doc, $Resource, [string]$NodeId, [string]$Name, [string]$Value, [string]$ValueType) {
    $children = $Resource.SelectSingleNode('children')
    if ($null -eq $children) {
        $children = $Doc.CreateElement('children')
        [void]$Resource.AppendChild($children)
    }
    $node = Find-MaterialParam $Resource $Name
    if ($null -eq $node) {
        $node = $Doc.CreateElement('node')
        $node.SetAttribute('id', $NodeId)
        [void](Add-AttributeNode $Doc $node 'Enabled' 'bool' 'True')
        [void](Add-AttributeNode $Doc $node 'ExportAsPreset' 'bool' 'True')
        [void](Add-AttributeNode $Doc $node 'GroupName' 'FixedString' '')
        [void](Add-AttributeNode $Doc $node 'ParameterName' 'FixedString' $Name)
        [void]$children.AppendChild($node)
    }
    [void](Set-AttributeValue $Doc $node 'Enabled' 'bool' 'True')
    if ($NodeId -eq 'Texture2DParameters') {
        [void](Set-AttributeValue $Doc $node 'ID' 'FixedString' $Value)
    } else {
        [void](Set-AttributeValue $Doc $node 'Value' $ValueType $Value)
        [void](Set-AttributeValue $Doc $node 'BaseValue' $ValueType $Value)
        if ($NodeId -eq 'Vector3Parameters') {
            [void](Set-AttributeValue $Doc $node 'IsColor' 'bool' 'True')
        }
    }
    return $node
}

$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)
if (-not $stats.Contains('new entry "LPA_AshenHeartguard_Unwanted"')) {
$stats += @'

new entry "LPA_AshenHeartguard_Unwanted"
type "Armor"
using "ARM_ScaleMail_Body"
data "RootTemplate" "aef31c6f-07a7-5b20-9007-e910ca009ea1"
data "Unique" "0"
data "Rarity" "Legendary"
data "Slot" "Breast"
data "ArmorClass" "16"
data "PassivesOnEquip" "LPA_AshenHeart_Cooling;LPA_AshenHeart_RageBuffer;LPA_AshenHeart_HeatSink"

new entry "LPA_AshenHeartguard_Bloodguzzler"
type "Armor"
using "ARM_ScaleMail_Body"
data "RootTemplate" "6211fd61-a504-5639-8281-fb67da2c4a84"
data "Unique" "0"
data "Rarity" "Legendary"
data "Slot" "Breast"
data "ArmorClass" "16"
data "PassivesOnEquip" "LPA_AshenHeart_Cooling;LPA_AshenHeart_RageBuffer;LPA_AshenHeart_HeatSink"

new entry "LPA_AshenHeartguard_Mighty"
type "Armor"
using "ARM_ScaleMail_Body"
data "RootTemplate" "fe127a4f-e1d5-533b-a2aa-52f6ce7befaf"
data "Unique" "0"
data "Rarity" "Legendary"
data "Slot" "Breast"
data "ArmorClass" "16"
data "PassivesOnEquip" "LPA_AshenHeart_Cooling;LPA_AshenHeart_RageBuffer;LPA_AshenHeart_HeatSink"

new entry "LPA_OrinVanity"
type "Armor"
using "ARM_Camp_Body"
data "RootTemplate" "33bcf8bc-50ff-507b-aadf-53de85fb396d"
data "Unique" "0"
data "Rarity" "Legendary"
data "Slot" "VanityBody"
data "ArmorClass" "0"
data "ArmorType" "None"
data "Proficiency Group" ""

new entry "LPA_AshenHeart_Cooling"
type "PassiveData"
data "DisplayName" "h6670348fg6d20g5716g844ag0985fbedd253;1"
data "Description" "h831efd35g9f91g5dc9gbde6g01904b9d294c;1"
data "Icon" "PassiveFeature_FiendishResilience"
data "Properties" "Highlighted"
data "Boosts" "Resistance(Cold,Resistant)"

new entry "LPA_AshenHeart_RageBuffer"
type "PassiveData"
data "DisplayName" "h1855e8eag9fbdg56e4gbefag0c2101e73dc2;1"
data "Description" "h4768ccdfgc2bag574cgb0bdgfe3fca739c11;1"
data "Icon" "Action_Barbarian_Rage"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnStatusApplied"
data "Conditions" "StatusId('RAGE') or StatusId('RAGE_FRENZY') or StatusId('RAGE_BEAR') or StatusId('RAGE_EAGLE') or StatusId('RAGE_ELK') or StatusId('RAGE_TIGER') or StatusId('RAGE_WOLF') or StatusId('RAGE_WILDMAGIC')"
data "StatsFunctors" "GainTemporaryHitPoints(6)"

new entry "LPA_AshenHeart_HeatSink"
type "PassiveData"
data "DisplayName" "h5270526fga25cg5885gba3fgc0e6843b151a;1"
data "Description" "hdcd838ccga0e7g5a5dgbc95g796e0abe470b;1"
data "Icon" "Spell_Abjuration_ArmorOfAgathys"
data "Properties" "Highlighted;OncePerTurn"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsDamageTypeFire()"
data "StatsFunctors" "GainTemporaryHitPoints(2)"
'@
    [IO.File]::WriteAllText($statsPath, $stats, $utf8)
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$templateChildren = $roots.SelectSingleNode("/save/region[@id='Templates']/node[@id='Templates']/children")

function Add-LpaRoot(
    [xml]$Doc, $Parent, [string]$Uuid, [string]$Name, [string]$ParentUuid,
    [string]$StatsId, [string]$DisplayHandle, [string]$DescriptionHandle, [string]$Slot
) {
    if ($null -ne $Doc.SelectSingleNode("//node[@id='GameObjects']/attribute[@id='MapKey' and @value='$Uuid']")) { return }
    $n = $Doc.CreateElement('node'); $n.SetAttribute('id','GameObjects')
    [void](Add-AttributeNode $Doc $n 'Description' 'TranslatedString' '')
    $n.SelectSingleNode("attribute[@id='Description']").RemoveAttribute('value')
    $n.SelectSingleNode("attribute[@id='Description']").SetAttribute('handle',$DescriptionHandle)
    $n.SelectSingleNode("attribute[@id='Description']").SetAttribute('version','1')
    [void](Add-AttributeNode $Doc $n 'DisplayName' 'TranslatedString' '')
    $n.SelectSingleNode("attribute[@id='DisplayName']").RemoveAttribute('value')
    $n.SelectSingleNode("attribute[@id='DisplayName']").SetAttribute('handle',$DisplayHandle)
    $n.SelectSingleNode("attribute[@id='DisplayName']").SetAttribute('version','1')
    [void](Add-AttributeNode $Doc $n 'LevelName' 'FixedString' '')
    [void](Add-AttributeNode $Doc $n 'MapKey' 'FixedString' $Uuid)
    [void](Add-AttributeNode $Doc $n 'Name' 'LSString' $Name)
    [void](Add-AttributeNode $Doc $n 'ParentTemplateId' 'FixedString' $ParentUuid)
    [void](Add-AttributeNode $Doc $n 'Stats' 'FixedString' $StatsId)
    [void](Add-AttributeNode $Doc $n 'Type' 'FixedString' 'item')
    if ($Slot) {
        $children = $Doc.CreateElement('children')
        $equipment = $Doc.CreateElement('node'); $equipment.SetAttribute('id','Equipment')
        $eqChildren = $Doc.CreateElement('children')
        $slotNode = $Doc.CreateElement('node'); $slotNode.SetAttribute('id','Slot')
        [void](Add-AttributeNode $Doc $slotNode 'Object' 'FixedString' $Slot)
        [void]$eqChildren.AppendChild($slotNode)
        [void]$equipment.AppendChild($eqChildren)
        [void]$children.AppendChild($equipment)
        [void]$n.AppendChild($children)
    }
    [void]$Parent.AppendChild($n)
}

Add-LpaRoot $roots $templateChildren 'aef31c6f-07a7-5b20-9007-e910ca009ea1' 'LPA_AshenHeartguard_Unwanted' '5ff8df3a-6924-4eb4-9d1a-9e87bd644bf7' 'LPA_AshenHeartguard_Unwanted' 'he9f3a87eg4696g51ecg8485gf508c98a1c3a' 'hd076927dg307fg59f8ga930g518610238004' ''
Add-LpaRoot $roots $templateChildren '6211fd61-a504-5639-8281-fb67da2c4a84' 'LPA_AshenHeartguard_Bloodguzzler' '5fc2fcce-810d-47d2-824c-f6acf7b81a22' 'LPA_AshenHeartguard_Bloodguzzler' 'h165ff7b7g322eg5399gb32bg586027fc365b' 'hd076927dg307fg59f8ga930g518610238004' ''
Add-LpaRoot $roots $templateChildren 'fe127a4f-e1d5-533b-a2aa-52f6ce7befaf' 'LPA_AshenHeartguard_Mighty' '48215bcb-b4a2-48cb-bfbe-8b601e678032' 'LPA_AshenHeartguard_Mighty' 'hcc84eecegdbdeg5af8g84fega758e3b1ad8b' 'hd076927dg307fg59f8ga930g518610238004' ''
# Equipment.Slot describes the model attachment, not Stats.Slot. Camp clothing
# still uses Body. Inherit the complete native Equipment block (including race
# visuals) instead of replacing it with a slot-only block.
Add-LpaRoot $roots $templateChildren '33bcf8bc-50ff-507b-aadf-53de85fb396d' 'LPA_OrinVanity' '0629b687-0f66-4555-9612-0a787e14545c' 'LPA_OrinVanity' 'h1723710agf0b1g5d30g9999g1c82cdb8da92' 'h2edb7642gdcdfg5878g83f3g0d592dca6a6b' ''
Save-XmlUtf8 $roots $rootsPath

$assetsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsx'
[xml]$assets = Get-Content -Raw -LiteralPath $assetsPath
$materials = $assets.SelectNodes("/save/region[@id='MaterialBank']/node[@id='MaterialBank']/children/node[@id='Resource']")
$glowMask = '3087930b-36cd-57b8-a553-bcc9bda3d544'
$pulseShader = 'Public/Shared/Assets/Materials/Base/Base_GM_Pulse_Color_AlphaTest_VT.lsf'

foreach ($m in $materials) {
    $name = Get-AttributeValue $m 'Name'
    if (-not $name) { continue }

    if ($name.StartsWith('LPA_SharSpear_') -or $name.StartsWith('LPA_WalkingFortress_')) {
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'Color' '0.10 0.018 0.16' 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'VariationColor' '0.10 0.018 0.16' 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'GlowColour' '0.38 0.08 0.62' 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'GlowMultiplier' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'GlowIntensity' '0' 'float')
    }

    if ($name.StartsWith('LPA_DragonsBreath_')) {
        [void](Set-AttributeValue $assets $m 'SourceFile' 'LSString' $pulseShader)
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'Color' '0.48 0.018 0.025' 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'GlowMultiplier' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'GlowIntensity' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'MinGlow' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'MaxGlow' '0' 'float')
    }

    if ($name.StartsWith('LPA_Icingdeath_') -or $name.StartsWith('LPA_Twinkle_')) {
        [void](Set-AttributeValue $assets $m 'SourceFile' 'LSString' $pulseShader)
        $isTwinkle = $name.StartsWith('LPA_Twinkle_')
        $surface = if ($isTwinkle) { '0.72 0.80 0.92' } else { '0.72 0.82 0.90' }
        $glow = if ($isTwinkle) { '0.035 0.20 1.0' } else { '0.18 0.46 0.82' }
        $mult = if ($isTwinkle) { '2.6' } else { '1.8' }
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'Color' $surface 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'Vector3Parameters' 'GlowColour' $glow 'fvec3')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'GlowMultiplier' $mult 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'MinGlow' '0.15' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'MaxGlow' '1' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'PulseSpeed' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'ScalarParameters' 'UseGMColor' '0' 'float')
        [void](Ensure-MaterialParam $assets $m 'Texture2DParameters' 'Glowmap' $glowMask 'FixedString')
    }

    if ($name.StartsWith('LPA_CharonsClaw_') -or
        $name.StartsWith('LPA_Carsomyr_') -or
        $name.StartsWith('LPA_EntreriDagger_')) {
        $p = Find-MaterialParam $m 'GlowMultiplier'
        if ($null -ne $p) { [void](Set-AttributeValue $assets $p 'Value' 'float' '0'); [void](Set-AttributeValue $assets $p 'BaseValue' 'float' '0') }
        $p = Find-MaterialParam $m 'GlowIntensity'
        if ($null -ne $p) { [void](Set-AttributeValue $assets $p 'Value' 'float' '0'); [void](Set-AttributeValue $assets $p 'BaseValue' 'float' '0') }
    }
}
Save-XmlUtf8 $assets $assetsPath

$stringsEn = @{
    'he9f3a87eg4696g51ecg8485gf508c98a1c3a' = 'Ashen Heartguard — Unwanted'
    'h165ff7b7g322eg5399gb32bg586027fc365b' = 'Ashen Heartguard — Bloodguzzler'
    'hcc84eecegdbdeg5af8g84fega758e3b1ad8b' = 'Ashen Heartguard — Mighty'
    'hd076927dg307fg59f8ga930g518610238004' = 'Inner plates draw heat away from the infernal engine before it can devour its bearer from within. A heart this hot cannot be extinguished — only kept cool enough to keep beating.'
    'h6670348fg6d20g5716g844ag0985fbedd253' = 'Engine Cooling'
    'h831efd35g9f91g5dc9gbde6g01904b9d294c' = 'The armour regulates the infernal engine, granting Resistance to Cold damage.'
    'h1855e8eag9fbdg56e4gbefag0c2101e73dc2' = 'Thermal Buffer'
    'h4768ccdfgc2bag574cgb0bdgfe3fca739c11' = 'When Rage ignites, the armour draws off the first surge of heat, granting 6 Temporary Hit Points.'
    'h5270526fga25cg5885gba3fgc0e6843b151a' = 'Heat Sink'
    'hdcd838ccga0e7g5a5dgbc95g796e0abe470b' = 'Once per turn, dealing Fire damage vents excess heat and grants 2 Temporary Hit Points.'
    'h1723710agf0b1g5d30g9999g1c82cdb8da92' = "Orin's Carapace — Vanity"
    'h2edb7642gdcdfg5878g83f3g0d592dca6a6b' = "A purely cosmetic copy of Orin's macabre dress, rebuilt for the camp-clothing slot. It grants no combat benefits."
}
$stringsRu = @{
    'he9f3a87eg4696g51ecg8485gf508c98a1c3a' = 'Страж Пепельного Сердца — Незваный'
    'h165ff7b7g322eg5399gb32bg586027fc365b' = 'Страж Пепельного Сердца — Кровопийца'
    'hcc84eecegdbdeg5af8g84fega758e3b1ad8b' = 'Страж Пепельного Сердца — Могучий'
    'hd076927dg307fg59f8ga930g518610238004' = 'Внутренние пластины отводят жар от инфернального двигателя, не позволяя ему пожрать носителя изнутри. Такое горячее сердце нельзя погасить — его можно только удержать достаточно холодным, чтобы оно билось дальше.'
    'h6670348fg6d20g5716g844ag0985fbedd253' = 'Охлаждение двигателя'
    'h831efd35g9f91g5dc9gbde6g01904b9d294c' = 'Доспех стабилизирует инфернальный двигатель и даёт сопротивление урону холодом.'
    'h1855e8eag9fbdg56e4gbefag0c2101e73dc2' = 'Тепловой буфер'
    'h4768ccdfgc2bag574cgb0bdgfe3fca739c11' = 'Когда вспыхивает Ярость, доспех принимает на себя первый выброс жара и даёт 6 временных хитов.'
    'h5270526fga25cg5885gba3fgc0e6843b151a' = 'Теплоотвод'
    'hdcd838ccga0e7g5a5dgbc95g796e0abe470b' = 'Раз за ход нанесение огненного урона отводит лишний жар и даёт 2 временных хита.'
    'h1723710agf0b1g5d30g9999g1c82cdb8da92' = 'Панцирь Орин — образ'
    'h2edb7642gdcdfg5878g83f3g0d592dca6a6b' = 'Чисто косметическая копия жуткого наряда Орин, перенесённая в слот лагерной одежды. Боевых бонусов не даёт.'
}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $list = $loc.SelectSingleNode('/contentList')
    $map = if ($file.Directory.Name -eq 'Russian') { $stringsRu } else { $stringsEn }
    foreach ($key in $map.Keys) {
        if ($null -eq $loc.SelectSingleNode("/contentList/content[@contentuid='$key']")) {
            $n = $loc.CreateElement('content')
            $n.SetAttribute('contentuid',$key); $n.SetAttribute('version','1'); $n.InnerText = $map[$key]
            [void]$list.AppendChild($n)
        }
    }
    Save-XmlUtf8 $loc $file.FullName
}

$metaPath = Join-Path $StageRoot 'Mods/DenimDragonArmor/meta.lsx'
$meta = [IO.File]::ReadAllText($metaPath)
$meta = $meta.Replace('0.3.1 preview', ('0.3.2 ' + $Mode)).Replace('0.3.1 final', ('0.3.2 ' + $Mode))
[IO.File]::WriteAllText($metaPath, $meta, $utf8)

Write-Host "Applied Legacy Party Armory 0.3.2 $Mode patch."
