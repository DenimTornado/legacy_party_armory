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

function Set-StatField([string]$Text, [string]$Entry, [string]$Field, [string]$Value) {
    $entryEsc = [regex]::Escape($Entry)
    $fieldEsc = [regex]::Escape($Field)
    $pattern = "(?ms)(new entry `"$entryEsc`".*?)(?=\r?\nnew entry `"|\z)"
    $m = [regex]::Match($Text, $pattern)
    if (-not $m.Success) { throw "Missing stat entry: $Entry" }
    $block = $m.Value
    $fieldPattern = "(?m)^data `"$fieldEsc`" `".*?`"\r?$"
    if ([regex]::IsMatch($block, $fieldPattern)) {
        $block = [regex]::Replace($block, $fieldPattern, "data `"$Field`" `"$Value`"")
    } else {
        $block = $block.TrimEnd() + "`n" + "data `"$Field`" `"$Value`"" + "`n"
    }
    return $Text.Substring(0,$m.Index) + $block + $Text.Substring($m.Index+$m.Length)
}

function Remove-StatField([string]$Text, [string]$Entry, [string]$Field) {
    $entryEsc = [regex]::Escape($Entry)
    $pattern = "(?ms)(new entry `"$entryEsc`".*?)(?=\r?\nnew entry `"|\z)"
    $m = [regex]::Match($Text, $pattern)
    if (-not $m.Success) { throw "Missing stat entry: $Entry" }
    $block = [regex]::Replace($m.Value, "(?m)^data `"$([regex]::Escape($Field))`" `".*?`"\r?\n?", '')
    return $Text.Substring(0,$m.Index) + $block + $Text.Substring($m.Index+$m.Length)
}

$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)

# Wyll's armour is the defensive half of the set: precise spellcasting and stable concentration.
$stats = Set-StatField $stats 'LPA_WyllLeatherArmor' 'Rarity' 'Legendary'
$stats = Set-StatField $stats 'LPA_WyllLeatherArmor' 'Boosts' 'AC(1);SpellSaveDC(1);RollBonus(MeleeSpellAttack,1);RollBonus(RangedSpellAttack,1);Advantage(Concentration)'

# The hat is about the Blade of Frontiers seeing the opening first, not generic archery.
$stats = Remove-StatField $stats 'LPA_WyllMarksmanHat' 'PassivesOnEquip'
$stats = Set-StatField $stats 'LPA_WyllMarksmanHat' 'Boosts' 'Initiative(2);RollBonus(RangedSpellAttack,1);Advantage(Skill,Perception)'
[IO.File]::WriteAllText($statsPath, $stats, $utf8)

function Set-Translated([xml]$Doc, $Node, [string]$Id, [string]$Handle) {
    $a = $Node.SelectSingleNode("attribute[@id='$Id']")
    if ($null -eq $a) {
        $a = $Doc.CreateElement('attribute')
        $a.SetAttribute('id',$Id)
        [void]$Node.AppendChild($a)
    }
    $a.SetAttribute('type','TranslatedString')
    $a.RemoveAttribute('value')
    $a.SetAttribute('handle',$Handle)
    $a.SetAttribute('version','1')
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$armor = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='def74bcd-48a7-55c2-99d6-9b72e66c2fe0']]")
$hat = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='334a92c4-f2b6-5dd8-9eb5-6606b424253e']]")
if ($null -eq $armor -or $null -eq $hat) { throw 'Missing Wyll custom roots' }

Set-Translated $roots $armor 'DisplayName' 'h5e6a413bg4cb9g598cg9bf7g3f5dad8b9b11'
Set-Translated $roots $armor 'Description' 'h30ad9018g9fb9g5cf7gbebbg448427fb73ef'
Set-Translated $roots $hat 'DisplayName' 'h74a3341dg1be9g528bgaf65gd0b8f94e5a22'
Set-Translated $roots $hat 'Description' 'h0e54e6f0g29b8g5897ga09fgd4e6db301d6a'
Save-XmlUtf8 $roots $rootsPath

foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $list = $loc.SelectSingleNode('/contentList')
    $ru = $file.Directory.Name -eq 'Russian'
    $strings = @{
        'h5e6a413bg4cb9g598cg9bf7g3f5dad8b9b11' = $(if ($ru) { 'Доспех Клинка Фронтира' } else { 'Armour of the Blade of Frontiers' })
        'h30ad9018g9fb9g5cf7gbebbg448427fb73ef' = $(if ($ru) { 'Эта кожа скроена для того, кто привык держать клинок в одной руке, а договор — в другой. Тёмные пластины не стесняют движений, а вплетённые в подкладку руны удерживают чужую магию ровно настолько, чтобы Клинок Фронтира успел ответить своей.' } else { 'Cut for a man accustomed to holding a blade in one hand and a bargain in the other. Dark plates leave the body free to move, while runes worked into the lining hold hostile magic at bay just long enough for the Blade of Frontiers to answer with his own.' })
        'h74a3341dg1be9g528bgaf65gd0b8f94e5a22' = $(if ($ru) { 'Взор Клинка Фронтира' } else { 'Gaze of the Blade of Frontiers' })
        'h0e54e6f0g29b8g5897ga09fgd4e6db301d6a' = $(if ($ru) { 'Герой не обязан видеть дальше всех. Достаточно заметить опасность на мгновение раньше — и успеть решить, будет ли следующей вспышкой сталь или заклятие.' } else { 'A hero need not see farther than everyone else. It is enough to notice danger a heartbeat sooner — and decide whether the next flash will be steel or spell.' })
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

Write-Host "Applied Wyll 0.3.12 gear identity pass for $Mode."
