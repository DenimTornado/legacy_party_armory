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

function Set-Attr([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = $Node.SelectSingleNode("attribute[@id='$Id']")
    if ($null -eq $a) {
        $a = $Doc.CreateElement('attribute')
        $a.SetAttribute('id', $Id)
        [void]$Node.AppendChild($a)
    }
    $a.SetAttribute('type', $Type)
    $a.SetAttribute('value', $Value)
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$orin = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='33bcf8bc-50ff-507b-aadf-53de85fb396d']]")
if ($null -eq $orin) { throw 'Missing Minthara vanity root' }

# Stock monochrome White/Black palette. The dye object itself is not distributed.
Set-Attr $roots $orin 'ColorPreset' 'guid' '9602f5d1-827b-f508-7dd4-c4b3ff068eec'
Save-XmlUtf8 $roots $rootsPath

foreach ($file in Get-ChildItem -LiteralPath (Join-Path $StageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    [xml]$loc = Get-Content -Raw -LiteralPath $file.FullName
    $ru = $file.Directory.Name -eq 'Russian'

    $name = $loc.SelectSingleNode("/contentList/content[@contentuid='h1723710agf0b1g5d30g9999g1c82cdb8da92']")
    if ($null -ne $name) {
        $name.InnerText = if ($ru) { 'Покров Мензоберранзана' } else { 'Veil of Menzoberranzan' }
    }

    $desc = $loc.SelectSingleNode("/contentList/content[@contentuid='h2edb7642gdcdfg5878g83f3g0d592dca6a6b']")
    if ($null -ne $desc) {
        $desc.InnerText = if ($ru) {
            'В Мензоберранзане говорят, что тьма не скрывает тайны — она сама решает, кому их открыть. Этот покров хранит молчание лучше любой клятвы.'
        } else {
            'In Menzoberranzan, they say darkness does not hide secrets — it chooses who is allowed to see them. This veil keeps silence better than any oath.'
        }
    }

    Save-XmlUtf8 $loc $file.FullName
}

Write-Host "Applied Minthara vanity refinement for $Mode."
