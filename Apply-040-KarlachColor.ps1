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

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$root = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='aef31c6f-07a7-5b20-9007-e910ca009ea1']]")
if ($null -eq $root) { throw 'Missing Ashen Heartguard root' }
$color = $root.SelectSingleNode("attribute[@id='ColorPreset']")
if ($null -eq $color) {
    $color = $roots.CreateElement('attribute')
    $color.SetAttribute('id','ColorPreset')
    [void]$root.AppendChild($color)
}
$color.SetAttribute('type','31')
# Black and Azure: charcoal/black base with cold azure accents.
$color.SetAttribute('value','b533d673-a221-613f-4be7-f2697bef97e0')
Save-XmlUtf8 $roots $rootsPath
Write-Host "Applied Ashen Heartguard Black and Azure preset for $Mode."
