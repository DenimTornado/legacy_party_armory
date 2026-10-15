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

# These three are private LPA copies, so their visible identity should belong to
# Shadowheart rather than Viconia/the stock Shar item names. Their inherited
# combat mechanics stay intact; this pass deliberately avoids overriding parent
# Boosts/Passives on already-powerful legendary templates.
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $ru = $file.Directory.Name -eq 'Russian'

    $strings = @{
        'hdf46927egaf48g5d52g93feg8e311d9eb3eb' = $(if ($ru) { 'Копьё Забытой Клятвы' } else { 'Spear of the Forgotten Oath' })
        'hcc7b83a4g1139g54e6g9b0ag9d8b52b1725b' = $(if ($ru) { 'Клятвы можно отнять, память стереть, имя заменить — но рука всё равно помнит, за что готова сражаться.' } else { 'Oaths can be taken, memories erased, names replaced — yet the hand still remembers what it is willing to fight for.' })
        'h87b0ac8cg342eg5d2eg8632g09d6c7e87817' = $(if ($ru) { 'Покров Утраченного Имени' } else { 'Veil of the Lost Name' })
        'h05b16ebdg1f11g51e7gb15ag8cec634bbaa5' = $(if ($ru) { 'Тьма учила её прятать имя. Теперь этот покров хранит не чужую волю, а право самой решать, что оставить в тени.' } else { 'Darkness taught her to hide her name. Now this veil guards no one else’s will, only her right to decide what remains in shadow.' })
        'h7700e6adgc056g5c38ga86bgb58371c463e7' = $(if ($ru) { 'Щит Последней Тайны' } else { 'Shield of the Last Secret' })
        'hd0779fd5g5ba9g50acg85b3g410d40119201' = $(if ($ru) { 'Одни тайны защищают из страха раскрыть их. Другие — потому что они наконец принадлежат тебе.' } else { 'Some secrets are guarded for fear of revealing them. Others are guarded because, at last, they belong to you.' })
    }

    foreach ($key in $strings.Keys) {
        $node = $loc.SelectSingleNode("/contentList/content[@contentuid='$key']")
        if ($null -eq $node) { throw "Missing localization handle $key in $($file.FullName)" }
        $node.InnerText = $strings[$key]
    }
    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Shadowheart identity pass for $Mode."
