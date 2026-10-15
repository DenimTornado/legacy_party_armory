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
        'heaa675e5g88a2g52ebgb394g5004a62ee766' = $(if ($ru) { 'Коготь Шарона' } else { "Charon’s Claw" })
        'h08126c70g53d3g502bg8eeegded082882f88' = $(if ($ru) { 'Чернёный клинок, чья тёмная сталь отвечает силе воли владельца. Пепельная завеса скрывает шаг, а Коготь охотно служит тому, кто сумеет удержать его в руке.' } else { 'A blackened blade whose dark steel answers the will of its wielder. Ash veils each step, and the Claw serves readily enough — provided the hand holding it proves worthy.' })
        'h157f5ce1g3648g585aga618g5285496df29b' = $(if ($ru) { 'Перчатки Шарона' } else { "Charon’s Gloves" })
        'h0b9ca8eag6663g541fga67egf7775e009313' = $(if ($ru) { 'Тёмная кожа и вплетённые в неё руны созданы, чтобы укрощать Коготь Шарона. Перчатки гасят чужие чары и делают хватку владельца почти безошибочной.' } else { 'Dark leather and woven runes were made to master Charon’s Claw. The gloves blunt hostile magic and make the wielder’s grip almost unerring.' })
        'h8012a034g606cg58c3g9e98g527cab5afead' = $(if ($ru) { 'Воля Когтя Шарона' } else { "Will of Charon’s Claw" })
        'h240b6ac3ga4fcg57d8ga1dfg572bd3cd751c' = $(if ($ru) { 'Вы владеете длинными мечами. Этот лёгкий клинок использует заклинательную характеристику для бросков атаки и урона.' } else { 'You gain proficiency with longswords. This light blade uses your spellcasting ability for attack and damage rolls.' })
        'h5f383545g3274g5ec5gbb7bg091fa16a1c79' = $(if ($ru) { 'Коготь и перчатки' } else { 'Claw and Gloves' })
        'h05ac2096ge3cag50c1ga0a8g7e48c426c3d9' = $(if ($ru) { 'Пока Коготь Шарона надет, вы получаете +1 к классу брони.' } else { 'While Charon’s Claw is equipped, you gain +1 Armour Class.' })
    }
    foreach ($key in $strings.Keys) {
        $node = $loc.SelectSingleNode("/contentList/content[@contentuid='$key']")
        if ($null -eq $node) { throw "Missing Wyll localization handle $key in $($file.FullName)" }
        $node.InnerText = $strings[$key]
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Wyll requested Charon names for $Mode."
