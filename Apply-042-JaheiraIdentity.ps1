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

$statsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Stats/Generated/Data/LegacyPartyArmory.txt'
$stats = [IO.File]::ReadAllText($statsPath)
# Keep it veteran-utility rather than raw power creep: mobile, alert and hard to pin down.
$stats = Set-StatField $stats 'LPA_HarperFinery' 'Boosts' 'RollBonus(SavingThrow,1);Advantage(Skill,Nature);Advantage(Skill,Survival);Initiative(1);Advantage(Skill,Perception)'
[IO.File]::WriteAllText($statsPath, $stats, $utf8)

foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $ru = $file.Directory.Name -eq 'Russian'
    $name = $loc.SelectSingleNode("/contentList/content[@contentuid='h559d9ba0g20dag52dfg9946g2e4b5e8f7547']")
    $desc = $loc.SelectSingleNode("/contentList/content[@contentuid='he05db00agd898g51aaga8adgae30aae46742']")
    if ($null -eq $name -or $null -eq $desc) { throw "Missing Jaheira localization in $($file.FullName)" }
    $name.InnerText = if ($ru) { 'Доспех Последней Арфистки' } else { 'Armour of the Last Harper' }
    $desc.InnerText = if ($ru) {
        'Не парадный знак ордена, а броня того, кто пережил слишком много войн, чтобы нуждаться в гербе. Кожа цвета коры, тусклая бронза и зелень листвы позволяют Джахейре исчезнуть среди деревьев — и первой заметить того, кто решил, что она стала медленнее.'
    } else {
        'No ceremonial badge of an order, but the armour of one who has survived too many wars to need a crest. Bark-brown leather, dull bronze and leaf-green panels let Jaheira vanish among the trees — and notice first anyone foolish enough to think she has grown slow.'
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Jaheira identity pass for $Mode."
