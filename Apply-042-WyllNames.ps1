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

foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $ru = $file.Directory.Name -eq 'Russian'
    $strings = @{
        'heaa675e5g88a2g52ebgb394g5004a62ee766' = $(if ($ru) { 'Чёрный Клык Фронтира' } else { 'Black Fang of the Frontiers' })
        'h08126c70g53d3g502bg8eeegded082882f88' = $(if ($ru) { 'Чернёный клинок отвечает не имени прежнего владельца, а воле того, кто держит его сейчас. Пепельная завеса скрывает шаг, а тёмная сталь превращает решимость Клинка Фронтира в удар.' } else { 'The blackened blade answers not to the name of its former master, but to the will of the hand that holds it now. Ash veils the step, while dark steel turns the Blade of Frontiers’ resolve into a strike.' })
        'h157f5ce1g3648g585aga618g5285496df29b' = $(if ($ru) { 'Перчатка Пепельного Договора' } else { 'Gauntlet of the Ashen Pact' })
        'h0b9ca8eag6663g541fga67egf7775e009313' = $(if ($ru) { 'Плотная тёмная кожа и вплетённые в неё руны напоминают: договоры связывают лишь тех, кто перестаёт выбирать. Перчатка гасит чужие чары и крепче удерживает Чёрный Клык.' } else { 'Dark leather and runes worked into it carry a reminder: bargains bind only those who stop choosing. The gauntlet blunts hostile magic and steadies the Black Fang in hand.' })
        'h8012a034g606cg58c3g9e98g527cab5afead' = $(if ($ru) { 'Воля Чёрного Клыка' } else { 'Will of the Black Fang' })
        'h240b6ac3ga4fcg57d8ga1dfg572bd3cd751c' = $(if ($ru) { 'Вы владеете длинными мечами. Этот лёгкий клинок использует заклинательную характеристику для бросков атаки и урона.' } else { 'You gain proficiency with longswords. This light blade uses your spellcasting ability for attack and damage rolls.' })
        'h5f383545g3274g5ec5gbb7bg091fa16a1c79' = $(if ($ru) { 'Клык и договор' } else { 'Fang and Pact' })
        'h05ac2096ge3cag50c1ga0a8g7e48c426c3d9' = $(if ($ru) { 'Пока Чёрный Клык Фронтира надет, вы получаете +1 к классу брони.' } else { 'While Black Fang of the Frontiers is equipped, you gain +1 Armour Class.' })
    }
    foreach ($key in $strings.Keys) {
        $node = $loc.SelectSingleNode("/contentList/content[@contentuid='$key']")
        if ($null -eq $node) { throw "Missing Wyll localization handle $key in $($file.FullName)" }
        $node.InnerText = $strings[$key]
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Wyll item naming pass for $Mode."
